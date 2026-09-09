# LeNet Zynq AXI 地址与寄存器表

## 系统地址段

| 主设备 | 从设备/地址块 | 基地址 | 范围 | 证据 |
|---|---|---:|---:|---|
| PS7 `M_AXI_GP0` | `lenet_full_top_0/s_axi_control/Reg` | `0x4000_0000` | 64 KiB | `lenet_system.bd` 中 `SEG_lenet_full_top_0_Reg` |
| HLS `m_axi_gmem0..3` | PS7 `S_AXI_HP0/HP0_DDR_LOWOCM` | `0x0000_0000` | 512 MiB | `lenet_system.bd` 四个 master segment |

## HLS 控制寄存器

所有地址均为相对 `0x4000_0000` 的偏移。64 位指针低 32 位在前，高 32 位在后。

| 偏移 | 名称 | 位宽 | 方向/说明 |
|---:|---|---:|---|
| `0x00` | `AP_CTRL` | 32 | bit0 `ap_start`; bit1 `ap_done`; bit2 `ap_idle`; bit3 `ap_ready`; bit7 `auto_restart`; bit9 `interrupt` |
| `0x04` | `GIE` | 32 | bit0 全局中断使能 |
| `0x08` | `IER` | 32 | bit0 完成中断；bit1 就绪中断 |
| `0x0C` | `ISR` | 32 | bit0 完成状态；bit1 就绪状态，写 1 翻转 |
| `0x10/0x14` | `feature_in` | 64 | 输入特征图 DDR 物理地址 |
| `0x1C/0x20` | `weight` | 64 | 权重 DDR 物理地址 |
| `0x28/0x2C` | `bias` | 64 | 偏置 DDR 物理地址 |
| `0x34/0x38` | `feature_out` | 64 | 输出 DDR 物理地址 |

权威工程内证据为归档驱动头文件 `xlenet_full_top_hw.h`，而不是手工猜测。
