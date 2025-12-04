#!/usr/bin/env python
"""
Script de migração: Criar lançamentos contábeis para aportes de capital existentes
Diferencia aportes em dinheiro (caixa), bens (imobilizado) e serviços (intangível)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database import models, crud_plano_contas

def migrar_aportes():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("MIGRAÇÃO: Criar lançamentos contábeis para aportes de capital")
        print("=" * 70)
        
        # Buscar todos os aportes
        aportes = db.query(models.AporteCapital).filter(
            models.AporteCapital.tipo_aporte.in_(['dinheiro', 'bens', 'servicos'])
        ).all()
        
        print(f"\n📋 Total de aportes encontrados: {len(aportes)}")
        
        # Mapear tipo de aporte para conta de débito
        mapeamento_contas = {
            'dinheiro': ('1.1.1.1', 'Caixa Corrente'),
            'bens': ('1.2.1.1', 'Equipamentos e Móveis'),
            'servicos': ('1.2.2.1', 'Serviços Capitalizados')
        }
        
        # Buscar conta de Capital Social
        conta_capital = crud_plano_contas.buscar_conta_por_codigo(db, "3.1")
        if not conta_capital:
            print("❌ Conta 3.1 (Capital Social) não encontrada!")
            return
        
        lancamentos_criados = 0
        lancamentos_existentes = 0
        
        for aporte in aportes:
            # Determinar conta de débito baseada no tipo
            codigo_debito, nome_debito = mapeamento_contas.get(aporte.tipo_aporte, ('1.1.1.1', 'Caixa Corrente'))
            
            # Verificar se já existe lançamento
            lancamento_existente = db.query(models.LancamentoContabil).filter(
                models.LancamentoContabil.historico.like(f"%Aporte de capital%{aporte.socio.nome}%"),
                models.LancamentoContabil.data == aporte.data,
                models.LancamentoContabil.valor == aporte.valor
            ).first()
            
            if lancamento_existente:
                print(f"   ⏭️  ID {aporte.id}: R$ {aporte.valor:.2f} - {aporte.socio.nome} - {aporte.tipo_aporte} - JÁ POSSUI LANÇAMENTO")
                lancamentos_existentes += 1
                continue
            
            # Buscar conta de débito
            conta_debito = crud_plano_contas.buscar_conta_por_codigo(db, codigo_debito)
            if not conta_debito:
                print(f"   ❌ Conta {codigo_debito} ({nome_debito}) não encontrada!")
                continue
            
            # Criar lançamento contábil
            historico = f"Aporte de capital - {aporte.socio.nome} - {aporte.tipo_aporte}"
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
            
            print(f"   ✅ ID {aporte.id}: R$ {aporte.valor:.2f} - {aporte.socio.nome} - {aporte.tipo_aporte} → {nome_debito}")
            lancamentos_criados += 1
        
        db.commit()
        
        print("\n" + "=" * 70)
        print(f"✅ MIGRAÇÃO CONCLUÍDA")
        print(f"   Lançamentos criados: {lancamentos_criados}")
        print(f"   Lançamentos já existentes: {lancamentos_existentes}")
        print("=" * 70)
        
        # Mostrar resumo por tipo
        print("\n📊 RESUMO POR TIPO DE APORTE:")
        for tipo, (codigo, nome) in mapeamento_contas.items():
            aportes_tipo = [a for a in aportes if a.tipo_aporte == tipo]
            total = sum(a.valor for a in aportes_tipo)
            if aportes_tipo:
                print(f"   {tipo.upper()}: {len(aportes_tipo)} aporte(s) = R$ {total:.2f} → {nome} ({codigo})")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    migrar_aportes()
