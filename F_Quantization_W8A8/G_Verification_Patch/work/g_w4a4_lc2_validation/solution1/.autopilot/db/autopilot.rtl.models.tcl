set SynModuleInfo {
  {SRCNAME lenet_w4a4_top_Pipeline_UNPACK_INPUT MODELNAME lenet_w4a4_top_Pipeline_UNPACK_INPUT RTLNAME lenet_w4a4_top_lenet_w4a4_top_Pipeline_UNPACK_INPUT
    SUBMODULES {
      {MODELNAME lenet_w4a4_top_flow_control_loop_pipe_sequential_init RTLNAME lenet_w4a4_top_flow_control_loop_pipe_sequential_init BINDTYPE interface TYPE internal_upc_flow_control INSTNAME lenet_w4a4_top_flow_control_loop_pipe_sequential_init_U}
    }
  }
  {SRCNAME lenet_w4a4_top_Pipeline_LOAD_LOCAL_WEIGHT MODELNAME lenet_w4a4_top_Pipeline_LOAD_LOCAL_WEIGHT RTLNAME lenet_w4a4_top_lenet_w4a4_top_Pipeline_LOAD_LOCAL_WEIGHT}
  {SRCNAME lenet_w4a4_top_Pipeline_OUT_ROW_OUT_COL MODELNAME lenet_w4a4_top_Pipeline_OUT_ROW_OUT_COL RTLNAME lenet_w4a4_top_lenet_w4a4_top_Pipeline_OUT_ROW_OUT_COL
    SUBMODULES {
      {MODELNAME lenet_w4a4_top_mul_4s_4s_8_1_1 RTLNAME lenet_w4a4_top_mul_4s_4s_8_1_1 BINDTYPE op TYPE mul IMPL auto LATENCY 0 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_mac_muladd_4s_4s_8s_9_4_1 RTLNAME lenet_w4a4_top_mac_muladd_4s_4s_8s_9_4_1 BINDTYPE op TYPE all IMPL dsp48 LATENCY 3 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_mac_muladd_4s_4s_9s_9_4_1 RTLNAME lenet_w4a4_top_mac_muladd_4s_4s_9s_9_4_1 BINDTYPE op TYPE all IMPL dsp48 LATENCY 3 ALLOW_PRAGMA 1}
    }
  }
  {SRCNAME lenet_w4a4_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL MODELNAME lenet_w4a4_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL RTLNAME lenet_w4a4_top_lenet_w4a4_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL
    SUBMODULES {
      {MODELNAME lenet_w4a4_top_mul_32ns_36ns_67_2_1 RTLNAME lenet_w4a4_top_mul_32ns_36ns_67_2_1 BINDTYPE op TYPE mul IMPL auto LATENCY 1 ALLOW_PRAGMA 1}
    }
  }
  {SRCNAME lenet_w4a4_top_Pipeline_LOAD_LOCAL_WEIGHT1 MODELNAME lenet_w4a4_top_Pipeline_LOAD_LOCAL_WEIGHT1 RTLNAME lenet_w4a4_top_lenet_w4a4_top_Pipeline_LOAD_LOCAL_WEIGHT1}
  {SRCNAME lenet_w4a4_top_Pipeline_VITIS_LOOP_147_1_KERNEL_ROW_KERNEL_COL MODELNAME lenet_w4a4_top_Pipeline_VITIS_LOOP_147_1_KERNEL_ROW_KERNEL_COL RTLNAME lenet_w4a4_top_lenet_w4a4_top_Pipeline_VITIS_LOOP_147_1_KERNEL_ROW_KERNEL_COL
    SUBMODULES {
      {MODELNAME lenet_w4a4_top_mux_21_4_1_1 RTLNAME lenet_w4a4_top_mux_21_4_1_1 BINDTYPE op TYPE mux IMPL auto LATENCY 0 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_mac_muladd_3ns_4s_15s_15_4_1 RTLNAME lenet_w4a4_top_mac_muladd_3ns_4s_15s_15_4_1 BINDTYPE op TYPE all IMPL dsp48 LATENCY 3 ALLOW_PRAGMA 1}
    }
  }
  {SRCNAME lenet_w4a4_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL2 MODELNAME lenet_w4a4_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL2 RTLNAME lenet_w4a4_top_lenet_w4a4_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL2
    SUBMODULES {
      {MODELNAME lenet_w4a4_top_mul_32ns_37ns_68_2_1 RTLNAME lenet_w4a4_top_mul_32ns_37ns_68_2_1 BINDTYPE op TYPE mul IMPL auto LATENCY 1 ALLOW_PRAGMA 1}
    }
  }
  {SRCNAME lenet_w4a4_top_Pipeline_LOAD_LOCAL_WEIGHT3 MODELNAME lenet_w4a4_top_Pipeline_LOAD_LOCAL_WEIGHT3 RTLNAME lenet_w4a4_top_lenet_w4a4_top_Pipeline_LOAD_LOCAL_WEIGHT3}
  {SRCNAME lenet_w4a4_top_Pipeline_VITIS_LOOP_147_1_KERNEL_ROW_KERNEL_COL4 MODELNAME lenet_w4a4_top_Pipeline_VITIS_LOOP_147_1_KERNEL_ROW_KERNEL_COL4 RTLNAME lenet_w4a4_top_lenet_w4a4_top_Pipeline_VITIS_LOOP_147_1_KERNEL_ROW_KERNEL_COL4
    SUBMODULES {
      {MODELNAME lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1 RTLNAME lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1 BINDTYPE op TYPE all IMPL dsp48 LATENCY 3 ALLOW_PRAGMA 1}
    }
  }
  {SRCNAME lenet_w4a4_top_Pipeline_REQUANT_VECTOR MODELNAME lenet_w4a4_top_Pipeline_REQUANT_VECTOR RTLNAME lenet_w4a4_top_lenet_w4a4_top_Pipeline_REQUANT_VECTOR}
  {SRCNAME lenet_w4a4_top_Pipeline_DENSE_OUTPUT_DENSE_INPUT MODELNAME lenet_w4a4_top_Pipeline_DENSE_OUTPUT_DENSE_INPUT RTLNAME lenet_w4a4_top_lenet_w4a4_top_Pipeline_DENSE_OUTPUT_DENSE_INPUT
    SUBMODULES {
      {MODELNAME lenet_w4a4_top_mac_muladd_3ns_4s_14s_14_4_1 RTLNAME lenet_w4a4_top_mac_muladd_3ns_4s_14s_14_4_1 BINDTYPE op TYPE all IMPL dsp48 LATENCY 3 ALLOW_PRAGMA 1}
    }
  }
  {SRCNAME lenet_w4a4_top_Pipeline_REQUANT_VECTOR5 MODELNAME lenet_w4a4_top_Pipeline_REQUANT_VECTOR5 RTLNAME lenet_w4a4_top_lenet_w4a4_top_Pipeline_REQUANT_VECTOR5
    SUBMODULES {
      {MODELNAME lenet_w4a4_top_mul_32ns_38ns_69_2_1 RTLNAME lenet_w4a4_top_mul_32ns_38ns_69_2_1 BINDTYPE op TYPE mul IMPL auto LATENCY 1 ALLOW_PRAGMA 1}
    }
  }
  {SRCNAME lenet_w4a4_top_Pipeline_DENSE_OUTPUT_DENSE_INPUT6 MODELNAME lenet_w4a4_top_Pipeline_DENSE_OUTPUT_DENSE_INPUT6 RTLNAME lenet_w4a4_top_lenet_w4a4_top_Pipeline_DENSE_OUTPUT_DENSE_INPUT6
    SUBMODULES {
      {MODELNAME lenet_w4a4_top_mac_muladd_4ns_7ns_7ns_10_4_1 RTLNAME lenet_w4a4_top_mac_muladd_4ns_7ns_7ns_10_4_1 BINDTYPE op TYPE all IMPL dsp48 LATENCY 3 ALLOW_PRAGMA 1}
    }
  }
  {SRCNAME lenet_w4a4_top_Pipeline_REQUANT_VECTOR7 MODELNAME lenet_w4a4_top_Pipeline_REQUANT_VECTOR7 RTLNAME lenet_w4a4_top_lenet_w4a4_top_Pipeline_REQUANT_VECTOR7}
  {SRCNAME lenet_w4a4_top_Pipeline_WRITE_LOGITS MODELNAME lenet_w4a4_top_Pipeline_WRITE_LOGITS RTLNAME lenet_w4a4_top_lenet_w4a4_top_Pipeline_WRITE_LOGITS}
  {SRCNAME lenet_w4a4_top MODELNAME lenet_w4a4_top RTLNAME lenet_w4a4_top IS_TOP 1
    SUBMODULES {
      {MODELNAME lenet_w4a4_top_mul_4ns_9ns_12_1_1 RTLNAME lenet_w4a4_top_mul_4ns_9ns_12_1_1 BINDTYPE op TYPE mul IMPL auto LATENCY 0 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_local_weight_V_RAM_AUTO_1R1W RTLNAME lenet_w4a4_top_local_weight_V_RAM_AUTO_1R1W BINDTYPE storage TYPE ram IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_local_weight_V_2_RAM_AUTO_1R1W RTLNAME lenet_w4a4_top_local_weight_V_2_RAM_AUTO_1R1W BINDTYPE storage TYPE ram IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_local_weight_V_4_RAM_AUTO_1R1W RTLNAME lenet_w4a4_top_local_weight_V_4_RAM_AUTO_1R1W BINDTYPE storage TYPE ram IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_input_V_RAM_1WNR_AUTO_1R1W RTLNAME lenet_w4a4_top_input_V_RAM_1WNR_AUTO_1R1W BINDTYPE storage TYPE ram_1wnr IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_conv1_acc_V_RAM_1WNR_AUTO_1R1W RTLNAME lenet_w4a4_top_conv1_acc_V_RAM_1WNR_AUTO_1R1W BINDTYPE storage TYPE ram_1wnr IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_pool1_V_RAM_AUTO_1R1W RTLNAME lenet_w4a4_top_pool1_V_RAM_AUTO_1R1W BINDTYPE storage TYPE ram IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_conv2_acc_V_RAM_1WNR_AUTO_1R1W RTLNAME lenet_w4a4_top_conv2_acc_V_RAM_1WNR_AUTO_1R1W BINDTYPE storage TYPE ram_1wnr IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_pool2_V_RAM_AUTO_1R1W RTLNAME lenet_w4a4_top_pool2_V_RAM_AUTO_1R1W BINDTYPE storage TYPE ram IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_conv3_acc_V_RAM_AUTO_1R1W RTLNAME lenet_w4a4_top_conv3_acc_V_RAM_AUTO_1R1W BINDTYPE storage TYPE ram IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_conv3_relu_V_RAM_AUTO_1R1W RTLNAME lenet_w4a4_top_conv3_relu_V_RAM_AUTO_1R1W BINDTYPE storage TYPE ram IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_fc1_acc_V_RAM_AUTO_1R1W RTLNAME lenet_w4a4_top_fc1_acc_V_RAM_AUTO_1R1W BINDTYPE storage TYPE ram IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_fc1_relu_V_RAM_AUTO_1R1W RTLNAME lenet_w4a4_top_fc1_relu_V_RAM_AUTO_1R1W BINDTYPE storage TYPE ram IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_fc2_acc_V_RAM_AUTO_1R1W RTLNAME lenet_w4a4_top_fc2_acc_V_RAM_AUTO_1R1W BINDTYPE storage TYPE ram IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_fc2_quant_V_RAM_AUTO_1R1W RTLNAME lenet_w4a4_top_fc2_quant_V_RAM_AUTO_1R1W BINDTYPE storage TYPE ram IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME lenet_w4a4_top_gmem0_m_axi RTLNAME lenet_w4a4_top_gmem0_m_axi BINDTYPE interface TYPE adapter IMPL m_axi}
      {MODELNAME lenet_w4a4_top_gmem1_m_axi RTLNAME lenet_w4a4_top_gmem1_m_axi BINDTYPE interface TYPE adapter IMPL m_axi}
      {MODELNAME lenet_w4a4_top_gmem2_m_axi RTLNAME lenet_w4a4_top_gmem2_m_axi BINDTYPE interface TYPE adapter IMPL m_axi}
      {MODELNAME lenet_w4a4_top_control_s_axi RTLNAME lenet_w4a4_top_control_s_axi BINDTYPE interface TYPE interface_s_axilite}
    }
  }
}
