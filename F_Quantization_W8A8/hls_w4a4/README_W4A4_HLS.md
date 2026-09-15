# LeNet-5 W4A4–INT32 HLS（Vitis HLS 2022.2）

## 设计范围

该工程实现无偏置 LeNet-5：权重与激活均为有符号 4 位，卷积和全连接采用有符号 INT32 累加。外部输入和权重使用两个 INT4 数值打包到一个字节的真实紧凑格式；内部逐元素解包为 `ap_int<4>`。各层使用 Q40 定点乘数进行 round-to-nearest、ties-to-even 重量化，并饱和到 `[-7, 7]`。

与训练、校准和 HLS 数据生成一致的 Resize 全测试集证据位于
`../results/w4a4_preprocessing_ablation/resize/`：FP32 准确率 99.30%，W4A4
准确率 98.11%，下降 1.19 个百分点，预测一致率 98.53%，各层 INT32
溢出检查通过。该结果与本目录保存的 10,000 张 HLS C-simulation 混淆矩阵
完全一致。旧的 Pad(2) 软件结果 97.46% 保留在
`../results/w4a4_preprocessing_ablation/pad/`，仅作为预处理消融实验。

## 放置位置

把整个目录放到：

`D:\GitHub\vivado\vivado\F_Quantization_W8A8\hls_w4a4`

测试平台默认从以下现有目录读取 `input_raw.txt` 和 `benchmark_samples`：

`D:\GitHub\vivado\vivado\lenet_project\handoff\LeNet_DSE_Framework_2022_2\model`

## 运行顺序

在 **Vitis HLS 2022.2 Command Prompt** 中运行：

```bat
cd /d D:\GitHub\vivado\vivado\F_Quantization_W8A8\hls_w4a4
python scripts\verify_package.py
run_csim.bat
run_csynth.bat
run_cosim.bat
run_export.bat
```

每一步必须以退出码 0 结束。C-sim/Co-sim 还必须打印 `W4A4_CSIM_SUMMARY: PASS`；导出的 IP 位于 `export\lenet_w4a4_top_ip.zip`。

## 接口数据格式

- `feature_in`：512 字节，共 1024 个 INT4；偶数索引在低四位，奇数索引在高四位。
- `weight`：30735 字节，共 61470 个 INT4，层顺序为 conv1、conv2、conv3、fc1、fc2。
- `logits`：10 个 INT32 容器；每个容器的值已完成最终输出层重量化，合法范围为 `[-7,7]`。
- 四位负数使用二进制补码，例如 `-1 = 0xF`、`-7 = 0x9`。

## 证据边界

软件的 10000 张 MNIST 测试证明量化模型准确率；C-sim 和 RTL Co-sim 证明本 HLS 实现对代表性样本的功能一致性；C 综合报告证明时序估计和资源需求；Vivado 集成、实现、时序、DRC、bitstream 与 XSA 才能证明系统级工程交付。未在明确型号的实体开发板上运行前，不应宣称已经完成板级实测或商品量产验证。

## 文件说明

- `src/lenet_w4a4.cpp`：HLS 顶层与网络计算。
- `include/lenet_w4a4.h`：尺寸、类型、偏移及 Q40 常量。
- `tb/tb_lenet_w4a4.cpp`：输入量化与权重打包；C-sim 测试 11 次，较慢的 RTL Co-sim 测试 1 次。
- `model/int4_weights/`：INT4 文本权重及权重尺度。
- `scripts/run_w4a4.tcl`：统一 HLS 流程。
- `scripts/verify_package.py`：权重计数、范围、尺度常量和数据类型的独立静态检查。
- `evidence/`：来自 PyTorch 全测试集的结果与原始评估脚本。
