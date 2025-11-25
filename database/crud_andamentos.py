from database.database import SessionLocal
from database.models import Andamento
from sqlalchemy.orm import Session
from datetime import datetime

def criar_andamento(processo_id: int, descricao: str, tipo: str = None, criado_por: int = None, data=None, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        a = Andamento(
            processo_id=processo_id,
            descricao=descricao,
            tipo=tipo,
            criado_por=criado_por,
            data=data or datetime.utcnow().date(),
            criado_em=datetime.utcnow()
        )
        db.add(a)
        db.commit()
        db.refresh(a)
        return a
    finally:
        if created_local_db:
            db.close()

def listar_andamentos_do_processo(processo_id: int, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        return db.query(Andamento).filter(Andamento.processo_id == processo_id).order_by(Andamento.data).all()
    finally:
        if created_local_db:
            db.close()

def buscar_andamento(id: int, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        return db.query(Andamento).filter(Andamento.id == id).first()
    finally:
        if created_local_db:
            db.close()

def atualizar_andamento(id: int, db: Session | None = None, **kwargs):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        a = db.query(Andamento).filter(Andamento.id == id).first()
        if not a:
            return None
        for k, v in kwargs.items():
            if hasattr(a, k):
                setattr(a, k, v)
        a.criado_em = a.criado_em  # keep
        db.commit()
        db.refresh(a)
        return a
    finally:
        if created_local_db:
            db.close()

def deletar_andamento(id: int, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        a = db.query(Andamento).filter(Andamento.id == id).first()
        if not a:
            return False
        db.delete(a)
        db.commit()
        return True
    finally:
        if created_local_db:
            db.close()
