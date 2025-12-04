"""
CRUD operations para Contabilidade (Sócios, Entradas, Despesas, Operações)
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from database import models
from database import crud_plano_contas
from typing import List, Optional, Dict, Any
from datetime import date as date_type, datetime, timedelta
from decimal import Decimal


# ==================== SÓCIOS ====================

def get_socios(db: Session, skip: int = 0, limit: int = 100) -> List[models.Socio]:
    """Lista todos os sócios"""
    return db.query(models.Socio).offset(skip).limit(limit).all()


def get_socio(db: Session, socio_id: int) -> Optional[models.Socio]:
    """Busca um sócio por ID"""
    return db.query(models.Socio).filter(models.Socio.id == socio_id).first()


def create_socio(db: Session, socio: Any) -> models.Socio:
    """Cria um novo sócio"""
    db_socio = models.Socio(
        nome=socio.nome,
        usuario_id=socio.usuario_id,
        funcao=socio.funcao,
        capital_social=socio.capital_social or 0.0,
        percentual=socio.percentual or 0.0,
        saldo=0.0
    )
    db.add(db_socio)
    db.commit()
    db.refresh(db_socio)
    return db_socio


def update_socio(db: Session, socio_id: int, socio: Any) -> Optional[models.Socio]:
    """Atualiza um sócio existente"""
    db_socio = get_socio(db, socio_id)
    if not db_socio:
        return None
    
    if socio.nome is not None:
        db_socio.nome = socio.nome
    if socio.usuario_id is not None:
        db_socio.usuario_id = socio.usuario_id
    if socio.funcao is not None:
        db_socio.funcao = socio.funcao
    if socio.capital_social is not None:
        db_socio.capital_social = socio.capital_social
    if socio.percentual is not None:
        db_socio.percentual = socio.percentual
    
    db.commit()
    db.refresh(db_socio)
    return db_socio


def delete_socio(db: Session, socio_id: int) -> bool:
    """Deleta um sócio"""
    db_socio = get_socio(db, socio_id)
    if not db_socio:
        return False
    
    db.delete(db_socio)
    db.commit()
    return True


# ==================== APORTES DE CAPITAL ====================

def create_aporte_capital(db: Session, socio_id: int, aporte: Any) -> models.AporteCapital:
    """Registra um aporte de capital"""
    db_aporte = models.AporteCapital(
        socio_id=socio_id,
        data=aporte.data,
        valor=aporte.valor,
        tipo_aporte=aporte.tipo_aporte,
        descricao=aporte.descricao
    )
    db.add(db_aporte)
    db.commit()
    db.refresh(db_aporte)
    
    # Atualizar capital social do sócio se for aporte de dinheiro ou bens
    if aporte.tipo_aporte in ['dinheiro', 'bens', 'servicos']:
        socio = get_socio(db, socio_id)
        if socio:
            socio.capital_social = (socio.capital_social or 0) + aporte.valor
            db.commit()
    
    return db_aporte


def get_aportes_socio(db: Session, socio_id: int) -> List[models.AporteCapital]:
    """Lista todos os aportes de um sócio"""
    return db.query(models.AporteCapital).filter(
        models.AporteCapital.socio_id == socio_id
    ).order_by(models.AporteCapital.data.desc()).all()


def get_aporte(db: Session, aporte_id: int) -> Optional[models.AporteCapital]:
    """Busca um aporte por ID"""
    return db.query(models.AporteCapital).filter(models.AporteCapital.id == aporte_id).first()


def update_aporte_capital(db: Session, aporte_id: int, update_data: Any) -> Optional[models.AporteCapital]:
    """Atualiza um aporte de capital"""
    db_aporte = get_aporte(db, aporte_id)
    if not db_aporte:
        return None
    
    valor_antigo = db_aporte.valor
    tipo_antigo = db_aporte.tipo_aporte
    
    if update_data.data is not None:
        db_aporte.data = update_data.data
    if update_data.valor is not None:
        db_aporte.valor = update_data.valor
    if update_data.tipo_aporte is not None:
        db_aporte.tipo_aporte = update_data.tipo_aporte
    if update_data.descricao is not None:
        db_aporte.descricao = update_data.descricao
    
    db_aporte.atualizado_em = datetime.utcnow()
    
    # Ajustar capital social se mudou valor ou tipo
    if tipo_antigo in ['dinheiro', 'bens', 'servicos']:
        socio = get_socio(db, db_aporte.socio_id)
        if socio:
            socio.capital_social = (socio.capital_social or 0) - valor_antigo
            if db_aporte.tipo_aporte in ['dinheiro', 'bens', 'servicos']:
                socio.capital_social += db_aporte.valor
    
    db.commit()
    db.refresh(db_aporte)
    return db_aporte


def delete_aporte_capital(db: Session, aporte_id: int) -> bool:
    """Deleta um aporte de capital"""
    db_aporte = get_aporte(db, aporte_id)
    if not db_aporte:
        return False
    
    # Ajustar capital social
    if db_aporte.tipo_aporte in ['dinheiro', 'bens', 'servicos']:
        socio = get_socio(db, db_aporte.socio_id)
        if socio:
            socio.capital_social = (socio.capital_social or 0) - db_aporte.valor
    
    db.delete(db_aporte)
    db.commit()
    return True


def get_relatorio_integralizacao(db: Session) -> Dict[str, Any]:
    """Gera relatório de integralização de capital"""
    socios = get_socios(db)
    resultado = []
    total_geral = 0.0
    
    for socio in socios:
        aportes = get_aportes_socio(db, socio.id)
        total_aportado = sum(a.valor for a in aportes if a.tipo_aporte in ['dinheiro', 'bens', 'servicos'])
        total_retirado = sum(a.valor for a in aportes if a.tipo_aporte == 'retirada')
        saldo = total_aportado - total_retirado
        
        resultado.append({
            "socio_id": socio.id,
            "socio_nome": socio.nome,
            "capital_social": socio.capital_social or 0,
            "total_aportado": total_aportado,
            "total_retirado": total_retirado,
            "saldo": saldo
        })
        total_geral += saldo
    
    return {
        "socios": resultado,
        "total_geral": total_geral
    }


# ==================== ENTRADAS ====================

def create_entrada(db: Session, entrada: Any) -> models.Entrada:
    """Cria uma nova entrada de honorários"""
    db_entrada = models.Entrada(
        cliente=entrada.cliente,
        cliente_id=entrada.cliente_id,
        data=entrada.data,
        valor=entrada.valor
    )
    db.add(db_entrada)
    db.flush()
    
    # Adicionar sócios e seus percentuais
    for socio_data in entrada.socios:
        entrada_socio = models.EntradaSocio(
            entrada_id=db_entrada.id,
            socio_id=socio_data.socio_id,
            percentual=socio_data.percentual
        )
        db.add(entrada_socio)
    
    db.commit()
    db.refresh(db_entrada)
    return db_entrada


def get_entrada(db: Session, entrada_id: int) -> Optional[models.Entrada]:
    """Busca uma entrada por ID"""
    return db.query(models.Entrada).filter(models.Entrada.id == entrada_id).first()


def get_entradas(db: Session, skip: int = 0, limit: int = 1000) -> List[models.Entrada]:
    """Lista todas as entradas"""
    return db.query(models.Entrada).order_by(models.Entrada.data.desc()).offset(skip).limit(limit).all()


def update_entrada(db: Session, entrada_id: int, entrada: Any) -> Optional[models.Entrada]:
    """Atualiza uma entrada existente"""
    db_entrada = get_entrada(db, entrada_id)
    if not db_entrada:
        return None
    
    db_entrada.cliente = entrada.cliente
    db_entrada.cliente_id = entrada.cliente_id
    db_entrada.data = entrada.data
    db_entrada.valor = entrada.valor
    
    # Atualizar sócios
    db.query(models.EntradaSocio).filter(
        models.EntradaSocio.entrada_id == entrada_id
    ).delete()
    
    for socio_data in entrada.socios:
        entrada_socio = models.EntradaSocio(
            entrada_id=entrada_id,
            socio_id=socio_data.socio_id,
            percentual=socio_data.percentual
        )
        db.add(entrada_socio)
    
    db.commit()
    db.refresh(db_entrada)
    return db_entrada


def delete_entrada(db: Session, entrada_id: int) -> bool:
    """Deleta uma entrada"""
    db_entrada = get_entrada(db, entrada_id)
    if not db_entrada:
        return False
    
    db.delete(db_entrada)
    db.commit()
    return True


# ==================== DESPESAS ====================

def create_despesa(db: Session, despesa: Any) -> models.Despesa:
    """Cria uma nova despesa"""
    db_despesa = models.Despesa(
        data=despesa.data,
        especie=despesa.especie,
        tipo=despesa.tipo,
        descricao=despesa.descricao,
        valor=despesa.valor
    )
    db.add(db_despesa)
    db.flush()
    
    # Adicionar responsáveis
    for resp_data in despesa.responsaveis:
        despesa_socio = models.DespesaSocio(
            despesa_id=db_despesa.id,
            socio_id=resp_data.socio_id
        )
        db.add(despesa_socio)
    
    db.commit()
    db.refresh(db_despesa)
    return db_despesa


def get_despesa(db: Session, despesa_id: int) -> Optional[models.Despesa]:
    """Busca uma despesa por ID"""
    return db.query(models.Despesa).filter(models.Despesa.id == despesa_id).first()


def get_despesas(db: Session, skip: int = 0, limit: int = 1000) -> List[models.Despesa]:
    """Lista todas as despesas"""
    return db.query(models.Despesa).order_by(models.Despesa.data.desc()).offset(skip).limit(limit).all()


def update_despesa(db: Session, despesa_id: int, despesa: Any) -> Optional[models.Despesa]:
    """Atualiza uma despesa existente"""
    db_despesa = get_despesa(db, despesa_id)
    if not db_despesa:
        return None
    
    db_despesa.data = despesa.data
    db_despesa.especie = despesa.especie
    db_despesa.tipo = despesa.tipo
    db_despesa.descricao = despesa.descricao
    db_despesa.valor = despesa.valor
    
    # Atualizar responsáveis
    db.query(models.DespesaSocio).filter(
        models.DespesaSocio.despesa_id == despesa_id
    ).delete()
    
    for resp_data in despesa.responsaveis:
        despesa_socio = models.DespesaSocio(
            despesa_id=despesa_id,
            socio_id=resp_data.socio_id
        )
        db.add(despesa_socio)
    
    db.commit()
    db.refresh(db_despesa)
    return db_despesa


def delete_despesa(db: Session, despesa_id: int) -> bool:
    """Deleta uma despesa"""
    db_despesa = get_despesa(db, despesa_id)
    if not db_despesa:
        return False
    
    db.delete(db_despesa)
    db.commit()
    return True


# ==================== CONFIGURAÇÃO ====================

def get_configuracao(db: Session) -> Optional[models.ConfiguracaoContabil]:
    """Busca a configuração contábil"""
    config = db.query(models.ConfiguracaoContabil).first()
    if not config:
        # Criar configuração padrão
        config = models.ConfiguracaoContabil(
            percentual_administrador=0.05,
            percentual_fundo_reserva=0.10,
            salario_minimo=1518.0
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


# ==================== SIMPLES NACIONAL ====================

def get_all_simples_faixas(db: Session) -> List[models.SimplesFaixa]:
    """Lista todas as faixas do Simples Nacional vigentes"""
    return db.query(models.SimplesFaixa).filter(
        or_(
            models.SimplesFaixa.vigencia_fim.is_(None),
            models.SimplesFaixa.vigencia_fim >= datetime.now().date()
        )
    ).order_by(models.SimplesFaixa.ordem).all()


def create_simples_faixa(db: Session, faixa_data: Any) -> models.SimplesFaixa:
    """Cria uma nova faixa do Simples"""
    db_faixa = models.SimplesFaixa(
        limite_superior=faixa_data.limite_superior,
        aliquota=faixa_data.aliquota,
        deducao=faixa_data.deducao,
        vigencia_inicio=faixa_data.vigencia_inicio,
        vigencia_fim=faixa_data.vigencia_fim,
        ordem=faixa_data.ordem
    )
    db.add(db_faixa)
    db.commit()
    db.refresh(db_faixa)
    return db_faixa


def update_simples_faixa(db: Session, faixa_id: int, faixa_data: Any) -> Optional[models.SimplesFaixa]:
    """Atualiza uma faixa do Simples"""
    db_faixa = db.query(models.SimplesFaixa).filter(models.SimplesFaixa.id == faixa_id).first()
    if not db_faixa:
        return None
    
    if faixa_data.limite_superior is not None:
        db_faixa.limite_superior = faixa_data.limite_superior
    if faixa_data.aliquota is not None:
        db_faixa.aliquota = faixa_data.aliquota
    if faixa_data.deducao is not None:
        db_faixa.deducao = faixa_data.deducao
    if faixa_data.vigencia_inicio is not None:
        db_faixa.vigencia_inicio = faixa_data.vigencia_inicio
    if faixa_data.vigencia_fim is not None:
        db_faixa.vigencia_fim = faixa_data.vigencia_fim
    if faixa_data.ordem is not None:
        db_faixa.ordem = faixa_data.ordem
    
    db.commit()
    db.refresh(db_faixa)
    return db_faixa


def delete_simples_faixa(db: Session, faixa_id: int) -> bool:
    """Deleta uma faixa do Simples"""
    db_faixa = db.query(models.SimplesFaixa).filter(models.SimplesFaixa.id == faixa_id).first()
    if not db_faixa:
        return False
    
    db.delete(db_faixa)
    db.commit()
    return True


# ==================== VALIDAÇÃO EQUAÇÃO CONTÁBIL ====================

def validar_equacao_contabil(db: Session) -> Dict[str, Any]:
    """Valida a equação contábil: Ativo = Passivo + PL"""
    contas = crud_plano_contas.listar_plano_contas(db)
    
    total_ativo = 0.0
    total_passivo = 0.0
    total_pl = 0.0
    
    for conta in contas:
        saldo = crud_plano_contas.calcular_saldo_conta(db, conta.id)
        if conta.tipo == 'Ativo':
            total_ativo += saldo
        elif conta.tipo == 'Passivo':
            total_passivo += saldo
        elif conta.tipo == 'PL':
            total_pl += saldo
    
    diferenca = total_ativo - (total_passivo + total_pl)
    balanceado = abs(diferenca) < 0.01
    
    return {
        "ativo": total_ativo,
        "passivo": total_passivo,
        "patrimonio_liquido": total_pl,
        "diferenca": diferenca,
        "balanceado": balanceado
    }


# ==================== OPERAÇÕES CONTÁBEIS ====================

def listar_operacoes_disponiveis(db: Session) -> List[models.Operacao]:
    """Lista todas as operações contábeis disponíveis"""
    return db.query(models.Operacao).filter(
        models.Operacao.ativo == True
    ).order_by(models.Operacao.ordem).all()


def _buscar_conta_por_codigo(db: Session, codigo: str) -> Optional[models.PlanoDeContas]:
    """Busca conta pelo código"""
    return crud_plano_contas.buscar_conta_por_codigo(db, codigo)


def executar_operacao(
    db: Session,
    operacao_codigo: str,
    valor: float,
    data: date_type,
    descricao: Optional[str] = None,
    socio_id: Optional[int] = None,
    criado_por_id: Optional[int] = None
) -> models.OperacaoContabil:
    """
    Executa uma operação contábil padronizada gerando os lançamentos correspondentes
    """
    # Buscar operação
    operacao = db.query(models.Operacao).filter(
        models.Operacao.codigo == operacao_codigo,
        models.Operacao.ativo == True
    ).first()
    
    if not operacao:
        raise ValueError(f"Operação '{operacao_codigo}' não encontrada ou inativa")
    
    # Calcular mês de referência
    mes_referencia = data.strftime("%Y-%m")
    
    # Criar registro da operação
    operacao_contabil = models.OperacaoContabil(
        operacao_id=operacao.id,
        data=data,
        valor=valor,
        descricao=descricao,
        mes_referencia=mes_referencia,
        socio_id=socio_id,
        criado_por_id=criado_por_id,
        cancelado=False
    )
    db.add(operacao_contabil)
    db.flush()
    
    # Executar lançamentos conforme operação
    if operacao_codigo == "REC_HON":
        _executar_rec_hon(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "RESERVAR_FUNDO":
        _executar_reservar_fundo(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "PRO_LABORE":
        _executar_pro_labore(db, operacao_contabil, valor, data, descricao, criado_por_id)

    elif operacao_codigo == "INSS_PESSOAL":
        _executar_inss_pessoal(db, operacao_contabil, valor, data, descricao, criado_por_id)
    
    elif operacao_codigo == "INSS_PATRONAL":
        _executar_inss_patronal(db, operacao_contabil, valor, data, descricao, criado_por_id)
    
    elif operacao_codigo == "PAGAR_INSS":
        _executar_pagar_inss(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "DISTRIBUIR_LUCROS":
        _executar_distribuir_lucros(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "PAGAR_DESPESA_FUNDO":
        _executar_pagar_despesa_fundo(db, operacao_contabil, valor, data, descricao, criado_por_id)
    
    elif operacao_codigo == "BAIXAR_FUNDO":
        _executar_baixar_fundo(db, operacao_contabil, valor, data, descricao)
    
    else:
        raise ValueError(f"Operação '{operacao_codigo}' não implementada")
    
    db.commit()
    db.refresh(operacao_contabil)
    return operacao_contabil


def _executar_rec_hon(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """REC_HON: D-Caixa / C-Receita"""
    conta_caixa = _buscar_conta_por_codigo(db, "1.1.1")
    conta_receita = _buscar_conta_por_codigo(db, "4.1.1")
    
    if not conta_caixa or not conta_receita:
        raise ValueError("Contas 1.1.1 (Caixa) ou 4.1.1 (Receita) não encontradas")
    
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_caixa.id,
        conta_credito_id=conta_receita.id,
        valor=valor,
        historico=historico or "Recebimento de honorários",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_reservar_fundo(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """RESERVAR_FUNDO: D-Lucros Acum. / C-Reserva"""
    conta_lucros = _buscar_conta_por_codigo(db, "3.3")
    conta_reserva = _buscar_conta_por_codigo(db, "3.2")
    
    if not conta_lucros or not conta_reserva:
        raise ValueError("Contas 3.3 (Lucros Acumulados) ou 3.2 (Reservas) não encontradas")
    
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_lucros.id,
        conta_credito_id=conta_reserva.id,
        valor=valor,
        historico=historico or "Constituição de fundo de reserva",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_pro_labore(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str], criado_por: Optional[int]):
    """PRO_LABORE: D-Despesa Pró-Labore / C-Caixa"""
    conta_despesa_pl = _buscar_conta_por_codigo(db, "5.1.1")
    conta_caixa = _buscar_conta_por_codigo(db, "1.1.1")
    
    if not conta_despesa_pl or not conta_caixa:
        raise ValueError("Contas 5.1.1 (Pró-labore) ou 1.1.1 (Caixa) não encontradas")
    
    # Lançamento do valor bruto
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_despesa_pl.id,
        conta_credito_id=conta_caixa.id,
        valor=valor,
        historico=historico or "Pagamento de pró-labore",
        automatico=True,
        editavel=True,
        criado_por=criado_por
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_inss_pessoal(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str], criado_por: Optional[int]):
    """INSS_PESSOAL: D-Despesa Pró-Labore / C-INSS a Recolher"""
    conta_despesa_pl = _buscar_conta_por_codigo(db, "5.1.1")
    conta_inss = _buscar_conta_por_codigo(db, "2.1.5")
    
    if not conta_despesa_pl or not conta_inss:
        raise ValueError("Contas 5.1.1 (Pró-labore) ou 2.1.5 (INSS a Pagar) não encontradas")
    
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_despesa_pl.id,
        conta_credito_id=conta_inss.id,
        valor=valor,
        historico=historico or "INSS pessoal sobre pró-labore",
        automatico=True,
        editavel=True,
        criado_por=criado_por
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_inss_patronal(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str], criado_por: Optional[int]):
    """INSS_PATRONAL: D-Despesa INSS patronal / C-INSS a Recolher"""
    conta_despesa_inss = _buscar_conta_por_codigo(db, "5.1.3")
    conta_inss = _buscar_conta_por_codigo(db, "2.1.5")
    
    if not conta_despesa_inss or not conta_inss:
        raise ValueError("Contas 5.1.3 (Encargos INSS) ou 2.1.5 (INSS a Pagar) não encontradas")
    
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_despesa_inss.id,
        conta_credito_id=conta_inss.id,
        valor=valor,
        historico=historico or "INSS patronal",
        automatico=True,
        editavel=True,
        criado_por=criado_por
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_pagar_inss(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """PAGAR_INSS: D-INSS a Recolher / C-Caixa"""
    conta_inss = _buscar_conta_por_codigo(db, "2.1.5")
    conta_caixa = _buscar_conta_por_codigo(db, "1.1.1")
    
    if not conta_inss or not conta_caixa:
        raise ValueError("Contas 2.1.5 (INSS a Pagar) ou 1.1.1 (Caixa) não encontradas")
    
    # Validar saldo de INSS
    saldo_inss = crud_plano_contas.calcular_saldo_conta(db, conta_inss.id)
    if saldo_inss < valor:
        raise ValueError(f"Saldo insuficiente em INSS a Pagar. Saldo: R$ {saldo_inss:.2f}, Valor: R$ {valor:.2f}")
    
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_inss.id,
        conta_credito_id=conta_caixa.id,
        valor=valor,
        historico=historico or "Pagamento de INSS",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_distribuir_lucros(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """DISTRIBUIR_LUCROS: D-Lucros Acum. / C-Caixa"""
    conta_lucros = _buscar_conta_por_codigo(db, "3.3")
    conta_caixa = _buscar_conta_por_codigo(db, "1.1.1")
    
    if not conta_lucros or not conta_caixa:
        raise ValueError("Contas 3.3 (Lucros Acumulados) ou 1.1.1 (Caixa) não encontradas")
    
    # Validar saldo de lucros
    saldo_lucros = crud_plano_contas.calcular_saldo_conta(db, conta_lucros.id)
    if saldo_lucros < valor:
        raise ValueError(f"Saldo insuficiente em Lucros Acumulados. Saldo: R$ {saldo_lucros:.2f}, Valor: R$ {valor:.2f}")
    
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_lucros.id,
        conta_credito_id=conta_caixa.id,
        valor=valor,
        historico=historico or "Distribuição de lucros",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_pagar_despesa_fundo(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str], criado_por: Optional[int]):
    """PAGAR_DESPESA_FUNDO: D-Outras Despesas / C-Caixa"""
    conta_despesas = _buscar_conta_por_codigo(db, "5.2")
    conta_caixa = _buscar_conta_por_codigo(db, "1.1.1")
    
    if not conta_despesas or not conta_caixa:
        raise ValueError("Contas 5.2 (Despesas Operacionais) ou 1.1.1 (Caixa) não encontradas")
    
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_despesas.id,
        conta_credito_id=conta_caixa.id,
        valor=valor,
        historico=historico or "Pagamento de despesa",
        automatico=True,
        editavel=True,
        criado_por=criado_por
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_baixar_fundo(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """BAIXAR_FUNDO: D-Reserva / C-Lucros Acum."""
    conta_reserva = _buscar_conta_por_codigo(db, "3.2")
    conta_lucros = _buscar_conta_por_codigo(db, "3.3")
    
    if not conta_reserva or not conta_lucros:
        raise ValueError("Contas 3.2 (Reservas) ou 3.3 (Lucros Acumulados) não encontradas")
    
    # Validar saldo de reserva
    saldo_reserva = crud_plano_contas.calcular_saldo_conta(db, conta_reserva.id)
    if saldo_reserva < valor:
        raise ValueError(f"Saldo insuficiente em Reserva. Saldo: R$ {saldo_reserva:.2f}, Valor: R$ {valor:.2f}")
    
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_reserva.id,
        conta_credito_id=conta_lucros.id,
        valor=valor,
        historico=historico or "Baixa do fundo de reserva",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def listar_historico_operacoes(
    db: Session,
    mes_referencia: Optional[str] = None,
    socio_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.OperacaoContabil]:
    """Lista histórico de operações contábeis executadas"""
    query = db.query(models.OperacaoContabil)
    
    if mes_referencia:
        query = query.filter(models.OperacaoContabil.mes_referencia == mes_referencia)
    
    if socio_id:
        query = query.filter(models.OperacaoContabil.socio_id == socio_id)
    
    return query.order_by(models.OperacaoContabil.data.desc()).offset(skip).limit(limit).all()


def get_operacao_contabil(db: Session, operacao_contabil_id: int) -> Optional[models.OperacaoContabil]:
    """Busca uma operação contábil por ID"""
    return db.query(models.OperacaoContabil).filter(
        models.OperacaoContabil.id == operacao_contabil_id
    ).first()


def cancelar_operacao(db: Session, operacao_contabil_id: int) -> models.OperacaoContabil:
    """Cancela uma operação contábil removendo seus lançamentos"""
    operacao = get_operacao_contabil(db, operacao_contabil_id)
    if not operacao:
        raise ValueError("Operação não encontrada")
    
    if operacao.cancelado:
        raise ValueError("Operação já cancelada")
    
    # Deletar todos os lançamentos associados
    db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.operacao_contabil_id == operacao_contabil_id
    ).delete()
    
    # Marcar como cancelado
    operacao.cancelado = True
    operacao.data_cancelamento = datetime.utcnow()
    
    db.commit()
    db.refresh(operacao)
    return operacao


# ==================== PREVISÕES MENSAIS ====================

def get_previsao_operacao_mensal(db: Session, mes: str) -> Optional[models.PrevisaoOperacaoMensal]:
    """Busca previsão de operação mensal (YYYY-MM)"""
    return db.query(models.PrevisaoOperacaoMensal).filter(
        models.PrevisaoOperacaoMensal.mes == mes
    ).first()


def consolidar_previsao_operacao_mes(db: Session, mes: str, forcar_recalculo: bool = False) -> models.PrevisaoOperacaoMensal:
    """Consolida a previsão da operação para um mês"""
    previsao = get_previsao_operacao_mensal(db, mes)
    
    if previsao and previsao.consolidado and not forcar_recalculo:
        return previsao
    
    # Calcular previsão (implementação simplificada - expandir conforme necessário)
    if not previsao:
        previsao = models.PrevisaoOperacaoMensal(mes=mes)
        db.add(previsao)
    
    # TODO: Implementar cálculo completo de impostos, pró-labore, etc.
    # Por enquanto, marcar como consolidado
    previsao.consolidado = True
    previsao.data_consolidacao = datetime.utcnow()
    
    db.commit()
    db.refresh(previsao)
    return previsao


def desconsolidar_previsao_operacao_mes(db: Session, mes: str) -> Optional[models.PrevisaoOperacaoMensal]:
    """Desconsolida a previsão da operação para um mês"""
    previsao = get_previsao_operacao_mensal(db, mes)
    if not previsao:
        return None
    
    previsao.consolidado = False
    previsao.data_consolidacao = None
    
    db.commit()
    db.refresh(previsao)
    return previsao


def calcular_percentual_participacao_socio(db: Session, socio_id: int, mes: str) -> float:
    """Calcula o percentual de participação de um sócio nas entradas de um mês"""
    # Extrair ano e mês
    ano, mes_num = map(int, mes.split('-'))
    data_inicio = date_type(ano, mes_num, 1)
    
    # Último dia do mês
    if mes_num == 12:
        data_fim = date_type(ano + 1, 1, 1) - timedelta(days=1)
    else:
        data_fim = date_type(ano, mes_num + 1, 1) - timedelta(days=1)
    
    # Buscar entradas do mês
    entradas = db.query(models.Entrada).filter(
        models.Entrada.data >= data_inicio,
        models.Entrada.data <= data_fim
    ).all()
    
    total_entradas = sum(e.valor for e in entradas)
    if total_entradas == 0:
        return 0.0
    
    # Calcular contribuição do sócio
    contribuicao_socio = 0.0
    for entrada in entradas:
        entrada_socio = db.query(models.EntradaSocio).filter(
            models.EntradaSocio.entrada_id == entrada.id,
            models.EntradaSocio.socio_id == socio_id
        ).first()
        
        if entrada_socio:
            contribuicao_socio += entrada.valor * (entrada_socio.percentual / 100.0)
    
    return (contribuicao_socio / total_entradas) * 100.0


def calcular_pro_labore_iterativo(
    db: Session,
    receita_bruta: float,
    receita_12m: float,
    faixa_simples: Any,
    despesas_gerais: float,
    percentual_pl: float = 0.05
) -> tuple:
    """
    Calcula pró-labore de forma iterativa considerando que o pró-labore
    impacta o próprio lucro líquido
    
    Returns: (pro_labore, inss_patronal, inss_pessoal, lucro_liquido)
    """
    # Cálculo simplificado - expandir conforme necessário
    imposto_simples = receita_bruta * faixa_simples.aliquota - faixa_simples.deducao
    lucro_bruto = receita_bruta - imposto_simples - despesas_gerais
    
    # Iteração simplificada
    pro_labore = lucro_bruto * percentual_pl
    inss_pessoal = pro_labore * 0.11
    inss_patronal = pro_labore * 0.20
    
    lucro_liquido = lucro_bruto - pro_labore - inss_patronal
    
    return (pro_labore, inss_patronal, inss_pessoal, lucro_liquido)


# ==================== DMPL (Demonstração das Mutações do PL) ====================

def calcular_dmpl(db: Session, ano_inicio: int, ano_fim: int) -> Dict[str, Any]:
    """
    Calcula DMPL baseado exclusivamente nos lançamentos contábeis das operações
    que afetam contas do Patrimônio Líquido (tipo='PL')
    """
    # Buscar contas PL
    contas_pl = db.query(models.PlanoDeContas).filter(
        models.PlanoDeContas.tipo == 'PL',
        models.PlanoDeContas.ativo == True
    ).all()
    
    if not contas_pl:
        return {
            "ano_inicio": ano_inicio,
            "ano_fim": ano_fim,
            "saldo_inicial": {"capital_social": 0, "reservas": 0, "lucros_acumulados": 0, "total": 0},
            "movimentacoes": [],
            "saldo_final": {"capital_social": 0, "reservas": 0, "lucros_acumulados": 0, "total": 0},
            "total_mutacoes": 0,
            "variacao_percentual": 0
        }
    
    # Saldo inicial (até 31/12 do ano anterior)
    data_inicio_periodo = date_type(ano_inicio, 1, 1)
    data_fim_anterior = date_type(ano_inicio - 1, 12, 31)
    
    saldo_inicial = _calcular_saldos_pl(db, contas_pl, None, data_fim_anterior)
    
    # Movimentações no período
    data_fim_periodo = date_type(ano_fim, 12, 31)
    movimentacoes = _extrair_movimentacoes_pl(db, contas_pl, data_inicio_periodo, data_fim_periodo)
    
    # Saldo final
    saldo_final = _calcular_saldos_pl(db, contas_pl, None, data_fim_periodo)
    
    # Calcular mutações
    total_mutacoes = saldo_final["total"] - saldo_inicial["total"]
    variacao_percentual = 0
    if saldo_inicial["total"] != 0:
        variacao_percentual = (total_mutacoes / abs(saldo_inicial["total"])) * 100
    
    return {
        "ano_inicio": ano_inicio,
        "ano_fim": ano_fim,
        "saldo_inicial": saldo_inicial,
        "movimentacoes": movimentacoes,
        "saldo_final": saldo_final,
        "total_mutacoes": total_mutacoes,
        "variacao_percentual": variacao_percentual
    }


def _calcular_saldos_pl(db: Session, contas_pl: List[models.PlanoDeContas], data_inicio: Optional[date_type], data_fim: Optional[date_type]) -> Dict[str, float]:
    """Calcula saldos por subgrupo do PL"""
    capital_social = 0.0
    reservas = 0.0
    lucros_acumulados = 0.0
    
    for conta in contas_pl:
        saldo = crud_plano_contas.calcular_saldo_conta(db, conta.id, data_inicio, data_fim)
        
        if conta.codigo.startswith("3.1"):  # Capital Social
            capital_social += saldo
        elif conta.codigo.startswith("3.2"):  # Reservas
            reservas += saldo
        elif conta.codigo.startswith("3.3") or conta.codigo.startswith("3.4"):  # Lucros/Prejuízos
            lucros_acumulados += saldo
    
    return {
        "capital_social": capital_social,
        "reservas": reservas,
        "lucros_acumulados": lucros_acumulados,
        "total": capital_social + reservas + lucros_acumulados
    }


def _extrair_movimentacoes_pl(db: Session, contas_pl: List[models.PlanoDeContas], data_inicio: date_type, data_fim: date_type) -> List[Dict[str, Any]]:
    """Extrai movimentações do PL no período por tipo de operação"""
    contas_pl_ids = [c.id for c in contas_pl]
    
    # Buscar lançamentos que afetam PL
    lancamentos = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.data >= data_inicio,
        models.LancamentoContabil.data <= data_fim,
        or_(
            models.LancamentoContabil.conta_debito_id.in_(contas_pl_ids),
            models.LancamentoContabil.conta_credito_id.in_(contas_pl_ids)
        )
    ).order_by(models.LancamentoContabil.data).all()
    
    # Agrupar por tipo de movimentação
    movimentacoes_agrupadas = {}
    
    for lanc in lancamentos:
        # Identificar tipo de movimentação
        tipo_mov = "Outras mutações do PL"
        
        if lanc.operacao_contabil_id:
            operacao = lanc.operacao_contabil
            if operacao:
                tipo_mov = operacao.operacao.nome
        
        if tipo_mov not in movimentacoes_agrupadas:
            movimentacoes_agrupadas[tipo_mov] = {
                "capital_social": 0.0,
                "reservas": 0.0,
                "lucros_acumulados": 0.0
            }
        
        # Calcular impacto no subgrupo
        conta_debito = lanc.conta_debito
        conta_credito = lanc.conta_credito
        
        # Se débito é PL, diminui; se crédito é PL, aumenta
        if conta_debito.tipo == 'PL':
            if conta_debito.codigo.startswith("3.1"):
                movimentacoes_agrupadas[tipo_mov]["capital_social"] -= lanc.valor
            elif conta_debito.codigo.startswith("3.2"):
                movimentacoes_agrupadas[tipo_mov]["reservas"] -= lanc.valor
            elif conta_debito.codigo.startswith("3.3") or conta_debito.codigo.startswith("3.4"):
                movimentacoes_agrupadas[tipo_mov]["lucros_acumulados"] -= lanc.valor
        
        if conta_credito.tipo == 'PL':
            if conta_credito.codigo.startswith("3.1"):
                movimentacoes_agrupadas[tipo_mov]["capital_social"] += lanc.valor
            elif conta_credito.codigo.startswith("3.2"):
                movimentacoes_agrupadas[tipo_mov]["reservas"] += lanc.valor
            elif conta_credito.codigo.startswith("3.3") or conta_credito.codigo.startswith("3.4"):
                movimentacoes_agrupadas[tipo_mov]["lucros_acumulados"] += lanc.valor
    
    # Converter para lista
    movimentacoes = []
    for descricao, valores in movimentacoes_agrupadas.items():
        total = valores["capital_social"] + valores["reservas"] + valores["lucros_acumulados"]
        movimentacoes.append({
            "descricao": descricao,
            "capital_social": valores["capital_social"],
            "reservas": valores["reservas"],
            "lucros_acumulados": valores["lucros_acumulados"],
            "total": total
        })
    
    return movimentacoes


# ==================== DFC (Demonstração dos Fluxos de Caixa) ====================

def calcular_dfc(db: Session, mes: int, ano: int) -> Dict[str, Any]:
    """
    Calcula DFC pelo método direto baseado nos lançamentos contábeis
    que afetam a conta Caixa (1.1.1)
    """
    # Buscar conta Caixa
    conta_caixa = crud_plano_contas.buscar_conta_por_codigo(db, "1.1.1")
    if not conta_caixa:
        raise ValueError("Conta 1.1.1 (Caixa e Bancos) não encontrada")
    
    # Período
    data_inicio = date_type(ano, mes, 1)
    if mes == 12:
        data_fim = date_type(ano, 12, 31)
    else:
        data_fim = date_type(ano, mes + 1, 1) - timedelta(days=1)
    
    # Saldo inicial e final
    data_anterior = data_inicio - timedelta(days=1)
    saldo_inicial = crud_plano_contas.calcular_saldo_conta(db, conta_caixa.id, None, data_anterior)
    saldo_final = crud_plano_contas.calcular_saldo_conta(db, conta_caixa.id, None, data_fim)
    
    # Buscar lançamentos que afetam caixa
    lancamentos = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.data >= data_inicio,
        models.LancamentoContabil.data <= data_fim,
        or_(
            models.LancamentoContabil.conta_debito_id == conta_caixa.id,
            models.LancamentoContabil.conta_credito_id == conta_caixa.id
        )
    ).all()
    
    # Classificar lançamentos
    operacionais = _classificar_fluxo_operacional(db, lancamentos, conta_caixa.id)
    investimentos = _classificar_fluxo_investimento(db, lancamentos, conta_caixa.id)
    financiamentos = _classificar_fluxo_financiamento(db, lancamentos, conta_caixa.id)
    
    variacao_liquida = (
        operacionais["total"] + 
        investimentos["total"] + 
        financiamentos["total"]
    )
    
    variacao_percentual = 0
    if saldo_inicial != 0:
        variacao_percentual = (variacao_liquida / abs(saldo_inicial)) * 100
    
    return {
        "mes": f"{ano}-{mes:02d}",
        "saldo_inicial": saldo_inicial,
        "operacionais": operacionais,
        "investimentos": investimentos,
        "financiamentos": financiamentos,
        "variacao_liquida": variacao_liquida,
        "saldo_final": saldo_final,
        "variacao_percentual": variacao_percentual
    }


def _classificar_fluxo_operacional(db: Session, lancamentos: List[models.LancamentoContabil], conta_caixa_id: int) -> Dict[str, float]:
    """Classifica fluxos operacionais"""
    recebimentos_clientes = 0.0
    pagamentos_fornecedores = 0.0
    pagamentos_salarios = 0.0
    pagamentos_impostos = 0.0
    outras_receitas = 0.0
    outras_despesas = 0.0
    
    for lanc in lancamentos:
        contraparte = lanc.conta_debito if lanc.conta_credito_id == conta_caixa_id else lanc.conta_credito
        valor_fluxo = lanc.valor if lanc.conta_debito_id == conta_caixa_id else -lanc.valor
        
        # Classificar por tipo de conta
        if contraparte.tipo == 'Receita':
            recebimentos_clientes += valor_fluxo
        elif contraparte.tipo == 'Despesa':
            if 'pró-labore' in contraparte.descricao.lower() or 'salário' in contraparte.descricao.lower():
                pagamentos_salarios += valor_fluxo
            else:
                outras_despesas += valor_fluxo
        elif contraparte.codigo.startswith('2.1.4') or contraparte.codigo.startswith('2.1.5'):  # Impostos
            pagamentos_impostos += valor_fluxo
        elif contraparte.tipo in ['Passivo', 'Ativo']:
            if contraparte.codigo.startswith('2.'):  # Passivo operacional
                pagamentos_fornecedores += valor_fluxo
    
    total = (recebimentos_clientes + pagamentos_fornecedores + pagamentos_salarios + 
             pagamentos_impostos + outras_receitas + outras_despesas)
    
    return {
        "recebimentos_clientes": recebimentos_clientes,
        "pagamentos_fornecedores": pagamentos_fornecedores,
        "pagamentos_salarios": pagamentos_salarios,
        "pagamentos_impostos": pagamentos_impostos,
        "outras_receitas": outras_receitas,
        "outras_despesas": outras_despesas,
        "total": total
    }


def _classificar_fluxo_investimento(db: Session, lancamentos: List[models.LancamentoContabil], conta_caixa_id: int) -> Dict[str, float]:
    """Classifica fluxos de investimento"""
    aquisicao_imobilizado = 0.0
    venda_imobilizado = 0.0
    aplicacoes_financeiras = 0.0
    resgate_aplicacoes = 0.0
    
    for lanc in lancamentos:
        contraparte = lanc.conta_debito if lanc.conta_credito_id == conta_caixa_id else lanc.conta_credito
        valor_fluxo = lanc.valor if lanc.conta_debito_id == conta_caixa_id else -lanc.valor
        
        # Classificar por conta
        if contraparte.codigo.startswith('1.2.'):  # Ativo não circulante
            if valor_fluxo < 0:
                aquisicao_imobilizado += valor_fluxo
            else:
                venda_imobilizado += valor_fluxo
    
    total = aquisicao_imobilizado + venda_imobilizado + aplicacoes_financeiras + resgate_aplicacoes
    
    return {
        "aquisicao_imobilizado": aquisicao_imobilizado,
        "venda_imobilizado": venda_imobilizado,
        "aplicacoes_financeiras": aplicacoes_financeiras,
        "resgate_aplicacoes": resgate_aplicacoes,
        "total": total
    }


def _classificar_fluxo_financiamento(db: Session, lancamentos: List[models.LancamentoContabil], conta_caixa_id: int) -> Dict[str, float]:
    """Classifica fluxos de financiamento"""
    aumento_capital = 0.0
    emprestimos_obtidos = 0.0
    pagamento_emprestimos = 0.0
    distribuicao_dividendos = 0.0
    
    for lanc in lancamentos:
        contraparte = lanc.conta_debito if lanc.conta_credito_id == conta_caixa_id else lanc.conta_credito
        valor_fluxo = lanc.valor if lanc.conta_debito_id == conta_caixa_id else -lanc.valor
        
        # Classificar por tipo PL ou passivo não circulante
        if contraparte.tipo == 'PL':
            if contraparte.codigo.startswith('3.1'):  # Capital
                if valor_fluxo > 0:
                    aumento_capital += valor_fluxo
            elif contraparte.codigo.startswith('3.3') or contraparte.codigo.startswith('3.4'):  # Lucros
                if valor_fluxo < 0:
                    distribuicao_dividendos += valor_fluxo
        elif contraparte.codigo.startswith('2.2.'):  # Passivo não circulante (empréstimos)
            if valor_fluxo > 0:
                emprestimos_obtidos += valor_fluxo
            else:
                pagamento_emprestimos += valor_fluxo
    
    total = aumento_capital + emprestimos_obtidos + pagamento_emprestimos + distribuicao_dividendos
    
    return {
        "aumento_capital": aumento_capital,
        "emprestimos_obtidos": emprestimos_obtidos,
        "pagamento_emprestimos": pagamento_emprestimos,
        "distribuicao_dividendos": distribuicao_dividendos,
        "total": total
    }
