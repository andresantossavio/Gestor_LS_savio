@echo off
cd /d %~dp0\legacy_desktop
if not exist "..\.venv\Scripts\activate" (
    echo Criando ambiente virtual na pasta raiz...
    python -m venv ..\.venv
)
..\.venv\Scripts\pip.exe install -r ..\requirements-desktop.txt
..\.venv\Scripts\python.exe main.py
