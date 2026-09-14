if {$argc < 2} { puts "ERROR: expected <dcp_path> <results_root>"; exit 2 }
set args [lrange $argv end-1 end]
set dcp [file normalize [lindex $args 0]]
set results [file normalize [lindex $args 1]]
if {![file exists $dcp]} { puts "ERROR: DCP not found: $dcp"; exit 2 }
file mkdir $results
open_checkpoint $dcp
report_route_status -file [file join $results postroute_route_status.rpt]
report_timing_summary -delay_type min_max -report_unconstrained -check_timing_verbose \
    -max_paths 20 -file [file join $results postroute_timing_summary.rpt]
report_utilization -hierarchical -file [file join $results postroute_utilization.rpt]
report_drc -ruledeck default -file [file join $results postroute_drc.rpt]

set route_status [get_property ROUTE_STATUS [current_design]]
set paths [get_timing_paths -delay_type max -max_paths 1 -nworst 1]
if {[llength $paths] == 0} { puts "ERROR: no setup timing path"; exit 3 }
set wns [get_property SLACK [lindex $paths 0]]
set tns 0.0
set bad [get_timing_paths -delay_type max -slack_lesser_than 0.0 -max_paths 100000]
foreach p $bad { set tns [expr {$tns + [get_property SLACK $p]}] }
set drc_critical [get_drc_violations -quiet -filter {SEVERITY == "Critical Warning" || SEVERITY == "Error"}]

set f [open [file join $results g_vivado_metrics.txt] w]
puts $f "DCP=$dcp"; puts $f "ROUTE_STATUS=$route_status"; puts $f "WNS_NS=$wns"
puts $f "TNS_NS=$tns"; puts $f "DRC_CRITICAL_COUNT=[llength $drc_critical]"; close $f
puts "ROUTE_STATUS=$route_status"
puts "WNS_NS=$wns"
puts "TNS_NS=$tns"
puts "DRC_CRITICAL_COUNT=[llength $drc_critical]"
if {$route_status ne "Fully Routed"} { puts "ERROR: design is not Fully Routed"; exit 4 }
if {$wns < 0.0} { puts "ERROR: setup timing failed"; exit 5 }
if {[llength $drc_critical] != 0} { puts "ERROR: critical DRC violations exist"; exit 6 }
puts "G_VIVADO_POST_ROUTE_PASS"
close_design
exit 0

