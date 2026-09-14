# Vitis HLS 2022.2 runner. The last four argv items are used because some
# Windows launchers retain "-f script.tcl" in Tcl's argv list.
if {$argc < 4} {
    puts "ERROR: expected <project_root> <model_root> <weight_root> <mode>"
    puts "mode: csim | csynth | cosim | export | all"
    puts "received argc=$argc argv=$argv"
    exit 2
}

set args [lrange $argv end-3 end]
set root [file normalize [lindex $args 0]]
set model_root [file normalize [lindex $args 1]]
set weight_root [file normalize [lindex $args 2]]
set mode [string tolower [lindex $args 3]]

if {$mode ni {csim csynth cosim export all}} {
    puts "ERROR: invalid mode '$mode'"
    exit 2
}

foreach required [list \
    [file join $root src lenet_w4a4.cpp] \
    [file join $root include lenet_w4a4.h] \
    [file join $root tb tb_lenet_w4a4.cpp] \
    [file join $model_root input_raw.txt] \
    [file join $weight_root conv1.weight.int4.txt]] {
    if {![file exists $required]} {
        puts "ERROR: missing required file: $required"
        exit 2
    }
}

puts "============================================================"
puts "LeNet-5 W4A4 INT32 HLS"
puts "Project root : $root"
puts "Model root   : $model_root"
puts "Weight root  : $weight_root"
puts "Run mode     : $mode"
puts "============================================================"

set original_dir [pwd]
set work_dir [file join $root work]
file mkdir $work_dir
cd $work_dir
open_project -reset w4a4_hls
set_top lenet_w4a4_top
add_files [file join $root src lenet_w4a4.cpp] \
    -cflags "-I[file join $root include] -std=c++11"
add_files -tb [file join $root tb tb_lenet_w4a4.cpp] \
    -cflags "-I[file join $root include] -std=c++11"

open_solution -reset solution1 -flow_target vivado
set_part xc7z020clg400-1
create_clock -period 10.0 -name default
config_export -format ip_catalog -rtl verilog
set test_args [list $model_root $weight_root --multi]
set single_test_args [list $model_root $weight_root]

if {$mode eq "csim" || $mode eq "all"} {
    csim_design -argv $test_args
}
if {$mode in {csynth cosim export all}} {
    csynth_design
}
if {$mode eq "cosim" || $mode eq "all"} {
    # RTL simulation is much slower; one representative sample is sufficient
    # here because C-sim already exercises the full representative set.
    cosim_design -rtl verilog -tool xsim -trace_level port -argv $single_test_args
}
if {$mode eq "export" || $mode eq "all"} {
    file mkdir [file join $root export]
    export_design -format ip_catalog -rtl verilog \
        -output [file join $root export lenet_w4a4_top_ip.zip]
}

close_project
cd $original_dir
puts "W4A4_${mode}_PASS"
exit
