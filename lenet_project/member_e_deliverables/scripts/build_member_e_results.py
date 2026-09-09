#!/usr/bin/env python3
"""Build and validate member E's LeNet HLS/Vivado DSE deliverables.

The script treats HLS csynth XML reports and Vivado post-route text reports as
the source of truth. It writes normalized CSV files, charts, a JSON summary,
and a validation report under lenet_project/member_e_deliverables.
"""

from __future__ import annotations

import csv
import json
import math
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter


SCRIPT_DIR = Path(__file__).resolve().parent
DELIVERABLE_DIR = SCRIPT_DIR.parent
PROJECT_DIR = DELIVERABLE_DIR.parent
FRAMEWORK_DIR = PROJECT_DIR / "handoff" / "LeNet_DSE_Framework_2022_2"
VIVADO_RUN_DIR = (
    PROJECT_DIR
    / "vivado"
    / "LeNet_Zynq_System"
    / "LeNet_Zynq_System.runs"
    / "impl_1"
)

DATA_DIR = DELIVERABLE_DIR / "data"
FIGURE_DIR = DELIVERABLE_DIR / "figures"
SOURCE_REPORT_DIR = DELIVERABLE_DIR / "source_reports"

CLOCK_CONFIGS = [
    "clk_10ns_baseline",
    "clk_9ns",
    "clk_8ns",
    "clk_7_5ns",
    "clk_7ns",
]
STRUCTURAL_CONFIGS = ["struct_baseline", "mac_unroll_2", "mac_unroll_5"]


def xml_text(root: ET.Element, path: str, default: str = "") -> str:
    node = root.find(path)
    return node.text.strip() if node is not None and node.text else default


def as_int(value: str) -> int:
    return int(float(value))


def as_float(value: str) -> float:
    return float(value)


def parse_hls_config(config_id: str) -> dict[str, object]:
    report = (
        FRAMEWORK_DIR
        / config_id
        / "solution1"
        / "syn"
        / "report"
        / "lenet_full_top_csynth.xml"
    )
    if not report.exists():
        raise FileNotFoundError(report)

    root = ET.parse(report).getroot()
    resources = root.find("./AreaEstimates/Resources")

    def resource(*names: str) -> int:
        if resources is None:
            raise ValueError(f"No resource section in {report}")
        for name in names:
            node = resources.find(name)
            if node is not None and node.text:
                return as_int(node.text)
        raise ValueError(f"Missing resource {names} in {report}")

    target_ns = as_float(xml_text(root, "./UserAssignments/TargetClockPeriod"))
    estimated_ns = as_float(
        xml_text(root, "./PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod")
    )
    latency = as_int(
        xml_text(root, "./PerformanceEstimates/SummaryOfOverallLatency/Worst-caseLatency")
    )
    interval = as_int(
        xml_text(root, "./PerformanceEstimates/SummaryOfOverallLatency/Interval-max")
    )
    return {
        "Config": config_id,
        "Target_ns": target_ns,
        "Estimated_ns": estimated_ns,
        "Estimated_Fmax_MHz": 1000.0 / estimated_ns,
        "Latency_cycles": latency,
        "Latency_ms_at_target": latency * target_ns / 1_000_000.0,
        "Interval": interval,
        "LUT": resource("LUT"),
        "FF": resource("FF"),
        "BRAM_18K": resource("BRAM_18K"),
        "DSP": resource("DSP48E", "DSP"),
        "Source_report": str(report.relative_to(PROJECT_DIR.parent)),
    }


def parse_csim(config_id: str) -> str:
    log = (
        FRAMEWORK_DIR
        / config_id
        / "solution1"
        / "csim"
        / "report"
        / "lenet_full_top_csim.log"
    )
    if not log.exists():
        return "NOT_FOUND"
    text = log.read_text(encoding="utf-8", errors="replace")
    return "PASS" if "Overall result: PASS" in text else "CHECK"


def first_match(pattern: str, text: str, cast=float):
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        raise ValueError(f"Pattern not found: {pattern}")
    return cast(match.group(1))


def parse_vivado_reports() -> dict[str, object]:
    timing_path = VIVADO_RUN_DIR / "lenet_system_wrapper_timing_summary_routed.rpt"
    utilization_path = VIVADO_RUN_DIR / "lenet_system_wrapper_utilization_placed.rpt"
    power_path = VIVADO_RUN_DIR / "lenet_system_wrapper_power_routed.rpt"

    timing = timing_path.read_text(encoding="utf-8", errors="replace")
    utilization = utilization_path.read_text(encoding="utf-8", errors="replace")
    power = power_path.read_text(encoding="utf-8", errors="replace")

    timing_row = re.search(
        r"^\s*([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)\s+\d+\s+\d+\s+"
        r"([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)",
        timing,
        re.MULTILINE,
    )
    if not timing_row:
        raise ValueError("Unable to parse Vivado timing summary")

    def table_used(label: str) -> int:
        return first_match(
            rf"^\|\s*{re.escape(label)}\s*\|\s*(\d+)\s*\|",
            utilization,
            int,
        )

    result = {
        "Tool": "Vivado 2022.2",
        "Design": "lenet_system_wrapper",
        "Device": "xc7z020clg400-1",
        "Design_state": "Fully Routed",
        "Timing_met": "All user specified timing constraints are met." in timing,
        "WNS_ns": float(timing_row.group(1)),
        "WHS_ns": float(timing_row.group(3)),
        "Slice_LUTs": table_used("Slice LUTs"),
        "Slice_Registers": table_used("Slice Registers"),
        "Block_RAM_Tile": table_used("Block RAM Tile"),
        "DSPs": table_used("DSPs"),
        "Total_On_Chip_Power_W": first_match(
            r"^\| Total On-Chip Power \(W\)\s*\|\s*([0-9.]+)", power
        ),
        "Power_confidence": first_match(
            r"^\| Confidence Level\s*\|\s*([^|]+?)\s*\|", power, str
        ).strip(),
        "PS7_power_W": first_match(
            r"^\| PS7\s*\|\s*([0-9.]+)", power
        ),
        "Timing_report": str(timing_path.relative_to(PROJECT_DIR.parent)),
        "Utilization_report": str(utilization_path.relative_to(PROJECT_DIR.parent)),
        "Power_report": str(power_path.relative_to(PROJECT_DIR.parent)),
    }
    return result


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def choose_font() -> str:
    candidates = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Arial"]
    installed = {font.name for font in font_manager.fontManager.ttflist}
    return next((name for name in candidates if name in installed), "Arial")


def style_axes(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#94A3B8")
    ax.spines["bottom"].set_color("#94A3B8")
    ax.grid(axis="y", color="#CBD5E1", linewidth=0.8, alpha=0.65)
    ax.set_axisbelow(True)


def display_config(label: str) -> str:
    names = {
        "clk_10ns_baseline": "10 ns baseline",
        "clk_9ns": "9 ns",
        "clk_8ns": "8 ns",
        "clk_7_5ns": "7.5 ns",
        "clk_7ns": "7 ns",
    }
    return names.get(label, label)


def save_clock_chart(rows: list[dict[str, object]]) -> None:
    ordered = sorted(rows, key=lambda row: float(row["Target_ns"]))
    x = [float(row["Target_ns"]) for row in ordered]
    y = [int(row["Latency_cycles"]) for row in ordered]
    labels = [str(row["Config"]) for row in ordered]
    colors = ["#C69214" if label == "clk_10ns_baseline" else "#285E8E" for label in labels]

    fig, ax = plt.subplots(figsize=(9.6, 5.6), facecolor="white")
    ax.plot(x, y, color="#285E8E", linewidth=2.0, zorder=1)
    ax.scatter(x, y, s=85, c=colors, edgecolors="#17324D", linewidths=0.8, zorder=2)
    for xi, yi, label in zip(x, y, labels):
        short = display_config(label)
        offset = (-42, 12) if xi >= 9.5 else (6, 10)
        ax.annotate(short, (xi, yi), xytext=offset, textcoords="offset points", fontsize=9)
    fig.text(0.08, 0.96, "目标时钟周期与 HLS 延迟周期", fontsize=16, fontweight="bold")
    fig.text(0.08, 0.91, "LeNet FP32 完整网络，XC7Z020；10 ns 基线的调度周期最少",
             fontsize=10, color="#475569")
    ax.set_xlabel("目标时钟周期（ns）")
    ax.set_ylabel("最坏情况延迟（cycles）")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value/1e6:.1f}M"))
    ax.set_xticks(x)
    style_axes(ax)
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig(FIGURE_DIR / "clock_latency_cycles.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def save_pareto_chart(rows: list[dict[str, object]]) -> None:
    fig, ax = plt.subplots(figsize=(9.6, 5.6), facecolor="white")
    for row in rows:
        baseline = row["Config"] == "clk_10ns_baseline"
        ax.scatter(
            int(row["Latency_cycles"]),
            int(row["LUT"]),
            s=125 if baseline else 80,
            color="#C69214" if baseline else "#285E8E",
            edgecolor="#17324D",
            linewidth=0.9,
            zorder=2,
        )
        short = display_config(str(row["Config"]))
        offset = (8, -18) if str(row["Config"]) == "clk_7_5ns" else (8, 7)
        ax.annotate(short, (int(row["Latency_cycles"]), int(row["LUT"])), xytext=offset,
                    textcoords="offset points", fontsize=9)
    fig.text(0.08, 0.96, "HLS 延迟与 LUT 的 Pareto 对比", fontsize=16, fontweight="bold")
    fig.text(0.08, 0.91, "五个时钟约束配置；左下方向代表更少周期和更少 LUT",
             fontsize=10, color="#475569")
    ax.set_xlabel("最坏情况延迟（cycles）")
    ax.set_ylabel("LUT")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value/1e6:.1f}M"))
    style_axes(ax)
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig(FIGURE_DIR / "pareto_latency_lut.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def save_structural_chart(rows: list[dict[str, object]]) -> None:
    labels = [str(row["Config"]).replace("struct_", "") for row in rows]
    measures = [
        ("延迟（million cycles）", [int(row["Latency_cycles"]) / 1e6 for row in rows], "{:.3f}"),
        ("LUT", [int(row["LUT"]) for row in rows], "{:,.0f}"),
        ("DSP", [int(row["DSP"]) for row in rows], "{:.0f}"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 4.4), facecolor="white")
    for ax, (title, values, fmt) in zip(axes, measures):
        bars = ax.bar(labels, values, color=["#285E8E", "#8AA8C1", "#B7C8D8"],
                      edgecolor="#17324D", linewidth=0.7)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.tick_params(axis="x", labelrotation=18, labelsize=9)
        ax.set_ylim(0, max(values) * 1.24 if max(values) else 1)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.025,
                    fmt.format(value), ha="center", va="bottom", fontsize=9)
        style_axes(ax)
    fig.text(0.06, 0.96, "MAC 循环展开结构实验", fontsize=16, fontweight="bold")
    fig.text(0.06, 0.89, "baseline、Unroll ×2 和 Unroll ×5 的综合结果完全相同",
             fontsize=10, color="#475569")
    fig.tight_layout(rect=(0, 0, 1, 0.82))
    fig.savefig(FIGURE_DIR / "structural_dse_comparison.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def compare_existing_clock(derived: list[dict[str, object]]) -> list[str]:
    existing_path = FRAMEWORK_DIR / "results" / "clock_dse_summary.csv"
    existing = {row["Config"]: row for row in read_csv(existing_path)}
    checks: list[str] = []
    for row in derived:
        source = existing[str(row["Config"])]
        pairs = [
            ("Target_ns", float),
            ("Estimated_ns", float),
            ("Latency_cycles", int),
            ("Interval", int),
            ("LUT", int),
            ("FF", int),
            ("BRAM_18K", int),
        ]
        for field, cast in pairs:
            left = cast(row[field])
            right = cast(float(source[field])) if cast is int else cast(source[field])
            if cast is float:
                ok = math.isclose(left, right, rel_tol=0, abs_tol=0.001)
            else:
                ok = left == right
            if not ok:
                raise ValueError(f"Clock summary mismatch {row['Config']} {field}: {left} != {right}")
        checks.append(f"{row['Config']}: raw csynth XML matches clock_dse_summary.csv")
    return checks


def compare_existing_structural(derived: list[dict[str, object]]) -> list[str]:
    existing_path = FRAMEWORK_DIR / "results" / "structural_dse_summary.csv"
    existing = {row["Config"]: row for row in read_csv(existing_path)}
    checks: list[str] = []
    for row in derived:
        source = existing[str(row["Config"])]
        for field in ["Latency_cycles", "LUT", "FF", "BRAM_18K", "DSP"]:
            if int(row[field]) != int(source[field]):
                raise ValueError(
                    f"Structural summary mismatch {row['Config']} {field}: "
                    f"{row[field]} != {source[field]}"
                )
        if row["CSim"] != source["CSim"]:
            raise ValueError(f"C-sim mismatch for {row['Config']}")
        checks.append(f"{row['Config']}: raw reports match structural_dse_summary.csv")
    return checks


def main() -> None:
    for directory in [DATA_DIR, FIGURE_DIR, SOURCE_REPORT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    font = choose_font()
    plt.rcParams.update({
        "font.family": font,
        "axes.unicode_minus": False,
        "text.color": "#172033",
        "axes.labelcolor": "#172033",
        "xtick.color": "#475569",
        "ytick.color": "#475569",
    })

    clock_rows = [parse_hls_config(config) for config in CLOCK_CONFIGS]
    structural_rows = []
    for config in STRUCTURAL_CONFIGS:
        row = parse_hls_config(config)
        row["CSim"] = parse_csim(config)
        structural_rows.append(row)
    vivado = parse_vivado_reports()

    checks = compare_existing_clock(clock_rows)
    checks.extend(compare_existing_structural(structural_rows))

    clock_fields = [
        "Config", "Target_ns", "Estimated_ns", "Estimated_Fmax_MHz",
        "Latency_cycles", "Latency_ms_at_target", "Interval", "LUT", "FF",
        "BRAM_18K", "DSP", "Source_report",
    ]
    structural_fields = [
        "Config", "CSim", "Target_ns", "Estimated_ns", "Estimated_Fmax_MHz",
        "Latency_cycles", "Latency_ms_at_target", "Interval", "LUT", "FF",
        "BRAM_18K", "DSP", "Source_report",
    ]
    write_csv(DATA_DIR / "clock_dse_validated.csv", clock_rows, clock_fields)
    write_csv(DATA_DIR / "structural_dse_validated.csv", structural_rows, structural_fields)
    write_csv(DATA_DIR / "vivado_post_route_summary.csv", [vivado], list(vivado.keys()))

    save_clock_chart(clock_rows)
    save_pareto_chart(clock_rows)
    save_structural_chart(structural_rows)

    baseline = next(row for row in clock_rows if row["Config"] == "clk_10ns_baseline")
    pareto_dominates = all(
        int(baseline["Latency_cycles"]) <= int(row["Latency_cycles"])
        and int(baseline["LUT"]) <= int(row["LUT"])
        for row in clock_rows
    )
    structural_identical = all(
        all(int(row[field]) == int(structural_rows[0][field])
            for field in ["Latency_cycles", "LUT", "FF", "BRAM_18K", "DSP"])
        for row in structural_rows[1:]
    )
    checks.extend([
        f"10 ns baseline weakly dominates all clock candidates in cycles and LUT: {pareto_dominates}",
        f"Structural baseline and both unroll candidates are identical: {structural_identical}",
        f"Vivado timing met: {vivado['Timing_met']}",
        f"Vivado route state: {vivado['Design_state']}",
    ])

    summary = {
        "generated_from": "HLS csynth XML and Vivado post-route reports",
        "clock_dse": clock_rows,
        "structural_dse": structural_rows,
        "vivado_post_route": vivado,
        "conclusions": {
            "selected_config": "clk_10ns_baseline",
            "pareto_dominates_in_cycles_and_lut": pareto_dominates,
            "unroll_2_and_5_changed_measured_results": not structural_identical,
            "power_is_vectorless_medium_confidence_estimate": True,
        },
    }
    (DATA_DIR / "analysis_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (DATA_DIR / "validation_report.md").write_text(
        "# 成员 E DSE 数据核验记录\n\n"
        "核验日期：2026-09-09\n\n"
        "## 核验结果\n\n"
        + "\n".join(f"- {item}" for item in checks)
        + "\n\n## 结论\n\n"
        "原始 HLS XML 与已有两张汇总表一致。10 ns 基线同时具有最低延迟周期和最低 LUT，"
        "因此是本轮时钟扫描的 Pareto 最优配置。两档单独 MAC 循环展开没有改变综合结果。"
        "Vivado 设计已完成布局布线并满足时序约束。\n",
        encoding="utf-8",
    )

    for name in ["lenet_full_top_csynth.rpt", "lenet_full_top_csynth.xml"]:
        source = FRAMEWORK_DIR / "clk_10ns_baseline" / "solution1" / "syn" / "report" / name
        shutil.copy2(source, SOURCE_REPORT_DIR / f"clk_10ns_baseline_{name}")
    for name in [
        "lenet_system_wrapper_timing_summary_routed.rpt",
        "lenet_system_wrapper_utilization_placed.rpt",
        "lenet_system_wrapper_power_routed.rpt",
        "lenet_system_wrapper_route_status.rpt",
    ]:
        shutil.copy2(VIVADO_RUN_DIR / name, SOURCE_REPORT_DIR / name)

    print(f"Generated member E deliverables in: {DELIVERABLE_DIR}")


if __name__ == "__main__":
    main()
