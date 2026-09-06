param(
    [string]$ModelDir = "..\model"
)

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
$buildDir = Join-Path $projectRoot "build"
$resultsDir = Join-Path $projectRoot "results"
$executable = Join-Path $buildDir "tb_lenet_conv.exe"

New-Item -ItemType Directory -Force $buildDir | Out-Null
New-Item -ItemType Directory -Force $resultsDir | Out-Null

Push-Location $projectRoot
try {
    & g++ -std=c++11 -O0 -Wall -Wextra -Wno-unknown-pragmas -Wno-unused-label `
        -Iinclude -Itb src/lenet_conv.cpp tb/tb_lenet_conv.cpp `
        -o $executable
    if ($LASTEXITCODE -ne 0) {
        throw "C++ compilation failed with exit code $LASTEXITCODE"
    }

    $simulationOutput = & $executable $ModelDir --multi 2>&1
    $simulationStatus = $LASTEXITCODE
    $simulationOutput | Tee-Object -FilePath (Join-Path $resultsDir "csim_results.txt")
    if ($simulationStatus -ne 0) {
        throw "C simulation failed with exit code $simulationStatus"
    }
} finally {
    Pop-Location
}
