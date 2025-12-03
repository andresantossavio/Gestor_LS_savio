"""
Migration: Adicionar conta 2.1.4 (Simples a Pagar)
Cria conta de passivo para provisão do Simples Nacional
"""
from database.database import SessionLocal
from database.models import PlanoDeContas


def run():
    """Adiciona conta 2.1.4 (Simples a Pagar)"""
    db = SessionLocal()
    
    try:
        # Verificar se já existe
        conta_existente = db.query(PlanoDeContas).filter_by(codigo="2.1.4").first()
        if conta_existente:
            print("⚠️  Conta 2.1.4 já existe")
            return
        
        # Buscar conta pai 2.1 (Passivo Circulante)
        conta_2_1 = db.query(PlanoDeContas).filter_by(codigo="2.1").first()
        if not conta_2_1:
            raise ValueError("Conta pai 2.1 não encontrada")
        
        # Criar conta 2.1.4 (Simples a Pagar)
        conta_2_1_4 = PlanoDeContas(
            codigo="2.1.4",
            descricao="Simples Nacional a Recolher",
            tipo="Passivo",
            natureza="Credora",
            nivel=3,
            aceita_lancamento=True,
            pai_id=conta_2_1.id,
            ativo=True
        )
        db.add(conta_2_1_4)
        db.commit()
        
        print("✅ Conta 2.1.4 (Simples Nacional a Recolher) criada com sucesso")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar conta: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
