"""
Script para limpar pendências antigas (por entrada) e gerar novas consolidadas por mês
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database.database import SessionLocal
from database.models import PagamentoPendente, Entrada, LancamentoContabil
from database import crud_pagamentos_pendentes
from sqlalchemy import extract, and_


def main():
    db = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("LIMPEZA E REGENERAÇÃO DE PENDÊNCIAS CONSOLIDADAS POR MÊS")
        print("="*80)
        
        # 1. Listar pendências existentes
        pendencias_antigas = db.query(PagamentoPendente).all()
        print(f"\n📋 Pendências existentes: {len(pendencias_antigas)}")
        
        if len(pendencias_antigas) > 0:
            print("\n⚠️  Será necessário excluir as pendências antigas (geradas por entrada)")
            print("    e gerar novas pendências consolidadas por mês.")
            
            resposta = input("\n🤔 Deseja continuar? (s/n): ").strip().lower()
            if resposta != 's':
                print("\n❌ Operação cancelada pelo usuário.")
                return
            
            # 2. Excluir lançamentos contábeis associados às pendências
            print("\n🗑️  Excluindo lançamentos contábeis de provisão e pagamento...")
            for pend in pendencias_antigas:
                # Buscar lançamentos relacionados
                mes_ref = f"{pend.ano_ref}-{pend.mes_ref:02d}"
                lancamentos = db.query(LancamentoContabil).filter(
                    and_(
                        LancamentoContabil.referencia_mes == mes_ref,
                        LancamentoContabil.tipo_lancamento.in_(['provisao', 'pagamento_provisao'])
                    )
                ).all()
                
                for lanc in lancamentos:
                    db.delete(lanc)
            
            db.commit()
            print(f"   ✓ Lançamentos contábeis excluídos")
            
            # 3. Excluir pendências
            print("\n🗑️  Excluindo pendências antigas...")
            for pend in pendencias_antigas:
                db.delete(pend)
            
            db.commit()
            print(f"   ✓ {len(pendencias_antigas)} pendências excluídas")
        
        # 4. Identificar meses com entradas
        print("\n📊 Identificando meses com entradas...")
        meses_com_entradas = db.query(
            extract('month', Entrada.data).label('mes'),
            extract('year', Entrada.data).label('ano')
        ).distinct().order_by('ano', 'mes').all()
        
        print(f"   ✓ Encontrados {len(meses_com_entradas)} meses com entradas:")
        for mes, ano in meses_com_entradas:
            print(f"      - {int(mes):02d}/{int(ano)}")
        
        # 5. Gerar pendências consolidadas para cada mês
        print("\n💰 Gerando pendências consolidadas por mês...")
        total_pendencias = 0
        
        for mes, ano in meses_com_entradas:
            mes_int = int(mes)
            ano_int = int(ano)
            print(f"\n   📅 Processando {mes_int:02d}/{ano_int}...")
            
            try:
                pendencias = crud_pagamentos_pendentes.gerar_pendencias_mes(
                    db, mes_int, ano_int
                )
                print(f"      ✓ {len(pendencias)} pendências geradas")
                total_pendencias += len(pendencias)
                
                for p in pendencias:
                    print(f"         - {p.tipo}: R$ {p.valor:.2f}")
            except Exception as e:
                print(f"      ❌ Erro: {e}")
        
        print("\n" + "="*80)
        print("✅ OPERAÇÃO CONCLUÍDA")
        print(f"Total de pendências consolidadas geradas: {total_pendencias}")
        print("="*80 + "\n")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
