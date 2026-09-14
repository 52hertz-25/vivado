from pathlib import Path
import sys

if len(sys.argv) != 3:
    raise SystemExit("ERROR: expected <baseline_csv> <new_csv>")

baseline = Path(sys.argv[1])
new = Path(sys.argv[2])
for path in (baseline, new):
    if not path.is_file():
        raise SystemExit(f"ERROR: result file missing: {path}")

def normalized(path):
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip()

if normalized(baseline) != normalized(new):
    raise SystemExit(
        "W4A4_LC2_MNIST_EQUIVALENCE_FAIL: result or confusion matrix differs"
    )

print(f"W4A4_LC2_MNIST_EQUIVALENCE_PASS baseline={baseline.name}")
