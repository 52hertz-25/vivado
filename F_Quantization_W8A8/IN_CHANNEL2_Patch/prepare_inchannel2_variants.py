from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
CONFIGS = {
    "w8a8": "lenet_w8a8.cpp",
    "w6a6": "lenet_w6a6.cpp",
    "w4a4": "lenet_w4a4.cpp",
}

for key, filename in CONFIGS.items():
    source = ROOT / f"hls_{key}" / "src" / filename
    target = source.with_name(source.stem + "_ic2.cpp")
    if not source.exists():
        raise SystemExit(f"ERROR: source not found: {source}")
    data = source.read_text(encoding="utf-8")
    pattern = r"(?m)^(\s*)IN_CHANNEL:\s*\n(\s*)for\s*\("
    matches = re.findall(pattern, data)
    if len(matches) != 1:
        raise SystemExit(f"ERROR: expected one IN_CHANNEL loop in {source}, found {len(matches)}")
    replacement = r"\1IN_CHANNEL:\n\2#pragma HLS UNROLL factor=2\n\2for ("
    data = re.sub(pattern, replacement, data, count=1)
    target.write_text(data, encoding="utf-8", newline="\n")
    print(f"IC2_VARIANT_READY={target}")

print("LEVEL3_IC2_VARIANT_PREPARATION_PASS")
