# LeNet-5 W8A8–INT32 Vitis HLS工程

## 环境

- Windows 10
- Vitis HLS 2022.2
- FPGA：XC7Z020CLG400-1

## 算法

- 输入激活：INT8，对称量化范围 `[-127,127]`
- 权重：INT8，按层对称量化
- MAC累加器：INT32
- 层间重量化：Q40整数乘法，使用“就近取整，正好一半时取偶数”
- ReLU后钳位到 `[0,127]`
- 最大池化直接在INT8激活上执行
- 最终输出：10个INT32 logits
- 模型无偏置，与原FP32/HLS基准一致

## 目录位置

将本压缩包内容解压并覆盖到：

`D:\GitHub\vivado\vivado\F_Quantization_W8A8\hls_w8a8`

## 运行

请使用“Vitis HLS 2022.2 Command Prompt”。

先执行：

`cd /d D:\GitHub\vivado\vivado\F_Quantization_W8A8\hls_w8a8`

再执行C仿真：

`run_csim.bat`

C仿真通过后执行综合：

`run_csynth.bat`

## 结果位置

- C-sim日志：命令窗口及 `vitis_hls.log`
- 综合报告：`work\w8a8_hls\solution1\syn\report\lenet_w8a8_top_csynth.rpt`

## 与Python实现的对应关系

Python软件模型每层先执行INT32卷积/全连接，再乘以输入激活scale和权重scale，随后除以下一层激活scale并重新量化。本工程将这个比例固化为Q40整数乘数，避免在硬件数据通路中使用浮点运算。

第一轮验收使用原工程的10个标准MNIST样本。全部预测标签一致时，C-sim输出`PASS`。这属于代表性样本验证，不等同于对10000张MNIST全部执行RTL仿真。
