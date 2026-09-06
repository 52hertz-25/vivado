#!/usr/bin/env python3
import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

FIELDS = ["config_id", "report_version", "top", "part", "target_clock_ns",
          "estimated_clock_ns", "latency_best_cycles", "latency_avg_cycles",
          "latency_worst_cycles", "interval_min", "interval_max",
          "bram_18k", "dsp", "ff", "lut", "uram", "report_path"]

def value(root, path, default=""):
    node = root.find(path)
    return node.text.strip() if node is not None and node.text else default

def locate_report(solution):
    reports = sorted(solution.glob("syn/report/*_csynth.xml"))
    if not reports:
        reports = sorted(solution.glob("syn/report/csynth.xml"))
    return reports[0] if reports else None

def parse(report, config_id):
    root = ET.parse(report).getroot()
    resource = root.find("./AreaEstimates/Resources")
    def res(*names):
        if resource is None: return ""
        for name in names:
            node = resource.find(name)
            if node is not None and node.text: return node.text.strip()
        return ""
    return {
        "config_id": config_id,
        "report_version": value(root, "./ReportVersion/Version"),
        "top": value(root, "./UserAssignments/TopModelName"),
        "part": value(root, "./UserAssignments/Part"),
        "target_clock_ns": value(root, "./UserAssignments/TargetClockPeriod"),
        "estimated_clock_ns": value(root, "./PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod"),
        "latency_best_cycles": value(root, "./PerformanceEstimates/SummaryOfOverallLatency/Best-caseLatency"),
        "latency_avg_cycles": value(root, "./PerformanceEstimates/SummaryOfOverallLatency/Average-caseLatency"),
        "latency_worst_cycles": value(root, "./PerformanceEstimates/SummaryOfOverallLatency/Worst-caseLatency"),
        "interval_min": value(root, "./PerformanceEstimates/SummaryOfOverallLatency/Interval-min"),
        "interval_max": value(root, "./PerformanceEstimates/SummaryOfOverallLatency/Interval-max"),
        "bram_18k": res("BRAM_18K"), "dsp": res("DSP48E", "DSP"),
        "ff": res("FF"), "lut": res("LUT"), "uram": res("URAM"),
        "report_path": str(report.resolve()),
    }

def main():
    root_dir = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1])
    rows = []
    for project in sorted((root_dir / "work").glob("*")):
        report = locate_report(project / "solution1")
        if report:
            rows.append(parse(report, project.name))
    out = root_dir / "results" / "hls_dse_results.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader(); writer.writerows(rows)
    print(f"Collected {len(rows)} configuration(s): {out}")
    return 0 if rows else 1

if __name__ == "__main__":
    raise SystemExit(main())
