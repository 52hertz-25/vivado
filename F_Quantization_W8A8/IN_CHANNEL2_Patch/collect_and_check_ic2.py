from pathlib import Path
import csv
import re

PATCH = Path(__file__).resolve().parent
ROOT = PATCH.parent
CONFIGS = ("w8a8", "w6a6", "w4a4")

def parse(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    latency = re.search(r"Latency \(cycles\).*?\n.*?\|\s*([0-9]+)\s*\|\s*([0-9]+)\s*\|", text, re.S)
    clock = re.search(r"Estimated Clock Period.*?\|\s*([0-9.]+)\s*(?:ns|us|ms)\s*\|", text, re.S)
    total = re.search(r"\|Total\s*\|\s*([0-9]+)\s*\|\s*([0-9]+)\s*\|\s*([0-9]+)\s*\|\s*([0-9]+)\s*\|", text)
    if not latency or not total:
        raise ValueError(f"cannot parse required metrics: {path}")
    bram, dsp, ff, lut = map(int, total.groups())
    return {
        "latency_min": int(latency.group(1)),
        "latency_max": int(latency.group(2)),
        "estimated_clock_ns": float(clock.group(1)) if clock else "",
        "lut": lut, "ff": ff, "bram_18k": bram, "dsp": dsp,
    }

rows = []
any_change = False
for key in CONFIGS:
    base = ROOT / f"hls_{key}" / "work" / f"{key}_hls" / "solution1" / "syn" / "report" / f"lenet_{key}_top_csynth.rpt"
    ic2 = ROOT / f"hls_{key}" / "final_delivery" / "reports" / "level3_ic2" / f"lenet_{key}_top_ic2_csynth.rpt"
    if not base.exists() or not ic2.exists():
        raise SystemExit(f"ERROR: missing baseline or IC2 report for {key}")
    b, n = parse(base), parse(ic2)
    changed = any(b[k] != n[k] for k in ("latency_min", "latency_max", "lut", "ff", "bram_18k", "dsp"))
    any_change |= changed
    for name, values in (("PE1_BASELINE", b), ("IN_CHANNEL_2", n)):
        rows.append({"configuration": key.upper(), "variant": name, **values, "changed_vs_baseline": changed if name == "IN_CHANNEL_2" else ""})

out = PATCH / "results" / "inchannel2_comparison.csv"
out.parent.mkdir(exist_ok=True)
with out.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader(); writer.writerows(rows)
print(f"RESULT_CSV={out}")
if not any_change:
    raise SystemExit("LEVEL3_IC2_NO_STRUCTURAL_CHANGE_FAIL")
print("LEVEL3_IC2_STRUCTURAL_CHANGE_PASS")
