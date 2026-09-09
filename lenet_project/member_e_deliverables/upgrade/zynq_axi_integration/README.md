# Zynq AXI 集成交付

本目录是成员 E 对 LeNet 任务 2 的 Zynq 端集成交付，包含 HLS IP、Block Design、地址与寄存器说明、PS 调用流程、实现报告、XSA 和可复现脚本。它解决的是“加速核如何被 Zynq PS 控制、如何访问 DDR，以及现有工程能否通过 Vivado 设计校验和实现结果复核”。

## 2026 年 9 月 9 日实际 Vivado 复核

已在本机 Vivado 2022.2 中执行 `scripts/rerun_vivado_reports.tcl`，而不是仅整理历史文件。脚本完成以下动作：

1. 打开 `LeNet_Zynq_System.xpr` 与 `lenet_system.bd`。
2. 执行 `validate_bd_design -force` 并重新生成 Block Design 输出。
3. 打开现有 `impl_1` 路由结果，重新导出布线、时序、层次资源和功耗报告。
4. 导出不含 bitstream 的 `lenet_system_wrapper.xsa`。

本次实测结果：

| 项目 | 结果 |
| --- | --- |
| 完全布线连接 | 26,721 / 26,721 |
| 布线错误 | 0 |
| 目标周期 | 10 ns |
| WNS / TNS | +0.415 ns / 0 ns |
| WHS / THS | +0.028 ns / 0 ns |
| 顶层 LUT / FF | 11,612 / 17,612 |
| RAMB36 / RAMB18 | 33 / 8，即 37 个 BRAM Tile 等效量 |
| DSP | 5 |

完整运行转录保存在 `evidence/fresh_vivado_rerun_20260909.txt`，末尾成功标记为 `MEMBER_E_VIVADO_RERUN_PASS`。本次生成的报告和硬件平台位于 `reports/rerun/`。

## 目录说明

- `ip/`：可导入 Vivado IP Catalog 的 `lenet_full_top` HLS IP。
- `bd/lenet_system.bd`：交付用 Block Design 源文件。
- `docs/`：连接关系、地址和寄存器表、PS 端调用顺序。
- `figures/`：由 BD 信息重绘的连接图。
- `reports/archived_impl/`：原工程历史实现报告的归档副本。
- `reports/rerun/`：本次 Vivado 2022.2 实际复核生成的报告与 XSA。
- `evidence/`：Block Design 校验历史和本次工具运行转录。
- `scripts/`：批处理复核脚本与交付清单生成器。

## 复现

在 PowerShell 中执行：

```powershell
.\scripts\run_vivado_reports.ps1
```

脚本会补齐 Vivado 批处理所需的 `PROCESSOR_ARCHITECTURE=AMD64` 环境变量，检查进程退出码并验证成功标记。

## 边界

本交付证明现有 Zynq 工程的 Block Design 可通过校验、已有实现可正确打开并重新出具报告。它没有宣称完成开发板下载或板上运行；板级验证需要组内提供目标开发板、约束和运行输入后另行执行。
