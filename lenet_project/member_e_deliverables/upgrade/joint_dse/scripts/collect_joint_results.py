#!/usr/bin/env python3
"""Collect real HLS results and build the member E joint-DSE evidence set."""

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
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "joint_dse_configs.csv"
D_MEASURED_PATH = ROOT / "d_provided_measurements.csv"
WORK_DIR = ROOT / "work"
RESULT_DIR = ROOT / "results"
RAW_DIR = ROOT / "raw_reports"
FIGURE_DIR = ROOT / "figures"

DEVICE_CAPACITY = {"lut": 53200, "ff": 106400, "bram_18k": 280, "dsp": 220}
FP32_REFERENCE_ACCURACY = 99.30


def read_configs() -> list[dict[str, str]]:
    with CONFIG_PATH.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def read_d_measurements() -> dict[str, dict[str, str]]:
    with D_MEASURED_PATH.open(newline="", encoding="utf-8-sig") as stream:
        return {row["config_id"]: row for row in csv.DictReader(stream)}


def text(root: ET.Element, path: str, default: str = "") -> str:
    node = root.find(path)
    return node.text.strip() if node is not None and node.text else default


def resource(resources: ET.Element | None, *names: str) -> str:
    if resources is None:
        return ""
    for name in names:
        node = resources.find(name)
        if node is not None and node.text:
            return node.text.strip()
    return ""


def locate(config_id: str, category: str, suffix: str) -> Path | None:
    base = WORK_DIR / config_id / "solution1" / category / "report"
    matches = sorted(base.glob(f"*{suffix}"))
    return matches[0] if matches else None


def parse_measured(config: dict[str, str]) -> dict[str, object]:
    config_id = config["config_id"]
    xml_path = locate(config_id, "syn", "_csynth.xml")
    rpt_path = locate(config_id, "syn", "_csynth.rpt")
    csim_path = locate(config_id, "csim", "_csim.log")
    if xml_path is None:
        imported = read_d_measurements().get(config_id)
        if imported:
            lut = int(imported["lut"])
            ff = int(imported["ff"])
            bram = int(imported["bram_18k"])
            dsp = int(imported["dsp"])
            pressure = 100.0 * sum([
                lut / DEVICE_CAPACITY["lut"], ff / DEVICE_CAPACITY["ff"],
                bram / DEVICE_CAPACITY["bram_18k"], dsp / DEVICE_CAPACITY["dsp"],
            ]) / 4.0
            target = float(config["target_clock_ns"])
            return {
                **config,
                "execution_status": "IMPORTED_D_MEASURED_RECORD",
                "csim": imported["csim"],
                "accuracy_percent": f"{FP32_REFERENCE_ACCURACY:.2f}",
                "accuracy_status": "B_FP32_SOFTWARE_BASELINE_REFERENCE_D_CSIM_REPORTED",
                "max_abs_error": "",
                "estimated_clock_ns": imported["estimated_clock_ns"],
                "latency_cycles": imported["latency_cycles"],
                "latency_ms_at_target": f"{int(imported['latency_cycles']) * target / 1_000_000.0:.6f}",
                "interval_cycles": imported["interval_cycles"],
                "reported_pipeline_ii": imported["reported_pipeline_ii"],
                "lut": lut, "ff": ff, "bram_18k": bram, "dsp": dsp,
                "resource_pressure_percent": f"{pressure:.4f}",
                "source_report": imported["provenance"],
            }
        return {
            **config,
            "execution_status": "NOT_RUN" if config["planned_status"] == "READY" else config["planned_status"],
            "csim": "",
            "accuracy_percent": "",
            "accuracy_status": "MISSING_F_RESULT" if config["precision"] != "FP32" else "",
        }

    root = ET.parse(xml_path).getroot()
    resources = root.find("./AreaEstimates/Resources")
    latency = text(root, "./PerformanceEstimates/SummaryOfOverallLatency/Worst-caseLatency")
    interval = text(root, "./PerformanceEstimates/SummaryOfOverallLatency/Interval-max")
    estimated = text(root, "./PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod")
    csim_text = csim_path.read_text(encoding="utf-8", errors="replace") if csim_path else ""
    csim = "PASS" if "Overall result: PASS" in csim_text else "FAIL_OR_MISSING"
    errors = [float(value) for value in re.findall(r"max_abs=([0-9.eE+-]+)", csim_text)]
    pipeline_iis = sorted({
        node.text.strip()
        for node in root.iter()
        if node.tag.split("}")[-1] in {"PipelineII", "II"} and node.text and node.text.strip().isdigit()
    }, key=int)

    lut = int(float(resource(resources, "LUT") or 0))
    ff = int(float(resource(resources, "FF") or 0))
    bram = int(float(resource(resources, "BRAM_18K") or 0))
    dsp = int(float(resource(resources, "DSP48E", "DSP") or 0))
    pressure = 100.0 * sum([
        lut / DEVICE_CAPACITY["lut"],
        ff / DEVICE_CAPACITY["ff"],
        bram / DEVICE_CAPACITY["bram_18k"],
        dsp / DEVICE_CAPACITY["dsp"],
    ]) / 4.0
    target = float(config["target_clock_ns"])

    raw_config_dir = RAW_DIR / config_id
    raw_config_dir.mkdir(parents=True, exist_ok=True)
    for source in [xml_path, rpt_path, csim_path]:
        if source and source.exists():
            shutil.copy2(source, raw_config_dir / source.name)

    return {
        **config,
        "execution_status": "VALIDATED" if csim == "PASS" else "CSIM_FAILED",
        "csim": csim,
        "accuracy_percent": f"{FP32_REFERENCE_ACCURACY:.2f}",
        "accuracy_status": "B_FP32_SOFTWARE_BASELINE_REFERENCE_AND_CSIM_NUMERICAL_PASS",
        "max_abs_error": f"{max(errors):.9g}" if errors else "",
        "estimated_clock_ns": estimated,
        "latency_cycles": latency,
        "latency_ms_at_target": f"{int(latency) * target / 1_000_000.0:.6f}",
        "interval_cycles": interval,
        "reported_pipeline_ii": ";".join(pipeline_iis),
        "lut": lut,
        "ff": ff,
        "bram_18k": bram,
        "dsp": dsp,
        "resource_pressure_percent": f"{pressure:.4f}",
        "source_report": str(xml_path.relative_to(ROOT)),
    }


def dominates(left: dict[str, object], right: dict[str, object]) -> bool:
    left_values = (
        -float(left["accuracy_percent"]),
        int(left["latency_cycles"]),
        float(left["resource_pressure_percent"]),
    )
    right_values = (
        -float(right["accuracy_percent"]),
        int(right["latency_cycles"]),
        float(right["resource_pressure_percent"]),
    )
    return all(a <= b for a, b in zip(left_values, right_values)) and any(
        a < b for a, b in zip(left_values, right_values)
    )


def annotate_pareto(rows: list[dict[str, object]]) -> None:
    measured = [row for row in rows if row.get("execution_status") in {"VALIDATED", "IMPORTED_D_MEASURED_RECORD"}]
    for row in measured:
        row["pareto_status"] = "DOMINATED" if any(
            dominates(other, row) for other in measured if other is not row
        ) else "PARETO"

    latency_values = [int(row["latency_cycles"]) for row in measured]
    resource_values = [float(row["resource_pressure_percent"]) for row in measured]
    latency_span = max(latency_values) - min(latency_values) or 1
    resource_span = max(resource_values) - min(resource_values) or 1.0
    for row in measured:
        latency_norm = (int(row["latency_cycles"]) - min(latency_values)) / latency_span
        resource_norm = (float(row["resource_pressure_percent"]) - min(resource_values)) / resource_span
        row["balanced_score"] = f"{0.5 * latency_norm + 0.5 * resource_norm:.6f}"

    recommendation = min(
        (row for row in measured if row["pareto_status"] == "PARETO"),
        key=lambda row: float(row["balanced_score"]),
    )
    recommendation["selection_role"] = "RECOMMENDED_BALANCED"
    min(measured, key=lambda row: float(row["resource_pressure_percent"]))[
        "selection_role"
    ] = "LOWEST_RESOURCE"
    highest_accuracy = max(float(row["accuracy_percent"]) for row in measured)
    min(
        (row for row in measured if math.isclose(float(row["accuracy_percent"]), highest_accuracy)),
        key=lambda row: int(row["latency_cycles"]),
    ).setdefault("selection_role", "HIGHEST_ACCURACY_TIE_FASTEST")
    for row in rows:
        row.setdefault("pareto_status", "NOT_EVALUATED")
        row.setdefault("balanced_score", "")
        row.setdefault("selection_role", "")


def choose_font() -> str:
    names = {font.name for font in font_manager.fontManager.ttflist}
    for candidate in ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Arial"]:
        if candidate in names:
            return candidate
    return "Arial"


def plot(rows: list[dict[str, object]]) -> None:
    measured = [row for row in rows if row.get("execution_status") in {"VALIDATED", "IMPORTED_D_MEASURED_RECORD"}]
    plt.rcParams.update({"font.family": choose_font(), "axes.unicode_minus": False})
    fig, ax = plt.subplots(figsize=(10.5, 6.2), facecolor="white")
    colors = {
        "RECOMMENDED_BALANCED": "#C47A13",
        "LOWEST_RESOURCE": "#2F6B9A",
        "HIGHEST_ACCURACY_TIE_FASTEST": "#4A8F65",
        "": "#9AA6B2",
    }
    for row in measured:
        role = str(row["selection_role"])
        color = colors.get(role, "#9AA6B2")
        marker = "X" if role == "RECOMMENDED_BALANCED" else ("x" if row["pareto_status"] == "DOMINATED" else "o")
        x = float(row["latency_ms_at_target"])
        y = float(row["resource_pressure_percent"])
        ax.scatter(x, y, s=180 if role == "RECOMMENDED_BALANCED" else 110,
                   marker=marker, color=color, edgecolor="#23364A", linewidth=0.8, zorder=3)
        ax.annotate(str(row["pe_variant"]), (x, y), xytext=(7, 7), textcoords="offset points", fontsize=10)
    fig.suptitle("成员 E 联合 DSE 已验证配置", x=0.10, y=0.97,
                 ha="left", fontsize=17, fontweight="bold")
    fig.text(0.10, 0.925, "FP32 Conv2，XC7Z020，10 ns；横轴越小越快，纵轴越小资源压力越低",
             fontsize=10, color="#4B5563")
    ax.set_xlabel("Latency at target clock (ms)")
    ax.set_ylabel("Composite resource pressure (% of device, mean of LUT/FF/BRAM/DSP)")
    ax.grid(axis="both", color="#D7DEE6", linewidth=0.8, alpha=0.75)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(handles=[
        Line2D([0], [0], marker="X", color="none", markerfacecolor="#C47A13",
               markeredgecolor="#23364A", markersize=10, label="推荐平衡点"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#2F6B9A",
               markeredgecolor="#23364A", markersize=9, label="最低资源点"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#9AA6B2",
               markeredgecolor="#23364A", markersize=9, label="Pareto 候选"),
        Line2D([0], [0], marker="x", color="#9AA6B2", markersize=9, label="被支配点"),
    ], loc="upper right", frameon=False, ncol=2)
    blocked = sum(1 for row in rows if str(row["execution_status"]).startswith("BLOCKED"))
    fig.text(0.12, 0.02, f"量化配置未绘图：{blocked} 组等待成员 F 的源码、尺度与真实准确率；未使用估算值。",
             fontsize=9.5, color="#5B6470")
    fig.tight_layout(rect=(0, 0.055, 1, 0.89))
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_DIR / "joint_pareto_accuracy_latency_resource.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def write_csv(rows: list[dict[str, object]]) -> None:
    fields = [
        "config_id", "search_scope", "precision", "total_bits", "pe_variant",
        "mac_parallelism", "output_channel_parallelism", "pipeline_mode",
        "target_clock_ns", "part", "execution_status", "csim",
        "accuracy_percent", "accuracy_status", "max_abs_error",
        "estimated_clock_ns", "latency_cycles", "latency_ms_at_target",
        "interval_cycles", "reported_pipeline_ii", "lut", "ff", "bram_18k", "dsp",
        "resource_pressure_percent", "pareto_status", "balanced_score",
        "selection_role", "source_file", "source_report",
    ]
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    with (RESULT_DIR / "joint_dse_validated.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = [parse_measured(config) for config in read_configs()]
    annotate_pareto(rows)
    write_csv(rows)
    plot(rows)

    measured = [row for row in rows if row.get("execution_status") in {"VALIDATED", "IMPORTED_D_MEASURED_RECORD"}]
    blocked = [row for row in rows if str(row.get("execution_status", "")).startswith("BLOCKED")]
    recommended = next((row for row in measured if row.get("selection_role") == "RECOMMENDED_BALANCED"), None)
    summary = {
        "method": "D-provided Vitis HLS 2022.2 measured records are imported when local raw XML cannot be regenerated; no estimated quantized rows",
        "validated_count": len(measured),
        "blocked_quantized_count": len(blocked),
        "recommended_config": recommended["config_id"] if recommended else None,
        "accuracy_limit": "FP32 uses B's 99.30% software baseline; F quantized accuracy is not available",
        "pareto_objectives": "maximize accuracy; minimize latency; minimize composite device resource pressure",
        "rows": rows,
    }
    (RESULT_DIR / "joint_dse_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Validated {len(measured)} configurations; blocked {len(blocked)} quantized configurations")
    if recommended:
        print(f"Recommended measured configuration: {recommended['config_id']}")


if __name__ == "__main__":
    main()
