@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "PATCH=%CD%"
set "ROOT=%PATCH%\.."
set "RESULTS=%PATCH%\results"
if not exist "%RESULTS%" mkdir "%RESULTS%"

where vivado >nul 2>&1
if errorlevel 1 (
  call D:\Xilinx\Vivado\2022.2\settings64.bat
)
where vivado >nul 2>&1 || (echo ERROR: vivado not found & exit /b 2)

set "DCP=%ROOT%\hls_w4a4\final_delivery\hardware\lenet_w4a4_system_routed.dcp"
if not exist "%DCP%" set "DCP=%ROOT%\hls_w4a4\vivado_review\delivery\lenet_w4a4_system_routed.dcp"
if not exist "%DCP%" set "DCP=%ROOT%\hls_w4a4\vivado_review\project\LeNet_W4A4_Review.runs\impl_1\lenet_system_wrapper_routed.dcp"
if not exist "%DCP%" (echo ERROR: routed DCP not found & exit /b 2)

echo [1/2] Rechecking existing routed DCP in Vivado...
call vivado -mode batch -nojournal -nolog -source "%PATCH%\run_g_vivado_postroute.tcl" -tclargs "%DCP%" "%RESULTS%" > "%RESULTS%\g_vivado_postroute.log" 2>&1
if errorlevel 1 (
  echo G_VIVADO_POST_ROUTE_FAIL
  echo See %RESULTS%\g_vivado_postroute.log
  exit /b 1
)

echo [2/2] Checking all existing G evidence...
powershell -NoProfile -ExecutionPolicy Bypass -File "%PATCH%\check_g_results.ps1" -Results "%RESULTS%"
if errorlevel 1 (echo G_RESULT_CHECK_FAIL & exit /b 1)

echo G_LEVEL_VALIDATION_ALL_PASS
exit /b 0
