from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy.orm import Session, joinedload
from database.database import SessionLocal, engine, Base
from database import crud_clientes, crud_processos, crud_tarefas, crud_andamentos, crud_anexos, crud_pagamentos, crud_usuarios, crud_contabilidade, models # Import models first
from .import_contabilidade import carregar_csv_contabilidade
from backend import schemas # Then import schemas
from backend import config_data # Import config data
import time  # Add this import for timing

# Ensure DB tables exist (uses existing SQLAlchemy Base)
# This needs to be run before the app is fully defined
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GESTOR_LS API")

# Routers
api_router = APIRouter(prefix="/api")
config_router = APIRouter(prefix="/api/config")


# --- Config Endpoints ---
@config_router.get("/ufs", response_model=list[str])
def get_ufs():
    return config_data.UFS

@config_router.get("/tipos", response_model=list[str])
def get_tipos():
    return config_data.TIPOS_PROCESSO

@config_router.get("/categorias", response_model=list[str])
def get_categorias():
    return config_data.CATEGORIAS_PROCESSO

@config_router.get("/tribunais", response_model=list[str])
def get_tribunais():
    return config_data.TRIBUNAIS

@config_router.get("/esferas", response_model=list[str])
def get_esferas():
    return config_data.ESFERAS_JUSTICA

@config_router.get("/classes", response_model=dict[str, list[str]])
def get_classes():
    return config_data.CLASSES_JURIDICAS

@config_router.get("/ritos", response_model=dict[str, list[str]])
def get_ritos():
    return config_data.RITOS


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


@api_router.get("/clientes/{cliente_id}", response_model=schemas.Cliente)
def buscar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = crud_clientes.buscar_cliente_por_id(cliente_id, db)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente


@api_router.post("/clientes", response_model=schemas.Cliente)
def criar_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    # Criar dict apenas com os campos que foram fornecidos (não None)
    dados = {k: v for k, v in cliente.model_dump().items() if v is not None}
    c = crud_clientes.criar_cliente(db, **dados)
    if not c:
        raise HTTPException(status_code=400, detail="Erro ao criar cliente")
    return c


@api_router.put("/clientes/{cliente_id}", response_model=schemas.Cliente)
def atualizar_cliente(cliente_id: int, cliente: schemas.ClienteUpdate, db: Session = Depends(get_db)):
    # Criar dict apenas com os campos que foram fornecidos (não None)
    dados = {k: v for k, v in cliente.model_dump().items() if v is not None}
    print(f"DEBUG - Atualizando cliente {cliente_id} com dados: {dados}")
    c = crud_clientes.atualizar_cliente(cliente_id, db, **dados)
    if not c:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return c


@api_router.delete("/clientes/{cliente_id}")
def deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    crud_clientes.deletar_cliente(cliente_id, db)
    return {"status": "ok"}

# ---------------- Contabilidade ----------------
from fastapi import UploadFile, File
from typing import List

# Endpoints de import CSV comentados (substituídos por cadastro manual de Entradas)
# @api_router.post("/contabilidade/import", response_model=List[dict])
# def import_contabilidade(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     ...

# @api_router.get("/contabilidade/recebimentos", response_model=List[dict])
# def listar_recebimentos(db: Session = Depends(get_db)):
#     ...

# --- Sócios ---
@api_router.get("/contabilidade/socios", response_model=List[schemas.Socio])
def listar_socios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_contabilidade.get_socios(db, skip=skip, limit=limit)

@api_router.post("/contabilidade/socios", response_model=schemas.Socio)
def criar_socio(socio: schemas.SocioCreate, db: Session = Depends(get_db)):
    return crud_contabilidade.create_socio(db, socio)

@api_router.put("/contabilidade/socios/{socio_id}", response_model=schemas.Socio)
def atualizar_socio(socio_id: int, socio: schemas.SocioUpdate, db: Session = Depends(get_db)):
    db_socio = crud_contabilidade.update_socio(db, socio_id, socio)
    if not db_socio:
        raise HTTPException(status_code=404, detail="Sócio não encontrado")
    return db_socio

@api_router.delete("/contabilidade/socios/{socio_id}")
def deletar_socio(socio_id: int, db: Session = Depends(get_db)):
    db_socio = crud_contabilidade.delete_socio(db, socio_id)
    if not db_socio:
        raise HTTPException(status_code=404, detail="Sócio não encontrado")
    return {"status": "ok"}

# --- Entradas ---
@api_router.get("/contabilidade/entradas", response_model=List[schemas.Entrada])
def listar_entradas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_contabilidade.get_entradas(db, skip=skip, limit=limit)

@api_router.post("/contabilidade/entradas", response_model=schemas.Entrada)
def criar_entrada(entrada: schemas.EntradaCreate, db: Session = Depends(get_db)):
    return crud_contabilidade.create_entrada(db, entrada)

# --- Despesas ---
@api_router.get("/contabilidade/despesas", response_model=List[schemas.Despesa])
def listar_despesas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_contabilidade.get_despesas(db, skip=skip, limit=limit)

@api_router.post("/contabilidade/despesas", response_model=schemas.Despesa)
def criar_despesa(despesa: schemas.DespesaCreate, db: Session = Depends(get_db)):
    return crud_contabilidade.create_despesa(db, despesa)

# --- DRE ---
@api_router.get("/contabilidade/dre")
def listar_dre_ano(year: int, db: Session = Depends(get_db)):
    """Retorna DRE dos 12 meses do ano especificado."""
    from utils.datas import meses_do_ano
    meses = meses_do_ano(year)
    
    resultado = []
    for mes in meses:
        dre = crud_contabilidade.get_dre_mensal(db, mes)
        if not dre:
            # Se não consolidado, retornar estrutura vazia
            resultado.append({
                "mes": mes,
                "receita_bruta": 0.0,
                "receita_12m": 0.0,
                "aliquota": 0.0,
                "aliquota_efetiva": 0.0,
                "deducao": 0.0,
                "imposto": 0.0,
                "inss_patronal": 0.0,
                "despesas_gerais": 0.0,
                "lucro_liquido": 0.0,
                "reserva_10p": 0.0,
                "consolidado": False
            })
        else:
            resultado.append({
                "mes": dre.mes,
                "receita_bruta": dre.receita_bruta,
                "receita_12m": dre.receita_12m,
                "aliquota": dre.aliquota,
                "aliquota_efetiva": dre.aliquota_efetiva,
                "deducao": dre.deducao,
                "imposto": dre.imposto,
                "inss_patronal": dre.inss_patronal,
                "despesas_gerais": dre.despesas_gerais,
                "lucro_liquido": dre.lucro_liquido,
                "reserva_10p": dre.reserva_10p,
                "consolidado": dre.consolidado
            })
    
    return resultado

@api_router.post("/contabilidade/dre/consolidar")
def consolidar_dre(mes: str, forcar: bool = False, db: Session = Depends(get_db)):
    """Consolida ou recalcula a DRE de um mês específico."""
    try:
        dre = crud_contabilidade.consolidar_dre_mes(db, mes, forcar_recalculo=forcar)
        return {
            "mes": dre.mes,
            "receita_bruta": dre.receita_bruta,
            "receita_12m": dre.receita_12m,
            "aliquota": dre.aliquota,
            "aliquota_efetiva": dre.aliquota_efetiva,
            "deducao": dre.deducao,
            "imposto": dre.imposto,
            "inss_patronal": dre.inss_patronal,
            "despesas_gerais": dre.despesas_gerais,
            "lucro_liquido": dre.lucro_liquido,
            "reserva_10p": dre.reserva_10p,
            "consolidado": dre.consolidado
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.delete("/contabilidade/dre/consolidar")
def desconsolidar_dre(mes: str, db: Session = Depends(get_db)):
    """Desconsolida um mês de DRE, permitindo recalcular posteriormente."""
    try:
        dre = crud_contabilidade.desconsolidar_dre_mes(db, mes)
        if not dre:
            raise HTTPException(status_code=404, detail=f"DRE do mês {mes} não encontrado")
        return {
            "mes": dre.mes,
            "consolidado": dre.consolidado,
            "message": f"Mês {mes} desconsolidado com sucesso"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Faixas Simples ---
@api_router.get("/contabilidade/simples-faixas")
def listar_simples_faixas(db: Session = Depends(get_db)):
    """Lista todas as faixas do Simples Nacional configuradas."""
    faixas = crud_contabilidade.get_all_simples_faixas(db)
    return [{
        "id": f.id,
        "limite_superior": f.limite_superior,
        "aliquota": f.aliquota,
        "deducao": f.deducao,
        "vigencia_inicio": str(f.vigencia_inicio),
        "vigencia_fim": str(f.vigencia_fim) if f.vigencia_fim else None,
        "ordem": f.ordem
    } for f in faixas]

@api_router.post("/contabilidade/simples-faixas")
def criar_simples_faixa(faixa_data: dict, db: Session = Depends(get_db)):
    """Cria uma nova faixa do Simples."""
    from datetime import date as date_type
    from datetime import datetime
    
    # Converter strings de data
    if "vigencia_inicio" in faixa_data and isinstance(faixa_data["vigencia_inicio"], str):
        faixa_data["vigencia_inicio"] = datetime.strptime(faixa_data["vigencia_inicio"], "%Y-%m-%d").date()
    if "vigencia_fim" in faixa_data and faixa_data["vigencia_fim"] and isinstance(faixa_data["vigencia_fim"], str):
        faixa_data["vigencia_fim"] = datetime.strptime(faixa_data["vigencia_fim"], "%Y-%m-%d").date()
    
    faixa = crud_contabilidade.create_simples_faixa(db, faixa_data)
    return {
        "id": faixa.id,
        "limite_superior": faixa.limite_superior,
        "aliquota": faixa.aliquota,
        "deducao": faixa.deducao,
        "vigencia_inicio": str(faixa.vigencia_inicio),
        "vigencia_fim": str(faixa.vigencia_fim) if faixa.vigencia_fim else None,
        "ordem": faixa.ordem
    }

@api_router.put("/contabilidade/simples-faixas/{faixa_id}")
def atualizar_simples_faixa(faixa_id: int, faixa_data: dict, db: Session = Depends(get_db)):
    """Atualiza uma faixa do Simples."""
    from datetime import datetime
    
    # Converter strings de data
    if "vigencia_inicio" in faixa_data and isinstance(faixa_data["vigencia_inicio"], str):
        faixa_data["vigencia_inicio"] = datetime.strptime(faixa_data["vigencia_inicio"], "%Y-%m-%d").date()
    if "vigencia_fim" in faixa_data and faixa_data["vigencia_fim"] and isinstance(faixa_data["vigencia_fim"], str):
        faixa_data["vigencia_fim"] = datetime.strptime(faixa_data["vigencia_fim"], "%Y-%m-%d").date()
    
    faixa = crud_contabilidade.update_simples_faixa(db, faixa_id, faixa_data)
    if not faixa:
        raise HTTPException(status_code=404, detail="Faixa não encontrada")
    return {
        "id": faixa.id,
        "limite_superior": faixa.limite_superior,
        "aliquota": faixa.aliquota,
        "deducao": faixa.deducao,
        "vigencia_inicio": str(faixa.vigencia_inicio),
        "vigencia_fim": str(faixa.vigencia_fim) if faixa.vigencia_fim else None,
        "ordem": faixa.ordem
    }

@api_router.delete("/contabilidade/simples-faixas/{faixa_id}")
def deletar_simples_faixa(faixa_id: int, db: Session = Depends(get_db)):
    """Deleta uma faixa do Simples."""
    sucesso = crud_contabilidade.delete_simples_faixa(db, faixa_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Faixa não encontrada")
    return {"status": "ok"}

@api_router.post("/contabilidade/simples-faixas/inicializar")
def inicializar_faixas_simples_endpoint(db: Session = Depends(get_db)):
    """Inicializa as faixas padrão do Simples Nacional (2025)."""
    from datetime import date
    from utils.simples import inicializar_faixas_simples
    
    try:
        data_vigencia = date(2025, 1, 1)
        inicializar_faixas_simples(db, data_vigencia)
        return {"status": "ok", "message": "Faixas do Simples inicializadas com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
    p = crud_processos.buscar_processo(db, processo_id)
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
    p = crud_processos.atualizar_processo(db, processo_id, processo.model_dump(exclude_unset=True))
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
app.include_router(config_router)
