from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent

def require_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"ERROR: {label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)

def make_plain(key):
    source = ROOT / f"hls_{key}" / "src" / f"lenet_{key}.cpp"
    target = source.with_name(f"lenet_{key}_lc2.cpp")
    text = source.read_text(encoding="utf-8")
    old = """OUT_CHANNEL:
    for (int oc = 0; oc < OUT_C; ++oc) {
    OUT_ROW:"""
    new = """OUT_CHANNEL:
    for (int oc = 0; oc < OUT_C; ++oc) {
        weight_t local_weight[IN_C * KERNEL_ELEMS];
#pragma HLS ARRAY_PARTITION variable=local_weight cyclic factor=2 dim=1
    LOAD_LOCAL_WEIGHT:
        for (int wi = 0; wi < IN_C * KERNEL_ELEMS; ++wi) {
#pragma HLS PIPELINE II=1
            local_weight[wi] =
                weight[oc * IN_C * KERNEL_ELEMS + wi];
        }
    OUT_ROW:"""
    text = require_once(text, old, new, f"{key} output-channel insertion")
    old = """            IN_CHANNEL:
                for (int ic = 0; ic < IN_C; ++ic) {"""
    new = """            IN_CHANNEL:
#pragma HLS UNROLL factor=2
                for (int ic = 0; ic < IN_C; ++ic) {"""
    text = require_once(text, old, new, f"{key} input-channel pragma")
    pattern = re.compile(
        r"const int weight_index =\s*\n\s*\(\(oc \* IN_C \+ ic\) \* KERNEL_SIZE \+ kh\) \*\s*\n\s*KERNEL_SIZE \+ kw;"
    )
    replacement = """const int weight_index =
                                (ic * KERNEL_SIZE + kh) * KERNEL_SIZE + kw;"""
    text, n = pattern.subn(replacement, text, count=1)
    if n != 1:
        raise SystemExit(f"ERROR: {key} weight index replacement failed")
    text = require_once(text, "weight[weight_index]", "local_weight[weight_index]", f"{key} local read")
    target.write_text(text, encoding="utf-8", newline="\n")
    print(f"LC2_VARIANT_READY={target}")

def make_w4a4():
    key = "w4a4"
    source = ROOT / "hls_w4a4" / "src" / "lenet_w4a4.cpp"
    target = source.with_name("lenet_w4a4_lc2.cpp")
    text = source.read_text(encoding="utf-8")
    old = """OUT_CHANNEL:
    for (int oc = 0; oc < OUT_C; ++oc) {

    OUT_ROW:"""
    new = """OUT_CHANNEL:
    for (int oc = 0; oc < OUT_C; ++oc) {
        weight_t local_weight[IN_C * KERNEL_ELEMS];
#pragma HLS ARRAY_PARTITION variable=local_weight cyclic factor=2 dim=1
    LOAD_LOCAL_WEIGHT:
        for (int wi = 0; wi < IN_C * KERNEL_ELEMS; ++wi) {
#pragma HLS PIPELINE II=1
            local_weight[wi] = unpack_int4(
                packed_weight,
                weight_offset + oc * IN_C * KERNEL_ELEMS + wi
            );
        }

    OUT_ROW:"""
    text = require_once(text, old, new, "w4a4 output-channel insertion")
    old = """            IN_CHANNEL:
                for (int ic = 0; ic < IN_C; ++ic) {"""
    new = """            IN_CHANNEL:
#pragma HLS UNROLL factor=2
                for (int ic = 0; ic < IN_C; ++ic) {"""
    text = require_once(text, old, new, "w4a4 input-channel pragma")
    pattern = re.compile(
        r"const int local_weight_index =\s*\n\s*\(\s*\n\s*\(\s*\n\s*oc \* IN_C \+\s*\n\s*ic\s*\n\s*\) \* KERNEL_SIZE \+\s*\n\s*kh\s*\n\s*\) \* KERNEL_SIZE \+\s*\n\s*kw;"
    )
    replacement = """const int local_weight_index =
                                (ic * KERNEL_SIZE + kh) * KERNEL_SIZE + kw;"""
    text, n = pattern.subn(replacement, text, count=1)
    if n != 1:
        raise SystemExit("ERROR: w4a4 weight index replacement failed")
    pattern = re.compile(
        r"const weight_t weight_value =\s*\n\s*unpack_int4\(\s*\n\s*packed_weight,\s*\n\s*weight_offset \+\s*\n\s*local_weight_index\s*\n\s*\);"
    )
    text, n = pattern.subn(
        "const weight_t weight_value = local_weight[local_weight_index];",
        text,
        count=1,
    )
    if n != 1:
        raise SystemExit("ERROR: w4a4 cached read replacement failed")
    target.write_text(text, encoding="utf-8", newline="\n")
    print(f"LC2_VARIANT_READY={target}")

make_plain("w8a8")
make_plain("w6a6")
make_w4a4()
print("LOCALCACHE2_VARIANT_PREPARATION_PASS")
