"""
Migration: Atualizar lançamentos contábeis dos meses de 2025
Gera lançamentos contábeis automáticos para todos os meses que têm entradas ou despesas
"""
from database.database import SessionLocal
from database.models import Entrada, Despesa
from database.crud_contabilidade import atualizar_lancamentos_mes
from datetime import datetime


def atualizar_lancamentos_meses_existentes():
    """
    Para cada mês que possui entradas ou despesas, chama atualizar_lancamentos_mes()
    para gerar os lançamentos contábeis automáticos.
    """
    db = SessionLocal()
    
    try:
        # Buscar todas as datas únicas de entradas e despesas
        entradas = db.query(Entrada).all()
        despesas = db.query(Despesa).all()
        
        meses_set = set()
        
        for entrada in entradas:
            mes = entrada.data.strftime('%Y-%m')
            meses_set.add(mes)
        
        for despesa in despesas:
            mes = despesa.data.strftime('%Y-%m')
            meses_set.add(mes)
        
        meses_ordenados = sorted(list(meses_set))
        
        print(f"🔄 Encontrados {len(meses_ordenados)} meses com movimentação")
        print(f"   Meses: {', '.join(meses_ordenados)}")
        print()
        
        for mes in meses_ordenados:
            print(f"📅 Processando mês {mes}...")
            try:
                resultado = atualizar_lancamentos_mes(db, mes)
                db.commit()
                
                print(f"   ✅ Lançamentos criados: {', '.join(resultado['lancamentos_criados'])}")
                print(f"   💰 Receita: R$ {resultado['receita_bruta']:.2f}")
                print(f"   💸 Despesas: R$ {resultado['despesas_gerais']:.2f}")
                print(f"   📊 Lucro Líquido: R$ {resultado['lucro_liquido']:.2f}")
                print()
            except Exception as e:
                db.rollback()
                print(f"   ❌ Erro ao processar mês {mes}: {e}")
                print()
        
        print(f"✅ Migration concluída! {len(meses_ordenados)} meses processados.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro durante migration: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Iniciando migration: atualizar_lancamentos_meses_existentes")
    print()
    atualizar_lancamentos_meses_existentes()
    print("✅ Migration finalizada")
