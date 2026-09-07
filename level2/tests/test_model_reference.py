#!/usr/bin/env python3
"""在 CPU 或 MPS 上验证 TXT 权重与随包提供的单样本参考结果。

本文件只做四件事：
1. 从 ``work/model.py`` 导入 LeNet5 结构；
2. 读取并恢复五层 TXT 权重；
3. 在指定设备上执行一次前向推理并抓取逐层输出；
4. 将实际输出与 ``model/hw_feature_maps`` 中的参考值比较。

不会训练、下载 MNIST 或生成 PTH。选择 MPS 时不会回退到 CPU。
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import time
import traceback
from typing import Any

# 如果某个算子不支持 MPS，直接报错，避免悄悄转到 CPU。
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "0"
sys.dont_write_bytecode = True

import numpy as np
import torch


WEIGHT_SHAPES = {
    "conv1.weight": (6, 1, 5, 5),
    "conv2.weight": (16, 6, 5, 5),
    "conv3.weight": (120, 16, 5, 5),
    "fc1.weight": (84, 120),
    "fc2.weight": (10, 84),
}

REFERENCE_SHAPES = {
    "conv1": (1, 6, 28, 28),
    "pool1": (1, 6, 14, 14),
    "conv2": (1, 16, 10, 10),
    "pool2": (1, 16, 5, 5),
    "conv3": (1, 120, 1, 1),
    "fc1": (1, 84),
    "fc2": (1, 10),
}

EXPECTED_LABEL = 7
MEAN = np.float32(0.1307)
STD = np.float32(0.3081)


def file_sha256(path: Path) -> str:
    """计算文件哈希，便于确认每次测试使用的是同一批输入。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_model_class(model_source: Path):
    """只导入 LeNet5 类，不执行 model.py 中受 __main__ 保护的训练入口。"""
    spec = importlib.util.spec_from_file_location(
        "supplied_lenet_definition", model_source
    )
    if spec is None or spec.loader is None:
        raise ValueError(f"无法导入模型定义：{model_source}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.LeNet5


def load_txt_weights(model, weights_dir: Path) -> list[dict[str, Any]]:
    """读取五份行主序 TXT，将其恢复为 state_dict 并严格装入模型。"""
    if set(model.state_dict()) != set(WEIGHT_SHAPES):
        raise ValueError("模型参数名称与五份权重文件不完全对应。")

    state_dict = {}
    inventory = []

    for parameter_name, expected_shape in WEIGHT_SHAPES.items():
        weight_path = weights_dir / f"{parameter_name}.txt"
        flat_values = np.loadtxt(weight_path, dtype=np.float32)

        expected_count = int(np.prod(expected_shape))
        if flat_values.size != expected_count:
            raise ValueError(
                f"{weight_path.name} 应有 {expected_count} 个数，"
                f"实际为 {flat_values.size} 个。"
            )
        if not np.isfinite(flat_values).all():
            raise ValueError(f"{weight_path.name} 含有 NaN 或无穷值。")
        if tuple(model.state_dict()[parameter_name].shape) != expected_shape:
            raise ValueError(f"模型中的 {parameter_name} 形状不符合说明。")

        restored = flat_values.reshape(expected_shape, order="C").copy()
        state_dict[parameter_name] = torch.from_numpy(restored)
        inventory.append(
            {
                "name": parameter_name,
                "shape": list(expected_shape),
                "count": expected_count,
                "source": str(weight_path),
                "sha256": file_sha256(weight_path),
            }
        )

    model.load_state_dict(state_dict, strict=True)
    return inventory


def load_golden_input(input_path: Path) -> np.ndarray:
    """读取 32×32 原始像素，并按模型包说明执行一次标准化。"""
    raw_pixels = np.loadtxt(input_path, dtype=np.float32)
    if raw_pixels.size != 32 * 32:
        raise ValueError("参考输入必须包含 1024 个像素。")
    if not np.isfinite(raw_pixels).all():
        raise ValueError("参考输入含有 NaN 或无穷值。")
    if raw_pixels.min() < 0 or raw_pixels.max() > 255:
        raise ValueError("参考输入像素必须位于 0 到 255。")

    image = raw_pixels.reshape(1, 1, 32, 32)
    return (image / np.float32(255) - MEAN) / STD


def load_reference_outputs(reference_dir: Path):
    """读取七个参考数组并检查形状。"""
    outputs = {}
    inventory = []

    for layer_name, expected_shape in REFERENCE_SHAPES.items():
        reference_path = reference_dir / f"{layer_name}.npy"
        array = np.load(reference_path, allow_pickle=False)

        if array.shape != expected_shape:
            raise ValueError(
                f"{reference_path.name} 形状应为 {expected_shape}，"
                f"实际为 {array.shape}。"
            )
        if not np.isfinite(array).all():
            raise ValueError(f"{reference_path.name} 含有 NaN 或无穷值。")

        outputs[layer_name] = array
        inventory.append(
            {
                "layer": layer_name,
                "source": str(reference_path),
                "sha256": file_sha256(reference_path),
            }
        )

    return outputs, inventory


def mps_memory_snapshot() -> dict[str, Any]:
    """记录 MPS 当前内存；这是快照，不是峰值统计。"""
    snapshot = {}
    metric_names = (
        "current_allocated_memory",
        "driver_allocated_memory",
        "recommended_max_memory",
    )

    for metric_name in metric_names:
        metric = getattr(torch.mps, metric_name, None)
        if metric is None:
            continue
        try:
            snapshot[f"{metric_name}_bytes"] = int(metric())
        except RuntimeError as error:
            snapshot[f"{metric_name}_unavailable"] = str(error)

    return snapshot


def synchronize_device(device_name: str) -> None:
    """CPU 运算是同步的；MPS 需要显式等待设备完成。"""
    if device_name == "mps":
        torch.mps.synchronize()


def run_forward_and_capture(
    model, normalized_input: np.ndarray, device_name: str
):
    """把模型和输入放到指定设备，并用 hook 抓取七个模块的输出。"""
    device = torch.device(device_name)
    model = model.to(device)
    input_tensor = torch.from_numpy(normalized_input.copy()).to(device)

    if any(
        parameter.device.type != device_name for parameter in model.parameters()
    ):
        raise RuntimeError(f"模型参数没有全部放到 {device_name}。")
    if input_tensor.device.type != device_name:
        raise RuntimeError(f"输入没有放到 {device_name}。")

    captured_outputs = {}
    layer_devices = {}
    hook_handles = []

    def make_hook(layer_name: str):
        def capture(_module, _inputs, output):
            if output.device.type != device_name:
                raise RuntimeError(f"{layer_name} 没有在 {device_name} 上执行。")
            layer_devices[layer_name] = str(output.device)
            captured_outputs[layer_name] = output.detach().cpu().numpy().copy()

        return capture

    for layer_name in REFERENCE_SHAPES:
        layer = getattr(model, layer_name)
        hook_handles.append(layer.register_forward_hook(make_hook(layer_name)))

    try:
        synchronize_device(device_name)
        started = time.perf_counter()
        with torch.inference_mode():
            logits = model(input_tensor)
        synchronize_device(device_name)
        elapsed_seconds = time.perf_counter() - started
    finally:
        for handle in hook_handles:
            handle.remove()

    return {
        "logits": logits.detach().cpu().numpy(),
        "outputs": captured_outputs,
        "devices": layer_devices,
        "device": str(logits.device),
        "elapsed_seconds": elapsed_seconds,
    }


def capture_point(layer_name: str) -> str:
    """说明 hook 抓到的是网络中哪个位置。"""
    if layer_name.startswith("pool"):
        return "post_relu_maxpool"
    if layer_name == "fc2":
        return "logits"
    return "pre_relu"


def compare_layers(
    actual_outputs: dict[str, np.ndarray],
    reference_outputs: dict[str, np.ndarray],
    layer_devices: dict[str, str],
    atol: float,
    rtol: float,
    output_dir: Path,
) -> list[dict[str, Any]]:
    """逐层比较并保存实际输出。"""
    feature_map_dir = output_dir / "actual_feature_maps"
    feature_map_dir.mkdir()
    comparisons = []

    for layer_name, reference in reference_outputs.items():
        actual = actual_outputs[layer_name]
        if actual.shape != reference.shape:
            raise ValueError(f"{layer_name} 的实际输出形状错误。")
        if not np.isfinite(actual).all():
            raise ValueError(f"{layer_name} 的实际输出含有 NaN 或无穷值。")

        difference = np.abs(
            actual.astype(np.float64) - reference.astype(np.float64)
        )
        allowed_error = atol + rtol * np.abs(reference.astype(np.float64))
        mismatch_mask = difference > allowed_error

        row = {
            "layer": layer_name,
            "shape": str(list(actual.shape)),
            "device": layer_devices[layer_name],
            "capture_point": capture_point(layer_name),
            "max_abs_error": float(difference.max()),
            "mean_abs_error": float(difference.mean()),
            "mismatched_elements": int(mismatch_mask.sum()),
            "total_elements": int(actual.size),
            "passed": not bool(mismatch_mask.any()),
        }
        comparisons.append(row)
        np.save(feature_map_dir / f"{layer_name}.npy", actual)

        result = "PASS" if row["passed"] else "FAIL"
        print(
            f"{layer_name:6s} {result}  "
            f"max_abs={row['max_abs_error']:.8g}  "
            f"mean_abs={row['mean_abs_error']:.8g}  "
            f"mismatched={row['mismatched_elements']}/{actual.size}",
            flush=True,
        )

    return comparisons


def save_layer_comparison(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def validate_reference(args, report: dict[str, Any]) -> int:
    """执行完整验证；返回适合作为命令退出状态的整数。"""
    model_source = args.project / "work/model.py"
    model_bundle = args.project / "model"

    model_class = import_model_class(model_source)
    model = model_class()
    model.eval()

    report["model_source"] = str(model_source)
    report["model_source_sha256"] = file_sha256(model_source)
    report["weights"] = load_txt_weights(model, model_bundle / "hw_weights")
    report["parameter_count"] = sum(p.numel() for p in model.parameters())
    report["parameter_bytes"] = sum(
        p.numel() * p.element_size() for p in model.parameters()
    )
    print(
        f"Parameters: {report['parameter_count']:,}; "
        f"FP32 weights: {report['parameter_bytes'] / 2**20:.4f} MiB",
        flush=True,
    )

    input_path = model_bundle / "Golden_Reference_For_HW/input_raw.txt"
    normalized_input = load_golden_input(input_path)
    reference_outputs, reference_files = load_reference_outputs(
        model_bundle / "hw_feature_maps"
    )
    report["input"] = {
        "source": str(input_path),
        "sha256": file_sha256(input_path),
        "shape": [1, 1, 32, 32],
        "normalization": "(raw/255 - 0.1307)/0.3081",
    }
    report["reference_files"] = reference_files
    report["static_validation"] = (
        "PASS: architecture, weights, input and reference shapes"
    )
    print("File checks: PASS (5 weights, 1 input, 7 reference arrays)", flush=True)

    print(f"Requested device: {args.device}", flush=True)
    if args.device == "mps":
        mps_available = torch.backends.mps.is_available()
        print(
            f"MPS built: {torch.backends.mps.is_built()}; "
            f"available: {mps_available}",
            flush=True,
        )
    else:
        mps_available = False

    if args.device == "mps" and not mps_available:
        report["status"] = "BLOCKED_MPS_UNAVAILABLE"
        report["message"] = (
            "当前进程无法使用 MPS；没有执行前向推理，也没有回退到 CPU。"
        )
        print(report["message"], flush=True)
        return 2

    if args.device == "mps":
        report["memory_before_model_on_mps"] = mps_memory_snapshot()

    inference = run_forward_and_capture(model, normalized_input, args.device)

    if args.device == "mps":
        report["memory_after_forward"] = mps_memory_snapshot()
    report["validation_seconds_including_capture"] = inference["elapsed_seconds"]
    report["actual_device"] = inference["device"]
    report["layer_devices"] = inference["devices"]

    comparisons = compare_layers(
        inference["outputs"],
        reference_outputs,
        inference["devices"],
        args.atol,
        args.rtol,
        args.output,
    )
    save_layer_comparison(args.output / "layer_comparison.csv", comparisons)

    actual_logits = inference["logits"]
    reference_logits = reference_outputs["fc2"]
    predicted_label = int(actual_logits.argmax(axis=1)[0])
    reference_label = int(reference_logits.argmax(axis=1)[0])
    all_layers_passed = all(row["passed"] for row in comparisons)
    overall_passed = (
        all_layers_passed
        and predicted_label == EXPECTED_LABEL
        and reference_label == EXPECTED_LABEL
    )

    report.update(
        {
            "layers": comparisons,
            "predicted_label": predicted_label,
            "reference_predicted_label": reference_label,
            "expected_label": EXPECTED_LABEL,
            "logits": actual_logits.tolist(),
            "reference_logits": reference_logits.tolist(),
            "status": "PASS" if overall_passed else "FAIL",
            "message": (
                "逐层参考对比在声明的误差范围内通过。"
                if overall_passed
                else "严格逐层参考对比失败；请从第一个失败层排查计算精度和生成平台。"
            ),
        }
    )
    print(
        f"Prediction: {predicted_label}; expected: {EXPECTED_LABEL}; "
        f"overall: {report['status']}",
        flush=True,
    )
    return 0 if overall_passed else 1


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="FPGA 项目根目录。",
    )
    parser.add_argument(
        "--device",
        choices=("cpu", "mps"),
        default="mps",
        help="执行网络前向的设备，默认 mps。",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="新的报告目录；为避免覆盖，不允许目录已经存在。",
    )
    parser.add_argument("--atol", type=float, default=1e-4)
    parser.add_argument("--rtol", type=float, default=1e-4)
    args = parser.parse_args()

    args.project = args.project.resolve()
    if not np.isfinite([args.atol, args.rtol]).all():
        parser.error("误差阈值必须为有限数值。")
    if min(args.atol, args.rtol) < 0:
        parser.error("误差阈值不能为负数。")

    if args.output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        args.output = (
            args.project
            / "results/model_reference_test"
            / f"{args.device}_{timestamp}"
        )
    args.output = args.output.resolve()
    if args.output.exists():
        parser.error("报告目录已经存在，请换一个新目录。")

    return args


def make_initial_report(args) -> dict[str, Any]:
    return {
        "stage": "model_reference_validation",
        "requested_device": args.device,
        "status": "ERROR",
        "environment": {
            "python": sys.executable,
            "torch": torch.__version__,
            "numpy": np.__version__,
            "machine": platform.machine(),
            "macos": platform.mac_ver()[0],
            "mps_built": torch.backends.mps.is_built(),
            "mps_available": torch.backends.mps.is_available(),
            "mps_cpu_fallback": "disabled",
        },
        "atol": args.atol,
        "rtol": args.rtol,
        "comparison_rule": (
            "abs(actual-reference) <= atol + rtol*abs(reference)"
        ),
        "scope": (
            "One supplied golden input. Not MNIST accuracy, "
            "not the 320-sample dataset evaluation."
        ),
    }


def main() -> int:
    args = parse_arguments()
    args.output.mkdir(parents=True)
    report = make_initial_report(args)

    try:
        exit_code = validate_reference(args, report)
    except Exception as error:
        report["status"] = "ERROR"
        report["message"] = str(error)
        report["traceback"] = traceback.format_exc()
        print(f"ERROR: {error}", flush=True)
        exit_code = 2

    report_path = args.output / "report.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Report: {report_path}", flush=True)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
