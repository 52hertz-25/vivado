#ifndef PE_CONFIG_H_
#define PE_CONFIG_H_

// =====================================================================
// 成员 D：PE 阵列优化参数配置（Conv2 模块）
// ---------------------------------------------------------------------
// PE_OC  : 同时并行的输出通道数（Output-Channel PE 数量）
//          每轮处理 PE_OC 个输出通道，共享同一 5×5 输入窗口。
// PE_MAC : 单个输出通道内的乘加并行路数（MAC PE 数量）
//          25 次乘加按 PE_MAC 路分组并行，默认 5 路（5×5 卷积核分 5 组）。
//
// 通过 -D 编译选项可在命令行覆盖，例如：
//   vitis_hls -f run_pe_sweep.tcl 时在 run_pe_sweep.tcl 中按配置注入。
// =====================================================================

#ifndef PE_OC
#define PE_OC 4
#endif

#ifndef PE_MAC
#define PE_MAC 5
#endif

#endif  // PE_CONFIG_H_
