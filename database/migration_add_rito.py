"""
Script de migração para adicionar a coluna 'rito' na tabela 'processos'
Execute este script caso a coluna não seja criada automaticamente
"""
import sqlite3
import os

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'gestor.db')

def add_rito_column():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verifica se a coluna já existe
        cursor.execute("PRAGMA table_info(processos)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'rito' not in columns:
            print("Adicionando coluna 'rito' na tabela 'processos'...")
            cursor.execute("ALTER TABLE processos ADD COLUMN rito TEXT")
            conn.commit()
            print("✓ Coluna 'rito' adicionada com sucesso!")
        else:
            print("✓ Coluna 'rito' já existe no banco de dados.")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Erro ao adicionar coluna: {e}")

if __name__ == "__main__":
    add_rito_column()
