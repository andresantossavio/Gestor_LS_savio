#!/usr/bin/env python
"""
Script para adicionar operações faltantes ao banco de dados
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import Operacao

def adicionar_operacoes_faltantes():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("ADICIONANDO OPERAÇÕES FALTANTES")
        print("=" * 70)
        
        # Operações a adicionar
        operacoes_faltantes = [
            {
                "codigo": "ADIANTAR_LUCROS",
                "nome": "Adiantar Lucros ao Sócio",
                "descricao": "Distribuir lucros antecipadamente usando a reserva legal individual do sócio. Lançamento: D-Reserva Legal (CDB subconta sócio) / C-Caixa Corrente. Resgata CDB da reserva individual. Exige informar sócio.",
                "ativo": True,
                "ordem": 15
            },
            {
                "codigo": "RECONHECER_RENDIMENTO_CDB",
                "nome": "Reconhecer Rendimento de CDB",
                "descricao": "Contabilizar juros/rendimentos ganhos nas aplicações CDB. Usuário escolhe qual CDB teve rendimento. Lançamento: D-CDB [específico] / C-Receitas Financeiras. Aumenta saldo do CDB e reconhece receita.",
                "ativo": True,
                "ordem": 19
            }
        ]
        
        adicionadas = 0
        ja_existentes = 0
        
        for op_data in operacoes_faltantes:
            # Verificar se já existe
            existente = db.query(Operacao).filter(Operacao.codigo == op_data["codigo"]).first()
            
            if existente:
                print(f"   ⏭️  {op_data['codigo']}: Já existe")
                ja_existentes += 1
            else:
                # Adicionar
                nova_op = Operacao(**op_data)
                db.add(nova_op)
                print(f"   ✅ {op_data['codigo']}: Adicionada (ordem {op_data['ordem']})")
                adicionadas += 1
        
        db.commit()
        
        print("\n" + "=" * 70)
        print(f"✅ PROCESSO CONCLUÍDO")
        print(f"   Operações adicionadas: {adicionadas}")
        print(f"   Operações já existentes: {ja_existentes}")
        print("=" * 70)
        
        # Listar todas as operações
        print("\n📋 OPERAÇÕES CADASTRADAS (ordenadas):")
        todas = db.query(Operacao).order_by(Operacao.ordem, Operacao.codigo).all()
        for op in todas:
            status = "✓" if op.ativo else "✗"
            print(f"   {op.ordem:2}. [{status}] {op.codigo}: {op.nome}")
        
        print(f"\n   Total: {len(todas)} operações")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    adicionar_operacoes_faltantes()
