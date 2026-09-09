# LeNet HLS 自动化 DSE 框架


## 核心任务

1. 保留 `fp32_baseline` 作为不可改的对照组。
2. 由 E 自己选择至少 3 个候选方案，例如：定点位宽、PE 数、循环展开因子或流水化位置。
3. 每次只改变明确记录的参数，先保证 C 仿真/精度合格，再比较 HLS 延迟与资源。
4. 对 1–2 个最佳候选重新导出 IP，并在 Vivado 中跑实现，补录 WNS、实际 LUT/BRAM/DSP 和功耗。
5. 画出 Pareto 图并说明为什么选择最终方案。

这保留了 E 的研究重点和独立贡献；框架只承担机械的批量运行与数据汇总。

## 第一次运行（只跑基线）

1. 解压到纯英文路径，例如 `D:\lenet_project\handoff\LeNet_E_DSE_Framework_2022_2`。
2. 从 Windows 开始菜单打开 **Vitis HLS 2022.2 Command Prompt**。
3. 双击或在命令行执行 `run_all.bat`。
4. 等待 C Simulation 和 C Synthesis 完成。
5. 查看 `results\hls_dse_results.csv`。

如果双击提示找不到 `vitis_hls.bat`，必须从 Vitis HLS 2022.2 Command Prompt 启动，不要从普通 CMD 启动。

## 新增一个候选方案

### 方案 A：只改 Pipeline/Unroll 指令

1. 编辑 `directives\candidate_pipeline.tcl`，把示例中的 `LOOP_LABEL` 换成综合报告中的真实循环标签。
2. 编辑 `configs\configs.tcl`，把 `candidate_pipeline` 的 `enabled 0` 改为 `enabled 1`。
3. 执行 `run_all.bat`。

### 方案 B：改位宽、PE 或源代码结构

1. 新建 `variants\候选名\lenet_conv.cpp`，不要覆盖 `src\lenet_conv.cpp` 基线。
2. 在 `configs\configs.tcl` 复制一条配置，修改 `id` 和 `source_cpp`，再设 `enabled 1`。
3. 位宽改变后必须先验证数值精度；结果填入 `results\accuracy_template.csv`。
4. 执行 `run_all.bat`。

## 输出和判定规则

- `work\配置名\`：各候选的独立 HLS 工程。
- `results\hls_dse_results.csv`：自动提取的 HLS 时钟、延迟、BRAM_18K、DSP、FF、LUT。
- `results\verified_baseline.csv`：小组已验证的基线数据。
- `results\accuracy_template.csv`：E 填写精度/误差。
- `py -3 scripts\plot_pareto.py`：生成延迟—LUT 散点图（需 matplotlib）。

候选方案只有同时满足以下条件才可进入 Vivado：

- C Simulation 通过；
- 精度达到小组预先约定阈值；
- HLS 结果至少在延迟、资源或功耗预期中有一项明显改善；
- 接口仍保持 `s_axilite control + 4 个 m_axi`，否则现有 Block Design 不能直接替换。

## 已验证基线（报告时可引用）

| 阶段 | 延迟 | LUT | FF/寄存器 | BRAM | DSP | 时序/功耗 |
|---|---:|---:|---:|---:|---:|---|
| Vitis HLS 2022.2 | 1,647,854 cycles | 17,108 | 13,452 | 70 BRAM_18K | 5 | 10 ns 目标 |
| Vivado post-route | — | 11,612 | 17,612 | 37 tiles | 5 | WNS +0.415 ns；WHS +0.028 ns；1.848 W* |

\* 1.848 W 为 Vivado 默认/向量无关活动下的 Medium-confidence 估算，不应写成实测板级功耗。

## 实验记录最低要求

每个配置必须记录：配置 ID、唯一改动、C 仿真是否通过、精度/最大误差、HLS 延迟、LUT、FF、BRAM、DSP。进入 Vivado 的候选再记录 post-route WNS/WHS 和功耗估算。不要混用 HLS 的 `BRAM_18K` 与 Vivado 的 `BRAM tile` 单位。

## 当前范围边界

脚本不会替 E 自动决定位宽、PE 数或在哪个循环上 Pipeline/Unroll；这些选择、实验解释和最终 Pareto 决策正是 E 的重点贡献。脚本也不会自动修改 Vivado Block Design，最佳候选 IP 的替换仍应在基线工程副本中进行。
