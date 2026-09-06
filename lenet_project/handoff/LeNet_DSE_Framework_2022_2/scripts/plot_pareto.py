#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

def number(v):
    try: return float(v)
    except (TypeError, ValueError): return None

root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1])
src = root / "results" / "hls_dse_results.csv"
rows = list(csv.DictReader(src.open(encoding="utf-8-sig")))
points = []
for r in rows:
    latency, lut = number(r.get("latency_worst_cycles")), number(r.get("lut"))
    if latency is not None and lut is not None: points.append((latency, lut, r["config_id"]))
if not points: raise SystemExit("No numeric points in results/hls_dse_results.csv")
try:
    import matplotlib.pyplot as plt
except ImportError:
    raise SystemExit("Install once: py -m pip install matplotlib")
plt.figure(figsize=(8, 5))
for x, y, label in points:
    plt.scatter(x, y); plt.annotate(label, (x, y), xytext=(5, 5), textcoords="offset points")
plt.xlabel("Worst-case latency (cycles)"); plt.ylabel("HLS LUT")
plt.title("LeNet HLS design-space exploration"); plt.grid(True, alpha=.3); plt.tight_layout()
out = root / "results" / "pareto_latency_lut.png"
plt.savefig(out, dpi=180)
print(out)
