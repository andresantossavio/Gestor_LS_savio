@echo off
cd /d %~dp0\legacy_desktop
if not exist "..\.venv\Scripts\python.exe" (
    python -m venv ..\.venv
    ..\.venv\Scripts\python.exe -m pip install --upgrade pip
    ..\.venv\Scripts\pip.exe install -r ..\requirements-desktop.txt
)
..\.venv\Scripts\python.exe main.py
