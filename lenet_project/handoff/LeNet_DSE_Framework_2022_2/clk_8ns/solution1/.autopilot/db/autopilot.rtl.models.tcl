set SynModuleInfo {
  {SRCNAME lenet_full_top_Pipeline_OUTPUT_ROW_OUTPUT_COL MODELNAME lenet_full_top_Pipeline_OUTPUT_ROW_OUTPUT_COL RTLNAME lenet_full_top_lenet_full_top_Pipeline_OUTPUT_ROW_OUTPUT_COL
    SUBMODULES {
      {MODELNAME flow_control_loop_pipe_sequential_init RTLNAME lenet_full_top_flow_control_loop_pipe_sequential_init BINDTYPE interface TYPE internal_upc_flow_control INSTNAME lenet_full_top_flow_control_loop_pipe_sequential_init_U}
    }
  }
  {SRCNAME lenet_full_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL MODELNAME lenet_full_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL RTLNAME lenet_full_top_lenet_full_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL}
  {SRCNAME lenet_full_top_Pipeline_INPUT_CHANNEL MODELNAME lenet_full_top_Pipeline_INPUT_CHANNEL RTLNAME lenet_full_top_lenet_full_top_Pipeline_INPUT_CHANNEL}
  {SRCNAME lenet_full_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL1 MODELNAME lenet_full_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL1 RTLNAME lenet_full_top_lenet_full_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL1}
  {SRCNAME lenet_full_top_Pipeline_INPUT_CHANNEL2 MODELNAME lenet_full_top_Pipeline_INPUT_CHANNEL2 RTLNAME lenet_full_top_lenet_full_top_Pipeline_INPUT_CHANNEL2}
  {SRCNAME lenet_full_top_Pipeline_RELU_LOOP MODELNAME lenet_full_top_Pipeline_RELU_LOOP RTLNAME lenet_full_top_lenet_full_top_Pipeline_RELU_LOOP}
  {SRCNAME lenet_full_top_Pipeline_DENSE_INPUT MODELNAME lenet_full_top_Pipeline_DENSE_INPUT RTLNAME lenet_full_top_lenet_full_top_Pipeline_DENSE_INPUT}
  {SRCNAME lenet_full_top_Pipeline_RELU_LOOP3 MODELNAME lenet_full_top_Pipeline_RELU_LOOP3 RTLNAME lenet_full_top_lenet_full_top_Pipeline_RELU_LOOP3}
  {SRCNAME lenet_full_top_Pipeline_DENSE_INPUT4 MODELNAME lenet_full_top_Pipeline_DENSE_INPUT4 RTLNAME lenet_full_top_lenet_full_top_Pipeline_DENSE_INPUT4}
  {SRCNAME lenet_full_top MODELNAME lenet_full_top RTLNAME lenet_full_top IS_TOP 1
    SUBMODULES {
      {MODELNAME fadd_32ns_32ns_32_8_full_dsp_1 RTLNAME lenet_full_top_fadd_32ns_32ns_32_8_full_dsp_1 BINDTYPE op TYPE fadd IMPL fulldsp LATENCY 7 ALLOW_PRAGMA 1}
      {MODELNAME fmul_32ns_32ns_32_4_max_dsp_1 RTLNAME lenet_full_top_fmul_32ns_32ns_32_4_max_dsp_1 BINDTYPE op TYPE fmul IMPL maxdsp LATENCY 3 ALLOW_PRAGMA 1}
      {MODELNAME fcmp_32ns_32ns_1_2_no_dsp_1 RTLNAME lenet_full_top_fcmp_32ns_32ns_1_2_no_dsp_1 BINDTYPE op TYPE fcmp IMPL auto LATENCY 1 ALLOW_PRAGMA 1}
      {MODELNAME conv1_output_RAM_1WNR_AUTO_1R1W RTLNAME lenet_full_top_conv1_output_RAM_1WNR_AUTO_1R1W BINDTYPE storage TYPE ram_1wnr IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME pool1_output_RAM_1WNR_AUTO_1R1W RTLNAME lenet_full_top_pool1_output_RAM_1WNR_AUTO_1R1W BINDTYPE storage TYPE ram_1wnr IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME conv2_output_RAM_1WNR_AUTO_1R1W RTLNAME lenet_full_top_conv2_output_RAM_1WNR_AUTO_1R1W BINDTYPE storage TYPE ram_1wnr IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME pool2_output_RAM_1WNR_AUTO_1R1W RTLNAME lenet_full_top_pool2_output_RAM_1WNR_AUTO_1R1W BINDTYPE storage TYPE ram_1wnr IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME conv3_output_RAM_AUTO_1R1W RTLNAME lenet_full_top_conv3_output_RAM_AUTO_1R1W BINDTYPE storage TYPE ram IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME fc1_output_RAM_AUTO_1R1W RTLNAME lenet_full_top_fc1_output_RAM_AUTO_1R1W BINDTYPE storage TYPE ram IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME gmem0_m_axi RTLNAME lenet_full_top_gmem0_m_axi BINDTYPE interface TYPE adapter IMPL m_axi}
      {MODELNAME gmem1_m_axi RTLNAME lenet_full_top_gmem1_m_axi BINDTYPE interface TYPE adapter IMPL m_axi}
      {MODELNAME gmem2_m_axi RTLNAME lenet_full_top_gmem2_m_axi BINDTYPE interface TYPE adapter IMPL m_axi}
      {MODELNAME gmem3_m_axi RTLNAME lenet_full_top_gmem3_m_axi BINDTYPE interface TYPE adapter IMPL m_axi}
      {MODELNAME control_s_axi RTLNAME lenet_full_top_control_s_axi BINDTYPE interface TYPE interface_s_axilite}
    }
  }
}
