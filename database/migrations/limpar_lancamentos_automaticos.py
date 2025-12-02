"""
Script para limpar lançamentos contábeis automáticos e pagamentos pendentes.
Mantém apenas lançamentos de capital.
"""

import sys
sys.path.insert(0, r'c:\PythonProjects\GESTOR_LS')

from database.database import SessionLocal
from database.models import LancamentoContabil, PagamentoPendente
from sqlalchemy import func

def limpar_lancamentos_automaticos():
    """Remove todos os lançamentos automáticos exceto os de capital."""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("LIMPEZA DE LANÇAMENTOS AUTOMÁTICOS E PAGAMENTOS PENDENTES")
        print("=" * 80)
        print()
        
        # 1. Contar lançamentos antes da limpeza
        total_lancamentos = db.query(func.count(LancamentoContabil.id)).scalar()
        print(f"Total de lançamentos contábeis: {total_lancamentos}")
        
        # Contar lançamentos automáticos
        lancamentos_automaticos = db.query(func.count(LancamentoContabil.id)).filter(
            LancamentoContabil.automatico == True
        ).scalar()
        print(f"Lançamentos automáticos: {lancamentos_automaticos}")
        
        # Contar lançamentos manuais (não automáticos)
        lancamentos_manuais = db.query(func.count(LancamentoContabil.id)).filter(
            LancamentoContabil.automatico == False
        ).scalar()
        print(f"Lançamentos manuais: {lancamentos_manuais}")
        
        # Contar lançamentos de capital (tipo_lancamento = 'capital')
        lancamentos_capital = db.query(func.count(LancamentoContabil.id)).filter(
            LancamentoContabil.tipo_lancamento == 'capital'
        ).scalar()
        print(f"Lançamentos de capital: {lancamentos_capital}")
        
        print()
        print("-" * 80)
        
        # 2. Contar pagamentos pendentes
        total_pagamentos = db.query(func.count(PagamentoPendente.id)).scalar()
        print(f"Total de pagamentos pendentes: {total_pagamentos}")
        
        print()
        print("=" * 80)
        print()
        
        # Confirmar ação
        resposta = input("Deseja excluir todos os lançamentos automáticos e pagamentos pendentes? (s/N): ")
        
        if resposta.lower() != 's':
            print("\nOperação cancelada.")
            return
        
        print()
        print("Iniciando limpeza...")
        print()
        
        # 3. Excluir pagamentos pendentes
        print("1. Excluindo pagamentos pendentes...")
        pagamentos_excluidos = db.query(PagamentoPendente).delete(synchronize_session=False)
        print(f"   ✓ {pagamentos_excluidos} pagamentos pendentes excluídos")
        
        # 4. Excluir lançamentos automáticos (exceto capital)
        print("2. Excluindo lançamentos automáticos (exceto capital)...")
        lancamentos_excluidos = db.query(LancamentoContabil).filter(
            LancamentoContabil.automatico == True,
            LancamentoContabil.tipo_lancamento != 'capital'
        ).delete(synchronize_session=False)
        print(f"   ✓ {lancamentos_excluidos} lançamentos automáticos excluídos")
        
        # 5. Excluir lançamentos de provisão
        print("3. Excluindo lançamentos de provisão...")
        provisoes_excluidas = db.query(LancamentoContabil).filter(
            LancamentoContabil.tipo_lancamento == 'provisao'
        ).delete(synchronize_session=False)
        print(f"   ✓ {provisoes_excluidas} lançamentos de provisão excluídos")
        
        # 6. Excluir lançamentos vinculados a entradas (exceto capital)
        print("4. Excluindo lançamentos vinculados a entradas...")
        entrada_lancamentos = db.query(LancamentoContabil).filter(
            LancamentoContabil.entrada_id != None,
            LancamentoContabil.tipo_lancamento != 'capital'
        ).delete(synchronize_session=False)
        print(f"   ✓ {entrada_lancamentos} lançamentos de entradas excluídos")
        
        # 7. Excluir lançamentos vinculados a despesas (exceto capital)
        print("5. Excluindo lançamentos vinculados a despesas...")
        despesa_lancamentos = db.query(LancamentoContabil).filter(
            LancamentoContabil.despesa_id != None,
            LancamentoContabil.tipo_lancamento != 'capital'
        ).delete(synchronize_session=False)
        print(f"   ✓ {despesa_lancamentos} lançamentos de despesas excluídos")
        
        # Commit das alterações
        db.commit()
        
        print()
        print("=" * 80)
        print("LIMPEZA CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        print()
        
        # Verificar lançamentos restantes
        lancamentos_restantes = db.query(func.count(LancamentoContabil.id)).scalar()
        lancamentos_capital_restantes = db.query(func.count(LancamentoContabil.id)).filter(
            LancamentoContabil.tipo_lancamento == 'capital'
        ).scalar()
        
        print(f"Lançamentos restantes: {lancamentos_restantes}")
        print(f"  - Lançamentos de capital: {lancamentos_capital_restantes}")
        print(f"  - Outros: {lancamentos_restantes - lancamentos_capital_restantes}")
        
        print()
        print("✓ Todos os lançamentos automáticos foram removidos")
        print("✓ Todos os pagamentos pendentes foram removidos")
        print("✓ Lançamentos de capital foram preservados")
        
    except Exception as e:
        db.rollback()
        print()
        print("=" * 80)
        print("ERRO durante a limpeza:")
        print("=" * 80)
        print(str(e))
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    limpar_lancamentos_automaticos()
