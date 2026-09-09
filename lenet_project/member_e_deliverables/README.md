# 成员 E 工作说明（陈正堃）

本目录是智能芯片设计课程“任务 2：LeNet”中成员 E 的独立交付区，负责 **Vitis HLS 设计空间探索（DSE）、结果核验、Pareto 分析，以及 Vivado 布线后证据归档**。本目录不包含其他成员的量化、训练或系统集成任务。

## 1. 已完成工作

### 1.1 时钟约束 DSE

核验了 5 组 Vitis HLS 2022.2 综合结果：

- `clk_10ns_baseline`
- `clk_9ns`
- `clk_8ns`
- `clk_7_5ns`
- `clk_7ns`

`scripts/build_member_e_results.py` 会直接读取各工程的 `lenet_full_top_csynth.xml`，提取目标/估计时钟、Latency、Interval、LUT、FF、BRAM_18K 和 DSP，并与已有 `clock_dse_summary.csv` 逐项比对。若原始 XML 与汇总表不一致，脚本会终止。

### 1.2 结构 DSE

核验了 3 组 10 ns 结构实验：baseline、MAC Unroll ×2 和 MAC Unroll ×5。三组实验均通过 CSim，且综合后的延迟和资源完全相同。因此，单独展开 MAC 循环没有产生有效硬件并行度，不能描述为优化成功。

### 1.3 Vivado post-route 核验

从现有 Vivado 2022.2 实现报告中提取并归档了布线状态、时序、资源和功耗。Windows GUI 截图辅助程序无法连接，因此交付材料使用原始 `.rpt` 的可读摘录图，而不是冒充 Vivado GUI 截屏。报告原文保存在 `source_reports/`。

## 2. 关键结果

| 项目 | 最终结果 |
|---|---:|
| 最终候选 | `clk_10ns_baseline` |
| HLS Latency | 1,647,854 cycles |
| 按 10 ns 换算延迟 | 16.479 ms |
| HLS LUT / FF | 17,108 / 13,452 |
| HLS BRAM_18K / DSP | 70 / 5 |
| Vivado WNS / WHS | +0.415 ns / +0.028 ns |
| Vivado LUT / Registers | 11,612 / 17,612 |
| Vivado BRAM tiles / DSP | 37 / 5 |
| Vivado Total On-Chip Power | 1.848 W（Medium confidence） |

虽然收紧时钟会提高估计 Fmax，但 HLS 调度周期明显增加。10 ns 基线在 5 个时钟配置中同时具有最少延迟周期、最低按目标周期换算的总延迟和最低 LUT，因此被选为最终方案。

> 注意：HLS 的 `BRAM_18K` 与 Vivado 的 `Block RAM Tile` 是不同报告口径，不能直接相减。1.848 W 是未加载仿真活动文件时的 Vivado 估算，不是板级实测功耗。

## 3. 目录结构

| 路径 | 内容 |
|---|---|
| `data/` | 核验后的时钟 DSE、结构 DSE、Vivado 汇总和核验记录 |
| `figures/` | 时钟曲线、Pareto 图、结构对比图和 Vivado 报告摘录图 |
| `source_reports/` | 10 ns 基线 HLS `csynth.rpt/xml` 与 Vivado 原始报告 |
| `dse_package/` | 配置、指令、源码、测试平台、模型、结构变体、脚本和结果快照 |
| `scripts/` | 数据、证据图、Word 和 PowerPoint 的生成代码 |
| `report/` | 成员 E 的正式实验报告 |
| `slides/` | 成员 E 的 3 页答辩 PowerPoint |

## 4. 正式交付文件

- `report/成员E_LeNet_DSE实验报告.docx`
- `slides/成员E_LeNet_DSE答辩.pptx`
- `data/clock_dse_validated.csv`
- `data/structural_dse_validated.csv`
- `data/vivado_post_route_summary.csv`
- `data/validation_report.md`
- `figures/clock_latency_cycles.png`
- `figures/pareto_latency_lut.png`
- `figures/structural_dse_comparison.png`

PPT 第 1 页的实验矩阵是原生可编辑表格，第 2 页的时钟曲线和 Pareto 图是原生可编辑 PowerPoint 图表。

## 5. 数据和图表复现

在仓库根目录执行：

```powershell
E:\anaconda\python.exe lenet_project\member_e_deliverables\scripts\build_member_e_results.py
```

该命令会：

1. 从 8 组原始 HLS XML 重新提取指标；
2. 检查原始报告与已有两张 CSV 是否一致；
3. 解析 Vivado timing、utilization、power 和 route status 报告；
4. 重新生成核验后的 CSV、JSON、核验记录和三张 DSE 图。

其余生成脚本：

- `scripts/build_vivado_evidence.mjs`：由 Vivado `.rpt` 生成证据摘录图；
- `scripts/build_member_e_report.py`：生成 Word 实验报告；
- `scripts/build_member_e_slides.mjs`：生成并校验 PowerPoint。

完整 HLS 中间工程仍位于 `lenet_project/handoff/LeNet_DSE_Framework_2022_2/`。本交付目录没有重复复制约 500 MB 的 `solution1` 缓存，但 `dse_package/` 已保留重新运行实验所需的源码、配置、模型、测试平台和脚本。

## 6. 工作边界与后续条件

本次工作对已有 8 组 HLS 原始报告和最终 Vivado 实现进行了重新提取、核验、分析和归档，**没有重新执行全部 HLS/Vivado 综合，也没有新增一版 LeNet 算子优化源码**。

根据 `E任务优化方案.docx` 的停止条件，现有 DSE 已足以形成成员 E 的独立贡献。若教师明确要求“必须体现代码级优化”，下一步应新建独立候选版本，实现：

1. 权重片上缓存；
2. 缓存数组 `ARRAY_PARTITION`；
3. 明确的并行 PE/MAC 数据通路；
4. 重新完成 CSim、HLS、导出 IP 和 Vivado post-route 对比。

新候选不得覆盖当前 10 ns 基线，且只有数值一致性、延迟/资源和 Vivado 时序都通过后，才能称为有效优化。

## 7. Git 说明

根目录 `.gitignore` 已排除 `课件/`、私有构建目录、图表工作簿快照、渲染预览、`node_modules` 连接、Python 缓存和 Vivado/Vitis 临时日志。正式源码、结果、报告和答辩材料保留在版本控制范围内。
