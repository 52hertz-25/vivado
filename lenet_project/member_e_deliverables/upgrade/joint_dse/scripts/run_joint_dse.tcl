# Member E joint DSE runner for the stable FP32 D0-D3 variants supplied by D.
# Quantized rows remain blocked until F supplies source, scales and accuracy.

set root_dir [file normalize [file join [file dirname [info script]] ".."]]
set model_dir [file normalize [file join $root_dir "model"]]
set include_dir [file normalize [file join $root_dir "include"]]
set tb_dir [file normalize [file join $root_dir "tb"]]
set work_dir [file normalize [file join $root_dir "work"]]
file mkdir $work_dir

set part_name "xc7z020clg400-1"
set clock_period_ns 10.0
set common_cflags "-std=c++11 -I$include_dir -I$tb_dir"

set experiments {
    {fp32_d0_no_pipeline_10ns lenet_conv_D0.cpp}
    {fp32_d1_pipeline_10ns lenet_conv_D1.cpp}
    {fp32_d2_pe5_pipeline_10ns lenet_conv_D2.cpp}
    {fp32_d3_pe5_oc2_pipeline_10ns lenet_conv_D3.cpp}
}

foreach experiment $experiments {
    lassign $experiment config_id source_name
    puts "MEMBER_E_BEGIN $config_id"
    cd $work_dir
    open_project -reset $config_id
    set_top lenet_conv2_top
    add_files [file join $root_dir "src" $source_name] -cflags $common_cflags
    add_files -tb [file join $tb_dir "tb_lenet_conv.cpp"] \
        -cflags "$common_cflags -DLENET_HLS_TOP_CONV2"
    open_solution -reset "solution1"
    set_part $part_name
    create_clock -period $clock_period_ns -name default

    set csim_ok 1
    if {[catch {csim_design -clean -argv $model_dir} csim_error]} {
        set csim_ok 0
        puts "MEMBER_E_CSIM_FAIL $config_id $csim_error"
    }
    if {$csim_ok} {
        puts "MEMBER_E_CSIM_PASS $config_id"
        if {[catch {csynth_design} csynth_error]} {
            puts "MEMBER_E_CSYNTH_FAIL $config_id $csynth_error"
        } else {
            puts "MEMBER_E_CSYNTH_PASS $config_id"
        }
    } else {
        puts "MEMBER_E_SKIP_CSYNTH $config_id"
    }
    close_project
}

cd $root_dir
exit
