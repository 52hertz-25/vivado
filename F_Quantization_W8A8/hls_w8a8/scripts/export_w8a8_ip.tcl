# ============================================================
# Export LeNet-5 W8A8 INT32 as a Vivado IP
# Vitis HLS 2022.2
# Target: XC7Z020-CLG400-1
# ============================================================

# Vitis HLS on Windows may include "-f" and the Tcl filename
# in argv. The project root is always the final argument.
if {$argc < 1} {
    puts "ERROR: project root argument is missing"
    puts "received argc=$argc"
    puts "received argv=$argv"
    exit 2
}

set root [file normalize [lindex $argv end]]

set work_dir    [file join $root work]
set project_dir [file join $work_dir w8a8_hls]
set export_dir  [file join $root export]
set ip_zip      [file join $export_dir lenet_w8a8_top_ip.zip]

puts "============================================================"
puts "LeNet-5 W8A8 INT32 IP export"
puts "Project root : $root"
puts "Project path : $project_dir"
puts "Export path  : $ip_zip"
puts "============================================================"

if {![file isdirectory $project_dir]} {
    puts "ERROR: synthesized HLS project was not found:"
    puts $project_dir
    puts "Run run_csynth.bat before exporting the IP."
    exit 2
}

file mkdir $export_dir
cd $work_dir

open_project w8a8_hls
open_solution solution1

config_export \
    -format ip_catalog \
    -rtl verilog \
    -vendor user.org \
    -library hls \
    -version 1.0 \
    -display_name "LeNet5 W8A8 INT32 Accelerator"

puts "Starting Vivado IP export..."

export_design \
    -format ip_catalog \
    -rtl verilog \
    -output $ip_zip

close_project

if {![file exists $ip_zip]} {
    puts "ERROR: IP ZIP was not generated:"
    puts $ip_zip
    exit 2
}

puts "============================================================"
puts "W8A8 IP export completed successfully"
puts "Generated IP:"
puts $ip_zip
puts "============================================================"

exit