#!/usr/bin/env python3
"""Preprocess photographed digit sheets. Extraction only; labels are supplied, never inferred."""

import argparse
import csv
import hashlib
import json
import re
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def read_image(path):
    # Respect phone EXIF orientation before finding rows and columns.
    from PIL import ImageOps

    with Image.open(path) as image:
        return cv2.cvtColor(
            np.array(ImageOps.exif_transpose(image).convert("RGB")), cv2.COLOR_RGB2BGR
        )


def save_image(path, array):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), array):
        raise RuntimeError(f"Cannot write {path}")


def order_corners(points):
    points = np.asarray(points, np.float32).reshape(4, 2)
    center = points.mean(axis=0)
    points = points[
        np.argsort(np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0]))
    ]
    points = np.roll(points, -np.argmin(points.sum(axis=1)), axis=0)
    return points


def rectify(image):
    height, width = image.shape[:2]
    # Limit detection cost while keeping full-resolution output.
    scale = min(1.0, 1600 / max(height, width))
    small = cv2.resize(image, None, fx=scale, fy=scale)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    # Paper can occupy almost the entire frame. Otsu then separates lit paper
    # from shaded paper instead of paper from desk. Use a conservative dark
    # background cutoff relative to the bright paper, retaining paper shadows.
    paper_level = float(np.percentile(gray, 90))
    threshold = float(np.clip(paper_level * 0.45, 45, 110))
    _, mask = cv2.threshold(
        cv2.GaussianBlur(gray, (9, 9), 0), threshold, 255, cv2.THRESH_BINARY
    )
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError(
            "No paper found; photograph the whole light-colored sheet on a dark surface."
        )
    contour = max(contours, key=cv2.contourArea)
    if cv2.contourArea(contour) < 0.25 * small.shape[0] * small.shape[1]:
        raise ValueError(
            "Paper occupies too little of image, or background is not distinguishable."
        )
    hull = cv2.convexHull(contour)
    corners = None
    for tolerance in (0.01, 0.015, 0.02, 0.03):
        polygon = cv2.approxPolyDP(hull, tolerance * cv2.arcLength(hull, True), True)
        if len(polygon) == 4:
            corners = order_corners(polygon.reshape(4, 2) / scale)
            break
    if corners is None:
        raise ValueError(
            "Paper outline is not a quadrilateral. Flatten the sheet and include all four corners."
        )
    tl, tr, br, bl = corners
    out_w = round(max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl)))
    out_h = round(max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr)))
    matrix = cv2.getPerspectiveTransform(
        corners,
        np.float32([[0, 0], [out_w - 1, 0], [out_w - 1, out_h - 1], [0, out_h - 1]]),
    )
    page = cv2.warpPerspective(image, matrix, (out_w, out_h))
    warning = ""
    if (
        np.any(corners[:, 0] < width * 0.008)
        or np.any(corners[:, 0] > width * 0.992)
        or np.any(corners[:, 1] < height * 0.008)
        or np.any(corners[:, 1] > height * 0.992)
    ):
        warning = "paper_near_image_edge"
    overlay = image.copy()
    cv2.polylines(overlay, [corners.astype(np.int32)], True, (0, 180, 0), 5)
    return page, corners, matrix, overlay, warning


def extract_digit(cell):
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    # Estimate slowly varying paper brightness, suppressing folds and shadows.
    side = max(15, int(min(gray.shape) * 0.16)) | 1
    background = cv2.morphologyEx(
        gray,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (side, side)),
    )
    corrected = cv2.divide(gray, np.maximum(background, 1), scale=255)
    binary = ((corrected < 170) & (gray < 190)).astype(np.uint8) * 255
    # Grid boundaries/folds at the cell edges must not become digits.
    margin_y, margin_x = (
        max(2, round(gray.shape[0] * 0.04)),
        max(2, round(gray.shape[1] * 0.04)),
    )
    interior = binary.copy()
    interior[:margin_y] = 0
    interior[-margin_y:] = 0
    interior[:, :margin_x] = 0
    interior[:, -margin_x:] = 0
    n, labels, stats, centers = cv2.connectedComponentsWithStats(interior)
    minimum = max(15, gray.size * 0.0008)
    valid = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= minimum]
    if not valid:
        return None, None, None, ["no_ink_detected"]
    largest = max(valid, key=lambda i: stats[i, cv2.CC_STAT_AREA])
    x, y, w, h, area = stats[largest]
    if h < gray.shape[0] * 0.07 or w < 2:
        return None, None, None, ["ink_too_small"]
    selected = [largest]
    flags = []
    # Retain nearby detached strokes; flag meaningful extra ink for human review.
    for i in valid:
        if i == largest:
            continue
        ix, iy, iw, ih, ia = stats[i]
        if ia < area * 0.04:
            continue
        gap_x = max(x - (ix + iw), ix - (x + w), 0)
        gap_y = max(y - (iy + ih), iy - (y + h), 0)
        if gap_x < max(w, h) * 0.3 and gap_y < max(w, h) * 0.3:
            selected.append(i)
            flags.append("detached_stroke")
        else:
            flags.append("extra_ink_ignored")
    foreground = np.isin(labels, selected)
    ys, xs = np.where(foreground)
    x0, x1, y0, y1 = int(xs.min()), int(xs.max() + 1), int(ys.min()), int(ys.max() + 1)
    if (
        x0 <= margin_x + 1
        or y0 <= margin_y + 1
        or x1 >= gray.shape[1] - margin_x - 1
        or y1 >= gray.shape[0] - margin_y - 1
    ):
        flags.append("ink_near_cell_edge")
    # Keep grayscale stroke variation, with a clean zero background.
    ink = np.where(foreground, 255 - corrected, 0).astype(np.uint8)
    roi = ink[y0:y1, x0:x1]
    ratio = 20 / max(roi.shape)
    rw, rh = max(1, round(roi.shape[1] * ratio)), max(1, round(roi.shape[0] * ratio))
    resized = cv2.resize(
        roi, (rw, rh), interpolation=cv2.INTER_AREA if ratio < 1 else cv2.INTER_LINEAR
    )
    canvas = np.zeros((28, 28), np.uint8)
    left, top = (28 - rw) // 2, (28 - rh) // 2
    canvas[top : top + rh, left : left + rw] = resized
    # Center by intensity mass without clipping the digit.
    mass = cv2.moments(canvas)
    if mass["m00"]:
        dx = int(
            np.clip(round(13.5 - mass["m10"] / mass["m00"]), -left, 28 - left - rw)
        )
        dy = int(np.clip(round(13.5 - mass["m01"] / mass["m00"]), -top, 28 - top - rh))
        canvas = cv2.warpAffine(canvas, np.float32([[1, 0, dx], [0, 1, dy]]), (28, 28))
    return canvas, roi, (x0, y0, x1, y1), sorted(set(flags))


def make_preview(entries, rows, cols, target):
    tile_w, tile_h = 250, 210
    preview = Image.new("RGB", (cols * tile_w, rows * tile_h + 48), "#edf1f5")
    draw = ImageDraw.Draw(preview)
    draw.text(
        (14, 14),
        "EXTRACTION REVIEW | supplied labels; no model inference",
        fill="#13273a",
    )
    for index, entry in enumerate(entries):
        ox, oy = (index % cols) * tile_w, (index // cols) * tile_h + 48
        draw.rounded_rectangle(
            (ox + 5, oy + 5, ox + tile_w - 5, oy + tile_h - 5), 8, fill="white"
        )
        raw = Image.fromarray(cv2.cvtColor(entry["cell"], cv2.COLOR_BGR2RGB))
        raw.thumbnail((115, 135))
        preview.paste(
            raw, (ox + 10 + (115 - raw.width) // 2, oy + 36 + (135 - raw.height) // 2)
        )
        if entry["digit"] is not None:
            processed = (
                Image.fromarray(entry["digit"])
                .convert("RGB")
                .resize((112, 112), Image.Resampling.NEAREST)
            )
            preview.paste(processed, (ox + 130, oy + 45))
        draw.text(
            (ox + 12, oy + 14),
            f"R{index // cols + 1} C{index % cols + 1} | label {entry['label']}",
            fill="#13273a",
        )
        draw.text(
            (ox + 12, oy + 177),
            entry["status"][:33],
            fill="#b34422" if entry["flags"] else "#177146",
        )
    preview.save(target)


def get_labels(path, args):
    count = args.rows * args.cols
    if args.labels is not None:
        labels = args.labels.split(",")
        if len(labels) != count or any(
            x not in list("0123456789") + ["-"] for x in labels
        ):
            raise ValueError(
                f"--labels requires {count} comma-separated digits or - for unused cells."
            )
        return labels
    if args.label is not None:
        return [str(args.label)] * count
    match = re.match(r"^([0-9])(?:_|$)", path.stem)
    if not match:
        raise ValueError(
            f"{path.name}: supply --label / --labels, or name a single-digit page like 6_01.jpg."
        )
    return [match.group(1)] * count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input", type=Path, help="Image, or directory of images (recursive)."
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="New output directory; existing directories are refused.",
    )
    parser.add_argument("--rows", type=int, default=4)
    parser.add_argument("--cols", type=int, default=4)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--label",
        type=int,
        choices=range(10),
        help="Same supplied label for every cell on every page.",
    )
    group.add_argument(
        "--labels", help="Row-major label list for one mixed page; - means unused."
    )
    args = parser.parse_args()
    if args.rows < 1 or args.cols < 1:
        parser.error("rows and cols must be positive")
    paths = (
        sorted(p for p in args.input.rglob("*") if p.suffix.lower() in EXTENSIONS)
        if args.input.is_dir()
        else [args.input]
    )
    if not paths or not all(p.is_file() for p in paths):
        parser.error("No input images found")
    if args.labels is not None and len(paths) != 1:
        parser.error("--labels is for one image only")
    # Validate all labels before creating files.
    label_sets = [get_labels(p, args) for p in paths]
    if args.output.exists():
        parser.error(
            "Output already exists; choose a new directory to avoid overwriting or mixing runs."
        )
    args.output.mkdir(parents=True)
    records = []
    page_reports = []
    for source, supplied in zip(paths, label_sets):
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        page_id = f"{source.stem}_{digest[:8]}"
        archive = args.output / "pages" / f"{page_id}{source.suffix.lower()}"
        archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, archive)
        try:
            image = read_image(source)
            page, corners, matrix, overlay, page_warning = rectify(image)
        except Exception as error:
            page_reports.append(
                {"page": str(source), "status": "failed", "error": str(error)}
            )
            print(f"FAILED {source.name}: {error}")
            continue
        save_image(args.output / "review" / f"{page_id}_paper.jpg", overlay)
        annotation = page.copy()
        entries = []
        height, width = page.shape[:2]
        for i, label in enumerate(supplied):
            row, col = divmod(i, args.cols)
            xa, xb = (
                round(col * width / args.cols),
                round((col + 1) * width / args.cols),
            )
            ya, yb = (
                round(row * height / args.rows),
                round((row + 1) * height / args.rows),
            )
            cell = page[ya:yb, xa:xb]
            digit, roi, box, flags = extract_digit(cell)
            sample = f"{label}_{page_id}_r{row + 1:02d}c{col + 1:02d}"
            status = "extracted"
            if label == "-":
                status = "unused" if digit is None else "ink_in_unused_cell"
                flags = [] if digit is None else [status]
            elif digit is None:
                status = "missing_digit"
            elif flags:
                status = "needs_review"
            entry = {
                "cell": cell,
                "digit": digit,
                "label": label,
                "status": status,
                "flags": flags,
            }
            entries.append(entry)
            raw_path = Path("cells") / f"{sample}.png"
            save_image(args.output / raw_path, cell)
            paths_out = {}
            if digit is not None and label != "-":
                padded = np.pad(digit, 2, constant_values=0)
                normalized = (
                    padded.astype(np.float32) / np.float32(255) - np.float32(0.1307)
                ) / np.float32(0.3081)
                for folder, array in [
                    ("processed_28x28", digit),
                    ("input_32x32", padded),
                    ("roi", roi),
                ]:
                    rel = Path(folder) / label / f"{sample}.png"
                    save_image(args.output / rel, array)
                    paths_out[folder] = str(rel)
                numeric = args.output / "normalized_32x32" / label
                numeric.mkdir(parents=True, exist_ok=True)
                np.save(numeric / f"{sample}.npy", normalized)
                np.savetxt(numeric / f"{sample}.txt", normalized, fmt="%.8f")
                paths_out["normalized"] = str(
                    (numeric / f"{sample}.npy").relative_to(args.output)
                )
            cv2.rectangle(annotation, (xa, ya), (xb - 1, yb - 1), (140, 140, 140), 2)
            cv2.putText(
                annotation,
                f"{row + 1},{col + 1} label={label}",
                (xa + 12, ya + 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (180, 70, 20),
                2,
            )
            if box is not None:
                x0, y0, x1, y1 = box
                cv2.rectangle(
                    annotation,
                    (xa + x0 - 4, ya + y0 - 4),
                    (xa + x1 + 4, ya + y1 + 4),
                    (0, 160, 0) if not flags else (0, 60, 220),
                    3,
                )
            records.append(
                {
                    "sample_id": sample,
                    "page_file": str(archive.relative_to(args.output)),
                    "source_sha256": digest,
                    "row": row + 1,
                    "col": col + 1,
                    "true_label": label,
                    "label_source": "supplied_position"
                    if args.labels
                    else "supplied_page_label"
                    if args.label is not None
                    else "filename",
                    "status": status,
                    "flags": ";".join(flags),
                    "human_reviewed": False,
                    "page_warning": page_warning,
                    "cell_box_rectified": json.dumps([xa, ya, xb, yb]),
                    "ink_box_in_cell": json.dumps(box),
                    "cell_file": str(raw_path),
                    **paths_out,
                }
            )
        save_image(args.output / "review" / f"{page_id}_regions.jpg", annotation)
        make_preview(
            entries,
            args.rows,
            args.cols,
            args.output / "review" / f"{page_id}_preview.png",
        )
        page_reports.append(
            {
                "page": str(source),
                "page_id": page_id,
                "status": "processed",
                "warning": page_warning,
                "corners": corners.tolist(),
                "perspective_matrix": matrix.tolist(),
                "expected_digits": sum(x != "-" for x in supplied),
                "extracted_digits": sum(
                    e["digit"] is not None and e["label"] != "-" for e in entries
                ),
                "flagged_cells": sum(bool(e["flags"]) for e in entries),
            }
        )
        print(
            f"{source.name}: {page_reports[-1]['extracted_digits']}/{page_reports[-1]['expected_digits']} extracted; {page_reports[-1]['flagged_cells']} flagged cells; {page_warning or 'paper outline OK'}"
        )
    if records:
        fields = list(dict.fromkeys(k for r in records for k in r))
        with (args.output / "preprocess_manifest.csv").open(
            "w", newline="", encoding="utf-8-sig"
        ) as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(records)
    counts = {
        str(i): sum(
            r["true_label"] == str(i) and bool(r.get("processed_28x28"))
            for r in records
        )
        for i in range(10)
    }
    report = {
        "stage": "preprocessing",
        "rows": args.rows,
        "cols": args.cols,
        "class_counts": counts,
        "pages": page_reports,
        "preprocessing": {
            "foreground": "white_on_black",
            "digit_long_side": 20,
            "centering": "intensity_mass",
            "canvas": 28,
            "padding_before_normalization": 2,
            "mean": 0.1307,
            "std": 0.3081,
            "dtype": "float32",
        },
        "notice": "Extraction only. Labels are supplied, not recognized. Model/HLS input convention still needs B/C confirmation. Review all previews before using dataset.",
    }
    (args.output / "preprocess_summary.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("Class counts:", counts)
    print("Preprocessing output:", args.output.resolve())
    if any(p["status"] == "failed" for p in page_reports):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
