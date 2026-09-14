@echo off
setlocal
cd /d "%~dp0"

set "IPZIP=lenet_w4a4_lc2_top_ip.zip"
set "IPDIR=%CD%\extracted_ip"
set "LOG=%CD%\w4a4_lc2_vivado_impl.log"

if not exist "%IPZIP%" (
  echo ERROR: %IPZIP% is not in %CD%
  echo Copy the exported IP ZIP into this folder, then run this BAT again.
  exit /b 2
)

echo [1/3] Extracting exported W4A4 LC2 IP...
if exist "%IPDIR%" rmdir /s /q "%IPDIR%"
powershell -NoProfile -Command "Expand-Archive -LiteralPath '%CD%\%IPZIP%' -DestinationPath '%IPDIR%' -Force"
if errorlevel 1 exit /b 3

echo [2/3] Running Vivado OOC synthesis, placement and routing...
call vivado -mode batch -nolog -nojournal -source run_w4a4_lc2_vivado_impl.tcl -tclargs "%IPDIR%" > "%LOG%" 2>&1
set "VIVADO_RC=%ERRORLEVEL%"

echo [3/3] Checking result...
if exist results\implementation_summary.txt type results\implementation_summary.txt
findstr /c:"W4A4_LC2_VIVADO_IMPL_TIMING_PASS" "%LOG%" >nul
if errorlevel 1 (
  echo W4A4_LC2_VIVADO_IMPL_FAIL
  echo See: %LOG%
  exit /b 1
)
if not "%VIVADO_RC%"=="0" (
  echo W4A4_LC2_VIVADO_IMPL_FAIL_RC_%VIVADO_RC%
  exit /b %VIVADO_RC%
)

echo W4A4_LC2_VIVADO_IMPL_ALL_PASS
echo Reports: %CD%\results
exit /b 0
