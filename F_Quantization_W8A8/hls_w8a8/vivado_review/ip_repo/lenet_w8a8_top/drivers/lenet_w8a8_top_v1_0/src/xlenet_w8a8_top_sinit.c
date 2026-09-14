// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.2 (64-bit)
// Tool Version Limit: 2019.12
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// ==============================================================
#ifndef __linux__

#include "xstatus.h"
#include "xparameters.h"
#include "xlenet_w8a8_top.h"

extern XLenet_w8a8_top_Config XLenet_w8a8_top_ConfigTable[];

XLenet_w8a8_top_Config *XLenet_w8a8_top_LookupConfig(u16 DeviceId) {
	XLenet_w8a8_top_Config *ConfigPtr = NULL;

	int Index;

	for (Index = 0; Index < XPAR_XLENET_W8A8_TOP_NUM_INSTANCES; Index++) {
		if (XLenet_w8a8_top_ConfigTable[Index].DeviceId == DeviceId) {
			ConfigPtr = &XLenet_w8a8_top_ConfigTable[Index];
			break;
		}
	}

	return ConfigPtr;
}

int XLenet_w8a8_top_Initialize(XLenet_w8a8_top *InstancePtr, u16 DeviceId) {
	XLenet_w8a8_top_Config *ConfigPtr;

	Xil_AssertNonvoid(InstancePtr != NULL);

	ConfigPtr = XLenet_w8a8_top_LookupConfig(DeviceId);
	if (ConfigPtr == NULL) {
		InstancePtr->IsReady = 0;
		return (XST_DEVICE_NOT_FOUND);
	}

	return XLenet_w8a8_top_CfgInitialize(InstancePtr, ConfigPtr);
}

#endif

