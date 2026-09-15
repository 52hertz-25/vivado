#!/usr/bin/env python3
"""Evaluate LeNet-5 W4A4 on MNIST and retain per-sample evidence.

The model was trained and calibrated with bilinear Resize((32, 32)), so that
pipeline is the default. Pad(2) remains available as a preprocessing ablation.
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
from pathlib import Path
from typing import Callable

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.transforms import InterpolationMode


BASE_DIR = Path(__file__).resolve().parent
FP32_MODEL_PATH = BASE_DIR / "lenet5_fp32_from_hls.pth"
INT4_WEIGHT_DIR = BASE_DIR / "exported_weights" / "int4"
WEIGHT_SCALE_PATH = INT4_WEIGHT_DIR / "weight_scales.json"
ACTIVATION_SCALE_PATH = BASE_DIR / "activation_calibration.json"
DEFAULT_DATA_DIR = BASE_DIR / "data"
HLS_DATA_DIR = BASE_DIR / "hls_w8a8" / "data" / "mnist_w8a8"
HLS_RESULT_PATH = (
    BASE_DIR
    / "hls_w4a4"
    / "reports"
    / "mnist"
    / "w4a4_mnist_10000_results.csv"
)

QMIN = -7
QMAX = 7
INT32_MAX = 2**31 - 1
LAYER_NAMES = ("conv1", "conv2", "conv3", "fc1", "fc2")
Q40_SHIFT = 40
Q40_MULTIPLIERS = {
    "conv1": 32113559987,
    "conv2": 41310957922,
    "conv3": 44103899460,
    "fc1": 78194388213,
    "fc2": 44572774922,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preprocess",
        choices=("resize", "pad"),
        default="resize",
        help="resize is the trained/HLS pipeline; pad is the ablation",
    )
    parser.add_argument(
        "--device",
        choices=("cpu", "mps", "auto"),
        default="cpu",
        help="CPU is the default for deterministic reference evidence",
    )
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="default: results/w4a4_preprocessing_ablation/<pipeline>",
    )
    parser.add_argument(
        "--compare-hls-q40",
        action="store_true",
        help="compare every Resize prediction with the HLS Q40 reference",
    )
    return parser.parse_args()


def select_device(requested: str) -> torch.device:
    if requested == "cpu":
        return torch.device("cpu")
    if requested == "mps":
        if not torch.backends.mps.is_available():
            raise RuntimeError("MPS was requested but is not available")
        return torch.device("mps")
    return torch.device("mps" if torch.backends.mps.is_available() else "cpu")


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def activation_scale(calibration: dict, name: str) -> float:
    item = calibration[name]
    if isinstance(item, dict) and "max_abs" in item:
        maximum = float(item["max_abs"])
    elif isinstance(item, dict) and "scale" in item:
        maximum = float(item["scale"]) * 127.0
    else:
        maximum = float(item) * 127.0
    return maximum / QMAX if maximum > 0 else 1.0


def weight_scale(scales: dict, name: str) -> float:
    item = scales[name]
    return float(item["scale"] if isinstance(item, dict) else item)


def clean_state_dict(checkpoint: object) -> dict[str, torch.Tensor]:
    if isinstance(checkpoint, torch.nn.Module):
        state = checkpoint.state_dict()
    elif isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        state = checkpoint["state_dict"]
    elif isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state = checkpoint["model_state_dict"]
    elif isinstance(checkpoint, dict):
        state = checkpoint
    else:
        raise TypeError("Unsupported FP32 checkpoint format")
    return {key.removeprefix("module."): value for key, value in state.items()}


class W4A4Model:
    def __init__(self, device: torch.device):
        self.device = device
        self.weight_scales = load_json(WEIGHT_SCALE_PATH)
        calibration = load_json(ACTIVATION_SCALE_PATH)
        self.activation_scales = {
            name: activation_scale(calibration, name)
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
        self.int4_weights = {
            name: self._load_int4_weight(name) for name in LAYER_NAMES
        }
        checkpoint = torch.load(
            FP32_MODEL_PATH,
            map_location="cpu",
            weights_only=False,
        )
        state = clean_state_dict(checkpoint)
        self.fp32_weights = {
            name: state[f"{name}.weight"].detach().to(device, torch.float32)
            for name in LAYER_NAMES
        }
        self.fp32_biases = {
            name: (
                state[f"{name}.bias"].detach().to(device, torch.float32)
                if f"{name}.bias" in state
                else None
            )
            for name in LAYER_NAMES
        }

    def _load_int4_weight(self, name: str) -> torch.Tensor:
        path = INT4_WEIGHT_DIR / f"{name}.weight.int4.npy"
        array = np.load(path).astype(np.int8, copy=False)
        if array.min() < QMIN or array.max() > QMAX:
            raise ValueError(f"{name} contains values outside [-7, 7]")
        return torch.from_numpy(array).to(self.device, torch.float32)

    @staticmethod
    def quantize_activation(value: torch.Tensor, scale: float) -> torch.Tensor:
        return torch.round(value / scale).clamp(QMIN, QMAX)

    def requantize_float(
        self,
        accumulator: torch.Tensor,
        layer: str,
        input_scale_name: str,
        output_scale_name: str,
    ) -> torch.Tensor:
        ratio = (
            self.activation_scales[input_scale_name]
            * weight_scale(self.weight_scales, layer)
            / self.activation_scales[output_scale_name]
        )
        return torch.round(accumulator * ratio).clamp(QMIN, QMAX)

    @staticmethod
    def requantize_q40(accumulator: torch.Tensor, layer: str) -> torch.Tensor:
        # FP32 is only an efficient container for exact integer MACs here.
        integer_accumulator = torch.round(accumulator).to(torch.int64)
        product = integer_accumulator * Q40_MULTIPLIERS[layer]
        magnitude = product.abs()
        quotient = magnitude >> Q40_SHIFT
        remainder = magnitude & ((1 << Q40_SHIFT) - 1)
        half = 1 << (Q40_SHIFT - 1)
        increment = (
            (remainder > half)
            | ((remainder == half) & ((quotient & 1) == 1))
        ).to(torch.int64)
        rounded = quotient + increment
        signed = torch.where(product < 0, -rounded, rounded)
        return signed.clamp(QMIN, QMAX).to(torch.float32)

    def fp32_forward(self, images: torch.Tensor) -> torch.Tensor:
        x = F.relu(
            F.conv2d(
                images,
                self.fp32_weights["conv1"],
                self.fp32_biases["conv1"],
            )
        )
        x = F.max_pool2d(x, 2)
        x = F.relu(
            F.conv2d(x, self.fp32_weights["conv2"], self.fp32_biases["conv2"])
        )
        x = F.max_pool2d(x, 2)
        x = F.relu(
            F.conv2d(x, self.fp32_weights["conv3"], self.fp32_biases["conv3"])
        )
        x = F.relu(
            F.linear(
                x.flatten(1),
                self.fp32_weights["fc1"],
                self.fp32_biases["fc1"],
            )
        )
        return F.linear(x, self.fp32_weights["fc2"], self.fp32_biases["fc2"])

    def w4a4_forward(
        self,
        images: torch.Tensor | None = None,
        *,
        quantized_input: torch.Tensor | None = None,
        q40: bool = False,
    ) -> tuple[torch.Tensor, dict[str, int]]:
        if quantized_input is None:
            if images is None:
                raise ValueError("images or quantized_input is required")
            x = self.quantize_activation(images, self.activation_scales["input"])
        else:
            x = quantized_input.to(self.device, torch.float32)

        if q40:
            requantize: Callable[[torch.Tensor, str, str, str], torch.Tensor] = (
                lambda value, layer, _input, _output: self.requantize_q40(
                    value, layer
                )
            )
        else:
            requantize = self.requantize_float

        maxima: dict[str, int] = {}

        accumulator = F.conv2d(x, self.int4_weights["conv1"])
        maxima["conv1"] = int(round(accumulator.abs().max().item()))
        x = requantize(accumulator, "conv1", "input", "conv1_relu").clamp_min(0)
        x = F.max_pool2d(x, 2)

        accumulator = F.conv2d(x, self.int4_weights["conv2"])
        maxima["conv2"] = int(round(accumulator.abs().max().item()))
        x = requantize(accumulator, "conv2", "pool1", "conv2_relu").clamp_min(0)
        x = F.max_pool2d(x, 2)

        accumulator = F.conv2d(x, self.int4_weights["conv3"])
        maxima["conv3"] = int(round(accumulator.abs().max().item()))
        x = requantize(accumulator, "conv3", "pool2", "conv3_relu").clamp_min(0)

        accumulator = F.linear(x.flatten(1), self.int4_weights["fc1"])
        maxima["fc1"] = int(round(accumulator.abs().max().item()))
        x = requantize(accumulator, "fc1", "conv3_relu", "fc1_relu").clamp_min(0)

        accumulator = F.linear(x, self.int4_weights["fc2"])
        maxima["fc2"] = int(round(accumulator.abs().max().item()))
        logits = requantize(accumulator, "fc2", "fc1_relu", "fc2_output")
        return logits, maxima


def build_transform(mode: str) -> transforms.Compose:
    first_step = (
        transforms.Resize(
            (32, 32),
            interpolation=InterpolationMode.BILINEAR,
            antialias=True,
        )
        if mode == "resize"
        else transforms.Pad(2)
    )
    return transforms.Compose(
        [
            first_step,
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,)),
        ]
    )


def load_hls_inputs() -> tuple[np.ndarray, np.ndarray]:
    images = np.fromfile(
        HLS_DATA_DIR / "mnist_test_32x32.bin", dtype=np.uint8
    ).reshape(-1, 1, 32, 32)
    labels = np.fromfile(HLS_DATA_DIR / "mnist_test_labels.bin", dtype=np.uint8)
    if len(images) != len(labels):
        raise ValueError("HLS image and label counts differ")
    return images, labels


def quantize_hls_pixels(pixels: np.ndarray, input_scale: float) -> np.ndarray:
    normalized = (pixels.astype(np.float64) / 255.0 - 0.1307) / 0.3081
    return np.clip(np.rint(normalized / input_scale), QMIN, QMAX).astype(np.int8)


def confusion_matrix(labels: list[int], predictions: list[int]) -> np.ndarray:
    matrix = np.zeros((10, 10), dtype=np.int64)
    for expected, predicted in zip(labels, predictions):
        matrix[expected, predicted] += 1
    return matrix


def read_hls_confusion(path: Path) -> np.ndarray:
    rows = list(csv.reader(path.open(encoding="utf-8-sig")))
    start = next(
        i for i, row in enumerate(rows) if row and row[0].startswith("expected")
    )
    matrix = np.zeros((10, 10), dtype=np.int64)
    for row in rows[start + 1 : start + 11]:
        matrix[int(row[0])] = [int(value) for value in row[1:11]]
    return matrix


def write_confusion(path: Path, matrix: np.ndarray) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["expected\\predicted", *range(10)])
        for expected in range(10):
            writer.writerow([expected, *matrix[expected].tolist()])


def main() -> None:
    args = parse_args()
    if args.batch_size <= 0:
        raise ValueError("--batch-size must be positive")
    if args.compare_hls_q40 and args.preprocess != "resize":
        raise ValueError("--compare-hls-q40 requires --preprocess resize")
    if args.compare_hls_q40 and args.device != "cpu":
        raise ValueError("--compare-hls-q40 requires --device cpu")

    device = select_device(args.device)
    output_dir = args.output_dir or (
        BASE_DIR / "results" / "w4a4_preprocessing_ablation" / args.preprocess
    )
    if not output_dir.is_absolute():
        output_dir = BASE_DIR / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset = datasets.MNIST(
        root=args.data_dir,
        train=False,
        download=True,
        transform=build_transform(args.preprocess),
    )
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
    )
    model = W4A4Model(device)

    hls_images: np.ndarray | None = None
    hls_labels: np.ndarray | None = None
    if args.compare_hls_q40:
        hls_images, hls_labels = load_hls_inputs()
        if len(hls_images) != len(dataset):
            raise ValueError("HLS and torchvision datasets have different lengths")

    records: list[dict] = []
    labels_all: list[int] = []
    fp32_predictions: list[int] = []
    w4a4_predictions: list[int] = []
    hls_predictions: list[int] = []
    maxima = {name: 0 for name in LAYER_NAMES}
    hls_input_mismatches = 0
    hls_logit_element_mismatches = 0
    hls_logit_vector_mismatches = 0
    offset = 0

    print(f"Device: {device}; preprocessing: {args.preprocess}; samples: {len(dataset)}")
    with torch.no_grad():
        for images, labels in loader:
            batch_size = len(labels)
            images = images.to(device)
            labels = labels.to(device)
            fp32_logits = model.fp32_forward(images)
            w4a4_logits, batch_maxima = model.w4a4_forward(images)
            fp32_pred = fp32_logits.argmax(dim=1)
            w4a4_pred = w4a4_logits.argmax(dim=1)

            hls_pred: torch.Tensor | None = None
            hls_logits: torch.Tensor | None = None
            if hls_images is not None and hls_labels is not None:
                expected_labels = hls_labels[offset : offset + batch_size]
                if not np.array_equal(expected_labels, labels.cpu().numpy()):
                    raise ValueError(f"Label mismatch at sample {offset}")
                hls_input = quantize_hls_pixels(
                    hls_images[offset : offset + batch_size],
                    model.activation_scales["input"],
                )
                software_input = model.quantize_activation(
                    images,
                    model.activation_scales["input"],
                ).cpu().numpy().astype(np.int8)
                hls_input_mismatches += int(
                    np.count_nonzero(hls_input != software_input)
                )
                hls_logits, hls_maxima = model.w4a4_forward(
                    quantized_input=torch.from_numpy(hls_input),
                    q40=True,
                )
                hls_pred = hls_logits.argmax(dim=1)
                logit_mismatch = w4a4_logits != hls_logits
                hls_logit_element_mismatches += int(logit_mismatch.sum().item())
                hls_logit_vector_mismatches += int(
                    logit_mismatch.any(dim=1).sum().item()
                )
                for name in LAYER_NAMES:
                    maxima[name] = max(maxima[name], hls_maxima[name])

            for name in LAYER_NAMES:
                maxima[name] = max(maxima[name], batch_maxima[name])

            labels_cpu = labels.cpu().tolist()
            fp32_cpu = fp32_pred.cpu().tolist()
            w4a4_cpu = w4a4_pred.cpu().tolist()
            w4a4_logits_cpu = w4a4_logits.cpu().tolist()
            hls_cpu = hls_pred.cpu().tolist() if hls_pred is not None else None
            hls_logits_cpu = hls_logits.cpu().tolist() if hls_logits is not None else None

            for local_index, expected in enumerate(labels_cpu):
                row = {
                    "sample_index": offset + local_index,
                    "preprocessing": args.preprocess,
                    "true_label": expected,
                    "fp32_prediction": fp32_cpu[local_index],
                    "w4a4_prediction": w4a4_cpu[local_index],
                    "fp32_correct": int(fp32_cpu[local_index] == expected),
                    "w4a4_correct": int(w4a4_cpu[local_index] == expected),
                    "fp32_w4a4_same": int(
                        fp32_cpu[local_index] == w4a4_cpu[local_index]
                    ),
                }
                for class_index, value in enumerate(w4a4_logits_cpu[local_index]):
                    row[f"w4a4_logit_{class_index}"] = int(round(value))
                if hls_cpu is not None and hls_logits_cpu is not None:
                    row["hls_q40_prediction"] = hls_cpu[local_index]
                    row["software_hls_same"] = int(
                        w4a4_cpu[local_index] == hls_cpu[local_index]
                    )
                    for class_index, value in enumerate(
                        hls_logits_cpu[local_index]
                    ):
                        row[f"hls_q40_logit_{class_index}"] = int(round(value))
                records.append(row)

            labels_all.extend(labels_cpu)
            fp32_predictions.extend(fp32_cpu)
            w4a4_predictions.extend(w4a4_cpu)
            if hls_cpu is not None:
                hls_predictions.extend(hls_cpu)
            offset += batch_size
            if offset % 2560 == 0 or offset == len(dataset):
                print(f"Evaluated {offset}/{len(dataset)}")

    total = len(labels_all)
    fp32_correct = sum(a == b for a, b in zip(labels_all, fp32_predictions))
    w4a4_correct = sum(a == b for a, b in zip(labels_all, w4a4_predictions))
    agreement = sum(a == b for a, b in zip(fp32_predictions, w4a4_predictions))
    overflow_passed = all(value <= INT32_MAX for value in maxima.values())
    fp32_accuracy = 100.0 * fp32_correct / total
    w4a4_accuracy = 100.0 * w4a4_correct / total

    result = {
        "configuration": "W4A4-INT32",
        "preprocessing": args.preprocess,
        "preprocessing_description": (
            "bilinear Resize((32, 32)), antialias=True"
            if args.preprocess == "resize"
            else "Pad(2) around the original 28x28 image"
        ),
        "device": str(device),
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "weight_bits": 4,
        "activation_bits": 4,
        "accumulator_bits": 32,
        "test_samples": total,
        "fp32_correct": fp32_correct,
        "w4a4_correct": w4a4_correct,
        "fp32_accuracy_percent": fp32_accuracy,
        "w4a4_accuracy_percent": w4a4_accuracy,
        "accuracy_drop_percentage_points": fp32_accuracy - w4a4_accuracy,
        "prediction_agreement_percent": 100.0 * agreement / total,
        "accumulator_max_abs": maxima,
        "int32_overflow_check": "PASS" if overflow_passed else "FAIL",
    }

    with (output_dir / "w4a4_predictions.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=list(records[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(records)

    matrix = confusion_matrix(labels_all, w4a4_predictions)
    write_confusion(output_dir / "w4a4_confusion_matrix.csv", matrix)

    if hls_predictions:
        hls_matrix = confusion_matrix(labels_all, hls_predictions)
        hls_disagreements = sum(
            a != b for a, b in zip(w4a4_predictions, hls_predictions)
        )
        stored_hls_matrix = read_hls_confusion(HLS_RESULT_PATH)
        comparison = {
            "samples": total,
            "software_hls_prediction_disagreements": hls_disagreements,
            "software_hls_prediction_agreement_percent": (
                100.0 * (total - hls_disagreements) / total
            ),
            "software_hls_input_element_mismatches": hls_input_mismatches,
            "software_hls_logit_element_mismatches": (
                hls_logit_element_mismatches
            ),
            "software_hls_logit_vector_mismatches": (
                hls_logit_vector_mismatches
            ),
            "software_hls_confusion_matrix_equal": bool(
                np.array_equal(matrix, hls_matrix)
            ),
            "q40_stored_hls_confusion_matrix_equal": bool(
                np.array_equal(hls_matrix, stored_hls_matrix)
            ),
            "stored_hls_result": str(HLS_RESULT_PATH.relative_to(BASE_DIR)),
        }
        (output_dir / "hls_comparison.json").write_text(
            json.dumps(comparison, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        result["hls_q40_comparison"] = comparison

    (output_dir / "w4a4_int32_results.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    flat_result = {
        key: json.dumps(value, ensure_ascii=False) if isinstance(value, dict) else value
        for key, value in result.items()
    }
    with (output_dir / "w4a4_accuracy_results.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=list(flat_result),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerow(flat_result)

    print(f"FP32: {fp32_correct}/{total} = {fp32_accuracy:.4f}%")
    print(f"W4A4: {w4a4_correct}/{total} = {w4a4_accuracy:.4f}%")
    print(f"Prediction agreement with FP32: {100.0 * agreement / total:.4f}%")
    if hls_predictions:
        print(f"W4A4 vs HLS Q40 disagreements: {hls_disagreements}/{total}")
    print(f"Results: {output_dir}")


if __name__ == "__main__":
    main()
