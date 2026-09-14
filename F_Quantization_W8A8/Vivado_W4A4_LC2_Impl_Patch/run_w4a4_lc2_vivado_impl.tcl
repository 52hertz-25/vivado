set script_dir [file normalize [file dirname [info script]]]
set ip_dir [file normalize [lindex $argv 0]]
set out_dir [file normalize "$script_dir/results"]
set proj_dir [file normalize "$script_dir/work_vivado_impl"]

if {![file isdirectory $ip_dir]} {
    puts "ERROR: Extracted IP directory not found: $ip_dir"
    exit 2
}

file mkdir $out_dir
create_project -force w4a4_lc2_impl $proj_dir -part xc7z020clg400-1

set rtl_files [glob -nocomplain "$ip_dir/hdl/verilog/*.v"]
if {[llength $rtl_files] == 0} {
    puts "ERROR: No Verilog files found under $ip_dir/hdl/verilog"
    exit 3
}

read_verilog $rtl_files
set xdc_file "$ip_dir/constraints/lenet_w4a4_top_ooc.xdc"
if {[file exists $xdc_file]} {
    read_xdc $xdc_file
} else {
    puts "WARNING: OOC XDC not found; creating 10 ns clock in Tcl."
}

synth_design -top lenet_w4a4_top -part xc7z020clg400-1 -mode out_of_context
if {[llength [get_clocks -quiet ap_clk]] == 0} {
    create_clock -name ap_clk -period 10.000 [get_ports ap_clk]
}
write_checkpoint -force "$out_dir/w4a4_lc2_post_synth.dcp"
report_utilization -file "$out_dir/post_synth_utilization.rpt"
report_timing_summary -delay_type max -max_paths 20 -file "$out_dir/post_synth_timing_summary.rpt"

opt_design
place_design
phys_opt_design
route_design

write_checkpoint -force "$out_dir/w4a4_lc2_post_route.dcp"
report_utilization -file "$out_dir/post_route_utilization.rpt"
report_timing_summary -delay_type max -max_paths 20 -report_unconstrained -file "$out_dir/post_route_timing_summary.rpt"
report_drc -file "$out_dir/post_route_drc.rpt"
report_methodology -file "$out_dir/post_route_methodology.rpt"

set route_status [get_property ROUTE_STATUS [current_design]]
set timing_paths [get_timing_paths -quiet -delay_type max -max_paths 1]
if {[llength $timing_paths] > 0} {
    set wns [get_property SLACK $timing_paths]
} else {
    set wns "NA"
}

set fp [open "$out_dir/implementation_summary.txt" w]
puts $fp "TOP=lenet_w4a4_top"
puts $fp "PART=xc7z020clg400-1"
puts $fp "TARGET_CLOCK_NS=10.000"
puts $fp "ROUTE_STATUS=$route_status"
puts $fp "WNS_NS=$wns"

set pass 1
if {![string match -nocase "*routed*" $route_status]} {
    set pass 0
}
if {$wns eq "NA" || $wns < 0.0} {
    set pass 0
}

if {$pass} {
    puts $fp "RESULT=PASS"
    close $fp
    puts "W4A4_LC2_VIVADO_IMPL_TIMING_PASS"
    exit 0
} else {
    puts $fp "RESULT=FAIL"
    close $fp
    puts "W4A4_LC2_VIVADO_IMPL_OR_TIMING_FAIL"
    exit 1
}
