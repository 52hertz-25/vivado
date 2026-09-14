// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.2 (64-bit)
// Tool Version Limit: 2019.12
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// ==============================================================
/***************************** Include Files *********************************/
#include "xlenet_w8a8_top.h"

/************************** Function Implementation *************************/
#ifndef __linux__
int XLenet_w8a8_top_CfgInitialize(XLenet_w8a8_top *InstancePtr, XLenet_w8a8_top_Config *ConfigPtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(ConfigPtr != NULL);

    InstancePtr->Control_BaseAddress = ConfigPtr->Control_BaseAddress;
    InstancePtr->IsReady = XIL_COMPONENT_IS_READY;

    return XST_SUCCESS;
}
#endif

void XLenet_w8a8_top_Start(XLenet_w8a8_top *InstancePtr) {
    u32 Data;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XLenet_w8a8_top_ReadReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_AP_CTRL) & 0x80;
    XLenet_w8a8_top_WriteReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_AP_CTRL, Data | 0x01);
}

u32 XLenet_w8a8_top_IsDone(XLenet_w8a8_top *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XLenet_w8a8_top_ReadReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_AP_CTRL);
    return (Data >> 1) & 0x1;
}

u32 XLenet_w8a8_top_IsIdle(XLenet_w8a8_top *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XLenet_w8a8_top_ReadReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_AP_CTRL);
    return (Data >> 2) & 0x1;
}

u32 XLenet_w8a8_top_IsReady(XLenet_w8a8_top *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XLenet_w8a8_top_ReadReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_AP_CTRL);
    // check ap_start to see if the pcore is ready for next input
    return !(Data & 0x1);
}

void XLenet_w8a8_top_EnableAutoRestart(XLenet_w8a8_top *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XLenet_w8a8_top_WriteReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_AP_CTRL, 0x80);
}

void XLenet_w8a8_top_DisableAutoRestart(XLenet_w8a8_top *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XLenet_w8a8_top_WriteReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_AP_CTRL, 0);
}

void XLenet_w8a8_top_Set_feature_in(XLenet_w8a8_top *InstancePtr, u64 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XLenet_w8a8_top_WriteReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_FEATURE_IN_DATA, (u32)(Data));
    XLenet_w8a8_top_WriteReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_FEATURE_IN_DATA + 4, (u32)(Data >> 32));
}

u64 XLenet_w8a8_top_Get_feature_in(XLenet_w8a8_top *InstancePtr) {
    u64 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XLenet_w8a8_top_ReadReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_FEATURE_IN_DATA);
    Data += (u64)XLenet_w8a8_top_ReadReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_FEATURE_IN_DATA + 4) << 32;
    return Data;
}

void XLenet_w8a8_top_Set_weight(XLenet_w8a8_top *InstancePtr, u64 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XLenet_w8a8_top_WriteReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_WEIGHT_DATA, (u32)(Data));
    XLenet_w8a8_top_WriteReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_WEIGHT_DATA + 4, (u32)(Data >> 32));
}

u64 XLenet_w8a8_top_Get_weight(XLenet_w8a8_top *InstancePtr) {
    u64 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XLenet_w8a8_top_ReadReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_WEIGHT_DATA);
    Data += (u64)XLenet_w8a8_top_ReadReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_WEIGHT_DATA + 4) << 32;
    return Data;
}

void XLenet_w8a8_top_Set_logits(XLenet_w8a8_top *InstancePtr, u64 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XLenet_w8a8_top_WriteReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_LOGITS_DATA, (u32)(Data));
    XLenet_w8a8_top_WriteReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_LOGITS_DATA + 4, (u32)(Data >> 32));
}

u64 XLenet_w8a8_top_Get_logits(XLenet_w8a8_top *InstancePtr) {
    u64 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XLenet_w8a8_top_ReadReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_LOGITS_DATA);
    Data += (u64)XLenet_w8a8_top_ReadReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_LOGITS_DATA + 4) << 32;
    return Data;
}

void XLenet_w8a8_top_InterruptGlobalEnable(XLenet_w8a8_top *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XLenet_w8a8_top_WriteReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_GIE, 1);
}

void XLenet_w8a8_top_InterruptGlobalDisable(XLenet_w8a8_top *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XLenet_w8a8_top_WriteReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_GIE, 0);
}

void XLenet_w8a8_top_InterruptEnable(XLenet_w8a8_top *InstancePtr, u32 Mask) {
    u32 Register;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Register =  XLenet_w8a8_top_ReadReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_IER);
    XLenet_w8a8_top_WriteReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_IER, Register | Mask);
}

void XLenet_w8a8_top_InterruptDisable(XLenet_w8a8_top *InstancePtr, u32 Mask) {
    u32 Register;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Register =  XLenet_w8a8_top_ReadReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_IER);
    XLenet_w8a8_top_WriteReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_IER, Register & (~Mask));
}

void XLenet_w8a8_top_InterruptClear(XLenet_w8a8_top *InstancePtr, u32 Mask) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XLenet_w8a8_top_WriteReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_ISR, Mask);
}

u32 XLenet_w8a8_top_InterruptGetEnabled(XLenet_w8a8_top *InstancePtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    return XLenet_w8a8_top_ReadReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_IER);
}

u32 XLenet_w8a8_top_InterruptGetStatus(XLenet_w8a8_top *InstancePtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    return XLenet_w8a8_top_ReadReg(InstancePtr->Control_BaseAddress, XLENET_W8A8_TOP_CONTROL_ADDR_ISR);
}

