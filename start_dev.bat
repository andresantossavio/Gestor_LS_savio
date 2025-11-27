@echo off
REM Este script inicia os servidores de desenvolvimento para o backend e frontend.

echo Iniciando servidor Backend (FastAPI)...
REM Abre uma nova janela de comando para o backend na porta 8000
REM Certifique-se de que seu ambiente virtual (.venv) está ativado ou que python/uvicorn estão no PATH.
start "Backend" cmd /k "uvicorn main:app --reload --port 8000"

echo Iniciando servidor Frontend (React)...
REM Abre uma nova janela de comando para o frontend na porta 5173
start "Frontend" cmd /k "cd /d frontend\react-app && npm run dev"