#!/usr/bin/env python3
"""Evaluate normalized 32x32 digit inputs with the supplied LeNet weights.

Saves predictions, class accuracy and error image sheets in the output folder.
"""

import argparse
import csv
from datetime import datetime
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True

DEFAULT_LABELS = list(range(10))
ERRORS_PER_SHEET = 12


def load_model_and_weights(model_source, weights_root):
    spec = importlib.util.spec_from_file_location("lenet5_definition", model_source)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot import model definition: {model_source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    net = module.LeNet5()
    weights_root = Path(weights_root)
    for name, param in net.named_parameters():
        if not name.endswith(".weight"):
            continue
        path = weights_root / f"{name}.txt"
        values = np.loadtxt(path, dtype=np.float32)
        if values.size != param.numel():
            raise ValueError(
                f"{path.name}: expected {param.numel()} values, got {values.size}"
            )
        with torch.no_grad():
            param.copy_(torch.from_numpy(values.reshape(param.shape).copy()))
    net.eval()
    return net


def collect_samples(input_root):
    """Return list of (label:int, path:Path). Labels come from directory names."""
    input_root = Path(input_root)
    samples = []
    for label_dir in sorted(input_root.iterdir()):
        if not label_dir.is_dir():
            continue
        try:
            label = int(label_dir.name)
        except ValueError:
            continue
        for path in sorted(label_dir.glob("*.npy")):
            samples.append((label, path))
    return samples


def softmax_rows(logits):
    # numerically stable softmax over last dim, in float64 for confidence only
    z = logits.astype(np.float64)
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def load_manifest(path):
    """Index preprocessing records by sample_id."""
    with path.open(encoding="utf-8-sig", newline="") as f:
        return {row["sample_id"]: row for row in csv.DictReader(f)}


def resolve_artifact(manifest_path, relative_path):
    """Resolve an image path stored relative to preprocess_manifest.csv."""
    if not relative_path:
        return None
    path = manifest_path.parent / relative_path
    return path if path.is_file() else None


def find_raw_page(page_path, raw_root):
    """Map a rectified name such as 9_02_ab12cd34.jpg back to 9_02.jpg."""
    if page_path is None or raw_root is None:
        return None
    parts = page_path.stem.split("_")
    if len(parts) < 3:
        return None
    candidate = raw_root / ("_".join(parts[:-1]) + page_path.suffix)
    return candidate if candidate.is_file() else None


def load_font(size):
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
    ]
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def thumbnail(path, size, fallback_text):
    """Load an image onto a fixed white tile while keeping its aspect ratio."""
    tile = Image.new("RGB", size, "white")
    if path is None:
        ImageDraw.Draw(tile).text(
            (10, 10), fallback_text, fill="gray", font=load_font(15)
        )
        return tile
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    tile.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return tile


def enlarged_pixels(path, size=(170, 170)):
    """Enlarge a tiny model image without smoothing its pixels."""
    if path is None:
        return thumbnail(None, size, "missing image")
    return (
        Image.open(path)
        .convert("L")
        .resize(size, Image.Resampling.NEAREST)
        .convert("RGB")
    )


def make_error_panel(prediction, record, manifest_path, raw_root):
    """Build one row: raw page, located cell, crop, 28x28 and 32x32 input."""
    width, height = 1420, 260
    panel = Image.new("RGB", (width, height), (245, 245, 245))
    draw = ImageDraw.Draw(panel)
    title_font, label_font = load_font(22), load_font(16)

    title = (
        f"{prediction['sample_id']}   true {prediction['true_label']} -> "
        f"pred {prediction['pred_label']}   confidence {float(prediction['confidence']):.3f}"
    )
    draw.text((8, 5), title, fill="black", font=title_font)

    page_path = resolve_artifact(manifest_path, record.get("page_file", ""))
    raw_path = find_raw_page(page_path, raw_root)
    cell_path = resolve_artifact(manifest_path, record.get("cell_file", ""))
    processed_path = resolve_artifact(manifest_path, record.get("processed_28x28", ""))
    input_path = resolve_artifact(manifest_path, record.get("input_32x32", ""))

    raw_tile = thumbnail(raw_path, (230, 190), "raw page unavailable")
    page_tile = Image.new("RGB", (230, 190), "white")
    if page_path is not None:
        page = Image.open(page_path).convert("RGB")
        try:
            box = json.loads(record.get("cell_box_rectified", ""))
            ImageDraw.Draw(page).rectangle(box, outline="red", width=12)
        except (TypeError, ValueError, json.JSONDecodeError):
            pass
        page.thumbnail(page_tile.size, Image.Resampling.LANCZOS)
        page_tile.paste(
            page,
            (
                (page_tile.width - page.width) // 2,
                (page_tile.height - page.height) // 2,
            ),
        )
    cell_tile = thumbnail(cell_path, (230, 190), "cell unavailable")
    processed_tile = enlarged_pixels(processed_path)
    input_tile = enlarged_pixels(input_path)

    columns = [
        (8, raw_tile, "raw photo"),
        (258, page_tile, "rectified page (red cell)"),
        (508, cell_tile, "cell crop"),
        (758, processed_tile, "processed 28x28"),
        (948, input_tile, "model input 32x32"),
    ]
    for x, image, label in columns:
        panel.paste(image, (x, 38))
        draw.text((x, 232), label, fill=(30, 30, 30), font=label_font)
    return panel, {
        "raw_file": str(raw_path) if raw_path else "",
        "page_file": str(page_path) if page_path else "",
        "row": record.get("row", ""),
        "col": record.get("col", ""),
        "cell_file": str(cell_path) if cell_path else "",
        "processed_28x28": str(processed_path) if processed_path else "",
        "input_32x32": str(input_path) if input_path else "",
    }


def write_error_review(wrong_rows, manifest_path, raw_root, outdir):
    """Write error_cases.csv and one or more visual review sheets."""
    output_columns = [
        "sample_id",
        "true_label",
        "pred_label",
        "confidence",
        "raw_file",
        "page_file",
        "row",
        "col",
        "cell_file",
        "processed_28x28",
        "input_32x32",
    ]
    detail_rows, panels = [], []
    manifest = load_manifest(manifest_path)
    for prediction in wrong_rows:
        record = manifest.get(prediction["sample_id"])
        if record is None:
            detail = {name: "" for name in output_columns}
        else:
            panel, detail = make_error_panel(
                prediction, record, manifest_path, raw_root
            )
            panels.append(panel)
        detail.update(
            {
                name: prediction[name]
                for name in ["sample_id", "true_label", "pred_label", "confidence"]
            }
        )
        detail_rows.append(detail)

    with (outdir / "error_cases.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=output_columns)
        writer.writeheader()
        writer.writerows(detail_rows)

    sheet_paths = []
    for start in range(0, len(panels), ERRORS_PER_SHEET):
        group = panels[start : start + ERRORS_PER_SHEET]
        sheet = Image.new(
            "RGB", (group[0].width, sum(p.height for p in group)), "white"
        )
        y = 0
        for panel in group:
            sheet.paste(panel, (0, y))
            y += panel.height
        suffix = (
            ""
            if len(panels) <= ERRORS_PER_SHEET
            else f"_{start // ERRORS_PER_SHEET + 1:03d}"
        )
        path = outdir / f"error_cases{suffix}.png"
        sheet.save(path)
        sheet_paths.append(path)
    return sheet_paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Root dir with <label>/*.npy model inputs.",
    )
    parser.add_argument(
        "--dataset",
        default="dataset",
        help="Dataset name written into accuracy_summary.csv.",
    )
    parser.add_argument(
        "--condition",
        default="original",
        help="Condition label (original / rotate / blur / ...).",
    )
    parser.add_argument(
        "--parameter",
        default="",
        help="Perturbation parameter string for this condition.",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=None,
        help="Output dir (created). Default results/baseline/<stamp>.",
    )
    parser.add_argument(
        "--model-source",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "work/model.py",
    )
    parser.add_argument(
        "--weights-root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "model/hw_weights",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Preprocessing manifest used to create visual error reports.",
    )
    parser.add_argument(
        "--raw-root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data/raw/dataset",
        help="Original page photos used by the visual error report.",
    )
    parser.add_argument("--device", choices=("auto", "cpu", "mps"), default="auto")
    args = parser.parse_args()

    args.input = args.input.resolve()
    if not args.input.is_dir():
        parser.error(f"Input root does not exist: {args.input}")

    if args.outdir is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        args.outdir = (
            Path(__file__).resolve().parents[1] / "results" / "baseline" / stamp
        )
    args.outdir.mkdir(parents=True, exist_ok=True)

    if args.device == "mps" and not torch.backends.mps.is_available():
        parser.error("MPS was requested but is not available")
    selected_device = (
        ("mps" if torch.backends.mps.is_available() else "cpu")
        if args.device == "auto"
        else args.device
    )
    device = torch.device(selected_device)
    net = load_model_and_weights(args.model_source, args.weights_root).to(device)

    samples = collect_samples(args.input)
    if not samples:
        parser.error(f"No <label>/*.npy files under {args.input}")
    print(
        f"samples={len(samples)}  condition={args.condition!r}  parameter={args.parameter!r}  device={device}",
        flush=True,
    )

    fieldnames = (
        ["sample_id", "file_path", "true_label", "pred_label", "correct", "confidence"]
        + [f"logit_{i}" for i in range(10)]
        + ["condition", "parameter"]
    )

    per_class = {label: {"total": 0, "correct": 0} for label in DEFAULT_LABELS}
    wrong_rows = []

    with (args.outdir / "predictions.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for label, path in samples:
            image = (
                np.load(path, allow_pickle=False)
                .reshape(1, 1, 32, 32)
                .astype(np.float32)
            )
            tensor = torch.from_numpy(image.copy()).to(device)
            with torch.inference_mode():
                logits = net(tensor).detach().cpu().numpy()  # (1, 10)
            pred = int(logits.argmax(axis=1)[0])
            prob = softmax_rows(logits)[0]
            correct = pred == label
            per_class.setdefault(label, {"total": 0, "correct": 0})
            per_class[label]["total"] += 1
            per_class[label]["correct"] += int(correct)
            row = {
                "sample_id": path.stem,
                "file_path": str(path),
                "true_label": label,
                "pred_label": pred,
                "correct": int(correct),
                "confidence": float(prob[pred]),
            }
            for i in range(10):
                row[f"logit_{i}"] = float(logits[0, i])
            row["condition"] = args.condition
            row["parameter"] = args.parameter
            writer.writerow(row)
            if not correct:
                wrong_rows.append(row.copy())
        f.flush()

    total = sum(c["total"] for c in per_class.values())
    correct = sum(c["correct"] for c in per_class.values())
    summary = [
        {
            "dataset": args.dataset,
            "condition": args.condition,
            "parameter": args.parameter,
            "sample_count": total,
            "correct_count": correct,
            "accuracy": correct / total if total else float("nan"),
            "notes": (
                "per-class="
                + ";".join(
                    f"{l}:{per_class[l]['correct']}/{per_class[l]['total']}"
                    for l in sorted(per_class)
                )
                if total
                else ""
            ),
        }
    ]
    with (args.outdir / "accuracy_summary.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as f:
        wcsv = csv.DictWriter(f, fieldnames=list(summary[0]))
        wcsv.writeheader()
        wcsv.writerows(summary)

    manifest_path = args.manifest or args.input.parent / "preprocess_manifest.csv"
    error_sheets = []
    if manifest_path.is_file():
        error_sheets = write_error_review(
            wrong_rows, manifest_path.resolve(), args.raw_root.resolve(), args.outdir
        )
    else:
        print(
            f"warning: no manifest found at {manifest_path}; visual error report skipped",
            file=sys.stderr,
            flush=True,
        )

    meta = {
        "dataset": args.dataset,
        "condition": args.condition,
        "parameter": args.parameter,
        "input_root": str(args.input),
        "device": str(device),
        "model_source": str(args.model_source),
        "weights_root": str(args.weights_root),
        "manifest": str(manifest_path.resolve()) if manifest_path.is_file() else None,
        "raw_root": str(args.raw_root.resolve()),
        "sample_count": total,
        "correct_count": correct,
        "accuracy": correct / total if total else None,
        "error_count": len(wrong_rows),
        "error_review_files": [str(path) for path in error_sheets],
    }
    (args.outdir / "run_meta.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )

    print(f"correct={correct}/{total}  accuracy={correct / total:.4%}", flush=True)
    print(f"predictions.csv     -> {args.outdir / 'predictions.csv'}", flush=True)
    print(f"accuracy_summary.csv-> {args.outdir / 'accuracy_summary.csv'}", flush=True)
    if error_sheets:
        print(
            "error review files  -> " + ", ".join(str(path) for path in error_sheets),
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
