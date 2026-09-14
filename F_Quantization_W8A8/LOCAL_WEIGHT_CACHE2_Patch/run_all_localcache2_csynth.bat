@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "ROOT=%~dp0.."
echo [1/5] Preparing local-cache variants...
python prepare_localcache2_variants.py > prepare_localcache2.log 2>&1
if errorlevel 1 goto fail
echo [2/5] Synthesizing W8A8 local-cache2...
call vitis_hls -f run_localcache2_csynth.tcl -tclargs "%ROOT%\hls_w8a8" "w8a8" "lenet_w8a8_top" "lenet_w8a8_lc2.cpp" "w8a8_lc2_hls" > w8a8_LC2_csynth.log 2>&1
if errorlevel 1 goto fail
findstr /c:"LOCALCACHE2_SYNTH_PASS" w8a8_LC2_csynth.log >nul || goto fail
echo [3/5] Synthesizing W6A6 local-cache2...
call vitis_hls -f run_localcache2_csynth.tcl -tclargs "%ROOT%\hls_w6a6" "w6a6" "lenet_w6a6_top" "lenet_w6a6_lc2.cpp" "w6a6_lc2_hls" > w6a6_LC2_csynth.log 2>&1
if errorlevel 1 goto fail
findstr /c:"LOCALCACHE2_SYNTH_PASS" w6a6_LC2_csynth.log >nul || goto fail
echo [4/5] Synthesizing W4A4 local-cache2...
call vitis_hls -f run_localcache2_csynth.tcl -tclargs "%ROOT%\hls_w4a4" "w4a4" "lenet_w4a4_top" "lenet_w4a4_lc2.cpp" "w4a4_lc2_hls" > w4a4_LC2_csynth.log 2>&1
if errorlevel 1 goto fail
findstr /c:"LOCALCACHE2_SYNTH_PASS" w4a4_LC2_csynth.log >nul || goto fail
echo [5/5] Collecting reports...
python collect_localcache2.py
if errorlevel 1 goto fail
echo LOCALCACHE2_ALL_SYNTH_PASS
exit /b 0
:fail
echo LOCALCACHE2_ALL_SYNTH_FAIL
exit /b 1
