"""
Migration script to add saldo column to socios table
"""
from database.database import SessionLocal, engine
from sqlalchemy import text

def migrate():
    db = SessionLocal()
    try:
        # Check if column already exists
        result = db.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('socios') 
            WHERE name='saldo'
        """))
        exists = result.scalar() > 0
        
        if not exists:
            print("Adding saldo column to socios table...")
            db.execute(text("""
                ALTER TABLE socios 
                ADD COLUMN saldo REAL DEFAULT 0.0 NOT NULL
            """))
            db.commit()
            print("Column saldo added successfully!")
        else:
            print("Column saldo already exists. No migration needed.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
