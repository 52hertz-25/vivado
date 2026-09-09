# 成员 E：位宽 × PE/Pipeline 联合 DSE

本目录对应升级计划 P1。器件、顶层、时钟、FP32 权重、输入预处理和 testbench 均固定，保证控制变量一致。

## 已实际执行

2026-09-09 使用 Vitis HLS 2022.2 对 D0、D1、D2、D3 四个 FP32 配置逐一执行：

1. CSim 数值验证；
2. C Synthesis；
3. 解析原始 `*_csynth.xml` / `*_csynth.rpt`；
4. 生成联合结果表、Pareto 标记和图。

四组均为 `execution_status=VALIDATED`、`csim=PASS`。完整运行日志归档于 `evidence/fresh_vitis_hls_run_20260909.txt`，各配置的 XML/RPT/CSim 日志归档于 `raw_reports/`。

## 当前范围

- D0-D3 均为成员 D 提供的 FP32 结构版本。
- 软件参考准确率为成员 B 的 MNIST FP32 99.30%；四个结构使用同一 golden feature map 做 CSim。
- INT8、INT6、INT4 仍缺成员 F 的可综合量化源码、scale/zero-point 和真实准确率，9 个配置保持 `BLOCKED_MISSING_F_QUANTIZED_SOURCE_SCALE_ACCURACY`，所有实验字段为空。

## 路径兼容说明

Vitis HLS 2022.2 在中文工程路径下无法创建 solution。本次实际运行使用 `E:\member_e_hls_tmp_20260909` 英文临时工作区，随后把 HLS work 复制回本目录（由 `.gitignore` 忽略），并将原始报告和日志归档为正式交付证据。

## 复现入口

```powershell
$env:PROCESSOR_ARCHITECTURE = "AMD64"
& 'E:\Xilinx\Vitis_HLS\2022.2\bin\vitis_hls.bat' -f 'scripts\run_joint_dse.tcl'
E:\anaconda\python.exe scripts\collect_joint_results.py
```

在中文路径下复现时，也应先复制到纯英文临时路径运行。
