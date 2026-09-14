// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.2 (64-bit)
// Tool Version Limit: 2019.12
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// ==============================================================
#ifndef __lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1__HH__
#define __lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1__HH__
#include "lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1_DSP48_3.h"

template<
    int ID,
    int NUM_STAGE,
    int din0_WIDTH,
    int din1_WIDTH,
    int din2_WIDTH,
    int dout_WIDTH>
SC_MODULE(lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1) {
    sc_core::sc_in_clk clk;
    sc_core::sc_in<sc_dt::sc_logic> reset;
    sc_core::sc_in<sc_dt::sc_logic> ce;
    sc_core::sc_in< sc_dt::sc_lv<din0_WIDTH> >   din0;
    sc_core::sc_in< sc_dt::sc_lv<din1_WIDTH> >   din1;
    sc_core::sc_in< sc_dt::sc_lv<din2_WIDTH> >   din2;
    sc_core::sc_out< sc_dt::sc_lv<dout_WIDTH> >   dout;



    lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1_DSP48_3 lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1_DSP48_3_U;

    SC_CTOR(lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1):  lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1_DSP48_3_U ("lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1_DSP48_3_U") {
        lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1_DSP48_3_U.clk(clk);
        lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1_DSP48_3_U.rst(reset);
        lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1_DSP48_3_U.ce(ce);
        lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1_DSP48_3_U.in0(din0);
        lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1_DSP48_3_U.in1(din1);
        lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1_DSP48_3_U.in2(din2);
        lenet_w4a4_top_mac_muladd_3ns_4s_16s_16_4_1_DSP48_3_U.dout(dout);

    }

};

#endif //
