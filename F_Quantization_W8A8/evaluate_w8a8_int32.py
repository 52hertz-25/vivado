from pathlib import Path
import csv
import json

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from model import LeNet5


BASE_DIR = Path(__file__).resolve().parent
DEVICE = torch.device("cpu")

FP32_MODEL_PATH = BASE_DIR / "lenet5_fp32_from_hls.pth"
WEIGHT_DIR = BASE_DIR / "exported_weights" / "int8"
WEIGHT_SCALE_PATH = WEIGHT_DIR / "weight_scales.json"
ACTIVATION_SCALE_PATH = BASE_DIR / "activation_calibration.json"
DATA_DIR = BASE_DIR / "data"

BATCH_SIZE = 128


def get_scale(data, name):
    """兼容不同JSON保存格式。"""
    item = data[name]

    if isinstance(item, dict):
        for key in ("scale", "scale_int8", "scale_value"):
            if key in item:
                return float(item[key])

    return float(item)


def quantize_activation(x, scale):
    """把浮点激活值对称量化到INT8。"""
    return torch.clamp(
        torch.round(x / scale),
        -127,
        127
    )


def load_int8_weight(name):
    path = WEIGHT_DIR / f"{name}.weight.int8.npy"

    if not path.exists():
        raise FileNotFoundError(
            f"找不到{name}的INT8权重文件：{path}"
        )

    array = np.load(path)

    if array.dtype != np.int8:
        raise TypeError(
            f"{path.name}的数据类型不是int8，而是{array.dtype}"
        )

    return torch.from_numpy(array).float()


with open(WEIGHT_SCALE_PATH, "r", encoding="utf-8") as file:
    weight_scale_data = json.load(file)

with open(ACTIVATION_SCALE_PATH, "r", encoding="utf-8") as file:
    activation_scale_data = json.load(file)


weight_scales = {
    name: get_scale(weight_scale_data, name)
    for name in ("conv1", "conv2", "conv3", "fc1", "fc2")
}

activation_scales = {
    name: get_scale(activation_scale_data, name)
    for name in (
        "input",
        "conv1_relu",
        "pool1",
        "conv2_relu",
        "pool2",
        "conv3_relu",
        "fc1_relu",
        "fc2_output",
    )
}


weights = {
    name: load_int8_weight(name)
    for name in ("conv1", "conv2", "conv3", "fc1", "fc2")
}


def w8a8_forward(x):
    """
    W8A8-INT32推理：
    INT8激活 × INT8权重，使用INT32语义进行累加。
    """

    # 输入量化
    x_q = quantize_activation(x, activation_scales["input"])

    # Conv1
    acc1 = torch.round(F.conv2d(x_q, weights["conv1"]))
    y1 = acc1 * (
        activation_scales["input"] *
        weight_scales["conv1"]
    )
    y1 = F.relu(y1)
    y1_q = quantize_activation(
        y1,
        activation_scales["conv1_relu"]
    )
    p1_q = F.max_pool2d(y1_q, 2)

    # Conv2
    acc2 = torch.round(F.conv2d(p1_q, weights["conv2"]))
    y2 = acc2 * (
        activation_scales["pool1"] *
        weight_scales["conv2"]
    )
    y2 = F.relu(y2)
    y2_q = quantize_activation(
        y2,
        activation_scales["conv2_relu"]
    )
    p2_q = F.max_pool2d(y2_q, 2)

    # Conv3
    acc3 = torch.round(F.conv2d(p2_q, weights["conv3"]))
    y3 = acc3 * (
        activation_scales["pool2"] *
        weight_scales["conv3"]
    )
    y3 = F.relu(y3)
    y3_q = quantize_activation(
        y3,
        activation_scales["conv3_relu"]
    )

    # FC1
    flat_q = torch.flatten(y3_q, 1)
    acc4 = torch.round(F.linear(flat_q, weights["fc1"]))
    y4 = acc4 * (
        activation_scales["conv3_relu"] *
        weight_scales["fc1"]
    )
    y4 = F.relu(y4)
    y4_q = quantize_activation(
        y4,
        activation_scales["fc1_relu"]
    )

    # FC2
    acc5 = torch.round(F.linear(y4_q, weights["fc2"]))
    logits = acc5 * (
        activation_scales["fc1_relu"] *
        weight_scales["fc2"]
    )

    accumulator_max = {
        "conv1": int(acc1.abs().max().item()),
        "conv2": int(acc2.abs().max().item()),
        "conv3": int(acc3.abs().max().item()),
        "fc1": int(acc4.abs().max().item()),
        "fc2": int(acc5.abs().max().item()),
    }

    return logits, accumulator_max


print("正在准备MNIST测试集……")

transform = transforms.Compose([
    transforms.Pad(2),
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

test_dataset = datasets.MNIST(
    root=DATA_DIR,
    train=False,
    download=False,
    transform=transform
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)


fp32_model = LeNet5().to(DEVICE)
state_dict = torch.load(
    FP32_MODEL_PATH,
    map_location=DEVICE,
    weights_only=True
)
fp32_model.load_state_dict(state_dict)
fp32_model.eval()


total = 0
fp32_correct = 0
int8_correct = 0
agreement = 0

global_accumulator_max = {
    "conv1": 0,
    "conv2": 0,
    "conv3": 0,
    "fc1": 0,
    "fc2": 0,
}


print("开始进行FP32与W8A8-INT32对比测试……")

with torch.no_grad():
    for batch_index, (images, labels) in enumerate(test_loader):
        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        fp32_logits = fp32_model(images)
        int8_logits, current_max = w8a8_forward(images)

        fp32_predictions = fp32_logits.argmax(dim=1)
        int8_predictions = int8_logits.argmax(dim=1)

        total += labels.size(0)
        fp32_correct += (
            fp32_predictions == labels
        ).sum().item()
        int8_correct += (
            int8_predictions == labels
        ).sum().item()
        agreement += (
            fp32_predictions == int8_predictions
        ).sum().item()

        for name in global_accumulator_max:
            global_accumulator_max[name] = max(
                global_accumulator_max[name],
                current_max[name]
            )

        if (batch_index + 1) % 20 == 0:
            print(f"已测试：{total}/{len(test_dataset)}")


fp32_accuracy = 100.0 * fp32_correct / total
int8_accuracy = 100.0 * int8_correct / total
agreement_rate = 100.0 * agreement / total
accuracy_drop = fp32_accuracy - int8_accuracy


print("=" * 60)
print("W8A8-INT32测试结果")
print("=" * 60)
print(f"测试图片数量：       {total}")
print(f"FP32正确数量：       {fp32_correct}")
print(f"W8A8正确数量：       {int8_correct}")
print(f"FP32准确率：         {fp32_accuracy:.2f}%")
print(f"W8A8-INT32准确率：   {int8_accuracy:.2f}%")
print(f"准确率下降：         {accuracy_drop:.2f}个百分点")
print(f"与FP32预测一致率：   {agreement_rate:.2f}%")

print("-" * 60)
print("各层INT32累加器最大绝对值：")

for name, value in global_accumulator_max.items():
    print(f"{name:<8} {value}")

int32_limit = 2**31 - 1
overflow_safe = all(
    value <= int32_limit
    for value in global_accumulator_max.values()
)

print(f"INT32溢出检查：      {'PASS' if overflow_safe else 'FAIL'}")
print("=" * 60)


result = {
    "method": "W8A8-INT32",
    "weight_bits": 8,
    "activation_bits": 8,
    "accumulator_bits": 32,
    "test_samples": total,
    "fp32_accuracy_percent": fp32_accuracy,
    "quantized_accuracy_percent": int8_accuracy,
    "accuracy_drop_percentage_points": accuracy_drop,
    "fp32_prediction_agreement_percent": agreement_rate,
    "accumulator_max_abs": global_accumulator_max,
    "int32_overflow_check": overflow_safe,
}

json_path = BASE_DIR / "w8a8_int32_results.json"

with open(json_path, "w", encoding="utf-8") as file:
    json.dump(result, file, indent=2, ensure_ascii=False)


csv_path = BASE_DIR / "accuracy_results.csv"

existing_rows = []

if csv_path.exists():
    with open(csv_path, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        existing_rows = [
            row for row in reader
            if row.get("Method") != "W8A8-INT32"
        ]

fieldnames = [
    "Method",
    "Weight_bits",
    "Activation_bits",
    "Accumulator_bits",
    "Accuracy_percent",
    "Accuracy_drop",
    "Agreement_with_FP32",
]

existing_rows.append({
    "Method": "W8A8-INT32",
    "Weight_bits": 8,
    "Activation_bits": 8,
    "Accumulator_bits": 32,
    "Accuracy_percent": f"{int8_accuracy:.2f}",
    "Accuracy_drop": f"{accuracy_drop:.2f}",
    "Agreement_with_FP32": f"{agreement_rate:.2f}",
})

with open(csv_path, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(existing_rows)


print("结果已经保存到：")
print(json_path)
print(csv_path)
print("W8A8-INT32推理评估完成。[PASS]")