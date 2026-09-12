from pathlib import Path
import json

import numpy as np
import torch


# ============================================================
# 1. 路径设置
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

FP32_MODEL_PATH = BASE_DIR / "lenet5_fp32_from_hls.pth"

OUTPUT_DIR = BASE_DIR / "exported_weights" / "int4"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SCALE_PATH = OUTPUT_DIR / "weight_scales.json"


# ============================================================
# 2. INT4量化参数
# ============================================================

# 使用对称有符号INT4量化
QMIN = -7
QMAX = 7

LAYER_NAMES = [
    "conv1",
    "conv2",
    "conv3",
    "fc1",
    "fc2",
]


# ============================================================
# 3. 读取FP32模型参数
# ============================================================

if not FP32_MODEL_PATH.exists():
    raise FileNotFoundError(
        f"找不到FP32模型文件：\n{FP32_MODEL_PATH}"
    )

print("开始进行INT4权重量化")
print("=" * 70)
print(f"FP32模型文件：{FP32_MODEL_PATH}")
print(f"INT4输出目录：{OUTPUT_DIR}")
print("=" * 70)

checkpoint = torch.load(
    FP32_MODEL_PATH,
    map_location="cpu",
    weights_only=False
)

# 兼容不同的pth保存格式
if isinstance(checkpoint, torch.nn.Module):
    state_dict = checkpoint.state_dict()

elif isinstance(checkpoint, dict):
    if "state_dict" in checkpoint:
        state_dict = checkpoint["state_dict"]
    elif "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
    else:
        state_dict = checkpoint

else:
    raise TypeError(
        "无法识别FP32模型文件的保存格式。"
    )

# 去掉可能存在的 module. 前缀
clean_state_dict = {}

for key, value in state_dict.items():
    clean_key = key

    if clean_key.startswith("module."):
        clean_key = clean_key[len("module."):]

    clean_state_dict[clean_key] = value


# ============================================================
# 4. 逐层执行INT4权重量化
# ============================================================

weight_scales = {}

for layer_name in LAYER_NAMES:
    weight_key = f"{layer_name}.weight"

    if weight_key not in clean_state_dict:
        available_keys = "\n".join(clean_state_dict.keys())

        raise KeyError(
            f"找不到权重：{weight_key}\n"
            f"模型中现有参数名称：\n{available_keys}"
        )

    fp32_weight = clean_state_dict[weight_key]

    if not isinstance(fp32_weight, torch.Tensor):
        fp32_weight = torch.tensor(
            fp32_weight,
            dtype=torch.float32
        )

    fp32_weight = fp32_weight.detach().cpu().float()

    # 计算对称量化缩放系数
    max_abs = float(fp32_weight.abs().max().item())

    if max_abs > 0:
        scale = max_abs / QMAX
    else:
        scale = 1.0

    # FP32转换为INT4数值
    # 实际使用int8容器存储，数值范围限制为[-7, 7]
    int4_weight = torch.round(fp32_weight / scale)
    int4_weight = torch.clamp(
        int4_weight,
        QMIN,
        QMAX
    )
    int4_weight = int4_weight.to(torch.int8)

    # 反量化，用于计算量化误差
    dequantized_weight = (
        int4_weight.to(torch.float32) * scale
    )

    rmse = torch.sqrt(
        torch.mean(
            (fp32_weight - dequantized_weight) ** 2
        )
    ).item()

    int_min = int(int4_weight.min().item())
    int_max = int(int4_weight.max().item())

    # 输出文件路径
    npy_path = (
        OUTPUT_DIR /
        f"{layer_name}.weight.int4.npy"
    )

    txt_path = (
        OUTPUT_DIR /
        f"{layer_name}.weight.int4.txt"
    )

    # 保存NPY文件
    int4_numpy = int4_weight.numpy()

    np.save(
        npy_path,
        int4_numpy
    )

    # 保存TXT文件，便于后续HLS读取
    np.savetxt(
        txt_path,
        int4_numpy.reshape(-1),
        fmt="%d"
    )

    # 保存该层量化参数
    weight_scales[layer_name] = {
        "bits": 4,
        "dtype": "int4",
        "storage_dtype": "int8",
        "qmin": QMIN,
        "qmax": QMAX,
        "zero_point": 0,
        "scale": float(scale),
        "shape": list(fp32_weight.shape),
        "number_of_values": int(fp32_weight.numel()),
        "max_abs_fp32": float(max_abs),
        "integer_min": int_min,
        "integer_max": int_max,
        "rmse": float(rmse),
        "npy_file": npy_path.name,
        "txt_file": txt_path.name,
    }

    print(
        f"{layer_name:<6} "
        f"scale={scale:.10f}  "
        f"整数范围=[{int_min:3d}, {int_max:3d}]  "
        f"RMSE={rmse:.10f}"
    )


# ============================================================
# 5. 保存所有层的缩放系数
# ============================================================

with open(
    SCALE_PATH,
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        weight_scales,
        file,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# 6. 最终检查
# ============================================================

all_passed = True

for layer_name, information in weight_scales.items():
    integer_min = information["integer_min"]
    integer_max = information["integer_max"]

    if integer_min < QMIN or integer_max > QMAX:
        all_passed = False
        print(
            f"[FAIL] {layer_name}超出INT4范围："
            f"[{integer_min}, {integer_max}]"
        )

print("=" * 70)

if all_passed:
    print("INT4权重量化完成。[PASS]")
else:
    print("INT4权重量化失败。[FAIL]")

print(f"量化文件保存在：\n{OUTPUT_DIR}")
print(f"缩放系数保存在：\n{SCALE_PATH}")