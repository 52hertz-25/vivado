if {$argc < 4} {
    puts "ERROR: expected <project_root> <model_root> <weight_root> <mode>"
    puts "mode: csim | csynth | all"
    exit 2
}

set root [file normalize [lindex $argv 0]]
set model_root [file normalize [lindex $argv 1]]
set weight_root [file normalize [lindex $argv 2]]
set mode [lindex $argv 3]
set project_dir [file join $root work w8a8_hls]

open_project -reset $project_dir
set_top lenet_w8a8_top
add_files [file join $root src lenet_w8a8.cpp] \
    -cflags "-I[file join $root include] -std=c++11"
add_files -tb [file join $root tb tb_lenet_w8a8.cpp] \
    -cflags "-I[file join $root include] -std=c++11"

open_solution -reset solution1 -flow_target vivado
set_part xc7z020clg400-1
create_clock -period 10.0 -name default
config_export -format ip_catalog -rtl verilog

if {$mode eq "csim" || $mode eq "all"} {
    csim_design -argv [list $model_root $weight_root --multi]
}
if {$mode eq "csynth" || $mode eq "all"} {
    csynth_design
}
if {$mode ne "csim" && $mode ne "csynth" && $mode ne "all"} {
    puts "ERROR: invalid mode $mode"
    close_project
    exit 2
}

close_project
exit
