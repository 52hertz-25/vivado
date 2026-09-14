@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PATCH=%CD%"
set "ROOT=%PATCH%\.."
set "HLS=%ROOT%\hls_w4a4"
set "DATA=%ROOT%\hls_w8a8\data\mnist_w8a8"
set "WEIGHTS=%HLS%\model\int4_weights"
set "RESULTS=%PATCH%\results"
if not exist "%RESULTS%" mkdir "%RESULTS%"

where vitis_hls >nul 2>&1 || (echo ERROR: vitis_hls not found & exit /b 2)
where vivado >nul 2>&1 || (echo ERROR: vivado not found & exit /b 2)

echo [1/3] Running balanced-20 C simulation, synthesis and RTL co-simulation...
call vitis_hls -f "%PATCH%\run_g_hls_verification.tcl" -tclargs "%HLS%" "%DATA%" "%WEIGHTS%" "%RESULTS%" > "%RESULTS%\g_hls_full.log" 2>&1
if errorlevel 1 (echo G_HLS_VALIDATION_FAIL & echo See %RESULTS%\g_hls_full.log & exit /b 1)

set "DCP=%HLS%\final_delivery\hardware\lenet_w4a4_system_routed.dcp"
if not exist "%DCP%" set "DCP=%HLS%\vivado_review\delivery\lenet_w4a4_system_routed.dcp"
if not exist "%DCP%" set "DCP=%HLS%\vivado_review\reports\lenet_w4a4_routed.dcp"
if not exist "%DCP%" (echo ERROR: routed DCP not found & exit /b 2)

echo [2/3] Rechecking routed design in Vivado...
call vivado -mode batch -nojournal -nolog -source "%PATCH%\run_g_vivado_postroute.tcl" -tclargs "%DCP%" "%RESULTS%" > "%RESULTS%\g_vivado_postroute.log" 2>&1
if errorlevel 1 (echo G_VIVADO_POST_ROUTE_FAIL & echo See %RESULTS%\g_vivado_postroute.log & exit /b 1)

echo [3/3] Checking evidence integrity...
powershell -NoProfile -ExecutionPolicy Bypass -File "%PATCH%\check_g_results.ps1" -Results "%RESULTS%"
if errorlevel 1 (echo G_RESULT_CHECK_FAIL & exit /b 1)
echo G_LEVEL_VALIDATION_ALL_PASS
exit /b 0
