from datetime import date
from sqlalchemy import func

from database.database import SessionLocal
from database import models
from database.crud_plano_contas import buscar_conta_por_codigo


def run(cutoff_mes: str = None):
    """
    Backfill de lançamentos de pagamento de INSS (D 2.1.5 / C 1.1.1)
    com base nos registros consolidados da DREMensal, apenas para meses
    ANTERIORES ao cutoff_mes (YYYY-MM). Útil para limpar saldo acumulado
    em 2.1.5 de meses antigos já consolidados.

    Ex.: cutoff_mes='2025-11' irá gerar pagamentos até 2025-10 inclusive.
    """
    db = SessionLocal()
    try:
        conta_inss = buscar_conta_por_codigo(db, "2.1.5")
        conta_caixa = buscar_conta_por_codigo(db, "1.1.1")
        if not conta_inss or not conta_caixa:
            raise RuntimeError("Contas 2.1.5 (INSS) ou 1.1.1 (Caixa) não encontradas")

        q = db.query(models.DREMensal).filter(models.DREMensal.consolidado == True)
        if cutoff_mes:
            q = q.filter(models.DREMensal.mes < cutoff_mes)
        q = q.order_by(models.DREMensal.mes)

        criados = 0
        pulados = 0
        for dre in q.all():
            inss_total = float(dre.inss_patronal or 0) + float(dre.inss_pessoal or 0)
            if inss_total <= 0:
                pulados += 1
                continue

            # Já existe pagamento para este mês?
            existente = db.query(models.LancamentoContabil).filter(
                models.LancamentoContabil.tipo_lancamento == 'pagamento_inss',
                models.LancamentoContabil.referencia_mes == dre.mes,
            ).first()
            if existente:
                pulados += 1
                continue

            # Data = último dia do mês de referência
            ano = int(dre.mes.split('-')[0])
            mes = int(dre.mes.split('-')[1])
            import calendar
            dia = calendar.monthrange(ano, mes)[1]
            data_lcto = date(ano, mes, dia)

            lcto = models.LancamentoContabil(
                data=data_lcto,
                conta_debito_id=conta_inss.id,
                conta_credito_id=conta_caixa.id,
                valor=inss_total,
                historico=f"Pagamento INSS (backfill) - {dre.mes}",
                automatico=True,
                editavel=False,
                tipo_lancamento='pagamento_inss',
                referencia_mes=dre.mes
            )
            db.add(lcto)
            criados += 1

        db.commit()
        print(f"BACKFILL CONCLUÍDO — Criados: {criados}, Pulados: {pulados}")
    except Exception as e:
        db.rollback()
        print("ERRO NO BACKFILL:", str(e))
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Por padrão, não cria pagamento para o mês de novembro de 2025
    run(cutoff_mes='2025-11')
