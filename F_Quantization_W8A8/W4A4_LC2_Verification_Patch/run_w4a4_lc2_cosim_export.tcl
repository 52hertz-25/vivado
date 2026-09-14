# Representative C-sim, C synthesis, RTL co-sim and IP export for W4A4 LC2.
if {$argc < 4} {
    puts "ERROR: expected <hls_root> <model_root> <weight_root> <result_dir>"
    exit 2
}
set args [lrange $argv end-3 end]
set hls_root [file normalize [lindex $args 0]]
set model_root [file normalize [lindex $args 1]]
set weight_root [file normalize [lindex $args 2]]
set result_dir [file normalize [lindex $args 3]]
set source_file [file join $hls_root src lenet_w4a4_lc2.cpp]
set header_dir [file join $hls_root include]
set tb_file [file join $hls_root tb tb_lenet_w4a4.cpp]

foreach required [list \
    $source_file \
    [file join $header_dir lenet_w4a4.h] \
    $tb_file \
    [file join $model_root input_raw.txt] \
    [file join $weight_root conv1.weight.int4.txt]] {
    if {![file exists $required]} {
        puts "ERROR: required file not found: $required"
        exit 3
    }
}

file mkdir $result_dir
set work_dir [file join $hls_root work_level3_localcache2_verify]
file mkdir $work_dir
cd $work_dir
set project_name w4a4_lc2_cosim_hls
open_project -reset $project_name
set_top lenet_w4a4_top
add_files $source_file -cflags "-I$header_dir -std=c++11"
add_files -tb $tb_file -cflags "-I$header_dir -std=c++11"
open_solution -reset solution1 -flow_target vivado
set_part xc7z020clg400-1
create_clock -period 10.0 -name default
config_export -format ip_catalog -rtl verilog

puts "W4A4_LC2_REPRESENTATIVE_CSIM_START"
csim_design -argv [list $model_root $weight_root --multi]
puts "W4A4_LC2_REPRESENTATIVE_CSIM_PASS"

puts "W4A4_LC2_CSYNTH_START"
csynth_design
puts "W4A4_LC2_CSYNTH_PASS"

puts "W4A4_LC2_RTL_COSIM_START"
cosim_design -rtl verilog -tool xsim -trace_level none \
    -argv [list $model_root $weight_root]
puts "W4A4_LC2_RTL_COSIM_PASS"

set report_root [file join $work_dir $project_name solution1]
set csynth_rpt [file join $report_root syn report lenet_w4a4_top_csynth.rpt]
set cosim_rpt [file join $report_root sim report lenet_w4a4_top_cosim.rpt]
if {![file exists $csynth_rpt]} {
    puts "ERROR: C synthesis report missing: $csynth_rpt"
    exit 4
}
if {![file exists $cosim_rpt]} {
    puts "ERROR: RTL co-simulation report missing: $cosim_rpt"
    exit 5
}
file copy -force $csynth_rpt [file join $result_dir w4a4_lc2_csynth.rpt]
file copy -force $cosim_rpt [file join $result_dir w4a4_lc2_cosim.rpt]

set export_path [file join $result_dir lenet_w4a4_lc2_top_ip.zip]
export_design -format ip_catalog -rtl verilog -output $export_path
if {![file exists $export_path]} {
    puts "ERROR: exported IP missing: $export_path"
    exit 6
}
close_project
puts "W4A4_LC2_CSIM_CSYNTH_COSIM_EXPORT_ALL_PASS"
exit 0
