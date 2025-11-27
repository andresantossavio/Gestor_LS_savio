@echo off
REM Este script inicia os servidores de desenvolvimento para o backend e frontend.

echo Verificando ambiente virtual do Python...
IF NOT EXIST .venv (
    echo Criando ambiente virtual...
    python -m venv .venv
    echo Instalando dependencias do backend...
    call .\.venv\Scripts\activate.bat
    pip install -r requirements.txt
) ELSE (
    call .\.venv\Scripts\activate.bat
)

echo Iniciando servidor Backend (FastAPI)...
REM Abre uma nova janela de comando para o backend na porta 8000
start "Backend" cmd /k "call .\.venv\Scripts\activate.bat && uvicorn main:app --reload --port 8000"

echo Iniciando servidor Frontend (React)...
REM Abre uma nova janela de comando para o frontend na porta 5173
REM Certifique-se de que as dependencias do frontend estao instaladas com 'npm install'
start "Frontend" cmd /k "cd /d frontend\react-app && npm run dev"