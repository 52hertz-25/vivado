#!/usr/bin/env python3
"""Draw report figures from the saved accuracy and blank-control tables."""

import argparse
import csv
import os
from pathlib import Path
import tempfile

os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "level2-matplotlib")
)
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np

COLORS = {
    "original": "#343434",
    "rotation": "#426A8C",
    "blur": "#628578",
    "noise": "#AF814A",
    "brightness": "#8D708E",
}
STYLE = {
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "font.size": 9,
    "axes.labelsize": 10,
    "axes.titlesize": 11,
    "axes.titleweight": "normal",
    "axes.linewidth": 0.7,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "legend.frameon": False,
    "grid.linewidth": 0.4,
    "grid.color": "#D9D9D9",
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
}


def read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def save_figure(figure, folder, name):
    for extension in ("png", "pdf", "svg"):
        figure.savefig(folder / f"{name}.{extension}", dpi=300, bbox_inches="tight")
    plt.close(figure)


def condition_label(row):
    condition, parameter = row["condition"], row["parameter"]
    if condition == "original":
        return "Baseline"
    if condition == "rotation":
        return f"Rotation {parameter.replace('deg', '°')}"
    if condition == "blur":
        return f"Gaussian blur {parameter.replace('x', ' × ')}"
    if condition == "noise":
        return f"Gaussian noise σ = {parameter.split('=')[-1]}"
    return f"Intensity × {parameter.rstrip('x')}"


def comparison_plot(folder, rows):
    if not rows:
        return
    values = [float(row["accuracy"]) * 100 for row in rows]
    positions = np.arange(len(rows))
    figure, axis = plt.subplots(figsize=(7.1, 4.8), layout="constrained")
    for position, value, row in zip(positions, values, rows):
        axis.scatter(
            value,
            position,
            s=32,
            color=COLORS.get(row["condition"], "#555555"),
            edgecolors="white",
            linewidths=0.4,
            zorder=3,
        )
        axis.annotate(
            f"{row['correct_count']}/{row['sample_count']}  ({value:.2f}%)",
            (value, position),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            fontsize=8,
            bbox=dict(facecolor="white", edgecolor="none", pad=0.3),
        )
    baseline = next(
        (float(r["accuracy"]) * 100 for r in rows if r["condition"] == "original"), None
    )
    if baseline is not None:
        axis.axvline(baseline, color="#777777", linestyle=(0, (3, 3)), linewidth=0.8)
    for index in range(1, len(rows)):
        if rows[index]["condition"] != rows[index - 1]["condition"]:
            axis.axhline(index - 0.5, color="#E5E5E5", linewidth=0.5)
    axis.set_yticks(positions, [condition_label(row) for row in rows])
    axis.invert_yaxis()
    axis.set_xlim(max(0, np.floor(min(values) / 5) * 5), 104)
    axis.set_xticks(np.arange(max(0, np.floor(min(values) / 5) * 5), 101, 2))
    axis.set_xlabel("Accuracy (%)")
    axis.set_title("Classification under input perturbations", loc="left", pad=12)
    axis.grid(axis="x", linestyle=":")
    axis.tick_params(axis="y", length=0)
    save_figure(figure, folder, "accuracy_comparison")


def rotation_plot(folder, rows):
    selected = [row for row in rows if row["condition"] in ("rotation", "original")]
    if not selected:
        return
    points = sorted(
        (
            0
            if row["condition"] == "original"
            else int(row["parameter"].replace("deg", "")),
            float(row["accuracy"]) * 100,
            int(row["sample_count"]),
        )
        for row in selected
    )
    angles, values, sizes = zip(*points)
    figure, axis = plt.subplots(figsize=(5.3, 3.4), layout="constrained")
    axis.plot(
        angles,
        values,
        "o-",
        color=COLORS["rotation"],
        linewidth=1.2,
        markersize=4.5,
        markeredgecolor="white",
        markeredgewidth=0.5,
    )
    for angle, value in zip(angles, values):
        axis.annotate(
            f"{value:.2f}",
            (angle, value),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            fontsize=8,
        )
    axis.set_xticks(angles)
    axis.set_xlim(min(angles) - 2, max(angles) + 2)
    axis.set_ylim(max(0, np.floor(min(values) / 5) * 5), min(100, max(values) + 2))
    axis.yaxis.set_major_locator(MultipleLocator(2))
    axis.set_xlabel("Rotation angle (°)")
    axis.set_ylabel("Accuracy (%)")
    axis.set_title("Rotation sensitivity", loc="left", pad=10)
    axis.text(
        1,
        1.03,
        f"n = {sizes[0]} per condition"
        if len(set(sizes)) == 1
        else "Sample sizes in CSV",
        transform=axis.transAxes,
        ha="right",
        fontsize=8,
        color="#555555",
    )
    axis.grid(axis="y", linestyle=":")
    save_figure(figure, folder, "rotation_accuracy")


def blank_plot(folder, rows):
    if not rows:
        return
    counts = np.array(
        [
            [
                int(
                    dict(
                        item.split(":")
                        for item in row["predicted_class_counts"].split(";")
                    ).get(str(i), 0)
                )
                for i in range(10)
            ]
            for row in rows
        ]
    )
    sizes = np.array([int(row["sample_count"]) for row in rows])
    fractions = counts / sizes[:, None] * 100
    labels = {
        "pure_white": "Uniform blank",
        "shadow": "Synthetic shadow",
        "clutter": "Synthetic clutter",
    }
    figure, axis = plt.subplots(figsize=(7.1, 2.9), layout="constrained")
    heatmap = axis.imshow(fractions, cmap="Blues", vmin=0, vmax=100, aspect="auto")
    for y in range(len(rows)):
        for x in range(10):
            axis.text(
                x,
                y,
                str(counts[y, x]),
                ha="center",
                va="center",
                color="white" if fractions[y, x] > 65 else "#222222",
                fontsize=9,
            )
    axis.set_xticks(range(10))
    axis.set_yticks(
        range(len(rows)),
        [
            f"{labels.get(r['parameter'], r['parameter'])}\n(n = {sizes[i]})"
            for i, r in enumerate(rows)
        ],
    )
    axis.set_xlabel("Predicted digit")
    axis.set_title("Predictions on synthetic no-target inputs", loc="left", pad=16)
    axis.tick_params(length=0)
    for spine in axis.spines.values():
        spine.set_visible(False)
    colorbar = figure.colorbar(heatmap, ax=axis, shrink=0.9, pad=0.025)
    colorbar.set_label("Within-group proportion (%)", fontsize=8)
    axis.text(
        0,
        -0.42,
        "Cell labels: counts. Colours: proportions within each control group.",
        transform=axis.transAxes,
        fontsize=8,
        color="#555555",
    )
    save_figure(figure, folder, "blank_prediction_distribution")


def write_figures(output_root, accuracy_rows, blank_rows):
    folder = Path(output_root) / "figures"
    folder.mkdir(parents=True, exist_ok=True)
    with plt.rc_context(STYLE):
        comparison_plot(folder, accuracy_rows)
        rotation_plot(folder, accuracy_rows)
        blank_plot(folder, blank_rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "results/robustness",
    )
    args = parser.parse_args()
    write_figures(
        args.results,
        read_rows(args.results / "accuracy_summary.csv"),
        read_rows(args.results / "blank_summary.csv"),
    )
    print(f"Figures: {args.results / 'figures'}")


if __name__ == "__main__":
    main()
