@echo off
setlocal
cd /d "%~dp0"
where vitis_hls.bat >nul 2>nul
if errorlevel 1 (
  echo ERROR: vitis_hls.bat is not in PATH.
  echo Open the Vitis HLS 2022.2 Command Prompt, then run this file again.
  pause
  exit /b 1
)
call vitis_hls.bat -f "%~dp0scripts\run_dse.tcl" -tclargs "%~dp0"
if errorlevel 1 (
  echo ERROR: one or more HLS runs failed. Check work\CONFIG_ID\solution1\solution1.log.
  pause
  exit /b 1
)
py -3 "%~dp0scripts\collect_results.py" "%~dp0"
echo.
echo Done. Open results\hls_dse_results.csv
pause
