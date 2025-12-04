#!/usr/bin/env python
"""
Script para verificar e corrigir lançamentos de aportes de capital
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database import models
from database import crud_plano_contas

def verificar_e_corrigir_aportes():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("VERIFICAÇÃO: Aportes de Capital e Lançamentos Contábeis")
        print("=" * 70)
        
        # Buscar todos os aportes
        aportes = db.query(models.AporteCapital).order_by(models.AporteCapital.data).all()
        
        print(f"\n📋 Total de aportes cadastrados: {len(aportes)}")
        print(f"\n{'ID':<5} {'Data':<12} {'Sócio':<25} {'Valor':<12} {'Tipo':<12} {'Descrição':<30}")
        print("-" * 110)
        
        total_dinheiro = 0
        total_bens = 0
        aportes_sem_lancamento = []
        
        for aporte in aportes:
            socio_nome = aporte.socio.nome if aporte.socio else "N/A"
            print(f"{aporte.id:<5} {str(aporte.data):<12} {socio_nome:<25} R$ {aporte.valor:<9.2f} {aporte.tipo_aporte:<12} {aporte.descricao or '':<30}")
            
            if aporte.tipo_aporte == 'dinheiro':
                total_dinheiro += aporte.valor
            elif aporte.tipo_aporte == 'bens':
                total_bens += aporte.valor
            
            # Verificar se existe lançamento contábil
            if aporte.tipo_aporte in ['dinheiro', 'bens', 'servicos']:
                lancamento = db.query(models.LancamentoContabil).filter(
                    models.LancamentoContabil.historico.like(f"%Aporte de capital%{socio_nome}%"),
                    models.LancamentoContabil.data == aporte.data,
                    models.LancamentoContabil.valor == aporte.valor
                ).first()
                
                if not lancamento:
                    aportes_sem_lancamento.append(aporte)
        
        print("-" * 110)
        print(f"\n💰 Total em dinheiro: R$ {total_dinheiro:.2f}")
        print(f"🏢 Total em bens: R$ {total_bens:.2f}")
        print(f"📊 Total geral: R$ {total_dinheiro + total_bens:.2f}")
        
        # Verificar Capital Social
        conta_capital = crud_plano_contas.buscar_conta_por_codigo(db, "3.1")
        if conta_capital:
            saldo_capital = crud_plano_contas.calcular_saldo_conta(db, conta_capital.id)
            print(f"\n✅ Saldo em Capital Social (3.1): R$ {saldo_capital:.2f}")
        
        # Verificar Caixa Corrente
        conta_caixa = crud_plano_contas.buscar_conta_por_codigo(db, "1.1.1.1")
        if conta_caixa:
            saldo_caixa = crud_plano_contas.calcular_saldo_conta(db, conta_caixa.id)
            print(f"💵 Saldo em Caixa Corrente (1.1.1.1): R$ {saldo_caixa:.2f}")
        
        # Aportes sem lançamento
        if aportes_sem_lancamento:
            print(f"\n⚠️  ATENÇÃO: {len(aportes_sem_lancamento)} aportes SEM lançamento contábil!")
            print("\nAportes sem lançamento:")
            for aporte in aportes_sem_lancamento:
                socio_nome = aporte.socio.nome if aporte.socio else "N/A"
                print(f"   ID {aporte.id}: {aporte.data} - {socio_nome} - R$ {aporte.valor:.2f} - {aporte.tipo_aporte}")
            
            resposta = input("\n❓ Deseja criar os lançamentos faltantes? (s/N): ")
            if resposta.lower() == 's':
                print("\n🔄 Criando lançamentos contábeis...")
                
                conta_caixa = crud_plano_contas.buscar_conta_por_codigo(db, "1.1.1.1")
                conta_capital = crud_plano_contas.buscar_conta_por_codigo(db, "3.1")
                
                if not conta_caixa or not conta_capital:
                    print("❌ Erro: Contas contábeis não encontradas!")
                    return
                
                for aporte in aportes_sem_lancamento:
                    socio_nome = aporte.socio.nome if aporte.socio else "N/A"
                    historico = f"Aporte de capital - {socio_nome} - {aporte.tipo_aporte}"
                    if aporte.descricao:
                        historico += f" - {aporte.descricao}"
                    
                    crud_plano_contas.criar_lancamento(
                        db=db,
                        data=aporte.data,
                        conta_debito_id=conta_caixa.id,
                        conta_credito_id=conta_capital.id,
                        valor=aporte.valor,
                        historico=historico,
                        automatico=True,
                        editavel=False,
                        criado_por=None
                    )
                    print(f"   ✅ Criado lançamento para aporte ID {aporte.id}")
                
                db.commit()
                print("\n✅ Lançamentos criados com sucesso!")
                
                # Verificar novos saldos
                saldo_capital = crud_plano_contas.calcular_saldo_conta(db, conta_capital.id)
                saldo_caixa = crud_plano_contas.calcular_saldo_conta(db, conta_caixa.id)
                
                print(f"\n📊 Saldos atualizados:")
                print(f"   Capital Social (3.1): R$ {saldo_capital:.2f}")
                print(f"   Caixa Corrente (1.1.1.1): R$ {saldo_caixa:.2f}")
        else:
            print("\n✅ Todos os aportes possuem lançamentos contábeis!")
        
        print("\n" + "=" * 70)
        print("VERIFICAÇÃO CONCLUÍDA")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    verificar_e_corrigir_aportes()
