"""
Migration script to add usuario_id column to socios table
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
            WHERE name='usuario_id'
        """))
        exists = result.scalar() > 0
        
        if not exists:
            print("Adding usuario_id column to socios table...")
            db.execute(text("""
                ALTER TABLE socios 
                ADD COLUMN usuario_id INTEGER
            """))
            db.commit()
            print("Column usuario_id added successfully!")
        else:
            print("Column usuario_id already exists. No migration needed.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
