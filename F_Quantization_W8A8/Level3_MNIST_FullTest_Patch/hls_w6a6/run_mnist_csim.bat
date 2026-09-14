@echo off
setlocal
set "PROJECT_ROOT=%~dp0"
if "%PROJECT_ROOT:~-1%"=="\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"
set "LIMIT=%~1"
if "%LIMIT%"=="" set "LIMIT=10000"
set "DATASET_ROOT=%PROJECT_ROOT%\..\hls_w8a8\data\mnist_w8a8"
set "WEIGHT_ROOT=%PROJECT_ROOT%\model\int6_weights"
set "RESULT_DIR=%PROJECT_ROOT%\reports\mnist"
set "RESULT_CSV=%RESULT_DIR%\w6a6_mnist_%LIMIT%_results.csv"
if not exist "%RESULT_DIR%" mkdir "%RESULT_DIR%"
if not exist "%DATASET_ROOT%\mnist_test_32x32.bin" (
    echo ERROR: MNIST image file not found: %DATASET_ROOT%\mnist_test_32x32.bin
    exit /b 2
)
if not exist "%DATASET_ROOT%\mnist_test_labels.bin" (
    echo ERROR: MNIST label file not found: %DATASET_ROOT%\mnist_test_labels.bin
    exit /b 2
)

echo Running W6A6 MNIST C-simulation, samples=%LIMIT%
vitis_hls -f "%PROJECT_ROOT%\scripts\run_w6a6_mnist_csim.tcl" "%PROJECT_ROOT%" "%DATASET_ROOT%" "%WEIGHT_ROOT%" "%LIMIT%" "%RESULT_CSV%"
set "RETURN_CODE=%ERRORLEVEL%"
if not "%RETURN_CODE%"=="0" (
    echo W6A6_MNIST_CSIM_BATCH_FAIL exit_code=%RETURN_CODE%
    exit /b %RETURN_CODE%
)
echo W6A6_MNIST_CSIM_BATCH_PASS
echo RESULT=%RESULT_CSV%
exit /b 0
