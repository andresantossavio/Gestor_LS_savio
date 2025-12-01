"""
Script de migração para adicionar as colunas 'pro_labore' e 'inss_pessoal' na tabela 'dre_mensal'
Execute este script para adicionar os novos campos de pró-labore e INSS pessoal
"""
import sqlite3
import os

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'gestor.db')

def add_prolabore_inss_columns():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verifica se as colunas já existem
        cursor.execute("PRAGMA table_info(dre_mensal)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'pro_labore' not in columns:
            print("Adicionando coluna 'pro_labore' na tabela 'dre_mensal'...")
            cursor.execute("ALTER TABLE dre_mensal ADD COLUMN pro_labore REAL DEFAULT 0.0")
            conn.commit()
            print("✓ Coluna 'pro_labore' adicionada com sucesso!")
        else:
            print("✓ Coluna 'pro_labore' já existe no banco de dados.")
        
        if 'inss_pessoal' not in columns:
            print("Adicionando coluna 'inss_pessoal' na tabela 'dre_mensal'...")
            cursor.execute("ALTER TABLE dre_mensal ADD COLUMN inss_pessoal REAL DEFAULT 0.0")
            conn.commit()
            print("✓ Coluna 'inss_pessoal' adicionada com sucesso!")
        else:
            print("✓ Coluna 'inss_pessoal' já existe no banco de dados.")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Erro ao adicionar colunas: {e}")

if __name__ == "__main__":
    add_prolabore_inss_columns()
