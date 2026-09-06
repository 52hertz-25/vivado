@echo off
setlocal

where vivado_hls >nul 2>nul
if errorlevel 1 (
    echo ERROR: vivado_hls was not found.
    echo Open "Vivado HLS 2019.1 Command Prompt" and run this file again.
    exit /b 1
)

pushd "%~dp0"
vivado_hls -f run_hls.tcl
set HLS_STATUS=%ERRORLEVEL%
popd

if not "%HLS_STATUS%"=="0" (
    echo ERROR: Vivado HLS flow failed with exit code %HLS_STATUS%.
    exit /b %HLS_STATUS%
)

echo Vivado HLS 2019.1 flow completed successfully.
exit /b 0
