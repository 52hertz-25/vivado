# Resume only the already-synthesized full-network solution and run RTL CoSim.
# Vivado HLS 2019.1 requires opening the project from its parent directory.

set root_dir [file dirname [file normalize [info script]]]
set model_dir [file normalize "$root_dir/../model"]

cd "$root_dir/build"
open_project "full_hls"
open_solution "solution1"
cosim_design -rtl verilog -argv $model_dir
close_project
exit
