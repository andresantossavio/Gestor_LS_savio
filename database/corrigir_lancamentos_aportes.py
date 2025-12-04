#!/usr/bin/env python
"""
Script de correção: Atualizar conta_debito dos lançamentos de aportes em bens
Corrige lançamentos existentes que foram para Caixa mas deveriam ir para Imobilizado
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database import models, crud_plano_contas

def corrigir_lancamentos_aportes():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("CORREÇÃO: Atualizar conta de débito de aportes em bens")
        print("=" * 70)
        
        # Buscar contas
        conta_caixa = crud_plano_contas.buscar_conta_por_codigo(db, "1.1.1.1")
        conta_imobilizado = crud_plano_contas.buscar_conta_por_codigo(db, "1.2.1.1")
        conta_intangivel = crud_plano_contas.buscar_conta_por_codigo(db, "1.2.2.1")
        conta_capital = crud_plano_contas.buscar_conta_por_codigo(db, "3.1")
        
        if not all([conta_caixa, conta_imobilizado, conta_intangivel, conta_capital]):
            print("❌ Alguma conta não encontrada!")
            return
        
        # Mapear tipo de aporte para conta
        mapeamento_contas = {
            'dinheiro': (conta_caixa, 'Caixa Corrente'),
            'bens': (conta_imobilizado, 'Equipamentos e Móveis'),
            'servicos': (conta_intangivel, 'Serviços Capitalizados')
        }
        
        # Buscar todos os aportes
        aportes = db.query(models.AporteCapital).filter(
            models.AporteCapital.tipo_aporte.in_(['dinheiro', 'bens', 'servicos'])
        ).all()
        
        print(f"\n📋 Total de aportes encontrados: {len(aportes)}")
        
        corrigidos = 0
        ja_corretos = 0
        nao_encontrados = 0
        
        for aporte in aportes:
            # Buscar lançamento associado
            lancamento = db.query(models.LancamentoContabil).filter(
                models.LancamentoContabil.historico.like(f"%Aporte de capital%{aporte.socio.nome}%"),
                models.LancamentoContabil.data == aporte.data,
                models.LancamentoContabil.valor == aporte.valor,
                models.LancamentoContabil.conta_credito_id == conta_capital.id
            ).first()
            
            if not lancamento:
                print(f"   ⚠️  ID {aporte.id}: R$ {aporte.valor:.2f} - {aporte.socio.nome} - {aporte.tipo_aporte} - LANÇAMENTO NÃO ENCONTRADO")
                nao_encontrados += 1
                continue
            
            # Determinar conta correta
            conta_correta, nome_conta = mapeamento_contas.get(aporte.tipo_aporte, (conta_caixa, 'Caixa Corrente'))
            
            # Verificar se já está correto
            if lancamento.conta_debito_id == conta_correta.id:
                print(f"   ✓  ID {aporte.id}: R$ {aporte.valor:.2f} - {aporte.socio.nome} - {aporte.tipo_aporte} → {nome_conta} (JÁ CORRETO)")
                ja_corretos += 1
                continue
            
            # Atualizar conta de débito
            conta_antiga = lancamento.conta_debito
            lancamento.conta_debito_id = conta_correta.id
            
            print(f"   🔄 ID {aporte.id}: R$ {aporte.valor:.2f} - {aporte.socio.nome} - {aporte.tipo_aporte}")
            print(f"      {conta_antiga.codigo} {conta_antiga.descricao} → {conta_correta.codigo} {nome_conta}")
            
            corrigidos += 1
        
        db.commit()
        
        print("\n" + "=" * 70)
        print(f"✅ CORREÇÃO CONCLUÍDA")
        print(f"   Lançamentos corrigidos: {corrigidos}")
        print(f"   Lançamentos já corretos: {ja_corretos}")
        print(f"   Lançamentos não encontrados: {nao_encontrados}")
        print("=" * 70)
        
        # Resumo por tipo
        print("\n📊 RESUMO FINAL POR TIPO:")
        for tipo, (conta, nome) in mapeamento_contas.items():
            aportes_tipo = [a for a in aportes if a.tipo_aporte == tipo]
            total = sum(a.valor for a in aportes_tipo)
            if aportes_tipo:
                print(f"   {tipo.upper()}: {len(aportes_tipo)} aporte(s) = R$ {total:.2f} → {nome} ({conta.codigo})")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    corrigir_lancamentos_aportes()
