"""
GESTOR_LS - Aplicação FastAPI Principal
Consolida todos os roteadores e configura a aplicação.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path as PathLib
from database.database import engine
from database import models

# Função para criar as tabelas no banco de dados
def create_database():
    models.Base.metadata.create_all(bind=engine)

# --- Lifespan para gerenciar eventos de inicialização e desligamento ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código a ser executado antes da aplicação iniciar
    print("✓ Iniciando GESTOR_LS...")
    create_database()
    print("✓ Banco de dados pronto")
    yield
    # Código a ser executado quando a aplicação for desligada
    print("✓ Aplicação encerrada.")

# Cria a aplicação FastAPI com o gerenciador de lifespan
app = FastAPI(
    title="GESTOR_LS API",
    description="API para gerenciamento de processos e contabilidade",
    version="1.0.0",
    lifespan=lifespan
)

# --- Configuração do CORS ---
# Permite que o frontend (rodando em localhost:3000) se comunique com o backend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite
    "http://127.0.0.1:5173",  # Vite
    "*"  # Desenvolvimento
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("✓ CORS configurado")

# --- Importar e registrar roteadores do backend ---
from backend.main import api_router, config_router

# Registrar os roteadores
app.include_router(api_router)
app.include_router(config_router)

print("✓ Roteadores registrados")
print("✓ GESTOR_LS pronto! Escutando em http://localhost:8000")
