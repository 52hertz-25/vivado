if {$argc < 4} {
    puts "ERROR: expected <hls_root> <dataset_root> <weight_root> <results_root>"
    exit 2
}
set args [lrange $argv end-3 end]
set hls_root [file normalize [lindex $args 0]]
set dataset_root [file normalize [lindex $args 1]]
set weight_root [file normalize [lindex $args 2]]
set results_root [file normalize [lindex $args 3]]
set patch_root [file dirname [file normalize [info script]]]
file mkdir $results_root

foreach required [list \
  [file join $hls_root src lenet_w4a4_lc2.cpp] \
  [file join $hls_root include lenet_w4a4.h] \
  [file join $patch_root tb_g_balanced20.cpp] \
  [file join $dataset_root mnist_test_32x32.bin] \
  [file join $dataset_root mnist_test_labels.bin] \
  [file join $weight_root conv1.weight.int4.txt]] {
    if {![file exists $required]} { puts "ERROR: missing $required"; exit 2 }
}

set work_root [file join $patch_root work]
file mkdir $work_root
cd $work_root
open_project -reset g_w4a4_lc2_validation
set_top lenet_w4a4_top
add_files [file join $hls_root src lenet_w4a4_lc2.cpp] -cflags "-I[file join $hls_root include] -std=c++11"
add_files -tb [file join $patch_root tb_g_balanced20.cpp] -cflags "-I[file join $hls_root include] -std=c++11"
open_solution -reset solution1 -flow_target vivado
set_part xc7z020clg400-1
create_clock -period 10.0 -name default
config_export -format ip_catalog -rtl verilog

set csim_csv [file join $results_root g_balanced20_csim.csv]
set cosim_csv [file join $results_root g_balanced20_cosim.csv]
csim_design -argv [list $dataset_root $weight_root $csim_csv]
if {![file exists $csim_csv]} { puts "ERROR: C-sim CSV missing"; exit 3 }
puts "G_CSIM_PASS"

csynth_design
cosim_design -rtl verilog -tool xsim -trace_level none \
    -argv [list $dataset_root $weight_root $cosim_csv]
if {![file exists $cosim_csv]} { puts "ERROR: Co-sim CSV missing"; exit 4 }

set a [open $csim_csv r]; set csim_text [read $a]; close $a
set b [open $cosim_csv r]; set cosim_text [read $b]; close $b
if {$csim_text ne $cosim_text} {
    puts "ERROR: C-sim and RTL Co-sim CSV files differ"
    exit 5
}
puts "G_COSIM_PASS"
close_project
exit 0

