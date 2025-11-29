"""
Utilitários para cálculo de dias úteis considerando feriados.
"""
from datetime import date, timedelta
from typing import List
from sqlalchemy.orm import Session
from database.models import Feriado, Municipio


def eh_fim_de_semana(data: date) -> bool:
    """Verifica se a data é sábado (5) ou domingo (6)."""
    return data.weekday() in (5, 6)


def eh_feriado(data: date, municipio_id: int, db: Session) -> bool:
    """
    Verifica se a data é feriado considerando:
    - Feriados nacionais
    - Feriados estaduais (se município tiver UF)
    - Feriados municipais específicos
    """
    if not municipio_id:
        # Se não tem município, considera apenas feriados nacionais
        feriado = db.query(Feriado).filter(
            Feriado.data == data,
            Feriado.tipo == "nacional"
        ).first()
        return feriado is not None
    
    # Busca o município para obter a UF
    municipio = db.query(Municipio).filter(Municipio.id == municipio_id).first()
    if not municipio:
        return False
    
    # Busca feriados aplicáveis
    feriado = db.query(Feriado).filter(
        Feriado.data == data
    ).filter(
        (Feriado.tipo == "nacional") |
        ((Feriado.tipo == "estadual") & (Feriado.uf == municipio.uf)) |
        ((Feriado.tipo == "municipal") & (Feriado.municipio_id == municipio_id))
    ).first()
    
    return feriado is not None


def eh_dia_util(data: date, municipio_id: int, db: Session) -> bool:
    """
    Verifica se a data é um dia útil.
    Dia útil = não é fim de semana E não é feriado
    """
    return not eh_fim_de_semana(data) and not eh_feriado(data, municipio_id, db)


def proximo_dia_util(data: date, municipio_id: int, db: Session) -> date:
    """Retorna o próximo dia útil a partir da data fornecida."""
    data_atual = data
    while not eh_dia_util(data_atual, municipio_id, db):
        data_atual += timedelta(days=1)
    return data_atual


def adicionar_dias_uteis(data_base: date, dias: int, municipio_id: int, db: Session) -> date:
    """
    Adiciona N dias úteis a uma data base.
    
    Args:
        data_base: Data inicial
        dias: Número de dias úteis a adicionar
        municipio_id: ID do município para considerar feriados locais
        db: Sessão do banco de dados
    
    Returns:
        Data após adicionar os dias úteis
    """
    if dias <= 0:
        return data_base
    
    data_atual = data_base
    dias_adicionados = 0
    
    while dias_adicionados < dias:
        data_atual += timedelta(days=1)
        if eh_dia_util(data_atual, municipio_id, db):
            dias_adicionados += 1
    
    return data_atual


def subtrair_dias_uteis(data_base: date, dias: int, municipio_id: int, db: Session) -> date:
    """
    Subtrai N dias úteis de uma data base.
    
    Args:
        data_base: Data inicial
        dias: Número de dias úteis a subtrair
        municipio_id: ID do município para considerar feriados locais
        db: Sessão do banco de dados
    
    Returns:
        Data após subtrair os dias úteis
    """
    if dias <= 0:
        return data_base
    
    data_atual = data_base
    dias_subtraidos = 0
    
    while dias_subtraidos < dias:
        data_atual -= timedelta(days=1)
        if eh_dia_util(data_atual, municipio_id, db):
            dias_subtraidos += 1
    
    return data_atual


def calcular_dias_uteis(data_inicio: date, data_fim: date, municipio_id: int, db: Session) -> int:
    """
    Calcula o número de dias úteis entre duas datas (inclusive).
    
    Args:
        data_inicio: Data inicial
        data_fim: Data final
        municipio_id: ID do município para considerar feriados locais
        db: Sessão do banco de dados
    
    Returns:
        Número de dias úteis entre as datas
    """
    if data_fim < data_inicio:
        return 0
    
    dias_uteis = 0
    data_atual = data_inicio
    
    while data_atual <= data_fim:
        if eh_dia_util(data_atual, municipio_id, db):
            dias_uteis += 1
        data_atual += timedelta(days=1)
    
    return dias_uteis


def listar_feriados_periodo(
    data_inicio: date,
    data_fim: date,
    municipio_id: int,
    db: Session
) -> List[Feriado]:
    """
    Lista todos os feriados em um período considerando a localidade.
    
    Args:
        data_inicio: Data inicial do período
        data_fim: Data final do período
        municipio_id: ID do município (None para apenas nacionais)
        db: Sessão do banco de dados
    
    Returns:
        Lista de feriados no período
    """
    query = db.query(Feriado).filter(
        Feriado.data >= data_inicio,
        Feriado.data <= data_fim
    )
    
    if municipio_id:
        municipio = db.query(Municipio).filter(Municipio.id == municipio_id).first()
        if municipio:
            query = query.filter(
                (Feriado.tipo == "nacional") |
                ((Feriado.tipo == "estadual") & (Feriado.uf == municipio.uf)) |
                ((Feriado.tipo == "municipal") & (Feriado.municipio_id == municipio_id))
            )
    else:
        query = query.filter(Feriado.tipo == "nacional")
    
    return query.order_by(Feriado.data).all()


def validar_prazo_em_dia_util(data: date, municipio_id: int, db: Session) -> date:
    """
    Se a data cair em dia não útil, retorna o próximo dia útil.
    Útil para garantir que prazos não caiam em feriados/finais de semana.
    """
    if eh_dia_util(data, municipio_id, db):
        return data
    return proximo_dia_util(data, municipio_id, db)
