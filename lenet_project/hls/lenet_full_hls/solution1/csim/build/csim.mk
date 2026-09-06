# ==============================================================
# Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.2 (64-bit)
# Tool Version Limit: 2019.12
# Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
# ==============================================================
CSIM_DESIGN = 1

__SIM_FPO__ = 1

__SIM_MATHHLS__ = 1

__SIM_FFT__ = 1

__SIM_FIR__ = 1

__SIM_DDS__ = 1

ObjDir = obj

HLS_SOURCES = ../../../../../member_c_conv_hls/tb/tb_lenet_conv.cpp ../../../../../member_c_conv_hls/src/lenet_conv.cpp

override TARGET := csim.exe

AUTOPILOT_ROOT := D:/Xilinx/Vitis_HLS/2022.2
AUTOPILOT_MACH := win64
ifdef AP_GCC_M32
  AUTOPILOT_MACH := Linux_x86
  IFLAG += -m32
endif
ifndef AP_GCC_PATH
  AP_GCC_PATH := D:/Xilinx/Vitis_HLS/2022.2/tps/win64/msys64/mingw64/bin
endif
AUTOPILOT_TOOL := ${AUTOPILOT_ROOT}/${AUTOPILOT_MACH}/tools
AP_CLANG_PATH := ${AUTOPILOT_ROOT}/tps/win64/msys64/mingw64/bin
AUTOPILOT_TECH := ${AUTOPILOT_ROOT}/common/technology


IFLAG += -I "${AUTOPILOT_ROOT}/include"
IFLAG += -I "${AUTOPILOT_ROOT}/include/ap_sysc"
IFLAG += -I "${AUTOPILOT_TECH}/generic/SystemC"
IFLAG += -I "${AUTOPILOT_TECH}/generic/SystemC/AESL_FP_comp"
IFLAG += -I "${AUTOPILOT_TECH}/generic/SystemC/AESL_comp"
IFLAG += -I "${AUTOPILOT_TOOL}/auto_cc/include"
IFLAG += -D__HLS_COSIM__

IFLAG += -D__HLS_CSIM__

IFLAG += -D__VITIS_HLS__

IFLAG += -D__SIM_FPO__

IFLAG += -D__SIM_FFT__

IFLAG += -D__SIM_FIR__

IFLAG += -D__SIM_DDS__

IFLAG += -D__DSP48E1__
IFLAG += -ID:/lenet_project/member_c_conv_hls/include -ID:/lenet_project/member_c_conv_hls/tb -DLENET_HLS_TOP_FULL -std=c++11 -Wno-unknown-pragmas 
IFLAG += -g
IFLAG += -DNT
LFLAG += -Wl,--enable-auto-import 
DFLAG += -D__xilinx_ip_top= -DAESL_TB
CCFLAG += -Werror=return-type
CCFLAG += -Wno-abi
TOOLCHAIN += 



include ./Makefile.rules

all: $(TARGET)



$(ObjDir)/tb_lenet_conv.o: ../../../../../member_c_conv_hls/tb/tb_lenet_conv.cpp $(ObjDir)/.dir
	$(Echo) "   Compiling ../../../../../member_c_conv_hls/tb/tb_lenet_conv.cpp in $(BuildMode) mode" $(AVE_DIR_DLOG)
	$(Verb)  $(CC) ${CCFLAG} -c -MMD -ID:/lenet_project/member_c_conv_hls/include -ID:/lenet_project/member_c_conv_hls/tb -DLENET_HLS_TOP_FULL -std=c++11 -Wno-unknown-pragmas -Wno-unknown-pragmas  $(IFLAG) $(DFLAG) $< -o $@ ; \

-include $(ObjDir)/tb_lenet_conv.d

$(ObjDir)/lenet_conv.o: ../../../../../member_c_conv_hls/src/lenet_conv.cpp $(ObjDir)/.dir
	$(Echo) "   Compiling ../../../../../member_c_conv_hls/src/lenet_conv.cpp in $(BuildMode) mode" $(AVE_DIR_DLOG)
	$(Verb)  $(CC) ${CCFLAG} -c -MMD -ID:/lenet_project/member_c_conv_hls/include  $(IFLAG) $(DFLAG) $< -o $@ ; \

-include $(ObjDir)/lenet_conv.d
