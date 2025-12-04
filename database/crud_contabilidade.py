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
    """Registra um aporte de capital e gera lançamento contábil correspondente"""
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
        
        # Gerar lançamento contábil baseado no tipo de aporte
        # Mapear tipo de aporte para conta de débito
        conta_debito_codigo = {
            'dinheiro': '1.1.1.1',  # Caixa Corrente
            'bens': '1.2.1.1',      # Equipamentos e Móveis (Imobilizado)
            'servicos': '1.2.2.1'   # Serviços Capitalizados (Intangível)
        }.get(aporte.tipo_aporte, '1.1.1.1')
        
        conta_debito = crud_plano_contas.buscar_conta_por_codigo(db, conta_debito_codigo)
        conta_capital = crud_plano_contas.buscar_conta_por_codigo(db, "3.1")
        
        if conta_debito and conta_capital:
            historico = f"Aporte de capital - {socio.nome} - {aporte.tipo_aporte}"
            if aporte.descricao:
                historico += f" - {aporte.descricao}"
            
            crud_plano_contas.criar_lancamento(
                db=db,
                data=aporte.data,
                conta_debito_id=conta_debito.id,
                conta_credito_id=conta_capital.id,
                valor=aporte.valor,
                historico=historico,
                automatico=True,
                editavel=False,
                criado_por=None
            )
    
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
    """Atualiza um aporte de capital e ajusta lançamentos contábeis"""
    db_aporte = get_aporte(db, aporte_id)
    if not db_aporte:
        return None
    
    valor_antigo = db_aporte.valor
    tipo_antigo = db_aporte.tipo_aporte
    data_antiga = db_aporte.data
    
    # Buscar lançamento contábil associado (se existir)
    lancamento_antigo = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.historico.like(f"%Aporte de capital%{db_aporte.socio.nome if db_aporte.socio else ''}%"),
        models.LancamentoContabil.data == data_antiga,
        models.LancamentoContabil.valor == valor_antigo
    ).first()
    
    # Atualizar dados do aporte (suporta dict ou objeto)
    if isinstance(update_data, dict):
        if 'data' in update_data:
            db_aporte.data = update_data['data']
        if 'valor' in update_data:
            db_aporte.valor = update_data['valor']
        if 'tipo_aporte' in update_data:
            db_aporte.tipo_aporte = update_data['tipo_aporte']
        if 'descricao' in update_data:
            db_aporte.descricao = update_data['descricao']
    else:
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
    socio = get_socio(db, db_aporte.socio_id)
    if socio:
        if tipo_antigo in ['dinheiro', 'bens', 'servicos']:
            socio.capital_social = (socio.capital_social or 0) - valor_antigo
        if db_aporte.tipo_aporte in ['dinheiro', 'bens', 'servicos']:
            socio.capital_social = (socio.capital_social or 0) + db_aporte.valor
    
    # Atualizar ou criar lançamento contábil
    if db_aporte.tipo_aporte in ['dinheiro', 'bens', 'servicos']:
        # Mapear tipo de aporte para conta de débito
        conta_debito_codigo = {
            'dinheiro': '1.1.1.1',  # Caixa Corrente
            'bens': '1.2.1.1',      # Equipamentos e Móveis (Imobilizado)
            'servicos': '1.2.2.1'   # Serviços Capitalizados (Intangível)
        }.get(db_aporte.tipo_aporte, '1.1.1.1')
        
        conta_debito = crud_plano_contas.buscar_conta_por_codigo(db, conta_debito_codigo)
        conta_capital = crud_plano_contas.buscar_conta_por_codigo(db, "3.1")
        
        if conta_debito and conta_capital:
            historico = f"Aporte de capital - {socio.nome if socio else 'N/A'} - {db_aporte.tipo_aporte}"
            if db_aporte.descricao:
                historico += f" - {db_aporte.descricao}"
            
            if lancamento_antigo:
                # Atualizar lançamento existente
                lancamento_antigo.data = db_aporte.data
                lancamento_antigo.valor = db_aporte.valor
                lancamento_antigo.historico = historico
                lancamento_antigo.conta_debito_id = conta_debito.id
            else:
                # Criar novo lançamento
                crud_plano_contas.criar_lancamento(
                    db=db,
                    data=db_aporte.data,
                    conta_debito_id=conta_debito.id,
                    conta_credito_id=conta_capital.id,
                    valor=db_aporte.valor,
                    historico=historico,
                    automatico=True,
                    editavel=False,
                    criado_por=None
                )
    elif lancamento_antigo and tipo_antigo in ['dinheiro', 'bens', 'servicos']:
        # Se mudou de tipo que gerava lançamento para tipo que não gera, excluir lançamento
        db.delete(lancamento_antigo)
    
    db.commit()
    db.refresh(db_aporte)
    return db_aporte


def delete_aporte_capital(db: Session, aporte_id: int) -> bool:
    """Deleta um aporte de capital e remove lançamento contábil associado"""
    db_aporte = get_aporte(db, aporte_id)
    if not db_aporte:
        return False
    
    # Buscar e excluir lançamento contábil associado
    if db_aporte.tipo_aporte in ['dinheiro', 'bens', 'servicos']:
        lancamento = db.query(models.LancamentoContabil).filter(
            models.LancamentoContabil.historico.like(f"%Aporte de capital%{db_aporte.socio.nome if db_aporte.socio else ''}%"),
            models.LancamentoContabil.data == db_aporte.data,
            models.LancamentoContabil.valor == db_aporte.valor
        ).first()
        
        if lancamento:
            db.delete(lancamento)
    
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
    db.flush()  # Garante que db_entrada.id esteja disponível
    
    # Adicionar sócios e seus percentuais (evitar duplicatas)
    socios_adicionados = set()
    for socio_data in entrada.socios:
        # Verificar se já não foi adicionado (evita duplicatas no mesmo request)
        chave = (db_entrada.id, socio_data.socio_id)
        if chave in socios_adicionados:
            continue
            
        # Verificar se já existe no banco (para caso de retry)
        entrada_socio_existente = db.query(models.EntradaSocio).filter(
            models.EntradaSocio.entrada_id == db_entrada.id,
            models.EntradaSocio.socio_id == socio_data.socio_id
        ).first()
        
        if not entrada_socio_existente:
            entrada_socio = models.EntradaSocio(
                entrada_id=db_entrada.id,
                socio_id=socio_data.socio_id,
                percentual=socio_data.percentual
            )
            db.add(entrada_socio)
            socios_adicionados.add(chave)
    
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
    db.flush()  # Garante que db_despesa.id esteja disponível
    
    # Adicionar responsáveis (evitar duplicatas)
    responsaveis_adicionados = set()
    for resp_data in despesa.responsaveis:
        # Verificar se já não foi adicionado (evita duplicatas no mesmo request)
        chave = (db_despesa.id, resp_data.socio_id)
        if chave in responsaveis_adicionados:
            continue
            
        # Verificar se já existe no banco (para caso de retry)
        despesa_socio_existente = db.query(models.DespesaSocio).filter(
            models.DespesaSocio.despesa_id == db_despesa.id,
            models.DespesaSocio.socio_id == resp_data.socio_id
        ).first()
        
        if not despesa_socio_existente:
            despesa_socio = models.DespesaSocio(
                despesa_id=db_despesa.id,
                socio_id=resp_data.socio_id
            )
            db.add(despesa_socio)
            responsaveis_adicionados.add(chave)
    
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
    
    elif operacao_codigo == "APLICAR_RESERVA_CDB":
        _executar_reservar_fundo(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "PROVISIONAR_SIMPLES":
        _executar_provisionar_simples(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "SEPARAR_OBRIGACOES_FISCAIS":
        _executar_separar_obrigacoes_fiscais(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "SEPARAR_PRO_LABORE":
        _executar_separar_pro_labore(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "RESGATAR_CDB_OBRIGACOES_FISCAIS":
        _executar_resgatar_cdb_obrigacoes_fiscais(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "RESGATAR_CDB_LUCROS":
        _executar_resgatar_cdb_lucros(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "PAGAR_SIMPLES":
        _executar_pagar_simples(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "PAGAR_PRO_LABORE":
        _executar_pagar_pro_labore(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "PRO_LABORE":
        _executar_pro_labore(db, operacao_contabil, valor, data, descricao, criado_por_id)

    elif operacao_codigo == "INSS_PESSOAL":
        _executar_inss_pessoal(db, operacao_contabil, valor, data, descricao, criado_por_id)
    
    elif operacao_codigo == "INSS_PATRONAL":
        _executar_inss_patronal(db, operacao_contabil, valor, data, descricao, criado_por_id)
    
    elif operacao_codigo == "PAGAR_INSS":
        _executar_pagar_inss(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "APLICAR_LUCROS_CDB":
        _executar_aplicar_lucros_cdb(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "ADIANTAR_LUCROS":
        _executar_adiantar_lucros(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "DISTRIBUIR_LUCROS":
        _executar_distribuir_lucros(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "PAGAR_DESPESA_FUNDO":
        _executar_pagar_despesa_fundo(db, operacao_contabil, valor, data, descricao, criado_por_id)
    
    elif operacao_codigo == "RESGATAR_CDB_RESERVA":
        _executar_baixar_fundo(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "RECONHECER_RESERVA_LEGAL":
        _executar_reconhecer_reserva_legal(db, operacao_contabil, valor, data, descricao)
    
    elif operacao_codigo == "RECONHECER_RENDIMENTO_CDB":
        # Requer tipo_cdb como parâmetro adicional
        tipo_cdb = descricao.split(':')[1].strip() if descricao and ':' in descricao else None
        if not tipo_cdb:
            raise ValueError("RECONHECER_RENDIMENTO_CDB requer especificar o tipo de CDB (OBRIGACOES_FISCAIS, RESERVA_LUCROS ou RESERVA_LEGAL) no campo descrição. Formato: 'Tipo: RESERVA_LUCROS'")
        _executar_reconhecer_rendimento_cdb(db, operacao_contabil, valor, data, None, tipo_cdb)
    
    elif operacao_codigo == "APURAR_RESULTADO":
        _executar_apurar_resultado(db, operacao_contabil, valor, data, descricao)
    
    else:
        raise ValueError(f"Operação '{operacao_codigo}' não implementada")
    
    db.commit()
    db.refresh(operacao_contabil)
    return operacao_contabil


def _executar_rec_hon(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """REC_HON: D-Caixa Corrente / C-Receita"""
    conta_caixa = _buscar_conta_por_codigo(db, "1.1.1.1")
    conta_receita = _buscar_conta_por_codigo(db, "4.1.1")
    
    if not conta_caixa or not conta_receita:
        raise ValueError("Contas 1.1.1.1 (Caixa Corrente) ou 4.1.1 (Receita) não encontradas")
    
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
    """
    APLICAR_RESERVA_CDB: D-CDB Reserva Legal / C-Caixa Corrente
    
    Aplicação simples de dinheiro em CDB de Reserva Legal.
    - Apenas move dinheiro do Caixa para o CDB (Ativo → Ativo)
    - NÃO mexe no PL ainda
    - Pode ser executado durante o mês, antes de apurar resultado
    - Exige informar sócio apenas para controle/histórico
    
    No fechamento do mês, executar RECONHECER_RESERVA_LEGAL para 
    transferir lucros apurados para a reserva do sócio no PL.
    """
    # Validar presença de sócio
    if not op.socio_id:
        raise ValueError(
            "APLICAR_RESERVA_CDB exige informar o sócio. "
            "Selecione o sócio beneficiário da reserva."
        )
    
    # Criar/obter subconta de CDB específica do sócio
    # Formato: 1.1.1.2.3.{socio_id} - CDB Reserva Legal - {Nome}
    subconta_cdb = crud_plano_contas._criar_subconta_cdb_reserva_socio(db, op.socio_id)
    
    # Buscar Caixa Corrente
    conta_caixa_corrente = _buscar_conta_por_codigo(db, "1.1.1.1")
    if not conta_caixa_corrente:
        raise ValueError("Conta 1.1.1.1 (Caixa Corrente) não encontrada")
    
    # Validar saldo em Caixa Corrente
    saldo_caixa = crud_plano_contas.calcular_saldo_conta(db, conta_caixa_corrente.id)
    if saldo_caixa < valor:
        raise ValueError(
            f"💰 Saldo insuficiente em Caixa Corrente para aplicar em CDB.\n"
            f"Saldo disponível: R$ {saldo_caixa:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n"
            f"Faltam: R$ {valor - saldo_caixa:.2f}\n\n"
            f"💡 Dica: Receba honorários primeiro ou resgateoutros CDBs."
        )
    
    # Lançamento ÚNICO: D-CDB Reserva Legal (subconta do sócio) / C-Caixa Corrente
    # Move dinheiro de Caixa para CDB específico do sócio
    # Isso permite rastreamento exato de quanto cada sócio tem no CDB
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=subconta_cdb.id,
        conta_credito_id=conta_caixa_corrente.id,
        valor=valor,
        historico=historico or f"Aplicação em CDB - reserva legal {op.socio.nome if op.socio else 'N/A'}",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_reconhecer_reserva_legal(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """
    RECONHECER_RESERVA_LEGAL: D-Lucros Acumulados / C-Reserva do Sócio (PL)
    
    Operação de fechamento mensal para reconhecer no PL os valores
    que foram aplicados em CDB de Reserva Legal durante o mês.
    
    Pré-requisito: APURAR_RESULTADO (precisa ter lucros acumulados)
    
    Fluxo completo:
    1. Durante o mês: APLICAR_RESERVA_CDB (várias vezes)
    2. Fim do mês: APURAR_RESULTADO
    3. Fim do mês: RECONHECER_RESERVA_LEGAL (valor total aplicado no mês)
    """
    # Validar presença de sócio
    if not op.socio_id:
        raise ValueError(
            "RECONHECER_RESERVA_LEGAL exige informar o sócio. "
            "Selecione o sócio beneficiário da reserva."
        )
    
    # Buscar conta de Lucros Acumulados
    conta_lucros = _buscar_conta_por_codigo(db, "3.3")
    if not conta_lucros:
        raise ValueError("Conta 3.3 (Lucros Acumulados) não encontrada")
    
    # Validar saldo em Lucros Acumulados
    saldo_lucros = crud_plano_contas.calcular_saldo_conta(db, conta_lucros.id)
    if saldo_lucros < valor:
        raise ValueError(
            f"💰 Saldo insuficiente em Lucros Acumulados.\n"
            f"Saldo disponível: R$ {saldo_lucros:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n"
            f"Faltam: R$ {valor - saldo_lucros:.2f}\n\n"
            f"💡 Dica: Execute APURAR_RESULTADO antes de reconhecer reservas."
        )
    
    # Criar/obter subconta de reserva do sócio
    subconta_reserva = crud_plano_contas._criar_subconta_reserva_socio(db, op.socio_id)
    
    # Lançamento: D-Lucros Acumulados / C-Reserva do Sócio (PL)
    # Move lucro para reserva específica do sócio no PL
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_lucros.id,
        conta_credito_id=subconta_reserva.id,
        valor=valor,
        historico=historico or f"Constituição de reserva legal - {op.socio.nome if op.socio else 'N/A'}",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_pro_labore(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str], criado_por: Optional[int]):
    """PRO_LABORE: D-Despesa INSS Pessoal / C-Pró-labore a Pagar"""
    conta_despesa_pl = _buscar_conta_por_codigo(db, "5.1.1")
    conta_passivo = _buscar_conta_por_codigo(db, "2.1.3.1")
    
    if not conta_despesa_pl or not conta_passivo:
        raise ValueError("Contas 5.1.1 (INSS Pessoal) ou 2.1.3.1 (Pró-labore a Pagar) não encontradas")
    
    # Lançamento de provisão (não é pagamento)
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_despesa_pl.id,
        conta_credito_id=conta_passivo.id,
        valor=valor,
        historico=historico or "Provisão de pró-labore",
        automatico=True,
        editavel=True,
        criado_por=criado_por
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_inss_pessoal(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str], criado_por: Optional[int]):
    """INSS_PESSOAL: D-Despesa INSS Pessoal / C-INSS a Recolher"""
    conta_despesa_pl = _buscar_conta_por_codigo(db, "5.1.1")
    conta_inss = _buscar_conta_por_codigo(db, "2.1.2.2")
    
    if not conta_despesa_pl or not conta_inss:
        raise ValueError("Contas 5.1.1 (INSS Pessoal) ou 2.1.2.2 (INSS a Recolher) não encontradas")
    
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
    """INSS_PATRONAL: D-Despesa INSS Patronal / C-INSS a Recolher"""
    conta_despesa_inss = _buscar_conta_por_codigo(db, "5.1.3")
    conta_inss = _buscar_conta_por_codigo(db, "2.1.2.2")
    
    if not conta_despesa_inss or not conta_inss:
        raise ValueError("Contas 5.1.3 (INSS Patronal) ou 2.1.2.2 (INSS a Recolher) não encontradas")
    
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
    """PAGAR_INSS: D-INSS a Recolher / C-Caixa Corrente
    Pagamento sai do Caixa Corrente (user deve resgatar CDB antes se necessário)
    """
    conta_inss = _buscar_conta_por_codigo(db, "2.1.2.2")
    conta_caixa_corrente = _buscar_conta_por_codigo(db, "1.1.1.1")
    
    if not conta_inss or not conta_caixa_corrente:
        raise ValueError("Contas 2.1.2.2 (INSS a Recolher) ou 1.1.1.1 (Caixa Corrente) não encontradas")
    
    # Validar saldo de INSS a Recolher
    saldo_inss = crud_plano_contas.calcular_saldo_conta(db, conta_inss.id)
    if saldo_inss < valor:
        raise ValueError(
            f"📋 Obrigação insuficiente em INSS a Recolher.\n"
            f"Saldo da obrigação: R$ {saldo_inss:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n\n"
            f"💡 Dica: Execute INSS_PESSOAL ou INSS_PATRONAL antes de pagar o INSS."
        )
    
    # Validar saldo em Caixa Corrente
    saldo_caixa = crud_plano_contas.calcular_saldo_conta(db, conta_caixa_corrente.id)
    if saldo_caixa < valor:
        raise ValueError(
            f"💰 Saldo insuficiente em Caixa Corrente.\n"
            f"Saldo disponível: R$ {saldo_caixa:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n"
            f"Faltam: R$ {valor - saldo_caixa:.2f}\n\n"
            f"💡 Dica: Execute RESGATAR_CDB_OBRIGACOES_FISCAIS primeiro para ter saldo no caixa."
        )
    
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_inss.id,
        conta_credito_id=conta_caixa_corrente.id,
        valor=valor,
        historico=historico or "Pagamento de INSS",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_distribuir_lucros(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """DISTRIBUIR_LUCROS: D-Lucros Acum. / C-Caixa Corrente"""
    conta_lucros = _buscar_conta_por_codigo(db, "3.3")
    conta_caixa = _buscar_conta_por_codigo(db, "1.1.1.1")
    
    if not conta_lucros or not conta_caixa:
        raise ValueError("Contas 3.3 (Lucros Acumulados) ou 1.1.1.1 (Caixa Corrente) não encontradas")
    
    # Validar saldo de lucros
    saldo_lucros = crud_plano_contas.calcular_saldo_conta(db, conta_lucros.id)
    if saldo_lucros < valor:
        raise ValueError(f"Saldo insuficiente em Lucros Acumulados. Saldo: R$ {saldo_lucros:.2f}, Valor: R$ {valor:.2f}")
    
    # Validar saldo em Caixa Corrente (precisa ter dinheiro para distribuir)
    saldo_caixa = crud_plano_contas.calcular_saldo_conta(db, conta_caixa.id)
    if saldo_caixa < valor:
        raise ValueError(
            f"💰 Saldo insuficiente em Caixa Corrente para distribuir lucros.\n"
            f"Saldo disponível: R$ {saldo_caixa:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n"
            f"Faltam: R$ {valor - saldo_caixa:.2f}"
        )
    
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
    """PAGAR_DESPESA_FUNDO: D-Outras Despesas / C-Caixa Corrente"""
    conta_despesas = _buscar_conta_por_codigo(db, "5.2")
    conta_caixa = _buscar_conta_por_codigo(db, "1.1.1.1")
    
    if not conta_despesas or not conta_caixa:
        raise ValueError("Contas 5.2 (Despesas Operacionais) ou 1.1.1.1 (Caixa Corrente) não encontradas")
    
    # Validar saldo em Caixa Corrente
    saldo_caixa = crud_plano_contas.calcular_saldo_conta(db, conta_caixa.id)
    if saldo_caixa < valor:
        raise ValueError(
            f"💰 Saldo insuficiente em Caixa Corrente para pagar despesa.\n"
            f"Saldo disponível: R$ {saldo_caixa:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n"
            f"Faltam: R$ {valor - saldo_caixa:.2f}"
        )
    
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
    """
    BAIXAR_FUNDO: D-Reserva (subconta do sócio) / C-Lucros Acum.
    
    MODIFICADO: Agora exige socio_id e debita da subconta específica
    """
    # Validar presença de sócio
    if not op.socio_id:
        raise ValueError(
            "BAIXAR_FUNDO exige informar o sócio. "
            "Selecione de qual sócio a reserva será baixada."
        )
    
    # Buscar subconta de reserva do sócio
    codigo_subconta = f"3.2.1.{op.socio_id}"
    conta_reserva = _buscar_conta_por_codigo(db, codigo_subconta)
    
    if not conta_reserva:
        raise ValueError(
            f"Subconta de reserva não encontrada para o sócio {op.socio.nome if op.socio else 'ID ' + str(op.socio_id)}. "
            f"Execute 'RESERVAR_FUNDO' primeiro para criar a subconta."
        )
    
    # Validar saldo na subconta
    saldo_reserva = crud_plano_contas.calcular_saldo_conta(db, conta_reserva.id)
    if saldo_reserva < valor:
        raise ValueError(
            f"Saldo insuficiente na reserva de {op.socio.nome if op.socio else 'N/A'}. "
            f"Saldo disponível: R$ {saldo_reserva:.2f}, Valor solicitado: R$ {valor:.2f}"
        )
    
    # Buscar conta de Lucros Acumulados
    conta_lucros = _buscar_conta_por_codigo(db, "3.3")
    if not conta_lucros:
        raise ValueError("Conta 3.3 (Lucros Acumulados) não encontrada")
    
    # Buscar subconta de CDB específica do sócio
    codigo_subconta_cdb = f"1.1.1.2.3.{op.socio_id}"
    subconta_cdb = _buscar_conta_por_codigo(db, codigo_subconta_cdb)
    
    if not subconta_cdb:
        raise ValueError(
            f"Subconta de CDB não encontrada para o sócio {op.socio.nome if op.socio else 'ID ' + str(op.socio_id)}. "
            f"Execute 'APLICAR_RESERVA_CDB' primeiro para criar a subconta."
        )
    
    # Buscar Caixa Corrente
    conta_caixa_corrente = _buscar_conta_por_codigo(db, "1.1.1.1")
    if not conta_caixa_corrente:
        raise ValueError("Conta 1.1.1.1 (Caixa Corrente) não encontrada")
    
    # Validar saldo na subconta de CDB do sócio
    saldo_cdb = crud_plano_contas.calcular_saldo_conta(db, subconta_cdb.id)
    if saldo_cdb < valor:
        raise ValueError(
            f"💰 Saldo insuficiente em CDB de {op.socio.nome if op.socio else 'N/A'}.\n"
            f"Saldo disponível: R$ {saldo_cdb:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n"
            f"Faltam: R$ {valor - saldo_cdb:.2f}\n\n"
            f"💡 Dica: Execute APLICAR_RESERVA_CDB antes de resgatar."
        )
    
    # Lançamento 1: D-Caixa Corrente / C-CDB Reserva Legal (subconta do sócio) (resgate)
    lancamento1 = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_caixa_corrente.id,
        conta_credito_id=subconta_cdb.id,
        valor=valor,
        historico=historico or f"Resgate de CDB - reserva legal {op.socio.nome if op.socio else 'N/A'}",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento1.operacao_contabil_id = op.id
    lancamento1.referencia_mes = op.mes_referencia
    
    # Lançamento 2: D-Reserva (sócio) / C-Lucros Acum (reversão no PL)
    lancamento2 = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_reserva.id,
        conta_credito_id=conta_lucros.id,
        valor=valor,
        historico=historico or f"Reversão de reserva legal - {op.socio.nome if op.socio else 'N/A'}",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento2.operacao_contabil_id = op.id
    lancamento2.referencia_mes = op.mes_referencia


def _executar_apurar_resultado(
    db: Session, 
    op: models.OperacaoContabil, 
    valor: float, 
    data: date_type, 
    historico: Optional[str]
):
    """
    APURAR_RESULTADO: Transfere lucro líquido para Lucros Acumulados
    
    Lançamento:
    - Lucro positivo: D-4.9.9 (técnica) / C-3.3 (Lucros Acum)
    - Prejuízo: D-3.3 / C-4.9.9
    
    Validações:
    - Não permite executar duas vezes no mesmo mês
    - Valor deve ser diferente de zero
    """
    # Validar valor
    if abs(valor) < 0.01:
        raise ValueError("Valor de apuração deve ser diferente de zero")
    
    # Calcular mês de referência
    mes_ref = op.mes_referencia  # Formato YYYY-MM
    
    # Verificar se já existe apuração para este mês (exceto a própria operação em caso de edição)
    existe_apuracao = db.query(models.OperacaoContabil).join(
        models.Operacao
    ).filter(
        models.Operacao.codigo == "APURAR_RESULTADO",
        models.OperacaoContabil.mes_referencia == mes_ref,
        models.OperacaoContabil.cancelado == False,
        models.OperacaoContabil.id != op.id  # Permitir edição da mesma operação
    ).first()
    
    if existe_apuracao:
        raise ValueError(
            f"Já existe apuração de resultado para {mes_ref}. "
            f"Cancele a operação anterior (ID {existe_apuracao.id}) antes de criar uma nova."
        )
    
    # Utilizar função existente de fechamento de resultado
    lancamento = crud_plano_contas.registrar_fechamento_resultado(
        db=db,
        mes=mes_ref,
        valor_resultado=valor,
        recriar=True  # Permite sobrescrever se necessário
    )
    
    if lancamento:
        # Vincular lançamento à operação
        lancamento.operacao_contabil_id = op.id
        lancamento.referencia_mes = mes_ref
        lancamento.historico = historico or f"Apuração do resultado - {mes_ref}"
        db.commit()
    else:
        raise ValueError("Falha ao criar lançamento de apuração")


def _executar_provisionar_simples(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """PROVISIONAR_SIMPLES: D-Despesa Simples / C-Simples a Recolher"""
    conta_despesa = _buscar_conta_por_codigo(db, "5.3.1")
    conta_passivo = _buscar_conta_por_codigo(db, "2.1.2.1")
    
    if not conta_despesa or not conta_passivo:
        raise ValueError("Contas 5.3.1 (Despesa Simples) ou 2.1.2.1 (Simples a Recolher) não encontradas")
    
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_despesa.id,
        conta_credito_id=conta_passivo.id,
        valor=valor,
        historico=historico or "Provisão de Simples Nacional",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_separar_obrigacoes_fiscais(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """SEPARAR_OBRIGACOES_FISCAIS: D-CDB - Obrigações Fiscais / C-Caixa Corrente
    Aplicação direta de dinheiro em CDB para INSS + Simples Nacional
    """
    conta_cdb_obrigacoes = _buscar_conta_por_codigo(db, "1.1.1.2.1")
    conta_caixa_corrente = _buscar_conta_por_codigo(db, "1.1.1.1")
    
    if not conta_cdb_obrigacoes or not conta_caixa_corrente:
        raise ValueError("Contas 1.1.1.2.1 (CDB - Obrigações Fiscais) ou 1.1.1.1 (Caixa Corrente) não encontradas")
    
    # Validar saldo em Caixa Corrente
    saldo_caixa = crud_plano_contas.calcular_saldo_conta(db, conta_caixa_corrente.id)
    if saldo_caixa < valor:
        raise ValueError(
            f"💰 Saldo insuficiente em Caixa Corrente para separar obrigações fiscais.\n"
            f"Saldo disponível: R$ {saldo_caixa:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n"
            f"Faltam: R$ {valor - saldo_caixa:.2f}\n\n"
            f"💡 Dica: Execute REC_HON (Receber Honorários) primeiro para ter saldo disponível."
        )
    
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_cdb_obrigacoes.id,
        conta_credito_id=conta_caixa_corrente.id,
        valor=valor,
        historico=historico or "Aplicação em CDB - Obrigações Fiscais (INSS + Simples)",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_separar_pro_labore(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """SEPARAR_PRO_LABORE: D-CDB - Reserva de Lucros / C-Caixa Corrente
    Aplicação direta de dinheiro em CDB para pró-labore
    """
    conta_cdb_pl = _buscar_conta_por_codigo(db, "1.1.1.2.2")
    conta_caixa_corrente = _buscar_conta_por_codigo(db, "1.1.1.1")
    
    if not conta_cdb_pl or not conta_caixa_corrente:
        raise ValueError("Contas 1.1.1.2.2 (CDB - Reserva de Lucros) ou 1.1.1.1 (Caixa Corrente) não encontradas")
    
    # Validar saldo em Caixa Corrente
    saldo_caixa = crud_plano_contas.calcular_saldo_conta(db, conta_caixa_corrente.id)
    if saldo_caixa < valor:
        raise ValueError(
            f"💰 Saldo insuficiente em Caixa Corrente para separar pró-labore.\n"
            f"Saldo disponível: R$ {saldo_caixa:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n"
            f"Faltam: R$ {valor - saldo_caixa:.2f}\n\n"
            f"💡 Dica: Execute REC_HON (Receber Honorários) primeiro para ter saldo disponível."
        )
    
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_cdb_pl.id,
        conta_credito_id=conta_caixa_corrente.id,
        valor=valor,
        historico=historico or "Aplicação em CDB - Reserva de Lucros (pró-labore)",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_pagar_simples(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """PAGAR_SIMPLES: D-Simples a Recolher / C-Caixa Corrente
    Pagamento sai do Caixa Corrente (user deve resgatar CDB antes se necessário)
    """
    conta_passivo = _buscar_conta_por_codigo(db, "2.1.2.1")
    conta_caixa_corrente = _buscar_conta_por_codigo(db, "1.1.1.1")
    
    if not conta_passivo or not conta_caixa_corrente:
        raise ValueError("Contas 2.1.2.1 (Simples a Recolher) ou 1.1.1.1 (Caixa Corrente) não encontradas")
    
    # Validar saldo em Simples a Recolher
    saldo_passivo = crud_plano_contas.calcular_saldo_conta(db, conta_passivo.id)
    if saldo_passivo < valor:
        raise ValueError(
            f"📋 Obrigação insuficiente em Simples a Recolher.\n"
            f"Saldo da obrigação: R$ {saldo_passivo:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n\n"
            f"💡 Dica: Execute PROVISIONAR_SIMPLES antes de pagar o Simples Nacional."
        )
    
    # Validar saldo em Caixa Corrente
    saldo_caixa = crud_plano_contas.calcular_saldo_conta(db, conta_caixa_corrente.id)
    if saldo_caixa < valor:
        raise ValueError(
            f"💰 Saldo insuficiente em Caixa Corrente.\n"
            f"Saldo disponível: R$ {saldo_caixa:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n"
            f"Faltam: R$ {valor - saldo_caixa:.2f}\n\n"
            f"💡 Dica: Execute RESGATAR_CDB_OBRIGACOES_FISCAIS primeiro para ter saldo no caixa."
        )
    
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_passivo.id,
        conta_credito_id=conta_caixa_corrente.id,
        valor=valor,
        historico=historico or "Pagamento de Simples Nacional",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_pagar_pro_labore(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """PAGAR_PRO_LABORE: D-Pró-labore a Pagar / C-Caixa Corrente
    Pagamento sai do Caixa Corrente (user deve resgatar CDB antes se necessário)
    """
    conta_passivo = _buscar_conta_por_codigo(db, "2.1.3.1")
    conta_caixa_corrente = _buscar_conta_por_codigo(db, "1.1.1.1")
    
    if not conta_passivo or not conta_caixa_corrente:
        raise ValueError("Contas 2.1.3.1 (Pró-labore a Pagar) ou 1.1.1.1 (Caixa Corrente) não encontradas")
    
    # Validar saldo em Pró-labore a Pagar
    saldo_passivo = crud_plano_contas.calcular_saldo_conta(db, conta_passivo.id)
    if saldo_passivo < valor:
        raise ValueError(
            f"📋 Obrigação insuficiente em Pró-labore a Pagar.\n"
            f"Saldo da obrigação: R$ {saldo_passivo:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n\n"
            f"💡 Dica: Execute PRO_LABORE (provisão) antes de pagar o pró-labore."
        )
    
    # Validar saldo em Caixa Corrente
    saldo_caixa = crud_plano_contas.calcular_saldo_conta(db, conta_caixa_corrente.id)
    if saldo_caixa < valor:
        raise ValueError(
            f"💰 Saldo insuficiente em Caixa Corrente.\n"
            f"Saldo disponível: R$ {saldo_caixa:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n"
            f"Faltam: R$ {valor - saldo_caixa:.2f}\n\n"
            f"💡 Dica: Execute RESGATAR_CDB_LUCROS primeiro para ter saldo no caixa."
        )
    
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_passivo.id,
        conta_credito_id=conta_caixa_corrente.id,
        valor=valor,
        historico=historico or "Pagamento de pró-labore",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_resgatar_cdb_obrigacoes_fiscais(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """RESGATAR_CDB_OBRIGACOES_FISCAIS: D-Caixa Corrente / C-CDB - Obrigações Fiscais
    Resgatar CDB de obrigações fiscais para o caixa corrente antes de pagar INSS/Simples
    """
    conta_cdb = _buscar_conta_por_codigo(db, "1.1.1.2.1")
    conta_caixa_corrente = _buscar_conta_por_codigo(db, "1.1.1.1")
    
    if not conta_cdb or not conta_caixa_corrente:
        raise ValueError("Contas 1.1.1.2.1 (CDB - Obrigações Fiscais) ou 1.1.1.1 (Caixa Corrente) não encontradas")
    
    # Validar saldo no CDB
    saldo_cdb = crud_plano_contas.calcular_saldo_conta(db, conta_cdb.id)
    if saldo_cdb < valor:
        raise ValueError(
            f"💰 Saldo insuficiente em CDB - Obrigações Fiscais.\n"
            f"Saldo disponível: R$ {saldo_cdb:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n"
            f"Faltam: R$ {valor - saldo_cdb:.2f}\n\n"
            f"💡 Dica: Execute SEPARAR_OBRIGACOES_FISCAIS primeiro para ter saldo no CDB."
        )
    
    # Lançamento: D-Caixa Corrente / C-CDB
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_caixa_corrente.id,
        conta_credito_id=conta_cdb.id,
        valor=valor,
        historico=historico or "Resgate de CDB - Obrigações Fiscais",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_aplicar_lucros_cdb(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """APLICAR_LUCROS_CDB: D-CDB - Reserva de Lucros / C-Caixa Corrente
    Aplicar dinheiro destinado à distribuição de lucros em CDB
    """
    conta_cdb_lucros = _buscar_conta_por_codigo(db, "1.1.1.2.2")
    conta_caixa_corrente = _buscar_conta_por_codigo(db, "1.1.1.1")
    
    if not conta_cdb_lucros or not conta_caixa_corrente:
        raise ValueError("Contas 1.1.1.2.2 (CDB - Reserva de Lucros) ou 1.1.1.1 (Caixa Corrente) não encontradas")
    
    # Validar saldo em Caixa Corrente
    saldo_caixa = crud_plano_contas.calcular_saldo_conta(db, conta_caixa_corrente.id)
    if saldo_caixa < valor:
        raise ValueError(
            f"💰 Saldo insuficiente em Caixa Corrente para aplicar lucros em CDB.\n"
            f"Saldo disponível: R$ {saldo_caixa:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n"
            f"Faltam: R$ {valor - saldo_caixa:.2f}\n\n"
            f"💡 Dica: Execute APURAR_RESULTADO primeiro para ter lucros disponíveis."
        )
    
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_cdb_lucros.id,
        conta_credito_id=conta_caixa_corrente.id,
        valor=valor,
        historico=historico or "Aplicação de lucros em CDB - aguardando distribuição",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_resgatar_cdb_lucros(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """RESGATAR_CDB_LUCROS: D-Caixa Corrente / C-CDB - Reserva de Lucros
    Resgatar CDB de reserva de lucros para o caixa corrente antes de pagar pró-labore ou distribuir lucros.
    Esta operação unifica o resgate tanto para pró-labore quanto para lucros.
    """
    conta_cdb = _buscar_conta_por_codigo(db, "1.1.1.2.2")
    conta_caixa_corrente = _buscar_conta_por_codigo(db, "1.1.1.1")
    
    if not conta_cdb or not conta_caixa_corrente:
        raise ValueError("Contas 1.1.1.2.2 (CDB - Reserva de Lucros) ou 1.1.1.1 (Caixa Corrente) não encontradas")
    
    # Validar saldo no CDB
    saldo_cdb = crud_plano_contas.calcular_saldo_conta(db, conta_cdb.id)
    if saldo_cdb < valor:
        raise ValueError(
            f"💰 Saldo insuficiente em CDB - Reserva de Lucros.\n"
            f"Saldo disponível: R$ {saldo_cdb:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n"
            f"Faltam: R$ {valor - saldo_cdb:.2f}\n\n"
            f"💡 Dica: Execute SEPARAR_PRO_LABORE ou APLICAR_LUCROS_CDB primeiro para ter saldo no CDB."
        )
    
    # Lançamento: D-Caixa Corrente / C-CDB
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=conta_caixa_corrente.id,
        conta_credito_id=conta_cdb.id,
        valor=valor,
        historico=historico or "Resgate de CDB - Reserva de Lucros",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_adiantar_lucros(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str]):
    """ADIANTAR_LUCROS: Distribuir lucros antecipadamente usando reserva individual do sócio"""
    if not op.socio_id:
        raise ValueError("Operação ADIANTAR_LUCROS requer informar o sócio")
    
    # Buscar subconta de reserva do sócio (deve existir)
    subconta_reserva = crud_plano_contas._obter_subconta_reserva_socio(db, op.socio_id)
    if not subconta_reserva:
        raise ValueError(
            f"Reserva do sócio {op.socio.nome if op.socio else 'N/A'} não encontrada.\n"
            f"💡 Dica: Execute APLICAR_RESERVA_CDB primeiro para criar a reserva do sócio."
        )
    
    conta_caixa = _buscar_conta_por_codigo(db, "1.1.1.1")
    if not conta_caixa:
        raise ValueError("Conta 1.1.1.1 (Caixa Corrente) não encontrada")
    
    # Validar saldo na reserva do sócio
    saldo_reserva = crud_plano_contas.calcular_saldo_conta(db, subconta_reserva.id)
    if saldo_reserva < valor:
        raise ValueError(
            f"💰 Saldo insuficiente na reserva de {op.socio.nome if op.socio else 'N/A'}.\n"
            f"Saldo disponível: R$ {saldo_reserva:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n"
            f"Faltam: R$ {valor - saldo_reserva:.2f}\n\n"
            f"💡 Dica: Execute APLICAR_RESERVA_CDB para aumentar a reserva deste sócio."
        )
    
    # Validar saldo em caixa (precisa ter dinheiro físico para distribuir)
    saldo_caixa = crud_plano_contas.calcular_saldo_conta(db, conta_caixa.id)
    if saldo_caixa < valor:
        raise ValueError(
            f"💰 Saldo insuficiente em Caixa Corrente.\n"
            f"Saldo disponível: R$ {saldo_caixa:.2f}\n"
            f"Valor solicitado: R$ {valor:.2f}\n"
            f"Faltam: R$ {valor - saldo_caixa:.2f}\n\n"
            f"💡 Dica: Resgatar CDB ou receber honorários antes de adiantar lucros."
        )
    
    # Lançamento: D-Reserva do Sócio / C-Caixa Corrente
    lancamento = crud_plano_contas.criar_lancamento(
        db=db,
        data=data,
        conta_debito_id=subconta_reserva.id,
        conta_credito_id=conta_caixa.id,
        valor=valor,
        historico=historico or f"Adiantamento de lucros - {op.socio.nome if op.socio else 'N/A'}",
        automatico=True,
        editavel=True,
        criado_por=op.criado_por_id
    )
    lancamento.operacao_contabil_id = op.id
    lancamento.referencia_mes = op.mes_referencia


def _executar_reconhecer_rendimento_cdb(db: Session, op: models.OperacaoContabil, valor: float, data: date_type, historico: Optional[str], tipo_cdb: str):
    """RECONHECER_RENDIMENTO_CDB: Contabilizar juros/rendimentos de CDB
    
    Para RESERVA_LEGAL: distribui rendimentos proporcionalmente entre as subcontas dos sócios
    Para outros tipos: lança direto na conta pai
    
    Args:
        tipo_cdb: 'OBRIGACOES_FISCAIS', 'RESERVA_LUCROS', 'RESERVA_LEGAL'
    """
    # Mapear tipo de CDB para contas
    mapeamento = {
        'OBRIGACOES_FISCAIS': ('1.1.1.2.1', 'CDB - Obrigações Fiscais'),
        'RESERVA_LUCROS': ('1.1.1.2.2', 'CDB - Reserva de Lucros'),
        'RESERVA_LEGAL': ('1.1.1.2.3', 'CDB - Reserva Legal')
    }
    
    if tipo_cdb not in mapeamento:
        raise ValueError(f"Tipo de CDB inválido: {tipo_cdb}. Use: OBRIGACOES_FISCAIS, RESERVA_LUCROS ou RESERVA_LEGAL")
    
    codigo_cdb, nome_cdb = mapeamento[tipo_cdb]
    conta_receita = _buscar_conta_por_codigo(db, "4.2.1")
    
    if not conta_receita:
        raise ValueError("Conta 4.2.1 (Rendimento de CDB) não encontrada")
    
    # Se for RESERVA_LEGAL, distribuir proporcionalmente entre subcontas dos sócios
    if tipo_cdb == 'RESERVA_LEGAL':
        # Buscar todas as subcontas de CDB Reserva Legal (1.1.1.2.3.*)
        todas_contas = crud_plano_contas.listar_plano_contas(db, apenas_ativas=True)
        subcontas_cdb = [c for c in todas_contas if c.codigo.startswith("1.1.1.2.3.") and c.aceita_lancamento]
        
        if not subcontas_cdb:
            raise ValueError(
                "Nenhuma subconta de CDB Reserva Legal encontrada. "
                "Execute APLICAR_RESERVA_CDB primeiro para criar as subcontas dos sócios."
            )
        
        # Calcular saldo total e proporções
        saldos = {sc: crud_plano_contas.calcular_saldo_conta(db, sc.id) for sc in subcontas_cdb}
        saldo_total = sum(saldos.values())
        
        if saldo_total <= 0:
            raise ValueError(
                f"Saldo total em CDB Reserva Legal é zero ou negativo (R$ {saldo_total:.2f}). "
                "Não é possível distribuir rendimentos."
            )
        
        # Distribuir rendimento proporcionalmente
        for subconta, saldo in saldos.items():
            if saldo <= 0:
                continue
            
            proporcao = saldo / saldo_total
            valor_proporcional = valor * proporcao
            
            # Extrair socio_id do código da subconta (1.1.1.2.3.{socio_id})
            socio_id = int(subconta.codigo.split('.')[-1])
            socio = db.query(models.Socio).filter(models.Socio.id == socio_id).first()
            nome_socio = socio.nome if socio else f"ID {socio_id}"
            
            # Lançamento: D-CDB (subconta do sócio) / C-Receitas Financeiras
            lancamento = crud_plano_contas.criar_lancamento(
                db=db,
                data=data,
                conta_debito_id=subconta.id,
                conta_credito_id=conta_receita.id,
                valor=valor_proporcional,
                historico=historico or f"Rendimento CDB Reserva Legal - {nome_socio} ({proporcao*100:.2f}%)",
                automatico=True,
                editavel=True,
                criado_por=op.criado_por_id
            )
            lancamento.operacao_contabil_id = op.id
            lancamento.referencia_mes = op.mes_referencia
    
    else:
        # Para outros tipos de CDB, lançar direto na conta pai
        conta_cdb = _buscar_conta_por_codigo(db, codigo_cdb)
        if not conta_cdb:
            raise ValueError(f"Conta {codigo_cdb} ({nome_cdb}) não encontrada")
        
        # Lançamento: D-CDB / C-Receitas Financeiras
        lancamento = crud_plano_contas.criar_lancamento(
            db=db,
            data=data,
            conta_debito_id=conta_cdb.id,
            conta_credito_id=conta_receita.id,
            valor=valor,
            historico=historico or f"Rendimento de {nome_cdb}",
            automatico=True,
            editavel=True,
            criado_por=op.criado_por_id
        )
        lancamento.operacao_contabil_id = op.id
        lancamento.referencia_mes = op.mes_referencia


def listar_historico_operacoes(
    db: Session,
    mes_referencia: Optional[str] = None,
    operacao_codigo: Optional[str] = None,
    socio_id: Optional[int] = None,
    incluir_cancelados: bool = False,
    skip: int = 0,
    limit: int = 100
) -> List[models.OperacaoContabil]:
    """Lista histórico de operações contábeis executadas"""
    query = db.query(models.OperacaoContabil)
    
    if mes_referencia:
        query = query.filter(models.OperacaoContabil.mes_referencia == mes_referencia)
    
    if operacao_codigo:
        query = query.filter(models.OperacaoContabil.operacao_codigo == operacao_codigo)
    
    if socio_id:
        query = query.filter(models.OperacaoContabil.socio_id == socio_id)
    
    if not incluir_cancelados:
        query = query.filter(models.OperacaoContabil.cancelado == False)
    
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
    percentual_contrib_admin: float = 0.0,
    percentual_pl: float = 0.05,
    salario_minimo: float = 1518.0
) -> tuple:
    """
    Calcula pró-labore considerando a lógica:
    - Administrador recebe: 5% do LL total + (85% do LL × % contribuição nas entradas)
    - Pró-labore = MIN(Total a receber, salário mínimo)
    - O restante é distribuído como lucro
    
    Resolve a circularidade:
    - LL = LB - INSS Patronal
    - INSS Patronal = 20% do Pró-labore
    - Pró-labore depende do LL
    
    Args:
        db: Sessão do banco
        receita_bruta: Receita bruta do mês
        receita_12m: Receita acumulada 12 meses
        faixa_simples: Objeto SimplesFaixa com aliquota e deducao
        despesas_gerais: Despesas gerais do mês
        percentual_contrib_admin: % de contribuição do admin nas entradas do mês
        percentual_pl: Percentual fixo para administração (padrão 5%)
        salario_minimo: Limite do pró-labore (padrão R$ 1.518)
    
    Returns: 
        (pro_labore_bruto, inss_patronal, inss_pessoal, lucro_liquido)
    """
    # Validação: se receita ou lucro bruto for zero/negativo
    if receita_bruta <= 0:
        return (0.0, 0.0, 0.0, 0.0)
    
    # Calcular imposto Simples
    imposto_simples = receita_bruta * faixa_simples.aliquota - faixa_simples.deducao
    lucro_bruto = receita_bruta - imposto_simples - despesas_gerais
    
    # Se lucro bruto for zero ou negativo, não há pró-labore
    if lucro_bruto <= 0:
        return (0.0, 0.0, 0.0, lucro_bruto)
    
    # LÓGICA CORRETA:
    # Total a receber pelo admin = 5% do LL + (85% do LL × % contribuição)
    # Total_admin = 0.05 × LL + 0.85 × LL × (percentual_contrib_admin / 100)
    # Total_admin = LL × (0.05 + 0.85 × percentual_contrib_admin / 100)
    
    percentual_total_admin = percentual_pl + (0.85 * percentual_contrib_admin / 100.0)
    
    # Pró-labore = MIN(Total_admin, salário_mínimo)
    # LL = LB - INSS_Patronal
    # INSS_Patronal = 0.20 × Pró-labore
    #
    # Se Total_admin < salário_mínimo:
    #   PL = Total_admin = LL × percentual_total_admin
    #   LL = LB - (PL × 0.20)
    #   LL = LB - (LL × percentual_total_admin × 0.20)
    #   LL × (1 + percentual_total_admin × 0.20) = LB
    #   LL = LB / (1 + percentual_total_admin × 0.20)
    
    # Calcular primeiro assumindo que Total_admin < salário_mínimo
    lucro_liquido_temp = lucro_bruto / (1 + percentual_total_admin * 0.20)
    total_admin_temp = lucro_liquido_temp * percentual_total_admin
    
    if total_admin_temp <= salario_minimo:
        # Caso simples: todo o valor do admin vira pró-labore
        lucro_liquido_final = lucro_liquido_temp
        pro_labore_final = total_admin_temp
    else:
        # Caso complexo: pró-labore limitado ao salário mínimo
        # PL = salário_mínimo (fixo)
        # LL = LB - (salário_mínimo × 0.20)
        inss_patronal_fixo = salario_minimo * 0.20
        lucro_liquido_final = lucro_bruto - inss_patronal_fixo
        pro_labore_final = salario_minimo
    
    inss_patronal_final = pro_labore_final * 0.20
    inss_pessoal_final = pro_labore_final * 0.11
    
    return (
        round(pro_labore_final, 2),
        round(inss_patronal_final, 2),
        round(inss_pessoal_final, 2),
        round(lucro_liquido_final, 2)
    )


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
