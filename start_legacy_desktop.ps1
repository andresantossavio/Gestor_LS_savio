# Starter script for legacy desktop UI
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir\legacy_desktop

if (-not (Test-Path "..\.venv\Scripts\python.exe")) {
    python -m venv ..\.venv
    ..\.venv\Scripts\Activate.ps1
    pip install -r ..\requirements-desktop.txt
} else {
    ..\.venv\Scripts\Activate.ps1
}

python main.py
