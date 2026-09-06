:: ==============================================================
:: Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.2 (64-bit)
:: Tool Version Limit: 2019.12
:: Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
:: ==============================================================

@echo off

D:/Xilinx/Vivado/2022.2/bin/vivado  -notrace -mode batch -source ipi_example.tcl -tclargs xc7z020-clg400-1 ../user_org_hls_lenet_full_top_1_0.zip
