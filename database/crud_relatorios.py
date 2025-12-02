from datetime import date, timedelta
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from . import models

# Helpers to sum by account code prefix

def _sum_credito_prefix(db: Session, prefix: str, d_ini: date, d_fim: date) -> float:
    return (
        db.query(func.coalesce(func.sum(models.LancamentoContabil.valor), 0.0))
        .filter(
            and_(
                models.LancamentoContabil.data >= d_ini,
                models.LancamentoContabil.data <= d_fim,
                models.LancamentoContabil.conta_credito.has(models.PlanoDeContas.codigo.like(f"{prefix}%")),
            )
        )
        .scalar()
        or 0.0
    )


def _sum_debito_prefix(db: Session, prefix: str, d_ini: date, d_fim: date) -> float:
    return (
        db.query(func.coalesce(func.sum(models.LancamentoContabil.valor), 0.0))
        .filter(
            and_(
                models.LancamentoContabil.data >= d_ini,
                models.LancamentoContabil.data <= d_fim,
                models.LancamentoContabil.conta_debito.has(models.PlanoDeContas.codigo.like(f"{prefix}%")),
            )
        )
        .scalar()
        or 0.0
    )


def _saldo_prefix_pl(db: Session, prefix: str, d_ini: date, d_fim: date) -> float:
    """Saldo para contas do Patrimônio Líquido (natureza tipicamente credora): crédito - débito."""
    cred = _sum_credito_prefix(db, prefix, d_ini, d_fim)
    deb = _sum_debito_prefix(db, prefix, d_ini, d_fim)
    return cred - deb


def montar_dmpl_periodo(db: Session, ano_inicio: int, ano_fim: int) -> dict:
    """Monta a DMPL para o período de anos informado (inclusive).

    Retorna estrutura compatível com frontend `DMPL.jsx`.
    """
    if ano_inicio > ano_fim:
        ano_inicio, ano_fim = ano_fim, ano_inicio

    ini_periodo = date(ano_inicio, 1, 1)
    fim_periodo = date(ano_fim, 12, 31)

    prev_ini = date(1900, 1, 1)
    prev_fim = ini_periodo - timedelta(days=1)

    # Saldos iniciais até 31/12 do ano anterior ao início do período
    si_capital = _saldo_prefix_pl(db, "3.1", prev_ini, prev_fim)
    si_reservas = _saldo_prefix_pl(db, "3.2", prev_ini, prev_fim)
    si_lpa = _saldo_prefix_pl(db, "3.3", prev_ini, prev_fim)

    # Movimentações no período
    mov_capital = _saldo_prefix_pl(db, "3.1", ini_periodo, fim_periodo)
    mov_reservas = _saldo_prefix_pl(db, "3.2", ini_periodo, fim_periodo)
    # Movimento do razão em 3.3 (normalmente registra destinações: reservas, distribuições)
    mov_lpa_ledger = _saldo_prefix_pl(db, "3.3", ini_periodo, fim_periodo)
    # Somar o lucro líquido apurado na DRE mensal do período para refletir o "resultado do exercício"
    lucro_liquido_periodo = (
        db.query(func.coalesce(func.sum(models.DREMensal.lucro_liquido), 0.0))
        .filter(models.DREMensal.mes >= f"{ano_inicio:04d}-01")
        .filter(models.DREMensal.mes <= f"{ano_fim:04d}-12")
        .scalar() or 0.0
    )
    mov_lpa = mov_lpa_ledger + lucro_liquido_periodo

    # Saldos finais
    sf_capital = si_capital + mov_capital
    sf_reservas = si_reservas + mov_reservas
    sf_lpa = si_lpa + mov_lpa

    saldo_inicial_total = si_capital + si_reservas + si_lpa
    total_mutacoes = mov_capital + mov_reservas + mov_lpa
    saldo_final_total = sf_capital + sf_reservas + sf_lpa

    variacao_percentual = 0.0
    if abs(saldo_inicial_total) > 1e-9:
        variacao_percentual = (saldo_final_total - saldo_inicial_total) / abs(saldo_inicial_total) * 100.0
    elif abs(saldo_final_total) > 1e-9:
        # Caso saldo inicial zero e houve formação de PL positivo
        variacao_percentual = 100.0

    return {
        "ano_inicio": ano_inicio,
        "ano_fim": ano_fim,
        "saldo_inicial": {
            "capital_social": si_capital,
            "reservas": si_reservas,
            "lucros_acumulados": si_lpa,
            "total": saldo_inicial_total,
        },
        "movimentacoes": [
            {
                "descricao": "Capital Social: aportes e reduções (líquido)",
                "capital_social": mov_capital,
                "reservas": 0.0,
                "lucros_acumulados": 0.0,
                "total": mov_capital,
            },
            {
                "descricao": "Reservas de lucros: constituições e utilizações (líquido)",
                "capital_social": 0.0,
                "reservas": mov_reservas,
                "lucros_acumulados": 0.0,
                "total": mov_reservas,
            },
            {
                "descricao": "Lucros/Prejuízos acumulados: resultado e distribuições (líquido)",
                "capital_social": 0.0,
                "reservas": 0.0,
                "lucros_acumulados": mov_lpa,
                "total": mov_lpa,
            },
        ],
        "saldo_final": {
            "capital_social": sf_capital,
            "reservas": sf_reservas,
            "lucros_acumulados": sf_lpa,
            "total": saldo_final_total,
        },
        "total_mutacoes": total_mutacoes,
        "variacao_percentual": variacao_percentual,
    }
