# PS 侧调用流程（伪代码）

```c
// 1. 分配 feature/weight/bias/output 连续缓冲区并填充输入。
flush_dcache(feature_in, feature_bytes);
flush_dcache(weight, weight_bytes);
flush_dcache(bias, bias_bytes);
invalidate_dcache(feature_out, output_bytes);

// 2. 初始化 AXI-Lite 驱动（控制基址 0x40000000）。
XLenet_full_top ip;
XLenet_full_top_Initialize(&ip, device_id);

// 3. 写入 4 个 64 位 DDR 物理地址。
XLenet_full_top_Set_feature_in(&ip, phys(feature_in));
XLenet_full_top_Set_weight(&ip, phys(weight));
XLenet_full_top_Set_bias(&ip, phys(bias));
XLenet_full_top_Set_feature_out(&ip, phys(feature_out));

// 4. 可选择轮询或中断。本项目给出最小轮询流程。
XLenet_full_top_Start(&ip);
while (!XLenet_full_top_IsDone(&ip)) { /* timeout guard */ }

// 5. 使 CPU 看见由 PL 写回 DDR 的结果，然后读取分类输出。
invalidate_dcache(feature_out, output_bytes);
consume(feature_out);
```

注意：上述内容是与现有 HLS 驱动 API 对齐的集成流程，不是板上运行记录。板级 DDR 分配、缓存 API 名称和 device ID 需由成员 C 的软件平台最终确定。
