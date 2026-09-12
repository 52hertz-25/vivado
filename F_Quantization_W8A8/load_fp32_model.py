from pathlib import Path

import numpy as np
import torch

from model import LeNet5


base_dir = Path(__file__).resolve().parent
weight_dir = base_dir / "hw_weights"

# 创建与HLS结构一致的LeNet模型
model = LeNet5()

# 权重文件与PyTorch层的对应关系
weight_files = {
    "conv1": "conv1.weight.txt",
    "conv2": "conv2.weight.txt",
    "conv3": "conv3.weight.txt",
    "fc1": "fc1.weight.txt",
    "fc2": "fc2.weight.txt",
}

print("开始加载FP32权重")
print("=" * 70)

with torch.no_grad():
    for layer_name, filename in weight_files.items():
        layer = getattr(model, layer_name)
        file_path = weight_dir / filename

        # 读取文本权重
        values = np.loadtxt(file_path, dtype=np.float32)

        # 按PyTorch层需要的形状重新排列
        tensor = torch.from_numpy(values).reshape_as(layer.weight)

        # 写入模型
        layer.weight.copy_(tensor)

        print(
            f"{layer_name:6s} "
            f"形状={str(tuple(layer.weight.shape)):18s} "
            f"最小值={layer.weight.min().item(): .6f} "
            f"最大值={layer.weight.max().item(): .6f}"
        )

model.eval()

total_params = sum(parameter.numel() for parameter in model.parameters())

print("=" * 70)
print("模型参数总数：", total_params)

if total_params == 61470:
    print("FP32模型和权重加载成功。[PASS]")
else:
    print("模型参数数量不正确。[FAIL]")

# 保存成PyTorch权重文件，方便后续量化和测试
output_path = base_dir / "lenet5_fp32_from_hls.pth"
torch.save(model.state_dict(), output_path)

print("已保存FP32权重：")
print(output_path)