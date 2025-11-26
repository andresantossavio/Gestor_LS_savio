from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session 
from fastapi.staticfiles import StaticFiles
from typing import List
from pydantic import BaseModel, ConfigDict

# Importa os componentes do banco de dados
from database import models
from database.database import SessionLocal, engine
from database import crud_processos, crud_usuarios, crud_clientes, crud_pagamentos, crud_tarefas, crud_anexos, crud_andamentos

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
    uf: str | None = None
    comarca: str | None = None
    vara: str | None = None
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

class AnexoSchema(BaseModel):
    id: int
    nome_arquivo: str
    caminho_arquivo: str
    data_upload: str | None = None
    processo_id: int

    model_config = ConfigDict(from_attributes=True)

class AndamentoSchema(BaseModel):
    id: int
    tipo_andamento_id: int
    data_andamento: str | None = None
    processo_id: int
    descricao_complementar: str | None = None
    model_config = ConfigDict(from_attributes=True)

class TarefaSchema(BaseModel):
    id: int
    tipo_tarefa_id: int
    descricao_complementar: str | None = None
    responsavel_id: int | None = None
    prazo: str | None = None

    model_config = ConfigDict(from_attributes=True)

class ProcessoCreateSchema(BaseModel):
    numero: str | None = None
    autor: str | None = None
    reu: str | None = None
    uf: str | None = None
    comarca: str | None = None
    vara: str | None = None
    fase: str | None = None
    status: str | None = None
    data_abertura: str | None = None
    cliente_id: int | None = None
    observacoes: str | None = None

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

class UsuarioUpdateSchema(BaseModel):
    nome: str | None = None
    email: str | None = None
    login: str | None = None
    senha: str | None = None
    perfil: str | None = None

# --- Schemas para Criação (Inputs da API) ---

class AndamentoCreateSchema(BaseModel):
    processo_id: int
    tipo_andamento_id: int
    data_andamento: str | None = None
    descricao_complementar: str | None = None

class TarefaCreateSchema(BaseModel):
    processo_id: int
    tipo_tarefa_id: int
    prazo: str | None = None
    responsavel_id: int | None = None
    descricao_complementar: str | None = None

# --- Schemas para os Tipos (Configurações) ---
class TipoAndamentoSchema(BaseModel):
    id: int
    nome: str

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

@app.post("/api/processos", response_model=ProcessoSchema, status_code=201)
def api_criar_processo(processo: ProcessoCreateSchema, db: Session = Depends(get_db)):
    """Endpoint para criar um novo processo."""
    return crud_processos.criar_processo(db=db, **processo.model_dump())

@app.get("/api/processos/{processo_id}", response_model=ProcessoSchema)
def api_buscar_processo(processo_id: int, db: Session = Depends(get_db)):
    """Endpoint para buscar um processo específico."""
    db_processo = crud_processos.buscar_processo(db, processo_id=processo_id)
    if db_processo is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return db_processo

@app.put("/api/processos/{processo_id}", response_model=ProcessoSchema)
def api_atualizar_processo(processo_id: int, processo: ProcessoCreateSchema, db: Session = Depends(get_db)):
    """Endpoint para atualizar um processo."""
    return crud_processos.atualizar_processo(db=db, processo_id=processo_id, dados_processo=processo.model_dump(exclude_unset=True))

@app.delete("/api/processos/{processo_id}", status_code=204)
def api_deletar_processo(processo_id: int, db: Session = Depends(get_db)):
    crud_processos.deletar_processo(db=db, processo_id=processo_id)
    return {"ok": True}

@app.get("/api/usuarios", response_model=List[UsuarioSchema])
def api_listar_usuarios(db: Session = Depends(get_db)):
    """Endpoint da API para listar todos os usuários."""
    usuarios = crud_usuarios.listar_usuarios(db)
    return usuarios

@app.post("/api/usuarios", response_model=UsuarioSchema, status_code=201)
def api_criar_usuario(usuario: UsuarioCreateSchema, db: Session = Depends(get_db)):
    """Endpoint da API para criar um novo usuário."""
    # Aqui você pode adicionar uma verificação para ver se o login já existe
    db_usuario = crud_usuarios.buscar_usuario_por_login(db, login=usuario.login)
    if db_usuario:
        raise HTTPException(status_code=400, detail="Login já cadastrado")
    return crud_usuarios.criar_usuario(db=db, **usuario.model_dump())

@app.get("/api/usuarios/{usuario_id}", response_model=UsuarioSchema)
def api_buscar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Endpoint para buscar um usuário específico pelo ID."""
    db_usuario = crud_usuarios.buscar_usuario(db, usuario_id=usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_usuario

@app.put("/api/usuarios/{usuario_id}", response_model=UsuarioSchema)
def api_atualizar_usuario(usuario_id: int, usuario: UsuarioUpdateSchema, db: Session = Depends(get_db)):
    """Endpoint para atualizar um usuário."""
    return crud_usuarios.atualizar_usuario(db=db, usuario_id=usuario_id, dados_usuario=usuario.model_dump(exclude_unset=True))

@app.delete("/api/usuarios/{usuario_id}", status_code=204)
def api_deletar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    crud_usuarios.deletar_usuario(db=db, usuario_id=usuario_id)
    return {"ok": True}

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

@app.get("/api/tarefas", response_model=List[TarefaSchema])
def api_listar_tarefas(db: Session = Depends(get_db)):
    """Endpoint da API para listar todas as tarefas."""
    tarefas = crud_tarefas.listar_tarefas(db)
    return tarefas

@app.get("/api/anexos", response_model=List[AnexoSchema])
def api_listar_anexos(db: Session = Depends(get_db)):
    """Endpoint da API para listar todos os anexos."""
    anexos = crud_anexos.listar_anexos(db)
    return anexos

@app.get("/api/andamentos", response_model=List[AndamentoSchema])
def api_listar_andamentos(db: Session = Depends(get_db)):
    """Endpoint da API para listar todos os andamentos."""
    andamentos = crud_andamentos.listar_andamentos(db)
    return andamentos

# --- Endpoints de Criação ---

@app.post("/api/andamentos", response_model=AndamentoSchema, status_code=201)
def api_criar_andamento(andamento: AndamentoCreateSchema, db: Session = Depends(get_db)):
    """Endpoint para criar um novo andamento em um processo."""
    return crud_andamentos.criar_andamento(db=db, **andamento.model_dump())

@app.post("/api/tarefas", response_model=TarefaSchema, status_code=201)
def api_criar_tarefa(tarefa: TarefaCreateSchema, db: Session = Depends(get_db)):
    """Endpoint para criar uma nova tarefa em um processo."""
    # O crud_tarefas.criar_tarefa precisa ser ajustado para receber esses campos
    return crud_tarefas.criar_tarefa(db=db, **tarefa.model_dump())

@app.post("/api/anexos", status_code=201)
async def api_criar_anexo(
    processo_id: int = Form(...),
    andamento_id: int | None = Form(None),
    file: UploadFile = File(...)
):
    """Endpoint para fazer upload de um anexo e associá-lo a um processo/andamento."""
    # Aqui entraria a lógica para salvar o arquivo em disco e registrar no DB
    # Ex: caminho = await crud_anexos.salvar_arquivo(file)
    #     crud_anexos.criar_anexo(db, processo_id=processo_id, caminho_arquivo=caminho, ...)
    return {"filename": file.filename, "processo_id": processo_id, "message": "Anexo recebido, lógica de salvamento a ser implementada."}
