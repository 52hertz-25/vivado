# LeNet-5 W6A6 INT32 HLS (Vitis HLS 2022.2)

This package implements LeNet-5 with signed 6-bit activations and weights and
signed 32-bit accumulation for `xc7z020clg400-1` at a 10 ns target clock.

The AXI master ports carry arrays whose C element type is `ap_int<6>`. Vitis
may pad memory transfers to byte lanes, but arithmetic operands remain six-bit.
Resource and latency values must be taken from the generated synthesis report.

## Install

Extract this directory as:

`D:\GitHub\vivado\vivado\F_Quantization_W8A8\hls_w6a6`

The shared FP32 model files must remain at:

`D:\GitHub\vivado\vivado\lenet_project\handoff\LeNet_DSE_Framework_2022_2\model`

## Verify and run

Use a Vitis HLS 2022.2 Command Prompt:

```bat
cd /d D:\GitHub\vivado\vivado\F_Quantization_W8A8\hls_w6a6
python scripts\verify_package.py
run_csim.bat
run_csynth.bat
run_cosim.bat
run_export.bat
```

Expected evidence markers are `W6A6_PACKAGE_PASS`, zero C-sim failures,
`C/RTL co-simulation finished: PASS`, and the matching batch PASS marker.

Generated artifacts are under `work\w6a6_hls\solution1`; the exported IP is
`export\lenet_w6a6_top_ip.zip`.

## Verified software reference

- MNIST samples: 10000
- FP32 accuracy: 98.82%
- W6A6 accuracy: 98.83%
- Prediction agreement with FP32: 99.87%
- INT32 overflow check: PASS

These software values are reference evidence only. HLS C-sim, C synthesis and
RTL co-simulation must be run on the target Windows installation before final
acceptance.
