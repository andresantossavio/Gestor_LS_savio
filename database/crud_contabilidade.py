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

# =================================================================
# Recebimentos + Participações
# =================================================================

def criar_recebimento_com_participacoes(
    db: Session,
    cliente_nome: Optional[str],
    data,
    valor_centavos: Optional[int],
    participacoes: List[dict],
    observacao: Optional[str] = None,
):
    rec = models.Recebimento(cliente_nome=cliente_nome, data=data, valor_centavos=valor_centavos, observacao=observacao)
    db.add(rec)
    db.flush()

    for p in participacoes or []:
        nome = p.get("socio_nome")
        usuario = None
        if nome:
            usuario = db.query(models.Usuario).filter(models.Usuario.nome.ilike(nome)).first()
        part = models.ParticipacaoSocio(
            recebimento_id=rec.id,
            usuario_id=usuario.id if usuario else None,
            socio_nome=nome,
            percentual_mil=p.get("percentual_mil") or 0,
        )
        db.add(part)

    db.commit()
    db.refresh(rec)
    return rec

def listar_recebimentos(db: Session) -> List[models.Recebimento]:
    return db.query(models.Recebimento).all()

# =================================================================
# CRUD for SimplesFaixa
# =================================================================

def create_simples_faixa(db: Session, faixa_data: dict) -> models.SimplesFaixa:
    """Cria uma nova faixa do Simples Nacional."""
    db_faixa = models.SimplesFaixa(**faixa_data)
    db.add(db_faixa)
    db.commit()
    db.refresh(db_faixa)
    return db_faixa

def get_simples_faixas_vigentes(db: Session, data_ref) -> List[models.SimplesFaixa]:
    """Busca faixas vigentes em uma data específica, ordenadas."""
    from datetime import date as date_type
    if isinstance(data_ref, str):
        from utils.datas import parse_mes
        data_ref = parse_mes(data_ref)
    
    return db.query(models.SimplesFaixa).filter(
        models.SimplesFaixa.vigencia_inicio <= data_ref,
        (models.SimplesFaixa.vigencia_fim.is_(None)) | (models.SimplesFaixa.vigencia_fim >= data_ref)
    ).order_by(models.SimplesFaixa.ordem).all()

def get_all_simples_faixas(db: Session) -> List[models.SimplesFaixa]:
    """Busca todas as faixas configuradas."""
    return db.query(models.SimplesFaixa).order_by(
        models.SimplesFaixa.vigencia_inicio.desc(),
        models.SimplesFaixa.ordem
    ).all()

def update_simples_faixa(db: Session, faixa_id: int, faixa_data: dict) -> Optional[models.SimplesFaixa]:
    """Atualiza uma faixa do Simples."""
    db_faixa = db.query(models.SimplesFaixa).filter(models.SimplesFaixa.id == faixa_id).first()
    if db_faixa:
        for key, value in faixa_data.items():
            setattr(db_faixa, key, value)
        db.commit()
        db.refresh(db_faixa)
    return db_faixa

def delete_simples_faixa(db: Session, faixa_id: int) -> bool:
    """Deleta uma faixa do Simples."""
    db_faixa = db.query(models.SimplesFaixa).filter(models.SimplesFaixa.id == faixa_id).first()
    if db_faixa:
        db.delete(db_faixa)
        db.commit()
        return True
    return False

# =================================================================
# CRUD e cálculo para DREMensal
# =================================================================

def consolidar_dre_mes(db: Session, mes: str, forcar_recalculo: bool = False) -> models.DREMensal:
    """
    Consolida ou recalcula a DRE de um mês específico (YYYY-MM).
    
    Args:
        db: Sessão do banco
        mes: Mês no formato YYYY-MM
        forcar_recalculo: Se True, recalcula mesmo se já consolidado
    
    Returns:
        DREMensal consolidado
    """
    from utils.datas import ultimos_12_meses, inicio_do_mes, fim_do_mes
    from utils.simples import calcular_faixa_simples, calcular_imposto_simples
    from sqlalchemy import func
    from datetime import datetime
    
    # Verificar se já existe e se está consolidado
    dre_existente = db.query(models.DREMensal).filter(models.DREMensal.mes == mes).first()
    if dre_existente and dre_existente.consolidado and not forcar_recalculo:
        return dre_existente
    
    inicio = inicio_do_mes(mes)
    fim = fim_do_mes(mes)
    
    # 1. Calcular receita bruta do mês
    receita_bruta = db.query(func.sum(models.Entrada.valor)).filter(
        models.Entrada.data >= inicio,
        models.Entrada.data <= fim
    ).scalar() or 0.0
    
    # 2. Calcular receita acumulada 12 meses
    meses_12 = ultimos_12_meses(mes)
    receita_12m = 0.0
    for mes_ant in meses_12:
        inicio_ant = inicio_do_mes(mes_ant)
        fim_ant = fim_do_mes(mes_ant)
        receita_mes_ant = db.query(func.sum(models.Entrada.valor)).filter(
            models.Entrada.data >= inicio_ant,
            models.Entrada.data <= fim_ant
        ).scalar() or 0.0
        receita_12m += receita_mes_ant
    
    # 3. Calcular faixa Simples e alíquotas
    try:
        aliquota, deducao, aliquota_efetiva = calcular_faixa_simples(receita_12m, inicio, db)
    except ValueError as e:
        # Fora do Simples ou sem faixas configuradas
        aliquota = 0.0
        deducao = 0.0
        aliquota_efetiva = 0.0
    
    # 4. Calcular imposto do mês
    imposto = calcular_imposto_simples(receita_bruta, aliquota_efetiva)
    
    # 5. Calcular INSS patronal (20% sobre pró-labore)
    # TODO: Implementar cálculo iterativo do pró-labore de André
    # Por ora, deixar zerado (será preenchido pelo endpoint de pró-labore)
    inss_patronal = 0.0
    
    # 6. Calcular despesas gerais do mês
    despesas_gerais = db.query(func.sum(models.Despesa.valor)).filter(
        models.Despesa.data >= inicio,
        models.Despesa.data <= fim
    ).scalar() or 0.0
    
    # 7. Calcular lucro líquido
    lucro_liquido = receita_bruta - imposto - inss_patronal - despesas_gerais
    
    # 8. Calcular reserva 10%
    reserva_10p = lucro_liquido * 0.10
    
    # 9. Salvar ou atualizar DRE
    if dre_existente:
        dre_existente.receita_bruta = receita_bruta
        dre_existente.receita_12m = receita_12m
        dre_existente.aliquota = aliquota
        dre_existente.aliquota_efetiva = aliquota_efetiva
        dre_existente.deducao = deducao
        dre_existente.imposto = imposto
        dre_existente.inss_patronal = inss_patronal
        dre_existente.despesas_gerais = despesas_gerais
        dre_existente.lucro_liquido = lucro_liquido
        dre_existente.reserva_10p = reserva_10p
        dre_existente.consolidado = True
        dre_existente.data_consolidacao = datetime.utcnow()
        db_dre = dre_existente
    else:
        db_dre = models.DREMensal(
            mes=mes,
            receita_bruta=receita_bruta,
            receita_12m=receita_12m,
            aliquota=aliquota,
            aliquota_efetiva=aliquota_efetiva,
            deducao=deducao,
            imposto=imposto,
            inss_patronal=inss_patronal,
            despesas_gerais=despesas_gerais,
            lucro_liquido=lucro_liquido,
            reserva_10p=reserva_10p,
            consolidado=True,
            data_consolidacao=datetime.utcnow()
        )
        db.add(db_dre)
    
    db.commit()
    db.refresh(db_dre)
    return db_dre

def desconsolidar_dre_mes(db: Session, mes: str) -> Optional[models.DREMensal]:
    """
    Desconsolida um mês de DRE, permitindo recalcular posteriormente.
    
    Args:
        db: Sessão do banco
        mes: Mês no formato YYYY-MM
    
    Returns:
        DREMensal desconsolidado ou None se não existir
    """
    dre = db.query(models.DREMensal).filter(models.DREMensal.mes == mes).first()
    if dre:
        dre.consolidado = False
        dre.data_consolidacao = None
        db.commit()
        db.refresh(dre)
    return dre

def get_dre_mensal(db: Session, mes: str) -> Optional[models.DREMensal]:
    """Busca DRE de um mês específico."""
    return db.query(models.DREMensal).filter(models.DREMensal.mes == mes).first()

def get_dre_ano(db: Session, ano: int) -> List[models.DREMensal]:
    """Busca DRE de todos os meses de um ano."""
    from utils.datas import meses_do_ano
    meses = meses_do_ano(ano)
    return db.query(models.DREMensal).filter(models.DREMensal.mes.in_(meses)).order_by(models.DREMensal.mes).all()
