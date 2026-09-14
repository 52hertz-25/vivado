LeNet Level 3 full-MNIST C-simulation patch
============================================================

Purpose
-------
Adds 10,000-sample MNIST C-simulation entry points for W6A6 and W4A4.
The existing W8A8 binary dataset is reused. Existing HLS projects and reports
are not overwritten: dedicated work projects w6a6_mnist_hls and
w4a4_mnist_hls are created.

Installation
------------
1. Extract this folder beside hls_w8a8, hls_w6a6 and hls_w4a4.
2. Run install_patch.bat from ordinary CMD.

Quick validation (Vitis HLS 2022.2 Command Prompt)
--------------------------------------------------
cd /d D:\GitHub\vivado\vivado\F_Quantization_W8A8\hls_w6a6
run_mnist_csim.bat 100 > W6A6_mnist_100.log 2>&1
findstr /i /c:"W6A6_MNIST_SUMMARY" /c:"BATCH_PASS" /c:"FAIL" /c:"ERROR:" W6A6_mnist_100.log

cd /d D:\GitHub\vivado\vivado\F_Quantization_W8A8\hls_w4a4
run_mnist_csim.bat 100 > W4A4_mnist_100.log 2>&1
findstr /i /c:"W4A4_MNIST_SUMMARY" /c:"BATCH_PASS" /c:"FAIL" /c:"ERROR:" W4A4_mnist_100.log

Full runs
---------
Run the two 10,000-sample jobs sequentially, not simultaneously.

cd /d D:\GitHub\vivado\vivado\F_Quantization_W8A8\hls_w6a6
run_mnist_csim.bat 10000 > W6A6_mnist_10000.log 2>&1

cd /d D:\GitHub\vivado\vivado\F_Quantization_W8A8\hls_w4a4
run_mnist_csim.bat 10000 > W4A4_mnist_10000.log 2>&1

Outputs
-------
hls_w6a6\reports\mnist\w6a6_mnist_<N>_results.csv
hls_w4a4\reports\mnist\w4a4_mnist_<N>_results.csv

The CSV contains accuracy, the 90 percent threshold result, and a 10x10
confusion matrix. A below-threshold result returns exit code 1 by design.
