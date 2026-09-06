# Vivado HLS 2019.1 flow for the complete LeNet-5 model-V2 baseline.
# Run in an ASCII path with: vivado_hls -f run_hls.tcl

set root_dir [file dirname [file normalize [info script]]]
set model_dir [file normalize "$root_dir/../model"]
set part_name "xc7z020clg400-1"
set clock_period_ns 10.0
set export_ip 0
set common_cflags "-std=c++11 -I$root_dir/include -I$root_dir/tb"

proc build_kernel {root_dir model_dir part_name clock_period_ns export_ip common_cflags kernel_name top_name tb_define run_cosim} {
    set build_dir [file normalize "$root_dir/build"]
    file mkdir $build_dir
    cd $build_dir

    open_project -reset "${kernel_name}_hls"
    set_top $top_name
    add_files "$root_dir/src/lenet_conv.cpp" -cflags $common_cflags
    set tb_cflags "$common_cflags -D${tb_define}"
    add_files -tb "$root_dir/tb/tb_lenet_conv.cpp" -cflags $tb_cflags

    open_solution -reset "solution1"
    set_part $part_name
    create_clock -period $clock_period_ns -name default

    csim_design -clean -argv $model_dir
    csynth_design
    if {$run_cosim} {
        cosim_design -rtl verilog -argv $model_dir
    } else {
        puts "INFO: Skipping RTL co-simulation for $top_name."
    }

    if {$export_ip} {
        export_design -rtl verilog -format ip_catalog
    } else {
        puts "INFO: Skipping IP packaging. Install AMD/Xilinx AR 76960 Y2K22 patch and set export_ip to 1 to enable it."
    }

    close_project
    cd $root_dir
}

build_kernel $root_dir $model_dir $part_name $clock_period_ns $export_ip $common_cflags \
    "conv1" "lenet_conv1_top" "LENET_HLS_TOP_CONV1" 1
build_kernel $root_dir $model_dir $part_name $clock_period_ns $export_ip $common_cflags \
    "conv2" "lenet_conv2_top" "LENET_HLS_TOP_CONV2" 1
build_kernel $root_dir $model_dir $part_name $clock_period_ns $export_ip $common_cflags \
    "conv3" "lenet_conv3_top" "LENET_HLS_TOP_CONV3" 1
build_kernel $root_dir $model_dir $part_name $clock_period_ns $export_ip $common_cflags \
    "fc1" "lenet_fc1_top" "LENET_HLS_TOP_FC1" 1
build_kernel $root_dir $model_dir $part_name $clock_period_ns $export_ip $common_cflags \
    "fc2" "lenet_fc2_top" "LENET_HLS_TOP_FC2" 1

# The full-network top is also RTL co-simulated for complete end-to-end proof.
build_kernel $root_dir $model_dir $part_name $clock_period_ns $export_ip $common_cflags \
    "full" "lenet_full_top" "LENET_HLS_TOP_FULL" 1

exit
