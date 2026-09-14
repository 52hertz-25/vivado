# Vitis HLS 2022.2 C simulation for the W4A4 local-weight-cache source.
if {$argc < 3} {
    puts "ERROR: expected <F_Quantization_W8A8_root> <limit> <result_csv>"
    exit 2
}
set args [lrange $argv end-2 end]
set root [file normalize [lindex $args 0]]
set limit [lindex $args 1]
set result_csv [file normalize [lindex $args 2]]
set hls_root [file join $root hls_w4a4]
set source_file [file join $hls_root src lenet_w4a4_lc2.cpp]
set header_dir [file join $hls_root include]
set tb_file [file join $hls_root tb tb_lenet_w4a4_mnist.cpp]
set dataset_root [file join $root hls_w8a8 data mnist_w8a8]
set weight_root [file join $hls_root model int4_weights]

foreach required [list \
    $source_file \
    $tb_file \
    [file join $dataset_root mnist_test_32x32.bin] \
    [file join $dataset_root mnist_test_labels.bin] \
    [file join $weight_root conv1.weight.int4.txt]] {
    if {![file exists $required]} {
        puts "ERROR: required file not found: $required"
        exit 3
    }
}

file mkdir [file dirname $result_csv]
set work_dir [file join $hls_root work_level3_localcache2_verify]
file mkdir $work_dir
cd $work_dir
open_project -reset w4a4_lc2_mnist_${limit}_hls
set_top lenet_w4a4_top
add_files $source_file -cflags "-I$header_dir -std=c++11"
add_files -tb $tb_file -cflags "-I$header_dir -std=c++11"
open_solution -reset solution1 -flow_target vivado
set_part xc7z020clg400-1
create_clock -period 10.0 -name default
puts "W4A4_LC2_MNIST_CSIM_START limit=$limit"
csim_design -argv [list $dataset_root $weight_root $limit $result_csv]
close_project
puts "W4A4_LC2_MNIST_CSIM_PASS limit=$limit"
exit 0
