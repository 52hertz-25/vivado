# Member E upgrade: validate the archived Zynq block design and regenerate
# implementation evidence from the existing routed checkpoint.
# Run with:
#   vivado -mode batch -source scripts/rerun_vivado_reports.tcl

set script_dir [file dirname [file normalize [info script]]]
set pkg_dir [file normalize [file join $script_dir ..]]
set lenet_root [file normalize [file join $pkg_dir .. .. ..]]
set xpr [file join $lenet_root vivado LeNet_Zynq_System LeNet_Zynq_System.xpr]
set out_dir [file join $pkg_dir reports rerun]
file mkdir $out_dir

puts "MEMBER_E_XPR=$xpr"
puts "MEMBER_E_OUT=$out_dir"
open_project $xpr
open_bd_design [get_files */lenet_system.bd]
validate_bd_design -force
save_bd_design
generate_target all [get_files */lenet_system.bd]
close_bd_design [current_bd_design]

open_run impl_1
report_route_status -file [file join $out_dir route_status.rpt]
report_timing_summary -delay_type min_max -report_unconstrained -check_timing_verbose -max_paths 10 -input_pins -file [file join $out_dir timing_summary.rpt]
report_utilization -hierarchical -file [file join $out_dir utilization_hierarchical.rpt]
report_power -file [file join $out_dir power.rpt]
write_hw_platform -fixed -force -file [file join $out_dir lenet_system_wrapper.xsa]
puts "MEMBER_E_VIVADO_RERUN_PASS"
close_project
exit
