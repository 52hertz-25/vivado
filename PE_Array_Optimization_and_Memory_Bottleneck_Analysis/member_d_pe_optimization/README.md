# 成员 D：LeNet-5 Conv2 PE 阵列优化（最终提交）

基于成员 C 的模型 V2 完整 HLS 基线，在**不改变顶层接口**的前提下优化 Conv2：先复现基线，再依次完成
Pipeline（D1）、PE_MAC=5（D2）、PE_OC=2/4（D3/D4）实验，最后通过**局部数组缓存**（D5）解除 AXI 端口瓶颈，
使 Conv2 流水线真正成形，实现 **80.44× 加速**（同环境 Vitis HLS 2022.2 口径），并通过 RTL Co-sim 与 10 样本端到端验证。

## 目录结构

```text
member_d_pe_optimization/
├─ include/
│  ├─ lenet_conv.h            # 统一头文件（来自成员 C）
│  └─ pe_config.h             # PE_OC / PE_MAC 参数（默认 4 / 5，可用 -D 覆盖）
├─ src/
│  ├─ lenet_conv_pe.cpp       # 最终版本源码（最终推荐配置）
│  └─ archive/                # 各版本源码存档（D0~D5，可回溯复现）
├─ tb/
│  ├─ tb_lenet_conv.cpp       # 逐层/端到端测试平台（来自成员 C，未改动）
│  └─ npy_reader.h
├─ scripts/
│  ├─ run_pe_sweep.tcl        # 按版本跑 Conv2 C-sim + 综合（D0~D5）
│  ├─ run_d5_cosim.tcl        # 最终候选 RTL Co-sim
│  ├─ run_full_pe_csim.tcl    # 完整网络 10 样本端到端 C-sim
│  └─ parse_csynth.py         # 报告解析工具（生成实验表数据）
├─ results/
│  ├─ pe_experiments.csv      # 实验对比表（版本/II/延迟/加速比/资源/时钟/误差）
│  ├─ csim_results.txt        # 最终源码本地 C++ 回归输出（10 样本）
│  ├─ full_network_csim.log   # 完整网络 HLS C-sim 日志
│  ├─ synthesis_reports/      # 各版本 csynth.rpt / csim.log 原始报告（D0~D5）
│  └─ cosim_reports/D5/       # 最终候选 RTL Co-sim 报告
├─ model/                     # 模型数据（权重/黄金特征/10 样本，供复现）
├─ docs/
│  ├─ member_c_report.md      # 成员 C 基线报告（参照）
│  └─ interface_spec.md       # 统一接口说明（参照）
├─ README.md                  # 本文件
└─ member_d_report.md         # 成员 D 正式报告
```

## 环境与路径

- 工具：Vitis HLS 2022.2（Build 3670227）
- 器件：`xc7z020-clg400-1`；目标时钟 10 ns；FP32
- 路径建议使用英文，例如：`D:\lenet_project\member_d_pe_optimization`
- 模型数据已随本目录提供（`model/`），测试平台通过 `-argv <model_dir> --multi` 读取

## 复现步骤

在 **Vitis HLS 2022.2 命令提示符**中执行：

```bat
cd /d D:\lenet_project\member_d_pe_optimization

rem 1) 复现各版本 Conv2 实验（C-sim + 综合）
vitis_hls -f scripts\run_pe_sweep.tcl D0
vitis_hls -f scripts\run_pe_sweep.tcl D1
vitis_hls -f scripts\run_pe_sweep.tcl D2
vitis_hls -f scripts\run_pe_sweep.tcl D3
vitis_hls -f scripts\run_pe_sweep.tcl D4
vitis_hls -f scripts\run_pe_sweep.tcl D5

rem 2) 最终候选 RTL Co-sim（需先完成 D5 综合，约 9 分钟）
vitis_hls -f scripts\run_d5_cosim.tcl

rem 3) 完整网络 10 样本端到端 C-sim
vitis_hls -f scripts\run_full_pe_csim.tcl
```

> 说明：脚本内的 `model_dir` 默认指向提交目录下的 `model/`，无需额外配置。

## 结果速览（Conv2 模块级，同环境 2022.2 口径）

| 版本 | 改动 | Latency (cycles) | 加速比 | DSP | LUT | 时钟(ns) | C-sim |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| D0 | 同环境实测基线 | 1,240,076 | 1.00× | 5 | 8,372 | 8.280 | PASS |
| D1 | 仅 Pipeline | 254,749 | 4.87× | 5 | 16,190 | 10.200 | PASS |
| D2 | PE_MAC=5 | 243,101 | 5.10× | 7 | 13,444 | 10.200 | PASS |
| D3 | PE_OC=2 | 283,203 | 4.38× | 7 | 15,476 | 10.203 | PASS |
| D4 | PE_OC=4 | 267,203 | 4.64× | 7 | 17,637 | 9.394 | PASS |
| **D5** | PE_OC=4+缓存+II=32 | **15,415** | **80.44×** | **103** | **45,726** | **9.591** | **PASS** |

- 最终版本 RTL Co-sim：**PASS**，RTL 实测 19,815 cycles
- 完整网络 10/10 分类一致，最大 logits 绝对误差 ≤ 1e-2（实测 4.29e-3）
- 详细分析见 `member_d_report.md`

## 关键结论

1. 顶层为 AXI 接口时，直接加 PE 并行度（D1~D4）会被**总线端口带宽**卡住，全部停在 ~25 万 cycles（4.4~5.1×）；
2. 把数据先搬进片上数组（D5）后，流水线才真正成形（II=32），延迟降到 15,415 cycles（80.44×）；
3. `II` 是速度与资源的旋钮：II=32 是 xc7z020 上可接受的平衡点（详见报告 5.3 节）。
