"""
CRUD para Pagamentos Pendentes - Sistema Simplificado
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, extract
from datetime import datetime, date
from typing import List, Optional, Dict
from database.models import PagamentoPendente, Entrada, Socio
from utils.simples import calcular_faixa_simples, calcular_imposto_simples


def listar_pagamentos_pendentes(
    db: Session, 
    mes: Optional[int] = None, 
    ano: Optional[int] = None,
    tipo: Optional[str] = None,
    socio_id: Optional[int] = None,
    apenas_pendentes: bool = False
) -> List[PagamentoPendente]:
    """Lista pagamentos pendentes com filtros opcionais"""
    query = db.query(PagamentoPendente)
    
    if mes:
        query = query.filter(PagamentoPendente.mes_ref == mes)
    if ano:
        query = query.filter(PagamentoPendente.ano_ref == ano)
    if tipo:
        query = query.filter(PagamentoPendente.tipo == tipo)
    if socio_id:
        query = query.filter(PagamentoPendente.socio_id == socio_id)
    if apenas_pendentes:
        query = query.filter(PagamentoPendente.confirmado == False)
    
    return query.order_by(
        PagamentoPendente.ano_ref.desc(),
        PagamentoPendente.mes_ref.desc(),
        PagamentoPendente.tipo
    ).all()


def obter_pagamento_pendente(db: Session, pagamento_id: int) -> Optional[PagamentoPendente]:
    """Obtém um pagamento pendente por ID"""
    return db.query(PagamentoPendente).filter(PagamentoPendente.id == pagamento_id).first()


def confirmar_pagamento(db: Session, pagamento_id: int, data_pagamento: date) -> PagamentoPendente:
    """Marca um pagamento como confirmado e cria lançamento contábil"""
    from database import crud_plano_contas
    
    pagamento = obter_pagamento_pendente(db, pagamento_id)
    if not pagamento:
        raise ValueError(f"Pagamento {pagamento_id} não encontrado")
    
    pagamento.confirmado = True
    pagamento.data_confirmacao = data_pagamento
    pagamento.atualizado_em = datetime.utcnow()
    
    db.commit()
    db.refresh(pagamento)
    
    return pagamento


def desconfirmar_pagamento(db: Session, pagamento_id: int) -> PagamentoPendente:
    """Remove a confirmação de um pagamento e estorna lançamento contábil"""
    from database.models import LancamentoContabil
    
    pagamento = obter_pagamento_pendente(db, pagamento_id)
    if not pagamento:
        raise ValueError(f"Pagamento {pagamento_id} não encontrado")
    
    # Buscar e remover lançamentos contábeis de pagamento relacionados
    mes_ref = f"{pagamento.ano_ref}-{pagamento.mes_ref:02d}"
    lancamentos = db.query(LancamentoContabil).filter(
        and_(
            LancamentoContabil.tipo_lancamento == 'pagamento_provisao',
            LancamentoContabil.referencia_mes == mes_ref,
            LancamentoContabil.historico.like(f"%{pagamento.descricao}%")
        )
    ).all()
    
    for lanc in lancamentos:
        db.delete(lanc)
        print(f"✓ Lançamento contábil {lanc.id} estornado")
    
    pagamento.confirmado = False
    pagamento.data_confirmacao = None
    pagamento.atualizado_em = datetime.utcnow()
    
    db.commit()
    db.refresh(pagamento)
    return pagamento


def excluir_pagamento_pendente(db: Session, pagamento_id: int) -> bool:
    """Exclui um pagamento pendente"""
    pagamento = obter_pagamento_pendente(db, pagamento_id)
    if not pagamento:
        return False
    
    db.delete(pagamento)
    db.commit()
    return True


def gerar_pendencias_mes(db: Session, mes: int, ano: int) -> List[PagamentoPendente]:
    """
    Gera pagamentos pendentes CONSOLIDADOS por mês (não por entrada).
    
    Um único pagamento de SIMPLES por mês, um único de INSS, etc.
    Baseado na DRE consolidada do mês.
    
    Args:
        db: Sessão do banco
        mes: Mês (1-12)
        ano: Ano (ex: 2025)
    
    Returns:
        Lista de pendências geradas
    """
    from database import crud_contabilidade, crud_plano_contas
    
    # Limpar pendências existentes do mês (para recalcular)
    pendencias_existentes = db.query(PagamentoPendente).filter(
        PagamentoPendente.mes_ref == mes,
        PagamentoPendente.ano_ref == ano
    ).all()
    
    for pend in pendencias_existentes:
        db.delete(pend)
    db.commit()
    
    # Buscar ou consolidar DRE do mês
    mes_str = f"{ano}-{mes:02d}"
    dre = crud_contabilidade.consolidar_dre_mes(db, mes_str, forcar_recalculo=False)
    
    if not dre or not dre.consolidado:
        print(f"⚠️  DRE do mês {mes_str} não consolidada. Consolidando automaticamente...")
        dre = crud_contabilidade.consolidar_dre_mes(db, mes_str, forcar_recalculo=True)
    
    pendencias = []
    
    # 1. Simples Nacional
    if dre.imposto > 0:
        pend_simples = PagamentoPendente(
            tipo="SIMPLES",
            descricao=f"Simples Nacional - {mes}/{ano}",
            valor=float(dre.imposto),
            mes_ref=mes,
            ano_ref=ano
        )
        db.add(pend_simples)
        pendencias.append(pend_simples)
    
    # 2. INSS (patronal + pessoal na mesma guia)
    inss_total = float(dre.inss_patronal or 0) + float(dre.inss_pessoal or 0)
    if inss_total > 0:
        pend_inss = PagamentoPendente(
            tipo="INSS",
            descricao=f"INSS (20% patronal + 11% administrador) - {mes}/{ano}",
            valor=inss_total,
            mes_ref=mes,
            ano_ref=ano
        )
        db.add(pend_inss)
        pendencias.append(pend_inss)
    
    # 3. Fundo de Reserva (10% do lucro líquido)
    if dre.reserva_10p > 0:
        pend_fundo = PagamentoPendente(
            tipo="FUNDO_RESERVA",
            descricao=f"Fundo de Reserva (10%) - {mes}/{ano}",
            valor=float(dre.reserva_10p),
            mes_ref=mes,
            ano_ref=ano
        )
        db.add(pend_fundo)
        pendencias.append(pend_fundo)
    
    # 4. Distribuição de lucros por sócio
    # Lucro para distribuir = lucro líquido - fundo reserva
    lucro_para_distribuir = float(dre.lucro_liquido or 0) - float(dre.reserva_10p or 0)
    
    if lucro_para_distribuir > 0:
        # Buscar sócios e suas contribuições no mês
        from database.models import Socio, Entrada, EntradaSocio
        from sqlalchemy import func, extract
        from datetime import date
        
        mes_inicio = date(ano, mes, 1)
        if mes == 12:
            mes_fim = date(ano + 1, 1, 1)
        else:
            mes_fim = date(ano, mes + 1, 1)
        
        # Calcular contribuição de cada sócio nas entradas do mês
        contrib_socios = {}
        total_faturamento = 0.0
        
        entradas_mes = db.query(Entrada).filter(
            Entrada.data >= mes_inicio,
            Entrada.data < mes_fim
        ).all()
        
        for entrada in entradas_mes:
            total_faturamento += float(entrada.valor)
            entradas_socios = db.query(EntradaSocio).filter(
                EntradaSocio.entrada_id == entrada.id
            ).all()
            
            for es in entradas_socios:
                if es.socio_id not in contrib_socios:
                    contrib_socios[es.socio_id] = 0.0
                contrib_socios[es.socio_id] += float(entrada.valor) * (float(es.percentual) / 100.0)
        
        # Gerar pendência de lucro para cada sócio
        for socio_id, contribuicao in contrib_socios.items():
            if contribuicao <= 0:
                continue
            
            socio = db.query(Socio).filter(Socio.id == socio_id).first()
            if not socio:
                continue
            
            # Percentual de contribuição do sócio
            percentual_socio = (contribuicao / total_faturamento * 100.0) if total_faturamento > 0 else 0.0
            lucro_socio_bruto = lucro_para_distribuir * (percentual_socio / 100.0)
            
            # Se é administrador, desconta INSS 11%
            is_admin = socio.funcao and 'Administrador' in socio.funcao
            if is_admin:
                inss_pessoal = float(dre.inss_pessoal or 0)
                lucro_socio_liquido = lucro_socio_bruto - inss_pessoal
                pro_labore = float(dre.pro_labore or 0)
                descricao = f"Lucro {socio.nome} ({percentual_socio:.1f}%) [Admin - Pró-labore R$ {pro_labore:.2f}, líquido INSS 11%] - {mes}/{ano}"
            else:
                lucro_socio_liquido = lucro_socio_bruto
                descricao = f"Lucro {socio.nome} ({percentual_socio:.1f}%) - {mes}/{ano}"
            
            if lucro_socio_liquido > 0:
                pend_lucro = PagamentoPendente(
                    tipo="LUCRO_SOCIO",
                    descricao=descricao,
                    valor=lucro_socio_liquido,
                    mes_ref=mes,
                    ano_ref=ano,
                    socio_id=socio_id
                )
                db.add(pend_lucro)
                pendencias.append(pend_lucro)
    
    db.commit()
    
    for p in pendencias:
        db.refresh(p)
        print(f"✓ Pendência consolidada: {p.tipo} - R$ {p.valor:.2f}")
    
    return pendencias


def gerar_pendencias_entrada(
    db: Session,
    entrada_id: int,
    valor_entrada: float,
    mes: int,
    ano: int,
    receita_12m: float,
    socios: List[Dict],  # [{"id": 1, "nome": "André", "percentual": 50.0, "is_admin": True}, ...]
    administrador_id: Optional[int] = None
) -> List[PagamentoPendente]:
    """
    DEPRECATED: Use gerar_pendencias_mes() ao invés desta função.
    
    Esta função não deve mais ser usada pois gera pendências por entrada,
    mas pagamentos devem ser consolidados por mês (um boleto de SIMPLES/mês, um de INSS/mês).
    
    Mantida apenas para compatibilidade com código legado.
    """
    pendencias = []
    LIMITE_PRO_LABORE = 1518.00  # Teto do pró-labore do administrador
    
    # 1. Simples Nacional
    aliquota, deducao, aliquota_efetiva = calcular_faixa_simples(
        receita_12m, 
        date(ano, mes, 1), 
        db
    )
    imposto_simples = calcular_imposto_simples(valor_entrada, aliquota_efetiva)
    
    pendencia_simples = PagamentoPendente(
        tipo="SIMPLES",
        descricao=f"Simples Nacional - {mes}/{ano}",
        valor=imposto_simples,
        mes_ref=mes,
        ano_ref=ano,
        entrada_id=entrada_id
    )
    db.add(pendencia_simples)
    pendencias.append(pendencia_simples)
    
    # Lucro bruto após Simples (antes de calcular INSS)
    lucro_bruto = valor_entrada - imposto_simples
    
    # 2. Identificar administrador e seu percentual de contribuição
    socio_admin = None
    percentual_contrib_admin = 0.0
    
    if administrador_id:
        socio_admin = next((s for s in socios if s["id"] == administrador_id), None)
    else:
        # Tentar identificar por flag is_admin ou função
        socio_admin = next((s for s in socios if s.get("is_admin") or s.get("funcao") == "Administrador"), None)
    
    if socio_admin:
        percentual_contrib_admin = socio_admin.get("percentual", 0.0)
    
    # 3. CÁLCULO ITERATIVO: pró-labore depende do lucro líquido, que depende do INSS patronal, que depende do pró-labore
    # Fórmula completa do pró-labore:
    # = min(lucro_líquido × 5% + lucro_líquido × 85% × percentual_contrib, R$ 1.518,00)
    
    # Inicializar
    pro_labore_admin = 0.0
    max_iteracoes = 100
    tolerancia = 0.01
    
    for _ in range(max_iteracoes):
        # INSS patronal é despesa (20% do pró-labore)
        inss_patronal = pro_labore_admin * 0.20
        
        # Lucro líquido = lucro bruto - INSS patronal (o pró-labore NÃO é despesa)
        lucro_liquido = lucro_bruto - inss_patronal
        
        # Pró-labore = 5% (parte administrativa) + 85% × percentual_contrib (parte de lucro)
        parte_admin = lucro_liquido * 0.05
        parte_lucro = lucro_liquido * 0.85 * (percentual_contrib_admin / 100.0)
        pro_labore_novo = min(parte_admin + parte_lucro, LIMITE_PRO_LABORE)
        
        # Se negativo, zerar
        if pro_labore_novo < 0:
            pro_labore_novo = 0.0
        
        # Verificar convergência
        if abs(pro_labore_novo - pro_labore_admin) < tolerancia:
            pro_labore_admin = pro_labore_novo
            break
        
        pro_labore_admin = pro_labore_novo
    
    # 4. Calcular INSS final (após convergência)
    inss_patronal = pro_labore_admin * 0.20  # 20% patronal (despesa)
    inss_retido_admin = pro_labore_admin * 0.11  # 11% do administrador (desconto)
    inss_total = inss_patronal + inss_retido_admin  # Pago na mesma guia
    
    pendencia_inss = PagamentoPendente(
        tipo="INSS",
        descricao=f"INSS (20% patronal + 11% administrador) - {mes}/{ano}",
        valor=inss_total,
        mes_ref=mes,
        ano_ref=ano,
        entrada_id=entrada_id
    )
    db.add(pendencia_inss)
    pendencias.append(pendencia_inss)
    
    # Lucro líquido final (após INSS patronal)
    lucro_liquido = lucro_bruto - inss_patronal
    
    # 5. Fundo de Reserva (10% do lucro líquido)
    fundo_reserva = lucro_liquido * 0.10
    pendencia_fundo = PagamentoPendente(
        tipo="FUNDO_RESERVA",
        descricao=f"Fundo de Reserva (10%) - {mes}/{ano}",
        valor=fundo_reserva,
        mes_ref=mes,
        ano_ref=ano,
        entrada_id=entrada_id
    )
    db.add(pendencia_fundo)
    pendencias.append(pendencia_fundo)
    
    # Lucro para distribuição (descontando fundo de reserva)
    lucro_para_distribuir = lucro_liquido - fundo_reserva
    
    # 6. Distribui lucro por sócio (USANDO PERCENTUAL DA ENTRADA, NÃO O FIXO)
    for socio_data in socios:
        # Usa percentual de contribuição nesta entrada específica
        percentual_entrada = socio_data["percentual"]
        
        # Se não tem percentual ou é 0, pula (não contribuiu para esta entrada)
        if not percentual_entrada or percentual_entrada <= 0:
            continue
        
        lucro_socio_bruto = lucro_para_distribuir * (percentual_entrada / 100.0)
        
        # Se é o administrador
        if socio_admin and socio_data["id"] == socio_admin["id"]:
            # Desconta o INSS 11% retido do pró-labore
            lucro_liquido_socio = lucro_socio_bruto - inss_retido_admin
            
            descricao = f"Lucro {socio_data['nome']} ({percentual_entrada:.1f}%) [Admin - Pró-labore R$ {pro_labore_admin:.2f}, líquido INSS 11%] - {mes}/{ano}"
        else:
            # Demais sócios: lucro direto, sem INSS
            lucro_liquido_socio = lucro_socio_bruto
            descricao = f"Lucro {socio_data['nome']} ({percentual_entrada:.1f}%) - {mes}/{ano}"
        
        pendencia_lucro = PagamentoPendente(
            tipo="LUCRO_SOCIO",
            descricao=descricao,
            valor=lucro_liquido_socio,
            mes_ref=mes,
            ano_ref=ano,
            socio_id=socio_data["id"],
            entrada_id=entrada_id
        )
        db.add(pendencia_lucro)
        pendencias.append(pendencia_lucro)
    
    db.commit()
    
    for p in pendencias:
        db.refresh(p)
    
    return pendencias


def obter_resumo_mes(db: Session, mes: int, ano: int) -> Dict:
    """
    Retorna resumo financeiro do mês:
    - Total de entradas
    - Total de saídas confirmadas
    - Total pendente
    - Breakdown por tipo
    """
    # Entradas do mês
    entradas = db.query(Entrada).filter(
        extract('month', Entrada.data_entrada) == mes,
        extract('year', Entrada.data_entrada) == ano
    ).all()
    
    total_entradas = sum(e.valor for e in entradas)
    
    # Pagamentos do mês
    pagamentos = listar_pagamentos_pendentes(db, mes=mes, ano=ano)
    
    total_saidas_confirmadas = sum(p.valor for p in pagamentos if p.confirmado)
    total_pendente = sum(p.valor for p in pagamentos if not p.confirmado)
    
    # Breakdown por tipo
    breakdown = {}
    for p in pagamentos:
        if p.tipo not in breakdown:
            breakdown[p.tipo] = {"confirmado": 0.0, "pendente": 0.0}
        
        if p.confirmado:
            breakdown[p.tipo]["confirmado"] += p.valor
        else:
            breakdown[p.tipo]["pendente"] += p.valor
    
    return {
        "mes": mes,
        "ano": ano,
        "total_entradas": total_entradas,
        "total_saidas_confirmadas": total_saidas_confirmadas,
        "total_pendente": total_pendente,
        "saldo_disponivel": total_entradas - total_saidas_confirmadas - total_pendente,
        "breakdown": breakdown,
        "qtd_entradas": len(entradas),
        "qtd_pagamentos": len(pagamentos),
        "qtd_confirmados": sum(1 for p in pagamentos if p.confirmado),
        "qtd_pendentes": sum(1 for p in pagamentos if not p.confirmado)
    }


def obter_pendencias_por_socio(db: Session, socio_id: int, apenas_pendentes: bool = True) -> Dict:
    """Retorna todas as pendências de um sócio específico"""
    pagamentos = listar_pagamentos_pendentes(
        db, 
        socio_id=socio_id,
        tipo="LUCRO_SOCIO",
        apenas_pendentes=apenas_pendentes
    )
    
    total_pendente = sum(p.valor for p in pagamentos if not p.confirmado)
    total_pago = sum(p.valor for p in pagamentos if p.confirmado)
    
    return {
        "socio_id": socio_id,
        "total_pendente": total_pendente,
        "total_pago": total_pago,
        "pagamentos": pagamentos
    }


def limpar_pagamentos_mes(db: Session, mes_ref: int, ano_ref: int) -> int:
    """
    Remove todos os pagamentos pendentes de um mês específico e seus lançamentos contábeis relacionados.
    
    Args:
        db: Sessão do banco de dados
        mes_ref: Mês de referência (1-12)
        ano_ref: Ano de referência
    
    Returns:
        Quantidade de pagamentos removidos
    """
    from database.models import LancamentoContabil
    
    # Buscar todos os pagamentos pendentes do mês
    pagamentos = db.query(PagamentoPendente).filter(
        PagamentoPendente.mes_ref == mes_ref,
        PagamentoPendente.ano_ref == ano_ref,
        PagamentoPendente.tipo.in_(['SIMPLES', 'INSS', 'PRO_LABORE', 'LUCRO_SOCIO', 'FUNDO_RESERVA'])
    ).all()
    
    contador = 0
    mes_str = f"{ano_ref}-{mes_ref:02d}"
    
    for pagamento in pagamentos:
        # Buscar e remover lançamentos contábeis relacionados
        lancamentos = db.query(LancamentoContabil).filter(
            LancamentoContabil.tipo_lancamento == 'pagamento_provisao',
            LancamentoContabil.referencia_mes == mes_str
        ).all()
        
        # Filtrar lançamentos que mencionam este pagamento na descrição
        for lanc in lancamentos:
            if pagamento.descricao in (lanc.historico or ''):
                db.delete(lanc)
                print(f"✓ Lançamento contábil {lanc.id} removido")
        
        # Remover o pagamento
        db.delete(pagamento)
        contador += 1
    
    db.commit()
    print(f"✓ {contador} pagamento(s) pendente(s) removido(s) de {mes_str}")
    
    return contador


def calcular_vencimento(ano_ref: int, mes_ref: int, dia: int) -> date:
    """
    Calcula a data de vencimento no mês seguinte, tratando virada de ano.
    
    Args:
        ano_ref: Ano de referência
        mes_ref: Mês de referência (1-12)
        dia: Dia do vencimento no mês seguinte
    
    Returns:
        Data de vencimento
    """
    from dateutil.relativedelta import relativedelta
    
    data_base = date(ano_ref, mes_ref, 1)
    data_seguinte = data_base + relativedelta(months=1)
    
    return date(data_seguinte.year, data_seguinte.month, dia)


def gerar_pagamentos_mes_dre(db: Session, mes: str) -> Dict:
    """
    Gera pagamentos pendentes automaticamente a partir de uma DRE consolidada.
    
    Cria pagamentos para:
    - Simples Nacional (vencimento dia 20 do mês seguinte)
    - INSS Total 31% (vencimento dia 20 do mês seguinte)
    - Pró-Labore líquido do administrador (vencimento dia 5 do mês seguinte)
    - Distribuição de lucros aos sócios (vencimento dia 5 do mês seguinte)
    - Fundo de Reserva 10% (vencimento dia 5 do mês seguinte)
    
    Args:
        mes: String no formato 'YYYY-MM'
    
    Returns:
        Dicionário com informações dos pagamentos gerados
    """
    from database import crud_contabilidade
    from calendar import month_name
    import locale
    
    # Configurar locale para português
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except:
            pass
    
    # Extrair ano e mês
    ano_ref, mes_ref = map(int, mes.split('-'))
    
    # Buscar DRE (consolidada ou calcular em tempo real)
    dre = crud_contabilidade.get_dre_mensal(db, mes)
    
    # Se DRE não existe ou não está consolidada, calcular em tempo real
    if not dre or not dre.consolidado:
        from backend.main import _calcular_dre_mes
        ano_int, mes_int = map(int, mes.split('-'))
        dre_calculada = _calcular_dre_mes(db, ano_int, mes_int)
        
        if not dre_calculada:
            raise ValueError(f"Não foi possível calcular DRE para {mes}")
        
        # Criar objeto DRE temporário com valores calculados
        class DRETemp:
            def __init__(self, dados):
                self.imposto = dados.get("imposto", 0)
                self.inss_total = dados.get("inss_total", 0)
                self.pro_labore = dados.get("pro_labore", 0)
                self.lucro_liquido = dados.get("lucro_liquido", 0)
                self.consolidado = False
        
        dre = DRETemp(dre_calculada)
    
    # Limpar pagamentos existentes
    qtd_removida = limpar_pagamentos_mes(db, mes_ref, ano_ref)
    
    # Calcular datas de vencimento
    venc_impostos = calcular_vencimento(ano_ref, mes_ref, 20)
    venc_lucros = calcular_vencimento(ano_ref, mes_ref, 5)
    
    # Nome do mês para descrições
    try:
        mes_nome = month_name[mes_ref].capitalize()
    except:
        mes_nome = str(mes_ref)
    ref_desc = f"{mes_nome}/{ano_ref}"
    
    pagamentos_criados = []
    total_por_tipo = {}
    
    # 1. SIMPLES NACIONAL
    valor_simples = round(float(dre.imposto or 0), 2)
    if valor_simples >= 0.01:
        pag_simples = PagamentoPendente(
            tipo='SIMPLES',
            descricao=f"Simples Nacional - Ref: {ref_desc}",
            valor=valor_simples,
            mes_ref=mes_ref,
            ano_ref=ano_ref,
            confirmado=False,
            data_confirmacao=None
        )
        db.add(pag_simples)
        pagamentos_criados.append(('SIMPLES', valor_simples))
        total_por_tipo['SIMPLES'] = valor_simples
    
    # 2. INSS TOTAL (31% = 20% patronal + 11% pessoal)
    valor_inss = round(float(dre.inss_total or 0), 2)
    if valor_inss >= 0.01:
        pag_inss = PagamentoPendente(
            tipo='INSS',
            descricao=f"INSS Total (31%) - Ref: {ref_desc}",
            valor=valor_inss,
            mes_ref=mes_ref,
            ano_ref=ano_ref,
            confirmado=False,
            data_confirmacao=None
        )
        db.add(pag_inss)
        pagamentos_criados.append(('INSS', valor_inss))
        total_por_tipo['INSS'] = valor_inss
    
    # 3. DISTRIBUIÇÃO DE LUCROS (apenas se houver lucro positivo)
    lucro_liquido = float(dre.lucro_liquido or 0)
    
    if lucro_liquido > 0:
        # Buscar sócio administrador
        admin_socio = db.query(Socio).filter(
            Socio.funcao.ilike('%administrador%')
        ).first()
        # Configuração de salário mínimo
        config = crud_contabilidade.get_configuracao(db)
        salario_minimo = config.salario_minimo if config else 1518.0
        
        # PRÓ-LABORE (limitado ao salário mínimo bruto, paga-se líquido após 11% INSS)
        pro_labore_bruto = min(float(dre.pro_labore or 0), salario_minimo)
        pro_labore_liquido = round(pro_labore_bruto * 0.89, 2)  # 89% = 100% - 11% INSS pessoal
        
        if pro_labore_liquido >= 0.01 and admin_socio:
            pag_prolabore = PagamentoPendente(
                tipo='PRO_LABORE',
                descricao=f"Pró-Labore {admin_socio.nome} - Ref: {ref_desc}",
                valor=pro_labore_liquido,
                mes_ref=mes_ref,
                ano_ref=ano_ref,
                socio_id=admin_socio.id,
                confirmado=False,
                data_confirmacao=None
            )
            db.add(pag_prolabore)
            pagamentos_criados.append(('PRO_LABORE', pro_labore_liquido))
            total_por_tipo['PRO_LABORE'] = pro_labore_liquido
        
        # Calcular valores de distribuição
        # Excedente do administrador: (5% + 85% × % contribuição) - salário mínimo, em líquido
        fundo_valor = round(lucro_liquido * 0.10, 2)
        disponivel_85p = lucro_liquido * 0.85
        # Percentual de contribuição do administrador no mês
        percentual_admin = 0.0
        if admin_socio:
            percentual_admin = crud_contabilidade.calcular_percentual_participacao_socio(db, admin_socio.id, mes)
        distribuicao_admin_bruta = (lucro_liquido * 0.05) + (disponivel_85p * (percentual_admin / 100.0))
        excedente_admin_bruto = max(0.0, distribuicao_admin_bruta - salario_minimo)
        excedente_admin_liquido = round(excedente_admin_bruto * 0.89, 2)
        
        # DISTRIBUIÇÃO AOS SÓCIOS (85% proporcional às entradas)
        socios = crud_contabilidade.get_socios(db)
        total_lucro_socios = 0.0
        
        for socio in socios:
            percentual = crud_contabilidade.calcular_percentual_participacao_socio(db, socio.id, mes)
            valor_socio = round(disponivel_85p * (percentual / 100.0), 2)
            
            # Se for o administrador, adicionar o excedente líquido (acima do salário mínimo)
            if admin_socio and socio.id == admin_socio.id and excedente_admin_liquido > 0:
                valor_socio += excedente_admin_liquido
                valor_socio = round(valor_socio, 2)
            
            if valor_socio >= 0.01:
                pag_lucro = PagamentoPendente(
                    tipo='LUCRO_SOCIO',
                    descricao=f"Distribuição Lucro {socio.nome} - Ref: {ref_desc}",
                    valor=valor_socio,
                    mes_ref=mes_ref,
                    ano_ref=ano_ref,
                    socio_id=socio.id,
                    confirmado=False,
                    data_confirmacao=None
                )
                db.add(pag_lucro)
                pagamentos_criados.append(('LUCRO_SOCIO', valor_socio))
                total_lucro_socios += valor_socio
        
        if total_lucro_socios > 0:
            total_por_tipo['LUCRO_SOCIO'] = total_lucro_socios
        
        # FUNDO DE RESERVA (10%)
        if fundo_valor >= 0.01:
            pag_fundo = PagamentoPendente(
                tipo='FUNDO_RESERVA',
                descricao=f"Fundo de Reserva (10%) - Ref: {ref_desc}",
                valor=fundo_valor,
                mes_ref=mes_ref,
                ano_ref=ano_ref,
                confirmado=False,
                data_confirmacao=None
            )
            db.add(pag_fundo)
            pagamentos_criados.append(('FUNDO_RESERVA', fundo_valor))
            total_por_tipo['FUNDO_RESERVA'] = fundo_valor
    
    db.commit()
    
    return {
        "mes": mes,
        "qtd_removida": qtd_removida,
        "qtd_criada": len(pagamentos_criados),
        "pagamentos": pagamentos_criados,
        "total_por_tipo": total_por_tipo
    }


def recalcular_pagamentos_se_nao_consolidado(db: Session, data_entrada: date) -> bool:
    """Recalcula pagamentos pendentes do mês se não estiver consolidado.
    
    Args:
        db: Sessão do banco
        data_entrada: Data da entrada/despesa para extrair ano e mês
    
    Returns:
        True se recalculou, False se mês consolidado ou erro
    """
    from database import crud_contabilidade
    
    try:
        # Formatar mês no padrão YYYY-MM
        mes_str = data_entrada.strftime('%Y-%m')
        
        # Verificar se DRE está consolidada
        dre = crud_contabilidade.get_dre_mensal(db, mes_str)
        if dre and dre.consolidado:
            print(f"⏭️  Mês {mes_str} consolidado - pagamentos não recalculados")
            return False
        
        # Recalcular pagamentos (vai limpar e recriar)
        resultado = gerar_pagamentos_mes_dre(db, mes_str)
        print(f"✓ Pagamentos recalculados para {mes_str}: {resultado['qtd_criada']} criados")
        return True
        
    except Exception as e:
        print(f"⚠️  Erro ao recalcular pagamentos: {e}")
        return False
