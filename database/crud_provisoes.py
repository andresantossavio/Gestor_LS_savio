"""
CRUD operations para sistema de provisões contábeis automáticas.
Calcula provisões por entrada de honorários e gerencia pagamentos parciais.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Optional
from . import models
from .crud_contabilidade import calcular_pro_labore_iterativo, get_configuracao


def calcular_e_provisionar_entrada(db: Session, entrada_id: int) -> Dict:
    """
    Calcula provisões para uma entrada de honorários e cria registro de ProvisaoEntrada.
    
    Fluxo:
    1. Busca receita dos últimos 12 meses (incluindo entrada atual)
    2. Calcula alíquota Simples e imposto proporcional
    3. Determina lucro bruto (valor - imposto - despesas proporcionais)
    4. Calcula pró-labore usando calcular_pro_labore_iterativo()
    5. Calcula INSS patronal e pessoal
    6. Calcula fundo de reserva (10%)
    7. Distribui lucro disponível (85%) entre sócios baseado em percentuais
    
    Args:
        db: Sessão do banco de dados
        entrada_id: ID da entrada a provisionar
    
    Returns:
        Dict com todos os valores calculados
    """
    # Buscar entrada
    entrada = db.query(models.Entrada).filter(models.Entrada.id == entrada_id).first()
    if not entrada:
        raise ValueError(f"Entrada {entrada_id} não encontrada")
    
    mes_referencia = entrada.data.strftime("%Y-%m")
    
    # 1. Calcular receita dos últimos 12 meses
    data_12m_atras = entrada.data - relativedelta(months=12)
    
    receita_12m = db.query(func.sum(models.Entrada.valor)).filter(
        models.Entrada.data > data_12m_atras,
        models.Entrada.data <= entrada.data
    ).scalar() or 0.0
    
    # 2. Calcular alíquota Simples Nacional
    faixas = db.query(models.SimplesFaixa).filter(
        models.SimplesFaixa.vigencia_inicio <= entrada.data
    ).filter(
        (models.SimplesFaixa.vigencia_fim >= entrada.data) | 
        (models.SimplesFaixa.vigencia_fim == None)
    ).order_by(models.SimplesFaixa.ordem).all()
    
    aliquota_nominal = 0.0
    deducao = 0.0
    
    for faixa in faixas:
        if receita_12m <= faixa.limite_superior:
            aliquota_nominal = faixa.aliquota
            deducao = faixa.deducao
            break
    
    # Alíquota efetiva = (Receita 12M × Alíquota - Dedução) / Receita 12M
    if receita_12m > 0:
        aliquota_efetiva = ((receita_12m * aliquota_nominal) - deducao) / receita_12m
    else:
        aliquota_efetiva = aliquota_nominal
    
    # Imposto proporcional desta entrada
    imposto_entrada = entrada.valor * aliquota_efetiva
    
    # 3. Buscar despesas do mês (proporcionais)
    inicio_mes = entrada.data.replace(day=1)
    if entrada.data.month == 12:
        fim_mes = entrada.data.replace(year=entrada.data.year + 1, month=1, day=1) - relativedelta(days=1)
    else:
        fim_mes = entrada.data.replace(month=entrada.data.month + 1, day=1) - relativedelta(days=1)
    
    despesas_mes = db.query(func.sum(models.Despesa.valor)).filter(
        models.Despesa.data >= inicio_mes,
        models.Despesa.data <= fim_mes
    ).scalar() or 0.0
    
    # Receita total do mês até agora
    receita_mes = db.query(func.sum(models.Entrada.valor)).filter(
        models.Entrada.data >= inicio_mes,
        models.Entrada.data <= entrada.data
    ).scalar() or 0.0
    
    # Despesas proporcionais a esta entrada
    if receita_mes > 0:
        despesas_proporcionais = despesas_mes * (entrada.valor / receita_mes)
    else:
        despesas_proporcionais = 0.0
    
    # 4. Calcular lucro bruto da entrada
    lucro_bruto = entrada.valor - imposto_entrada - despesas_proporcionais
    
    # 5. Identificar sócio administrador e seu percentual nesta entrada
    admin_socio = db.query(models.Socio).filter(
        models.Socio.funcao.ilike('%administrador%')
    ).first()
    
    percentual_contrib_admin = 100.0  # Default se não tiver admin
    
    if admin_socio:
        # Buscar percentual do admin nesta entrada específica
        entrada_socio_admin = db.query(models.EntradaSocio).filter(
            models.EntradaSocio.entrada_id == entrada_id,
            models.EntradaSocio.socio_id == admin_socio.id
        ).first()
        
        if entrada_socio_admin:
            percentual_contrib_admin = entrada_socio_admin.percentual
    
    # 6. Calcular pró-labore e INSS usando função iterativa
    config = get_configuracao(db)
    salario_minimo = config.salario_minimo if config else 1518.0
    
    pro_labore, inss_patronal, inss_pessoal, lucro_liquido = calcular_pro_labore_iterativo(
        lucro_bruto,
        percentual_contrib_admin,
        salario_minimo
    )

    # 5% do lucro líquido já embutido na função iterativa (não gerar campo separado)

    # 7. Calcular fundo de reserva (10%)
    fundo_reserva = lucro_liquido * 0.10
    
    # 8. Calcular lucro disponível total (85%)
    lucro_disponivel_total = lucro_liquido * 0.85
    
    # 9. Distribuir lucro disponível (85%) somente entre sócios NÃO administradores.
    # Administrador terá remuneração via pró-labore; não entra na lista de distribuição.
    distribuicao_socios = []
    
    entradas_socios = db.query(models.EntradaSocio).filter(
        models.EntradaSocio.entrada_id == entrada_id
    ).all()
    
    # Somente percentuais específicos da entrada definem participação.
    if entradas_socios:
        for entrada_socio in entradas_socios:
            socio = db.query(models.Socio).filter(models.Socio.id == entrada_socio.socio_id).first()
            if not socio or (admin_socio and socio.id == admin_socio.id):
                continue
            lucro_socio = lucro_disponivel_total * (entrada_socio.percentual / 100.0)
            distribuicao_socios.append({
                "socio_id": socio.id,
                "nome": socio.nome,
                "percentual_entrada": entrada_socio.percentual,
                "lucro_disponivel": round(lucro_socio, 2)
            })
    
    # 10. Salvar ou atualizar ProvisaoEntrada
    provisao_existente = db.query(models.ProvisaoEntrada).filter(
        models.ProvisaoEntrada.entrada_id == entrada_id
    ).first()
    
    if provisao_existente:
        # Atualizar
        provisao_existente.mes_referencia = mes_referencia
        provisao_existente.data_calculo = datetime.utcnow()
        provisao_existente.receita_12m_base = receita_12m
        provisao_existente.aliquota_simples = aliquota_efetiva
        provisao_existente.imposto_provisionado = imposto_entrada
        provisao_existente.lucro_bruto = lucro_bruto
        # Registrar valores por entrada para geração correta das provisões
        provisao_existente.pro_labore_previsto = pro_labore
        provisao_existente.inss_patronal_previsto = inss_patronal
        provisao_existente.inss_pessoal_previsto = inss_pessoal
        provisao_existente.fundo_reserva_previsto = fundo_reserva
        provisao_existente.lucro_disponivel_total = lucro_disponivel_total
        provisao_existente.distribuicao_socios = distribuicao_socios
        provisao = provisao_existente
    else:
        # Criar nova
        provisao = models.ProvisaoEntrada(
            entrada_id=entrada_id,
            mes_referencia=mes_referencia,
            data_calculo=datetime.utcnow(),
            receita_12m_base=receita_12m,
            aliquota_simples=aliquota_efetiva,
            imposto_provisionado=imposto_entrada,
            lucro_bruto=lucro_bruto,
            pro_labore_previsto=pro_labore,
            inss_patronal_previsto=inss_patronal,
            inss_pessoal_previsto=inss_pessoal,
            fundo_reserva_previsto=fundo_reserva,
            lucro_disponivel_total=lucro_disponivel_total,
            distribuicao_socios=distribuicao_socios
        )
        db.add(provisao)
    
    db.commit()
    db.refresh(provisao)
    
    # Retornar dicionário com todos os valores
    return {
        "entrada_id": entrada_id,
        "mes_referencia": mes_referencia,
        "receita_12m_base": receita_12m,
        "aliquota_simples": aliquota_efetiva,
        "imposto_provisionado": imposto_entrada,
        "lucro_bruto": lucro_bruto,
        "pro_labore_previsto": pro_labore,
        "inss_patronal_previsto": inss_patronal,
        "inss_pessoal_previsto": inss_pessoal,
        "fundo_reserva_previsto": fundo_reserva,
        "lucro_disponivel_total": lucro_disponivel_total,
        "distribuicao_socios": distribuicao_socios
    }


def get_saldo_disponivel_mes(db: Session, mes: int, ano: int, tipo: str = 'all') -> Dict:
    """
    Calcula saldo disponível de um mês: provisões - pagamentos efetivos.
    
    Args:
        db: Sessão do banco
        mes: Mês (1-12)
        ano: Ano (ex: 2024)
        tipo: 'pro_labore', 'inss', 'simples', 'lucros', ou 'all'
    
    Returns:
        Dict com provisões, pagamentos e saldo disponível
    """
    mes_str = f"{ano}-{str(mes).zfill(2)}"
    
    # Buscar todas as provisões do mês
    provisoes = db.query(models.ProvisaoEntrada).filter(
        models.ProvisaoEntrada.mes_referencia == mes_str
    ).all()
    
    # Somar provisões
    pro_labore_previsto = sum(p.pro_labore_previsto for p in provisoes)
    inss_patronal_previsto = sum(p.inss_patronal_previsto for p in provisoes)
    inss_pessoal_previsto = sum(p.inss_pessoal_previsto for p in provisoes)
    inss_total_previsto = inss_patronal_previsto + inss_pessoal_previsto
    imposto_previsto = sum(p.imposto_provisionado for p in provisoes)
    fundo_previsto = sum(p.fundo_reserva_previsto for p in provisoes)
    
    # Agregar lucros por sócio
    lucros_por_socio = {}
    for provisao in provisoes:
        for dist in provisao.distribuicao_socios:
            socio_id = dist['socio_id']
            if socio_id not in lucros_por_socio:
                lucros_por_socio[socio_id] = {
                    'socio_id': socio_id,
                    'nome': dist['nome'],
                    'previsto': 0.0,
                    'pago': 0.0
                }
            lucros_por_socio[socio_id]['previsto'] += dist['lucro_disponivel']
    
    # Calcular pagamentos efetivos do mês
    # Pró-labore (LEGADO): débitos na conta 2.1.3.1 (Pró-labore a Pagar) para 1.1.1 (Caixa)
    conta_pro_labore = db.query(models.PlanoDeContas).filter(
        models.PlanoDeContas.codigo == "2.1.3.1"
    ).first()
    
    pro_labore_pago = 0.0
    if conta_pro_labore:
        pro_labore_pago = db.query(func.sum(models.LancamentoContabil.valor)).filter(
            models.LancamentoContabil.referencia_mes == mes_str,
            models.LancamentoContabil.tipo_lancamento == 'pagamento_pro_labore',
            models.LancamentoContabil.conta_debito_id == conta_pro_labore.id
        ).scalar() or 0.0
    
    # Pró-labore (ATUAL): pagamentos via 3.4 como 'pagamento_lucro' (líquido + INSS 11% retido)
    conta_lucros_para_pro_labore = db.query(models.PlanoDeContas).filter(
        models.PlanoDeContas.codigo == "3.4"
    ).first()
    if conta_lucros_para_pro_labore:
        pro_labore_via_lucros = db.query(func.sum(models.LancamentoContabil.valor)).filter(
            models.LancamentoContabil.referencia_mes == mes_str,
            models.LancamentoContabil.tipo_lancamento == 'pagamento_lucro',
            models.LancamentoContabil.conta_debito_id == conta_lucros_para_pro_labore.id,
            models.LancamentoContabil.historico.ilike('%Pagamento pró-labore%')
        ).scalar() or 0.0
        pro_labore_pago += pro_labore_via_lucros
    
    # INSS: débitos na conta 2.1.2.2 (INSS a Recolher) para 1.1.1 (Caixa)
    conta_inss = db.query(models.PlanoDeContas).filter(
        models.PlanoDeContas.codigo == "2.1.2.2"
    ).first()
    
    inss_pago = 0.0
    if conta_inss:
        inss_pago = db.query(func.sum(models.LancamentoContabil.valor)).filter(
            models.LancamentoContabil.referencia_mes == mes_str,
            models.LancamentoContabil.tipo_lancamento == 'pagamento_imposto',
            models.LancamentoContabil.conta_debito_id == conta_inss.id
        ).scalar() or 0.0
    
    # Simples: débitos na conta 2.1.2.1 (Simples a Recolher) para 1.1.1 (Caixa)
    conta_simples = db.query(models.PlanoDeContas).filter(
        models.PlanoDeContas.codigo == "2.1.2.1"
    ).first()
    
    simples_pago = 0.0
    if conta_simples:
        simples_pago = db.query(func.sum(models.LancamentoContabil.valor)).filter(
            models.LancamentoContabil.referencia_mes == mes_str,
            models.LancamentoContabil.tipo_lancamento == 'pagamento_imposto',
            models.LancamentoContabil.conta_debito_id == conta_simples.id
        ).scalar() or 0.0
    
    # Lucros: débitos na conta 3.4 (Lucros Distribuídos) para 1.1.1 (Caixa)
    conta_lucros = db.query(models.PlanoDeContas).filter(
        models.PlanoDeContas.codigo == "3.4"
    ).first()
    
    if conta_lucros:
        # Buscar pagamentos de lucro agrupados por sócio (usando historico ou outro campo)
        pagamentos_lucro = db.query(models.LancamentoContabil).filter(
            models.LancamentoContabil.referencia_mes == mes_str,
            models.LancamentoContabil.tipo_lancamento == 'pagamento_lucro',
            models.LancamentoContabil.conta_debito_id == conta_lucros.id
        ).all()
        
        # TODO: Melhorar para identificar sócio específico no pagamento
        # Por enquanto, soma total de pagamentos de lucro
        for pagamento in pagamentos_lucro:
            # Tentar extrair socio_id do histórico ou adicionar campo socio_id em LancamentoContabil
            pass
    
    return {
        "mes": mes,
        "ano": ano,
        "mes_referencia": mes_str,
        "pro_labore": {
            "previsto": round(pro_labore_previsto, 2),
            "pago": round(pro_labore_pago, 2),
            "disponivel": round(pro_labore_previsto - pro_labore_pago, 2)
        },
        "inss": {
            "previsto": round(inss_total_previsto, 2),
            "patronal_previsto": round(inss_patronal_previsto, 2),
            "pessoal_previsto": round(inss_pessoal_previsto, 2),
            "pago": round(inss_pago, 2),
            "disponivel": round(inss_total_previsto - inss_pago, 2)
        },
        "simples": {
            "previsto": round(imposto_previsto, 2),
            "pago": round(simples_pago, 2),
            "disponivel": round(imposto_previsto - simples_pago, 2)
        },
        "fundo_reserva": {
            "previsto": round(fundo_previsto, 2)
        },
        "lucros_por_socio": list(lucros_por_socio.values())
    }


def listar_provisoes_mes(db: Session, mes: int, ano: int) -> List[Dict]:
    """
    Lista todas as provisões de um mês com detalhes das entradas.
    
    Returns:
        Lista de dicionários com provisão + dados da entrada
    """
    mes_str = f"{ano}-{str(mes).zfill(2)}"
    
    provisoes = db.query(models.ProvisaoEntrada).filter(
        models.ProvisaoEntrada.mes_referencia == mes_str
    ).all()
    
    resultado = []
    for provisao in provisoes:
        entrada = provisao.entrada
        resultado.append({
            "provisao_id": provisao.id,
            "entrada_id": entrada.id,
            "data": entrada.data.isoformat(),
            "cliente": entrada.cliente,
            "valor_entrada": entrada.valor,
            "imposto_provisionado": provisao.imposto_provisionado,
            "pro_labore_previsto": provisao.pro_labore_previsto,
            "inss_total_previsto": provisao.inss_patronal_previsto + provisao.inss_pessoal_previsto,
            "fundo_reserva_previsto": provisao.fundo_reserva_previsto,
            "distribuicao_socios": provisao.distribuicao_socios
        })
    
    return resultado
