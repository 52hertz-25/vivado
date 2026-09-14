from pathlib import Path
import csv
import re

PATCH = Path(__file__).resolve().parent
ROOT = PATCH.parent
CONFIGS = [("W8A8", "w8a8"), ("W6A6", "w6a6"), ("W4A4", "w4a4")]

def parse_report(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    clock = re.search(r"\|ap_clk\s*\|\s*[0-9.]+ ns\|\s*([0-9.]+) ns", text)
    latency = re.search(r"\|\s*([0-9]+)\|\s*\1\|\s*[0-9.]+\s+(?:ns|us|ms)\|", text)
    total = re.search(r"\|Total\s*\|\s*([0-9]+)\|\s*([0-9]+)\|\s*([0-9]+)\|\s*([0-9]+)\|", text)
    if not (clock and latency and total):
        raise ValueError(f"Could not parse report: {path}")
    bram, dsp, ff, lut = map(int, total.groups())
    return [float(clock.group(1)), int(latency.group(1)), lut, ff, bram, dsp]

rows = []
for label, key in CONFIGS:
    base = ROOT / f"hls_{key}" / "work" / f"{key}_hls" / "solution1" / "syn" / "report" / f"lenet_{key}_top_csynth.rpt"
    pe5 = ROOT / f"hls_{key}" / "final_delivery" / "reports" / "level3_pe5" / f"lenet_{key}_top_pe5_csynth.rpt"
    for pe, report in [(1, base), (5, pe5)]:
        if not report.exists():
            raise SystemExit(f"ERROR: report not found: {report}")
        rows.append([label, pe, *parse_report(report), str(report)])

out_dir = PATCH / "results"
out_dir.mkdir(exist_ok=True)
out = out_dir / "bitwidth_pe_cross_results.csv"
with out.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["configuration", "pe_mac", "estimated_clock_ns", "latency_cycles", "lut", "ff", "bram_18k", "dsp", "source"])
    writer.writerows(rows)
print(f"LEVEL3_PE_CROSS_RESULTS={out}")
print("LEVEL3_PE_CROSS_COLLECTION_PASS")

