from typing import Optional, Tuple
from datetime import date
from sqlalchemy.orm import Session
from database.models import SimplesFaixa


def calcular_faixa_simples(
    receita_12m: float,
    data_ref: date,
    db: Session
) -> Tuple[float, float, float, float]:
    """
    Calcula alíquota, dedução, alíquota efetiva e imposto do Simples Nacional.
    
    Args:
        receita_12m: Receita bruta acumulada nos últimos 12 meses
        data_ref: Data de referência para buscar faixas vigentes
        db: Sessão do banco de dados
    
    Returns:
        (aliquota, deducao, aliquota_efetiva, imposto)
        
    Raises:
        ValueError: Se receita exceder 4.800.000,00 (fora do Simples)
    """
    # Buscar faixas vigentes na data de referência, ordenadas por ordem
    faixas = db.query(SimplesFaixa).filter(
        SimplesFaixa.vigencia_inicio <= data_ref,
        (SimplesFaixa.vigencia_fim.is_(None)) | (SimplesFaixa.vigencia_fim >= data_ref)
    ).order_by(SimplesFaixa.ordem).all()
    
    if not faixas:
        raise ValueError("Nenhuma faixa do Simples Nacional configurada para a data de referência")
    
    # Verificar se excede o limite máximo (última faixa)
    limite_max = faixas[-1].limite_superior
    if receita_12m > limite_max:
        raise ValueError(
            f"Receita acumulada 12m (R$ {receita_12m:,.2f}) excede o limite "
            f"do Simples Nacional (R$ {limite_max:,.2f})"
        )
    
    # Encontrar faixa aplicável
    faixa_aplicavel = None
    for faixa in faixas:
        if receita_12m <= faixa.limite_superior:
            faixa_aplicavel = faixa
            break
    
    if not faixa_aplicavel:
        # Fallback: usar última faixa se não encontrar (não deve ocorrer)
        faixa_aplicavel = faixas[-1]
    
    aliquota = faixa_aplicavel.aliquota
    deducao = faixa_aplicavel.deducao
    
    # Alíquota efetiva = (Receita_12m × Alíquota - Dedução) / Receita_12m
    if receita_12m > 0:
        aliquota_efetiva = (receita_12m * aliquota - deducao) / receita_12m
    else:
        aliquota_efetiva = 0.0
    
    # Garantir que alíquota efetiva não seja negativa
    aliquota_efetiva = max(0.0, aliquota_efetiva)
    
    return aliquota, deducao, aliquota_efetiva


def calcular_imposto_simples(receita_bruta_mes: float, aliquota_efetiva: float) -> float:
    """
    Calcula o imposto do Simples Nacional do mês.
    
    Args:
        receita_bruta_mes: Receita bruta do mês atual
        aliquota_efetiva: Alíquota efetiva já calculada
    
    Returns:
        Valor do imposto a pagar no mês
    """
    return receita_bruta_mes * aliquota_efetiva


def inicializar_faixas_simples(db: Session, data_vigencia: date) -> None:
    """
    Inicializa as faixas do Simples Nacional com valores padrão (2025).
    Executar apenas uma vez ou ao mudar legislação.
    
    Args:
        db: Sessão do banco de dados
        data_vigencia: Data de início da vigência (ex: 2025-01-01)
    """
    # Verificar se já existem faixas vigentes
    faixas_existentes = db.query(SimplesFaixa).filter(
        SimplesFaixa.vigencia_inicio <= data_vigencia,
        (SimplesFaixa.vigencia_fim.is_(None)) | (SimplesFaixa.vigencia_fim >= data_vigencia)
    ).count()
    
    if faixas_existentes > 0:
        print(f"Faixas já existem para a data {data_vigencia}")
        return
    
    # Faixas do Simples Nacional (Anexo III - Serviços)
    faixas_padrao = [
        {"limite": 180000.00, "aliquota": 0.045, "deducao": 0.0, "ordem": 1},
        {"limite": 360000.00, "aliquota": 0.09, "deducao": 8100.0, "ordem": 2},
        {"limite": 720000.00, "aliquota": 0.102, "deducao": 12420.0, "ordem": 3},
        {"limite": 1800000.00, "aliquota": 0.14, "deducao": 39780.0, "ordem": 4},
        {"limite": 3600000.00, "aliquota": 0.22, "deducao": 183780.0, "ordem": 5},
        {"limite": 4800000.00, "aliquota": 0.33, "deducao": 828000.0, "ordem": 6},
    ]
    
    for faixa_data in faixas_padrao:
        faixa = SimplesFaixa(
            limite_superior=faixa_data["limite"],
            aliquota=faixa_data["aliquota"],
            deducao=faixa_data["deducao"],
            vigencia_inicio=data_vigencia,
            vigencia_fim=None,  # Vigente indefinidamente até nova regra
            ordem=faixa_data["ordem"]
        )
        db.add(faixa)
    
    db.commit()
    print(f"Faixas do Simples Nacional inicializadas com vigência a partir de {data_vigencia}")
