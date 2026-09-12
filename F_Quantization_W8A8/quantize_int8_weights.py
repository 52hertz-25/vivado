from pathlib import Path
import json

import numpy as np
import torch

from model import LeNet5


base_dir = Path(__file__).resolve().parent
weight_path = base_dir / "lenet5_fp32_from_hls.pth"

output_dir = base_dir / "exported_weights" / "int8"
output_dir.mkdir(parents=True, exist_ok=True)

scale_path = output_dir / "weight_scales.json"

# 创建模型并加载FP32权重
model = LeNet5()
state_dict = torch.load(weight_path, map_location="cpu")
model.load_state_dict(state_dict)
model.eval()

layer_names = [
    "conv1",
    "conv2",
    "conv3",
    "fc1",
    "fc2"
]

# 对称INT8量化范围
qmin = -127
qmax = 127

scale_results = {}

print("开始进行INT8权重量化")
print("=" * 78)

for layer_name in layer_names:
    layer = getattr(model, layer_name)

    fp32_weight = layer.weight.detach().cpu()

    # 每层使用一个对称量化缩放系数
    max_abs = fp32_weight.abs().max().item()
    scale = max_abs / qmax if max_abs > 0 else 1.0

    # FP32转换为INT8
    int8_weight = torch.round(fp32_weight / scale)
    int8_weight = torch.clamp(int8_weight, qmin, qmax)
    int8_weight = int8_weight.to(torch.int8)

    # 反量化，用于检查量化误差
    dequantized_weight = int8_weight.float() * scale
    difference = dequantized_weight - fp32_weight

    max_error = difference.abs().max().item()
    mean_error = difference.abs().mean().item()
    rmse = torch.sqrt(torch.mean(difference ** 2)).item()

    # 导出为HLS容易读取的一维整数文本
    txt_path = output_dir / f"{layer_name}.weight.int8.txt"

    np.savetxt(
        txt_path,
        int8_weight.numpy().reshape(-1),
        fmt="%d"
    )

    # 同时保存NumPy格式，方便Python再次读取
    npy_path = output_dir / f"{layer_name}.weight.int8.npy"
    np.save(npy_path, int8_weight.numpy())

    scale_results[layer_name] = {
        "bits": 8,
        "dtype": "int8",
        "qmin": qmin,
        "qmax": qmax,
        "zero_point": 0,
        "scale": scale,
        "shape": list(fp32_weight.shape),
        "number_of_values": fp32_weight.numel(),
        "max_abs_fp32": max_abs,
        "max_abs_error": max_error,
        "mean_abs_error": mean_error,
        "rmse": rmse
    }

    print(
        f"{layer_name:6s} "
        f"scale={scale:.10f} "
        f"整数范围=[{int8_weight.min().item():4d}, "
        f"{int8_weight.max().item():4d}] "
        f"RMSE={rmse:.10f}"
    )

# 保存每层量化参数
with open(scale_path, "w", encoding="utf-8") as file:
    json.dump(scale_results, file, indent=4)

print("=" * 78)
print("INT8权重量化完成。[PASS]")
print("量化文件保存在：")
print(output_dir)
print("缩放系数保存在：")
print(scale_path)