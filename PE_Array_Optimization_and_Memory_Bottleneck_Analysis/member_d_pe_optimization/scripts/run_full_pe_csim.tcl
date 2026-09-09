# =====================================================================
# 成员 D 提交版：最终版本（lenet_conv_pe.cpp）完整网络
# 10 样本端到端 C-sim 验证
# 用法：vitis_hls -f scripts/run_full_pe_csim.tcl
# =====================================================================
set scripts_dir [file dirname [file normalize [info script]]]
set root_dir [file normalize "$scripts_dir/.."]
set model_dir [file normalize "$root_dir/model"]
set part_name "xc7z020clg400-1"
set clock_period_ns 10.0
set common_cflags "-std=c++11 -I$root_dir/include -I$root_dir/tb"

set build_dir [file normalize "$root_dir/build_full_pe"]
file mkdir $build_dir
cd $build_dir
open_project -reset "full_pe_hls"
set_top lenet_full_top
add_files "$root_dir/src/lenet_conv_pe.cpp" -cflags $common_cflags
add_files -tb "$root_dir/tb/tb_lenet_conv.cpp" -cflags "$common_cflags -DLENET_HLS_TOP_FULL"
open_solution -reset "solution1"
set_part $part_name
create_clock -period $clock_period_ns -name default
csim_design -clean -argv "$model_dir --multi"
file copy -force "$build_dir/full_pe_hls/solution1/csim/report/lenet_full_top_csim.log" "$root_dir/results/full_network_csim.log"
puts "INFO: Full-network PE csim done. Log archived to results/full_network_csim.log"
close_project
cd $root_dir
exit
