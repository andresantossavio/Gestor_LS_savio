"""
Script de inicialização das faixas do Simples Nacional.
Executa uma vez para popular o banco com as faixas padrão vigentes a partir de 2025-01-01.
"""

from datetime import date
from database.database import SessionLocal
from utils.simples import inicializar_faixas_simples

def main():
    db = SessionLocal()
    try:
        print("Inicializando faixas do Simples Nacional...")
        data_vigencia = date(2025, 1, 1)
        inicializar_faixas_simples(db, data_vigencia)
        print("Faixas inicializadas com sucesso!")
    except Exception as e:
        print(f"Erro ao inicializar faixas: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
