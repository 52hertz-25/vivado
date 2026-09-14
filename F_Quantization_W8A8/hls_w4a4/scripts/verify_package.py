#!/usr/bin/env python3
"""Offline structural and quantization-constant checks for the W4A4 package."""

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QMAX = 7
SHIFT = 40
LAYERS = {
    "conv1": (150, "input", "conv1_relu", 32113559987),
    "conv2": (2400, "pool1", "conv2_relu", 41310957922),
    "conv3": (48000, "pool2", "conv3_relu", 44103899460),
    "fc1": (10080, "conv3_relu", "fc1_relu", 78194388213),
    "fc2": (840, "fc1_relu", "fc2_output", 44572774922),
}


def activation_scale(data, name):
    return float(data[name]["max_abs"]) / QMAX


def main():
    weight_root = ROOT / "model" / "int4_weights"
    weights_meta = json.loads((weight_root / "weight_scales.json").read_text())
    activations = json.loads(
        (ROOT / "model" / "activation_calibration.json").read_text()
    )
    header = (ROOT / "include" / "lenet_w4a4.h").read_text()

    total = 0
    for name, (expected_count, input_name, output_name, expected_q40) in LAYERS.items():
        path = weight_root / f"{name}.weight.int4.txt"
        values = [int(token) for token in path.read_text().split()]
        assert len(values) == expected_count, (name, len(values), expected_count)
        assert min(values) >= -7 and max(values) <= 7, name
        assert int(weights_meta[name]["number_of_values"]) == expected_count
        ratio = (
            activation_scale(activations, input_name)
            * float(weights_meta[name]["scale"])
            / activation_scale(activations, output_name)
        )
        calculated = int(round(ratio * (1 << SHIFT)))
        assert calculated == expected_q40, (name, calculated, expected_q40)
        symbol = name.upper() + "_REQUANT_Q40"
        match = re.search(symbol + r"\s*=\s*(\d+)ULL", header)
        assert match and int(match.group(1)) == calculated, symbol
        total += len(values)

    assert total == 61470
    assert math.ceil(total / 2) == 30735
    assert "typedef ap_int<4> act_t" in header
    assert "typedef ap_int<4> weight_t" in header
    assert "typedef ap_int<32> accum_t" in header
    assert "typedef ap_uint<8> packed_t" in header
    print("W4A4_PACKAGE_VERIFY_PASS")
    print(f"weights={total}, packed_weight_bytes={math.ceil(total / 2)}")
    print("range=[-7,7], accumulator=INT32, requantization=Q40 ties-to-even")


if __name__ == "__main__":
    main()
