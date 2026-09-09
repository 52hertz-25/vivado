D成员 PE_MAC=5 并行补丁

这份代码只做一项修改：把5x5卷积的25次乘加拆成5路并行部分和。
原来的网络结构、顶层接口、CHW/OIHW数据布局和FP32类型均未改变。

修改位置：
1. src/lenet_conv.cpp 中保留了原函数 mac_5x5。
2. 新增 mac_5x5_pe5，使用5个独立 partial 累加器。
3. conv5x5_valid 中的调用已切换到 mac_5x5_pe5。

你需要做的事情：
1. 先备份自己的原工程。
2. 对照本文件夹中的 src/lenet_conv.cpp 合并修改，不要覆盖已经改过的其他内容。
3. 先运行 C Simulation。只有 C-sim PASS 才继续。
4. 再运行 C Synthesis，记录 Latency、Interval、DSP、BRAM、LUT、FF 和 Estimated Clock。
5. 与未修改的D0基线比较，确认延迟是否下降、DSP是否增加。
6. 如果 C-sim 结果与基线略有差异，检查最终分类一致，并确认最大 logits 绝对误差不超过1e-2。

切回基线的方法：
把 conv5x5_valid 中的 mac_5x5_pe5 改回 mac_5x5 即可。

注意：
- 写了 UNROLL/PIPELINE 不代表一定获得5倍加速，最终以综合报告为准。
- 如果报告提示 memory port conflict，说明外部权重读取限制了并行度，应记录该现象，后续再考虑局部权重缓存。
- 这里没有覆盖你自己的工程，请始终保留最近一个能够 PASS 的版本。
