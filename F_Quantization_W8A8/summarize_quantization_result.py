from pathlib import Path
import csv
import json

import matplotlib.pyplot as plt


# ============================================================
# 1. 工作目录
# ============================================================

# 既支持正常运行文件，也支持Thonny临时运行
if "__file__" in globals():
    BASE_DIR = Path(__file__).resolve().parent
else:
    BASE_DIR = Path.cwd()


# ============================================================
# 2. 输入结果文件
# ============================================================

RESULT_FILES = {
    "W8A8-INT32": (
        BASE_DIR /
        "w8a8_int32_results.json"
    ),
    "W6A6-INT32": (
        BASE_DIR /
        "w6a6_int32_results.json"
    ),
    "W4A4-INT32": (
        BASE_DIR /
        "w4a4_int32_results.json"
    ),
}


# ============================================================
# 3. 输出文件
# ============================================================

SUMMARY_CSV_PATH = (
    BASE_DIR /
    "quantization_summary.csv"
)

SUMMARY_JSON_PATH = (
    BASE_DIR /
    "quantization_summary.json"
)

ACCURACY_FIGURE_PATH = (
    BASE_DIR /
    "quantization_accuracy_comparison.png"
)

TRADEOFF_FIGURE_PATH = (
    BASE_DIR /
    "quantization_tradeoff_comparison.png"
)


# ============================================================
# 4. 模型信息
# ============================================================

TOTAL_WEIGHTS = 61470

CONFIGURATION_INFO = {
    "FP32": {
        "weight_bits": 32,
        "activation_bits": 32,
    },

    "W8A8-INT32": {
        "weight_bits": 8,
        "activation_bits": 8,
    },

    "W6A6-INT32": {
        "weight_bits": 6,
        "activation_bits": 6,
    },

    "W4A4-INT32": {
        "weight_bits": 4,
        "activation_bits": 4,
    },
}


# ============================================================
# 5. 读取JSON文件
# ============================================================

def load_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"找不到结果文件：\n{path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


results = {}

print("开始读取量化结果文件……")
print("=" * 80)

for configuration, path in RESULT_FILES.items():
    results[configuration] = load_json(path)
    print(f"[PASS] {configuration}: {path.name}")

print("=" * 80)


# ============================================================
# 6. 通用字段读取函数
# ============================================================

def get_first_value(
    data,
    field_names,
    default=None
):
    for field_name in field_names:
        if field_name in data:
            return data[field_name]

    if default is not None:
        return default

    print("当前JSON字段为：")
    print(list(data.keys()))

    raise KeyError(
        "找不到字段，尝试过："
        + ", ".join(field_names)
    )


def get_fp32_accuracy(data):
    value = get_first_value(
        data,
        [
            "fp32_accuracy_percent",
            "fp32_accuracy",
            "FP32Accuracy",
        ]
    )

    return float(value)


def get_quantized_accuracy(data):
    value = get_first_value(
        data,
        [
            "quantized_accuracy_percent",
            "w8a8_accuracy_percent",
            "w6a6_accuracy_percent",
            "w4a4_accuracy_percent",
            "quantized_accuracy",
            "QuantizedAccuracy",
        ]
    )

    return float(value)


def get_agreement(data):
    value = get_first_value(
        data,
        [
            "fp32_prediction_agreement_percent",
            "prediction_agreement_percent",
            "agreement_percent",
            "prediction_agreement",
            "agreement",
            "PredictionAgreement",
        ]
    )

    return float(value)


def get_test_samples(data):
    value = get_first_value(
        data,
        [
            "test_samples",
            "total",
            "Total",
        ],
        default=10000
    )

    return int(value)


def get_overflow_result(data):
    value = get_first_value(
        data,
        [
            "int32_overflow_check",
            "overflow_check",
            "INT32OverflowCheck",
        ],
        default="UNKNOWN"
    )

    if isinstance(value, bool):
        if value:
            return "PASS"
        return "FAIL"

    return str(value)


def get_accumulator_max(data):
    value = get_first_value(
        data,
        [
            "accumulator_max_abs",
            "accumulator_maximum",
            "accumulator_max",
        ],
        default={}
    )

    if isinstance(value, dict):
        return value

    return {}


# ============================================================
# 7. 读取并检查FP32基准
# ============================================================

fp32_accuracy_list = []

for configuration in [
    "W8A8-INT32",
    "W6A6-INT32",
    "W4A4-INT32",
]:
    value = get_fp32_accuracy(
        results[configuration]
    )

    fp32_accuracy_list.append(value)


fp32_accuracy = fp32_accuracy_list[0]

if max(fp32_accuracy_list) - min(fp32_accuracy_list) > 0.01:
    print("[WARNING] 三个文件中的FP32准确率不完全一致：")
    print(fp32_accuracy_list)
    print("汇总表将使用第一个FP32结果。")
else:
    print(
        f"统一FP32基准检查通过："
        f"{fp32_accuracy:.2f}%"
    )


# ============================================================
# 8. 构造FP32基准行
# ============================================================

fp32_storage_bytes = int(
    TOTAL_WEIGHTS *
    32 /
    8
)

summary_rows = []

summary_rows.append({
    "Configuration": "FP32",
    "WeightBits": 32,
    "ActivationBits": 32,
    "AccumulatorBits": 32,
    "TestSamples": get_test_samples(
        results["W8A8-INT32"]
    ),
    "AccuracyPercent": fp32_accuracy,
    "AccuracyDropPoints": 0.0,
    "PredictionAgreementPercent": 100.0,
    "TheoreticalWeightStorageBytes": (
        fp32_storage_bytes
    ),
    "TheoreticalWeightStorageKB": (
        fp32_storage_bytes / 1024.0
    ),
    "CompressionRatioVsFP32": 1.0,
    "INT32OverflowCheck": "N/A",
})


# ============================================================
# 9. 构造量化配置行
# ============================================================

for configuration in [
    "W8A8-INT32",
    "W6A6-INT32",
    "W4A4-INT32",
]:
    data = results[configuration]

    weight_bits = CONFIGURATION_INFO[
        configuration
    ]["weight_bits"]

    activation_bits = CONFIGURATION_INFO[
        configuration
    ]["activation_bits"]

    quantized_accuracy = (
        get_quantized_accuracy(data)
    )

    accuracy_drop = (
        fp32_accuracy -
        quantized_accuracy
    )

    agreement = get_agreement(data)

    storage_bytes = int(
        (
            TOTAL_WEIGHTS *
            weight_bits +
            7
        ) // 8
    )

    compression_ratio = (
        fp32_storage_bytes /
        storage_bytes
    )

    summary_rows.append({
        "Configuration": configuration,
        "WeightBits": weight_bits,
        "ActivationBits": activation_bits,
        "AccumulatorBits": 32,
        "TestSamples": get_test_samples(data),
        "AccuracyPercent": quantized_accuracy,
        "AccuracyDropPoints": accuracy_drop,
        "PredictionAgreementPercent": agreement,
        "TheoreticalWeightStorageBytes": (
            storage_bytes
        ),
        "TheoreticalWeightStorageKB": (
            storage_bytes / 1024.0
        ),
        "CompressionRatioVsFP32": (
            compression_ratio
        ),
        "INT32OverflowCheck": (
            get_overflow_result(data)
        ),
    })


# ============================================================
# 10. 保存CSV汇总结果
# ============================================================

CSV_FIELDS = [
    "Configuration",
    "WeightBits",
    "ActivationBits",
    "AccumulatorBits",
    "TestSamples",
    "AccuracyPercent",
    "AccuracyDropPoints",
    "PredictionAgreementPercent",
    "TheoreticalWeightStorageBytes",
    "TheoreticalWeightStorageKB",
    "CompressionRatioVsFP32",
    "INT32OverflowCheck",
]

with open(
    SUMMARY_CSV_PATH,
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=CSV_FIELDS
    )

    writer.writeheader()

    for row in summary_rows:
        writer.writerow(row)


# ============================================================
# 11. 保存JSON汇总结果
# ============================================================

summary_json = {
    "model": "LeNet-5",
    "total_weights": TOTAL_WEIGHTS,
    "fp32_baseline_accuracy_percent": (
        fp32_accuracy
    ),
    "results": summary_rows,
    "recommendation": {
        "reliable_configuration": (
            "W8A8-INT32"
        ),
        "balanced_configuration": (
            "W6A6-INT32"
        ),
        "maximum_compression_configuration": (
            "W4A4-INT32"
        ),
        "hardware_comparison_candidates": [
            "W8A8-INT32",
            "W4A4-INT32",
        ],
    },
}

with open(
    SUMMARY_JSON_PATH,
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        summary_json,
        file,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# 12. 在Shell中显示汇总结果
# ============================================================

print()
print("=" * 105)
print("LeNet-5量化结果汇总")
print("=" * 105)

header = (
    f"{'配置':<16}"
    f"{'W/A位宽':>10}"
    f"{'准确率':>12}"
    f"{'精度变化':>14}"
    f"{'一致率':>12}"
    f"{'存储量KB':>14}"
    f"{'压缩比':>12}"
    f"{'溢出':>10}"
)

print(header)
print("-" * 105)

for row in summary_rows:
    configuration = row["Configuration"]

    bit_width = (
        f"{row['WeightBits']}/"
        f"{row['ActivationBits']}"
    )

    accuracy_text = (
        f"{row['AccuracyPercent']:.2f}%"
    )

    if configuration == "FP32":
        drop_text = "0.00"
    else:
        drop_value = row["AccuracyDropPoints"]

        if drop_value >= 0:
            drop_text = f"-{drop_value:.2f}"
        else:
            drop_text = f"+{-drop_value:.2f}"

    agreement_text = (
        f"{row['PredictionAgreementPercent']:.2f}%"
    )

    storage_text = (
        f"{row['TheoreticalWeightStorageKB']:.2f}"
    )

    compression_text = (
        f"{row['CompressionRatioVsFP32']:.2f}x"
    )

    overflow_text = row["INT32OverflowCheck"]

    print(
        f"{configuration:<16}"
        f"{bit_width:>10}"
        f"{accuracy_text:>12}"
        f"{drop_text:>14}"
        f"{agreement_text:>12}"
        f"{storage_text:>14}"
        f"{compression_text:>12}"
        f"{overflow_text:>10}"
    )

print("=" * 105)


# ============================================================
# 13. 准确率柱状图
# ============================================================

configuration_names = [
    row["Configuration"]
    for row in summary_rows
]

accuracy_values = [
    row["AccuracyPercent"]
    for row in summary_rows
]

bar_colors = [
    "#4C78A8",
    "#59A14F",
    "#F2A541",
    "#E15759",
]

plt.figure(figsize=(10, 6))

bars = plt.bar(
    configuration_names,
    accuracy_values,
    color=bar_colors,
    width=0.65
)

plt.title(
    "LeNet-5 Quantization Accuracy Comparison",
    fontsize=15,
    fontweight="bold"
)

plt.xlabel(
    "Numerical Configuration",
    fontsize=12
)

plt.ylabel(
    "Accuracy (%)",
    fontsize=12
)

minimum_accuracy = min(accuracy_values)

plt.ylim(
    max(0, minimum_accuracy - 1.0),
    100.0
)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.35
)

for bar, value in zip(
    bars,
    accuracy_values
):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 0.08,
        f"{value:.2f}%",
        ha="center",
        va="bottom",
        fontsize=11
    )

plt.tight_layout()

plt.savefig(
    ACCURACY_FIGURE_PATH,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 14. 压缩率与准确率权衡图
# ============================================================

quantized_rows = [
    row
    for row in summary_rows
    if row["Configuration"] != "FP32"
]

compression_values = [
    row["CompressionRatioVsFP32"]
    for row in quantized_rows
]

quantized_accuracy_values = [
    row["AccuracyPercent"]
    for row in quantized_rows
]

quantized_names = [
    row["Configuration"]
    for row in quantized_rows
]

plt.figure(figsize=(9, 6))

plt.plot(
    compression_values,
    quantized_accuracy_values,
    color="#4C78A8",
    marker="o",
    linewidth=2.3,
    markersize=9
)

for compression, accuracy, name in zip(
    compression_values,
    quantized_accuracy_values,
    quantized_names
):
    plt.annotate(
        name,
        (compression, accuracy),
        xytext=(8, 8),
        textcoords="offset points",
        fontsize=10
    )

plt.title(
    "Accuracy-Compression Trade-off",
    fontsize=15,
    fontweight="bold"
)

plt.xlabel(
    "Theoretical Compression Ratio vs FP32",
    fontsize=12
)

plt.ylabel(
    "Accuracy (%)",
    fontsize=12
)

plt.grid(
    linestyle="--",
    alpha=0.35
)

plt.tight_layout()

plt.savefig(
    TRADEOFF_FIGURE_PATH,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 15. 输出各层累加器最大值
# ============================================================

print()
print("各量化配置INT32累加器最大绝对值：")
print("-" * 60)

for configuration in [
    "W8A8-INT32",
    "W6A6-INT32",
    "W4A4-INT32",
]:
    accumulator_data = get_accumulator_max(
        results[configuration]
    )

    print(configuration)

    if accumulator_data:
        for layer_name, value in accumulator_data.items():
            print(
                f"  {layer_name:<6}: {value}"
            )
    else:
        print("  未记录累加器数据")


# ============================================================
# 16. 给出方案结论
# ============================================================

print()
print("=" * 80)
print("量化方案结论")
print("=" * 80)

print(
    "W8A8-INT32：精度基本无损，"
    "适合作为主要硬件实现方案。"
)

print(
    "W6A6-INT32：精度基本无损，"
    "适合作为精度和资源之间的折中方案。"
)

print(
    "W4A4-INT32：压缩率最高，"
    "但准确率存在一定下降。"
)

print()
print(
    "建议后续在HLS中重点比较"
    "W8A8与W4A4两种配置。"
)


# ============================================================
# 17. 完成
# ============================================================

print()
print("结果已经保存到：")
print(SUMMARY_CSV_PATH)
print(SUMMARY_JSON_PATH)
print(ACCURACY_FIGURE_PATH)
print(TRADEOFF_FIGURE_PATH)

print()
print("量化结果汇总完成。[PASS]")