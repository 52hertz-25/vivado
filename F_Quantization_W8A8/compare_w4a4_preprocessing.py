#!/usr/bin/env python3
"""Compare the retained Pad(2) ablation with the canonical Resize run."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_ROOT = BASE_DIR / "results" / "w4a4_preprocessing_ablation"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pad",
        type=Path,
        default=DEFAULT_ROOT / "pad" / "w4a4_predictions.csv",
    )
    parser.add_argument(
        "--resize",
        type=Path,
        default=DEFAULT_ROOT / "resize" / "w4a4_predictions.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_ROOT / "comparison",
    )
    return parser.parse_args()


def read_predictions(path: Path) -> dict[int, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    result = {int(row["sample_index"]): row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"Duplicate sample_index in {path}")
    return result


def transition(pad_correct: bool, resize_correct: bool, changed: bool) -> str:
    if pad_correct and resize_correct:
        return "both_correct"
    if pad_correct:
        return "pad_only_correct"
    if resize_correct:
        return "resize_only_correct"
    return "both_wrong_changed" if changed else "both_wrong_same_prediction"


def main() -> None:
    args = parse_args()
    pad = read_predictions(args.pad)
    resize = read_predictions(args.resize)
    if pad.keys() != resize.keys():
        raise ValueError("Pad and Resize sample sets differ")

    output_rows: list[dict] = []
    counts: Counter[str] = Counter()
    for sample_index in sorted(pad):
        left = pad[sample_index]
        right = resize[sample_index]
        if left["true_label"] != right["true_label"]:
            raise ValueError(f"Label mismatch at sample {sample_index}")
        expected = int(left["true_label"])
        pad_prediction = int(left["w4a4_prediction"])
        resize_prediction = int(right["w4a4_prediction"])
        pad_correct = pad_prediction == expected
        resize_correct = resize_prediction == expected
        changed = pad_prediction != resize_prediction
        category = transition(pad_correct, resize_correct, changed)
        counts[category] += 1
        output_rows.append(
            {
                "sample_index": sample_index,
                "true_label": expected,
                "pad_prediction": pad_prediction,
                "resize_prediction": resize_prediction,
                "prediction_changed": int(changed),
                "pad_correct": int(pad_correct),
                "resize_correct": int(resize_correct),
                "transition": category,
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "prediction_comparison.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=list(output_rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(output_rows)

    total = len(output_rows)
    pad_correct_count = sum(row["pad_correct"] for row in output_rows)
    resize_correct_count = sum(row["resize_correct"] for row in output_rows)
    changed_count = sum(row["prediction_changed"] for row in output_rows)
    summary = {
        "samples": total,
        "pad_correct": pad_correct_count,
        "pad_accuracy_percent": 100.0 * pad_correct_count / total,
        "resize_correct": resize_correct_count,
        "resize_accuracy_percent": 100.0 * resize_correct_count / total,
        "resize_minus_pad_accuracy_points": (
            100.0 * (resize_correct_count - pad_correct_count) / total
        ),
        "prediction_changed": changed_count,
        "prediction_changed_percent": 100.0 * changed_count / total,
        "transitions": dict(sorted(counts.items())),
    }
    (args.output_dir / "comparison_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    with (args.output_dir / "transition_summary.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["transition", "sample_count", "percent"])
        for name, count in sorted(counts.items()):
            writer.writerow([name, count, 100.0 * count / total])

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Results: {args.output_dir}")


if __name__ == "__main__":
    main()
