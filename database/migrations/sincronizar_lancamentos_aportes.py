"""
Sincronizar lançamentos contábeis de aportes com os registros de AporteCapital

Objetivo: garantir que cada AporteCapital possua um lançamento contábil com:
- Data igual à data do aporte
- Contas corretas conforme o tipo do aporte
- Histórico padronizado contendo o nome do sócio
- Campos automatico=True, editavel=False, tipo_lancamento='aporte_capital'
- referencia_mes = YYYY-MM da data do aporte

Caso exista um lançamento semelhante (mesmo tipo 'aporte_capital', mesmo valor e histórico contendo
o nome do sócio) com data divergente, ele será ATUALIZADO (UPDATE) ao invés de recriado.

Data: 2025-12-02
"""

import sys
from datetime import date as date_type

sys.path.insert(0, '.')

from database.database import SessionLocal
from database import models
from database.crud_plano_contas import buscar_conta_por_codigo


def _historico_padronizado(aporte: models.AporteCapital) -> str:
    socio_nome = aporte.socio.nome if aporte.socio else "Sócio"
    if aporte.tipo_aporte == 'dinheiro':
        base = f"Aporte de capital em dinheiro - {socio_nome}"
    elif aporte.tipo_aporte == 'bens':
        base = f"Aporte de capital em bens - {socio_nome}"
    elif aporte.tipo_aporte == 'servicos':
        base = f"Aporte de capital em serviços - {socio_nome}"
    elif aporte.tipo_aporte == 'retirada':
        base = f"Retirada de capital - {socio_nome}"
    else:
        base = f"Aporte de capital - {socio_nome}"

    if getattr(aporte, 'descricao', None):
        base += f" - {aporte.descricao}"
    return base


def _contas_por_tipo(db, tipo: str):
    conta_capital = buscar_conta_por_codigo(db, "3.1")
    if not conta_capital:
        raise ValueError("Conta 3.1 (Capital Social) não encontrada")

    if tipo == 'dinheiro':
        conta_debito = buscar_conta_por_codigo(db, "1.1.1")
        conta_credito = conta_capital
    elif tipo == 'bens':
        conta_debito = buscar_conta_por_codigo(db, "1.2.1.1")
        conta_credito = conta_capital
    elif tipo == 'servicos':
        conta_debito = buscar_conta_por_codigo(db, "1.2.2.1")
        conta_credito = conta_capital
    elif tipo == 'retirada':
        conta_debito = conta_capital
        conta_credito = buscar_conta_por_codigo(db, "1.1.1")
    else:
        raise ValueError(f"Tipo de aporte inválido: {tipo}")

    if not conta_debito or not conta_credito:
        raise ValueError("Contas contábeis necessárias não encontradas para o tipo de aporte")

    return conta_debito, conta_credito


def sincronizar_lancamentos_aportes():
    db = SessionLocal()
    try:
        print("=" * 80)
        print("SINCRONIZAÇÃO: Aportes de Capital → Lançamentos Contábeis (UPDATE/UPSERT)")
        print("=" * 80)

        aportes = db.query(models.AporteCapital).order_by(models.AporteCapital.data).all()
        print(f"Aportes encontrados: {len(aportes)}")

        atualizados = 0
        criados = 0
        ignorados = 0
        erros = 0

        for aporte in aportes:
            try:
                # Determinar contas e histórico esperados
                conta_debito, conta_credito = _contas_por_tipo(db, aporte.tipo_aporte)
                historico_esperado = _historico_padronizado(aporte)
                socio_nome = aporte.socio.nome if aporte.socio else ""

                # Procurar lançamento existente do mesmo sócio/valor (mesmo tipo de operação)
                candidato = db.query(models.LancamentoContabil).filter(
                    models.LancamentoContabil.tipo_lancamento == 'aporte_capital',
                    models.LancamentoContabil.valor == aporte.valor,
                    models.LancamentoContabil.historico.like(f"%{socio_nome}%")
                ).order_by(models.LancamentoContabil.data.desc()).first()

                referencia_mes = aporte.data.strftime('%Y-%m') if isinstance(aporte.data, date_type) else None

                if candidato:
                    # Se já está igual, apenas ignorar
                    igual = (
                        candidato.data == aporte.data and
                        candidato.conta_debito_id == conta_debito.id and
                        candidato.conta_credito_id == conta_credito.id and
                        candidato.historico == historico_esperado and
                        getattr(candidato, 'referencia_mes', None) == referencia_mes
                    )

                    if igual:
                        ignorados += 1
                        print(f"  ⏭️  {socio_nome} {aporte.data} R$ {aporte.valor:.2f} - já sincronizado")
                    else:
                        # UPDATE in-place para bater com o aporte
                        candidato.data = aporte.data
                        candidato.conta_debito_id = conta_debito.id
                        candidato.conta_credito_id = conta_credito.id
                        candidato.historico = historico_esperado
                        candidato.automatico = True
                        candidato.editavel = False
                        candidato.tipo_lancamento = 'aporte_capital'
                        if hasattr(candidato, 'referencia_mes'):
                            candidato.referencia_mes = referencia_mes
                        atualizados += 1
                        print(f"  ✏️  ATUALIZADO: {socio_nome} → {aporte.data} R$ {aporte.valor:.2f}")
                else:
                    # Criar novo lançamento
                    lanc = models.LancamentoContabil(
                        data=aporte.data,
                        conta_debito_id=conta_debito.id,
                        conta_credito_id=conta_credito.id,
                        valor=aporte.valor,
                        historico=historico_esperado,
                        automatico=True,
                        editavel=False,
                        tipo_lancamento='aporte_capital',
                        referencia_mes=referencia_mes
                    )
                    db.add(lanc)
                    criados += 1
                    print(f"  ✅ CRIADO: {socio_nome} {aporte.data} R$ {aporte.valor:.2f}")

            except Exception as e:
                erros += 1
                print(f"  ❌ ERRO com aporte ID {aporte.id}: {e}")

        db.commit()

        print("\n" + "=" * 80)
        print("SINCRONIZAÇÃO CONCLUÍDA")
        print("=" * 80)
        print(f"Atualizados: {atualizados}")
        print(f"Criados:    {criados}")
        print(f"Ignorados:  {ignorados}")
        print(f"Erros:      {erros}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ ERRO FATAL: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    sincronizar_lancamentos_aportes()
