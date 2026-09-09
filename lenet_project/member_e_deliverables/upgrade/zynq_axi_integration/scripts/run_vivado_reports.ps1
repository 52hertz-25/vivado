$ErrorActionPreference = "Stop"
$env:PROCESSOR_ARCHITECTURE = "AMD64"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$packageDir = Split-Path -Parent $scriptDir
$tclPath = Join-Path $scriptDir "rerun_vivado_reports.tcl"
$logPath = Join-Path $packageDir "reports\vivado_rerun.log"
$journalPath = Join-Path $packageDir "reports\vivado_rerun.jou"
$vivadoBat = "E:\Xilinx\Vivado\2022.2\bin\vivado.bat"

if (-not (Test-Path -LiteralPath $vivadoBat)) {
    throw "Vivado 2022.2 launcher not found: $vivadoBat"
}

& cmd.exe /d /c call $vivadoBat -mode batch -source $tclPath -log $logPath -journal $journalPath -notrace
if ($LASTEXITCODE -ne 0) {
    throw "Vivado failed with exit code $LASTEXITCODE. See $logPath"
}

if (-not (Select-String -LiteralPath $logPath -SimpleMatch "MEMBER_E_VIVADO_RERUN_PASS" -Quiet)) {
    throw "Vivado exited without the expected success marker. See $logPath"
}

Write-Output "Member E Vivado report rerun completed successfully."
