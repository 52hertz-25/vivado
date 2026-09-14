@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "ROOT=%~dp0.."
set "HLS_ROOT=%ROOT%\hls_w4a4"
set "MODEL_ROOT=%HLS_ROOT%\..\..\lenet_project\handoff\LeNet_DSE_Framework_2022_2\model"
set "WEIGHT_ROOT=%HLS_ROOT%\model\int4_weights"
set "RESULT_DIR=%~dp0results\cosim_export"
echo Running W4A4 LC2 representative C-sim, C synthesis, RTL co-sim and IP export...
call vitis_hls -f run_w4a4_lc2_cosim_export.tcl -tclargs "%HLS_ROOT%" "%MODEL_ROOT%" "%WEIGHT_ROOT%" "%RESULT_DIR%" > w4a4_lc2_cosim_export.log 2>&1
if errorlevel 1 goto fail
findstr /c:"W4A4_LC2_CSIM_CSYNTH_COSIM_EXPORT_ALL_PASS" w4a4_lc2_cosim_export.log >nul || goto fail
echo RESULT_DIR=%RESULT_DIR%
echo W4A4_LC2_COSIM_EXPORT_PASS
exit /b 0
:fail
echo W4A4_LC2_COSIM_EXPORT_FAIL
exit /b 1
