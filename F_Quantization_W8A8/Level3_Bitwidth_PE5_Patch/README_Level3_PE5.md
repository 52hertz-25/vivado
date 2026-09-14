# Level 3: bit-width × PE5 cross experiment

This patch adds one controlled synthesis point (`PE_MAC=5`) to each measured
quantized design: W8A8, W6A6 and W4A4. The original reports are the `PE_MAC=1`
baseline. Only an HLS unroll directive is added to the five-column convolution
inner loop, so the arithmetic model and trained weights are unchanged.

## Run

1. Extract this folder beside `hls_w8a8`, `hls_w6a6`, and `hls_w4a4`.
2. Open **Vitis HLS 2022.2 Command Prompt**.
3. Run:

   `cd /d D:\GitHub\vivado\vivado\F_Quantization_W8A8\Level3_Bitwidth_PE5_Patch`

   `run_all_pe5_csynth.bat`

The three runs are independent and may take several minutes. Results are copied
to each project's `final_delivery\reports\level3_pe5` directory. A combined CSV
is written to `Level3_Bitwidth_PE5_Patch\results\bitwidth_pe_cross_results.csv`.

The experiment passes when all three logs contain `LEVEL3_PE5_SYNTH_PASS` and
the combined CSV contains six rows: PE1 and PE5 for each bit-width.

