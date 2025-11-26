from database.models import Andamento
from sqlalchemy.orm import Session
from datetime import datetime


def criar_andamento(processo_id: int, descricao: str, db: Session, tipo: str = None, criado_por: int = None, data=None):
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


def listar_andamentos_do_processo(processo_id: int, db: Session):
    return db.query(Andamento).filter(Andamento.processo_id == processo_id).order_by(Andamento.data.desc()).all()


def buscar_andamento(andamento_id: int, db: Session):
    return db.query(Andamento).filter(Andamento.id == andamento_id).first()


def atualizar_andamento(andamento_id: int, db: Session, **kwargs):
    a = db.query(Andamento).filter(Andamento.id == andamento_id).first()
    if not a:
        return None
    for k, v in kwargs.items():
        if hasattr(a, k):
            setattr(a, k, v)
    db.commit()
    db.refresh(a)
    return a


def deletar_andamento(andamento_id: int, db: Session):
    a = db.query(Andamento).filter(Andamento.id == andamento_id).first()
    if not a:
        return False
    db.delete(a)
    db.commit()
    return True
