@echo off
setlocal
set "PROJECT_ROOT=%~dp0"
if "%PROJECT_ROOT:~-1%"=="\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"
set "LIMIT=%~1"
if "%LIMIT%"=="" set "LIMIT=10000"
set "DATASET_ROOT=%PROJECT_ROOT%\data\mnist_w8a8"
set "WEIGHT_ROOT=%PROJECT_ROOT%\model\int8_weights"
set "RESULT_DIR=%PROJECT_ROOT%\reports\mnist"
set "RESULT_CSV=%RESULT_DIR%\w8a8_mnist_%LIMIT%_results.csv"
if not exist "%RESULT_DIR%" mkdir "%RESULT_DIR%"

echo Running W8A8 MNIST C-simulation, samples=%LIMIT%
vitis_hls -f "%PROJECT_ROOT%\scripts\run_w8a8_mnist_csim.tcl" "%PROJECT_ROOT%" "%DATASET_ROOT%" "%WEIGHT_ROOT%" "%LIMIT%" "%RESULT_CSV%"
set "RETURN_CODE=%ERRORLEVEL%"
if not "%RETURN_CODE%"=="0" (
    echo W8A8_MNIST_CSIM_BATCH_FAIL exit_code=%RETURN_CODE%
    exit /b %RETURN_CODE%
)
echo W8A8_MNIST_CSIM_BATCH_PASS
echo RESULT=%RESULT_CSV%
exit /b 0
