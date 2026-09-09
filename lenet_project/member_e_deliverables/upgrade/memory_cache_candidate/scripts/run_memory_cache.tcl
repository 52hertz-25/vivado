# Controlled comparison: D2 compute baseline vs D2 plus local Conv2 weight cache.

set root_dir [file normalize [file join [file dirname [info script]] ".."]]
set model_dir [file normalize [file join $root_dir "model"]]
set include_dir [file normalize [file join $root_dir "include"]]
set tb_dir [file normalize [file join $root_dir "tb"]]
set work_dir [file normalize [file join $root_dir "work"]]
file mkdir $work_dir

set common_cflags "-std=c++11 -I$include_dir -I$tb_dir"
set experiments {
    {d2_external_weight_baseline lenet_conv_D2_baseline.cpp}
    {d2_local_weight_cache lenet_conv_cache.cpp}
}

foreach experiment $experiments {
    lassign $experiment config_id source_name
    puts "MEMBER_E_CACHE_BEGIN $config_id"
    cd $work_dir
    open_project -reset $config_id
    set_top lenet_conv2_top
    add_files [file join $root_dir "src" $source_name] -cflags $common_cflags
    add_files -tb [file join $tb_dir "tb_lenet_conv.cpp"] \
        -cflags "$common_cflags -DLENET_HLS_TOP_CONV2"
    open_solution -reset "solution1"
    set_part "xc7z020clg400-1"
    create_clock -period 10.0 -name default
    if {[catch {csim_design -clean -argv $model_dir} csim_error]} {
        puts "MEMBER_E_CACHE_CSIM_FAIL $config_id $csim_error"
        close_project
        continue
    }
    puts "MEMBER_E_CACHE_CSIM_PASS $config_id"
    if {[catch {csynth_design} csynth_error]} {
        puts "MEMBER_E_CACHE_CSYNTH_FAIL $config_id $csynth_error"
    } else {
        puts "MEMBER_E_CACHE_CSYNTH_PASS $config_id"
    }
    close_project
}

cd $root_dir
exit
