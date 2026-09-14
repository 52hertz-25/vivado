from pathlib import Path
import csv, re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

def parse(path):
    t = path.read_text(encoding="utf-8", errors="ignore")
    lat = re.search(r"Latency \(cycles\).*?\n.*?\|\s*(\d+)\s*\|\s*(\d+)\s*\|", t, re.S)
    total = re.search(r"\|Total\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", t)
    clocks = re.findall(r"\|\s*(?:ap_clk|default)\s*\|\s*([0-9.]+)\s*ns\s*\|\s*([0-9.]+)\s*ns", t, re.I)
    if not lat or not total: raise SystemExit(f"ERROR: cannot parse {path}")
    bram, dsp, ff, lut = map(int, total.groups())
    return [int(lat.group(1)), int(lat.group(2)), clocks[0][1] if clocks else "", lut, ff, bram, dsp]

rows=[]; changes=0
for k in ("w8a8","w6a6","w4a4"):
    base=ROOT/f"hls_{k}"/"work"/f"{k}_hls"/"solution1"/"syn"/"report"/f"lenet_{k}_top_csynth.rpt"
    new=ROOT/f"hls_{k}"/"final_delivery"/"reports"/"level3_localcache2"/f"lenet_{k}_top_lc2_csynth.rpt"
    b=parse(base); n=parse(new); changed=b[:2]+b[3:] != n[:2]+n[3:]; changes += changed
    rows += [[k.upper(),"BASELINE",*b,""],[k.upper(),"LOCAL_CACHE_IC2",*n,changed]]
out=HERE/"results"/"localcache2_comparison.csv"; out.parent.mkdir(exist_ok=True)
with out.open("w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["configuration","variant","latency_min","latency_max","estimated_clock_ns","lut","ff","bram_18k","dsp","changed"]); w.writerows(rows)
print(f"RESULT_CSV={out}")
if not changes: raise SystemExit("LOCALCACHE2_NO_STRUCTURAL_CHANGE_FAIL")
print(f"LOCALCACHE2_STRUCTURAL_CHANGE_PASS changed_configs={changes}")
