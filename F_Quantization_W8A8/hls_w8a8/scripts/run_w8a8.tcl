# ============================================================
# LeNet-5 W8A8 INT32
# Vitis HLS 2022.2 unified run script
#
# Arguments:
#   project_root model_root weight_root mode
#
# Supported modes:
#   csim    : C simulation
#   csynth  : C synthesis
#   cosim   : RTL co-simulation
#   all     : C simulation + synthesis + RTL co-simulation
# ============================================================

# ------------------------------------------------------------
# 1. Read command-line arguments
# ------------------------------------------------------------

# On Windows, Vitis HLS 2022.2 may include "-f" and the Tcl
# filename in argv. Therefore, take the final four arguments.
if {$argc < 4} {
    puts "ERROR: expected <project_root> <model_root> <weight_root> <mode>"
    puts "Valid modes: csim | csynth | cosim | all"
    puts "received argc=$argc"
    puts "received argv=$argv"
    exit 2
}

set user_args [lrange $argv end-3 end]

set root        [file normalize [lindex $user_args 0]]
set model_root  [file normalize [lindex $user_args 1]]
set weight_root [file normalize [lindex $user_args 2]]
set mode        [lindex $user_args 3]

puts "============================================================"
puts "LeNet-5 W8A8 INT32 HLS"
puts "Project root : $root"
puts "Model root   : $model_root"
puts "Weight root  : $weight_root"
puts "Run mode     : $mode"
puts "============================================================"

# ------------------------------------------------------------
# 2. Validate mode
# ------------------------------------------------------------

if {$mode ne "csim" &&
    $mode ne "csynth" &&
    $mode ne "cosim" &&
    $mode ne "all"} {

    puts "ERROR: invalid mode: $mode"
    puts "Valid modes: csim, csynth, cosim, all"
    exit 2
}

# ------------------------------------------------------------
# 3. Prepare paths
# ------------------------------------------------------------

set source_file [file join $root src lenet_w8a8.cpp]
set header_dir  [file join $root include]
set tb_file     [file join $root tb tb_lenet_w8a8.cpp]
set work_dir    [file join $root work]

# ------------------------------------------------------------
# 4. Check required files and directories
# ------------------------------------------------------------

if {![file exists $source_file]} {
    puts "ERROR: source file not found:"
    puts $source_file
    exit 2
}

if {![file isdirectory $header_dir]} {
    puts "ERROR: include directory not found:"
    puts $header_dir
    exit 2
}

if {![file exists $tb_file]} {
    puts "ERROR: testbench file not found:"
    puts $tb_file
    exit 2
}

if {![file isdirectory $model_root]} {
    puts "ERROR: model directory not found:"
    puts $model_root
    exit 2
}

if {![file isdirectory $weight_root]} {
    puts "ERROR: weight directory not found:"
    puts $weight_root
    exit 2
}

# Verify the five W8A8 weight files.
set required_weights [list \
    "conv1.weight.int8.txt" \
    "conv2.weight.int8.txt" \
    "conv3.weight.int8.txt" \
    "fc1.weight.int8.txt" \
    "fc2.weight.int8.txt" \
]

foreach weight_file $required_weights {
    set full_weight_path [file join $weight_root $weight_file]

    if {![file exists $full_weight_path]} {
        puts "ERROR: weight file not found:"
        puts $full_weight_path
        exit 2
    }
}

# ------------------------------------------------------------
# 5. Create/open the HLS project
# ------------------------------------------------------------

# Use a relative project name because the Windows HLS
# open_project command rejects drive-letter absolute paths.
file mkdir $work_dir
cd $work_dir

set project_dir w8a8_hls

puts "Work directory: [pwd]"
puts "HLS project   : $project_dir"

open_project -reset $project_dir
set_top lenet_w8a8_top

# ------------------------------------------------------------
# 6. Add source and testbench
# ------------------------------------------------------------

add_files $source_file \
    -cflags "-I$header_dir -std=c++11"

add_files -tb $tb_file \
    -cflags "-I$header_dir -std=c++11"

# ------------------------------------------------------------
# 7. Configure the HLS solution
# ------------------------------------------------------------

open_solution -reset solution1 -flow_target vivado

set_part xc7z020clg400-1

create_clock -period 10.0 -name default

config_export -format ip_catalog -rtl verilog

# ------------------------------------------------------------
# 8. Run C simulation
# ------------------------------------------------------------

if {$mode eq "csim" || $mode eq "all"} {
    puts "============================================================"
    puts "Starting W8A8 C simulation"
    puts "Testing 10 representative MNIST samples"
    puts "============================================================"

    csim_design -argv [list $model_root $weight_root --multi]

    puts "============================================================"
    puts "W8A8 C simulation completed"
    puts "============================================================"
}

# ------------------------------------------------------------
# 9. Run C synthesis
# ------------------------------------------------------------

# RTL co-simulation requires synthesized RTL, so synthesis is
# also performed automatically in cosim mode.
if {$mode eq "csynth" ||
    $mode eq "cosim" ||
    $mode eq "all"} {

    puts "============================================================"
    puts "Starting W8A8 C synthesis"
    puts "============================================================"

    csynth_design

    puts "============================================================"
    puts "W8A8 C synthesis completed"
    puts "============================================================"
}

# ------------------------------------------------------------
# 10. Run RTL co-simulation
# ------------------------------------------------------------

if {$mode eq "cosim" || $mode eq "all"} {
    puts "============================================================"
    puts "Starting W8A8 RTL co-simulation"
    puts "RTL language : Verilog"
    puts "Simulator    : XSim"
    puts "Test scope   : one representative MNIST sample"
    puts "============================================================"

    # Do not pass --multi here. RTL simulation is much slower
    # than C simulation, so first verify one representative sample.
    cosim_design \
        -rtl verilog \
        -tool xsim \
        -trace_level port \
        -argv [list $model_root $weight_root]

    puts "============================================================"
    puts "W8A8 RTL co-simulation completed"
    puts "============================================================"
}

# ------------------------------------------------------------
# 11. Finish
# ------------------------------------------------------------

close_project

puts "============================================================"
puts "W8A8 HLS operation completed successfully"
puts "Mode: $mode"
puts "============================================================"

exit