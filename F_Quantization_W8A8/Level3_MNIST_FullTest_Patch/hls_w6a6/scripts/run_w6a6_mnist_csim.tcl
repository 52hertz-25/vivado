# Vitis HLS 2022.2: W6A6 full MNIST C-simulation only.
if {$argc < 5} {
    puts "ERROR: expected <root> <dataset_root> <weight_root> <limit> <result_csv>"
    exit 2
}
set args [lrange $argv end-4 end]
set root [file normalize [lindex $args 0]]
set dataset_root [file normalize [lindex $args 1]]
set weight_root [file normalize [lindex $args 2]]
set limit [lindex $args 3]
set result_csv [file normalize [lindex $args 4]]

set source_file [file join $root src lenet_w6a6.cpp]
set header_dir [file join $root include]
set tb_file [file join $root tb tb_lenet_w6a6_mnist.cpp]
foreach required [list $source_file $tb_file] {
    if {![file exists $required]} {
        puts "ERROR: required file not found: $required"
        exit 2
    }
}
if {![file isdirectory $dataset_root] || ![file isdirectory $weight_root]} {
    puts "ERROR: dataset or weight directory not found"
    exit 2
}

file mkdir [file dirname $result_csv]
set work_dir [file join $root work]
file mkdir $work_dir
cd $work_dir

open_project -reset w6a6_mnist_hls
set_top lenet_w6a6_top
add_files $source_file -cflags "-I$header_dir -std=c++11"
add_files -tb $tb_file -cflags "-I$header_dir -std=c++11"
open_solution -reset solution1 -flow_target vivado
set_part xc7z020clg400-1
create_clock -period 10.0 -name default

puts "W6A6_MNIST_CSIM_START limit=$limit"
csim_design -argv [list $dataset_root $weight_root $limit $result_csv]
close_project
puts {W6A6_MNIST_CSIM_PASS}
exit 0
