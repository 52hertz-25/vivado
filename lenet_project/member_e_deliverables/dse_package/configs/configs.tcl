# Structural DSE at the selected 10 ns clock
set dse_configs [list \
    [dict create id struct_baseline enabled 1 description "FP32 baseline at 10 ns" source_cpp "src/lenet_conv.cpp" top_name "lenet_full_top" clock_ns 10.0 cflags "" directives "directives/baseline.tcl" run_csim 1 run_cosim 0 export_ip 0] \
    [dict create id mac_unroll_2 enabled 1 description "MAC loop unroll factor 2" source_cpp "variants/mac_unroll_2/lenet_conv.cpp" top_name "lenet_full_top" clock_ns 10.0 cflags "" directives "directives/baseline.tcl" run_csim 1 run_cosim 0 export_ip 0] \
    [dict create id mac_unroll_5 enabled 1 description "MAC loop unroll factor 5" source_cpp "variants/mac_unroll_5/lenet_conv.cpp" top_name "lenet_full_top" clock_ns 10.0 cflags "" directives "directives/baseline.tcl" run_csim 1 run_cosim 0 export_ip 0] \
]
