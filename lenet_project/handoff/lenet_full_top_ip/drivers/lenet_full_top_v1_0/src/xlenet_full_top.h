// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.2 (64-bit)
// Tool Version Limit: 2019.12
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// ==============================================================
#ifndef XLENET_FULL_TOP_H
#define XLENET_FULL_TOP_H

#ifdef __cplusplus
extern "C" {
#endif

/***************************** Include Files *********************************/
#ifndef __linux__
#include "xil_types.h"
#include "xil_assert.h"
#include "xstatus.h"
#include "xil_io.h"
#else
#include <stdint.h>
#include <assert.h>
#include <dirent.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stddef.h>
#endif
#include "xlenet_full_top_hw.h"

/**************************** Type Definitions ******************************/
#ifdef __linux__
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
#else
typedef struct {
    u16 DeviceId;
    u64 Control_BaseAddress;
} XLenet_full_top_Config;
#endif

typedef struct {
    u64 Control_BaseAddress;
    u32 IsReady;
} XLenet_full_top;

typedef u32 word_type;

/***************** Macros (Inline Functions) Definitions *********************/
#ifndef __linux__
#define XLenet_full_top_WriteReg(BaseAddress, RegOffset, Data) \
    Xil_Out32((BaseAddress) + (RegOffset), (u32)(Data))
#define XLenet_full_top_ReadReg(BaseAddress, RegOffset) \
    Xil_In32((BaseAddress) + (RegOffset))
#else
#define XLenet_full_top_WriteReg(BaseAddress, RegOffset, Data) \
    *(volatile u32*)((BaseAddress) + (RegOffset)) = (u32)(Data)
#define XLenet_full_top_ReadReg(BaseAddress, RegOffset) \
    *(volatile u32*)((BaseAddress) + (RegOffset))

#define Xil_AssertVoid(expr)    assert(expr)
#define Xil_AssertNonvoid(expr) assert(expr)

#define XST_SUCCESS             0
#define XST_DEVICE_NOT_FOUND    2
#define XST_OPEN_DEVICE_FAILED  3
#define XIL_COMPONENT_IS_READY  1
#endif

/************************** Function Prototypes *****************************/
#ifndef __linux__
int XLenet_full_top_Initialize(XLenet_full_top *InstancePtr, u16 DeviceId);
XLenet_full_top_Config* XLenet_full_top_LookupConfig(u16 DeviceId);
int XLenet_full_top_CfgInitialize(XLenet_full_top *InstancePtr, XLenet_full_top_Config *ConfigPtr);
#else
int XLenet_full_top_Initialize(XLenet_full_top *InstancePtr, const char* InstanceName);
int XLenet_full_top_Release(XLenet_full_top *InstancePtr);
#endif

void XLenet_full_top_Start(XLenet_full_top *InstancePtr);
u32 XLenet_full_top_IsDone(XLenet_full_top *InstancePtr);
u32 XLenet_full_top_IsIdle(XLenet_full_top *InstancePtr);
u32 XLenet_full_top_IsReady(XLenet_full_top *InstancePtr);
void XLenet_full_top_EnableAutoRestart(XLenet_full_top *InstancePtr);
void XLenet_full_top_DisableAutoRestart(XLenet_full_top *InstancePtr);

void XLenet_full_top_Set_feature_in(XLenet_full_top *InstancePtr, u64 Data);
u64 XLenet_full_top_Get_feature_in(XLenet_full_top *InstancePtr);
void XLenet_full_top_Set_weight(XLenet_full_top *InstancePtr, u64 Data);
u64 XLenet_full_top_Get_weight(XLenet_full_top *InstancePtr);
void XLenet_full_top_Set_bias(XLenet_full_top *InstancePtr, u64 Data);
u64 XLenet_full_top_Get_bias(XLenet_full_top *InstancePtr);
void XLenet_full_top_Set_feature_out(XLenet_full_top *InstancePtr, u64 Data);
u64 XLenet_full_top_Get_feature_out(XLenet_full_top *InstancePtr);

void XLenet_full_top_InterruptGlobalEnable(XLenet_full_top *InstancePtr);
void XLenet_full_top_InterruptGlobalDisable(XLenet_full_top *InstancePtr);
void XLenet_full_top_InterruptEnable(XLenet_full_top *InstancePtr, u32 Mask);
void XLenet_full_top_InterruptDisable(XLenet_full_top *InstancePtr, u32 Mask);
void XLenet_full_top_InterruptClear(XLenet_full_top *InstancePtr, u32 Mask);
u32 XLenet_full_top_InterruptGetEnabled(XLenet_full_top *InstancePtr);
u32 XLenet_full_top_InterruptGetStatus(XLenet_full_top *InstancePtr);

#ifdef __cplusplus
}
#endif

#endif
