if {$argc < 5} { puts "ERROR: expected five arguments"; exit 2 }
set args [lrange $argv end-4 end]
set root [file normalize [lindex $args 0]]
set tag [lindex $args 1]
set top [lindex $args 2]
set source_name [lindex $args 3]
set project_name [lindex $args 4]
set source_file [file join $root src $source_name]
set include_dir [file join $root include]
set work_dir [file join $root work_level3_localcache2]
set report_dir [file join $root final_delivery reports level3_localcache2]
if {![file exists $source_file]} { puts "ERROR: source not found: $source_file"; exit 3 }
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
set rpt [file join $work_dir $project_name solution1 syn report ${top}_csynth.rpt]
set xml [file join $work_dir $project_name solution1 syn report ${top}_csynth.xml]
if {![file exists $rpt]} { puts "ERROR: synthesis report missing"; exit 4 }
file copy -force $rpt [file join $report_dir ${top}_lc2_csynth.rpt]
if {[file exists $xml]} { file copy -force $xml [file join $report_dir ${top}_lc2_csynth.xml] }
close_project
puts "LOCALCACHE2_SYNTH_PASS tag=$tag"
exit 0
