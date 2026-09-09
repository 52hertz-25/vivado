# LeNet-5 HLS 统一接口说明（模型 V2）

## 1. 顶层函数约定

六个顶层函数都使用相同的四参数形式：

```cpp
void top(
    const float feature_in[],
    const float weight[],
    const float bias[],
    float feature_out[]);
```

- `feature_in`：输入特征，FP32、CHW 行主序展平。
- `weight`：权重，FP32；卷积层按 OIHW 展平，全连接层按 `[out][in]` 展平。
- `bias`：偏置，FP32。成员 B 的模型为 `bias=False`，当前测试统一传入全零数组；保留该端口用于接口一致性。
- `feature_out`：输出特征，FP32。Conv1/2/3 与 FC1 输出均为激活前数值，FC2 输出为 10 个 logits。

所有数组元素均为 32 bit，即第 `i` 个元素相对基地址的字节偏移为 `4*i`。

## 2. 模块与数组深度

| 顶层函数 | `feature_in` | `weight` | `bias` | `feature_out` | 运算 |
| --- | ---: | ---: | ---: | ---: | --- |
| `lenet_conv1_top` | 1,024 | 150 | 6 | 4,704 | 1×32×32 → 6×28×28 |
| `lenet_conv2_top` | 1,176 | 2,400 | 16 | 1,600 | 6×14×14 → 16×10×10 |
| `lenet_conv3_top` | 400 | 48,000 | 120 | 120 | 16×5×5 → 120×1×1 |
| `lenet_fc1_top` | 120 | 10,080 | 84 | 84 | 120 → 84 |
| `lenet_fc2_top` | 84 | 840 | 10 | 10 | 84 → 10 |
| `lenet_full_top` | 1,024 | 61,470 | 236 | 10 | 完整 LeNet-5 推理 |

## 3. AXI 与控制接口

HLS 指令对所有顶层保持一致：

```cpp
#pragma HLS INTERFACE m_axi port=feature_in  offset=direct bundle=gmem0
#pragma HLS INTERFACE m_axi port=weight      offset=direct bundle=gmem1
#pragma HLS INTERFACE m_axi port=bias        offset=direct bundle=gmem2
#pragma HLS INTERFACE m_axi port=feature_out offset=direct bundle=gmem3
#pragma HLS INTERFACE ap_ctrl_hs port=return
```

- `gmem0`～`gmem3` 是四个独立 AXI4 Master 接口，允许输入、权重、偏置和输出分别连接存储空间。
- `offset=direct` 会把四个数组基地址作为顶层地址端口直接暴露。
- `ap_ctrl_hs` 生成 `ap_start`、`ap_done`、`ap_idle`、`ap_ready` 控制信号；生成 RTL 已核对包含这些端口。
- 启动时先设置四个基地址并保持有效，再将 `ap_start` 拉高；检测到 `ap_done=1` 后读取输出。复位为低有效 `ap_rst_n`。

## 4. 完整网络权重打包

`lenet_full_top` 的 `weight` 采用连续打包，顺序和偏移如下（偏移单位为 FP32 元素）：

| 分段 | 起始偏移 | 元素数 | 结束偏移（不含） |
| --- | ---: | ---: | ---: |
| Conv1 | 0 | 150 | 150 |
| Conv2 | 150 | 2,400 | 2,550 |
| Conv3 | 2,550 | 48,000 | 50,550 |
| FC1 | 50,550 | 10,080 | 60,630 |
| FC2 | 60,630 | 840 | 61,470 |

`bias` 也按 Conv1、Conv2、Conv3、FC1、FC2 顺序打包，起始偏移分别为 0、6、22、142、226，总计 236 个元素；当前全部填 0。

## 5. 完整推理顺序

```text
input normalization
  → Conv1 → ReLU → MaxPool 2×2
  → Conv2 → ReLU → MaxPool 2×2
  → Conv3 → ReLU
  → FC1   → ReLU
  → FC2 logits → argmax
```

输入预处理为 `(pixel / 255.0 - 0.1307) / 0.3081`。卷积均使用 5×5、stride=1、padding=0；池化均使用 2×2、stride=2。
