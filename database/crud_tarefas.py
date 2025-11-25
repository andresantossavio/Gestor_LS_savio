from database.database import SessionLocal
from database.models import Tarefa
from sqlalchemy.orm import Session
from datetime import datetime, date

def criar_tarefa(titulo: str, descricao: str = None, prazo: date = None,
                 responsavel_id: int = None, processo_id: int = None, status: str = "pendente", db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        t = Tarefa(
            titulo=titulo,
            descricao=descricao,
            prazo=prazo,
            responsavel_id=responsavel_id,
            processo_id=processo_id,
            status=status,
            criado_em=datetime.utcnow(),
            atualizado_em=datetime.utcnow()
        )
        db.add(t)
        db.commit()
        db.refresh(t)
        return t
    finally:
        if created_local_db:
            db.close()

def listar_tarefas_do_processo(processo_id: int, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        return db.query(Tarefa).filter(Tarefa.processo_id == processo_id).order_by(Tarefa.prazo).all()
    finally:
        if created_local_db:
            db.close()

def listar_tarefas_gerais(db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        return db.query(Tarefa).filter(Tarefa.processo_id == None).order_by(Tarefa.prazo).all()
    finally:
        if created_local_db:
            db.close()

def listar_tarefas_por_responsavel(responsavel_id: int, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        return db.query(Tarefa).filter(Tarefa.responsavel_id == responsavel_id).order_by(Tarefa.prazo).all()
    finally:
        if created_local_db:
            db.close()

def buscar_tarefa(id: int, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        return db.query(Tarefa).filter(Tarefa.id == id).first()
    finally:
        if created_local_db:
            db.close()

def atualizar_tarefa(id: int, db: Session | None = None, **kwargs):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        t = db.query(Tarefa).filter(Tarefa.id == id).first()
        if not t:
            return None
        for k, v in kwargs.items():
            if hasattr(t, k):
                setattr(t, k, v)
        t.atualizado_em = datetime.utcnow()
        db.commit()
        db.refresh(t)
        return t
    finally:
        if created_local_db:
            db.close()

def deletar_tarefa(id: int, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        t = db.query(Tarefa).filter(Tarefa.id == id).first()
        if not t:
            return False
        db.delete(t)
        db.commit()
        return True
    finally:
        if created_local_db:
            db.close()

def listar_tarefas_por_prazo(inicio, fim, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        return db.query(Tarefa).filter(Tarefa.prazo >= inicio, Tarefa.prazo <= fim).all()
    finally:
        if created_local_db:
            db.close()
