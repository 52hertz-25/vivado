from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
COUNTS = {"conv1": 150, "conv2": 2400, "conv3": 48000, "fc1": 10080, "fc2": 840}

required = [
    ROOT / "include" / "lenet_w6a6.h",
    ROOT / "src" / "lenet_w6a6.cpp",
    ROOT / "tb" / "tb_lenet_w6a6.cpp",
    ROOT / "scripts" / "run_w6a6.tcl",
]

for path in required:
    if not path.is_file():
        raise SystemExit(f"W6A6_PACKAGE_FAIL missing={path}")

weight_root = ROOT / "model" / "int6_weights"
for name, expected in COUNTS.items():
    path = weight_root / f"{name}.weight.int6.txt"
    values = [int(x) for x in path.read_text(encoding="utf-8").split()]
    if len(values) != expected:
        raise SystemExit(f"W6A6_PACKAGE_FAIL {name} count={len(values)} expected={expected}")
    if min(values) < -31 or max(values) > 31:
        raise SystemExit(f"W6A6_PACKAGE_FAIL {name} range=[{min(values)},{max(values)}]")
    print(f"{name}: count={len(values)} range=[{min(values)},{max(values)}]")

metadata_path = weight_root / "weight_scales.json"
metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
for name in COUNTS:
    if metadata[name]["dtype"] != "int6" or metadata[name]["bits"] != 6:
        raise SystemExit(f"W6A6_PACKAGE_FAIL invalid metadata for {name}")

print("W6A6_PACKAGE_PASS")
