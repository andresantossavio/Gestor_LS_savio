# Starter script for the web app (PowerShell)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install --upgrade pip
    pip install -r requirements.txt
} else {
    .\.venv\Scripts\Activate.ps1
}

python main.py
