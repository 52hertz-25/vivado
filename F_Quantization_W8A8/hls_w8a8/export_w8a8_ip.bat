@echo off
setlocal

rem ============================================================
rem Export LeNet-5 W8A8 INT32 Vivado IP
rem Vitis HLS 2022.2
rem ============================================================

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"

echo ============================================================
echo Exporting LeNet-5 W8A8 INT32 Vivado IP...
echo Project root: %ROOT%
echo ============================================================

vitis_hls -f "%ROOT%\scripts\export_w8a8_ip.tcl" "%ROOT%"

if errorlevel 1 (
    echo ============================================================
    echo W8A8 IP export FAILED.
    echo Check the first ERROR message above.
    echo ============================================================
    exit /b 1
)

echo ============================================================
echo W8A8 IP export PASSED.
echo Output:
echo %ROOT%\export\lenet_w8a8_top_ip.zip
echo ============================================================

endlocal