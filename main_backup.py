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
from backend.main import app as backend_app
from backend.main import api_router, config_router

# Registrar os roteadores
app.include_router(api_router)
app.include_router(config_router)

print("✓ Roteadores registrados")
print("✓ GESTOR_LS pronto! Escutando em http://localhost:8000")

    subtipo_pj: str | None = None
    capacidade: str | None = None
    responsavel_nome: str | None = None
    responsavel_cpf: str | None = None
    telefone: str | None = None
    email: str | None = None
    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    uf: str | None = None
    cep: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
        # Evita que a relação 'processos' seja incluída na serialização, prevenindo erros de referência circular ou de dados.
        exclude={'processos'}
    )

class ClienteCreateSchema(BaseModel):
    nome: str
    cpf_cnpj: str
    nome_fantasia: str | None = None
    tipo_pessoa: str | None = None
    tipo_pj: str | None = None
    subtipo_pj: str | None = None
    capacidade: str | None = None
    responsavel_nome: str | None = None
    responsavel_cpf: str | None = None
    telefone: str | None = None
    email: str | None = None
    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    uf: str | None = None
    cep: str | None = None

class ClienteUpdateSchema(BaseModel):
    nome: str | None = None
    cpf_cnpj: str | None = None
    nome_fantasia: str | None = None
    tipo_pessoa: str | None = None
    tipo_pj: str | None = None
    subtipo_pj: str | None = None
    capacidade: str | None = None
    responsavel_nome: str | None = None
    responsavel_cpf: str | None = None
    telefone: str | None = None
    email: str | None = None
    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    uf: str | None = None
    cep: str | None = None

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
    uf: UFsEnum | None = None
    categoria: CategoriaEnum | None = None
    tribunal_originario: TribunalOriginarioEnum | None = None
    esfera_justica: EsferaJusticaEnum | None = None
    tipo: TipoProcessoEnum | None = None
    comarca: str | None = None
    vara: str | None = None
    fase: str | None = None
    status: str | None = None
    data_abertura: str | None = None
    classe: str | None = None
    sub_classe: str | None = None
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

# --- Endpoints de Configuração ---

@app.get("/api/config/ufs", response_model=List[str])
def api_listar_ufs():
    """Retorna a lista de todas as UFs do Brasil."""
    return [uf.value for uf in UFsEnum]

@app.get("/api/config/tipos", response_model=List[str])
def api_listar_tipos():
    """Retorna os tipos de processo."""
    return [tipo.value for tipo in TipoProcessoEnum]

@app.get("/api/config/categorias", response_model=List[str])
def api_listar_categorias():
    """Retorna as categorias de processo (Comum, Originário)."""
    return [cat.value for cat in CategoriaEnum]

@app.get("/api/config/tribunais", response_model=List[str])
def api_listar_tribunais():
    """Retorna a lista de tribunais para processos originários."""
    return [trib.value for trib in TribunalOriginarioEnum]

@app.get("/api/config/esferas", response_model=List[str])
def api_listar_esferas():
    """Retorna as esferas de justiça (Federal, Estadual)."""
    return [esfera.value for esfera in EsferaJusticaEnum]

@app.get("/api/config/classes", response_model=dict)
def api_listar_classes():
    """Retorna a estrutura de classes e sub-classes jurídicas."""
    return {
        "Cível": ["Comum", "Juizado Especial", "Família", "Inventário"],
        "Criminal": ["Ação Privada", "Ação Pública"],
        "Trabalhista": [], # Confirmando que não há sub-classes
        "Tributário": [],
        "Empresarial": [],
        "Previdenciário": [],
        "Eleitoral": ["Eleitoral Cível", "Eleitoral Criminal"]
    }

# --- Endpoints de Processos ---

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
    """Endpoint para buscar um processo específico pelo ID."""
    db_processo = crud_processos.buscar_processo(db, processo_id=processo_id)
    if db_processo is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return db_processo

@app.put("/api/processos/{processo_id}", response_model=ProcessoSchema)
def api_atualizar_processo(processo_id: int, processo: ProcessoCreateSchema, db: Session = Depends(get_db)): # O schema aqui está para a entrada de dados
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

@app.post("/api/clientes", response_model=ClienteSchema, status_code=201)
def api_criar_cliente(cliente: ClienteCreateSchema, db: Session = Depends(get_db)):
    """Endpoint para criar um novo cliente."""
    return crud_clientes.criar_cliente(db=db, **cliente.model_dump())

@app.get("/api/clientes/{cliente_id}", response_model=ClienteSchema)
def api_buscar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Endpoint para buscar um cliente específico."""
    db_cliente = crud_clientes.buscar_cliente(db, cliente_id=cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return db_cliente

@app.put("/api/clientes/{cliente_id}", response_model=ClienteSchema)
def api_atualizar_cliente(cliente_id: int, cliente: ClienteUpdateSchema, db: Session = Depends(get_db)):
    """Endpoint para atualizar um cliente."""
    return crud_clientes.atualizar_cliente(db=db, cliente_id=cliente_id, **cliente.model_dump(exclude_unset=True))

@app.delete("/api/clientes/{cliente_id}", status_code=204)
def api_deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    crud_clientes.deletar_cliente(db=db, cliente_id=cliente_id)
    return {"ok": True}

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


# --- Endpoints de Contabilidade ---

# Endpoints para Socios
@app.post("/api/contabilidade/socios", response_model=schemas.Socio, status_code=201)
def api_criar_socio(socio: schemas.SocioCreate, db: Session = Depends(get_db)):
    return crud_contabilidade.create_socio(db=db, socio=socio)

@app.get("/api/contabilidade/socios", response_model=List[schemas.Socio])
def api_listar_socios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    socios = crud_contabilidade.get_socios(db, skip=skip, limit=limit)
    return socios

@app.get("/api/contabilidade/socios/{socio_id}", response_model=schemas.Socio)
def api_buscar_socio(socio_id: int, db: Session = Depends(get_db)):
    db_socio = crud_contabilidade.get_socio(db, socio_id=socio_id)
    if db_socio is None:
        raise HTTPException(status_code=404, detail="Sócio não encontrado")
    return db_socio

@app.put("/api/contabilidade/socios/{socio_id}", response_model=schemas.Socio)
def api_atualizar_socio(socio_id: int, socio: schemas.SocioUpdate, db: Session = Depends(get_db)):
    return crud_contabilidade.update_socio(db=db, socio_id=socio_id, socio_update=socio)

@app.delete("/api/contabilidade/socios/{socio_id}", status_code=204)
def api_deletar_socio(socio_id: int, db: Session = Depends(get_db)):
    crud_contabilidade.delete_socio(db=db, socio_id=socio_id)
    return {"ok": True}

# Aporte de Capital do Sócio
@app.post("/api/contabilidade/socios/{socio_id}/aportes")
def api_aporte_capital(
    socio_id: int,
    aporte: schemas.AporteCapitalCreate,
    db: Session = Depends(get_db)
):
    try:
        return crud_contabilidade.registrar_aporte_capital(
            db=db,
            socio_id=socio_id,
            valor=aporte.valor,
            data=aporte.data,
            forma=aporte.forma
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoints para Entradas
@app.post("/api/contabilidade/entradas", response_model=schemas.Entrada, status_code=201)
def api_criar_entrada(entrada: schemas.EntradaCreate, db: Session = Depends(get_db)):
    return crud_contabilidade.create_entrada(db=db, entrada=entrada)

@app.get("/api/contabilidade/entradas", response_model=List[schemas.Entrada])
def api_listar_entradas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    entradas = crud_contabilidade.get_entradas(db, skip=skip, limit=limit)
    return entradas

# Endpoints para Despesas
@app.post("/api/contabilidade/despesas", response_model=schemas.Despesa, status_code=201)
def api_criar_despesa(despesa: schemas.DespesaCreate, db: Session = Depends(get_db)):
    return crud_contabilidade.create_despesa(db=db, despesa=despesa)

@app.get("/api/contabilidade/despesas", response_model=List[schemas.Despesa])
def api_listar_despesas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    despesas = crud_contabilidade.get_despesas(db, skip=skip, limit=limit)
    return despesas

# --- Endpoints de Feriados ---

@app.get("/api/feriados", response_model=List[schemas.FeriadoResponse])
def listar_feriados(
    tipo: Optional[str] = None,
    uf: Optional[str] = None,
    municipio_id: Optional[int] = None,
    ano: Optional[int] = None,
    data_inicio: Optional[date_type] = None,
    data_fim: Optional[date_type] = None,
    db: Session = Depends(get_db)
):
    """
    Lista feriados com filtros opcionais.
    Query params: tipo, uf, municipio_id, ano, data_inicio, data_fim
    """
    return crud_feriados.listar_feriados(
        db, tipo=tipo, uf=uf, municipio_id=municipio_id,
        ano=ano, data_inicio=data_inicio, data_fim=data_fim
    )

@app.get("/api/feriados/{feriado_id}", response_model=schemas.FeriadoResponse)
def buscar_feriado(feriado_id: int, db: Session = Depends(get_db)):
    """Busca um feriado por ID."""
    feriado = crud_feriados.buscar_feriado_por_id(feriado_id, db)
    if not feriado:
        raise HTTPException(status_code=404, detail="Feriado não encontrado")
    return feriado

@app.post("/api/feriados", response_model=schemas.FeriadoResponse)
def criar_feriado(feriado: schemas.FeriadoCreate, db: Session = Depends(get_db)):
    """Cria um novo feriado."""
    try:
        return crud_feriados.criar_feriado(
            db=db,
            nome=feriado.nome,
            data=feriado.data,
            tipo=feriado.tipo,
            uf=feriado.uf,
            municipio_id=feriado.municipio_id,
            recorrente_anual=feriado.recorrente_anual
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/feriados/{feriado_id}", response_model=schemas.FeriadoResponse)
def atualizar_feriado(feriado_id: int, feriado: schemas.FeriadoUpdate, db: Session = Depends(get_db)):
    """Atualiza um feriado existente."""
    try:
        updated = crud_feriados.atualizar_feriado(
            feriado_id, db, 
            nome=feriado.nome,
            data=feriado.data,
            tipo=feriado.tipo,
            uf=feriado.uf,
            municipio_id=feriado.municipio_id,
            recorrente_anual=feriado.recorrente_anual
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Feriado não encontrado")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/feriados/{feriado_id}", status_code=204)
def deletar_feriado(feriado_id: int, db: Session = Depends(get_db)):
    """Deleta um feriado."""
    sucesso = crud_feriados.deletar_feriado(feriado_id, db)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Feriado não encontrado")

# --- Endpoint de UFs para configuração ---

@app.get("/api/config/ufs")
def get_ufs():
    """Retorna lista de UFs brasileiras."""
    return ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
            "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", 
            "RS", "RO", "RR", "SC", "SP", "SE", "TO"]

# --- Endpoints de Municípios ---

@app.get("/api/municipios", response_model=List[schemas.MunicipioResponse])
def listar_municipios(db: Session = Depends(get_db)):
    """Lista todos os municípios cadastrados."""
    return crud_municipios.listar_municipios(db)

@app.get("/api/municipios/uf/{uf}", response_model=List[schemas.MunicipioResponse])
def listar_municipios_por_uf(uf: str, db: Session = Depends(get_db)):
    """Lista municípios de uma UF específica."""
    municipios = crud_municipios.listar_municipios_por_uf(uf, db)
    if not municipios:
        raise HTTPException(status_code=404, detail=f"Nenhum município encontrado para UF: {uf}")
    return municipios

@app.get("/api/municipios/{municipio_id}", response_model=schemas.MunicipioResponse)
def buscar_municipio(municipio_id: int, db: Session = Depends(get_db)):
    """Busca um município por ID."""
    municipio = crud_municipios.buscar_municipio_por_id(municipio_id, db)
    if not municipio:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    return municipio

# --- Servir o Frontend (React) ---
# Esta linha faz com que o FastAPI sirva os arquivos da pasta 'build' do seu app React.
# Descomente a linha abaixo apenas quando for fazer o deploy para produção.
# app.mount("/", StaticFiles(directory="frontend/react-app/build", html=True), name="static")
