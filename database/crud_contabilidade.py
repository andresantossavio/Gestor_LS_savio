from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from . import models
from backend import schemas

# =================================================================
# CRUD for ConfiguracaoContabil
# =================================================================

def get_configuracao(db: Session) -> models.ConfiguracaoContabil:
    """Pega a primeira configuração encontrada ou cria uma com valores padrão."""
    config = db.query(models.ConfiguracaoContabil).first()
    if not config:
        config = models.ConfiguracaoContabil()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

# =================================================================
# CRUD for Fundo
# =================================================================

def get_or_create_fundo(db: Session, nome: str) -> models.Fundo:
    """Pega um fundo pelo nome ou cria se não existir."""
    fundo = db.query(models.Fundo).filter(models.Fundo.nome == nome).first()
    if not fundo:
        fundo = models.Fundo(nome=nome, saldo=0.0)
        db.add(fundo)
        db.commit()
        db.refresh(fundo)
    return fundo

# =================================================================
# CRUD for Socio
# =================================================================

def create_socio(db: Session, socio: schemas.SocioCreate) -> models.Socio:
    """Cria um novo sócio no banco de dados."""
    db_socio = models.Socio(**socio.dict())
    db.add(db_socio)
    db.commit()
    db.refresh(db_socio)
    return db_socio

def get_socio(db: Session, socio_id: int) -> Optional[models.Socio]:
    """Busca um sócio pelo ID."""
    return db.query(models.Socio).filter(models.Socio.id == socio_id).first()

def get_socios(db: Session, skip: int = 0, limit: int = 100) -> List[models.Socio]:
    """Busca todos os sócios com paginação."""
    return db.query(models.Socio).offset(skip).limit(limit).all()

def update_socio(db: Session, socio_id: int, socio_update: schemas.SocioUpdate) -> Optional[models.Socio]:
    """Atualiza um sócio existente."""
    db_socio = get_socio(db, socio_id)
    if db_socio:
        update_data = socio_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_socio, key, value)
        db.commit()
        db.refresh(db_socio)
    return db_socio

def delete_socio(db: Session, socio_id: int) -> Optional[models.Socio]:
    """Deleta um sócio."""
    db_socio = get_socio(db, socio_id)
    if db_socio:
        db.delete(db_socio)
        db.commit()
    return db_socio

# =================================================================
# CRUD for Entrada (with business logic)
# =================================================================

def create_entrada(db: Session, entrada: schemas.EntradaCreate) -> models.Entrada:
    """
    Cria uma nova entrada, distribui os valores para o administrador,
    fundo de reserva e sócios, e atualiza os saldos.
    """
    config = get_configuracao(db)
    # Suposição: O primeiro sócio com 'Administrador' na função é o admin.
    admin_socio = db.query(models.Socio).filter(models.Socio.funcao.ilike('%administrador%')).first()

    valor_total = entrada.valor
    valor_admin = valor_total * config.percentual_administrador
    valor_fundo = valor_total * config.percentual_fundo_reserva
    valor_restante = valor_total - valor_admin - valor_fundo

    fundo_reserva = get_or_create_fundo(db, nome="Fundo de Reserva")
    fundo_reserva.saldo += valor_fundo

    if admin_socio:
        admin_socio.saldo += valor_admin
    
    entrada_data = entrada.dict(exclude={'socios'})
    db_entrada = models.Entrada(**entrada_data)
    db.add(db_entrada)
    db.flush() # Use flush to get the db_entrada.id before commit

    for socio_assoc_data in entrada.socios:
        socio = get_socio(db, socio_id=socio_assoc_data.socio_id)
        if socio:
            valor_socio = valor_restante * socio_assoc_data.percentual
            socio.saldo += valor_socio
        
        db_assoc = models.EntradaSocio(
            entrada_id=db_entrada.id,
            socio_id=socio_assoc_data.socio_id,
            percentual=socio_assoc_data.percentual
        )
        db.add(db_assoc)

    db.commit()
    db.refresh(db_entrada)
    return db_entrada

def get_entradas(db: Session, skip: int = 0, limit: int = 100) -> List[models.Entrada]:
    """Busca todas as entradas com os sócios relacionados."""
    return db.query(models.Entrada).options(joinedload(models.Entrada.socios)).offset(skip).limit(limit).all()

# =================================================================
# CRUD for Despesa (with business logic)
# =================================================================

def create_despesa(db: Session, despesa: schemas.DespesaCreate) -> models.Despesa:
    """
    Cria uma nova despesa e deduz o valor do saldo dos sócios responsáveis.
    """
    despesa_data = despesa.dict(exclude={'responsaveis'})
    db_despesa = models.Despesa(**despesa_data)
    db.add(db_despesa)
    db.flush() # Get ID before commit

    num_responsaveis = len(despesa.responsaveis)
    if num_responsaveis > 0:
        valor_por_responsavel = despesa.valor / num_responsaveis
        
        for resp_assoc_data in despesa.responsaveis:
            socio = get_socio(db, socio_id=resp_assoc_data.socio_id)
            if socio:
                socio.saldo -= valor_por_responsavel
            
            db_assoc = models.DespesaSocio(
                despesa_id=db_despesa.id,
                socio_id=resp_assoc_data.socio_id
            )
            db.add(db_assoc)

    db.commit()
    db.refresh(db_despesa)
    return db_despesa

def get_despesas(db: Session, skip: int = 0, limit: int = 100) -> List[models.Despesa]:
    """Busca todas as despesas com os responsáveis relacionados."""
    return db.query(models.Despesa).options(joinedload(models.Despesa.responsaveis)).offset(skip).limit(limit).all()

# =================================================================
# CRUD for PlanoDeContas
# =================================================================

def create_plano_de_contas(db: Session, plano_de_contas: schemas.PlanoDeContasCreate) -> models.PlanoDeContas:
    """Cria uma nova conta no plano de contas."""
    db_plano = models.PlanoDeContas(**plano_de_contas.dict())
    db.add(db_plano)
    db.commit()
    db.refresh(db_plano)
    return db_plano

def get_plano_de_contas(db: Session, skip: int = 0, limit: int = 100) -> List[models.PlanoDeContas]:
    """Busca todas as contas do plano de contas."""
    return db.query(models.PlanoDeContas).offset(skip).limit(limit).all()

# =================================================================
# CRUD for LancamentoContabil
# =================================================================

def create_lancamento_contabil(db: Session, lancamento: schemas.LancamentoContabilCreate) -> models.LancamentoContabil:
    """Cria um novo lançamento contábil."""
    db_lancamento = models.LancamentoContabil(**lancamento.dict())
    db.add(db_lancamento)
    db.commit()
    db.refresh(db_lancamento)
    return db_lancamento

def get_lancamentos_contabeis(db: Session, skip: int = 0, limit: int = 100) -> List[models.LancamentoContabil]:
    """Busca todos os lançamentos contábeis."""
    return db.query(models.LancamentoContabil).offset(skip).limit(limit).all()
