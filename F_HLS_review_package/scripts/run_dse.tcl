if {$argc < 1} {
    puts "ERROR: usage: vitis_hls -f scripts/run_dse.tcl -tclargs <framework_root>"
    exit 2
}

set root [file normalize [file join [file dirname [info script]] ..]]
set part_name "xc7z020clg400-1"
source [file join $root configs configs.tcl]
file mkdir [file join $root work]

foreach cfg $dse_configs {
    if {![dict get $cfg enabled]} { continue }
    set id [dict get $cfg id]
    set project_dir $id
    set source_cpp [file join $root [dict get $cfg source_cpp]]
    set include_dir [file join $root include]
    set tb_cpp [file join $root tb tb_lenet_conv.cpp]
    set cflags "-I$include_dir -I[file join $root tb] [dict get $cfg cflags]"

    if {![file exists $source_cpp]} {
        puts "ERROR: $id source does not exist: $source_cpp"
        continue
    }

    puts "=== DSE START: $id ([dict get $cfg description]) ==="
    open_project -reset $project_dir
    set_top [dict get $cfg top_name]
    add_files $source_cpp -cflags $cflags
    add_files -tb $tb_cpp -cflags $cflags
    open_solution -reset solution1 -flow_target vivado
    set_part $part_name
    create_clock -period [dict get $cfg clock_ns] -name default
    config_export -format ip_catalog -rtl verilog

    set directive_file [file join $root [dict get $cfg directives]]
    if {[file exists $directive_file]} { source $directive_file }

    if {[dict get $cfg run_csim]} { csim_design -argv [list [file join $root model]] }
    csynth_design
    if {[dict get $cfg run_cosim]} { cosim_design -rtl verilog }
    if {[dict get $cfg export_ip]} { export_design -format ip_catalog -rtl verilog }
    close_project
    puts "=== DSE DONE: $id ==="
}

exit
