from pathlib import Path
import json

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms

from model import LeNet5


base_dir = Path(__file__).resolve().parent
weight_path = base_dir / "lenet5_fp32_from_hls.pth"
data_dir = base_dir / "data"
output_path = base_dir / "activation_calibration.json"

# 与FP32模型完全相同的数据预处理
transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

print("正在准备激活值校准数据……")

train_dataset = datasets.MNIST(
    root=data_dir,
    train=True,
    download=True,
    transform=transform
)

# 只取前1024张训练图片进行校准
calibration_dataset = Subset(train_dataset, range(1024))

calibration_loader = DataLoader(
    calibration_dataset,
    batch_size=128,
    shuffle=False,
    num_workers=0
)

# 校准过程使用CPU，更稳定
device = torch.device("cpu")

model = LeNet5()
state_dict = torch.load(weight_path, map_location="cpu")
model.load_state_dict(state_dict)
model = model.to(device)
model.eval()

# 保存各位置观察到的最大绝对值
max_abs = {
    "input": 0.0,
    "conv1_relu": 0.0,
    "pool1": 0.0,
    "conv2_relu": 0.0,
    "pool2": 0.0,
    "conv3_relu": 0.0,
    "fc1_relu": 0.0,
    "fc2_output": 0.0
}

def update_max(name, tensor):
    current = tensor.detach().abs().max().item()
    if current > max_abs[name]:
        max_abs[name] = current


print("开始校准，共1024张训练图片……")

with torch.no_grad():
    processed = 0

    for images, _ in calibration_loader:
        images = images.to(device)

        update_max("input", images)

        x = F.relu(model.conv1(images))
        update_max("conv1_relu", x)

        x = model.pool1(x)
        update_max("pool1", x)

        x = F.relu(model.conv2(x))
        update_max("conv2_relu", x)

        x = model.pool2(x)
        update_max("pool2", x)

        x = F.relu(model.conv3(x))
        update_max("conv3_relu", x)

        x = x.view(x.size(0), -1)

        x = F.relu(model.fc1(x))
        update_max("fc1_relu", x)

        x = model.fc2(x)
        update_max("fc2_output", x)

        processed += images.size(0)
        print(f"已校准：{processed}/1024")

# 对称INT8量化范围为-127到127
calibration_result = {}

print("=" * 65)
print("W8A8激活值校准结果")
print("=" * 65)

for name, value in max_abs.items():
    scale = value / 127.0 if value > 0 else 1.0

    calibration_result[name] = {
        "max_abs": value,
        "scale_int8": scale,
        "zero_point": 0,
        "qmin": -127,
        "qmax": 127
    }

    print(
        f"{name:14s} "
        f"max_abs={value:12.6f} "
        f"scale={scale:.10f}"
    )

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(calibration_result, file, indent=4)

print("=" * 65)
print("激活值校准完成。[PASS]")
print("校准参数已保存到：")
print(output_path)