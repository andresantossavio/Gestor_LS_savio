"""Rebuild Lancamentos Contábeis a partir das Entradas existentes.

ATENÇÃO: Este script APAGA todos os lançamentos contábeis ligados a entradas
e todas as provisões de entrada, recriando-os de acordo com a lógica atual:
 - L1: Recebimento de honorários
 - L2: Provisão imposto (Simples)
 - (REMOVIDO) Pró-labore / INSS por entrada
 - L5: Fundo de reserva 10%
 - L6-N: Lucros distribuídos (exclui sócio administrador)

Pré-requisitos:
 - Lógica atualizada em `crud_plano_contas.lancar_entrada_honorarios`
 - Lógica atualizada em `crud_provisoes.calcular_e_provisionar_entrada`

Uso:
    python -m database.migrations.rebuild_lancamentos_from_entradas           # executa
    python -m database.migrations.rebuild_lancamentos_from_entradas --dry-run # mostra contagens sem alterar

Recomendações:
 - Faça backup do banco antes (dump ou cópia do arquivo SQLite se for o caso).
 - Execute em ambiente de desenvolvimento primeiro.
"""

import sys
from database.database import SessionLocal
from database import models
from database.crud_provisoes import calcular_e_provisionar_entrada
from database import crud_plano_contas


def main(dry_run: bool = False):
    db = SessionLocal()
    try:
        entradas = db.query(models.Entrada).all()
        total_entradas = len(entradas)

        lancamentos_q = db.query(models.LancamentoContabil).filter(models.LancamentoContabil.entrada_id.isnot(None))
        provisoes_q = db.query(models.ProvisaoEntrada)

        total_lancamentos = lancamentos_q.count()
        total_provisoes = provisoes_q.count()

        print(f"Entradas encontradas: {total_entradas}")
        print(f"Lancamentos ligados a entradas (serão removidos): {total_lancamentos}")
        print(f"Provisões de entrada (serão removidas): {total_provisoes}")

        if dry_run:
            print("Dry-run: nenhuma alteração realizada.")
            return

        # Remover lançamentos e provisões
        lancamentos_q.delete(synchronize_session=False)
        provisoes_q.delete(synchronize_session=False)
        db.commit()
        print("Remoção concluída. Recriando provisões e lançamentos...")

        recriados_provisoes = 0
        recriados_lancamentos = 0
        erros = 0

        for entrada in entradas:
            try:
                calcular_e_provisionar_entrada(db, entrada.id)
                recriados_provisoes += 1
                novos_lanc = crud_plano_contas.lancar_entrada_honorarios(db, entrada.id)
                recriados_lancamentos += len(novos_lanc)
            except Exception as e:
                erros += 1
                print(f"[ERRO] Entrada {entrada.id} - {e}")
                db.rollback()

        print("\nResumo:")
        print(f"Provisões recriadas: {recriados_provisoes}")
        print(f"Lancamentos recriados: {recriados_lancamentos}")
        print(f"Entradas com erro: {erros}")
        if erros == 0:
            print("Rebuild finalizado sem erros.")
        else:
            print("Rebuild concluído com alguns erros. Verifique os logs acima.")
    finally:
        db.close()


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    main(dry_run=dry)
