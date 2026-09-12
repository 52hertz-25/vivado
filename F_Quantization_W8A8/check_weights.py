from pathlib import Path
import numpy as np

base_dir = Path(__file__).resolve().parent
weight_dir = base_dir / "hw_weights"

expected = {
    "conv1.weight.txt": 6 * 1 * 5 * 5,
    "conv2.weight.txt": 16 * 6 * 5 * 5,
    "conv3.weight.txt": 120 * 16 * 5 * 5,
    "fc1.weight.txt": 84 * 120,
    "fc2.weight.txt": 10 * 84,
}

print("开始检查FP32权重文件")
print("=" * 50)

all_pass = True

for filename, expected_count in expected.items():
    file_path = weight_dir / filename

    if not file_path.exists():
        print(filename, "文件不存在 [FAIL]")
        all_pass = False
        continue

    values = np.loadtxt(file_path, dtype=np.float32)
    actual_count = values.size

    if actual_count == expected_count:
        status = "PASS"
    else:
        status = "FAIL"
        all_pass = False

    print(
        f"{filename:20s} "
        f"实际数量={actual_count:6d} "
        f"应有数量={expected_count:6d} "
        f"[{status}]"
    )

print("=" * 50)

if all_pass:
    print("全部权重检查通过，可以进行量化。")
else:
    print("权重检查未通过，请不要继续量化。")