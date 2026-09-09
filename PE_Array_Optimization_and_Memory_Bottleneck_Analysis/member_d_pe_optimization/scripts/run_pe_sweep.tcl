# =====================================================================
# 成员 D 提交版：PE 阵列优化扫描脚本
# 对指定版本执行 lenet_conv2_top 的 C-sim + C 综合，并把原始报告
# 归档到 results/synthesis_reports/<config>/。
#
# 用法（在 Vitis HLS 2022.2 命令提示符，提交目录内）:
#   vitis_hls -f scripts/run_pe_sweep.tcl D0
#   vitis_hls -f scripts/run_pe_sweep.tcl D1
#   vitis_hls -f scripts/run_pe_sweep.tcl D2
#   vitis_hls -f scripts/run_pe_sweep.tcl D3
#   vitis_hls -f scripts/run_pe_sweep.tcl D4
#   vitis_hls -f scripts/run_pe_sweep.tcl D5
#
# 各配置:
#   D0 = 基线(无优化)     D1 = 仅 Pipeline II=1   D2 = PE_MAC=5
#   D3 = PE_OC=2+PE_MAC=5 D4 = PE_OC=4+PE_MAC=5
#   D5 = PE_OC=4+PE_MAC=5+局部缓存(II=32)
# =====================================================================

set config ""
foreach a $argv {
    if {[regexp {^D[0-5]$} $a]} {
        set config $a
        break
    }
}
if {$config eq ""} {
    puts "ERROR: usage: vitis_hls -f scripts/run_pe_sweep.tcl <D0|D1|D2|D3|D4|D5>"
    exit 1
}

set scripts_dir [file dirname [file normalize [info script]]]
set root_dir [file normalize "$scripts_dir/.."]
set model_dir [file normalize "$root_dir/model"]
set part_name "xc7z020clg400-1"
set clock_period_ns 10.0
set common_cflags "-std=c++11 -I$root_dir/include -I$root_dir/tb"

switch $config {
    "D0" { set src_file "$root_dir/src/archive/lenet_conv_D0.cpp" }
    "D1" { set src_file "$root_dir/src/archive/lenet_conv_D1.cpp" }
    "D2" { set src_file "$root_dir/src/archive/lenet_conv_D2.cpp" }
    "D3" { set src_file "$root_dir/src/archive/lenet_conv_D3.cpp" }
    "D4" { set src_file "$root_dir/src/archive/lenet_conv_D4.cpp" }
    "D5" { set src_file "$root_dir/src/lenet_conv_pe.cpp" }
    default {
        puts "ERROR: unknown config '$config'"
        exit 1
    }
}
if {![file exists $src_file]} {
    puts "ERROR: source file not found: $src_file"
    exit 1
}

set build_dir [file normalize "$root_dir/build_$config"]
set report_dir [file normalize "$root_dir/results/synthesis_reports/$config"]
file mkdir "$build_dir"
file mkdir "$report_dir"

puts "INFO: Sweep $config | src=$src_file"

cd $build_dir
open_project -reset "conv2_hls"
set_top lenet_conv2_top
add_files $src_file -cflags $common_cflags
add_files -tb "$root_dir/tb/tb_lenet_conv.cpp" -cflags "$common_cflags -DLENET_HLS_TOP_CONV2"
open_solution -reset "solution1"
set_part $part_name
create_clock -period $clock_period_ns -name default
csim_design -clean -argv $model_dir
csynth_design

file copy -force "$build_dir/conv2_hls/solution1/syn/report/lenet_conv2_top_csynth.rpt" "$report_dir/"
file copy -force "$build_dir/conv2_hls/solution1/syn/report/csynth.rpt" "$report_dir/"
file copy -force "$build_dir/conv2_hls/solution1/syn/report/csynth.xml" "$report_dir/"
file copy -force "$build_dir/conv2_hls/solution1/csim/report/lenet_conv2_top_csim.log" "$report_dir/"

puts "INFO: Sweep $config done. Reports archived to $report_dir"
close_project
cd $root_dir
exit
