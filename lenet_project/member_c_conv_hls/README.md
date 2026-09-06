# 成员 C：完整 LeNet-5 Vivado HLS 2019.1 基线（模型 V2）

本目录是成员 C 的最终交付：在原 Conv1/Conv2 基础上补齐 Conv3、FC1、FC2，并提供完整网络顶层、统一接口、逐层/端到端验证、HLS 综合报告和生成 RTL。所有结果均由成员 B 的新权重重新计算，旧权重和旧实验结果未混入本版本。

## 完成内容

- 五个独立计算顶层：`lenet_conv1_top`、`lenet_conv2_top`、`lenet_conv3_top`、`lenet_fc1_top`、`lenet_fc2_top`。
- 完整推理顶层：`lenet_full_top`。
- 5×5 滑动窗口、卷积 MAC、ReLU、2×2 最大池化、全连接。
- 统一四数据端口：`feature_in`、`weight`、`bias`、`feature_out`。
- 统一 `ap_ctrl_hs` 控制协议，RTL 含 `ap_start`、`ap_done`、`ap_idle`、`ap_ready`。
- 新权重下的逐层隔离验证、逐层串联验证、单样本完整推理和 10 样本端到端回归。
- Vivado HLS 2019.1 下六个顶层的 C-sim、C synthesis 和 Verilog RTL Co-sim。

## 目录说明

最终压缩包解压后的顶层结构如下：

```text
成员C_LeNet5_HLS_模型V2_最终版/
├─ SHA256SUMS.txt                 # 包内文件完整性校验值
├─ 成员C添加任务.txt              # 本次新增任务原文
├─ model.py                       # 成员 B 提供的 LeNet-5 软件模型
├─ model/                         # 已规范化的模型 V2 数据，供测试平台直接读取
└─ member_c_conv_hls/             # 成员 C 的 HLS 工程源码与实验结果
```

### `model/`：新权重与软件参考数据

```text
model/
├─ hw_weights/
│  ├─ conv1.weight.txt            # 6×1×5×5，共 150 个 FP32 权重
│  ├─ conv2.weight.txt            # 16×6×5×5，共 2,400 个 FP32 权重
│  ├─ conv3.weight.txt            # 120×16×5×5，共 48,000 个 FP32 权重
│  ├─ fc1.weight.txt              # 84×120，共 10,080 个 FP32 权重
│  └─ fc2.weight.txt              # 10×84，共 840 个 FP32 权重
├─ hw_feature_maps/
│  ├─ conv1.npy / pool1.npy       # 第一卷积层及池化层黄金输出
│  ├─ conv2.npy / pool2.npy       # 第二卷积层及池化层黄金输出
│  └─ conv3.npy / fc1.npy / fc2.npy
│                                  # Conv3、FC1、FC2 激活前黄金输出
├─ benchmark_samples/
│  ├─ input_00_label_7.txt ... input_09_label_9.txt
│  │                                # 10 个 32×32 输入样本
│  ├─ output_00_label_7.txt ... output_09_label_9.txt
│  │                                # 对应的 10 维软件 logits
│  └─ README.txt                    # 多样本命名和格式说明
├─ input_raw.txt                    # 单图逐层验证输入
├─ final_output.txt                 # 单图最终软件 logits
├─ structure.txt                    # 网络层尺寸、参数量和激活配置
├─ WEIGHT_FORMAT_README.txt         # 权重展平顺序说明
├─ max_abs_stats.txt                # 各层权重最大绝对值
└─ baseline_summary.txt             # 成员 B 的训练/测试准确率记录
```

`model/` 共包含 61,470 个 FP32 权重、7 个逐层黄金特征图和 10 组端到端样本。特征图使用 CHW 展平；卷积权重使用 OIHW 展平；全连接权重使用 `[out][in]` 展平。模型为 `bias=False`，所以测试时向统一 `bias` 端口传入全零数组。

### `member_c_conv_hls/`：硬件实现与证据

```text
member_c_conv_hls/
├─ include/
│  └─ lenet_conv.h                  # FP32 类型、各层尺寸、权重偏移、六个顶层声明
├─ src/
│  └─ lenet_conv.cpp                # 窗口生成、MAC、ReLU、池化、Dense 和完整网络
├─ tb/
│  ├─ tb_lenet_conv.cpp             # 逐层隔离/串联、单样本、10 样本测试平台
│  └─ npy_reader.h                  # 读取成员 B 的 float32 NumPy 黄金特征图
├─ docs/
│  ├─ member_c_report.md            # 原理、误差、综合资源、延迟和最终结论
│  ├─ interface_spec.md             # AXI 深度、数据布局、权重偏移和控制时序
│  └─ 小组群提交说明.txt             # 可直接复制到小组群的提交说明
├─ results/
│  ├─ csim_results.txt              # 当前源码的完整本地 C++ 回归输出
│  └─ hls_2019_1/
│     ├─ performance_summary.md      # 便于阅读的六模块性能汇总
│     ├─ performance_summary.csv     # 便于后续制表/对比的结构化指标
│     ├─ vivado_hls_model_v2.log     # 六模块首次完整 HLS 流程日志
│     ├─ vivado_hls_full_cosim.log   # 完整顶层补充 RTL Co-sim 日志
│     └─ conv1/ conv2/ conv3/ fc1/ fc2/ full/
│        ├─ *_csim.log               # 当前模块 HLS C Simulation 输出
│        ├─ *_csynth.rpt             # 时钟、Latency、BRAM/DSP/FF/LUT 原始报告
│        ├─ *_cosim.rpt              # Verilog RTL Co-sim 状态与实测延迟
│        ├─ *.xml                    # HLS 机器可读综合结果
│        └─ verilog/                 # Co-sim 事务、延迟和仿真日志
├─ generated_rtl/
│  ├─ conv1/                         # lenet_conv1_top.v 及其依赖模块
│  ├─ conv2/                         # lenet_conv2_top.v 及其依赖模块
│  ├─ conv3/                         # lenet_conv3_top.v 及其依赖模块
│  ├─ fc1/                           # lenet_fc1_top.v 及其依赖模块
│  ├─ fc2/                           # lenet_fc2_top.v 及其依赖模块
│  └─ full/                          # lenet_full_top.v 及完整网络依赖模块
├─ run_csim.ps1                      # 使用 g++ 编译并执行全部软件侧回归
├─ run_hls.tcl                       # 重建六工程并依次执行 C-sim/综合/RTL Co-sim
├─ run_full_cosim.tcl                # 只重跑已综合完整顶层的 RTL Co-sim
└─ run_vivado_hls_2019_1.bat         # 检查 2019.1 环境并启动 run_hls.tcl
```

`generated_rtl/<模块>/` 中应整体使用该目录内的 Verilog 文件，不能只复制 `*_top.v`，因为顶层还会例化 AXI Master、浮点运算和内部计算子模块。查看实验结果时，优先阅读 `performance_summary.md`；需要核验原始证据时，再打开对应模块的 `*_csynth.rpt` 和 `*_cosim.rpt`。

## 复现实验

本地 C++ 回归：

```powershell
cd C:\Users\zhaofabuhuipang\Desktop\智能芯片\member_c_conv_hls
.\run_csim.ps1
```

Vivado HLS 2019.1 对中文路径支持不稳定，建议保持以下 ASCII 路径结构：

```text
D:\lenet_project\
├─ model\
└─ member_c_conv_hls\
```

在 **Vivado HLS 2019.1 Command Prompt** 中执行：

```bat
cd /d D:\lenet_project\member_c_conv_hls
run_vivado_hls_2019_1.bat
```

或者：

```bat
vivado_hls -f run_hls.tcl
```

脚本目标器件为 `xc7z020clg400-1`，时钟周期 10 ns。Vivado HLS 2019.1 在 2022 年以后可能触发 AR 76960（Y2K22 revision overflow），所以默认跳过 IP catalog 打包，但 C-sim、综合、RTL 生成和 RTL Co-sim 不受影响。安装官方补丁后，可将 `run_hls.tcl` 中的 `export_ip` 改为 `1`。

## 最终结论

- Conv1、Conv2、Conv3、FC1、FC2 和完整网络的 C-sim / C synthesis / Verilog RTL Co-sim：全部 PASS。
- 10 个端到端样本：10/10 分类一致，最大 logits 绝对误差 `4.29098681e-3`，低于 `1e-2` 门限。
- 完整网络 HLS 估计：5,472,207 cycles，100 MHz 下约 54.722 ms；RTL Co-sim 实测 5,679,805 cycles；37 BRAM_18K、27 DSP48E、6,762 FF、11,682 LUT。

完整数值见 `results/hls_2019_1/performance_summary.md`，接口见 `docs/interface_spec.md`。
