"""
CRUD operations para Plano de Contas e Lançamentos Contábeis
"""
from sqlalchemy.orm import Session
from database import models
from typing import List, Optional
from datetime import date as date_type, datetime


# ===== PLANO DE CONTAS =====

def listar_plano_contas(db: Session, apenas_ativas: bool = True) -> List[models.PlanoDeContas]:
    """Lista todas as contas do plano de contas"""
    query = db.query(models.PlanoDeContas).order_by(models.PlanoDeContas.codigo)
    if apenas_ativas:
        query = query.filter(models.PlanoDeContas.ativo == True)
    return query.all()


def buscar_conta_por_codigo(db: Session, codigo: str) -> Optional[models.PlanoDeContas]:
    """Busca uma conta pelo código"""
    return db.query(models.PlanoDeContas).filter(models.PlanoDeContas.codigo == codigo).first()


def buscar_conta_por_id(db: Session, conta_id: int) -> Optional[models.PlanoDeContas]:
    """Busca uma conta pelo ID"""
    return db.query(models.PlanoDeContas).filter(models.PlanoDeContas.id == conta_id).first()


def calcular_saldo_conta(db: Session, conta_id: int, data_inicio: Optional[date_type] = None, data_fim: Optional[date_type] = None) -> float:
    """
    Calcula o saldo de uma conta considerando sua natureza (Devedora ou Credora)
    
    Natureza Devedora (Ativo, Despesa):
        Saldo = Σ Débitos - Σ Créditos
    
    Natureza Credora (Passivo, PL, Receita):
        Saldo = Σ Créditos - Σ Débitos
    """
    conta = buscar_conta_por_id(db, conta_id)
    if not conta:
        return 0.0
    
    # Query para débitos
    query_debitos = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.conta_debito_id == conta_id
    )
    if data_inicio:
        query_debitos = query_debitos.filter(models.LancamentoContabil.data >= data_inicio)
    if data_fim:
        query_debitos = query_debitos.filter(models.LancamentoContabil.data <= data_fim)
    
    total_debitos = sum(lanc.valor for lanc in query_debitos.all())
    
    # Query para créditos
    query_creditos = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.conta_credito_id == conta_id
    )
    if data_inicio:
        query_creditos = query_creditos.filter(models.LancamentoContabil.data >= data_inicio)
    if data_fim:
        query_creditos = query_creditos.filter(models.LancamentoContabil.data <= data_fim)
    
    total_creditos = sum(lanc.valor for lanc in query_creditos.all())
    
    # Calcular saldo conforme natureza (D = Devedora, C = Credora)
    if conta.natureza == "D":
        return total_debitos - total_creditos
    else:  # C = Credora
        return total_creditos - total_debitos


# ===== LANÇAMENTOS CONTÁBEIS =====

def criar_lancamento(
    db: Session,
    data: date_type,
    conta_debito_id: int,
    conta_credito_id: int,
    valor: float,
    historico: str,
    automatico: bool = True,
    editavel: bool = True,
    criado_por: Optional[int] = None,
    entrada_id: Optional[int] = None,
    despesa_id: Optional[int] = None
) -> models.LancamentoContabil:
    """Cria um lançamento contábil"""
    
    # Validar contas
    conta_debito = buscar_conta_por_id(db, conta_debito_id)
    conta_credito = buscar_conta_por_id(db, conta_credito_id)
    
    if not conta_debito or not conta_credito:
        raise ValueError("Conta de débito ou crédito não encontrada")
    
    if not conta_debito.aceita_lancamento:
        raise ValueError(f"Conta {conta_debito.codigo} - {conta_debito.descricao} não aceita lançamentos (conta sintética)")
    
    if not conta_credito.aceita_lancamento:
        raise ValueError(f"Conta {conta_credito.codigo} - {conta_credito.descricao} não aceita lançamentos (conta sintética)")
    
    if valor <= 0:
        raise ValueError("Valor do lançamento deve ser maior que zero")
    
    lancamento = models.LancamentoContabil(
        data=data,
        conta_debito_id=conta_debito_id,
        conta_credito_id=conta_credito_id,
        valor=valor,
        historico=historico,
        automatico=automatico,
        editavel=editavel,
        criado_por=criado_por,
        entrada_id=entrada_id,
        despesa_id=despesa_id
    )
    
    db.add(lancamento)
    db.commit()
    db.refresh(lancamento)
    return lancamento


def editar_lancamento(
    db: Session,
    lancamento_id: int,
    data: Optional[date_type] = None,
    conta_debito_id: Optional[int] = None,
    conta_credito_id: Optional[int] = None,
    valor: Optional[float] = None,
    historico: Optional[str] = None
) -> models.LancamentoContabil:
    """Edita um lançamento contábil existente"""
    
    lancamento = db.query(models.LancamentoContabil).filter(models.LancamentoContabil.id == lancamento_id).first()
    if not lancamento:
        raise ValueError("Lançamento não encontrado")
    
    if not lancamento.editavel:
        raise ValueError("Este lançamento não pode ser editado")
    
    if data:
        lancamento.data = data
    if conta_debito_id:
        conta = buscar_conta_por_id(db, conta_debito_id)
        if not conta or not conta.aceita_lancamento:
            raise ValueError("Conta de débito inválida")
        lancamento.conta_debito_id = conta_debito_id
    if conta_credito_id:
        conta = buscar_conta_por_id(db, conta_credito_id)
        if not conta or not conta.aceita_lancamento:
            raise ValueError("Conta de crédito inválida")
        lancamento.conta_credito_id = conta_credito_id
    if valor is not None:
        if valor <= 0:
            raise ValueError("Valor deve ser maior que zero")
        lancamento.valor = valor
    if historico:
        lancamento.historico = historico
    
    lancamento.editado_em = datetime.utcnow()
    lancamento.automatico = False  # Marca como editado manualmente
    
    db.commit()
    db.refresh(lancamento)
    return lancamento


def excluir_lancamento(db: Session, lancamento_id: int):
    """Exclui um lançamento contábil"""
    lancamento = db.query(models.LancamentoContabil).filter(models.LancamentoContabil.id == lancamento_id).first()
    if not lancamento:
        raise ValueError("Lançamento não encontrado")
    
    if not lancamento.editavel:
        raise ValueError("Este lançamento não pode ser excluído")
    
    db.delete(lancamento)
    db.commit()


def marcar_pagamento_lancamento(
    db: Session,
    lancamento_id: int,
    data_pagamento: date_type,
    valor_pago: Optional[float] = None,
    observacao: Optional[str] = None
) -> dict:
    """
    Marca um lançamento de provisão como pago (total ou parcial).
    
    Se valor_pago < valor do lançamento:
    - Marca o lançamento original como pago parcialmente
    - Cria novo lançamento de provisão com o saldo restante
    - Cria lançamento(s) de pagamento efetivo
    
    Args:
        lancamento_id: ID do lançamento de provisão a ser pago
        data_pagamento: Data em que o pagamento foi efetivado
        valor_pago: Valor efetivamente pago (se None, paga total)
        observacao: Observação adicional para histórico
    
    Returns:
        Dict com informações do pagamento e novos lançamentos criados
    """
    # Buscar lançamento
    lancamento = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.id == lancamento_id
    ).first()
    
    if not lancamento:
        raise ValueError(f"Lançamento {lancamento_id} não encontrado")
    
    if lancamento.tipo_lancamento == 'efetivo':
        raise ValueError("Não é possível marcar pagamento de lançamento efetivo. Apenas provisões podem ser pagas.")
    
    if lancamento.pago:
        raise ValueError("Este lançamento já foi marcado como pago")
    
    # Se valor_pago não foi informado, pagar total
    if valor_pago is None:
        valor_pago = lancamento.valor
    
    if valor_pago <= 0:
        raise ValueError("Valor pago deve ser maior que zero")
    
    # Tolerância de R$ 0,05 para diferenças de arredondamento
    TOLERANCIA_ARREDONDAMENTO = 0.05
    diferenca = valor_pago - lancamento.valor
    
    if diferenca > TOLERANCIA_ARREDONDAMENTO:
        raise ValueError(f"Valor pago (R$ {valor_pago:.2f}) excede o valor provisionado (R$ {lancamento.valor:.2f}) em R$ {diferenca:.2f}. Tolerância máxima: R$ {TOLERANCIA_ARREDONDAMENTO:.2f}")
    
    # Se o valor pago está dentro da tolerância mas é maior, considerar como pagamento total
    saldo_restante = lancamento.valor - valor_pago
    if abs(saldo_restante) <= TOLERANCIA_ARREDONDAMENTO:
        pagamento_parcial = False
        saldo_restante = 0
    else:
        pagamento_parcial = valor_pago < lancamento.valor
    
    resultado = {
        "lancamento_original_id": lancamento_id,
        "valor_provisionado": lancamento.valor,
        "valor_pago": valor_pago,
        "pagamento_parcial": pagamento_parcial,
        "saldo_restante": saldo_restante,
        "lancamentos_criados": []
    }
    
    # Determinar tipo de pagamento efetivo baseado no tipo de provisão
    if lancamento.tipo_lancamento == 'provisao':
        # Identificar pelo código da conta
        conta_credito = lancamento.conta_credito
        
        if conta_credito.codigo == "2.1.3.1":  # Pró-labore a Pagar
            tipo_pagamento = 'pagamento_pro_labore'
        elif conta_credito.codigo in ["2.1.2.1", "2.1.2.2"]:  # Impostos a Recolher
            tipo_pagamento = 'pagamento_imposto'
        elif conta_credito.codigo == "3.2.2":  # Fundo Reserva (não gera pagamento, só ajuste)
            tipo_pagamento = None
        elif conta_credito.codigo == "3.4":  # Lucros Distribuídos
            tipo_pagamento = 'pagamento_lucro'
        else:
            tipo_pagamento = 'pagamento_imposto'  # Default
    else:
        tipo_pagamento = lancamento.tipo_lancamento
    
    # Buscar conta caixa
    conta_caixa = buscar_conta_por_codigo(db, "1.1.1")
    if not conta_caixa:
        raise ValueError("Conta Caixa (1.1.1) não encontrada")
    
    # Criar lançamento(s) de pagamento efetivo
    if tipo_pagamento and tipo_pagamento == 'pagamento_pro_labore':
        # Pró-labore: criar dois lançamentos (líquido + INSS retido)
        valor_liquido = valor_pago * 0.89
        valor_inss = valor_pago * 0.11
        
        conta_inss = buscar_conta_por_codigo(db, "2.1.2.2")
        
        hist_base = f"Pagamento {lancamento.historico}"
        if observacao:
            hist_base += f" - {observacao}"
        
        # Lançamento líquido
        lanc_liquido = models.LancamentoContabil(
            data=data_pagamento,
            conta_debito_id=lancamento.conta_credito_id,
            conta_credito_id=conta_caixa.id,
            valor=valor_liquido,
            historico=f"{hist_base} (líquido)",
            automatico=True,
            editavel=False,
            tipo_lancamento=tipo_pagamento,
            referencia_mes=lancamento.referencia_mes,
            lancamento_origem_id=lancamento_id,
            pago=True,
            data_pagamento=data_pagamento,
            valor_pago=valor_liquido
        )
        db.add(lanc_liquido)
        resultado["lancamentos_criados"].append({"tipo": "pagamento_liquido", "valor": valor_liquido})
        
        # Lançamento INSS retido
        if conta_inss:
            lanc_inss = models.LancamentoContabil(
                data=data_pagamento,
                conta_debito_id=lancamento.conta_credito_id,
                conta_credito_id=conta_inss.id,
                valor=valor_inss,
                historico=f"{hist_base} (INSS 11% retido)",
                automatico=True,
                editavel=False,
                tipo_lancamento=tipo_pagamento,
                referencia_mes=lancamento.referencia_mes,
                lancamento_origem_id=lancamento_id,
                pago=True,
                data_pagamento=data_pagamento,
                valor_pago=valor_inss
            )
            db.add(lanc_inss)
            resultado["lancamentos_criados"].append({"tipo": "retencao_inss", "valor": valor_inss})
    
    elif tipo_pagamento:
        # Outros pagamentos: simples
        hist_base = f"Pagamento {lancamento.historico}"
        if observacao:
            hist_base += f" - {observacao}"
        
        lanc_pagamento = models.LancamentoContabil(
            data=data_pagamento,
            conta_debito_id=lancamento.conta_credito_id,
            conta_credito_id=conta_caixa.id,
            valor=valor_pago,
            historico=hist_base,
            automatico=True,
            editavel=False,
            tipo_lancamento=tipo_pagamento,
            referencia_mes=lancamento.referencia_mes,
            lancamento_origem_id=lancamento_id,
            pago=True,
            data_pagamento=data_pagamento,
            valor_pago=valor_pago
        )
        db.add(lanc_pagamento)
        resultado["lancamentos_criados"].append({"tipo": "pagamento", "valor": valor_pago})
    
    # Atualizar lançamento original
    lancamento.pago = True
    lancamento.data_pagamento = data_pagamento
    lancamento.valor_pago = valor_pago
    
    # Se pagamento parcial (saldo restante > tolerância), criar novo lançamento de provisão com saldo
    if pagamento_parcial and saldo_restante > TOLERANCIA_ARREDONDAMENTO:
        lanc_saldo = models.LancamentoContabil(
            data=lancamento.data,
            conta_debito_id=lancamento.conta_debito_id,
            conta_credito_id=lancamento.conta_credito_id,
            valor=saldo_restante,
            historico=f"{lancamento.historico} (saldo após pagamento parcial)",
            automatico=True,
            editavel=False,
            tipo_lancamento=lancamento.tipo_lancamento,
            referencia_mes=lancamento.referencia_mes,
            entrada_id=lancamento.entrada_id,
            despesa_id=lancamento.despesa_id,
            lancamento_origem_id=lancamento_id,
            pago=False
        )
        db.add(lanc_saldo)
        resultado["lancamentos_criados"].append({"tipo": "saldo_restante", "valor": saldo_restante})
    
    db.commit()
    
    return resultado


def listar_lancamentos(
    db: Session,
    data_inicio: Optional[date_type] = None,
    data_fim: Optional[date_type] = None,
    conta_id: Optional[int] = None,
    tipo_lancamento: Optional[str] = None,
    apenas_pendentes: bool = False,
    limit: int = 100,
    offset: int = 0
) -> List[models.LancamentoContabil]:
    """Lista lançamentos contábeis com filtros"""
    
    query = db.query(models.LancamentoContabil).order_by(models.LancamentoContabil.data.desc(), models.LancamentoContabil.id.desc())
    
    if data_inicio:
        query = query.filter(models.LancamentoContabil.data >= data_inicio)
    if data_fim:
        query = query.filter(models.LancamentoContabil.data <= data_fim)
    if conta_id:
        query = query.filter(
            (models.LancamentoContabil.conta_debito_id == conta_id) |
            (models.LancamentoContabil.conta_credito_id == conta_id)
        )
    if tipo_lancamento:
        query = query.filter(models.LancamentoContabil.tipo_lancamento == tipo_lancamento)
    if apenas_pendentes:
        query = query.filter(
            models.LancamentoContabil.tipo_lancamento == 'provisao',
            models.LancamentoContabil.pago == False
        )
    
    return query.limit(limit).offset(offset).all()


# ===== LANÇAMENTOS AUTOMÁTICOS =====

def lancar_entrada_honorarios(db: Session, entrada_id: int) -> List[models.LancamentoContabil]:
    """
    Cria lançamentos automáticos para entrada de honorários com sistema de provisões.
    
    Lançamentos criados:
    L1: D: Caixa (1.1.1) / C: Receita (4.1.1) - Receita efetiva
    L2: D: Simples (5.3.1) / C: Simples a Recolher (2.1.2.1) - Provisão imposto
    L3: D: Pró-labore (5.1.1) / C: Pró-labore a Pagar (2.1.3.1) - Provisão
    L4: D: INSS Patronal (5.1.3) / C: INSS a Recolher (2.1.2.2) - Provisão
    L5: D: Lucros Acumulados (3.3) / C: Fundo Reserva (3.2.2) - Provisão 10%
    L6-N: D: Lucros Acumulados (3.3) / C: Lucros Distribuídos (3.4) - Por sócio
    """
    from .crud_provisoes import calcular_e_provisionar_entrada
    
    entrada = db.query(models.Entrada).filter(models.Entrada.id == entrada_id).first()
    if not entrada:
        raise ValueError("Entrada não encontrada")
    
    # Verificar se já existem lançamentos para esta entrada
    lancamentos_existentes = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.entrada_id == entrada_id
    ).all()
    
    if lancamentos_existentes:
        return lancamentos_existentes
    
    # Calcular provisões
    provisao = calcular_e_provisionar_entrada(db, entrada_id)
    mes_referencia = entrada.data.strftime("%Y-%m")
    
    # Buscar contas necessárias
    contas = {
        'caixa': buscar_conta_por_codigo(db, "1.1.1"),
        'receita': buscar_conta_por_codigo(db, "4.1.1"),
        'simples_despesa': buscar_conta_por_codigo(db, "5.3.1"),
        'simples_passivo': buscar_conta_por_codigo(db, "2.1.2.1"),
        'pro_labore_despesa': buscar_conta_por_codigo(db, "5.1.1"),
        'pro_labore_passivo': buscar_conta_por_codigo(db, "2.1.3.1"),
        'inss_despesa': buscar_conta_por_codigo(db, "5.1.3"),
        'inss_passivo': buscar_conta_por_codigo(db, "2.1.2.2"),
        'lucros_acumulados': buscar_conta_por_codigo(db, "3.3"),
        'fundo_reserva': buscar_conta_por_codigo(db, "3.2.2"),
        'lucros_distribuidos': buscar_conta_por_codigo(db, "3.4"),
    }
    
    # Verificar se todas as contas existem
    for nome, conta in contas.items():
        if not conta:
            raise ValueError(f"Conta {nome} não encontrada no plano de contas")
    
    lancamentos = []
    
    # L1: Receita efetiva (entrada de caixa)
    lanc1 = models.LancamentoContabil(
        data=entrada.data,
        conta_debito_id=contas['caixa'].id,
        conta_credito_id=contas['receita'].id,
        valor=entrada.valor,
        historico=f"Recebimento de honorários - {entrada.cliente}",
        automatico=True,
        editavel=False,
        entrada_id=entrada_id,
        tipo_lancamento='efetivo',
        referencia_mes=mes_referencia
    )
    db.add(lanc1)
    lancamentos.append(lanc1)
    
    # L2: Provisão Simples Nacional
    if provisao['imposto_provisionado'] > 0:
        lanc2 = models.LancamentoContabil(
            data=entrada.data,
            conta_debito_id=contas['simples_despesa'].id,
            conta_credito_id=contas['simples_passivo'].id,
            valor=provisao['imposto_provisionado'],
            historico=f"Provisão Simples Nacional - {entrada.cliente}",
            automatico=True,
            editavel=False,
            entrada_id=entrada_id,
            tipo_lancamento='provisao',
            referencia_mes=mes_referencia
        )
        db.add(lanc2)
        lancamentos.append(lanc2)
    
    # L3: Provisão Pró-labore
    if provisao['pro_labore_previsto'] > 0:
        lanc3 = models.LancamentoContabil(
            data=entrada.data,
            conta_debito_id=contas['pro_labore_despesa'].id,
            conta_credito_id=contas['pro_labore_passivo'].id,
            valor=provisao['pro_labore_previsto'],
            historico=f"Provisão pró-labore - {entrada.cliente}",
            automatico=True,
            editavel=False,
            entrada_id=entrada_id,
            tipo_lancamento='provisao',
            referencia_mes=mes_referencia
        )
        db.add(lanc3)
        lancamentos.append(lanc3)
    
    # L4: Provisão INSS Patronal
    if provisao['inss_patronal_previsto'] > 0:
        lanc4 = models.LancamentoContabil(
            data=entrada.data,
            conta_debito_id=contas['inss_despesa'].id,
            conta_credito_id=contas['inss_passivo'].id,
            valor=provisao['inss_patronal_previsto'],
            historico=f"Provisão INSS patronal 20% - {entrada.cliente}",
            automatico=True,
            editavel=False,
            entrada_id=entrada_id,
            tipo_lancamento='provisao',
            referencia_mes=mes_referencia
        )
        db.add(lanc4)
        lancamentos.append(lanc4)
    
    # L5: Provisão Fundo de Reserva 10%
    if provisao['fundo_reserva_previsto'] > 0:
        lanc5 = models.LancamentoContabil(
            data=entrada.data,
            conta_debito_id=contas['lucros_acumulados'].id,
            conta_credito_id=contas['fundo_reserva'].id,
            valor=provisao['fundo_reserva_previsto'],
            historico=f"Provisão fundo de reserva 10% - {entrada.cliente}",
            automatico=True,
            editavel=False,
            entrada_id=entrada_id,
            tipo_lancamento='provisao',
            referencia_mes=mes_referencia
        )
        db.add(lanc5)
        lancamentos.append(lanc5)
    
    # L6-N: Provisão Lucros Distribuídos por sócio
    for socio_dist in provisao['distribuicao_socios']:
        if socio_dist['lucro_disponivel'] > 0:
            lanc_lucro = models.LancamentoContabil(
                data=entrada.data,
                conta_debito_id=contas['lucros_acumulados'].id,
                conta_credito_id=contas['lucros_distribuidos'].id,
                valor=socio_dist['lucro_disponivel'],
                historico=f"Provisão lucro disponível - {socio_dist['nome']} ({socio_dist['percentual_entrada']}%)",
                automatico=True,
                editavel=False,
                entrada_id=entrada_id,
                tipo_lancamento='provisao',
                referencia_mes=mes_referencia
            )
            db.add(lanc_lucro)
            lancamentos.append(lanc_lucro)
    
    db.commit()
    
    for lanc in lancamentos:
        db.refresh(lanc)
    
    return lancamentos


def _determinar_conta_despesa(descricao: str, tipo: str = None, categoria: str = None) -> str:
    """
    Determina a conta contábil baseada na descrição/tipo/categoria da despesa
    usando palavras-chave
    """
    # Mapear palavras-chave para contas
    mapeamento = {
        "aluguel": "5.2.1",
        "agua": "5.2.2",
        "água": "5.2.2",
        "luz": "5.2.2", 
        "energia": "5.2.2",
        "eletrica": "5.2.2",
        "elétrica": "5.2.2",
        "internet": "5.2.3",
        "telefone": "5.2.3",
        "celular": "5.2.3",
        "material": "5.2.4",
        "escritorio": "5.2.4",
        "escritório": "5.2.4",
        "papelaria": "5.2.4",
        "salario": "5.1.2",
        "salário": "5.1.2",
        "estagiario": "5.1.2",
        "estagiário": "5.1.2",
        "pro-labore": "5.1.1",
        "prolabore": "5.1.1",
        "pró-labore": "5.1.1",
        "inss": "5.1.3",
        "simples": "5.3.1",
        "imposto": "5.3.1",
        "taxa": "5.3.2",
    }
    
    # Juntar todos os textos disponíveis
    texto = (f"{descricao or ''} {tipo or ''} {categoria or ''}").lower()
    
    # Procurar palavra-chave
    for palavra_chave, codigo in mapeamento.items():
        if palavra_chave in texto:
            return codigo
    
    # Padrão: Material de Escritório
    return "5.2.4"


def lancar_despesa(db: Session, despesa_id: int) -> models.LancamentoContabil:
    """
    Cria lançamento automático para despesa
    D: Despesa (conta apropriada)
    C: Caixa e Bancos (1.1.1)
    """
    despesa = db.query(models.Despesa).filter(models.Despesa.id == despesa_id).first()
    if not despesa:
        raise ValueError("Despesa não encontrada")
    
    # Verificar se já existe lançamento para esta despesa
    lancamento_existente = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.despesa_id == despesa_id
    ).first()
    
    if lancamento_existente:
        return lancamento_existente
    
    # Determinar conta de despesa usando função inteligente
    codigo_conta = _determinar_conta_despesa(
        descricao=despesa.descricao,
        tipo=despesa.tipo,
        categoria=despesa.categoria
    )
    
    conta_despesa = buscar_conta_por_codigo(db, codigo_conta)
    conta_caixa = buscar_conta_por_codigo(db, "1.1.1")
    
    if not conta_despesa or not conta_caixa:
        raise ValueError("Contas do plano de contas não encontradas")
    
    historico = f"Pagamento - {despesa.tipo or 'Despesa'}"
    if despesa.descricao:
        historico += f" - {despesa.descricao}"
    
    return criar_lancamento(
        db=db,
        data=despesa.data,
        conta_debito_id=conta_despesa.id,
        conta_credito_id=conta_caixa.id,
        valor=despesa.valor,
        historico=historico,
        automatico=True,
        editavel=True,
        despesa_id=despesa_id
    )


# ===== BALANÇO PATRIMONIAL =====

def gerar_balanco_patrimonial(db: Session, mes: int, ano: int):
    """
    Gera o Balanço Patrimonial com hierarquia de contas.
    Retorna estrutura com Ativo, Passivo e Patrimônio Líquido.
    """
    from datetime import date as date_type
    
    # Data limite para cálculo dos saldos (último dia do mês)
    import calendar
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_fim = date_type(ano, mes, ultimo_dia)
    
    def construir_hierarquia(conta_pai_codigo: str):
        """Constrói hierarquia recursiva de contas"""
        contas = db.query(models.PlanoDeContas).filter(
            models.PlanoDeContas.codigo.like(f"{conta_pai_codigo}%"),
            models.PlanoDeContas.ativo == True
        ).order_by(models.PlanoDeContas.codigo).all()
        
        # Organizar em estrutura hierárquica
        estrutura = []
        contas_dict = {c.codigo: {
            "id": c.id,
            "codigo": c.codigo,
            "nome": c.descricao,
            "natureza": c.natureza,
            "nivel": c.nivel,
            "aceita_lancamento": c.aceita_lancamento,
            "saldo": calcular_saldo_conta(db, c.id, data_fim=data_fim),
            "subgrupos": []
        } for c in contas}
        
        # Conectar pais e filhos
        for codigo, conta_data in contas_dict.items():
            if len(codigo) == 1:  # Conta raiz (1, 2, 3, 4, 5)
                estrutura.append(conta_data)
            else:
                # Encontrar pai (remover último segmento)
                partes = codigo.split('.')
                if len(partes) > 1:
                    codigo_pai = '.'.join(partes[:-1])
                else:
                    codigo_pai = codigo[:-1] if len(codigo) > 1 else None
                
                if codigo_pai and codigo_pai in contas_dict:
                    contas_dict[codigo_pai]["subgrupos"].append(conta_data)
        
        return estrutura
    
    def atualizar_saldos_sinteticos(grupos):
        """Atualiza saldos das contas sintéticas somando seus filhos"""
        for grupo in grupos:
            if grupo["subgrupos"]:
                # Primeiro atualiza os filhos recursivamente
                atualizar_saldos_sinteticos(grupo["subgrupos"])
                # Se não aceita lançamento, é sintética - calcula saldo pela soma dos filhos
                if not grupo["aceita_lancamento"]:
                    grupo["saldo"] = sum(sub["saldo"] for sub in grupo["subgrupos"])
    
    # Gerar estruturas
    ativo = construir_hierarquia("1")
    passivo = construir_hierarquia("2")
    patrimonio_liquido = construir_hierarquia("3")
    
    # Calcular resultado do período (Receitas - Despesas) e adicionar aos Lucros Acumulados
    receitas = construir_hierarquia("4")
    despesas = construir_hierarquia("5")
    
    def calcular_saldo_grupo(grupos):
        """Calcula saldo total de um grupo"""
        total = 0.0
        for grupo in grupos:
            if grupo["aceita_lancamento"]:
                total += grupo["saldo"]
            if grupo["subgrupos"]:
                total += calcular_saldo_grupo(grupo["subgrupos"])
        return total
    
    resultado_periodo = calcular_saldo_grupo(receitas) - calcular_saldo_grupo(despesas)
    
    # Adicionar resultado aos Lucros Acumulados (conta 3.3)
    def adicionar_resultado_lucros(grupos, resultado):
        """Adiciona o resultado do período na conta de Lucros Acumulados"""
        for grupo in grupos:
            if grupo["codigo"] == "3.3":
                grupo["saldo"] += resultado
                return True
            if grupo["subgrupos"]:
                if adicionar_resultado_lucros(grupo["subgrupos"], resultado):
                    return True
        return False
    
    adicionar_resultado_lucros(patrimonio_liquido, resultado_periodo)
    
    # Atualizar saldos das contas sintéticas
    atualizar_saldos_sinteticos(ativo)
    atualizar_saldos_sinteticos(passivo)
    atualizar_saldos_sinteticos(patrimonio_liquido)
    
    # Calcular totais recursivamente
    def calcular_total_recursivo(grupos):
        """Calcula total somando apenas contas analíticas (que aceitam lançamento)"""
        total = 0.0
        for grupo in grupos:
            # Se aceita lançamento, é conta analítica - soma o saldo
            if grupo["aceita_lancamento"]:
                # Contas de natureza devedora reduzem o total (ex: Lucros Distribuídos)
                if grupo["natureza"] == "D":
                    total -= grupo["saldo"]
                else:
                    total += grupo["saldo"]
            # Se tem subgrupos, processa recursivamente (sejam analíticas ou sintéticas)
            if grupo["subgrupos"]:
                total += calcular_total_recursivo(grupo["subgrupos"])
        return total
    
    total_ativo = calcular_total_recursivo(ativo)
    total_passivo = calcular_total_recursivo(passivo)
    total_pl = calcular_total_recursivo(patrimonio_liquido)
    
    return {
        "ativo": ativo,
        "passivo": passivo,
        "patrimonioLiquido": patrimonio_liquido,
        "totais": {
            "ativo": total_ativo,
            "passivo": total_passivo,
            "patrimonioLiquido": total_pl,
            "passivoMaisPl": total_passivo + total_pl
        }
    }
