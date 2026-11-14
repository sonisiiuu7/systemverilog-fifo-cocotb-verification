param([string]$ArchivePath = "")
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path $PSScriptRoot -Parent
$toolsDir = Join-Path $projectRoot '.tools'
New-Item -ItemType Directory -Force $toolsDir | Out-Null
$archive = Join-Path $toolsDir 'iverilog.zip'
$url = 'https://github.com/EDAPack/iverilog-bin/releases/download/v13.0.42506700046/iverilog-windows-x64-13.0.42506700046.zip'
$expectedHash = '0DE599CE348FFB6DAA8DACD184E59A5C41F14C62A265DD752875DC2361A30537'
if ($ArchivePath) {
    Copy-Item -LiteralPath $ArchivePath -Destination $archive -Force
} elseif (-not (Test-Path -LiteralPath $archive)) {
    Invoke-WebRequest -Uri $url -OutFile $archive
}
if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ne $expectedHash) {
    throw 'Simulator archive SHA256 mismatch. Do not use this archive.'
}
Expand-Archive -LiteralPath $archive -DestinationPath $toolsDir -Force
$bin = Join-Path $toolsDir 'iverilog\bin'
if (-not (Test-Path (Join-Path $bin 'zlib1.dll'))) {
    $gitRoot = Split-Path (Split-Path (Get-Command git).Source -Parent) -Parent
    $zlib = Join-Path $gitRoot 'mingw64\bin\zlib1.dll'
    if (-not (Test-Path -LiteralPath $zlib)) { throw 'Install 64-bit Git for Windows: its zlib1.dll is required by this simulator build.' }
    Copy-Item -LiteralPath $zlib -Destination (Join-Path $bin 'zlib1.dll')
}
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    python -m venv (Join-Path $projectRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Python virtual environment creation failed.' }
}
& $python -m pip install -r (Join-Path $projectRoot 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Python dependencies failed to install.' }
$oldPath = $env:PATH
try {
    $env:PATH = "$bin;$oldPath"
    & $python (Join-Path $PSScriptRoot 'run.py') --phase local-setup --suite smoke
    if ($LASTEXITCODE -ne 0) { throw 'Simulator smoke check failed.' }
} finally { $env:PATH = $oldPath }
Write-Output 'Setup verified. Run: powershell -ExecutionPolicy Bypass -File scripts/verify.ps1'
