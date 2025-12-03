from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from . import models
from backend import schemas
from datetime import date as date_type, datetime
from . import crud_plano_contas

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
# Aportes de Capital
# =================================================================

def create_aporte_capital(
    db: Session,
    socio_id: int,
    data: date_type,
    valor: float,
    tipo_aporte: str,
    descricao: Optional[str] = None
) -> models.AporteCapital:
    """
    Cria um novo aporte de capital, gera lançamento contábil e recalcula o capital_social do sócio.
    
    Args:
        tipo_aporte: 'dinheiro', 'bens', 'servicos' (aporte) ou 'retirada' (saída de sócio)
    """
    from database.crud_plano_contas import buscar_conta_por_codigo
    
    # Validar tipo
    tipos_validos = ['dinheiro', 'bens', 'servicos', 'retirada']
    if tipo_aporte not in tipos_validos:
        raise ValueError(f"Tipo de aporte inválido. Use: {', '.join(tipos_validos)}")
    
    # Validar sócio
    socio = get_socio(db, socio_id)
    if not socio:
        raise ValueError("Sócio não encontrado")
    
    # Criar aporte
    aporte = models.AporteCapital(
        socio_id=socio_id,
        data=data,
        valor=valor,
        tipo_aporte=tipo_aporte,
        descricao=descricao
    )
    db.add(aporte)
    db.flush()
    
    # Criar lançamento contábil correspondente
    conta_capital = buscar_conta_por_codigo(db, "3.1")
    if not conta_capital:
        raise ValueError("Conta 3.1 (Capital Social) não encontrada no plano de contas")
    
    if tipo_aporte == 'dinheiro':
        conta_debito = buscar_conta_por_codigo(db, "1.1.1")  # Caixa e Bancos
        if not conta_debito:
            raise ValueError("Conta 1.1.1 (Caixa e Bancos) não encontrada")
        historico = f"Aporte de capital em dinheiro - {socio.nome}"
        if descricao:
            historico += f" - {descricao}"
        lanc = models.LancamentoContabil(
            data=data,
            conta_debito_id=conta_debito.id,
            conta_credito_id=conta_capital.id,
            valor=valor,
            historico=historico,
            automatico=True,
            editavel=False,
            tipo_lancamento='aporte_capital'
        )
        
    elif tipo_aporte == 'bens':
        conta_debito = buscar_conta_por_codigo(db, "1.2.1.1")  # Equipamentos e Móveis
        if not conta_debito:
            raise ValueError("Conta 1.2.1.1 (Equipamentos e Móveis) não encontrada")
        historico = f"Aporte de capital em bens - {socio.nome}"
        if descricao:
            historico += f" - {descricao}"
        lanc = models.LancamentoContabil(
            data=data,
            conta_debito_id=conta_debito.id,
            conta_credito_id=conta_capital.id,
            valor=valor,
            historico=historico,
            automatico=True,
            editavel=False,
            tipo_lancamento='aporte_capital'
        )
        
    elif tipo_aporte == 'servicos':
        conta_debito = buscar_conta_por_codigo(db, "1.2.2.1")  # Serviços Capitalizados
        if not conta_debito:
            raise ValueError("Conta 1.2.2.1 (Serviços Capitalizados) não encontrada")
        historico = f"Aporte de capital em serviços - {socio.nome}"
        if descricao:
            historico += f" - {descricao}"
        lanc = models.LancamentoContabil(
            data=data,
            conta_debito_id=conta_debito.id,
            conta_credito_id=conta_capital.id,
            valor=valor,
            historico=historico,
            automatico=True,
            editavel=False,
            tipo_lancamento='aporte_capital'
        )
        
    elif tipo_aporte == 'retirada':
        # Retirada inverte: debita Capital, credita Caixa
        conta_caixa = buscar_conta_por_codigo(db, "1.1.1")
        if not conta_caixa:
            raise ValueError("Conta 1.1.1 (Caixa e Bancos) não encontrada")
        historico = f"Retirada de capital - {socio.nome}"
        if descricao:
            historico += f" - {descricao}"
        lanc = models.LancamentoContabil(
            data=data,
            conta_debito_id=conta_capital.id,
            conta_credito_id=conta_caixa.id,
            valor=valor,
            historico=historico,
            automatico=True,
            editavel=False,
            tipo_lancamento='aporte_capital'
        )
    
    db.add(lanc)
    db.flush()
    
    # Recalcular capital social
    recalcular_capital_social_socio(db, socio_id)
    
    db.commit()
    db.refresh(aporte)
    return aporte

def get_aporte(db: Session, aporte_id: int) -> Optional[models.AporteCapital]:
    """Busca um aporte específico pelo ID."""
    return db.query(models.AporteCapital).filter(models.AporteCapital.id == aporte_id).first()

def get_aportes_socio(db: Session, socio_id: int) -> List[models.AporteCapital]:
    """Retorna todos os aportes de um sócio ordenados por data decrescente."""
    return db.query(models.AporteCapital).filter(
        models.AporteCapital.socio_id == socio_id
    ).order_by(models.AporteCapital.data.desc()).all()

def get_aportes_periodo(
    db: Session,
    data_inicio: Optional[date_type] = None,
    data_fim: Optional[date_type] = None
) -> List[models.AporteCapital]:
    """Retorna aportes em um período específico."""
    query = db.query(models.AporteCapital)
    
    if data_inicio:
        query = query.filter(models.AporteCapital.data >= data_inicio)
    if data_fim:
        query = query.filter(models.AporteCapital.data <= data_fim)
    
    return query.order_by(models.AporteCapital.data.desc()).all()

def update_aporte_capital(
    db: Session,
    aporte_id: int,
    update_data: dict
) -> Optional[models.AporteCapital]:
    """Atualiza um aporte, recria o lançamento contábil e recalcula o capital_social do sócio."""
    aporte = get_aporte(db, aporte_id)
    if not aporte:
        return None
    
    socio_id = aporte.socio_id
    socio = aporte.socio
    
    # Remover lançamento contábil antigo (busca por características do aporte)
    lancamento_antigo = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.tipo_lancamento == 'aporte_capital',
        models.LancamentoContabil.data == aporte.data,
        models.LancamentoContabil.valor == aporte.valor,
        models.LancamentoContabil.historico.like(f'%{socio.nome}%')
    ).first()
    
    if lancamento_antigo:
        db.delete(lancamento_antigo)
        db.flush()
    
    # Atualizar campos do aporte
    for key, value in update_data.items():
        if hasattr(aporte, key) and value is not None:
            setattr(aporte, key, value)
    
    aporte.atualizado_em = datetime.utcnow()
    db.flush()
    
    # Recriar lançamento contábil com dados atualizados
    from database.crud_plano_contas import buscar_conta_por_codigo
    
    conta_capital = buscar_conta_por_codigo(db, "3.1")
    
    if aporte.tipo_aporte == 'dinheiro':
        conta_debito = buscar_conta_por_codigo(db, "1.1.1")
        historico = f"Aporte de capital em dinheiro - {socio.nome}"
        if aporte.descricao:
            historico += f" - {aporte.descricao}"
        lanc = models.LancamentoContabil(
            data=aporte.data,
            conta_debito_id=conta_debito.id,
            conta_credito_id=conta_capital.id,
            valor=aporte.valor,
            historico=historico,
            automatico=True,
            editavel=False,
            tipo_lancamento='aporte_capital'
        )
    elif aporte.tipo_aporte == 'bens':
        conta_debito = buscar_conta_por_codigo(db, "1.2.1.1")
        historico = f"Aporte de capital em bens - {socio.nome}"
        if aporte.descricao:
            historico += f" - {aporte.descricao}"
        lanc = models.LancamentoContabil(
            data=aporte.data,
            conta_debito_id=conta_debito.id,
            conta_credito_id=conta_capital.id,
            valor=aporte.valor,
            historico=historico,
            automatico=True,
            editavel=False,
            tipo_lancamento='aporte_capital'
        )
    elif aporte.tipo_aporte == 'servicos':
        conta_debito = buscar_conta_por_codigo(db, "1.2.2.1")
        historico = f"Aporte de capital em serviços - {socio.nome}"
        if aporte.descricao:
            historico += f" - {aporte.descricao}"
        lanc = models.LancamentoContabil(
            data=aporte.data,
            conta_debito_id=conta_debito.id,
            conta_credito_id=conta_capital.id,
            valor=aporte.valor,
            historico=historico,
            automatico=True,
            editavel=False,
            tipo_lancamento='aporte_capital'
        )
    elif aporte.tipo_aporte == 'retirada':
        conta_caixa = buscar_conta_por_codigo(db, "1.1.1")
        historico = f"Retirada de capital - {socio.nome}"
        if aporte.descricao:
            historico += f" - {aporte.descricao}"
        lanc = models.LancamentoContabil(
            data=aporte.data,
            conta_debito_id=conta_capital.id,
            conta_credito_id=conta_caixa.id,
            valor=aporte.valor,
            historico=historico,
            automatico=True,
            editavel=False,
            tipo_lancamento='aporte_capital'
        )
    
    db.add(lanc)
    db.flush()
    
    # Recalcular capital social
    recalcular_capital_social_socio(db, socio_id)
    
    db.commit()
    db.refresh(aporte)
    return aporte

def delete_aporte_capital(db: Session, aporte_id: int) -> bool:
    """Deleta um aporte, remove o lançamento contábil e recalcula o capital_social do sócio."""
    aporte = get_aporte(db, aporte_id)
    if not aporte:
        return False
    
    socio_id = aporte.socio_id
    
    # Remover lançamento contábil associado
    lancamento = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.tipo_lancamento == 'aporte_capital',
        models.LancamentoContabil.data == aporte.data,
        models.LancamentoContabil.valor == aporte.valor,
        models.LancamentoContabil.historico.like(f'%{aporte.socio.nome}%')
    ).first()
    
    if lancamento:
        db.delete(lancamento)
    
    db.delete(aporte)
    db.flush()
    
    # Recalcular capital social
    recalcular_capital_social_socio(db, socio_id)
    
    db.commit()
    return True

def alocar_reserva_legal(db: Session, mes: str, valor_reserva: float) -> Optional[models.LancamentoContabil]:
    """
    Aloca 10% do lucro líquido para a Reserva Legal (Fundo de Reserva).
    
    Lançamento: D 3.3 (Lucros Acumulados) / C 3.2.1 (Reserva de Lucros)
    """
    from database.crud_plano_contas import buscar_conta_por_codigo
    import calendar
    
    if valor_reserva <= 0:
        return None
    
    ano_int = int(mes.split('-')[0])
    mes_int = int(mes.split('-')[1])
    dia = calendar.monthrange(ano_int, mes_int)[1]
    data_lcto = date_type(ano_int, mes_int, dia)
    
    conta_lucros = buscar_conta_por_codigo(db, "3.3")
    conta_reserva = buscar_conta_por_codigo(db, "3.2.1")
    
    if not conta_lucros or not conta_reserva:
        raise ValueError("Contas 3.3 ou 3.2.1 não encontradas no plano de contas")
    
    # Verificar se já existe alocação para este mês
    existente = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.tipo_lancamento == 'alocacao_reserva',
        models.LancamentoContabil.referencia_mes == mes
    ).first()
    
    if existente:
        # Atualizar valor
        existente.valor = valor_reserva
        db.commit()
        return existente
    
    # Criar novo lançamento
    lanc = models.LancamentoContabil(
        data=data_lcto,
        conta_debito_id=conta_lucros.id,
        conta_credito_id=conta_reserva.id,
        valor=valor_reserva,
        historico=f"Alocação de reserva legal (10%) - {mes}",
        automatico=True,
        editavel=False,
        tipo_lancamento='alocacao_reserva',
        referencia_mes=mes
    )
    db.add(lanc)
    db.commit()
    db.refresh(lanc)
    return lanc

def validar_equacao_contabil(db: Session, data_referencia: Optional[date_type] = None) -> dict:
    """
    Valida a equação contábil: Ativo = Passivo + Patrimônio Líquido
    
    Retorna dict com totais e validações de integridade.
    """
    from database.crud_plano_contas import calcular_saldo_conta, buscar_conta_por_codigo
    from sqlalchemy import func
    
    # Calcular totais por tipo
    contas_ativo = db.query(models.PlanoDeContas).filter(
        models.PlanoDeContas.tipo == 'Ativo',
        models.PlanoDeContas.aceita_lancamento == True
    ).all()
    
    contas_passivo = db.query(models.PlanoDeContas).filter(
        models.PlanoDeContas.tipo == 'Passivo',
        models.PlanoDeContas.aceita_lancamento == True
    ).all()
    
    contas_pl = db.query(models.PlanoDeContas).filter(
        models.PlanoDeContas.tipo == 'PL',
        models.PlanoDeContas.aceita_lancamento == True
    ).all()
    
    total_ativo = sum(calcular_saldo_conta(db, c.id, data_fim=data_referencia) for c in contas_ativo)
    total_passivo = sum(calcular_saldo_conta(db, c.id, data_fim=data_referencia) for c in contas_passivo)
    total_pl = sum(calcular_saldo_conta(db, c.id, data_fim=data_referencia) for c in contas_pl)
    
    diferenca = total_ativo - (total_passivo + total_pl)
    balanceado = abs(diferenca) < 0.01
    
    # Verificar capital social
    conta_capital = buscar_conta_por_codigo(db, "3.1")
    capital_contabil = calcular_saldo_conta(db, conta_capital.id, data_fim=data_referencia) if conta_capital else 0.0
    
    # Somar aportes de todos os sócios
    query_positivos = db.query(func.sum(models.AporteCapital.valor)).filter(
        models.AporteCapital.tipo_aporte.in_(['dinheiro', 'bens', 'servicos'])
    )
    if data_referencia:
        query_positivos = query_positivos.filter(models.AporteCapital.data <= data_referencia)
    aportes_positivos = query_positivos.scalar() or 0.0
    
    query_retiradas = db.query(func.sum(models.AporteCapital.valor)).filter(
        models.AporteCapital.tipo_aporte == 'retirada'
    )
    if data_referencia:
        query_retiradas = query_retiradas.filter(models.AporteCapital.data <= data_referencia)
    retiradas = query_retiradas.scalar() or 0.0
    
    capital_socios = float(aportes_positivos) - float(retiradas)
    capital_match = abs(capital_contabil - capital_socios) < 0.01
    
    return {
        'ativo': round(total_ativo, 2),
        'passivo': round(total_passivo, 2),
        'patrimonio_liquido': round(total_pl, 2),
        'diferenca': round(diferenca, 2),
        'balanceado': balanceado,
        'capital_social_contabil': round(capital_contabil, 2),
        'capital_social_socios': round(capital_socios, 2),
        'capital_match': capital_match,
        'mensagem': 'Contabilidade balanceada!' if (balanceado and capital_match) else 'ATENÇÃO: Desequilíbrio contábil detectado!'
    }

def recalcular_capital_social_socio(db: Session, socio_id: int):
    """
    Recalcula o capital_social do sócio somando todos os aportes.
    Aportes positivos (dinheiro, bens, servicos) somam.
    Retiradas são valores negativos que diminuem o capital.
    """
    from sqlalchemy import func
    
    # Somar aportes (dinheiro, bens, servicos)
    aportes_positivos = db.query(func.sum(models.AporteCapital.valor)).filter(
        models.AporteCapital.socio_id == socio_id,
        models.AporteCapital.tipo_aporte.in_(['dinheiro', 'bens', 'servicos'])
    ).scalar() or 0.0
    
    # Somar retiradas (valores sempre positivos na tabela, mas subtraem do capital)
    retiradas = db.query(func.sum(models.AporteCapital.valor)).filter(
        models.AporteCapital.socio_id == socio_id,
        models.AporteCapital.tipo_aporte == 'retirada'
    ).scalar() or 0.0
    
    capital_total = float(aportes_positivos) - float(retiradas)
    
    # Atualizar sócio
    socio = get_socio(db, socio_id)
    if socio:
        socio.capital_social = capital_total
        db.flush()

def get_relatorio_integralizacao(db: Session) -> dict:
    """
    Retorna relatório de integralização de capital por sócio e tipo.
    """
    socios = get_socios(db)
    relatorio = {
        'socios': [],
        'total_geral': 0.0
    }
    
    for socio in socios:
        aportes = get_aportes_socio(db, socio.id)
        
        # Agrupar por tipo
        aportes_por_tipo = {
            'dinheiro': 0.0,
            'bens': 0.0,
            'servicos': 0.0,
            'retirada': 0.0
        }
        
        for aporte in aportes:
            if aporte.tipo_aporte in aportes_por_tipo:
                aportes_por_tipo[aporte.tipo_aporte] += float(aporte.valor)
        
        total_socio = (
            aportes_por_tipo['dinheiro'] +
            aportes_por_tipo['bens'] +
            aportes_por_tipo['servicos'] -
            aportes_por_tipo['retirada']
        )
        
        relatorio['socios'].append({
            'id': socio.id,
            'nome': socio.nome,
            'aportes_por_tipo': aportes_por_tipo,
            'total': total_socio
        })
        
        relatorio['total_geral'] += total_socio
    
    return relatorio

# =================================================================
# Aportes de Capital (Função Antiga - Manter por compatibilidade)
# =================================================================

def registrar_aporte_capital(
    db: Session,
    socio_id: int,
    valor: float,
    data: date_type,
    forma: str = 'dinheiro'
) -> dict:
    """Registra um aporte de capital (dinheiro ou bens) e lança o lançamento contábil.

    Lançamentos:
    - Dinheiro: D 1.1.1 (Caixa e Bancos) / C 3.1 (Capital Social)
    - Bens:     D 1.2.1.1 (Equipamentos e Móveis) / C 3.1 (Capital Social)
    """
    socio = get_socio(db, socio_id)
    if not socio:
        raise ValueError("Sócio não encontrado")

    conta_capital = crud_plano_contas.buscar_conta_por_codigo(db, "3.1")
    if not conta_capital:
        raise ValueError("Conta Capital Social (3.1) não encontrada no plano de contas")

    if forma == 'bens':
        conta_debito = crud_plano_contas.buscar_conta_por_codigo(db, "1.2.1.1")  # Equipamentos e Móveis
        historico = f"Aporte de capital em bens - {socio.nome}"
    else:
        conta_debito = crud_plano_contas.buscar_conta_por_codigo(db, "1.1.1")  # Caixa e Bancos
        historico = f"Aporte de capital em dinheiro - {socio.nome}"

    if not conta_debito:
        raise ValueError("Conta de débito para aporte não encontrada no plano de contas")

    lanc = models.LancamentoContabil(
        data=data,
        conta_debito_id=conta_debito.id,
        conta_credito_id=conta_capital.id,
        valor=valor,
        historico=historico,
        automatico=True,
        editavel=False,
        tipo_lancamento='efetivo'
    )
    db.add(lanc)

    # Atualiza capital social do sócio
    socio.capital_social = (socio.capital_social or 0.0) + float(valor)

    db.commit()
    db.refresh(lanc)
    db.refresh(socio)

    return {
        "socio_id": socio.id,
        "novo_capital_social": socio.capital_social,
        "lancamento_id": lanc.id
    }

# =================================================================
# CRUD for Entrada (with business logic)
# =================================================================

def create_entrada(db: Session, entrada: schemas.EntradaCreate) -> models.Entrada:
    """
    Cria uma nova entrada.
    Ajuste: remover crédito imediato de 5% para administrador.
    Apenas reserva de 10% é destacada aqui; percentuais dos sócios definem
    participação para saldo distribuído preliminar (não inclui pró-labore).
    Pró-labore e 5% do lucro líquido do administrador serão tratados em provisões.
    """
    # Validar se o mês está consolidado
    mes_entrada = entrada.data.strftime('%Y-%m')
    dre_mes = db.query(models.DREMensal).filter(models.DREMensal.mes == mes_entrada).first()
    if dre_mes and dre_mes.consolidado:
        raise ValueError(
            f"Não é possível criar entrada no mês {mes_entrada} pois ele já está consolidado. "
            "Desconsolide a DRE primeiro."
        )
    
    config = get_configuracao(db)
    # Suposição: O primeiro sócio com 'Administrador' na função é o admin.
    admin_socio = db.query(models.Socio).filter(models.Socio.funcao.ilike('%administrador%')).first()

    valor_total = entrada.valor
    valor_fundo = valor_total * config.percentual_fundo_reserva
    valor_restante = valor_total - valor_fundo

    fundo_reserva = get_or_create_fundo(db, nome="Fundo de Reserva")
    fundo_reserva.saldo += valor_fundo

    # Removido crédito imediato do administrador (5%) para evitar dupla contagem
    
    entrada_data = entrada.dict(exclude={'socios'})
    db_entrada = models.Entrada(**entrada_data)
    db.add(db_entrada)
    db.flush() # Use flush to get the db_entrada.id before commit

    for socio_assoc_data in entrada.socios:
        socio = get_socio(db, socio_id=socio_assoc_data.socio_id)
        percentual_int = socio_assoc_data.percentual  # já inteiro
        if socio:
            valor_socio = valor_restante * (percentual_int / 100.0)
            # Administrador recebe apenas participação se tiver percentual atribuído
            socio.saldo += valor_socio

        db_assoc = models.EntradaSocio(
            entrada_id=db_entrada.id,
            socio_id=socio_assoc_data.socio_id,
            percentual=percentual_int  # armazenado como inteiro
        )
        db.add(db_assoc)

    db.commit()
    db.refresh(db_entrada)
    
    # Atualizar lançamentos contábeis do mês
    try:
        atualizar_lancamentos_mes(db, mes_entrada)
        db.commit()
    except Exception as e:
        db.rollback()
        raise ValueError(f"Erro ao atualizar lançamentos contábeis: {str(e)}")
    
    return db_entrada

def get_entrada(db: Session, entrada_id: int) -> models.Entrada:
    """Busca uma entrada específica pelo ID."""
    return db.query(models.Entrada).filter(models.Entrada.id == entrada_id).first()

def get_entradas(db: Session, skip: int = 0, limit: int = 100) -> List[models.Entrada]:
    """Busca todas as entradas com os sócios relacionados."""
    return db.query(models.Entrada).options(joinedload(models.Entrada.socios)).offset(skip).limit(limit).all()

def update_entrada(db: Session, entrada_id: int, entrada: schemas.EntradaCreate) -> models.Entrada:
    """
    Atualiza uma entrada existente, incluindo as porcentagens dos sócios.
    
    IMPORTANTE: Recalcula provisões e lançamentos contábeis automaticamente.
    """
    from .crud_provisoes import calcular_e_provisionar_entrada
    from . import crud_plano_contas
    
    db_entrada = db.query(models.Entrada).filter(models.Entrada.id == entrada_id).first()
    if not db_entrada:
        return None
    
    # Validar se o mês antigo está consolidado
    mes_antigo = db_entrada.data.strftime('%Y-%m')
    dre_mes_antigo = db.query(models.DREMensal).filter(models.DREMensal.mes == mes_antigo).first()
    if dre_mes_antigo and dre_mes_antigo.consolidado:
        raise ValueError(
            f"Não é possível editar entrada do mês {mes_antigo} pois ele já está consolidado. "
            "Desconsolide a DRE primeiro."
        )
    
    # Validar se o novo mês está consolidado (se a data mudou)
    mes_novo = entrada.data.strftime('%Y-%m')
    if mes_novo != mes_antigo:
        dre_mes_novo = db.query(models.DREMensal).filter(models.DREMensal.mes == mes_novo).first()
        if dre_mes_novo and dre_mes_novo.consolidado:
            raise ValueError(
                f"Não é possível mover entrada para o mês {mes_novo} pois ele já está consolidado. "
                "Desconsolide a DRE primeiro."
            )
    
    # Verificar se há pagamentos parciais já realizados para esta entrada
    # Se houver, bloquear edição
    lancamentos_pagamento = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.entrada_id == entrada_id,
        models.LancamentoContabil.tipo_lancamento.in_(['pagamento_pro_labore', 'pagamento_lucro', 'pagamento_imposto'])
    ).first()
    
    if lancamentos_pagamento:
        raise ValueError(
            "Não é possível editar esta entrada pois já existem pagamentos parciais realizados. "
            "Estorne os pagamentos antes de editar."
        )
    
    # 1. Deletar provisão antiga (se existir)
    provisao_antiga = db.query(models.ProvisaoEntrada).filter(
        models.ProvisaoEntrada.entrada_id == entrada_id
    ).first()
    if provisao_antiga:
        db.delete(provisao_antiga)
    
    # 2. Deletar lançamentos contábeis antigos (já configurado com cascade, mas fazemos explícito)
    db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.entrada_id == entrada_id
    ).delete()
    
    # 3. Atualizar campos básicos
    for key, value in entrada.dict(exclude={'socios'}).items():
        setattr(db_entrada, key, value)
    
    # 4. Se socios foram fornecidos, atualizar as porcentagens
    if entrada.socios:
        # 4a. Reverter os saldos dos sócios anteriores
        entradas_socios_antigas = db.query(models.EntradaSocio).filter(
            models.EntradaSocio.entrada_id == entrada_id
        ).all()
        
        for assoc in entradas_socios_antigas:
            socio = get_socio(db, socio_id=assoc.socio_id)
            if socio:
                valor_antigo = (assoc.percentual / 100) * db_entrada.valor
                socio.saldo -= valor_antigo
        
        # 4b. Excluir associações antigas
        db.query(models.EntradaSocio).filter(models.EntradaSocio.entrada_id == entrada_id).delete()
        
        # 4c. Criar novas associações e atualizar saldos
        for socio_assoc_data in entrada.socios:
            socio = get_socio(db, socio_id=socio_assoc_data.socio_id)
            if socio:
                valor_saldo = (socio_assoc_data.percentual / 100) * entrada.valor
                socio.saldo += valor_saldo
            
            db_assoc = models.EntradaSocio(
                entrada_id=entrada_id,
                socio_id=socio_assoc_data.socio_id,
                percentual=socio_assoc_data.percentual
            )
            db.add(db_assoc)
    
    db.commit()
    db.refresh(db_entrada)
    
    # Atualizar lançamentos contábeis dos meses afetados
    try:
        atualizar_lancamentos_mes(db, mes_novo)
        if mes_novo != mes_antigo:
            atualizar_lancamentos_mes(db, mes_antigo)
        db.commit()
    except Exception as e:
        db.rollback()
        raise ValueError(f"Erro ao atualizar lançamentos contábeis: {str(e)}")
    
    return db_entrada

def delete_entrada(db: Session, entrada_id: int) -> models.Entrada:
    """Exclui uma entrada revertendo efeitos em saldos, fundo e lançamentos.
    Passos:
    1. Carrega entrada e sócios associados.
    2. Reverte saldo dos sócios (parte que haviam recebido na criação).
    3. Reverte saldo do Fundo de Reserva.
    4. Remove provisão por entrada (se existir).
    5. Remove lançamentos contábeis ligados à entrada.
    6. Remove associações EntradaSocio e a própria entrada.
    """
    db_entrada = db.query(models.Entrada).filter(models.Entrada.id == entrada_id).first()
    if not db_entrada:
        return None
    
    # Validar se o mês está consolidado
    mes_entrada = db_entrada.data.strftime('%Y-%m')
    dre_mes = db.query(models.DREMensal).filter(models.DREMensal.mes == mes_entrada).first()
    if dre_mes and dre_mes.consolidado:
        raise ValueError(
            f"Não é possível deletar entrada do mês {mes_entrada} pois ele já está consolidado. "
            "Desconsolide a DRE primeiro."
        )

    # Configuração (percentual fundo)
    config = get_configuracao(db)
    percentual_fundo = config.percentual_fundo_reserva if config else 0.10
    valor_fundo = (db_entrada.valor or 0) * percentual_fundo
    valor_restante = (db_entrada.valor or 0) - valor_fundo

    # Reverter saldo dos sócios conforme percentuais da entrada
    entrada_socios = db.query(models.EntradaSocio).filter(models.EntradaSocio.entrada_id == entrada_id).all()
    for es in entrada_socios:
        socio = get_socio(db, es.socio_id)
        if socio:
            socio.saldo -= valor_restante * (es.percentual / 100.0)

    # Reverter fundo de reserva
    if valor_fundo > 0:
        fundo_reserva = get_or_create_fundo(db, "Fundo de Reserva")
        fundo_reserva.saldo = max(fundo_reserva.saldo - valor_fundo, 0.0)

    # Remover provisão por entrada (se ainda existir)
    provisao = db.query(models.ProvisaoEntrada).filter(models.ProvisaoEntrada.entrada_id == entrada_id).first()
    if provisao:
        db.delete(provisao)

    # Remover lançamentos contábeis vinculados
    db.query(models.LancamentoContabil).filter(models.LancamentoContabil.entrada_id == entrada_id).delete(synchronize_session=False)

    # Remover associações sócios
    db.query(models.EntradaSocio).filter(models.EntradaSocio.entrada_id == entrada_id).delete(synchronize_session=False)

    # Remover entrada
    db.delete(db_entrada)
    db.commit()
    
    # Recalcular lançamentos automáticos do mês para atualizar DRE
    atualizar_lancamentos_mes(db, mes_entrada)
    
    # Atualizar lançamentos contábeis do mês
    try:
        atualizar_lancamentos_mes(db, mes_entrada)
        db.commit()
    except Exception as e:
        db.rollback()
        raise ValueError(f"Erro ao atualizar lançamentos contábeis: {str(e)}")
    
    return db_entrada

# =================================================================
# CRUD for Despesa (with business logic)
# =================================================================


def create_despesa(db: Session, despesa: schemas.DespesaCreate) -> models.Despesa:
    """
    Cria uma nova despesa e deduz o valor do saldo dos sócios responsáveis.
    """
    # Validar se o mês está consolidado
    mes_despesa = despesa.data.strftime('%Y-%m')
    dre_mes = db.query(models.DREMensal).filter(models.DREMensal.mes == mes_despesa).first()
    if dre_mes and dre_mes.consolidado:
        raise ValueError(
            f"Não é possível criar despesa no mês {mes_despesa} pois ele já está consolidado. "
            "Desconsolide a DRE primeiro."
        )
    
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
    
    # Atualizar lançamentos contábeis do mês
    try:
        atualizar_lancamentos_mes(db, mes_despesa)
        db.commit()
    except Exception as e:
        db.rollback()
        raise ValueError(f"Erro ao atualizar lançamentos contábeis: {str(e)}")
    
    return db_despesa

def get_despesas(db: Session, skip: int = 0, limit: int = 100) -> List[models.Despesa]:
    """Busca todas as despesas com os responsáveis relacionados."""
    return db.query(models.Despesa).options(joinedload(models.Despesa.responsaveis)).offset(skip).limit(limit).all()

def update_despesa(db: Session, despesa_id: int, despesa: schemas.DespesaCreate) -> models.Despesa:
    """Atualiza uma despesa existente, incluindo os responsáveis."""
    db_despesa = db.query(models.Despesa).filter(models.Despesa.id == despesa_id).first()
    if not db_despesa:
        return None
    
    # Validar se o mês antigo está consolidado
    mes_antigo = db_despesa.data.strftime('%Y-%m')
    dre_mes_antigo = db.query(models.DREMensal).filter(models.DREMensal.mes == mes_antigo).first()
    if dre_mes_antigo and dre_mes_antigo.consolidado:
        raise ValueError(
            f"Não é possível editar despesa do mês {mes_antigo} pois ele já está consolidado. "
            "Desconsolide a DRE primeiro."
        )
    
    # Validar se o novo mês está consolidado (se a data mudou)
    mes_novo = despesa.data.strftime('%Y-%m')
    if mes_novo != mes_antigo:
        dre_mes_novo = db.query(models.DREMensal).filter(models.DREMensal.mes == mes_novo).first()
        if dre_mes_novo and dre_mes_novo.consolidado:
            raise ValueError(
                f"Não é possível mover despesa para o mês {mes_novo} pois ele já está consolidado. "
                "Desconsolide a DRE primeiro."
            )
    
    # Atualizar campos básicos
    for key, value in despesa.dict(exclude={'responsaveis'}).items():
        setattr(db_despesa, key, value)
    
    # Se responsaveis foram fornecidos, atualizar
    if despesa.responsaveis:
        # 1. Reverter os saldos dos responsáveis anteriores
        despesas_socios_antigas = db.query(models.DespesaSocio).filter(
            models.DespesaSocio.despesa_id == despesa_id
        ).all()
        
        num_responsaveis_antigos = len(despesas_socios_antigas)
        if num_responsaveis_antigos > 0:
            valor_por_responsavel_antigo = db_despesa.valor / num_responsaveis_antigos
            for assoc in despesas_socios_antigas:
                socio = get_socio(db, socio_id=assoc.socio_id)
                if socio:
                    socio.saldo += valor_por_responsavel_antigo
        
        # 2. Excluir associações antigas
        db.query(models.DespesaSocio).filter(models.DespesaSocio.despesa_id == despesa_id).delete()
        
        # 3. Criar novas associações e atualizar saldos
        num_novos_responsaveis = len(despesa.responsaveis)
        if num_novos_responsaveis > 0:
            valor_por_responsavel_novo = despesa.valor / num_novos_responsaveis
            for resp_assoc_data in despesa.responsaveis:
                socio = get_socio(db, socio_id=resp_assoc_data.socio_id)
                if socio:
                    socio.saldo -= valor_por_responsavel_novo
                
                db_assoc = models.DespesaSocio(
                    despesa_id=despesa_id,
                    socio_id=resp_assoc_data.socio_id
                )
                db.add(db_assoc)
    
    db.commit()
    db.refresh(db_despesa)
    
    # Atualizar lançamentos contábeis dos meses afetados
    try:
        atualizar_lancamentos_mes(db, mes_novo)
        if mes_novo != mes_antigo:
            atualizar_lancamentos_mes(db, mes_antigo)
        db.commit()
    except Exception as e:
        db.rollback()
        raise ValueError(f"Erro ao atualizar lançamentos contábeis: {str(e)}")
    
    return db_despesa

def delete_despesa(db: Session, despesa_id: int) -> models.Despesa:
    """Exclui uma despesa."""
    db_despesa = db.query(models.Despesa).filter(models.Despesa.id == despesa_id).first()
    if not db_despesa:
        return None
    
    # Validar se o mês está consolidado
    mes_despesa = db_despesa.data.strftime('%Y-%m')
    dre_mes = db.query(models.DREMensal).filter(models.DREMensal.mes == mes_despesa).first()
    if dre_mes and dre_mes.consolidado:
        raise ValueError(
            f"Não é possível deletar despesa do mês {mes_despesa} pois ele já está consolidado. "
            "Desconsolide a DRE primeiro."
        )
    
    # Excluir associações com sócios responsáveis primeiro
    db.query(models.DespesaSocio).filter(models.DespesaSocio.despesa_id == despesa_id).delete()
    
    db.delete(db_despesa)
    db.commit()
    
    # Atualizar lançamentos contábeis do mês
    try:
        atualizar_lancamentos_mes(db, mes_despesa)
        db.commit()
    except Exception as e:
        db.rollback()
        raise ValueError(f"Erro ao atualizar lançamentos contábeis: {str(e)}")
    
    return db_despesa

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
# Funções auxiliares para UPDATE de lançamentos (padrão UPSERT)
# =================================================================

def atualizar_ou_criar_lancamento(
    db: Session,
    mes: str,
    tipo_lancamento: str,
    conta_debito_id: int,
    conta_credito_id: int,
    valor: float,
    historico: str,
    data: date_type
) -> models.LancamentoContabil:
    """
    Atualiza um lançamento existente ou cria novo se não existir (padrão UPSERT).
    
    Busca pela chave composta: (referencia_mes, tipo_lancamento, conta_debito_id, conta_credito_id, automatico=True)
    
    Args:
        db: Sessão do banco de dados
        mes: Mês de referência no formato YYYY-MM
        tipo_lancamento: Tipo do lançamento (receita, despesa, simples, inss_provisao, etc.)
        conta_debito_id: ID da conta de débito
        conta_credito_id: ID da conta de crédito
        valor: Valor do lançamento
        historico: Descrição do lançamento
        data: Data do lançamento
    
    Returns:
        Lançamento contábil atualizado ou criado
    """
    from datetime import datetime
    
    # Buscar lançamento existente pela chave composta
    existente = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.referencia_mes == mes,
        models.LancamentoContabil.tipo_lancamento == tipo_lancamento,
        models.LancamentoContabil.conta_debito_id == conta_debito_id,
        models.LancamentoContabil.conta_credito_id == conta_credito_id,
        models.LancamentoContabil.automatico == True
    ).first()
    
    if existente:
        # UPDATE: atualizar apenas campos que podem mudar
        existente.valor = valor
        existente.historico = historico
        existente.data = data
        existente.editado_em = datetime.utcnow()
        db.flush()
        return existente
    else:
        # INSERT: criar novo lançamento
        novo = models.LancamentoContabil(
            data=data,
            conta_debito_id=conta_debito_id,
            conta_credito_id=conta_credito_id,
            valor=valor,
            historico=historico,
            automatico=True,
            editavel=False,
            tipo_lancamento=tipo_lancamento,
            referencia_mes=mes
        )
        db.add(novo)
        db.flush()
        return novo


def deletar_lancamento_se_existir(
    db: Session,
    mes: str,
    tipo_lancamento: str,
    conta_debito_id: int,
    conta_credito_id: int
) -> None:
    """
    Deleta um lançamento automático específico se ele existir.
    
    Usado quando um valor vai para zero (ex: despesas = 0) e não queremos
    manter lançamento com valor zero no razão.
    
    Args:
        db: Sessão do banco de dados
        mes: Mês de referência no formato YYYY-MM
        tipo_lancamento: Tipo do lançamento
        conta_debito_id: ID da conta de débito
        conta_credito_id: ID da conta de crédito
    """
    db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.referencia_mes == mes,
        models.LancamentoContabil.tipo_lancamento == tipo_lancamento,
        models.LancamentoContabil.conta_debito_id == conta_debito_id,
        models.LancamentoContabil.conta_credito_id == conta_credito_id,
        models.LancamentoContabil.automatico == True
    ).delete(synchronize_session=False)

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

def calcular_pro_labore_iterativo(lucro_bruto: float, percentual_contrib_admin: float = 100.0, salario_minimo: float = 1518.0) -> tuple:
    """
    Calcula o pró-labore e INSS de forma iterativa.
    
    O pró-labore é composto por:
    - 5% do lucro líquido (parte administrativa)
    - 85% do lucro líquido × percentual de contribuição do administrador
    - Limitado ao salário mínimo
    
    O lucro líquido depende do INSS patronal (20% do pró-labore), criando uma dependência circular.
    IMPORTANTE: O pró-labore NÃO é despesa na DRE, apenas o INSS PATRONAL (20%) é!
    O INSS PESSOAL (11%) é desconto do funcionário, não é despesa da empresa.
    
    Fórmulas:
    - pró-labore = min(lucro_líquido * 5% + lucro_líquido * 85% * %contrib, salário_mínimo)
    - INSS_patronal = pró-labore * 20% ← Despesa na DRE (iterativa)
    - INSS_pessoal = pró-labore * 11% ← Desconto do funcionário (não é despesa)
    - lucro_líquido = lucro_bruto - INSS_patronal (não desconta pró-labore nem INSS pessoal)
    
    Args:
        lucro_bruto: Lucro bruto do mês (receita - impostos - despesas gerais)
        percentual_contrib_admin: % de contribuição do administrador (0-100, ex: 50.0 para 50%)
        salario_minimo: Valor do salário mínimo (default 1518.0)
    
    Returns:
        tuple: (pro_labore, inss_patronal, inss_pessoal, lucro_liquido)
    """
    PERCENTUAL_ADMINISTRADOR = 0.05  # 5%
    PERCENTUAL_LUCRO_DISPONIVEL = 0.85  # 85%
    ALIQUOTA_INSS_PESSOAL = 0.11  # 11%
    ALIQUOTA_INSS_PATRONAL = 0.20  # 20%
    
    # Se o lucro bruto for negativo ou zero, não há pró-labore
    if lucro_bruto <= 0:
        return (0.0, 0.0, 0.0, lucro_bruto)
    
    # Converter percentual de contribuição para decimal (50.0 → 0.5)
    contrib_decimal = percentual_contrib_admin / 100.0
    
    # Inicializar com pró-labore = 0
    pro_labore = 0.0
    
    # Iteração até convergência (diferença < R$ 0.01)
    max_iterations = 100
    tolerance = 0.01
    
    for _ in range(max_iterations):
        # Calcular APENAS INSS PATRONAL (20%) como despesa na DRE
        # INSS Pessoal (11%) é desconto do funcionário, não é despesa da empresa
        inss_patronal = pro_labore * ALIQUOTA_INSS_PATRONAL
        
        # Calcular lucro líquido (apenas INSS patronal é despesa, pro-labore NÃO)
        lucro_liquido = lucro_bruto - inss_patronal
        
        # Calcular novo pró-labore
        # = 5% do lucro líquido + (85% do lucro líquido × % contribuição do admin)
        parte_admin = lucro_liquido * PERCENTUAL_ADMINISTRADOR
        parte_lucro = lucro_liquido * PERCENTUAL_LUCRO_DISPONIVEL * contrib_decimal
        pro_labore_novo = min(parte_admin + parte_lucro, salario_minimo)
        
        # Se o pró-labore ficar negativo, zerar
        if pro_labore_novo < 0:
            pro_labore_novo = 0.0
        
        # Verificar convergência
        diferenca = abs(pro_labore_novo - pro_labore)
        if diferenca < tolerance:
            pro_labore = pro_labore_novo
            break
        
        pro_labore = pro_labore_novo
    
    # Calcular valores finais
    inss_patronal = pro_labore * ALIQUOTA_INSS_PATRONAL
    inss_pessoal = pro_labore * ALIQUOTA_INSS_PESSOAL
    # Lucro líquido: apenas INSS patronal é despesa na DRE (INSS pessoal é desconto do funcionário)
    lucro_liquido = lucro_bruto - inss_patronal
    
    return (pro_labore, inss_patronal, inss_pessoal, lucro_liquido)


def calcular_impostos_previstos_mes(db: Session, mes: str) -> dict:
    """
    Calcula impostos previstos do mês SEM gravar no banco.
    Útil para mostrar valores em tempo real no balanço quando mês não está consolidado.
    
    Args:
        db: Sessão do banco de dados
        mes: Mês no formato YYYY-MM
        
    Returns:
        dict com imposto_simples, inss_patronal, inss_pessoal, receita_bruta, despesas_gerais, lucro_liquido
    """
    from utils.datas import ultimos_12_meses, inicio_do_mes, fim_do_mes
    from utils.simples import calcular_faixa_simples, calcular_imposto_simples
    from sqlalchemy import func
    
    inicio = inicio_do_mes(mes)
    fim = fim_do_mes(mes)
    
    # Calcular receita bruta do mês
    receita_bruta = db.query(func.sum(models.Entrada.valor)).filter(
        models.Entrada.data >= inicio,
        models.Entrada.data <= fim
    ).scalar() or 0.0
    
    # Calcular receita acumulada 12 meses
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
    
    # Calcular faixa Simples e alíquotas
    try:
        aliquota, deducao, aliquota_efetiva = calcular_faixa_simples(receita_12m, inicio, db)
    except ValueError:
        aliquota = 0.0
        deducao = 0.0
        aliquota_efetiva = 0.0
    
    # Calcular imposto do mês
    imposto_simples = calcular_imposto_simples(receita_bruta, aliquota_efetiva)
    
    # Calcular despesas gerais do mês
    despesas_gerais = db.query(func.sum(models.Despesa.valor)).filter(
        models.Despesa.data >= inicio,
        models.Despesa.data <= fim
    ).scalar() or 0.0
    
    # Calcular lucro bruto e INSS
    lucro_bruto = receita_bruta - imposto_simples - despesas_gerais
    
    # Calcular percentual de contribuição do administrador
    admin_socio = db.query(models.Socio).filter(
        models.Socio.funcao.ilike('%administrador%')
    ).first()
    
    percentual_contrib_admin = 100.0
    if admin_socio:
        entradas_mes = db.query(models.Entrada).filter(
            models.Entrada.data >= inicio,
            models.Entrada.data <= fim
        ).all()
        
        contribuicao_admin = 0.0
        faturamento_total = 0.0
        
        for entrada in entradas_mes:
            faturamento_total += float(entrada.valor or 0)
            entrada_socio = db.query(models.EntradaSocio).filter(
                models.EntradaSocio.entrada_id == entrada.id,
                models.EntradaSocio.socio_id == admin_socio.id
            ).first()
            
            if entrada_socio:
                percentual = float(entrada_socio.percentual or 0)
                contribuicao_admin += float(entrada.valor or 0) * (percentual / 100)
        
        if faturamento_total > 0:
            percentual_contrib_admin = (contribuicao_admin / faturamento_total) * 100
    
    config = get_configuracao(db)
    salario_minimo = config.salario_minimo if config else 1518.0
    pro_labore, inss_patronal, inss_pessoal, lucro_liquido = calcular_pro_labore_iterativo(
        lucro_bruto,
        percentual_contrib_admin,
        salario_minimo
    )
    
    return {
        'imposto_simples': imposto_simples,
        'inss_patronal': inss_patronal,
        'inss_pessoal': inss_pessoal,
        'receita_bruta': receita_bruta,
        'despesas_gerais': despesas_gerais,
        'lucro_bruto': lucro_bruto,
        'lucro_liquido': lucro_liquido
    }


def atualizar_lancamentos_mes(db: Session, mes: str) -> dict:
    """
    Recalcula todos os lançamentos contábeis automáticos de um mês específico.
    
    Esta função é chamada sempre que uma entrada ou despesa é criada, editada ou deletada.
    Ela:
    1. Calcula a DRE do mês em tempo real
    2. Deleta lançamentos automáticos antigos (exceto fechamento/reserva/consolidação)
    3. Recria lançamentos: Receitas, Despesas, Simples (PROVISÃO), INSS Provisão, Fechamento, Reserva
    
    Args:
        db: Sessão do banco de dados
        mes: Mês no formato YYYY-MM
        
    Returns:
        dict com valores calculados da DRE
    """
    from utils.datas import ultimos_12_meses, inicio_do_mes, fim_do_mes
    from utils.simples import calcular_faixa_simples, calcular_imposto_simples
    from database.crud_plano_contas import buscar_conta_por_codigo, registrar_fechamento_resultado
    from sqlalchemy import func
    import calendar
    
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
    except ValueError:
        aliquota = 0.0
        deducao = 0.0
        aliquota_efetiva = 0.0
    
    # 4. Calcular imposto do mês
    imposto = calcular_imposto_simples(receita_bruta, aliquota_efetiva)
    
    # 5. Calcular despesas gerais do mês
    despesas_gerais = db.query(func.sum(models.Despesa.valor)).filter(
        models.Despesa.data >= inicio,
        models.Despesa.data <= fim
    ).scalar() or 0.0
    
    # 6. Calcular lucro bruto e INSS
    lucro_bruto = receita_bruta - imposto - despesas_gerais
    
    # Calcular percentual de contribuição do administrador
    admin_socio = db.query(models.Socio).filter(
        models.Socio.funcao.ilike('%administrador%')
    ).first()
    
    percentual_contrib_admin = 100.0
    if admin_socio:
        entradas_mes = db.query(models.Entrada).filter(
            models.Entrada.data >= inicio,
            models.Entrada.data <= fim
        ).all()
        
        contribuicao_admin = 0.0
        faturamento_total = 0.0
        
        for entrada in entradas_mes:
            faturamento_total += float(entrada.valor or 0)
            entrada_socio = db.query(models.EntradaSocio).filter(
                models.EntradaSocio.entrada_id == entrada.id,
                models.EntradaSocio.socio_id == admin_socio.id
            ).first()
            
            if entrada_socio:
                percentual = float(entrada_socio.percentual or 0)
                contribuicao_admin += float(entrada.valor or 0) * (percentual / 100)
        
        if faturamento_total > 0:
            percentual_contrib_admin = (contribuicao_admin / faturamento_total) * 100
    
    config = get_configuracao(db)
    salario_minimo = config.salario_minimo if config else 1518.0
    pro_labore, inss_patronal, inss_pessoal, lucro_liquido = calcular_pro_labore_iterativo(
        lucro_bruto,
        percentual_contrib_admin,
        salario_minimo
    )
    
    # 7. Calcular reserva 10%
    reserva_10p = lucro_liquido * 0.10
    lucro_disponivel = lucro_liquido - reserva_10p
    
    # 8. NOVO: Não deletar mais - usar padrão UPDATE para preservar IDs
    # (Removido: DELETE de lançamentos automáticos)
    
    # 9. Buscar contas do plano
    conta_caixa = buscar_conta_por_codigo(db, "1.1.1")
    conta_receita = buscar_conta_por_codigo(db, "4.1.1")
    conta_despesa_geral = buscar_conta_por_codigo(db, "5.1.1")  # Pró-labore ou despesas gerais
    conta_simples = buscar_conta_por_codigo(db, "5.3.1")
    conta_simples_pagar = buscar_conta_por_codigo(db, "2.1.4")  # Simples a Pagar
    conta_inss_despesa = buscar_conta_por_codigo(db, "5.1.3")
    conta_inss_recolher = buscar_conta_por_codigo(db, "2.1.5")
    conta_lucros_distribuidos = buscar_conta_por_codigo(db, "3.4.1")
    
    if not all([conta_caixa, conta_receita, conta_despesa_geral, conta_simples, conta_simples_pagar,
                conta_inss_despesa, conta_inss_recolher, conta_lucros_distribuidos]):
        raise ValueError("Uma ou mais contas essenciais não encontradas no plano de contas")
    
    ano_int = int(mes.split('-')[0])
    mes_int = int(mes.split('-')[1])
    dia = calendar.monthrange(ano_int, mes_int)[1]
    data_lcto = date_type(ano_int, mes_int, dia)
    
    lancamentos_criados = []
    
    # 10. NOVO: Atualizar ou criar lançamentos de receita (padrão UPDATE)
    if receita_bruta > 0:
        atualizar_ou_criar_lancamento(
            db=db,
            mes=mes,
            tipo_lancamento='receita',
            conta_debito_id=conta_caixa.id,
            conta_credito_id=conta_receita.id,
            valor=receita_bruta,
            historico=f"Receita de honorários - {mes}",
            data=data_lcto
        )
        lancamentos_criados.append('receita')
    else:
        # Se receita zerou, deletar lançamento existente
        deletar_lancamento_se_existir(db, mes, 'receita', conta_caixa.id, conta_receita.id)
    
    # 11. NOVO: Atualizar ou criar lançamentos de despesas (padrão UPDATE)
    if despesas_gerais > 0:
        atualizar_ou_criar_lancamento(
            db=db,
            mes=mes,
            tipo_lancamento='despesa',
            conta_debito_id=conta_despesa_geral.id,
            conta_credito_id=conta_caixa.id,
            valor=despesas_gerais,
            historico=f"Despesas gerais - {mes}",
            data=data_lcto
        )
        lancamentos_criados.append('despesa')
    else:
        # Se despesas zeraram, deletar lançamento existente
        deletar_lancamento_se_existir(db, mes, 'despesa', conta_despesa_geral.id, conta_caixa.id)
    
    # 12. NOVO: Atualizar ou criar lançamento de Simples (PROVISÃO em 2.1.4)
    if imposto > 0:
        atualizar_ou_criar_lancamento(
            db=db,
            mes=mes,
            tipo_lancamento='simples',
            conta_debito_id=conta_simples.id,
            conta_credito_id=conta_simples_pagar.id,  # Provisão: C 2.1.4 em vez de C 1.1.1
            valor=imposto,
            historico=f"Provisão Simples Nacional - {mes}",
            data=data_lcto
        )
        lancamentos_criados.append('simples')
    else:
        # Se imposto zerou, deletar lançamento existente
        deletar_lancamento_se_existir(db, mes, 'simples', conta_simples.id, conta_simples_pagar.id)
    
    # 13. NOVO: Atualizar ou criar lançamentos de INSS (padrão UPDATE)
    if inss_patronal > 0:
        # INSS Patronal (despesa)
        atualizar_ou_criar_lancamento(
            db=db,
            mes=mes,
            tipo_lancamento='inss_provisao',
            conta_debito_id=conta_inss_despesa.id,
            conta_credito_id=conta_inss_recolher.id,
            valor=inss_patronal,
            historico=f"INSS Patronal (20%) - {mes}",
            data=data_lcto
        )
        lancamentos_criados.append('inss_patronal')
    else:
        # Se INSS patronal zerou, deletar lançamento existente
        deletar_lancamento_se_existir(db, mes, 'inss_provisao', conta_inss_despesa.id, conta_inss_recolher.id)
    
    if inss_pessoal > 0:
        # INSS Pessoal (11%) - vai para mesma conta que INSS Patronal (2.1.5)
        # D 3.4.1 (Lucros Distribuídos) / C 2.1.5 (INSS a Recolher)
        atualizar_ou_criar_lancamento(
            db=db,
            mes=mes,
            tipo_lancamento='inss_pessoal',
            conta_debito_id=conta_lucros_distribuidos.id,
            conta_credito_id=conta_inss_recolher.id,
            valor=inss_pessoal,
            historico=f"INSS Pessoal (11%) - Retenção - {mes}",
            data=data_lcto
        )
        lancamentos_criados.append('inss_pessoal')
    else:
        # Se INSS pessoal zerou, deletar lançamento existente
        deletar_lancamento_se_existir(db, mes, 'inss_pessoal', conta_lucros_distribuidos.id, conta_inss_recolher.id)
    
    # 14. Registrar fechamento do resultado (D 4.9.9 / C 3.3)
    registrar_fechamento_resultado(db, mes, lucro_liquido, recriar=True)
    lancamentos_criados.append('fechamento')
    
    # 15. Alocar reserva legal (D 3.3 / C 3.2.1)
    if reserva_10p > 0:
        alocar_reserva_legal(db, mes, reserva_10p)
        lancamentos_criados.append('reserva')
    
    db.flush()
    
    return {
        'receita_bruta': receita_bruta,
        'receita_12m': receita_12m,
        'aliquota_efetiva': aliquota_efetiva,
        'imposto': imposto,
        'despesas_gerais': despesas_gerais,
        'lucro_bruto': lucro_bruto,
        'pro_labore': pro_labore,
        'inss_patronal': inss_patronal,
        'inss_pessoal': inss_pessoal,
        'lucro_liquido': lucro_liquido,
        'reserva_10p': reserva_10p,
        'lucro_disponivel': lucro_disponivel,
        'lancamentos_criados': lancamentos_criados
    }


def cobrir_deficit_caixa(db: Session, valor_necessario: float, mes: str) -> Optional[models.LancamentoContabil]:
    """
    Transfere recursos do Fundo Reserva para Caixa quando necessário.
    
    Args:
        db: Sessão do banco
        valor_necessario: Valor que precisa estar disponível em caixa
        mes: Mês de referência no formato YYYY-MM
        
    Returns:
        Lançamento contábil de cobertura ou None se não for necessário
    """
    from database.crud_plano_contas import buscar_conta_por_codigo, calcular_saldo_conta
    import calendar
    
    # Verificar saldo do caixa
    conta_caixa = buscar_conta_por_codigo(db, "1.1.1")
    if not conta_caixa:
        raise ValueError("Conta 1.1.1 (Caixa) não encontrada")
    
    saldo_caixa = calcular_saldo_conta(db, conta_caixa.id)
    
    # Se já tem saldo suficiente, não precisa cobrir
    if saldo_caixa >= valor_necessario:
        return None
    
    deficit = valor_necessario - saldo_caixa
    
    # Verificar saldo do Fundo Reserva
    conta_fundo = buscar_conta_por_codigo(db, "3.2.1")
    if not conta_fundo:
        raise ValueError("Conta 3.2.1 (Fundo Reserva) não encontrada")
    
    saldo_fundo = calcular_saldo_conta(db, conta_fundo.id)
    
    if saldo_fundo < deficit:
        raise ValueError(f"Fundo Reserva insuficiente. Necessário: R$ {deficit:.2f}, Disponível: R$ {saldo_fundo:.2f}")
    
    # Criar lançamento de cobertura: D 1.1.1 (Caixa) / C 3.2.1 (Fundo Reserva)
    ano_int = int(mes.split('-')[0])
    mes_int = int(mes.split('-')[1])
    dia = calendar.monthrange(ano_int, mes_int)[1]
    data_lcto = date_type(ano_int, mes_int, dia)
    
    lanc_cobertura = models.LancamentoContabil(
        data=data_lcto,
        conta_debito_id=conta_caixa.id,
        conta_credito_id=conta_fundo.id,
        valor=deficit,
        historico=f"Cobertura de déficit de caixa - {mes}",
        automatico=True,
        editavel=False,
        tipo_lancamento='cobertura_deficit',
        referencia_mes=mes
    )
    db.add(lanc_cobertura)
    db.flush()
    
    return lanc_cobertura


def distribuir_lucros_socios(db: Session, mes: str, lucro_disponivel: float) -> List[models.LancamentoContabil]:
    """
    Distribui lucros para os sócios proporcionalmente aos seus percentuais.
    
    Args:
        db: Sessão do banco
        mes: Mês de referência no formato YYYY-MM
        lucro_disponivel: Valor de lucro a ser distribuído (já descontada a reserva legal)
        
    Returns:
        Lista de lançamentos contábeis criados
    """
    from database.crud_plano_contas import buscar_conta_por_codigo
    import calendar
    
    if lucro_disponivel <= 0:
        return []
    
    # Buscar conta de origem (Lucros Distribuídos - Débito)
    conta_retencao = buscar_conta_por_codigo(db, "3.4.1")
    if not conta_retencao:
        raise ValueError("Conta 3.4.1 (Lucros Distribuídos) não encontrada")
    
    # Buscar todos os sócios ativos
    socios = db.query(models.Socio).order_by(models.Socio.id).all()
    if not socios:
        raise ValueError("Nenhum sócio cadastrado no sistema")
    
    # Calcular total de percentuais
    total_percentual = sum(float(s.percentual or 0) for s in socios)
    if total_percentual <= 0:
        raise ValueError("Total de percentuais dos sócios é zero ou inválido")
    
    ano_int = int(mes.split('-')[0])
    mes_int = int(mes.split('-')[1])
    dia = calendar.monthrange(ano_int, mes_int)[1]
    data_lcto = date_type(ano_int, mes_int, dia)
    
    lancamentos = []
    
    # PRIMEIRO: Deletar lançamentos existentes de distribuição de lucros deste mês
    # para evitar duplicação ao reconsolidar
    db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.tipo_lancamento == 'distribuicao_lucro',
        models.LancamentoContabil.referencia_mes == mes
    ).delete(synchronize_session=False)
    
    for idx, socio in enumerate(socios, start=1):
        percentual = float(socio.percentual or 0)
        if percentual <= 0:
            continue
        
        # Calcular valor proporcional
        valor_socio = lucro_disponivel * (percentual / total_percentual)
        
        # Buscar conta individual do sócio (2.1.7.X)
        codigo_conta_socio = f"2.1.7.{idx}"
        conta_socio = buscar_conta_por_codigo(db, codigo_conta_socio)
        
        if not conta_socio:
            raise ValueError(f"Conta {codigo_conta_socio} (Lucros a Distribuir - {socio.nome}) não encontrada")
        
        # Criar lançamento: D 3.4.1 / C 2.1.7.X
        lanc_dist = models.LancamentoContabil(
            data=data_lcto,
            conta_debito_id=conta_retencao.id,
            conta_credito_id=conta_socio.id,
            valor=valor_socio,
            historico=f"Distribuição de lucros - {socio.nome} ({percentual:.2f}%) - {mes}",
            automatico=True,
            editavel=False,
            tipo_lancamento='distribuicao_lucro',
            referencia_mes=mes
        )
        db.add(lanc_dist)
        lancamentos.append(lanc_dist)
    
    db.flush()
    return lancamentos


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
    
    # IMPORTANTE: Atualizar lançamentos automáticos ANTES de consolidar
    # Isso garante que provisões (receita, despesa, simples, inss, fechamento, reserva)
    # estejam atualizadas baseadas nas entradas/despesas do banco.
    # A função atualizar_lancamentos_mes usa padrão UPDATE, então não duplica.
    atualizar_lancamentos_mes(db, mes)
    
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
    
    # 5. Calcular despesas gerais do mês
    despesas_gerais = db.query(func.sum(models.Despesa.valor)).filter(
        models.Despesa.data >= inicio,
        models.Despesa.data <= fim
    ).scalar() or 0.0
    
    # 6. Calcular lucro bruto (antes de pró-labore e INSS)
    lucro_bruto = receita_bruta - imposto - despesas_gerais
    
    # 7. Calcular percentual de contribuição do administrador no mês
    admin_socio = db.query(models.Socio).filter(
        models.Socio.funcao.ilike('%administrador%')
    ).first()
    
    percentual_contrib_admin = 100.0  # Default se não tiver sócio admin
    
    if admin_socio:
        # Calcular contribuição do admin no mês
        entradas_mes = db.query(models.Entrada).filter(
            models.Entrada.data >= inicio,
            models.Entrada.data <= fim
        ).all()
        
        contribuicao_admin = 0.0
        faturamento_total = 0.0
        
        for entrada in entradas_mes:
            faturamento_total += float(entrada.valor or 0)
            entrada_socio = db.query(models.EntradaSocio).filter(
                models.EntradaSocio.entrada_id == entrada.id,
                models.EntradaSocio.socio_id == admin_socio.id
            ).first()
            
            if entrada_socio:
                percentual = float(entrada_socio.percentual or 0)
                contribuicao_admin += float(entrada.valor or 0) * (percentual / 100)
        
        if faturamento_total > 0:
            percentual_contrib_admin = (contribuicao_admin / faturamento_total) * 100
    
    # 8. Calcular pró-labore e INSS de forma iterativa
    config = get_configuracao(db)
    salario_minimo = config.salario_minimo if config else 1518.0
    pro_labore, inss_patronal, inss_pessoal, lucro_liquido = calcular_pro_labore_iterativo(
        lucro_bruto, 
        percentual_contrib_admin,
        salario_minimo
    )
    
    # 9. Calcular reserva 10%
    reserva_10p = lucro_liquido * 0.10
    
    # 10. Salvar ou atualizar DRE
    if dre_existente:
        dre_existente.receita_bruta = receita_bruta
        dre_existente.receita_12m = receita_12m
        dre_existente.aliquota = aliquota
        dre_existente.aliquota_efetiva = aliquota_efetiva
        dre_existente.deducao = deducao
        dre_existente.imposto = imposto
        dre_existente.pro_labore = pro_labore
        dre_existente.inss_patronal = inss_patronal
        dre_existente.inss_pessoal = inss_pessoal
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
            pro_labore=pro_labore,
            inss_patronal=inss_patronal,
            inss_pessoal=inss_pessoal,
            despesas_gerais=despesas_gerais,
            lucro_liquido=lucro_liquido,
            reserva_10p=reserva_10p,
            consolidado=True,
            data_consolidacao=datetime.utcnow()
        )
        db.add(db_dre)
    
    db.commit()
    db.refresh(db_dre)

    # Lançamentos de provisão removidos - não mais automáticos

    # Registrar fechamento do resultado no razão para refletir no PL (3.3) - OBRIGATÓRIO
    # SEMPRE recriar para garantir atualização após desconsolidar/excluir/reconsolidar
    from database.crud_plano_contas import registrar_fechamento_resultado, buscar_conta_por_codigo
    registrar_fechamento_resultado(db, mes, db_dre.lucro_liquido, recriar=True)
    
    # Alocar 10% para reserva legal
    if db_dre.reserva_10p > 0:
        alocar_reserva_legal(db, mes, db_dre.reserva_10p)
    else:
        # Se reserva zerou, deletar lançamento existente
        db.query(models.LancamentoContabil).filter(
            models.LancamentoContabil.tipo_lancamento == 'alocacao_reserva',
            models.LancamentoContabil.referencia_mes == mes
        ).delete(synchronize_session=False)
    
    # ========== PAGAMENTOS E DISTRIBUIÇÃO (QUANDO CONSOLIDAR) ==========
    
    # IMPORTANTE: Remover lançamentos de consolidação existentes para evitar duplicação
    # ao reconsolidar (quando forcar_recalculo=True)
    tipos_consolidacao = ['pagamento_simples', 'pagamento_inss', 'cobertura_deficit']
    db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.referencia_mes == mes,
        models.LancamentoContabil.tipo_lancamento.in_(tipos_consolidacao)
    ).delete(synchronize_session=False)
    db.flush()
    
    import calendar
    conta_caixa = buscar_conta_por_codigo(db, "1.1.1")
    ano_int = int(mes.split('-')[0])
    mes_int = int(mes.split('-')[1])
    dia = calendar.monthrange(ano_int, mes_int)[1]
    data_lcto = date_type(ano_int, mes_int, dia)
    
    # 1. Calcular INSS total a pagar (31%: 20% patronal + 11% pessoal)
    inss_total = inss_patronal + inss_pessoal
    
    # 2. Calcular total de impostos a pagar (Simples + INSS)
    total_impostos = imposto + inss_total
    
    if total_impostos > 0:
        # 3. Validar e cobrir déficit de caixa se necessário
        try:
            cobrir_deficit_caixa(db, total_impostos, mes)
        except ValueError as e:
            db.rollback()
            raise ValueError(f"Erro ao consolidar DRE: {str(e)}")
    
    # 4. Criar lançamento de pagamento do SIMPLES: D 2.1.4 (Simples a Pagar) / C 1.1.1 (Caixa)
    if imposto > 0:
        conta_simples_pagar = buscar_conta_por_codigo(db, "2.1.4")
        
        if not conta_simples_pagar or not conta_caixa:
            db.rollback()
            raise ValueError("Contas 2.1.4 ou 1.1.1 não encontradas")
        
        lanc_pgto_simples = models.LancamentoContabil(
            data=data_lcto,
            conta_debito_id=conta_simples_pagar.id,
            conta_credito_id=conta_caixa.id,
            valor=imposto,
            historico=f"Pagamento Simples Nacional - {mes}",
            automatico=True,
            editavel=False,
            tipo_lancamento='pagamento_simples',
            referencia_mes=mes
        )
        db.add(lanc_pgto_simples)
    
    # 5. Criar lançamento de pagamento do INSS: D 2.1.5 (INSS a Recolher) / C 1.1.1 (Caixa)
    if inss_total > 0:
        conta_inss_recolher = buscar_conta_por_codigo(db, "2.1.5")
        
        if not conta_inss_recolher or not conta_caixa:
            db.rollback()
            raise ValueError("Contas 2.1.5 ou 1.1.1 não encontradas")
        
        lanc_pgto_inss = models.LancamentoContabil(
            data=data_lcto,
            conta_debito_id=conta_inss_recolher.id,
            conta_credito_id=conta_caixa.id,
            valor=inss_total,
            historico=f"Pagamento INSS (31%: 20% Patronal + 11% Pessoal) - {mes}",
            automatico=True,
            editavel=False,
            tipo_lancamento='pagamento_inss',
            referencia_mes=mes
        )
        db.add(lanc_pgto_inss)
    
    # 6. Distribuir lucros aos sócios (85% do lucro líquido após reserva)
    lucro_disponivel = lucro_liquido - reserva_10p
    if lucro_disponivel > 0:
        try:
            distribuir_lucros_socios(db, mes, lucro_disponivel)
        except ValueError as e:
            db.rollback()
            raise ValueError(f"Erro ao distribuir lucros: {str(e)}")
    
    db.commit()
    
    return db_dre

def desconsolidar_dre_mes(db: Session, mes: str) -> Optional[models.DREMensal]:
    """
    Desconsolida um mês de DRE, permitindo recalcular posteriormente.
    Remove lançamentos de consolidação (pagamento Simples, pagamento INSS, distribuição lucro, cobertura déficit).
    
    Args:
        db: Sessão do banco
        mes: Mês no formato YYYY-MM
    
    Returns:
        DREMensal desconsolidado ou None se não existir
    """
    dre = db.query(models.DREMensal).filter(models.DREMensal.mes == mes).first()
    if dre:
        # Deletar lançamentos de consolidação
        tipos_consolidacao = ['pagamento_simples', 'pagamento_inss', 'distribuicao_lucro', 'cobertura_deficit']
        db.query(models.LancamentoContabil).filter(
            models.LancamentoContabil.referencia_mes == mes,
            models.LancamentoContabil.tipo_lancamento.in_(tipos_consolidacao)
        ).delete(synchronize_session=False)
        
        # Recalcular lançamentos automáticos do mês
        atualizar_lancamentos_mes(db, mes)
        
        # Marcar DRE como não consolidado
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

def calcular_percentual_participacao_socio(db: Session, socio_id: int, mes: str) -> float:
    """
    Calcula o percentual de participação de um sócio nas entradas de um mês específico.
    
    Args:
        db: Sessão do banco de dados
        socio_id: ID do sócio
        mes: String no formato 'YYYY-MM'
    
    Returns:
        Percentual de participação (0.0 a 100.0)
    """
    from utils.datas import inicio_do_mes, fim_do_mes
    
    inicio = inicio_do_mes(mes)
    fim = fim_do_mes(mes)
    
    # Buscar todas as entradas do mês
    entradas = db.query(models.Entrada).filter(
        models.Entrada.data >= inicio,
        models.Entrada.data <= fim
    ).all()
    
    if not entradas:
        return 0.0
    
    # Calcular total de entradas e contribuição do sócio
    entrada_total = 0.0
    socio_total = 0.0
    
    for entrada in entradas:
        valor_entrada = float(entrada.valor or 0)
        entrada_total += valor_entrada
        
        # Buscar participação do sócio nesta entrada
        entrada_socio = db.query(models.EntradaSocio).filter(
            models.EntradaSocio.entrada_id == entrada.id,
            models.EntradaSocio.socio_id == socio_id
        ).first()
        
        if entrada_socio:
            percentual = float(entrada_socio.percentual or 0)
            socio_total += valor_entrada * (percentual / 100.0)
    
    # Calcular percentual de participação
    if entrada_total > 0:
        return (socio_total / entrada_total) * 100.0
    else:
        return 0.0


# =================================================================
# DEPRECIAÇÃO DE ATIVOS IMOBILIZADOS
# =================================================================

def calcular_depreciacao_prevista_mes(db: Session, mes: int, ano: int):
    """
    Calcula a depreciação prevista para o mês sem gravar no banco.
    Retorna valores para conta de despesa (5.2.9) e redutora (1.2.9).
    """
    from backend.config_data import DEPRECIACAO_PADRAO_BR, CATEGORIAS_ATIVOS, CONTAS_DEPRECIACAO
    from utils.datas import fim_do_mes
    
    # Data de referência (fim do mês)
    data_ref = fim_do_mes(f"{ano}-{mes:02d}")
    
    # Buscar todos os ativos imobilizados ativos e elegíveis
    ativos = db.query(models.AtivoImobilizado).filter(
        models.AtivoImobilizado.ativo == True,
        models.AtivoImobilizado.elegivel_depreciacao == True,
        models.AtivoImobilizado.data_aquisicao <= data_ref
    ).all()
    
    if not ativos:
        return {
            'despesa': 0.0,
            'acumulada': 0.0,
            'total': 0.0,
            'detalhes': []
        }
    
    total_depreciacao = 0.0
    detalhes = []
    
    for ativo in ativos:
        # Identificar categoria do ativo
        categoria = ativo.categoria.lower() if ativo.categoria else 'imobilizado_geral'
        
        # Se categoria não estiver nas taxas padrão, tentar mapear por palavras-chave
        if categoria not in DEPRECIACAO_PADRAO_BR:
            descricao_lower = ativo.descricao.lower()
            categoria_encontrada = False
            
            for cat_key, palavras in CATEGORIAS_ATIVOS.items():
                if any(palavra in descricao_lower for palavra in palavras):
                    categoria = cat_key
                    categoria_encontrada = True
                    break
            
            if not categoria_encontrada:
                categoria = 'imobilizado_geral'
        
        # Obter taxa de depreciação anual
        taxa_anual = DEPRECIACAO_PADRAO_BR.get(categoria, DEPRECIACAO_PADRAO_BR['imobilizado_geral'])
        
        # Calcular depreciação mensal
        valor_aquisicao = float(ativo.valor_aquisicao or 0)
        depreciacao_mensal = valor_aquisicao * (taxa_anual / 12)
        
        total_depreciacao += depreciacao_mensal
        
        detalhes.append({
            'ativo_id': ativo.id,
            'descricao': ativo.descricao,
            'categoria': categoria,
            'valor_aquisicao': valor_aquisicao,
            'taxa_anual': taxa_anual,
            'depreciacao_mensal': depreciacao_mensal
        })
    
    return {
        'despesa': total_depreciacao,           # Conta 5.2.9 (despesa - aumenta)
        'acumulada': total_depreciacao,         # Conta 1.2.9 (redutora do ativo - aumenta)
        'total': total_depreciacao,
        'detalhes': detalhes,
        'conta_despesa': CONTAS_DEPRECIACAO['despesa'],
        'conta_redutora': CONTAS_DEPRECIACAO['redutora']
    }


def gerar_alertas(db: Session, mes: int, ano: int, ajustes: dict = None):
    """
    Gera alertas contextuais sobre o estado financeiro do mês.
    Verifica saldo de caixa, uso de fundos, impostos a pagar, etc.
    """
    from backend.config_data import ALERTAS_CONFIG
    from utils.datas import fim_do_mes
    
    alertas = []
    
    # Buscar saldo de caixa
    conta_caixa = crud_plano_contas.buscar_conta_por_codigo(db, '1.1.1')
    if conta_caixa:
        data_fim = fim_do_mes(f"{ano}-{mes:02d}")
        saldo_caixa = crud_plano_contas.calcular_saldo_conta(db, conta_caixa.id, data_fim=data_fim)
        
        # Calcular total de impostos a pagar
        impostos_total = 0.0
        if ajustes:
            impostos_total = ajustes.get('2.1.4', 0) + ajustes.get('2.1.5', 0)
        
        # Verificar se caixa é suficiente
        if saldo_caixa < impostos_total:
            deficit = impostos_total - saldo_caixa
            
            # Verificar saldo do fundo de reserva
            conta_fundo = crud_plano_contas.buscar_conta_por_codigo(db, '3.2.1')
            if conta_fundo:
                saldo_fundo = crud_plano_contas.calcular_saldo_conta(db, conta_fundo.id, data_fim=data_fim)
                
                if saldo_fundo >= deficit:
                    percentual_uso = (deficit / saldo_fundo) * 100 if saldo_fundo > 0 else 0
                    
                    alertas.append({
                        'tipo': 'warning',
                        'icone': '⚠️',
                        'mensagem': f'Será necessário usar R$ {deficit:.2f} do Fundo de Reserva para pagar impostos ({percentual_uso:.1f}% do fundo).'
                    })
                    
                    # Alerta adicional se usar muito do fundo
                    if percentual_uso > (ALERTAS_CONFIG['percentual_uso_fundo'] * 100):
                        alertas.append({
                            'tipo': 'danger',
                            'icone': '🔴',
                            'mensagem': f'ATENÇÃO: Uso elevado do Fundo de Reserva! Considere reduzir despesas ou aumentar receitas.'
                        })
                else:
                    falta = deficit - saldo_fundo
                    alertas.append({
                        'tipo': 'danger',
                        'icone': '🔴',
                        'mensagem': f'CRÍTICO: Caixa e Fundo insuficientes! Faltam R$ {falta:.2f} para pagar os impostos.'
                    })
            else:
                alertas.append({
                    'tipo': 'danger',
                    'icone': '🔴',
                    'mensagem': f'Caixa insuficiente e Fundo de Reserva não encontrado. Déficit: R$ {deficit:.2f}'
                })
        else:
            saldo_apos = saldo_caixa - impostos_total
            alertas.append({
                'tipo': 'success',
                'icone': '✅',
                'mensagem': f'Caixa suficiente para pagar todos os impostos. Saldo após pagamento: R$ {saldo_apos:.2f}'
            })
        
        # Alertar sobre caixa baixo
        if saldo_caixa < ALERTAS_CONFIG['saldo_minimo_caixa']:
            alertas.append({
                'tipo': 'warning',
                'icone': '⚠️',
                'mensagem': f'Saldo de caixa abaixo do mínimo recomendado (R$ {ALERTAS_CONFIG["saldo_minimo_caixa"]:.2f}). Saldo atual: R$ {saldo_caixa:.2f}'
            })
    
    # Verificar lucro disponível para distribuição
    if ajustes and '2.1.7' in ajustes:
        lucro_disponivel = ajustes['2.1.7']
        if lucro_disponivel > 0:
            alertas.append({
                'tipo': 'info',
                'icone': '💰',
                'mensagem': f'Lucro disponível para distribuição aos sócios: R$ {lucro_disponivel:.2f}'
            })
        elif lucro_disponivel < 0:
            alertas.append({
                'tipo': 'warning',
                'icone': '📉',
                'mensagem': f'Prejuízo no mês: R$ {abs(lucro_disponivel):.2f}. Considere revisar despesas.'
            })
    
    # Alertar sobre depreciação significativa
    if ajustes and '5.2.9' in ajustes:
        depreciacao = ajustes['5.2.9']
        if depreciacao > 500:  # Mais de R$ 500 em depreciação
            alertas.append({
                'tipo': 'info',
                'icone': '📊',
                'mensagem': f'Depreciação mensal de ativos: R$ {depreciacao:.2f}'
            })
    
    return alertas


# =================================================================
# CRUD DE ATIVOS IMOBILIZADOS
# =================================================================

def create_ativo_imobilizado(db: Session, ativo_data: dict):
    """Cria um novo ativo imobilizado"""
    ativo = models.AtivoImobilizado(**ativo_data)
    db.add(ativo)
    db.commit()
    db.refresh(ativo)
    return ativo


def get_ativo_imobilizado(db: Session, ativo_id: int):
    """Busca um ativo imobilizado pelo ID"""
    return db.query(models.AtivoImobilizado).filter(
        models.AtivoImobilizado.id == ativo_id
    ).first()


def listar_ativos_imobilizados(db: Session, apenas_ativos: bool = True):
    """Lista todos os ativos imobilizados"""
    query = db.query(models.AtivoImobilizado)
    if apenas_ativos:
        query = query.filter(models.AtivoImobilizado.ativo == True)
    return query.order_by(models.AtivoImobilizado.data_aquisicao.desc()).all()


def update_ativo_imobilizado(db: Session, ativo_id: int, ativo_data: dict):
    """Atualiza um ativo imobilizado"""
    ativo = get_ativo_imobilizado(db, ativo_id)
    if not ativo:
        return None
    
    for key, value in ativo_data.items():
        if hasattr(ativo, key):
            setattr(ativo, key, value)
    
    db.commit()
    db.refresh(ativo)
    return ativo


def delete_ativo_imobilizado(db: Session, ativo_id: int):
    """Desativa um ativo imobilizado (soft delete)"""
    ativo = get_ativo_imobilizado(db, ativo_id)
    if not ativo:
        return False
    
    ativo.ativo = False
    db.commit()
    return True


# =================================================================
# CRUD DE SAQUES DE FUNDOS
# =================================================================

def registrar_saque_fundo(db: Session, saque_data: dict):
    """
    Registra um saque do fundo de reserva ou investimento.
    Valida saldo disponível e cria lançamento contábil.
    """
    from utils.datas import fim_do_mes
    
    # Validar campos obrigatórios
    required_fields = ['data', 'valor', 'tipo_fundo', 'beneficiario_id', 'motivo']
    for field in required_fields:
        if field not in saque_data:
            raise ValueError(f"Campo obrigatório ausente: {field}")
    
    tipo_fundo = saque_data['tipo_fundo']
    valor = float(saque_data['valor'])
    data_saque = saque_data['data']
    
    # Determinar conta do fundo
    if tipo_fundo == 'reserva':
        codigo_fundo = '3.2.1'  # Fundo de Reserva
    elif tipo_fundo == 'investimento':
        codigo_fundo = '3.2.2'  # Fundo de Investimento
    else:
        raise ValueError(f"Tipo de fundo inválido: {tipo_fundo}")
    
    # Buscar conta do fundo
    conta_fundo = crud_plano_contas.buscar_conta_por_codigo(db, codigo_fundo)
    if not conta_fundo:
        raise ValueError(f"Conta do fundo não encontrada: {codigo_fundo}")
    
    # Validar saldo disponível
    saldo_fundo = crud_plano_contas.calcular_saldo_conta(db, conta_fundo.id, data_fim=data_saque)
    if saldo_fundo < valor:
        raise ValueError(f"Saldo insuficiente no fundo. Disponível: R$ {saldo_fundo:.2f}, Solicitado: R$ {valor:.2f}")
    
    # Buscar conta de caixa
    conta_caixa = crud_plano_contas.buscar_conta_por_codigo(db, '1.1.1')
    if not conta_caixa:
        raise ValueError("Conta de caixa não encontrada: 1.1.1")
    
    # Criar lançamento contábil: D Fundo / C Caixa
    lancamento = models.LancamentoContabil(
        data=data_saque,
        valor=valor,
        conta_debito_id=conta_fundo.id,      # Debita o fundo (reduz PL)
        conta_credito_id=conta_caixa.id,     # Credita o caixa (aumenta ativo)
        historico=f"Saque {tipo_fundo} - {saque_data['motivo'][:100]}",
        tipo_lancamento='saque_fundo',
        automatico=False,
        editavel=True
    )
    db.add(lancamento)
    db.flush()
    
    # Criar registro de saque
    saque = models.SaqueFundo(
        data=data_saque,
        valor=valor,
        tipo_fundo=tipo_fundo,
        beneficiario_id=saque_data['beneficiario_id'],
        motivo=saque_data['motivo'],
        comprovante_path=saque_data.get('comprovante_path'),
        lancamento_id=lancamento.id,
        criado_por=saque_data.get('criado_por')
    )
    db.add(saque)
    db.commit()
    db.refresh(saque)
    
    return saque


def listar_saques_fundo(db: Session, tipo_fundo: str = None, beneficiario_id: int = None):
    """Lista saques de fundos com filtros opcionais"""
    query = db.query(models.SaqueFundo)
    
    if tipo_fundo:
        query = query.filter(models.SaqueFundo.tipo_fundo == tipo_fundo)
    
    if beneficiario_id:
        query = query.filter(models.SaqueFundo.beneficiario_id == beneficiario_id)
    
    return query.order_by(models.SaqueFundo.data.desc()).all()


def get_saque_fundo(db: Session, saque_id: int):
    """Busca um saque de fundo pelo ID"""
    return db.query(models.SaqueFundo).filter(
        models.SaqueFundo.id == saque_id
    ).first()


# =================================================================
# CRUD for Operações Contábeis Padronizadas
# =================================================================

def inicializar_operacoes(db: Session):
    """Cria as 8 operações contábeis padronizadas no banco de dados"""
    operacoes_padrao = [
        {"codigo": "REC_HON", "nome": "Receber honorários", "descricao": "Recebimento de honorários: D-Caixa / C-Receita", "ordem": 1},
        {"codigo": "RESERVAR_FUNDO", "nome": "Reservar fundo", "descricao": "Transferência para fundo de reserva: D-Lucros Acum. / C-Reserva", "ordem": 2},
        {"codigo": "PRO_LABORE", "nome": "Pró-labore (bruto)", "descricao": "Pagamento de pró-labore com INSS: D-Despesa Pró-labore / C-Caixa (líquido 89%) + C-INSS a Recolher (11%)", "ordem": 3},
        {"codigo": "INSS_PATRONAL", "nome": "INSS patronal", "descricao": "Provisão INSS patronal: D-Despesa INSS patronal / C-INSS a Recolher", "ordem": 4},
        {"codigo": "PAGAR_INSS", "nome": "Pagar INSS", "descricao": "Pagamento de INSS acumulado: D-INSS a Recolher / C-Caixa", "ordem": 5},
        {"codigo": "DISTRIBUIR_LUCROS", "nome": "Distribuir lucros", "descricao": "Distribuição de lucros aos sócios: D-Lucros Acum. / C-Caixa", "ordem": 6},
        {"codigo": "PAGAR_DESPESA_FUNDO", "nome": "Pagar despesa via fundo", "descricao": "Pagamento de despesa usando fundo de reserva: D-Outras Despesas / C-Caixa", "ordem": 7},
        {"codigo": "BAIXAR_FUNDO", "nome": "Baixa do fundo", "descricao": "Transferência do fundo de volta para lucros: D-Reserva / C-Lucros Acum.", "ordem": 8},
        {"codigo": "PAGAR_ALUGUEL", "nome": "Pagar aluguel", "descricao": "Despesa de aluguel: D-Aluguel / C-Caixa", "ordem": 9},
        {"codigo": "PAGAR_AGUA_LUZ", "nome": "Pagar água/luz", "descricao": "Despesa de água/luz: D-Água e Luz / C-Caixa", "ordem": 10},
        {"codigo": "PAGAR_INTERNET", "nome": "Pagar internet/telefone", "descricao": "Despesa de internet/telefone: D-Internet e Telefone / C-Caixa", "ordem": 11},
        {"codigo": "PAGAR_MATERIAL", "nome": "Pagar material de escritório", "descricao": "Despesa de material de escritório: D-Material de Escritório / C-Caixa", "ordem": 12},
        {"codigo": "DEPRECIAR_IMOBILIZADO", "nome": "Depreciar imobilizado", "descricao": "Depreciação de imobilizado: D-Depreciação / C-Depreciação Acumulada. Não permite duplicidade no mesmo mês.", "ordem": 13},
    ]
    
    for op_data in operacoes_padrao:
        # Verifica se já existe
        existe = db.query(models.Operacao).filter(models.Operacao.codigo == op_data["codigo"]).first()
        if not existe:
            operacao = models.Operacao(**op_data)
            db.add(operacao)
    
    db.commit()


def listar_operacoes_disponiveis(db: Session) -> List[models.Operacao]:
    """Lista todas as operações contábeis disponíveis"""
    return db.query(models.Operacao).filter(
        models.Operacao.ativo == True
    ).order_by(models.Operacao.ordem).all()


def get_operacao_por_codigo(db: Session, codigo: str) -> Optional[models.Operacao]:
    """Busca uma operação pelo código"""
    return db.query(models.Operacao).filter(
        models.Operacao.codigo == codigo,
        models.Operacao.ativo == True
    ).first()


def _executar_receber_honorarios(db: Session, operacao_contabil: models.OperacaoContabil, valor: float, data: date_type, descricao: str):
    """Operação 1: Receber honorários - D-Caixa / C-Receita"""
    from database.crud_plano_contas import buscar_conta_por_codigo
    
    conta_caixa = buscar_conta_por_codigo(db, "1.1")
    conta_receita = buscar_conta_por_codigo(db, "4.1")
    
    if not conta_caixa or not conta_receita:
        raise ValueError("Contas contábeis não encontradas. Certifique-se que o plano de contas está inicializado.")
    
    lancamento = models.LancamentoContabil(
        data=data,
        valor=valor,
        conta_debito_id=conta_caixa.id,
        conta_credito_id=conta_receita.id,
        historico=descricao or f"Recebimento de honorários - {data.strftime('%d/%m/%Y')}",
        tipo_lancamento='operacao_padrao',
        automatico=True,
        editavel=False,
        operacao_contabil_id=operacao_contabil.id,
        referencia_mes=operacao_contabil.mes_referencia
    )
    db.add(lancamento)


def _executar_reservar_fundo(db: Session, operacao_contabil: models.OperacaoContabil, valor: float, data: date_type, descricao: str):
    """Operação 2: Reservar fundo - D-Lucros Acum. / C-Reserva"""
    from database.crud_plano_contas import buscar_conta_por_codigo
    
    conta_lucros_acum = buscar_conta_por_codigo(db, "3.2")
    conta_reserva = buscar_conta_por_codigo(db, "3.1")
    
    if not conta_lucros_acum or not conta_reserva:
        raise ValueError("Contas contábeis não encontradas.")
    
    lancamento = models.LancamentoContabil(
        data=data,
        valor=valor,
        conta_debito_id=conta_lucros_acum.id,
        conta_credito_id=conta_reserva.id,
        historico=descricao or f"Transferência para fundo de reserva - {data.strftime('%d/%m/%Y')}",
        tipo_lancamento='operacao_padrao',
        automatico=True,
        editavel=False,
        operacao_contabil_id=operacao_contabil.id,
        referencia_mes=operacao_contabil.mes_referencia
    )
    db.add(lancamento)


def _executar_pro_labore(db: Session, operacao_contabil: models.OperacaoContabil, valor: float, data: date_type, descricao: str):
    """Operação 3: Pró-labore (bruto) - D-Despesa Pró-labore / C-Caixa (89%) + C-INSS a Recolher (11%)"""
    from database.crud_plano_contas import buscar_conta_por_codigo
    
    conta_despesa_pl = buscar_conta_por_codigo(db, "5.1")
    conta_caixa = buscar_conta_por_codigo(db, "1.1")
    conta_inss = buscar_conta_por_codigo(db, "2.1")
    
    if not conta_despesa_pl or not conta_caixa or not conta_inss:
        raise ValueError("Contas contábeis não encontradas.")
    
    # Calcular valores
    valor_inss = valor * 0.11  # 11% de INSS
    valor_liquido = valor * 0.89  # 89% líquido
    
    # Lançamento 1: Débito despesa pró-labore (valor bruto)
    # Lançamento 2: Crédito caixa (valor líquido)
    lancamento1 = models.LancamentoContabil(
        data=data,
        valor=valor_liquido,
        conta_debito_id=conta_despesa_pl.id,
        conta_credito_id=conta_caixa.id,
        historico=descricao or f"Pró-labore líquido (89%) - {data.strftime('%d/%m/%Y')}",
        tipo_lancamento='operacao_padrao',
        automatico=True,
        editavel=False,
        operacao_contabil_id=operacao_contabil.id,
        referencia_mes=operacao_contabil.mes_referencia
    )
    db.add(lancamento1)
    
    # Lançamento 3: Crédito INSS a recolher (11%)
    lancamento2 = models.LancamentoContabil(
        data=data,
        valor=valor_inss,
        conta_debito_id=conta_despesa_pl.id,
        conta_credito_id=conta_inss.id,
        historico=f"INSS sobre pró-labore (11%) - {data.strftime('%d/%m/%Y')}",
        tipo_lancamento='operacao_padrao',
        automatico=True,
        editavel=False,
        operacao_contabil_id=operacao_contabil.id,
        referencia_mes=operacao_contabil.mes_referencia
    )
    db.add(lancamento2)


def _executar_inss_patronal(db: Session, operacao_contabil: models.OperacaoContabil, valor: float, data: date_type, descricao: str):
    """Operação 4: INSS patronal - D-Despesa INSS patronal / C-INSS a Recolher"""
    from database.crud_plano_contas import buscar_conta_por_codigo
    
    conta_despesa_inss = buscar_conta_por_codigo(db, "5.2")
    conta_inss = buscar_conta_por_codigo(db, "2.1")
    
    if not conta_despesa_inss or not conta_inss:
        raise ValueError("Contas contábeis não encontradas.")
    
    lancamento = models.LancamentoContabil(
        data=data,
        valor=valor,
        conta_debito_id=conta_despesa_inss.id,
        conta_credito_id=conta_inss.id,
        historico=descricao or f"INSS patronal - {data.strftime('%d/%m/%Y')}",
        tipo_lancamento='operacao_padrao',
        automatico=True,
        editavel=False,
        operacao_contabil_id=operacao_contabil.id,
        referencia_mes=operacao_contabil.mes_referencia
    )
    db.add(lancamento)


def _executar_pagar_inss(db: Session, operacao_contabil: models.OperacaoContabil, valor: float, data: date_type, descricao: str):
    """Operação 5: Pagar INSS - D-INSS a Recolher / C-Caixa"""
    from database.crud_plano_contas import buscar_conta_por_codigo
    
    conta_inss = buscar_conta_por_codigo(db, "2.1")
    conta_caixa = buscar_conta_por_codigo(db, "1.1")
    
    if not conta_inss or not conta_caixa:
        raise ValueError("Contas contábeis não encontradas.")
    
    # Validar se há saldo suficiente em INSS a Recolher
    saldo_inss = calcular_saldo_conta(db, conta_inss.id)
    if saldo_inss < valor:
        raise ValueError(f"Saldo insuficiente em INSS a Recolher. Saldo atual: R$ {saldo_inss:.2f}")
    
    lancamento = models.LancamentoContabil(
        data=data,
        valor=valor,
        conta_debito_id=conta_inss.id,
        conta_credito_id=conta_caixa.id,
        historico=descricao or f"Pagamento de INSS - {data.strftime('%d/%m/%Y')}",
        tipo_lancamento='operacao_padrao',
        automatico=True,
        editavel=False,
        operacao_contabil_id=operacao_contabil.id,
        referencia_mes=operacao_contabil.mes_referencia
    )
    db.add(lancamento)


def _executar_distribuir_lucros(db: Session, operacao_contabil: models.OperacaoContabil, valor: float, data: date_type, descricao: str):
    """Operação 6: Distribuir lucros - D-Lucros Acum. / C-Caixa"""
    from database.crud_plano_contas import buscar_conta_por_codigo
    
    conta_lucros_acum = buscar_conta_por_codigo(db, "3.2")
    conta_caixa = buscar_conta_por_codigo(db, "1.1")
    
    if not conta_lucros_acum or not conta_caixa:
        raise ValueError("Contas contábeis não encontradas.")
    
    # Validar se há saldo suficiente em Lucros Acumulados
    saldo_lucros = calcular_saldo_conta(db, conta_lucros_acum.id)
    if saldo_lucros < valor:
        raise ValueError(f"Saldo insuficiente em Lucros Acumulados. Saldo atual: R$ {saldo_lucros:.2f}")
    
    lancamento = models.LancamentoContabil(
        data=data,
        valor=valor,
        conta_debito_id=conta_lucros_acum.id,
        conta_credito_id=conta_caixa.id,
        historico=descricao or f"Distribuição de lucros - {data.strftime('%d/%m/%Y')}",
        tipo_lancamento='operacao_padrao',
        automatico=True,
        editavel=False,
        operacao_contabil_id=operacao_contabil.id,
        referencia_mes=operacao_contabil.mes_referencia
    )
    db.add(lancamento)


def _executar_pagar_despesa_fundo(db: Session, operacao_contabil: models.OperacaoContabil, valor: float, data: date_type, descricao: str):
    """Operação 7: Pagar despesa via fundo - D-Outras Despesas / C-Caixa"""
    from database.crud_plano_contas import buscar_conta_por_codigo
    
    conta_outras_despesas = buscar_conta_por_codigo(db, "5.3")
    conta_caixa = buscar_conta_por_codigo(db, "1.1")
    
    if not conta_outras_despesas or not conta_caixa:
        raise ValueError("Contas contábeis não encontradas.")
    
    lancamento = models.LancamentoContabil(
        data=data,
        valor=valor,
        conta_debito_id=conta_outras_despesas.id,
        conta_credito_id=conta_caixa.id,
        historico=descricao or f"Pagamento de despesa - {data.strftime('%d/%m/%Y')}",
        tipo_lancamento='operacao_padrao',
        automatico=True,
        editavel=False,
        operacao_contabil_id=operacao_contabil.id,
        referencia_mes=operacao_contabil.mes_referencia
    )
    db.add(lancamento)


def _executar_baixar_fundo(db: Session, operacao_contabil: models.OperacaoContabil, valor: float, data: date_type, descricao: str):
    """Operação 8: Baixa do fundo - D-Reserva / C-Lucros Acum."""
    from database.crud_plano_contas import buscar_conta_por_codigo
    
    conta_reserva = buscar_conta_por_codigo(db, "3.1")
    conta_lucros_acum = buscar_conta_por_codigo(db, "3.2")
    
    if not conta_reserva or not conta_lucros_acum:
        raise ValueError("Contas contábeis não encontradas.")
    
    # Validar se há saldo suficiente em Reserva
    saldo_reserva = calcular_saldo_conta(db, conta_reserva.id)
    if saldo_reserva < valor:
        raise ValueError(f"Saldo insuficiente em Reserva. Saldo atual: R$ {saldo_reserva:.2f}")
    
    lancamento = models.LancamentoContabil(
        data=data,
        valor=valor,
        conta_debito_id=conta_reserva.id,
        conta_credito_id=conta_lucros_acum.id,
        historico=descricao or f"Baixa do fundo de reserva - {data.strftime('%d/%m/%Y')}",
        tipo_lancamento='operacao_padrao',
        automatico=True,
        editavel=False,
        operacao_contabil_id=operacao_contabil.id,
        referencia_mes=operacao_contabil.mes_referencia
    )
    db.add(lancamento)


def executar_operacao(
    db: Session,
    operacao_codigo: str,
    valor: float,
    data: date_type,
    descricao: Optional[str] = None,
    socio_id: Optional[int] = None,
    usuario_id: Optional[int] = None
) -> models.OperacaoContabil:
    """
    Executa uma operação contábil padronizada e gera os lançamentos contábeis correspondentes.
    
    Args:
        operacao_codigo: Código da operação (REC_HON, RESERVAR_FUNDO, etc.)
        valor: Valor da operação
        data: Data da operação
        descricao: Descrição opcional
        socio_id: ID do sócio (para operações relacionadas a sócios)
        usuario_id: ID do usuário que está executando a operação
    
    Returns:
        OperacaoContabil criada com seus lançamentos
    """
    # Buscar operação
    operacao = get_operacao_por_codigo(db, operacao_codigo)
    if not operacao:
        raise ValueError(f"Operação '{operacao_codigo}' não encontrada ou inativa.")
    
    # Calcular mês de referência
    mes_referencia = data.strftime('%Y-%m')
    
    # Criar registro da operação
    operacao_contabil = models.OperacaoContabil(
        operacao_id=operacao.id,
        data=data,
        valor=valor,
        descricao=descricao,
        mes_referencia=mes_referencia,
        socio_id=socio_id,
        criado_por_id=usuario_id
    )
    db.add(operacao_contabil)
    db.flush()  # Para obter o ID
    
    # Executar a operação específica
    executores = {
        "REC_HON": _executar_receber_honorarios,
        "RESERVAR_FUNDO": _executar_reservar_fundo,
        "PRO_LABORE": _executar_pro_labore,
        "INSS_PATRONAL": _executar_inss_patronal,
        "PAGAR_INSS": _executar_pagar_inss,
        "DISTRIBUIR_LUCROS": _executar_distribuir_lucros,
        "PAGAR_DESPESA_FUNDO": _executar_pagar_despesa_fundo,
        "BAIXAR_FUNDO": _executar_baixar_fundo,
    }
    
    executor = executores.get(operacao_codigo)
    if not executor:
        raise ValueError(f"Executor não implementado para operação '{operacao_codigo}'.")
    
    # Executar e gerar lançamentos
    executor(db, operacao_contabil, valor, data, descricao or "")
    
    db.commit()
    db.refresh(operacao_contabil)
    
    return operacao_contabil


def listar_historico_operacoes(
    db: Session,
    mes_referencia: Optional[str] = None,
    operacao_codigo: Optional[str] = None,
    socio_id: Optional[int] = None,
    incluir_cancelados: bool = False
) -> List[models.OperacaoContabil]:
    """
    Lista o histórico de operações contábeis executadas.
    
    Args:
        mes_referencia: Filtrar por mês (formato YYYY-MM)
        operacao_codigo: Filtrar por código de operação
        socio_id: Filtrar por sócio
        incluir_cancelados: Se deve incluir operações canceladas
    """
    query = db.query(models.OperacaoContabil).options(
        joinedload(models.OperacaoContabil.operacao),
        joinedload(models.OperacaoContabil.socio),
        joinedload(models.OperacaoContabil.lancamentos)
    )
    
    if not incluir_cancelados:
        query = query.filter(models.OperacaoContabil.cancelado == False)
    
    if mes_referencia:
        query = query.filter(models.OperacaoContabil.mes_referencia == mes_referencia)
    
    if operacao_codigo:
        query = query.join(models.Operacao).filter(models.Operacao.codigo == operacao_codigo)
    
    if socio_id:
        query = query.filter(models.OperacaoContabil.socio_id == socio_id)
    
    return query.order_by(models.OperacaoContabil.data.desc()).all()


def cancelar_operacao(db: Session, operacao_contabil_id: int) -> models.OperacaoContabil:
    """
    Cancela uma operação contábil e remove seus lançamentos.
    
    Args:
        operacao_contabil_id: ID da operação a cancelar
    
    Returns:
        OperacaoContabil cancelada
    """
    operacao_contabil = db.query(models.OperacaoContabil).filter(
        models.OperacaoContabil.id == operacao_contabil_id
    ).first()
    
    if not operacao_contabil:
        raise ValueError(f"Operação contábil #{operacao_contabil_id} não encontrada.")
    
    if operacao_contabil.cancelado:
        raise ValueError(f"Operação contábil #{operacao_contabil_id} já está cancelada.")
    
    # Remover todos os lançamentos associados
    db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.operacao_contabil_id == operacao_contabil_id
    ).delete()
    
    # Marcar como cancelado
    operacao_contabil.cancelado = True
    operacao_contabil.data_cancelamento = datetime.utcnow()
    
    db.commit()
    db.refresh(operacao_contabil)
    
    return operacao_contabil


def get_operacao_contabil(db: Session, operacao_contabil_id: int) -> Optional[models.OperacaoContabil]:
    """Busca uma operação contábil pelo ID com relacionamentos"""
    return db.query(models.OperacaoContabil).options(
        joinedload(models.OperacaoContabil.operacao),
        joinedload(models.OperacaoContabil.socio),
        joinedload(models.OperacaoContabil.lancamentos).joinedload(models.LancamentoContabil.conta_debito),
        joinedload(models.OperacaoContabil.lancamentos).joinedload(models.LancamentoContabil.conta_credito)
    ).filter(
        models.OperacaoContabil.id == operacao_contabil_id
    ).first()

    # ================================
    # NOVAS OPERAÇÕES DE DESPESA
    # ================================
    from database.crud_plano_contas import buscar_conta_por_codigo, calcular_saldo_conta
    from datetime import datetime

    def _executar_pagar_aluguel(db: Session, operacao_contabil: models.OperacaoContabil, valor: float, data: date_type, descricao: str):
        """Despesa de aluguel: D-Aluguel / C-Caixa"""
        conta_aluguel = buscar_conta_por_codigo(db, "5.2.1")
        conta_caixa = buscar_conta_por_codigo(db, "1.1.1")
        if not conta_aluguel or not conta_caixa:
            raise ValueError("Contas contábeis não encontradas.")
        saldo_caixa = calcular_saldo_conta(db, conta_caixa.id)
        if saldo_caixa < valor:
            raise ValueError(f"Saldo insuficiente em Caixa. Saldo atual: R$ {saldo_caixa:.2f}")
        lancamento = models.LancamentoContabil(
            data=data,
            valor=valor,
            conta_debito_id=conta_aluguel.id,
            conta_credito_id=conta_caixa.id,
            historico=descricao or f"Pagamento de aluguel - {data.strftime('%d/%m/%Y')}",
            tipo_lancamento='operacao_padrao',
            automatico=True,
            editavel=False,
            operacao_contabil_id=operacao_contabil.id,
            referencia_mes=operacao_contabil.mes_referencia
        )
        db.add(lancamento)

    def _executar_pagar_agua_luz(db: Session, operacao_contabil: models.OperacaoContabil, valor: float, data: date_type, descricao: str):
        """Despesa de água/luz: D-Água e Luz / C-Caixa"""
        conta_agua_luz = buscar_conta_por_codigo(db, "5.2.2")
        conta_caixa = buscar_conta_por_codigo(db, "1.1.1")
        if not conta_agua_luz or not conta_caixa:
            raise ValueError("Contas contábeis não encontradas.")
        saldo_caixa = calcular_saldo_conta(db, conta_caixa.id)
        if saldo_caixa < valor:
            raise ValueError(f"Saldo insuficiente em Caixa. Saldo atual: R$ {saldo_caixa:.2f}")
        lancamento = models.LancamentoContabil(
            data=data,
            valor=valor,
            conta_debito_id=conta_agua_luz.id,
            conta_credito_id=conta_caixa.id,
            historico=descricao or f"Pagamento de água/luz - {data.strftime('%d/%m/%Y')}",
            tipo_lancamento='operacao_padrao',
            automatico=True,
            editavel=False,
            operacao_contabil_id=operacao_contabil.id,
            referencia_mes=operacao_contabil.mes_referencia
        )
        db.add(lancamento)

    def _executar_pagar_internet(db: Session, operacao_contabil: models.OperacaoContabil, valor: float, data: date_type, descricao: str):
        """Despesa de internet/telefone: D-Internet e Telefone / C-Caixa"""
        conta_internet = buscar_conta_por_codigo(db, "5.2.3")
        conta_caixa = buscar_conta_por_codigo(db, "1.1.1")
        if not conta_internet or not conta_caixa:
            raise ValueError("Contas contábeis não encontradas.")
        saldo_caixa = calcular_saldo_conta(db, conta_caixa.id)
        if saldo_caixa < valor:
            raise ValueError(f"Saldo insuficiente em Caixa. Saldo atual: R$ {saldo_caixa:.2f}")
        lancamento = models.LancamentoContabil(
            data=data,
            valor=valor,
            conta_debito_id=conta_internet.id,
            conta_credito_id=conta_caixa.id,
            historico=descricao or f"Pagamento de internet/telefone - {data.strftime('%d/%m/%Y')}",
            tipo_lancamento='operacao_padrao',
            automatico=True,
            editavel=False,
            operacao_contabil_id=operacao_contabil.id,
            referencia_mes=operacao_contabil.mes_referencia
        )
        db.add(lancamento)

    def _executar_pagar_material(db: Session, operacao_contabil: models.OperacaoContabil, valor: float, data: date_type, descricao: str):
        """Despesa de material de escritório: D-Material de Escritório / C-Caixa"""
        conta_material = buscar_conta_por_codigo(db, "5.2.4")
        conta_caixa = buscar_conta_por_codigo(db, "1.1.1")
        if not conta_material or not conta_caixa:
            raise ValueError("Contas contábeis não encontradas.")
        saldo_caixa = calcular_saldo_conta(db, conta_caixa.id)
        if saldo_caixa < valor:
            raise ValueError(f"Saldo insuficiente em Caixa. Saldo atual: R$ {saldo_caixa:.2f}")
        lancamento = models.LancamentoContabil(
            data=data,
            valor=valor,
            conta_debito_id=conta_material.id,
            conta_credito_id=conta_caixa.id,
            historico=descricao or f"Pagamento de material de escritório - {data.strftime('%d/%m/%Y')}",
            tipo_lancamento='operacao_padrao',
            automatico=True,
            editavel=False,
            operacao_contabil_id=operacao_contabil.id,
            referencia_mes=operacao_contabil.mes_referencia
        )
        db.add(lancamento)

    def _executar_depreciar_imobilizado(db: Session, operacao_contabil: models.OperacaoContabil, valor: float, data: date_type, descricao: str):
        """Depreciação de imobilizado: D-Depreciação / C-Depreciação Acumulada. Impede duplicidade no mesmo mês."""
        conta_depreciacao = buscar_conta_por_codigo(db, "5.2.5")
        conta_deprec_acum = buscar_conta_por_codigo(db, "1.2.1.2")
        if not conta_depreciacao or not conta_deprec_acum:
            raise ValueError("Contas contábeis não encontradas.")
        # Impedir duplicidade: verifica se já existe lançamento de depreciação para o mês
        mes_ref = operacao_contabil.mes_referencia
        existe = db.query(models.LancamentoContabil).filter(
            models.LancamentoContabil.conta_debito_id == conta_depreciacao.id,
            models.LancamentoContabil.conta_credito_id == conta_deprec_acum.id,
            models.LancamentoContabil.referencia_mes == mes_ref
        ).first()
        if existe:
            raise ValueError(f"Já existe lançamento de depreciação para o mês {mes_ref}.")
        lancamento = models.LancamentoContabil(
            data=data,
            valor=valor,
            conta_debito_id=conta_depreciacao.id,
            conta_credito_id=conta_deprec_acum.id,
            historico=descricao or f"Depreciação de imobilizado - {data.strftime('%d/%m/%Y')}",
            tipo_lancamento='operacao_padrao',
            automatico=True,
            editavel=False,
            operacao_contabil_id=operacao_contabil.id,
            referencia_mes=mes_ref
        )
        db.add(lancamento)
