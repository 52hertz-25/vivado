#!/usr/bin/env python3
"""Build the source-derived BD diagram and SHA-256 manifest for the AXI package."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]


def draw_box(ax, xy, wh, title, lines, color):
    x, y = xy
    width, height = wh
    ax.add_patch(FancyBboxPatch(
        (x, y), width, height, boxstyle="round,pad=0.02",
        linewidth=1.6, edgecolor=color, facecolor="white"))
    ax.text(x + width / 2, y + height - 0.07, title, ha="center", va="top",
            fontsize=13, fontweight="bold", color=color)
    ax.text(x + 0.04, y + height - 0.18, "\n".join(lines), ha="left", va="top",
            fontsize=9.2, color="#263238", linespacing=1.45)


def arrow(ax, start, end, label, color, rad=0.0):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=14, linewidth=2, color=color,
        connectionstyle=f"arc3,rad={rad}"))
    middle_x = (start[0] + end[0]) / 2
    middle_y = (start[1] + end[1]) / 2
    ax.text(middle_x, middle_y + 0.025, label, ha="center", va="bottom",
            fontsize=8.6, color=color,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.5})


def build_diagram():
    output = ROOT / "figures" / "block_design_connection_map.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(13.2, 7.2), dpi=180)
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    axis.text(0.5, 0.95, "LeNet Zynq AXI Block Design Connection Map",
              ha="center", fontsize=19, fontweight="bold", color="#12344D")
    axis.text(0.5, 0.905, "Reconstructed from lenet_system.bd (not a GUI screenshot)",
              ha="center", fontsize=10.5, color="#546E7A")

    draw_box(axis, (0.04, 0.28), (0.27, 0.48), "Zynq-7000 Processing System",
             ["M_AXI_GP0  (control master)", "S_AXI_HP0  (DDR data slave)",
              "FCLK_CLK0 / RESET0_N", "DDR + FIXED_IO"], "#1565C0")
    draw_box(axis, (0.39, 0.55), (0.22, 0.20), "AXI Interconnect",
             ["1 slave -> 1 master", "AXI-Lite control path"], "#7B1FA2")
    draw_box(axis, (0.69, 0.26), (0.27, 0.50), "lenet_full_top_0 v1.0",
             ["s_axi_control", "base: 0x4000_0000", "", "m_axi_gmem0", "m_axi_gmem1",
              "m_axi_gmem2", "m_axi_gmem3"], "#00897B")
    draw_box(axis, (0.39, 0.16), (0.22, 0.20), "proc_sys_reset_0",
             ["interconnect_aresetn", "peripheral_aresetn"], "#EF6C00")

    arrow(axis, (0.31, 0.65), (0.39, 0.65), "M_AXI_GP0", "#7B1FA2")
    arrow(axis, (0.61, 0.65), (0.69, 0.65), "s_axi_control", "#7B1FA2")
    arrow(axis, (0.69, 0.42), (0.31, 0.42), "gmem0..3 -> S_AXI_HP0", "#00897B", 0.08)
    arrow(axis, (0.31, 0.31), (0.69, 0.31), "FCLK_CLK0", "#1565C0", -0.08)
    arrow(axis, (0.50, 0.36), (0.50, 0.55), "reset nets", "#EF6C00")
    arrow(axis, (0.61, 0.25), (0.69, 0.32), "ap_rst_n", "#EF6C00")

    axis.text(
        0.5, 0.06,
        "Control: PS writes pointers/start via GP0 | Data: HLS masters access DDR via HP0 | Clock target: 10 ns",
        ha="center", fontsize=10, color="#37474F")
    figure.tight_layout()
    figure.savefig(output, bbox_inches="tight")
    plt.close(figure)


def build_manifest():
    entries = []
    for path in sorted(candidate for candidate in ROOT.rglob("*") if candidate.is_file()):
        if path.name == "artifact_manifest_sha256.csv":
            continue
        if path.suffix.lower() in {".log", ".jou", ".pb"}:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append((path.relative_to(ROOT).as_posix(), path.stat().st_size, digest))
    output = ROOT / "artifact_manifest_sha256.csv"
    with output.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(["relative_path", "size_bytes", "sha256"])
        writer.writerows(entries)


if __name__ == "__main__":
    build_diagram()
    build_manifest()
    print(f"AXI package prepared at {ROOT}")
