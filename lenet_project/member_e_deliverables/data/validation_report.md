# 成员 E DSE 数据核验记录

核验日期：2026-09-09

## 核验结果

- clk_10ns_baseline: raw csynth XML matches clock_dse_summary.csv
- clk_9ns: raw csynth XML matches clock_dse_summary.csv
- clk_8ns: raw csynth XML matches clock_dse_summary.csv
- clk_7_5ns: raw csynth XML matches clock_dse_summary.csv
- clk_7ns: raw csynth XML matches clock_dse_summary.csv
- struct_baseline: raw reports match structural_dse_summary.csv
- mac_unroll_2: raw reports match structural_dse_summary.csv
- mac_unroll_5: raw reports match structural_dse_summary.csv
- 10 ns baseline weakly dominates all clock candidates in cycles and LUT: True
- Structural baseline and both unroll candidates are identical: True
- Vivado timing met: True
- Vivado route state: Fully Routed

## 结论

原始 HLS XML 与已有两张汇总表一致。10 ns 基线同时具有最低延迟周期和最低 LUT，因此是本轮时钟扫描的 Pareto 最优配置。两档单独 MAC 循环展开没有改变综合结果。Vivado 设计已完成布局布线并满足时序约束。
