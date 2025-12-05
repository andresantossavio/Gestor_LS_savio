"""
Script de migração para adicionar colunas de prazos em tarefas.
"""
import sqlite3
import os

def migrar_prazos_tarefas():
    # Tentar localizar o banco de dados
    possible_paths = [
        '/app/gestor_ls.db',
        'gestor_ls.db',
        os.path.join(os.path.dirname(__file__), '..', 'gestor_ls.db'),
        os.path.join(os.path.dirname(__file__), 'gestor_ls.db'),
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        db_path = '/app/gestor_ls.db'  # Default
    
    print(f"Conectando ao banco de dados: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se as colunas já existem
        cursor.execute("PRAGMA table_info(tarefas)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Adicionar prazo_administrativo se não existir
        if 'prazo_administrativo' not in columns:
            print("Adicionando coluna prazo_administrativo...")
            cursor.execute("ALTER TABLE tarefas ADD COLUMN prazo_administrativo DATE")
            print("✓ Coluna prazo_administrativo adicionada")
        else:
            print("✓ Coluna prazo_administrativo já existe")
        
        # Adicionar prazo_fatal se não existir
        if 'prazo_fatal' not in columns:
            print("Adicionando coluna prazo_fatal...")
            cursor.execute("ALTER TABLE tarefas ADD COLUMN prazo_fatal DATE")
            print("✓ Coluna prazo_fatal adicionada")
        else:
            print("✓ Coluna prazo_fatal já existe")
        
        # Adicionar etapa_workflow_atual se não existir
        if 'etapa_workflow_atual' not in columns:
            print("Adicionando coluna etapa_workflow_atual...")
            cursor.execute("ALTER TABLE tarefas ADD COLUMN etapa_workflow_atual VARCHAR(50) DEFAULT 'analise_pendente'")
            print("✓ Coluna etapa_workflow_atual adicionada")
        else:
            print("✓ Coluna etapa_workflow_atual já existe")
        
        # Adicionar workflow_historico se não existir
        if 'workflow_historico' not in columns:
            print("Adicionando coluna workflow_historico...")
            cursor.execute("ALTER TABLE tarefas ADD COLUMN workflow_historico JSON")
            print("✓ Coluna workflow_historico adicionada")
        else:
            print("✓ Coluna workflow_historico já existe")
        
        # Adicionar conteudo_intimacao se não existir
        if 'conteudo_intimacao' not in columns:
            print("Adicionando coluna conteudo_intimacao...")
            cursor.execute("ALTER TABLE tarefas ADD COLUMN conteudo_intimacao TEXT")
            print("✓ Coluna conteudo_intimacao adicionada")
        else:
            print("✓ Coluna conteudo_intimacao já existe")
        
        # Adicionar classificacao_intimacao se não existir
        if 'classificacao_intimacao' not in columns:
            print("Adicionando coluna classificacao_intimacao...")
            cursor.execute("ALTER TABLE tarefas ADD COLUMN classificacao_intimacao VARCHAR(100)")
            print("✓ Coluna classificacao_intimacao adicionada")
        else:
            print("✓ Coluna classificacao_intimacao já existe")
        
        # Adicionar conteudo_decisao se não existir
        if 'conteudo_decisao' not in columns:
            print("Adicionando coluna conteudo_decisao...")
            cursor.execute("ALTER TABLE tarefas ADD COLUMN conteudo_decisao TEXT")
            print("✓ Coluna conteudo_decisao adicionada")
        else:
            print("✓ Coluna conteudo_decisao já existe")
        
        # Adicionar tarefa_origem_id se não existir
        if 'tarefa_origem_id' not in columns:
            print("Adicionando coluna tarefa_origem_id...")
            cursor.execute("ALTER TABLE tarefas ADD COLUMN tarefa_origem_id INTEGER REFERENCES tarefas(id)")
            print("✓ Coluna tarefa_origem_id adicionada")
        else:
            print("✓ Coluna tarefa_origem_id já existe")
        
        conn.commit()
        print("\n✓ Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"\n✗ Erro durante a migração: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrar_prazos_tarefas()
