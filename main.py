from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, ConfigDict

# Importa os componentes do banco de dados
from database import models
from database.database import SessionLocal, engine
from database import crud_processos, crud_usuarios, crud_clientes, crud_pagamentos

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

class ClienteSchema(BaseModel):
    id: int
    nome: str
    cpf_cnpj: str
    telefone: str | None = None
    email: str | None = None

    model_config = ConfigDict(from_attributes=True)

class PagamentoSchema(BaseModel):
    id: int
    descricao: str | None = None
    valor: float
    data_pagamento: str | None = None
    tipo: str | None = None
    processo_id: int | None = None

    model_config = ConfigDict(from_attributes=True)

class UsuarioSchema(BaseModel):
    id: int
    nome: str
    email: str | None = None
    login: str
    perfil: str

    model_config = ConfigDict(from_attributes=True)

class UsuarioCreateSchema(BaseModel):
    nome: str
    email: str | None = None
    login: str
    senha: str
    perfil: str

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
    processos = crud_processos.listar_processos(db)
    return processos

@app.get("/api/usuarios", response_model=List[UsuarioSchema])
def api_listar_usuarios(db: Session = Depends(get_db)):
    """Endpoint da API para listar todos os usuários."""
    usuarios = crud_usuarios.listar_usuarios(db)
    return usuarios

@app.post("/api/usuarios", response_model=UsuarioSchema, status_code=201)
def api_criar_usuario(usuario: UsuarioCreateSchema, db: Session = Depends(get_db)):
    """Endpoint da API para criar um novo usuário."""
    # Aqui você pode adicionar uma verificação para ver se o login já existe
    return crud_usuarios.criar_usuario(db=db, **usuario.model_dump())

@app.get("/api/clientes", response_model=List[ClienteSchema])
def api_listar_clientes(db: Session = Depends(get_db)):
    """Endpoint da API para listar todos os clientes."""
    clientes = crud_clientes.listar_clientes(db)
    return clientes

@app.get("/api/pagamentos", response_model=List[PagamentoSchema])
def api_listar_pagamentos(db: Session = Depends(get_db)):
    """Endpoint da API para listar todos os pagamentos."""
    pagamentos = crud_pagamentos.listar_pagamentos(db)
    return pagamentos