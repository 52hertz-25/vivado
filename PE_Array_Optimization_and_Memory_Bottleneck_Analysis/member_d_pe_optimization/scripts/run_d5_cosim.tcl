# =====================================================================
# 成员 D 提交版：最终候选 D5 的 RTL Co-sim
# 用法：vitis_hls -f scripts/run_d5_cosim.tcl
# 前置：先运行 scripts/run_pe_sweep.tcl D5 生成 build_d5 工程
# =====================================================================
set scripts_dir [file dirname [file normalize [info script]]]
set root_dir [file normalize "$scripts_dir/.."]
set model_dir [file normalize "$root_dir/model"]
set report_dir [file normalize "$root_dir/results/cosim_reports/D5"]
file mkdir $report_dir

set build_dir [file normalize "$root_dir/build_d5"]
if {![file exists "$build_dir/conv2_hls/conv2_hls.xpr"] && ![file exists "$build_dir/conv2_hls/hls.app"]} {
    puts "ERROR: build_d5 project not found. Run 'vitis_hls -f scripts/run_pe_sweep.tcl D5' first."
    exit 1
}

cd $build_dir
open_project "conv2_hls"
open_solution "solution1"
cosim_design -argv $model_dir
file copy -force "$build_dir/conv2_hls/solution1/sim/report/lenet_conv2_top_cosim.rpt" "$report_dir/"
puts "INFO: D5 RTL co-sim done. Report archived to $report_dir"
close_project
cd $root_dir
exit
