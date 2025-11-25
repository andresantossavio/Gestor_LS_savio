from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Processo

def criar_processo(
    numero,
    autor,
    reu,
    fase,
    uf,
    comarca,
    vara,
    status,
    observacoes,
    data_abertura,
    data_fechamento,
    cliente_id,
    db: Session | None = None
):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        novo = Processo(
            numero=numero,
            autor=autor,
            reu=reu,
            fase=fase,
            uf=uf,
            comarca=comarca,
            vara=vara,
            status=status,
            observacoes=observacoes,
            data_abertura=data_abertura,
            data_fechamento=data_fechamento,
            cliente_id=cliente_id
        )
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo
    finally:
        if created_local_db:
            db.close()


def listar_processos(db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        processos = db.query(Processo).all()
        return processos
    finally:
        if created_local_db:
            db.close()


def buscar_processo_por_id(processo_id, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        processo = db.query(Processo).filter(Processo.id == processo_id).first()
        return processo
    finally:
        if created_local_db:
            db.close()


def atualizar_processo(processo_id, db: Session | None = None, **kwargs):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    processo = db.query(Processo).filter(Processo.id == processo_id).first()
    if processo:
        for key, value in kwargs.items():
            setattr(processo, key, value)
        db.commit()
        db.refresh(processo)
    if created_local_db:
        db.close()
    return processo


def deletar_processo(processo_id, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    processo = db.query(Processo).filter(Processo.id == processo_id).first()
    if processo:
        db.delete(processo)
        db.commit()
    if created_local_db:
        db.close()
    return processo
