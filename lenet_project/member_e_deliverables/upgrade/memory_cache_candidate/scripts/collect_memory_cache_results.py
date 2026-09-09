#!/usr/bin/env python3
"""Collect the controlled Conv2 memory-cache experiment."""

from __future__ import annotations

import csv
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
RESULTS = ROOT / "results"
RAW = ROOT / "raw_reports"
CONFIGS = ["d2_external_weight_baseline", "d2_local_weight_cache"]


def xml_text(root: ET.Element, path: str, default: str = "") -> str:
    node = root.find(path)
    return node.text.strip() if node is not None and node.text else default


def find_report(config: str, category: str, suffix: str) -> Path | None:
    paths = sorted((WORK / config / "solution1" / category / "report").glob(f"*{suffix}"))
    return paths[0] if paths else None


def parse(config: str) -> dict[str, object]:
    xml_path = find_report(config, "syn", "_csynth.xml")
    rpt_path = find_report(config, "syn", "_csynth.rpt")
    csim_path = find_report(config, "csim", "_csim.log")
    if xml_path is None:
        cpu_log_path = RESULTS / f"{config}_cpu_csim.log"
        cpu_text = cpu_log_path.read_text(encoding="utf-8", errors="replace") if cpu_log_path.exists() else ""
        errors = [float(value) for value in re.findall(r"max_abs=([0-9.eE+-]+)", cpu_text)]
        return {
            "config_id": config,
            "status": "CPU_CSIM_PASS_HLS_NOT_RUN" if "Overall result: PASS" in cpu_text else "NOT_RUN",
            "csim": "PASS_CPU" if "Overall result: PASS" in cpu_text else "",
            "max_abs_error": f"{max(errors):.9g}" if errors else "",
            "decision": "WAIT_HLS_SYNTHESIS",
            "source_report": str(cpu_log_path.relative_to(ROOT)) if cpu_log_path.exists() else "",
        }
    root = ET.parse(xml_path).getroot()
    resources = root.find("./AreaEstimates/Resources")

    def res(*names: str) -> int:
        if resources is None:
            return 0
        for name in names:
            node = resources.find(name)
            if node is not None and node.text:
                return int(float(node.text))
        return 0

    csim_text = csim_path.read_text(encoding="utf-8", errors="replace") if csim_path else ""
    errors = [float(value) for value in re.findall(r"max_abs=([0-9.eE+-]+)", csim_text)]
    row = {
        "config_id": config,
        "status": "VALIDATED" if "Overall result: PASS" in csim_text else "CSIM_FAILED",
        "csim": "PASS" if "Overall result: PASS" in csim_text else "FAIL_OR_MISSING",
        "max_abs_error": f"{max(errors):.9g}" if errors else "",
        "target_clock_ns": xml_text(root, "./UserAssignments/TargetClockPeriod"),
        "estimated_clock_ns": xml_text(root, "./PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod"),
        "latency_cycles": int(xml_text(root, "./PerformanceEstimates/SummaryOfOverallLatency/Worst-caseLatency")),
        "interval_cycles": int(xml_text(root, "./PerformanceEstimates/SummaryOfOverallLatency/Interval-max")),
        "lut": res("LUT"),
        "ff": res("FF"),
        "bram_18k": res("BRAM_18K"),
        "dsp": res("DSP48E", "DSP"),
        "source_report": str(xml_path.relative_to(ROOT)),
    }
    destination = RAW / config
    destination.mkdir(parents=True, exist_ok=True)
    for source in [xml_path, rpt_path, csim_path]:
        if source and source.exists():
            shutil.copy2(source, destination / source.name)
    return row


def main() -> None:
    rows = [parse(config) for config in CONFIGS]
    RESULTS.mkdir(parents=True, exist_ok=True)
    fields = [
        "config_id", "status", "csim", "max_abs_error", "target_clock_ns",
        "estimated_clock_ns", "latency_cycles", "interval_cycles", "lut", "ff",
        "bram_18k", "dsp", "latency_change_percent", "interval_change_percent",
        "lut_change", "ff_change", "bram_change", "dsp_change", "decision", "source_report",
    ]
    if all(row.get("status") == "VALIDATED" for row in rows):
        baseline, candidate = rows
        for metric in ["latency", "interval"]:
            base_value = int(baseline[f"{metric}_cycles"])
            candidate_value = int(candidate[f"{metric}_cycles"])
            candidate[f"{metric}_change_percent"] = f"{100.0 * (candidate_value - base_value) / base_value:.4f}"
        for metric in ["lut", "ff", "bram_18k", "dsp"]:
            candidate[metric.replace("_18k", "") + "_change"] = int(candidate[metric]) - int(baseline[metric])
        latency_gain = int(candidate["latency_cycles"]) < int(baseline["latency_cycles"])
        interval_gain = int(candidate["interval_cycles"]) < int(baseline["interval_cycles"])
        candidate["decision"] = "KEEP_FOR_IP_REVIEW" if latency_gain or interval_gain else "STOP_NO_PERFORMANCE_GAIN"
        baseline["decision"] = "CONTROL"
    with (RESULTS / "memory_cache_comparison.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    (RESULTS / "memory_cache_summary.json").write_text(
        json.dumps({"comparison": rows}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
