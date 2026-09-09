# 成员 E DSE 可复现实验包

这个目录只包含成员 E 的 LeNet HLS/Vivado 设计空间探索材料。为控制仓库体积，未复制约 500 MB 的 `solution1` 中间工程；关键的 10 ns 基线 `csynth.rpt/xml` 与 Vivado post-route 报告保存在上级 `source_reports/`，完整中间工程仍保留在原始 `handoff/LeNet_DSE_Framework_2022_2/` 中。

## 已完成实验

- 时钟约束：10 ns、9 ns、8 ns、7.5 ns、7 ns，共 5 组。
- 结构探索：baseline、MAC Unroll ×2、MAC Unroll ×5，共 3 组。
- 所有结果已从原始 `csynth.xml` 重新提取并与原有汇总 CSV 逐项核验。
- 10 ns 基线已完成 Vivado 布线后时序、资源与功耗报告核验。

## 目录用途

- `configs/`：批量实验配置。
- `directives/`：各配置使用的 HLS 指令。
- `src/`、`include/`、`tb/`、`model/`：基线源码、头文件、测试平台和模型数据。
- `variants/`：结构实验的独立源码变体。
- `scripts/`：运行、收集与绘图脚本。
- `results/`：原始汇总表、核验后的汇总表及核验记录。

## 复现方式

在 Vitis HLS 2022.2 命令环境中，从本目录执行 `run_all.bat`。重新核验已生成报告并输出课程交付图表时，在仓库根目录运行：

```powershell
E:\anaconda\python.exe lenet_project\member_e_deliverables\scripts\build_member_e_results.py
```

目前证据已经满足 `E任务优化方案.docx` 的探索与归档要求，因此没有继续修改 LeNet 算子实现。若教师明确要求“实际代码优化”，再以权重缓存、数组分区和并行 PE 为一组受控候选，并重新执行 CSim、HLS 与 Vivado 实现。
