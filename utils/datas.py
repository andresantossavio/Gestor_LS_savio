from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from typing import List


def formato_mes(data: date) -> str:
    """Converte date para string YYYY-MM"""
    return data.strftime("%Y-%m")


def parse_mes(mes_str: str) -> date:
    """Converte string YYYY-MM para primeiro dia do mês"""
    return datetime.strptime(mes_str, "%Y-%m").date()


def mes_atual() -> str:
    """Retorna mês atual em formato YYYY-MM"""
    return formato_mes(datetime.now().date())


def meses_do_ano(ano: int) -> List[str]:
    """Gera lista de 12 meses do ano em formato YYYY-MM (jan a dez)"""
    return [f"{ano}-{m:02d}" for m in range(1, 13)]


def ultimos_12_meses(mes_referencia: str) -> List[str]:
    """
    Retorna lista dos últimos 12 meses (incluindo mês de referência).
    Ex: mes_referencia='2025-06' -> ['2024-07', '2024-08', ..., '2025-06']
    """
    data_ref = parse_mes(mes_referencia)
    meses = []
    for i in range(11, -1, -1):
        mes_data = data_ref - relativedelta(months=i)
        meses.append(formato_mes(mes_data))
    return meses


def inicio_do_mes(mes_str: str) -> date:
    """Retorna primeiro dia do mês YYYY-MM"""
    return parse_mes(mes_str)


def fim_do_mes(mes_str: str) -> date:
    """Retorna último dia do mês YYYY-MM"""
    primeiro_dia = parse_mes(mes_str)
    proximo_mes = primeiro_dia + relativedelta(months=1)
    ultimo_dia = proximo_mes - relativedelta(days=1)
    return ultimo_dia
