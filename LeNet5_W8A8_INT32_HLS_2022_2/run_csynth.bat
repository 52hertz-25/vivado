@echo off
setlocal
set "ROOT=%~dp0"
set "MODEL_ROOT=%ROOT%..\..\lenet_project\handoff\LeNet_DSE_Framework_2022_2\model"
set "WEIGHT_ROOT=%ROOT%model\int8_weights"

echo Running W8A8 C-synthesis...
vitis_hls -f "%ROOT%scripts\run_w8a8.tcl" -tclargs "%ROOT%" "%MODEL_ROOT%" "%WEIGHT_ROOT%" csynth
if errorlevel 1 (
    echo W8A8 C-synthesis FAILED.
    exit /b 1
)
echo W8A8 C-synthesis PASSED.
endlocal
