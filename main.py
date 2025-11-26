from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, ConfigDict

# Importa os componentes do banco de dados
from database import models
from database.database import SessionLocal, engine
from database.crud_processos import listar_processos

# Cria as tabelas no banco de dados se elas não existirem
models.Base.metadata.create_all(bind=engine)

# Cria a aplicação FastAPI
app = FastAPI()

# --- Pydantic Schemas (Modelos de dados para a API) ---

class ProcessoSchema(BaseModel):
    id: int
    numero: str | None = None
    autor: str | None = None
    reu: str | None = None
    fase: str | None = None
    status: str | None = None
    data_abertura: str | None = None

    # Configuração para permitir que o Pydantic leia dados de objetos SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


# --- Dependência para Gerenciamento da Sessão do Banco de Dados ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Endpoints (Rotas) da API ---

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do GESTOR_LS"}

@app.get("/api/processos", response_model=List[ProcessoSchema])
def api_listar_processos(db: Session = Depends(get_db)):
    """Endpoint da API para listar todos os processos."""
    processos = listar_processos(db=db)
    return processos