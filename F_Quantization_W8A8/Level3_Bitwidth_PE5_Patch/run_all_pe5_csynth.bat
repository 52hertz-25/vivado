@echo off
setlocal
set "PATCH_ROOT=%~dp0"
if "%PATCH_ROOT:~-1%"=="\" set "PATCH_ROOT=%PATCH_ROOT:~0,-1%"
set "PROJECT_ROOT=%PATCH_ROOT%\.."

python "%PATCH_ROOT%\prepare_pe5_variants.py"
if errorlevel 1 exit /b %errorlevel%

call :run_one hls_w8a8 W8A8 lenet_w8a8_top lenet_w8a8_pe5.cpp w8a8_pe5_hls
if errorlevel 1 exit /b %errorlevel%
call :run_one hls_w6a6 W6A6 lenet_w6a6_top lenet_w6a6_pe5.cpp w6a6_pe5_hls
if errorlevel 1 exit /b %errorlevel%
call :run_one hls_w4a4 W4A4 lenet_w4a4_top lenet_w4a4_pe5.cpp w4a4_pe5_hls
if errorlevel 1 exit /b %errorlevel%

python "%PATCH_ROOT%\collect_pe_results.py"
if errorlevel 1 exit /b %errorlevel%
echo LEVEL3_BITWIDTH_PE5_BATCH_PASS
exit /b 0

:run_one
set "HLS_ROOT=%PROJECT_ROOT%\%~1"
set "LOG=%PATCH_ROOT%\%~2_PE5_csynth.log"
echo Running %~2 PE5 synthesis...
vitis_hls -f "%PATCH_ROOT%\run_pe5_csynth.tcl" "%HLS_ROOT%" %~2 %~3 %~4 %~5 > "%LOG%" 2>&1
if errorlevel 1 (
  echo LEVEL3_PE5_SYNTH_FAIL tag=%~2 log=%LOG%
  exit /b 1
)
findstr /i /c:"LEVEL3_PE5_SYNTH_PASS" /c:"ERROR:" "%LOG%"
exit /b 0

