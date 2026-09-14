if {$argc < 5} {
    puts "ERROR: expected <project_root> <tag> <top> <source> <project_name>"
    exit 2
}
set args [lrange $argv end-4 end]
set root [file normalize [lindex $args 0]]
set tag [lindex $args 1]
set top [lindex $args 2]
set source_name [lindex $args 3]
set project_name [lindex $args 4]
set source_file [file join $root src $source_name]
set include_dir [file join $root include]
set work_dir [file join $root work_level3_ic2]
set report_dir [file join $root final_delivery reports level3_ic2]

if {![file exists $source_file]} {
    puts "ERROR: source not found: $source_file"
    exit 3
}

file mkdir $work_dir
file mkdir $report_dir
cd $work_dir
open_project -reset $project_name
set_top $top
add_files $source_file -cflags "-I$include_dir -std=c++11"
open_solution -reset solution1 -flow_target vivado
set_part xc7z020clg400-1
create_clock -period 10.0 -name default
config_export -format ip_catalog -rtl verilog
csynth_design

set generated_report [file join $work_dir $project_name solution1 syn report ${top}_csynth.rpt]
set generated_xml [file join $work_dir $project_name solution1 syn report ${top}_csynth.xml]
if {![file exists $generated_report]} {
    puts "ERROR: synthesis report not found: $generated_report"
    exit 4
}
file copy -force $generated_report [file join $report_dir ${top}_ic2_csynth.rpt]
if {[file exists $generated_xml]} {
    file copy -force $generated_xml [file join $report_dir ${top}_ic2_csynth.xml]
}
close_project
puts "LEVEL3_IC2_SYNTH_PASS tag=$tag report=[file join $report_dir ${top}_ic2_csynth.rpt]"
exit 0
