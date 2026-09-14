param([string]$Results = ".\results")
$ErrorActionPreference = "Stop"
$required = @(
  "g_balanced20_csim.csv", "g_balanced20_cosim.csv", "g_vivado_metrics.txt",
  "postroute_route_status.rpt", "postroute_timing_summary.rpt",
  "postroute_utilization.rpt", "postroute_drc.rpt"
)
foreach ($name in $required) {
  $p = Join-Path $Results $name
  if (!(Test-Path $p) -or (Get-Item $p).Length -eq 0) { throw "Missing or empty result: $p" }
}
$a = (Get-FileHash (Join-Path $Results "g_balanced20_csim.csv") -Algorithm SHA256).Hash
$b = (Get-FileHash (Join-Path $Results "g_balanced20_cosim.csv") -Algorithm SHA256).Hash
if ($a -ne $b) { throw "C-sim and RTL Co-sim CSV hashes differ" }
$m = Get-Content (Join-Path $Results "g_vivado_metrics.txt") -Raw
if ($m -notmatch "ROUTE_STATUS=Fully Routed") { throw "Route status failed" }
if ($m -match "DRC_CRITICAL_COUNT=([1-9][0-9]*)") { throw "Critical DRC exists" }
$summary = @(
  "G verification evidence generated: $(Get-Date -Format s)",
  "CSIM_CSV_SHA256=$a", "COSIM_CSV_SHA256=$b", $m.Trim(),
  "RESULT=PASS"
) -join [Environment]::NewLine
$summary | Set-Content (Join-Path $Results "g_verification_summary.txt") -Encoding UTF8
Write-Host "G_LEVEL_VALIDATION_ALL_PASS"

