"""
Migração: Adiciona coluna municipio_id na tabela processos
Remove colunas antigas: uf, comarca
Converte processo existente para o novo formato
"""
import sqlite3
from database.database import SessionLocal
from database.models import Municipio

def migrar_processos():
    conn = sqlite3.connect('gestor_ls.db')
    cursor = conn.cursor()
    
    try:
        print("Iniciando migração da tabela processos...")
        
        # 1. Verificar se a coluna municipio_id já existe
        cursor.execute("PRAGMA table_info(processos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'municipio_id' in columns:
            print("✓ Coluna municipio_id já existe")
        else:
            # 2. Adicionar coluna municipio_id
            print("Adicionando coluna municipio_id...")
            cursor.execute("ALTER TABLE processos ADD COLUMN municipio_id INTEGER")
            conn.commit()
            print("✓ Coluna municipio_id adicionada")
        
        # 3. Buscar processo existente com comarca
        cursor.execute("SELECT id, uf, comarca FROM processos WHERE comarca IS NOT NULL")
        processo_antigo = cursor.fetchone()
        
        if processo_antigo:
            processo_id, uf, comarca = processo_antigo
            print(f"\nProcesso encontrado:")
            print(f"  ID: {processo_id}")
            print(f"  UF: {uf}")
            print(f"  Comarca: {comarca}")
            
            # 4. Tentar encontrar município correspondente
            db = SessionLocal()
            try:
                # Buscar por nome da comarca (remover "Comarca de" se existir)
                nome_comarca = comarca.replace("Comarca de ", "").strip()
                municipio = db.query(Municipio).filter(
                    Municipio.nome.like(f"%{nome_comarca}%")
                ).first()
                
                if not municipio and uf:
                    # Buscar pelo UF se não encontrou pelo nome
                    municipio = db.query(Municipio).filter(
                        Municipio.uf == uf
                    ).first()
                
                if municipio:
                    print(f"  Município encontrado: {municipio.nome}/{municipio.uf} (ID: {municipio.id})")
                    
                    # 5. Atualizar processo com municipio_id
                    cursor.execute(
                        "UPDATE processos SET municipio_id = ? WHERE id = ?",
                        (municipio.id, processo_id)
                    )
                    conn.commit()
                    print("✓ Processo atualizado com municipio_id")
                else:
                    print(f"⚠ Nenhum município encontrado para '{comarca}' / '{uf}'")
                    print("  O processo será mantido sem municipio_id")
            
            finally:
                db.close()
        else:
            print("\nNenhum processo com comarca encontrado")
        
        # 6. Verificar se há colunas antigas para remover
        # SQLite não suporta DROP COLUMN diretamente, então vamos deixar as colunas antigas
        # Elas serão ignoradas pelo modelo SQLAlchemy
        print("\n✓ Migração concluída!")
        print("Nota: As colunas 'uf' e 'comarca' antigas foram mantidas para compatibilidade")
        
        # 7. Mostrar estado final
        cursor.execute("SELECT id, numero, municipio_id FROM processos")
        processos = cursor.fetchall()
        print(f"\nProcessos na base:")
        for p in processos:
            print(f"  ID: {p[0]}, Número: {p[1]}, Município ID: {p[2]}")
    
    except Exception as e:
        print(f"✗ Erro na migração: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrar_processos()
