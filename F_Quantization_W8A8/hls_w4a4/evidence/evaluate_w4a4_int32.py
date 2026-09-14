from pathlib import Path
import csv
import json

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


# ============================================================
# 1. 路径设置
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

FP32_MODEL_PATH = BASE_DIR / "lenet5_fp32_from_hls.pth"

INT4_WEIGHT_DIR = (
    BASE_DIR /
    "exported_weights" /
    "int4"
)

WEIGHT_SCALE_PATH = (
    INT4_WEIGHT_DIR /
    "weight_scales.json"
)

ACTIVATION_SCALE_PATH = (
    BASE_DIR /
    "activation_calibration.json"
)

DATA_DIR = BASE_DIR / "data"

JSON_RESULT_PATH = (
    BASE_DIR /
    "w4a4_int32_results.json"
)

CSV_RESULT_PATH = (
    BASE_DIR /
    "w4a4_accuracy_results.csv"
)


# ============================================================
# 2. 运行设备
# ============================================================

if torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
else:
    DEVICE = torch.device("cpu")

print(f"运行设备：{DEVICE}")


# ============================================================
# 3. W4A4量化参数
# ============================================================

QMIN = -7
QMAX = 7

INT32_MIN = -(2 ** 31)
INT32_MAX = 2 ** 31 - 1

LAYER_NAMES = [
    "conv1",
    "conv2",
    "conv3",
    "fc1",
    "fc2",
]


# ============================================================
# 4. 读取JSON
# ============================================================

def load_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"找不到文件：\n{path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


weight_scale_data = load_json(
    WEIGHT_SCALE_PATH
)

activation_scale_data = load_json(
    ACTIVATION_SCALE_PATH
)


# ============================================================
# 5. 提取权重缩放系数
# ============================================================

def get_weight_scale(layer_name):
    item = weight_scale_data[layer_name]

    if isinstance(item, dict):
        return float(item["scale"])

    return float(item)


# ============================================================
# 6. 计算W4A4激活值缩放系数
# ============================================================

def get_activation_scale(name):
    if name not in activation_scale_data:
        raise KeyError(
            f"激活值校准文件中找不到：{name}"
        )

    item = activation_scale_data[name]

    if isinstance(item, dict):
        if "max_abs" in item:
            max_abs = float(item["max_abs"])
            return max_abs / QMAX if max_abs > 0 else 1.0

        if "scale" in item:
            # 原校准文件是按照INT8的127计算的
            int8_scale = float(item["scale"])
            max_abs = int8_scale * 127.0
            return max_abs / QMAX if max_abs > 0 else 1.0

    # 如果JSON中直接存的是数字，默认它是INT8 scale
    int8_scale = float(item)
    max_abs = int8_scale * 127.0

    return max_abs / QMAX if max_abs > 0 else 1.0


# 兼容校准文件中pool2可能写成pool12的情况
def find_activation_scale(*names):
    for name in names:
        if name in activation_scale_data:
            return get_activation_scale(name)

    raise KeyError(
        f"找不到激活缩放系数，尝试过：{names}"
    )


activation_scales = {
    "input": find_activation_scale("input"),

    "conv1_relu": find_activation_scale(
        "conv1_relu"
    ),

    "pool1": find_activation_scale(
        "pool1"
    ),

    "conv2_relu": find_activation_scale(
        "conv2_relu"
    ),

    "pool2": find_activation_scale(
        "pool2",
        "pool12"
    ),

    "conv3_relu": find_activation_scale(
        "conv3_relu"
    ),

    "fc1_relu": find_activation_scale(
        "fc1_relu"
    ),

    "fc2_output": find_activation_scale(
        "fc2_output"
    ),
}


# ============================================================
# 7. 加载INT4权重
# ============================================================

def load_int4_weight(layer_name):
    path = (
        INT4_WEIGHT_DIR /
        f"{layer_name}.weight.int4.npy"
    )

    if not path.exists():
        raise FileNotFoundError(
            f"找不到{layer_name}的INT4权重：\n{path}"
        )

    array = np.load(path)

    if array.dtype != np.int8:
        array = array.astype(np.int8)

    if array.min() < QMIN or array.max() > QMAX:
        raise ValueError(
            f"{layer_name}权重超出INT4范围："
            f"[{array.min()}, {array.max()}]"
        )

    return torch.from_numpy(array).to(
        DEVICE
    ).to(torch.float32)


int4_weights = {}

for layer_name in LAYER_NAMES:
    int4_weights[layer_name] = load_int4_weight(
        layer_name
    )


# ============================================================
# 8. 加载FP32权重
# ============================================================

if not FP32_MODEL_PATH.exists():
    raise FileNotFoundError(
        f"找不到FP32模型文件：\n{FP32_MODEL_PATH}"
    )

checkpoint = torch.load(
    FP32_MODEL_PATH,
    map_location="cpu",
    weights_only=False
)

if isinstance(checkpoint, torch.nn.Module):
    fp32_state_dict = checkpoint.state_dict()

elif isinstance(checkpoint, dict):
    if "state_dict" in checkpoint:
        fp32_state_dict = checkpoint["state_dict"]

    elif "model_state_dict" in checkpoint:
        fp32_state_dict = checkpoint["model_state_dict"]

    else:
        fp32_state_dict = checkpoint

else:
    raise TypeError(
        "无法识别FP32模型文件格式。"
    )

clean_state_dict = {}

for key, value in fp32_state_dict.items():
    clean_key = key

    if clean_key.startswith("module."):
        clean_key = clean_key[len("module."):]

    clean_state_dict[clean_key] = value


def get_fp32_parameter(name):
    if name not in clean_state_dict:
        return None

    value = clean_state_dict[name]

    if not isinstance(value, torch.Tensor):
        value = torch.tensor(value)

    return value.detach().to(
        DEVICE
    ).to(torch.float32)


fp32_weights = {}
fp32_biases = {}

for layer_name in LAYER_NAMES:
    weight_name = f"{layer_name}.weight"
    bias_name = f"{layer_name}.bias"

    fp32_weights[layer_name] = get_fp32_parameter(
        weight_name
    )

    fp32_biases[layer_name] = get_fp32_parameter(
        bias_name
    )

    if fp32_weights[layer_name] is None:
        raise KeyError(
            f"FP32模型中找不到：{weight_name}"
        )


# ============================================================
# 9. 量化与反量化函数
# ============================================================

def quantize_activation(value, scale):
    quantized = torch.round(value / scale)

    quantized = torch.clamp(
        quantized,
        QMIN,
        QMAX
    )

    return quantized


def requantize_accumulator(
    accumulator,
    input_scale,
    weight_scale,
    output_scale,
    bias=None
):
    value = (
        accumulator *
        input_scale *
        weight_scale
    )

    if bias is not None:
        if value.ndim == 4:
            value = value + bias.view(
                1,
                -1,
                1,
                1
            )
        else:
            value = value + bias.view(
                1,
                -1
            )

    quantized = torch.round(
        value / output_scale
    )

    quantized = torch.clamp(
        quantized,
        QMIN,
        QMAX
    )

    return quantized


# ============================================================
# 10. FP32前向推理
# ============================================================

def fp32_forward(images):
    x = F.conv2d(
        images,
        fp32_weights["conv1"],
        fp32_biases["conv1"]
    )

    x = F.relu(x)
    x = F.max_pool2d(x, 2)

    x = F.conv2d(
        x,
        fp32_weights["conv2"],
        fp32_biases["conv2"]
    )

    x = F.relu(x)
    x = F.max_pool2d(x, 2)

    x = F.conv2d(
        x,
        fp32_weights["conv3"],
        fp32_biases["conv3"]
    )

    x = F.relu(x)

    x = torch.flatten(x, 1)

    x = F.linear(
        x,
        fp32_weights["fc1"],
        fp32_biases["fc1"]
    )

    x = F.relu(x)

    x = F.linear(
        x,
        fp32_weights["fc2"],
        fp32_biases["fc2"]
    )

    return x


# ============================================================
# 11. W4A4–INT32前向推理
# ============================================================

def w4a4_forward(images):
    accumulator_maximum = {}

    # 输入量化为4位
    input_scale = activation_scales["input"]

    x = quantize_activation(
        images,
        input_scale
    )

    # --------------------------------------------------------
    # Conv1
    # --------------------------------------------------------

    accumulator = F.conv2d(
        x,
        int4_weights["conv1"],
        bias=None
    )

    accumulator_maximum["conv1"] = int(
        accumulator.abs().max().item()
    )

    x = requantize_accumulator(
        accumulator,
        input_scale,
        get_weight_scale("conv1"),
        activation_scales["conv1_relu"],
        fp32_biases["conv1"]
    )

    x = torch.clamp(x, min=0)
    x = F.max_pool2d(x, 2)

    # --------------------------------------------------------
    # Conv2
    # --------------------------------------------------------

    accumulator = F.conv2d(
        x,
        int4_weights["conv2"],
        bias=None
    )

    accumulator_maximum["conv2"] = int(
        accumulator.abs().max().item()
    )

    x = requantize_accumulator(
        accumulator,
        activation_scales["pool1"],
        get_weight_scale("conv2"),
        activation_scales["conv2_relu"],
        fp32_biases["conv2"]
    )

    x = torch.clamp(x, min=0)
    x = F.max_pool2d(x, 2)

    # --------------------------------------------------------
    # Conv3
    # --------------------------------------------------------

    accumulator = F.conv2d(
        x,
        int4_weights["conv3"],
        bias=None
    )

    accumulator_maximum["conv3"] = int(
        accumulator.abs().max().item()
    )

    x = requantize_accumulator(
        accumulator,
        activation_scales["pool2"],
        get_weight_scale("conv3"),
        activation_scales["conv3_relu"],
        fp32_biases["conv3"]
    )

    x = torch.clamp(x, min=0)
    x = torch.flatten(x, 1)

    # --------------------------------------------------------
    # FC1
    # --------------------------------------------------------

    accumulator = F.linear(
        x,
        int4_weights["fc1"],
        bias=None
    )

    accumulator_maximum["fc1"] = int(
        accumulator.abs().max().item()
    )

    x = requantize_accumulator(
        accumulator,
        activation_scales["conv3_relu"],
        get_weight_scale("fc1"),
        activation_scales["fc1_relu"],
        fp32_biases["fc1"]
    )

    x = torch.clamp(x, min=0)

    # --------------------------------------------------------
    # FC2
    # --------------------------------------------------------

    accumulator = F.linear(
        x,
        int4_weights["fc2"],
        bias=None
    )

    accumulator_maximum["fc2"] = int(
        accumulator.abs().max().item()
    )

    x = requantize_accumulator(
        accumulator,
        activation_scales["fc1_relu"],
        get_weight_scale("fc2"),
        activation_scales["fc2_output"],
        fp32_biases["fc2"]
    )

    return x, accumulator_maximum


# ============================================================
# 12. 准备MNIST测试集
# ============================================================

print("正在准备MNIST测试集……")

transform = transforms.Compose([
    transforms.Pad(2),
    transforms.ToTensor(),
    transforms.Normalize(
        (0.1307,),
        (0.3081,)
    ),
])

test_dataset = datasets.MNIST(
    root=DATA_DIR,
    train=False,
    download=True,
    transform=transform
)

test_loader = DataLoader(
    test_dataset,
    batch_size=256,
    shuffle=False,
    num_workers=0
)

print(f"测试图片数量：{len(test_dataset)}")


# ============================================================
# 13. 运行完整测试
# ============================================================

fp32_correct = 0
w4a4_correct = 0
prediction_same = 0
total = 0

global_accumulator_maximum = {
    "conv1": 0,
    "conv2": 0,
    "conv3": 0,
    "fc1": 0,
    "fc2": 0,
}

print("开始进行FP32与W4A4–INT32对比测试……")

with torch.no_grad():
    for batch_index, (images, labels) in enumerate(
        test_loader
    ):
        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        fp32_logits = fp32_forward(images)

        w4a4_logits, current_maximum = (
            w4a4_forward(images)
        )

        fp32_prediction = torch.argmax(
            fp32_logits,
            dim=1
        )

        w4a4_prediction = torch.argmax(
            w4a4_logits,
            dim=1
        )

        fp32_correct += (
            fp32_prediction == labels
        ).sum().item()

        w4a4_correct += (
            w4a4_prediction == labels
        ).sum().item()

        prediction_same += (
            fp32_prediction == w4a4_prediction
        ).sum().item()

        total += labels.size(0)

        for layer_name in LAYER_NAMES:
            global_accumulator_maximum[layer_name] = max(
                global_accumulator_maximum[layer_name],
                current_maximum[layer_name]
            )

        if total % 2560 == 0:
            print(f"已测试：{total}/{len(test_dataset)}")


# ============================================================
# 14. 计算最终结果
# ============================================================

fp32_accuracy = (
    100.0 *
    fp32_correct /
    total
)

w4a4_accuracy = (
    100.0 *
    w4a4_correct /
    total
)

accuracy_drop = (
    fp32_accuracy -
    w4a4_accuracy
)

agreement = (
    100.0 *
    prediction_same /
    total
)

overflow_passed = all(
    value <= INT32_MAX
    for value in global_accumulator_maximum.values()
)


# ============================================================
# 15. 显示测试结果
# ============================================================

print("=" * 70)
print("W4A4–INT32测试结果")
print("=" * 70)

print(f"测试图片数量：       {total}")
print(f"FP32正确数量：       {fp32_correct}")
print(f"W4A4正确数量：       {w4a4_correct}")
print(f"FP32准确率：         {fp32_accuracy:.2f}%")
print(f"W4A4–INT32准确率：   {w4a4_accuracy:.2f}%")
print(f"准确率下降：         {accuracy_drop:.2f}个百分点")
print(f"与FP32预测一致率：   {agreement:.2f}%")

print("-" * 70)
print("各层INT32累加器最大绝对值：")

for layer_name in LAYER_NAMES:
    print(
        f"{layer_name:<6} "
        f"{global_accumulator_maximum[layer_name]}"
    )

print(
    "INT32溢出检查：     "
    f"{'PASS' if overflow_passed else 'FAIL'}"
)

print("=" * 70)


# ============================================================
# 16. 保存JSON结果
# ============================================================
result = {
    "configuration": "W4A4-INT32",
    "weight_bits": 4,
    "activation_bits": 4,
    "accumulator_bits": 32,
    "test_samples": int(total),
    "fp32_correct": int(fp32_correct),
    "w4a4_correct": int(w4a4_correct),
    "fp32_accuracy_percent": float(fp32_accuracy),
    "w4a4_accuracy_percent": float(w4a4_accuracy),
    "accuracy_drop_percentage_points": float(
        accuracy_drop
    ),
    "prediction_agreement_percent": float(
        agreement
    ),
    "accumulator_max_abs": {
        name: int(value)
        for name, value
        in global_accumulator_maximum.items()
    },
    "int32_overflow_check": (
        "PASS" if overflow_passed else "FAIL"
    ),
}

with open(
    JSON_RESULT_PATH,
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        result,
        file,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# 17. 保存CSV结果
# ============================================================

fieldnames = [
    "Configuration",
    "WeightBits",
    "ActivationBits",
    "AccumulatorBits",
    "Total",
    "FP32Correct",
    "QuantizedCorrect",
    "FP32Accuracy",
    "QuantizedAccuracy",
    "AccuracyDrop",
    "PredictionAgreement",
    "INT32OverflowCheck",
]

csv_row = {
    "Configuration": "W4A4-INT32",
    "WeightBits": 4,
    "ActivationBits": 4,
    "AccumulatorBits": 32,
    "Total": int(total),
    "FP32Correct": int(fp32_correct),
    "QuantizedCorrect": int(w4a4_correct),
    "FP32Accuracy": float(fp32_accuracy),
    "QuantizedAccuracy": float(w4a4_accuracy),
    "AccuracyDrop": float(accuracy_drop),
    "PredictionAgreement": float(agreement),
    "INT32OverflowCheck": (
        "PASS" if overflow_passed else "FAIL"
    ),
}

with open(
    CSV_RESULT_PATH,
    "w",
    newline="",
    encoding="utf-8"
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerow(csv_row)


# ============================================================
# 18. 完成
# ============================================================

print("结果已经保存到：")
print(JSON_RESULT_PATH)
print(CSV_RESULT_PATH)

if overflow_passed:
    print("W4A4–INT32推理评估完成。[PASS]")
else:
    print("W4A4–INT32推理评估完成，但存在溢出。[FAIL]")