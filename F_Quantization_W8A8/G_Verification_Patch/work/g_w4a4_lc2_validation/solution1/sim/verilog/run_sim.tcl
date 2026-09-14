# ==============================================================
# Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.2 (64-bit)
# Tool Version Limit: 2019.12
# Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
# ==============================================================
set ::env(PATH) "$::env(PATH);D:/Xilinx/Vitis_HLS/2022.2/win64/tools/fpo_v7_1"

set ::env(PATH) "$::env(PATH);D:/Xilinx/Vitis_HLS/2022.2/win64/tools/fft_v9_1"
set ::env(PATH) "$::env(PATH);D:/Xilinx/Vitis_HLS/2022.2/win64/tools/fir_v7_0"
set ::env(PATH) "$::env(PATH);D:/Xilinx/Vitis_HLS/2022.2/win64/tools/dds_v6_0"

source check_sim.tcl
source dataflow_monitor_API.tcl

set ap_argv "D:/GitHub/vivado/vivado/F_Quantization_W8A8/hls_w8a8/data/mnist_w8a8 D:/GitHub/vivado/vivado/F_Quantization_W8A8/hls_w4a4/model/int4_weights D:/GitHub/vivado/vivado/F_Quantization_W8A8/G_Verification_Patch/results/g_balanced20_cosim.csv"
# --> test vector generation

::AP::printMsg INFO COSIM 302 COSIM_302_998

cd ../wrapc

file delete -force  "err.log"

if {![file exists cosim.tv.exe]} {
	::AP::printMsg ERR COSIM 321 COSIM_321_999
	return -code error -errorcode $::errorCode
}

set ret [catch {eval exec ./cosim.tv.exe D:/GitHub/vivado/vivado/F_Quantization_W8A8/hls_w8a8/data/mnist_w8a8 D:/GitHub/vivado/vivado/F_Quantization_W8A8/hls_w4a4/model/int4_weights D:/GitHub/vivado/vivado/F_Quantization_W8A8/G_Verification_Patch/results/g_balanced20_cosim.csv | tee temp0.log >&@ stdout} err]

if {$ret == 1} {
	::AP::printMsg ERR COSIM 320 COSIM_320_1000
	return -code error -errorcode $::errorCode
}

if {[file isfile lenet_w4a4_top.autotvin.dat]} {
	file delete -force lenet_w4a4_top.autotvin.dat
}

if {[file isfile lenet_w4a4_top.autotvout.dat]} {
	file delete -force lenet_w4a4_top.autotvout.dat
}

sc_sim_check $ret $err "temp0.log"

cd ../tv/cdatafile
set ret [check_tvin_file]

if {$ret == 1} {
	::AP::printMsg ERR COSIM 344 COSIM_344_1005
	return -code error -errorcode $::errorCode
}

cd ../

# --> verilog simulation

::AP::printMsg INFO COSIM 323 COSIM_323_1007

::AP::printMsg INFO COSIM 15 COSIM_15_1011

cd ../verilog

file delete -force ".exit.err"
file delete -force ".aesl_error"
file delete -force "err.log"

if {[file isfile run_xsim.bat]} {
	set ret [catch {eval exec "./run_xsim.bat | tee temp2.log" >&@ stdout} err]
}
    df_record_move

cd ../tv/rtldatafile

set ret [check_tvout_file]

if {$ret == 1} {
	::AP::printMsg ERR COSIM 344 COSIM_344_1020
	return -code error -errorcode $::errorCode
}

cd ../../wrapc_pc

::AP::printMsg INFO COSIM 316 COSIM_316_1021

if {![file exists cosim.pc.exe]} {
    ::AP::printMsg ERR COSIM 320 COSIM_320_1022
    return -code error -errorcode $::errorCode
}

set ret [catch {eval exec ./cosim.pc.exe D:/GitHub/vivado/vivado/F_Quantization_W8A8/hls_w8a8/data/mnist_w8a8 D:/GitHub/vivado/vivado/F_Quantization_W8A8/hls_w4a4/model/int4_weights D:/GitHub/vivado/vivado/F_Quantization_W8A8/G_Verification_Patch/results/g_balanced20_cosim.csv | tee temp0.log >&@ stdout} err]

sc_sim_check $ret $err "temp3.log"
