@echo off
cd /d %~dp0
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install --upgrade pip
    .venv\Scripts\pip.exe install -r requirements.txt
)
echo "Iniciando servidor FastAPI com Uvicorn na porta 8000..."
.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
