from datetime import date

from database.database import SessionLocal
from database import models
from database.crud_plano_contas import buscar_conta_por_codigo


def run(max_mes_inclusivo: str):
    """
    Cria lançamentos faltantes de INSS Pessoal (11%) com base na DRE consolidada.
    Para cada mês consolidado até `max_mes_inclusivo` (YYYY-MM), se houver
    inss_pessoal > 0 e não existir lançamento tipo 'inss_pessoal' para o mês,
    cria: D 3.4.1 / C 2.1.5 com data no último dia do mês e referencia_mes.
    """
    db = SessionLocal()
    try:
        conta_inss = buscar_conta_por_codigo(db, "2.1.5")
        conta_lucros = buscar_conta_por_codigo(db, "3.4.1")
        if not conta_inss or not conta_lucros:
            raise RuntimeError("Contas 2.1.5 (INSS) ou 3.4.1 (Lucros Distribuídos) não encontradas")

        q = db.query(models.DREMensal).filter(models.DREMensal.consolidado == True)
        if max_mes_inclusivo:
            q = q.filter(models.DREMensal.mes <= max_mes_inclusivo)
        q = q.order_by(models.DREMensal.mes)

        criados = 0
        pulados = 0
        for dre in q.all():
            valor = float(dre.inss_pessoal or 0)
            if valor <= 0:
                pulados += 1
                continue

            existente = db.query(models.LancamentoContabil).filter(
                models.LancamentoContabil.tipo_lancamento == 'inss_pessoal',
                models.LancamentoContabil.referencia_mes == dre.mes,
            ).first()
            if existente:
                pulados += 1
                continue

            ano = int(dre.mes.split('-')[0])
            mes = int(dre.mes.split('-')[1])
            import calendar
            dia = calendar.monthrange(ano, mes)[1]
            data_lcto = date(ano, mes, dia)

            lcto = models.LancamentoContabil(
                data=data_lcto,
                conta_debito_id=conta_lucros.id,
                conta_credito_id=conta_inss.id,
                valor=valor,
                historico=f"INSS Pessoal (11%) - Retenção - {dre.mes}",
                automatico=True,
                editavel=False,
                tipo_lancamento='inss_pessoal',
                referencia_mes=dre.mes
            )
            db.add(lcto)
            criados += 1

        db.commit()
        print(f"BACKFILL INSS PESSOAL CONCLUÍDO — Criados: {criados}, Pulados: {pulados}")
    except Exception as e:
        db.rollback()
        print("ERRO NO BACKFILL INSS PESSOAL:", str(e))
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run('2025-11')
