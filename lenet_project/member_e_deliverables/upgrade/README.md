# 成员 E 升级任务交付（陈正堃）

本目录对应 `E_plan/Member_E_Upgrade_Task_Plan.docx`，只覆盖成员 E 的联合 DSE、片上缓存候选和 Zynq AXI 集成工作。

## 实际执行状态

| 目录 | 工作 | 状态 |
|---|---|---|
| `joint_dse/` | FP32/INT8/INT6/INT4 × D0/D1/D2，并加入 D3 负对照 | 4 个 FP32 已完成本机 Vitis HLS CSim/综合；9 个量化配置等待成员 F 输入 |
| `memory_cache_candidate/` | D2 基线与本地 BRAM 权重缓存对照 | 两组均完成 HLS；缓存无性能收益，结论为停止采用 |
| `zynq_axi_integration/` | IP、BD、寄存器、驱动、实现报告和 XSA | 已实际运行 Vivado batch，BD 强制校验、报告与 XSA 导出成功 |
| `report/` | DOCX 与 PDF 正式报告 | 已按最新真实运行结果更新 |

## 关键结果

- 联合矩阵共 13 个稳定配置 ID；所有量化阻塞行保持空值，不填造数据。
- D2 延迟最低：243,101 cycles，10 ns 换算 2.43101 ms；LUT 13,444、FF 16,887、DSP 7，作为平衡推荐。
- D0 是最低资源备选。
- 缓存候选：243,353 cycles，比 D2 基线慢 0.1037%；LUT +780、FF -4,766、BRAM18K +10、DSP 不变，结论 `STOP_NO_PERFORMANCE_GAIN`。
- Vivado 本次复跑：26,721/26,721 条网络完成、0 路由错误，10 ns 下 WNS +0.415 ns、TNS 0；XSA 创建成功。

## 工具启动注意事项

当前自动化 shell 默认缺少 `PROCESSOR_ARCHITECTURE`，调用 Xilinx 启动器前必须设置：

```powershell
$env:PROCESSOR_ARCHITECTURE = "AMD64"
```

Vivado 可直接处理当前工程路径；Vitis HLS 2022.2 无法在中文路径创建 solution，因此本次在 `E:\member_e_hls_tmp_20260909` 英文临时目录实际运行，然后把原始报告复制回交付目录。

## 验证与复现

```powershell
E:\anaconda\python.exe joint_dse\scripts\collect_joint_results.py
E:\anaconda\python.exe memory_cache_candidate\scripts\collect_memory_cache_results.py
powershell.exe -ExecutionPolicy Bypass -File zynq_axi_integration\scripts\run_vivado_reports.ps1
E:\anaconda\python.exe zynq_axi_integration\scripts\build_axi_package.py
E:\anaconda\python.exe scripts\build_upgrade_report.py
E:\anaconda\python.exe scripts\validate_upgrade_deliverables.py
```

HLS 原始日志和 XML/RPT 均在各子目录的 `evidence/` 与 `raw_reports/` 中；Vivado 本次报告与 XSA 在 `zynq_axi_integration/reports/rerun/`。
