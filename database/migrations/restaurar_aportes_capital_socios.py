"""
Migration: Restaurar aportes de capital por sócio

Objetivo: Comparar o capital_social de cada sócio com os lançamentos
contábeis de aporte/retirada em 3.1 e criar lançamentos de ajuste para
recompor valores que foram apagados por engano em limpezas anteriores.

Regra:
- Para cada sócio, calcular:
    existente = (somatório de créditos em 3.1 com historico contendo o nome)
                - (somatório de débitos em 3.1 com historico contendo o nome)
    esperado = socio.capital_social (valor atual cadastrado no sócio)
    faltante = esperado - existente
- Se faltante > 0: criar um lançamento de aporte (D 1.1.1 / C 3.1)
  tipo_lancamento='aporte_capital', automatico=True, editavel=False
  historico inclui o nome do sócio e tag '[Restauração]'.
- Se faltante < 0: criar retirada (D 3.1 / C 1.1.1) no valor absoluto.

Notas:
- Usamos a data atual para os ajustes; referencia_mes fica nula.
- Esta migration é idempotente: se rodar novamente e nada faltar, não cria nada.
"""

from datetime import date
from typing import Tuple

from database.database import SessionLocal
from database.models import LancamentoContabil, PlanoDeContas, Socio


def _buscar_conta_por_codigo(db, codigo: str) -> PlanoDeContas:
    return db.query(PlanoDeContas).filter(PlanoDeContas.codigo == codigo).first()


def _sum_socio_capital_mov(db, socio_nome: str) -> Tuple[float, float]:
    # Soma créditos na 3.1 com historico contendo o nome
    conta_capital = _buscar_conta_por_codigo(db, "3.1")
    if not conta_capital:
        raise ValueError("Conta 3.1 (Capital Social) não encontrada")

    creditos = db.query(LancamentoContabil).filter(
        LancamentoContabil.conta_credito_id == conta_capital.id,
        LancamentoContabil.historico.ilike(f"%{socio_nome}%")
    ).all()
    debitos = db.query(LancamentoContabil).filter(
        LancamentoContabil.conta_debito_id == conta_capital.id,
        LancamentoContabil.historico.ilike(f"%{socio_nome}%")
    ).all()

    soma_creditos = sum(l.valor or 0 for l in creditos)
    soma_debitos = sum(l.valor or 0 for l in debitos)
    return soma_creditos, soma_debitos


def restaurar_aportes():
    db = SessionLocal()
    try:
        conta_capital = _buscar_conta_por_codigo(db, "3.1")
        conta_caixa = _buscar_conta_por_codigo(db, "1.1.1")
        if not conta_capital or not conta_caixa:
            raise ValueError("Contas essenciais (3.1, 1.1.1) não encontradas")

        socios = db.query(Socio).order_by(Socio.id).all()
        print(f"👥 Sócios encontrados: {len(socios)}")
        criados = 0

        for s in socios:
            esperado = float(s.capital_social or 0)
            soma_creditos, soma_debitos = _sum_socio_capital_mov(db, s.nome)
            existente = soma_creditos - soma_debitos
            faltante = round(esperado - existente, 2)

            print(f"- {s.nome}: esperado={esperado:.2f} existente={existente:.2f} faltante={faltante:.2f}")

            if abs(faltante) < 0.01:
                continue

            hist_base = f"[Restauração] Ajuste de capital - {s.nome}"
            if faltante > 0:
                # Criar aporte: D 1.1.1 / C 3.1
                lanc = LancamentoContabil(
                    data=date.today(),
                    conta_debito_id=conta_caixa.id,
                    conta_credito_id=conta_capital.id,
                    valor=faltante,
                    historico=f"{hist_base} - Aporte complementar",
                    automatico=True,
                    editavel=False,
                    tipo_lancamento='aporte_capital',
                    referencia_mes=None,
                )
            else:
                # Criar retirada: D 3.1 / C 1.1.1
                valor_abs = abs(faltante)
                lanc = LancamentoContabil(
                    data=date.today(),
                    conta_debito_id=conta_capital.id,
                    conta_credito_id=conta_caixa.id,
                    valor=valor_abs,
                    historico=f"{hist_base} - Retirada de ajuste",
                    automatico=True,
                    editavel=False,
                    tipo_lancamento='aporte_capital',
                    referencia_mes=None,
                )

            db.add(lanc)
            criados += 1

        db.commit()
        print(f"✅ Restauração concluída. Lançamentos criados: {criados}")
    except Exception as e:
        db.rollback()
        print(f"❌ Erro na restauração: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Iniciando restauração de aportes por sócio...")
    restaurar_aportes()
