"""
Migration: Criar contas de depreciação
- 5.2.9: Despesa de Depreciação (Devedora)
- 1.2.9: Depreciação Acumulada (-) (Credora - conta redutora do ativo)
"""
from database.database import SessionLocal
from database.models import PlanoDeContas


def run():
    """Cria contas 5.2.9 e 1.2.9 para depreciação"""
    db = SessionLocal()
    
    try:
        # ===== CONTA 5.2.9 (Despesa de Depreciação) =====
        conta_5_2_9_existente = db.query(PlanoDeContas).filter_by(codigo="5.2.9").first()
        if conta_5_2_9_existente:
            print("⚠️  Conta 5.2.9 já existe")
        else:
            # Buscar conta pai 5.2 (Despesas Operacionais)
            conta_5_2 = db.query(PlanoDeContas).filter_by(codigo="5.2").first()
            if not conta_5_2:
                raise ValueError("Conta pai 5.2 não encontrada")
            
            # Criar conta 5.2.9 (Despesa de Depreciação)
            conta_5_2_9 = PlanoDeContas(
                codigo="5.2.9",
                descricao="Despesa de Depreciação",
                tipo="despesa",
                natureza="Devedora",
                nivel=3,
                aceita_lancamento=True,
                pai_id=conta_5_2.id,
                ativo=True
            )
            db.add(conta_5_2_9)
            db.commit()
            print("✅ Conta 5.2.9 (Despesa de Depreciação) criada com sucesso")
        
        # ===== CONTA 1.2.9 (Depreciação Acumulada) =====
        conta_1_2_9_existente = db.query(PlanoDeContas).filter_by(codigo="1.2.9").first()
        if conta_1_2_9_existente:
            print("⚠️  Conta 1.2.9 já existe")
        else:
            # Buscar conta pai 1.2 (Ativo Não Circulante)
            conta_1_2 = db.query(PlanoDeContas).filter_by(codigo="1.2").first()
            if not conta_1_2:
                raise ValueError("Conta pai 1.2 não encontrada")
            
            # Criar conta 1.2.9 (Depreciação Acumulada - conta redutora)
            conta_1_2_9 = PlanoDeContas(
                codigo="1.2.9",
                descricao="Depreciação Acumulada (-)",
                tipo="ativo",
                natureza="Credora",  # Credora porque reduz o ativo
                nivel=3,
                aceita_lancamento=True,
                pai_id=conta_1_2.id,
                ativo=True
            )
            db.add(conta_1_2_9)
            db.commit()
            print("✅ Conta 1.2.9 (Depreciação Acumulada) criada com sucesso")
        
        print("\n✅ Migration de contas de depreciação concluída")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar contas: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
