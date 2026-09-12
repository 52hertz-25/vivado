from pathlib import Path
import csv

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from model import LeNet5


base_dir = Path(__file__).resolve().parent
weight_path = base_dir / "lenet5_fp32_from_hls.pth"
data_dir = base_dir / "data"
result_path = base_dir / "accuracy_results.csv"

# 与原模型保持完全相同的预处理
transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

print("正在准备MNIST测试集……")

test_dataset = datasets.MNIST(
    root=data_dir,
    train=False,
    download=True,
    transform=transform
)

# Mac和Thonny环境使用num_workers=0最稳定
test_loader = DataLoader(
    test_dataset,
    batch_size=256,
    shuffle=False,
    num_workers=0
)

# 优先使用苹果MPS加速
if torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")

print("运行设备：", device)
print("测试图片数量：", len(test_dataset))

# 加载FP32模型
model = LeNet5()
state_dict = torch.load(weight_path, map_location="cpu")
model.load_state_dict(state_dict)
model = model.to(device)
model.eval()

correct = 0
total = 0

print("开始测试FP32模型……")

with torch.no_grad():
    for batch_index, (images, labels) in enumerate(test_loader):
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)
        predictions = outputs.argmax(dim=1)

        correct += predictions.eq(labels).sum().item()
        total += labels.size(0)

        if (batch_index + 1) % 10 == 0:
            print(f"已测试：{total}/{len(test_dataset)}")

accuracy = 100.0 * correct / total

print("=" * 50)
print("正确数量：", correct)
print("测试总数：", total)
print(f"FP32测试准确率：{accuracy:.2f}%")
print("=" * 50)

# 保存基准结果，后续加入INT8、INT6和INT4结果
with open(result_path, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([
        "Config",
        "Weight_bits",
        "Activation_bits",
        "Accumulator_bits",
        "Correct",
        "Total",
        "Accuracy_percent"
    ])
    writer.writerow([
        "FP32_baseline",
        32,
        32,
        32,
        correct,
        total,
        f"{accuracy:.4f}"
    ])

print("结果已保存到：")
print(result_path)