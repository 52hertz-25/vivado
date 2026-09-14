from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parent.parent
CONFIGS = {
    "w8a8": "lenet_w8a8.cpp",
    "w6a6": "lenet_w6a6.cpp",
    "w4a4": "lenet_w4a4.cpp",
}

for key, filename in CONFIGS.items():
    source = ROOT / f"hls_{key}" / "src" / filename
    target = source.with_name(source.stem + "_pe5.cpp")
    if not source.exists():
        raise SystemExit(f"ERROR: source not found: {source}")
    text = source.read_text(encoding="utf-8")
    pattern = r"(?m)^(\s*)KERNEL_COL:\s*$"
    matches = re.findall(pattern, text)
    if len(matches) != 1:
        raise SystemExit(f"ERROR: expected one exact KERNEL_COL label in {source}")
    text = re.sub(pattern, r"\1KERNEL_COL:\n\1#pragma HLS UNROLL factor=5", text, count=1)
    target.write_text(text, encoding="utf-8", newline="\n")
    print(f"PE5_VARIANT_READY={target}")

print("LEVEL3_PE5_VARIANT_PREPARATION_PASS")
