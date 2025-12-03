"""
Migration: Criar tabela ativos_imobilizados
Cria a tabela para gerenciamento de ativos imobilizados e cálculo de depreciação
"""
from database.database import engine, Base
from database import models


def run():
    """Cria tabela ativos_imobilizados"""
    try:
        # Criar apenas a tabela AtivoImobilizado
        models.AtivoImobilizado.__table__.create(bind=engine, checkfirst=True)
        print("✅ Tabela 'ativos_imobilizados' criada com sucesso")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        # Se a tabela já existir, não é um erro crítico
        if "already exists" in str(e).lower():
            print("⚠️  Tabela 'ativos_imobilizados' já existe")
        else:
            raise


if __name__ == "__main__":
    run()
