param([string]$Phase = 'local', [switch]$Mutations, [switch]$Sweep)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Run scripts/bootstrap.ps1 first.' }
$oldPath = $env:PATH
try {
    $env:PATH = (Join-Path $projectRoot '.tools\iverilog\bin') + ";$oldPath"
    & $python (Join-Path $PSScriptRoot 'run.py') --phase $Phase --suite random
    if ($LASTEXITCODE -ne 0) { throw 'FIFO verification failed.' }
    if ($Mutations) {
        & $python (Join-Path $PSScriptRoot 'mutate.py')
        if ($LASTEXITCODE -ne 0) { throw 'Fault-detection verification failed.' }
    }
    if ($Sweep) {
        & $python (Join-Path $PSScriptRoot 'sweep.py')
        if ($LASTEXITCODE -ne 0) { throw 'Parameter sweep failed.' }
    }
} finally { $env:PATH = $oldPath }
