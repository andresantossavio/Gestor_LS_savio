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


def _get_or_create_conta(
    db: Session,
    codigo: str,
    descricao: str,
    tipo: str,
    natureza: str,
    nivel: int,
    pai_codigo: Optional[str] = None,
    aceita_lancamento: bool = True,
) -> models.PlanoDeContas:
    """Obtém uma conta por código ou cria caso não exista.

    Observação: mantém o padrão já usado no init, com natureza
    como rótulo completo ("Devedora"/"Credora").
    """
    conta = buscar_conta_por_codigo(db, codigo)
    if conta:
        return conta

    conta = models.PlanoDeContas(
        codigo=codigo,
        descricao=descricao,
        tipo=tipo,
        natureza=natureza,
        nivel=nivel,
        aceita_lancamento=aceita_lancamento,
        ativo=True,
    )
    # Definir pai, se informado e existir
    if pai_codigo:
        pai = buscar_conta_por_codigo(db, pai_codigo)
        if pai:
            conta.pai_id = pai.id
    db.add(conta)
    db.commit()
    db.refresh(conta)
    return conta


def _ultimo_dia_mes(ano: int, mes: int) -> date_type:
    import calendar
    dia = calendar.monthrange(ano, mes)[1]
    return date_type(ano, mes, dia)


def _criar_subconta_reserva_socio(
    db: Session,
    socio_id: int
) -> models.PlanoDeContas:
    """
    Cria dinamicamente uma subconta de reserva para um sócio específico.
    Formato: 3.2.1.{socio_id} - Reserva - {Nome do Sócio}
    
    A subconta é criada automaticamente na primeira execução de RESERVAR_FUNDO.
    """
    socio = db.query(models.Socio).filter(models.Socio.id == socio_id).first()
    if not socio:
        raise ValueError(f"Sócio ID {socio_id} não encontrado")
    
    codigo_subconta = f"3.2.1.{socio_id}"
    descricao_subconta = f"Reserva - {socio.nome}"
    
    # Verificar se já existe
    conta_existente = buscar_conta_por_codigo(db, codigo_subconta)
    if conta_existente:
        return conta_existente
    
    # Garantir que a conta pai (3.2.1) existe e é sintética
    conta_pai = buscar_conta_por_codigo(db, "3.2.1")
    if not conta_pai:
        raise ValueError("Conta 3.2.1 (Reserva de Lucros) não encontrada")
    
    if conta_pai.aceita_lancamento:
        # Transformar em sintética se ainda não for
        conta_pai.aceita_lancamento = False
        db.commit()
    
    # Criar subconta analítica
    subconta = models.PlanoDeContas(
        codigo=codigo_subconta,
        descricao=descricao_subconta,
        tipo="PL",
        natureza="Credora",
        nivel=4,
        aceita_lancamento=True,
        ativo=True,
        pai_id=conta_pai.id
    )
    db.add(subconta)
    db.commit()
    db.refresh(subconta)
    
    return subconta


def _criar_subconta_cdb_reserva_socio(
    db: Session,
    socio_id: int
) -> models.PlanoDeContas:
    """
    Cria dinamicamente uma subconta de CDB Reserva Legal para um sócio específico.
    Formato: 1.1.1.2.3.{socio_id} - CDB Reserva Legal - {Nome do Sócio}
    
    Permite rastreamento de quanto cada sócio tem aplicado em CDB.
    """
    socio = db.query(models.Socio).filter(models.Socio.id == socio_id).first()
    if not socio:
        raise ValueError(f"Sócio ID {socio_id} não encontrado")
    
    codigo_subconta = f"1.1.1.2.3.{socio_id}"
    descricao_subconta = f"CDB Reserva Legal - {socio.nome}"
    
    # Verificar se já existe
    conta_existente = buscar_conta_por_codigo(db, codigo_subconta)
    if conta_existente:
        return conta_existente
    
    # Garantir que a conta pai (1.1.1.2.3) existe e é sintética
    conta_pai = buscar_conta_por_codigo(db, "1.1.1.2.3")
    if not conta_pai:
        raise ValueError("Conta 1.1.1.2.3 (CDB - Reserva Legal) não encontrada")
    
    if conta_pai.aceita_lancamento:
        # Transformar em sintética se ainda não for
        conta_pai.aceita_lancamento = False
        db.commit()
    
    # Criar subconta analítica
    subconta = models.PlanoDeContas(
        codigo=codigo_subconta,
        descricao=descricao_subconta,
        tipo="Ativo",
        natureza="Devedora",
        nivel=6,
        aceita_lancamento=True,
        ativo=True,
        pai_id=conta_pai.id
    )
    db.add(subconta)
    db.commit()
    db.refresh(subconta)
    
    return subconta


def _obter_subconta_reserva_socio(
    db: Session,
    socio_id: int
) -> Optional[models.PlanoDeContas]:
    """
    Obtém a subconta de reserva de um sócio específico.
    Retorna None se não existir.
    
    Formato: 3.2.1.{socio_id} - Reserva - {Nome do Sócio}
    """
    codigo_subconta = f"3.2.1.{socio_id}"
    return buscar_conta_por_codigo(db, codigo_subconta)


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
    
    # Calcular saldo conforme natureza (Devedora ou Credora)
    # Normalizar para aceitar "D"/"Devedora" e "C"/"Credora"
    natureza_normalizada = conta.natureza.upper() if conta.natureza else ""
    if natureza_normalizada in ("D", "DEVEDORA"):
        return total_debitos - total_creditos
    else:  # Credora
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
    """Edita um lançamento contábil existente - permite edição de QUALQUER lançamento"""
    
    lancamento = db.query(models.LancamentoContabil).filter(models.LancamentoContabil.id == lancamento_id).first()
    if not lancamento:
        raise ValueError("Lançamento não encontrado")
    
    # Removida restrição: permite editar mesmo lançamentos automáticos
    
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
    # Mantém histórico de que foi editado, mas não força editavel=True
    
    db.commit()
    db.refresh(lancamento)
    return lancamento


def excluir_lancamento(db: Session, lancamento_id: int):
    """Exclui um lançamento contábil - permite exclusão de QUALQUER lançamento"""
    lancamento = db.query(models.LancamentoContabil).filter(models.LancamentoContabil.id == lancamento_id).first()
    if not lancamento:
        raise ValueError("Lançamento não encontrado")
    
    # Removida restrição: permite excluir mesmo lançamentos automáticos
    
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
            # Guard: pró-labore desativado para evitar duplicidades com fluxo de lucros (3.4)
            raise ValueError(
                "Pagamento de pró-labore desativado. Registre o saque como 'pagamento_lucro' (D 3.4 / C 1.1.1)."
            )
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

def registrar_fechamento_resultado(
    db: Session,
    mes: str,
    valor_resultado: float,
    recriar: bool = False,
) -> Optional[models.LancamentoContabil]:
    """Registra lançamento de fechamento do resultado para o mês (YYYY-MM).

    Regras:
    - Se valor > 0: D 4.9.9 (técnica) / C 3.3 (Lucros Acumulados)
    - Se valor < 0: D 3.3 / C 4.9.9
    - Se valor ~ 0: não lança
    - Idempotente por mês: ao recriar, remove existentes do tipo 'fechamento_resultado'.
    """
    if not mes or len(mes) != 7 or mes[4] != '-':
        raise ValueError("Parâmetro 'mes' deve estar no formato YYYY-MM")

    # Tolerância para valores muito pequenos
    if abs(valor_resultado) < 0.005:
        return None

    ano_int = int(mes.split('-')[0])
    mes_int = int(mes.split('-')[1])
    data_lcto = _ultimo_dia_mes(ano_int, mes_int)

    # Garantir contas necessárias
    conta_lucros = buscar_conta_por_codigo(db, "3.3")
    if not conta_lucros:
        raise ValueError("Conta 3.3 (Lucros Acumulados) não encontrada")

    # Conta técnica de resultado no grupo de Receitas
    conta_tecnica = _get_or_create_conta(
        db,
        codigo="4.9.9",
        descricao="Fechamento do Resultado (técnica)",
        tipo="Receita",
        natureza="Credora",
        nivel=3,
        pai_codigo="4",
        aceita_lancamento=True,
    )

    historico = f"Fechamento do resultado do mês {mes}"

    # Determinar contas de débito e crédito conforme sinal do resultado
    if valor_resultado > 0:
        conta_debito_id = conta_tecnica.id
        conta_credito_id = conta_lucros.id
        valor = valor_resultado
    else:
        conta_debito_id = conta_lucros.id
        conta_credito_id = conta_tecnica.id
        valor = abs(valor_resultado)

    # NOVO: Buscar lançamento existente ao invés de deletar (padrão UPDATE)
    existente = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.referencia_mes == mes,
        models.LancamentoContabil.tipo_lancamento == 'fechamento_resultado'
    ).first()

    if existente:
        # UPDATE: atualizar valores (incluindo contas se lucro mudou de sinal)
        from datetime import datetime
        existente.valor = valor
        existente.historico = historico
        existente.conta_debito_id = conta_debito_id
        existente.conta_credito_id = conta_credito_id
        existente.data = data_lcto
        existente.editado_em = datetime.utcnow()
        db.commit()
        db.refresh(existente)
        return existente
    else:
        # INSERT: criar novo lançamento
        lanc = models.LancamentoContabil(
            data=data_lcto,
            conta_debito_id=conta_debito_id,
            conta_credito_id=conta_credito_id,
            valor=valor,
            historico=historico,
            automatico=True,
            editavel=False,
            tipo_lancamento='fechamento_resultado',
            referencia_mes=mes,
        )
        db.add(lanc)
        db.commit()
        db.refresh(lanc)
        return lanc

def lancar_entrada_honorarios(db: Session, entrada_id: int) -> List[models.LancamentoContabil]:
    """
    Cria apenas o lançamento de receita efetiva para uma entrada de honorários.
    
    As provisões (Simples, Pró-labore, INSS, Fundo Reserva, Lucros) são criadas
    apenas na consolidação mensal da DRE, não individualmente por entrada.
    
    Lançamento criado:
    L1: D: Caixa (1.1.1) / C: Receita (4.1.1) - Valor da entrada (efetivo)
    """
    entrada = db.query(models.Entrada).filter(models.Entrada.id == entrada_id).first()
    if not entrada:
        raise ValueError("Entrada não encontrada")
    
    # Verificar se já existem lançamentos para esta entrada
    lancamentos_existentes = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.entrada_id == entrada_id
    ).all()
    
    if lancamentos_existentes:
        return lancamentos_existentes
    
    mes_referencia = entrada.data.strftime("%Y-%m")
    
    # Buscar contas necessárias
    conta_caixa = buscar_conta_por_codigo(db, "1.1.1")
    conta_receita = buscar_conta_por_codigo(db, "4.1.1")
    
    if not conta_caixa or not conta_receita:
        raise ValueError("Contas de Caixa ou Receita não encontradas no plano de contas")
    
    lancamentos = []
    
    # L1: Receita efetiva (entrada de caixa)
    lanc1 = models.LancamentoContabil(
        data=entrada.data,
        conta_debito_id=conta_caixa.id,
        conta_credito_id=conta_receita.id,
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
    
    Se o mês NÃO está consolidado, mostra valores de impostos em tempo real
    (provisionados mas não pagos) nas contas 2.1.4 (Simples) e 2.1.5 (INSS).
    """
    from datetime import date as date_type
    from database import crud_contabilidade
    
    # Data limite para cálculo dos saldos (último dia do mês)
    import calendar
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_fim = date_type(ano, mes, ultimo_dia)
    mes_str = f"{ano}-{mes:02d}"
    
    # Cálculo sempre baseado nos lançamentos contábeis registrados
    mes_consolidado = True
    ajustes_tempo_real = {}
    alertas = []
    
    def construir_hierarquia(conta_pai_codigo: str, inverter_sinal: bool = False):
        """Constrói hierarquia recursiva de contas
        
        Args:
            conta_pai_codigo: Código da conta raiz
            inverter_sinal: Se True, inverte o sinal dos saldos (usado para Passivo e PL)
        """
        contas = db.query(models.PlanoDeContas).filter(
            models.PlanoDeContas.codigo.like(f"{conta_pai_codigo}%"),
            models.PlanoDeContas.ativo == True
        ).order_by(models.PlanoDeContas.codigo).all()
        
        # Organizar em estrutura hierárquica
        estrutura = []
        contas_dict = {}
        for c in contas:
            saldo_base = calcular_saldo_conta(db, c.id, data_fim=data_fim)
            
            # Para contas do PL (grupo 3) com natureza DEVEDORA (contas redutoras como 3.4.1),
            # inverter o sinal para que subtraiam do PL ao invés de somar
            if conta_pai_codigo == "3" and c.natureza and c.natureza.upper() in ("D", "DEVEDORA"):
                saldo_final = -saldo_base
            else:
                saldo_final = -saldo_base if inverter_sinal else saldo_base
            
            contas_dict[c.codigo] = {
                "id": c.id,
                "codigo": c.codigo,
                "nome": c.descricao,
                "natureza": c.natureza,
                "nivel": c.nivel,
                "aceita_lancamento": c.aceita_lancamento,
                "saldo": saldo_final,
                "subgrupos": []
            }
        
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
    
    # Gerar estruturas usando sinal natural do razão
    # Ativo: natureza devedora (positivo)
    # Passivo/PL: natureza credora (negativo no razão, mas apresentado como positivo)
    ativo = construir_hierarquia("1", inverter_sinal=False)
    passivo = construir_hierarquia("2", inverter_sinal=False)
    patrimonio_liquido = construir_hierarquia("3", inverter_sinal=False)
    
    # Calcular resultado do período (Receitas - Despesas)
    receitas = construir_hierarquia("4", inverter_sinal=False)
    despesas = construir_hierarquia("5", inverter_sinal=False)
    
    def calcular_saldo_grupo(grupos):
        """Calcula saldo total de um grupo"""
        total = 0.0
        for grupo in grupos:
            if grupo["aceita_lancamento"]:
                total += grupo["saldo"]
            if grupo["subgrupos"]:
                total += calcular_saldo_grupo(grupo["subgrupos"])
        return total
    
    # Resultado do período já está registrado no razão via fechamento_resultado
    # A conta 3.3 (Lucros Acumulados) já contém o saldo correto via lançamentos contábeis
    # Não é necessário calcular ou adicionar manualmente
    
    # Atualizar saldos das contas sintéticas
    atualizar_saldos_sinteticos(ativo)
    atualizar_saldos_sinteticos(passivo)
    atualizar_saldos_sinteticos(patrimonio_liquido)
    
    # Calcular totais recursivamente
    def calcular_total_recursivo(grupos):
        """Calcula total somando saldos já calculados (sintéticas já agregadas)"""
        total = 0.0
        for grupo in grupos:
            # Apenas somar os saldos do primeiro nível (grupos raiz), pois sintéticas já agregaram seus filhos
            total += grupo["saldo"]
        return total
    
    total_ativo = calcular_total_recursivo(ativo)
    total_passivo = calcular_total_recursivo(passivo)
    total_pl = calcular_total_recursivo(patrimonio_liquido)
    
    # O cálculo de saldo já considera a natureza da conta:
    # - Ativo (Devedora): Débitos - Créditos = positivo quando há saldo devedor
    # - Passivo/PL (Credora): Créditos - Débitos = positivo quando há saldo credor
    # Ambos aparecem como positivos no balanço patrimonial
    # A equação contábil é: Ativo = Passivo + PL
    
    resultado = {
        "ativo": ativo,
        "passivo": passivo,
        "patrimonioLiquido": patrimonio_liquido,
        "totais": {
            "ativo": total_ativo,
            "passivo": total_passivo,
            "patrimonioLiquido": total_pl,
            "passivoMaisPl": total_passivo + total_pl
        },
        "metadata": {
            "mes": mes_str,
            "consolidado": mes_consolidado,
            "ajustesTempoReal": False,
            "ajustesAplicados": [],
            "alertas": []
        }
    }
    
    return resultado


# ===== LANÇAMENTOS AUTOMÁTICOS PARA PAGAMENTOS PENDENTES =====

def lancar_pendencia_gerada(db: Session, pendencia_id: int) -> Optional[models.LancamentoContabil]:
    """
    Cria lançamento contábil quando uma pendência é gerada (provisão).
    
    Lançamentos por tipo:
    - SIMPLES: D: 5.3.1 (Despesa Simples) / C: 2.1.4 (Simples a Pagar)
    - INSS: D: 5.1.3 (Despesa INSS) / C: 2.1.5 (INSS a Pagar)
    - FUNDO_RESERVA: D: 3.4.1 (Lucros Distribuídos) / C: 3.2.1 (Reserva de Lucros)
    - LUCRO_SOCIO: D: 3.4.1 (Lucros Distribuídos) / C: 2.1.6 (Lucros a Pagar)
    """
    from database.models import PagamentoPendente
    
    pendencia = db.query(PagamentoPendente).filter(PagamentoPendente.id == pendencia_id).first()
    if not pendencia:
        return None
    
    # Mapear tipo de pendência para contas contábeis
    mapeamento_contas = {
        "SIMPLES": {
            "debito": "5.3.1",  # Despesa com Simples
            "credito": "2.1.4",  # Simples a Pagar
            "historico": f"Provisão Simples Nacional - {pendencia.descricao}"
        },
        "INSS": {
            "debito": "5.1.3",  # Despesa com INSS
            "credito": "2.1.5",  # INSS a Pagar
            "historico": f"Provisão INSS - {pendencia.descricao}"
        },
        "FUNDO_RESERVA": {
            "debito": "3.4.1",  # Lucros Distribuídos (PL)
            "credito": "3.2.1",  # Reserva de Lucros (PL)
            "historico": f"Constituição Fundo de Reserva - {pendencia.descricao}"
        },
        "LUCRO_SOCIO": {
            "debito": "3.4.1",  # Lucros Distribuídos (PL)
            "credito": "2.1.6",  # Lucros a Pagar (Passivo)
            "historico": f"Provisão lucro a distribuir - {pendencia.descricao}"
        }
    }
    
    config = mapeamento_contas.get(pendencia.tipo)
    if not config:
        return None  # Tipo não mapeado
    
    # Buscar contas
    conta_debito = buscar_conta_por_codigo(db, config["debito"])
    conta_credito = buscar_conta_por_codigo(db, config["credito"])
    
    if not conta_debito or not conta_credito:
        print(f"⚠️  Contas não encontradas para tipo {pendencia.tipo}: D:{config['debito']} C:{config['credito']}")
        return None
    
    mes_ref = f"{pendencia.ano_ref}-{pendencia.mes_ref:02d}"
    
    # Criar lançamento de provisão
    lancamento = models.LancamentoContabil(
        data=datetime.now().date(),
        conta_debito_id=conta_debito.id,
        conta_credito_id=conta_credito.id,
        valor=pendencia.valor,
        historico=config["historico"],
        automatico=True,
        editavel=False,
        tipo_lancamento='provisao',
        referencia_mes=mes_ref,
        pago=False
    )
    
    db.add(lancamento)
    db.commit()
    db.refresh(lancamento)
    
    return lancamento


def lancar_pagamento_pendencia(db: Session, pendencia_id: int, data_pagamento: date_type) -> Optional[models.LancamentoContabil]:
    """
    Cria lançamento contábil quando uma pendência é confirmada (paga).
    
    Lançamentos por tipo (baixa da obrigação):
    - SIMPLES: D: 2.1.4 (Simples a Pagar) / C: 1.1.1 (Caixa)
    - INSS: D: 2.1.5 (INSS a Pagar) / C: 1.1.1 (Caixa)
    - FUNDO_RESERVA: Não gera saída de caixa (apenas transferência interna de PL)
    - LUCRO_SOCIO: D: 2.1.6 (Lucros a Pagar) / C: 1.1.1 (Caixa)
    """
    from database.models import PagamentoPendente
    
    pendencia = db.query(PagamentoPendente).filter(PagamentoPendente.id == pendencia_id).first()
    if not pendencia:
        return None
    
    # Fundo de Reserva não gera saída de caixa
    if pendencia.tipo == "FUNDO_RESERVA":
        return None
    
    # Mapear tipo de pendência para contas contábeis (pagamento)
    mapeamento_contas = {
        "SIMPLES": {
            "debito": "2.1.4",  # Simples a Pagar
            "credito": "1.1.1",  # Caixa
            "historico": f"Pagamento Simples Nacional - {pendencia.descricao}"
        },
        "INSS": {
            "debito": "2.1.5",  # INSS a Pagar
            "credito": "1.1.1",  # Caixa
            "historico": f"Pagamento INSS - {pendencia.descricao}"
        },
        "LUCRO_SOCIO": {
            "debito": "2.1.6",  # Lucros a Pagar
            "credito": "1.1.1",  # Caixa
            "historico": f"Pagamento de lucros - {pendencia.descricao}"
        }
    }
    
    config = mapeamento_contas.get(pendencia.tipo)
    if not config:
        return None  # Tipo não mapeado
    
    # Buscar contas
    conta_debito = buscar_conta_por_codigo(db, config["debito"])
    conta_credito = buscar_conta_por_codigo(db, config["credito"])
    
    if not conta_debito or not conta_credito:
        print(f"⚠️  Contas não encontradas para tipo {pendencia.tipo}: D:{config['debito']} C:{config['credito']}")
        return None
    
    mes_ref = f"{pendencia.ano_ref}-{pendencia.mes_ref:02d}"
    
    # Criar lançamento de pagamento
    lancamento = models.LancamentoContabil(
        data=data_pagamento,
        conta_debito_id=conta_debito.id,
        conta_credito_id=conta_credito.id,
        valor=pendencia.valor,
        historico=config["historico"],
        automatico=True,
        editavel=False,
        tipo_lancamento='pagamento_provisao',
        referencia_mes=mes_ref,
        pago=True,
        data_pagamento=data_pagamento,
        valor_pago=pendencia.valor
    )
    
    db.add(lancamento)
    db.commit()
    db.refresh(lancamento)
    
    return lancamento
