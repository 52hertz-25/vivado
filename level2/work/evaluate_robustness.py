#!/usr/bin/env python3
"""Evaluate every generated robustness group and create nested result reports."""

import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import numpy as np
import torch
from PIL import Image, ImageDraw

sys.dont_write_bytecode = True
from plot_results import write_figures

from evaluate import load_font, load_model_and_weights, softmax_rows


PREDICTION_FIELDS = (
    ["sample_id", "file_path", "true_label", "pred_label", "correct", "confidence"]
    + [f"logit_{i}" for i in range(10)]
    + ["condition", "parameter"]
)
GROUP_ORDER = {
    ("rotation", "-15deg"): 10,
    ("rotation", "-10deg"): 11,
    ("rotation", "+10deg"): 12,
    ("rotation", "+15deg"): 13,
    ("blur", "3x3"): 20,
    ("blur", "5x5"): 21,
    ("noise", "sigma=10/255"): 30,
    ("noise", "sigma=25/255"): 31,
    ("brightness", "0.7x"): 40,
    ("brightness", "1.3x"): 41,
    ("blank", "pure_white"): 50,
    ("blank", "shadow"): 51,
    ("blank", "clutter"): 52,
}
ERRORS_PER_SHEET = 12


def choose_device(requested):
    if requested == "cpu":
        return torch.device("cpu")
    if requested == "mps":
        if not torch.backends.mps.is_available():
            raise RuntimeError("MPS was requested but is not available")
        return torch.device("mps")
    return torch.device("mps" if torch.backends.mps.is_available() else "cpu")


def read_manifest(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"Empty robustness manifest: {path}")
    return rows


def group_folder(record):
    parts = Path(record["normalized_32x32"]).parts
    if len(parts) < 2:
        raise ValueError(f"Invalid normalized path: {record['normalized_32x32']}")
    return parts[1]


def group_records(records):
    groups = defaultdict(list)
    for record in records:
        groups[(record["condition"], record["parameter"], group_folder(record))].append(
            record
        )
    return sorted(
        groups.items(), key=lambda item: (GROUP_ORDER.get(item[0][:2], 999), item[0][2])
    )


def load_batch(records, robustness_root):
    arrays = []
    for record in records:
        path = robustness_root / record["normalized_32x32"]
        array = np.load(path, allow_pickle=False)
        if (
            array.shape != (32, 32)
            or array.dtype != np.float32
            or not np.isfinite(array).all()
        ):
            raise ValueError(f"Invalid model input: {path}")
        arrays.append(array)
    return torch.from_numpy(np.stack(arrays)[:, None].copy())


def infer(net, device, inputs, batch_size):
    outputs = []
    with torch.inference_mode():
        for batch in inputs.split(batch_size):
            outputs.append(net(batch.to(device)).detach().cpu().numpy())
    return np.concatenate(outputs, axis=0)


def prediction_rows(records, logits, robustness_root):
    probabilities = softmax_rows(logits)
    predictions = logits.argmax(axis=1)
    rows = []
    for index, record in enumerate(records):
        has_label = record["true_label"] != ""
        true_label = int(record["true_label"]) if has_label else ""
        pred_label = int(predictions[index])
        row = {
            "sample_id": record["sample_id"],
            "file_path": str((robustness_root / record["normalized_32x32"]).resolve()),
            "true_label": true_label,
            "pred_label": pred_label,
            "correct": int(pred_label == true_label) if has_label else "",
            "confidence": float(probabilities[index, pred_label]),
            "condition": record["condition"],
            "parameter": record["parameter"],
        }
        for label in range(10):
            row[f"logit_{label}"] = float(logits[index, label])
        rows.append(row)
    return rows


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def labeled_summary(rows):
    total = len(rows)
    correct = sum(int(row["correct"]) for row in rows)
    per_class = []
    for label in range(10):
        selected = [row for row in rows if row["true_label"] == label]
        per_class.append(
            f"{label}:{sum(int(row['correct']) for row in selected)}/{len(selected)}"
        )
    return {
        "dataset": "self_collected",
        "condition": rows[0]["condition"],
        "parameter": rows[0]["parameter"],
        "sample_count": total,
        "correct_count": correct,
        "accuracy": correct / total,
        "notes": "per-class=" + ";".join(per_class),
    }


def blank_summary(rows):
    counts = Counter(int(row["pred_label"]) for row in rows)
    confidences = np.array([float(row["confidence"]) for row in rows])
    return {
        "dataset": "synthetic_blank",
        "condition": "blank",
        "parameter": rows[0]["parameter"],
        "sample_count": len(rows),
        "predicted_digit_count": len(rows),
        "mean_confidence": float(confidences.mean()),
        "max_confidence": float(confidences.max()),
        "predicted_class_counts": ";".join(
            f"{label}:{counts[label]}" for label in range(10)
        ),
        "notes": "No target label; report predictions instead of accuracy.",
    }


def image_tile(path, size=(190, 190)):
    image = Image.open(path).convert("L").resize(size, Image.Resampling.NEAREST)
    return image.convert("RGB")


def error_panel(prediction, manifest_record, robustness_root):
    width, height = 900, 280
    panel = Image.new("RGB", (width, height), "#f5f5f5")
    draw = ImageDraw.Draw(panel)
    title = (
        f"True {prediction['true_label']}  /  Predicted {prediction['pred_label']}"
        f"     Confidence {float(prediction['confidence']):.3f}"
    )
    draw.text((12, 8), title, fill="black", font=load_font(20))
    draw.text((12, 34), prediction["sample_id"], fill="#555555", font=load_font(13))
    source_path = Path(manifest_record["source_file"])
    if not source_path.is_absolute():
        source_path = Path(__file__).resolve().parents[1] / source_path
    if not source_path.is_file():
        source_path = (
            robustness_root.parent
            / "preprocessed/dataset/processed_28x28"
            / str(prediction["true_label"])
            / f"{manifest_record['source_sample_id']}.png"
        )
    items = [
        (source_path, "Baseline 28 x 28"),
        (robustness_root / manifest_record["processed_28x28"], "Perturbed 28 x 28"),
        (robustness_root / manifest_record["input_32x32"], "Model input 32 x 32"),
    ]
    for index, (path, label) in enumerate(items):
        x = 8 + index * 245
        panel.paste(image_tile(path), (x, 62))
        draw.text((x, 258), label, fill="#333333", font=load_font(15))
    return panel


def write_error_review(rows, records, robustness_root, outdir):
    record_by_id = {record["sample_id"]: record for record in records}
    wrong = [row for row in rows if row["correct"] == 0]
    details = []
    panels = []
    for row in wrong:
        record = record_by_id[row["sample_id"]]
        details.append(
            {
                "sample_id": row["sample_id"],
                "source_sample_id": record["source_sample_id"],
                "true_label": row["true_label"],
                "pred_label": row["pred_label"],
                "confidence": row["confidence"],
                "source_file": record["source_file"],
                "processed_28x28": str(
                    (robustness_root / record["processed_28x28"]).resolve()
                ),
                "input_32x32": str((robustness_root / record["input_32x32"]).resolve()),
            }
        )
        panels.append(error_panel(row, record, robustness_root))
    fields = [
        "sample_id",
        "source_sample_id",
        "true_label",
        "pred_label",
        "confidence",
        "source_file",
        "processed_28x28",
        "input_32x32",
    ]
    write_csv(outdir / "error_cases.csv", details, fields)
    paths = []
    for start in range(0, len(panels), ERRORS_PER_SHEET):
        selected = panels[start : start + ERRORS_PER_SHEET]
        sheet = Image.new(
            "RGB", (selected[0].width, sum(p.height for p in selected)), "white"
        )
        y = 0
        for panel in selected:
            sheet.paste(panel, (0, y))
            y += panel.height
        suffix = (
            ""
            if len(panels) <= ERRORS_PER_SHEET
            else f"_{start // ERRORS_PER_SHEET + 1:03d}"
        )
        path = outdir / f"error_cases{suffix}.png"
        sheet.save(path)
        paths.append(str(path.resolve()))
    return paths


def read_baseline_summary(path):
    if not path.is_file():
        return None
    with path.open(encoding="utf-8-sig", newline="") as f:
        row = next(csv.DictReader(f), None)
    if row is None:
        return None
    return {
        "dataset": "self_collected",
        "condition": "original",
        "parameter": "",
        "sample_count": int(row["sample_count"]),
        "correct_count": int(row["correct_count"]),
        "accuracy": float(row["accuracy"]),
        "notes": row.get("notes", ""),
    }


def main():
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--robustness-root", type=Path, default=project_root / "data/robustness"
    )
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument(
        "--output", type=Path, default=project_root / "results/robustness"
    )
    parser.add_argument(
        "--baseline-summary",
        type=Path,
        default=project_root / "results/baseline/accuracy_summary.csv",
    )
    parser.add_argument(
        "--model-source", type=Path, default=project_root / "work/model.py"
    )
    parser.add_argument(
        "--weights-root", type=Path, default=project_root / "model/hw_weights"
    )
    parser.add_argument("--device", choices=("auto", "cpu", "mps"), default="auto")
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args()

    robustness_root = args.robustness_root.resolve()
    manifest_path = (
        args.manifest or robustness_root / "robustness_manifest.csv"
    ).resolve()
    output_root = args.output.resolve()
    if not robustness_root.is_dir():
        parser.error(f"Robustness root does not exist: {robustness_root}")
    if not manifest_path.is_file():
        parser.error(f"Manifest does not exist: {manifest_path}")
    if output_root.exists() and any(output_root.iterdir()):
        parser.error(f"Output directory is not empty: {output_root}")
    if args.batch_size < 1:
        parser.error("--batch-size must be at least 1")

    records = read_manifest(manifest_path)
    device = choose_device(args.device)
    net = load_model_and_weights(
        args.model_source.resolve(), args.weights_root.resolve()
    ).to(device)
    output_root.mkdir(parents=True, exist_ok=True)

    all_predictions = []
    accuracy_rows = []
    blank_rows = []
    group_meta = []
    for (condition, parameter, folder), selected in group_records(records):
        inputs = load_batch(selected, robustness_root)
        logits = infer(net, device, inputs, args.batch_size)
        predictions = prediction_rows(selected, logits, robustness_root)
        group_output = output_root / condition / folder
        write_csv(group_output / "predictions.csv", predictions, PREDICTION_FIELDS)
        all_predictions.extend(predictions)

        if condition == "blank":
            summary = blank_summary(predictions)
            blank_rows.append(summary)
            write_csv(group_output / "blank_summary.csv", [summary], list(summary))
            error_files = []
            result_text = (
                f"predictions={Counter(row['pred_label'] for row in predictions)}"
            )
        else:
            summary = labeled_summary(predictions)
            accuracy_rows.append(summary)
            write_csv(group_output / "accuracy_summary.csv", [summary], list(summary))
            error_files = write_error_review(
                predictions, selected, robustness_root, group_output
            )
            result_text = (
                f"correct={summary['correct_count']}/{summary['sample_count']} "
                f"accuracy={summary['accuracy']:.4%}"
            )
        group_meta.append(
            {
                "condition": condition,
                "parameter": parameter,
                "folder": folder,
                "sample_count": len(selected),
                "error_review_files": error_files,
            }
        )
        print(f"{condition:10s} {parameter:14s} {result_text}", flush=True)

    baseline = read_baseline_summary(args.baseline_summary.resolve())
    if baseline is not None:
        accuracy_rows.insert(0, baseline)
    write_csv(output_root / "predictions.csv", all_predictions, PREDICTION_FIELDS)
    write_csv(
        output_root / "accuracy_summary.csv", accuracy_rows, list(accuracy_rows[0])
    )
    write_csv(output_root / "blank_summary.csv", blank_rows, list(blank_rows[0]))
    write_figures(output_root, accuracy_rows, blank_rows)

    meta = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "device": str(device),
        "model_source": str(args.model_source.resolve()),
        "weights_root": str(args.weights_root.resolve()),
        "robustness_root": str(robustness_root),
        "manifest": str(manifest_path),
        "prediction_count": len(all_predictions),
        "labeled_group_count": sum(
            group["condition"] != "blank" for group in group_meta
        ),
        "blank_group_count": sum(group["condition"] == "blank" for group in group_meta),
        "groups": group_meta,
    }
    (output_root / "run_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"combined results: {output_root}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
