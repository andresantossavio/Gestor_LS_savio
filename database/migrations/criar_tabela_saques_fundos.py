"""
Migration: Criar tabela saques_fundos
Cria a tabela para rastreamento de saques dos fundos de reserva e investimento
"""
from database.database import engine, Base
from database import models


def run():
    """Cria tabela saques_fundos"""
    try:
        # Criar apenas a tabela SaqueFundo
        models.SaqueFundo.__table__.create(bind=engine, checkfirst=True)
        print("✅ Tabela 'saques_fundos' criada com sucesso")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        # Se a tabela já existir, não é um erro crítico
        if "already exists" in str(e).lower():
            print("⚠️  Tabela 'saques_fundos' já existe")
        else:
            raise


if __name__ == "__main__":
    run()
