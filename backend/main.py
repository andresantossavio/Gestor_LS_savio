from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy.orm import Session, joinedload
from database.database import SessionLocal, engine, Base
from database import crud_clientes, crud_processos, crud_tarefas, crud_andamentos, crud_anexos, crud_pagamentos, crud_usuarios, models # Import models first
from backend import schemas # Then import schemas
import time  # Add this import for timing

# Ensure DB tables exist (uses existing SQLAlchemy Base)
# This needs to be run before the app is fully defined
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GESTOR_LS API")
api_router = APIRouter(prefix="/api")

# Enable CORS for local development and frontend app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@api_router.get("/clientes", response_model=list[schemas.Cliente])
def listar_clientes(db: Session = Depends(get_db)):
    return crud_clientes.listar_clientes(db)


@api_router.post("/clientes", response_model=schemas.Cliente)
def criar_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    c = crud_clientes.criar_cliente(
        cliente.nome, cliente.cpf_cnpj, cliente.telefone, cliente.email, db
    )
    if not c:
        raise HTTPException(status_code=400, detail="Erro ao criar cliente")
    return c


@api_router.put("/clientes/{cliente_id}", response_model=schemas.Cliente)
def atualizar_cliente(cliente_id: int, cliente: schemas.ClienteUpdate, db: Session = Depends(get_db)):
    c = crud_clientes.atualizar_cliente(
        cliente_id, cliente.nome, cliente.cpf_cnpj, cliente.telefone, cliente.email, db
    )
    if not c:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return c


@api_router.delete("/clientes/{cliente_id}")
def deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    crud_clientes.deletar_cliente(cliente_id, db)
    return {"status": "ok"}


# Processos endpoints
@api_router.get("/processos", response_model=list[schemas.Processo])
def listar_processos(db: Session = Depends(get_db)):
    start_time = time.time()  # Start timing
    processos = db.query(models.Processo).options(joinedload(models.Processo.cliente)).all()
    end_time = time.time()  # End timing
    print(f"Query execution time: {end_time - start_time} seconds")  # Log the time
    return processos


@api_router.get("/processos/{processo_id}", response_model=schemas.Processo)
def get_processo(processo_id: int, db: Session = Depends(get_db)):
    p = crud_processos.buscar_processo_por_id(processo_id, db)
    if not p:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return p


@api_router.post("/processos", response_model=schemas.Processo)
def criar_processo(processo: schemas.ProcessoCreate, db: Session = Depends(get_db)):
    p = crud_processos.criar_processo(
        processo.numero,
        processo.autor,
        processo.reu,
        processo.fase,
        processo.uf,
        processo.comarca,
        processo.vara,
        processo.status,
        processo.observacoes,
        processo.data_abertura,
        processo.data_fechamento,
        processo.cliente_id,
        db,
    )
    return p


@api_router.put("/processos/{processo_id}", response_model=schemas.Processo)
def atualizar_processo_api(processo_id: int, processo: schemas.ProcessoUpdate, db: Session = Depends(get_db)):
    p = crud_processos.atualizar_processo(processo_id, db, **processo.model_dump())
    if not p:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return p


@api_router.delete("/processos/{processo_id}")
def deletar_processo_api(processo_id: int, db: Session = Depends(get_db)):
    crud_processos.deletar_processo(processo_id, db)
    return {"status": "ok"}


# Tarefas endpoints
@api_router.get("/tarefas", response_model=list[schemas.Tarefa])
def listar_tarefas(db: Session = Depends(get_db)):
    return crud_tarefas.listar_tarefas_gerais(db)


@api_router.get("/tarefas/{tarefa_id}", response_model=schemas.Tarefa)
def get_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    t = crud_tarefas.buscar_tarefa(tarefa_id, db)
    if not t:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return t


@api_router.post("/tarefas", response_model=schemas.Tarefa)
def criar_tarefa_api(t: schemas.TarefaCreate, db: Session = Depends(get_db)):
    n = crud_tarefas.criar_tarefa(t.titulo, t.descricao, t.prazo, t.responsavel_id, t.processo_id, t.status, db)
    return n


@api_router.put("/tarefas/{tarefa_id}", response_model=schemas.Tarefa)
def atualizar_tarefa_api(tarefa_id: int, t: schemas.TarefaUpdate, db: Session = Depends(get_db)):
    updated = crud_tarefas.atualizar_tarefa(tarefa_id, db, **t.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return updated


@api_router.delete("/tarefas/{tarefa_id}")
def deletar_tarefa_api(tarefa_id: int, db: Session = Depends(get_db)):
    crud_tarefas.deletar_tarefa(tarefa_id, db)
    return {"status": "ok"}


# Andamentos endpoints
@api_router.get("/andamentos/{processo_id}", response_model=list[schemas.Andamento])
def listar_andamentos_do_processo(processo_id: int, db: Session = Depends(get_db)):
    return crud_andamentos.listar_andamentos_do_processo(processo_id, db)


@api_router.post("/andamentos", response_model=schemas.Andamento)
def criar_andamento_api(a: schemas.AndamentoCreate, db: Session = Depends(get_db)):
    na = crud_andamentos.criar_andamento(a.processo_id, a.descricao, a.tipo, a.criado_por, a.data, db)
    return na


@api_router.delete("/andamentos/{andamento_id}")
def deletar_andamento_api(andamento_id: int, db: Session = Depends(get_db)):
    crud_andamentos.deletar_andamento(andamento_id, db)
    return {"status": "ok"}


# Anexos endpoints
@api_router.get("/anexos/processo/{processo_id}", response_model=list[schemas.Anexo])
def listar_anexos_processo(processo_id: int, db: Session = Depends(get_db)):
    return crud_anexos.listar_anexos_do_processo(processo_id, db)


@api_router.post("/anexos", response_model=schemas.Anexo)
def criar_anexo_api(a: schemas.AnexoCreate, db: Session = Depends(get_db)):
    na = crud_anexos.criar_anexo(a.processo_id, a.andamento_id, a.nome_original, a.caminho_arquivo, a.mime, a.tamanho, a.criado_por, db)
    return na


@api_router.delete("/anexos/{anexo_id}")
def deletar_anexo_api(anexo_id: int, db: Session = Depends(get_db)):
    crud_anexos.deletar_anexo(anexo_id, db)
    return {"status": "ok"}


# Pagamentos endpoints
@api_router.get("/pagamentos", response_model=list[schemas.Pagamento])
def listar_pagamentos(db: Session = Depends(get_db)):
    return crud_pagamentos.listar_pagamentos(db)


@api_router.post("/pagamentos", response_model=schemas.Pagamento)
def criar_pagamento_api(p: schemas.PagamentoCreate, db: Session = Depends(get_db)):
    return crud_pagamentos.criar_pagamento(p.descricao, p.valor, p.tipo, p.processo_id, p.data_pagamento, db)


@api_router.delete("/pagamentos/{pagamento_id}")
def deletar_pagamento_api(pagamento_id: int, db: Session = Depends(get_db)):
    crud_pagamentos.deletar_pagamento(pagamento_id, db)
    return {"status": "ok"}


# Usuarios endpoints
@api_router.get("/usuarios", response_model=list[schemas.Usuario])
def listar_usuarios(db: Session = Depends(get_db)):
    return crud_usuarios.listar_usuarios(db)


@api_router.post("/usuarios", response_model=schemas.Usuario)
def criar_usuario_api(u: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    return crud_usuarios.criar_usuario(db, **u.model_dump())

@api_router.put("/usuarios/{usuario_id}", response_model=schemas.Usuario)
def atualizar_usuario_api(usuario_id: int, usuario: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    u = crud_usuarios.atualizar_usuario(usuario_id, db, **usuario.model_dump(exclude_unset=True))
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return u

@api_router.delete("/usuarios/{usuario_id}")
def deletar_usuario_api(usuario_id: int, db: Session = Depends(get_db)):
    crud_usuarios.deletar_usuario(usuario_id, db)
    return {"status": "ok"}



# Serve frontend static files from the repository root `frontend/` directory
frontend_build_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist"

# Mount the 'assets' directory from the build output
if (frontend_build_dir / "assets").exists():
    app.mount("/frontend/assets", StaticFiles(directory=str(frontend_build_dir / "assets")), name="assets")


@app.get("/")
def index():
    # prefer built react app in `frontend/dist/index.html` if available
    index_html = frontend_build_dir / "index.html"
    if index_html.exists():
        return FileResponse(str(index_html))
    return {"error": "Frontend not built. Run `npm run build` in `frontend/react-app`."}


# register API router
app.include_router(api_router)
