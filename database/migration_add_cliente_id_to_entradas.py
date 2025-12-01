"""
Migration script to add cliente_id column to entradas table
"""
from database.database import SessionLocal, engine
from sqlalchemy import text

def migrate():
    db = SessionLocal()
    try:
        # Check if column already exists
        result = db.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('entradas') 
            WHERE name='cliente_id'
        """))
        exists = result.scalar() > 0
        
        if not exists:
            print("Adding cliente_id column to entradas table...")
            db.execute(text("""
                ALTER TABLE entradas 
                ADD COLUMN cliente_id INTEGER
            """))
            db.commit()
            print("Column cliente_id added successfully!")
        else:
            print("Column cliente_id already exists. No migration needed.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
