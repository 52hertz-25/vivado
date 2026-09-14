@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "ROOT=%~dp0.."

echo [1/5] Preparing IC2 source variants...
python prepare_inchannel2_variants.py > prepare_ic2.log 2>&1
if errorlevel 1 goto :fail

echo [2/5] Synthesizing W8A8 IC2...
call vitis_hls -f run_inchannel2_csynth.tcl -tclargs "%ROOT%\hls_w8a8" "w8a8" "lenet_w8a8_top" "lenet_w8a8_ic2.cpp" "w8a8_ic2_hls" > w8a8_IC2_csynth.log 2>&1
if errorlevel 1 goto :fail
findstr /c:"LEVEL3_IC2_SYNTH_PASS" w8a8_IC2_csynth.log >nul
if errorlevel 1 goto :fail

echo [3/5] Synthesizing W6A6 IC2...
call vitis_hls -f run_inchannel2_csynth.tcl -tclargs "%ROOT%\hls_w6a6" "w6a6" "lenet_w6a6_top" "lenet_w6a6_ic2.cpp" "w6a6_ic2_hls" > w6a6_IC2_csynth.log 2>&1
if errorlevel 1 goto :fail
findstr /c:"LEVEL3_IC2_SYNTH_PASS" w6a6_IC2_csynth.log >nul
if errorlevel 1 goto :fail

echo [4/5] Synthesizing W4A4 IC2...
call vitis_hls -f run_inchannel2_csynth.tcl -tclargs "%ROOT%\hls_w4a4" "w4a4" "lenet_w4a4_top" "lenet_w4a4_ic2.cpp" "w4a4_ic2_hls" > w4a4_IC2_csynth.log 2>&1
if errorlevel 1 goto :fail
findstr /c:"LEVEL3_IC2_SYNTH_PASS" w4a4_IC2_csynth.log >nul
if errorlevel 1 goto :fail

echo [5/5] Collecting and checking results...
python collect_and_check_ic2.py
if errorlevel 1 goto :fail
echo LEVEL3_IC2_ALL_SYNTH_PASS
exit /b 0

:fail
echo LEVEL3_IC2_ALL_SYNTH_FAIL
exit /b 1

