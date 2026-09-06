############################################################
## This file is generated automatically by Vitis HLS.
## Please DO NOT edit it.
## Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
############################################################
open_project lenet_full_hls
set_top lenet_full_top
add_files ../member_c_conv_hls/src/lenet_conv.cpp -cflags "-ID:/lenet_project/member_c_conv_hls/include"
add_files ../member_c_conv_hls/include/lenet_conv.h
add_files -tb ../member_c_conv_hls/tb/npy_reader.h
add_files -tb ../member_c_conv_hls/tb/tb_lenet_conv.cpp -cflags "-DLENET_HLS_TOP_FULL -ID:/lenet_project/member_c_conv_hls/include -ID:/lenet_project/member_c_conv_hls/tb -std=c++11"
open_solution "solution1" -flow_target vivado
set_part {xc7z020clg400-1}
create_clock -period 10 -name default
config_export -description {LeNet-5 full network accelerator for Zynq-7020} -display_name {LeNet Full Accelerator} -library hls -output D:/lenet_project/hls/lenet_full_hls/solution1/impl/ip -vendor user.org -version 1.0
#source "./lenet_full_hls/solution1/directives.tcl"
csim_design -argv {D:/lenet_project/model} -clean
csynth_design
cosim_design
export_design -rtl verilog -format ip_catalog -output D:/lenet_project/hls/lenet_full_hls/solution1/impl/ip
