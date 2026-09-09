# Block Design 连接说明

现有 `lenet_system.bd` 的关键数据通路如下：

- PS7 `M_AXI_GP0` → AXI Interconnect → `lenet_full_top_0/s_axi_control`，用于启动、状态和四个 DDR 指针寄存器。
- `lenet_full_top_0/m_axi_gmem0..3` → PS7 `S_AXI_HP0`，用于 feature、weight、bias、output 的高带宽 DDR 访问。
- PS7 `FCLK_CLK0` 驱动 HLS IP、GP0/HP0 及互连时钟。
- `proc_sys_reset_0` 生成互连与外设低有效复位，连接 HLS `ap_rst_n`。
- PS7 DDR 与 FIXED_IO 作为顶层外部接口。

`figures/block_design_connection_map.png` 是从上述 `.bd` 源文件重建的归档连接图，不冒充 Vivado GUI 截图。
