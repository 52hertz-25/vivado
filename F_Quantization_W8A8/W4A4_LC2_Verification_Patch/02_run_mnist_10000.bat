@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "ROOT=%~dp0.."
set "RESULT=%~dp0results\w4a4_lc2_mnist_10000_results.csv"
echo Running W4A4 LC2 MNIST C-sim, 10000 samples...
call vitis_hls -f run_w4a4_lc2_mnist.tcl -tclargs "%ROOT%" "10000" "%RESULT%" > w4a4_lc2_mnist_10000.log 2>&1
if errorlevel 1 goto fail
findstr /c:"W4A4_LC2_MNIST_CSIM_PASS" w4a4_lc2_mnist_10000.log >nul || goto fail
python check_mnist_equivalence.py "%ROOT%\hls_w4a4\reports\mnist\w4a4_mnist_10000_results.csv" "%RESULT%" >> w4a4_lc2_mnist_10000.log 2>&1
if errorlevel 1 goto fail
findstr /c:"W4A4_LC2_MNIST_EQUIVALENCE_PASS" w4a4_lc2_mnist_10000.log >nul || goto fail
echo RESULT=%RESULT%
echo W4A4_LC2_MNIST_10000_PASS
exit /b 0
:fail
echo W4A4_LC2_MNIST_10000_FAIL
exit /b 1
