#!/usr/bin/env python3
"""Generate reproducible robustness inputs from the canonical 28x28 dataset.

Each labeled variant changes exactly one factor. The transformed 28x28 image is
padded by two pixels and normalized with the same formula as preprocess.py.
Synthetic blank controls are also produced, but remain explicitly unlabeled.
"""

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


MEAN = np.float32(0.1307)
STD = np.float32(0.3081)
IMAGE_SIZE = 28
PADDING = 2
DEFAULT_SEED = 20260907


@dataclass(frozen=True)
class Variant:
    condition: str
    folder: str
    parameter: str
    value: float


LABELED_VARIANTS = (
    Variant("rotation", "angle_m15", "-15deg", -15.0),
    Variant("rotation", "angle_m10", "-10deg", -10.0),
    Variant("rotation", "angle_p10", "+10deg", 10.0),
    Variant("rotation", "angle_p15", "+15deg", 15.0),
    Variant("blur", "kernel_3", "3x3", 3),
    Variant("blur", "kernel_5", "5x5", 5),
    Variant("noise", "sigma_10", "sigma=10/255", 10.0),
    Variant("noise", "sigma_25", "sigma=25/255", 25.0),
    Variant("brightness", "factor_0p7", "0.7x", 0.7),
    Variant("brightness", "factor_1p3", "1.3x", 1.3),
)


def collect_labeled_images(input_root):
    samples = []
    for label_dir in sorted(input_root.iterdir(), key=lambda p: p.name):
        if not label_dir.is_dir() or not label_dir.name.isdigit():
            continue
        label = int(label_dir.name)
        if label not in range(10):
            continue
        samples.extend((label, path) for path in sorted(label_dir.glob("*.png")))
    return samples


def read_grayscale(path):
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Cannot read image: {path}")
    if image.shape != (IMAGE_SIZE, IMAGE_SIZE):
        raise ValueError(f"{path}: expected 28x28, got {image.shape}")
    return image


def sample_rng(seed, sample_id, variant):
    key = f"{seed}:{sample_id}:{variant.condition}:{variant.parameter}".encode()
    local_seed = int.from_bytes(hashlib.sha256(key).digest()[:8], "little")
    return np.random.default_rng(local_seed)


def transform(image, variant, rng):
    if variant.condition == "rotation":
        matrix = cv2.getRotationMatrix2D((13.5, 13.5), variant.value, 1.0)
        return cv2.warpAffine(
            image,
            matrix,
            (IMAGE_SIZE, IMAGE_SIZE),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0,
        )

    if variant.condition == "blur":
        kernel = int(variant.value)
        return cv2.GaussianBlur(image, (kernel, kernel), sigmaX=0)

    if variant.condition == "noise":
        noise = rng.normal(0.0, variant.value, image.shape)
        return (
            np.clip(image.astype(np.float32) + noise, 0, 255).round().astype(np.uint8)
        )

    if variant.condition == "brightness":
        return (
            np.clip(image.astype(np.float32) * variant.value, 0, 255)
            .round()
            .astype(np.uint8)
        )

    raise ValueError(f"Unknown condition: {variant.condition}")


def model_input(processed):
    padded = np.pad(processed, PADDING, constant_values=0)
    normalized = (padded.astype(np.float32) / np.float32(255) - MEAN) / STD
    return padded.astype(np.uint8), normalized.astype(np.float32)


def save_image(path, image):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image):
        raise OSError(f"Failed to save image: {path}")


def save_sample(output_root, variant_root, sample_id, label_folder, processed):
    padded, normalized = model_input(processed)
    processed_path = (
        variant_root / "processed_28x28" / label_folder / f"{sample_id}.png"
    )
    input_path = variant_root / "input_32x32" / label_folder / f"{sample_id}.png"
    normalized_path = (
        variant_root / "normalized_32x32" / label_folder / f"{sample_id}.npy"
    )
    save_image(processed_path, processed)
    save_image(input_path, padded)
    normalized_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(normalized_path, normalized, allow_pickle=False)
    return {
        "processed_28x28": str(processed_path.relative_to(output_root)),
        "input_32x32": str(input_path.relative_to(output_root)),
        "normalized_32x32": str(normalized_path.relative_to(output_root)),
    }


def raw_page_for_sample(sample_id, raw_root):
    parts = sample_id.split("_")
    if len(parts) < 3:
        return ""
    candidate = raw_root / f"{parts[1]}_{parts[2]}.jpg"
    return str(candidate) if candidate.is_file() else ""


def load_font(size):
    for path in (
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
    ):
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def write_preview(variant_root, title, records, output_root, limit=20):
    selected = records[:limit]
    columns, tile_width, tile_height = 5, 150, 150
    rows = max(1, (len(selected) + columns - 1) // columns)
    canvas = Image.new(
        "RGB", (columns * tile_width, 42 + rows * tile_height), "#edf1f5"
    )
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 10), title, fill="#102a43", font=load_font(20))
    for index, record in enumerate(selected):
        x = (index % columns) * tile_width
        y = 42 + (index // columns) * tile_height
        path = output_root / record["processed_28x28"]
        image = (
            Image.open(path).convert("L").resize((112, 112), Image.Resampling.NEAREST)
        )
        canvas.paste(image.convert("RGB"), (x + 19, y + 4))
        label = record["true_label"] if record["true_label"] != "" else "blank"
        draw.text(
            (x + 8, y + 120),
            f"{label} | {record['sample_id'][:15]}",
            fill="#243b53",
            font=load_font(13),
        )
    canvas.save(variant_root / "review.png")


def generate_labeled_variants(samples, input_root, raw_root, output_root, seed):
    all_records = []
    counts = {}
    for variant in LABELED_VARIANTS:
        variant_root = output_root / variant.condition / variant.folder
        variant_records = []
        suffix = f"{variant.condition}_{variant.folder}"
        for label, source_path in samples:
            source_id = source_path.stem
            sample_id = f"{source_id}__{suffix}"
            image = read_grayscale(source_path)
            rng = sample_rng(seed, source_id, variant)
            processed = transform(image, variant, rng)
            paths = save_sample(
                output_root, variant_root, sample_id, str(label), processed
            )
            record = {
                "sample_id": sample_id,
                "source_sample_id": source_id,
                "true_label": label,
                "condition": variant.condition,
                "parameter": variant.parameter,
                "source_file": str(source_path.resolve()),
                "raw_page": raw_page_for_sample(source_id, raw_root),
                **paths,
            }
            variant_records.append(record)
            all_records.append(record)
        counts[f"{variant.condition}/{variant.folder}"] = len(variant_records)
        write_preview(
            variant_root,
            f"{variant.condition} | {variant.parameter} | first {min(20, len(variant_records))} samples",
            variant_records,
            output_root,
        )
    return all_records, counts


def blank_shadow(rng):
    yy, xx = np.mgrid[0:IMAGE_SIZE, 0:IMAGE_SIZE]
    image = np.zeros((IMAGE_SIZE, IMAGE_SIZE), np.float32)
    for _ in range(rng.integers(1, 4)):
        cx, cy = rng.uniform(-5, 33, size=2)
        sx, sy = rng.uniform(7, 20, size=2)
        strength = rng.uniform(8, 45)
        image += strength * np.exp(-(((xx - cx) / sx) ** 2 + ((yy - cy) / sy) ** 2) / 2)
    image += rng.normal(0, 1.5, image.shape)
    return np.clip(image, 0, 70).round().astype(np.uint8)


def blank_clutter(rng):
    image = np.zeros((IMAGE_SIZE, IMAGE_SIZE), np.uint8)
    for _ in range(rng.integers(3, 9)):
        color = int(rng.integers(25, 150))
        thickness = int(rng.integers(1, 3))
        if rng.random() < 0.7:
            p1 = tuple(int(v) for v in rng.integers(0, IMAGE_SIZE, size=2))
            p2 = tuple(int(v) for v in rng.integers(0, IMAGE_SIZE, size=2))
            cv2.line(image, p1, p2, color, thickness, cv2.LINE_AA)
        else:
            center = tuple(int(v) for v in rng.integers(0, IMAGE_SIZE, size=2))
            radius = int(rng.integers(1, 6))
            cv2.circle(image, center, radius, color, thickness, cv2.LINE_AA)
    return image


def generate_blank_controls(output_root, seed, blank_count):
    all_records = []
    counts = {}
    definitions = (
        ("pure_white", 1, lambda _rng: np.zeros((IMAGE_SIZE, IMAGE_SIZE), np.uint8)),
        ("shadow", blank_count, blank_shadow),
        ("clutter", blank_count, blank_clutter),
    )
    for folder, count, generator in definitions:
        variant_root = output_root / "blank" / folder
        records = []
        for index in range(1, count + 1):
            sample_id = f"blank_{folder}_{index:03d}"
            rng = np.random.default_rng(
                int.from_bytes(
                    hashlib.sha256(f"{seed}:{sample_id}".encode()).digest()[:8],
                    "little",
                )
            )
            processed = generator(rng)
            paths = save_sample(
                output_root, variant_root, sample_id, "unlabeled", processed
            )
            record = {
                "sample_id": sample_id,
                "source_sample_id": "",
                "true_label": "",
                "condition": "blank",
                "parameter": folder,
                "source_file": "",
                "raw_page": "",
                **paths,
            }
            records.append(record)
            all_records.append(record)
        counts[f"blank/{folder}"] = len(records)
        write_preview(
            variant_root,
            f"blank | {folder} | {len(records)} samples",
            records,
            output_root,
        )
    return all_records, counts


def write_manifest(output_root, records):
    fields = [
        "sample_id",
        "source_sample_id",
        "true_label",
        "condition",
        "parameter",
        "source_file",
        "raw_page",
        "processed_28x28",
        "input_32x32",
        "normalized_32x32",
    ]
    with (output_root / "robustness_manifest.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def main():
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=project_root / "data/preprocessed/dataset/processed_28x28",
        help="Canonical 28x28 root containing label folders 0 through 9.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root / "data/robustness",
        help="New output directory. It must not already contain files.",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--blank-count",
        type=int,
        default=32,
        help="Number of synthetic shadow and clutter controls; pure blank is stored once.",
    )
    args = parser.parse_args()

    input_root = args.input.resolve()
    output_root = args.output.resolve()
    raw_root = project_root / "data/raw/dataset"
    if not input_root.is_dir():
        parser.error(f"Input directory does not exist: {input_root}")
    if output_root.exists() and any(output_root.iterdir()):
        parser.error(f"Output directory is not empty: {output_root}")
    if args.blank_count < 1:
        parser.error("--blank-count must be at least 1")

    samples = collect_labeled_images(input_root)
    label_counts = {label: sum(y == label for y, _ in samples) for label in range(10)}
    if any(count == 0 for count in label_counts.values()):
        parser.error(f"Every label 0-9 must have samples; found {label_counts}")
    output_root.mkdir(parents=True, exist_ok=True)

    labeled_records, labeled_counts = generate_labeled_variants(
        samples, input_root, raw_root, output_root, args.seed
    )
    blank_records, blank_counts = generate_blank_controls(
        output_root, args.seed, args.blank_count
    )
    records = labeled_records + blank_records
    write_manifest(output_root, records)

    summary = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(input_root),
        "source_sample_count": len(samples),
        "source_label_counts": label_counts,
        "seed": args.seed,
        "normalization": {"padding": PADDING, "mean": float(MEAN), "std": float(STD)},
        "labeled_variant_count": len(LABELED_VARIANTS),
        "labeled_output_count": len(labeled_records),
        "blank_output_count": len(blank_records),
        "counts": {**labeled_counts, **blank_counts},
        "blank_note": (
            "Blank controls are synthetic model-input-level checks. Pure white becomes an "
            "all-zero inverted 28x28 image; shadow and clutter contain no target digit."
        ),
    }
    (output_root / "robustness_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"source samples: {len(samples)}")
    print(f"labeled robustness samples: {len(labeled_records)}")
    print(f"blank controls: {len(blank_records)}")
    print(f"manifest: {output_root / 'robustness_manifest.csv'}")
    print(f"summary:  {output_root / 'robustness_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
