from database.models import Andamento
from sqlalchemy.orm import Session
from datetime import datetime, date


def criar_andamento(db: Session, processo_id: int, tipo_andamento_id: int, descricao_complementar: str | None = None, data_andamento: date | None = None, criado_por: int | None = None):
    """Cria um novo andamento no banco de dados."""
    a = Andamento(
        processo_id=processo_id,
        tipo_andamento_id=tipo_andamento_id,
        descricao_complementar=descricao_complementar,
        criado_por=criado_por,
        data=data_andamento or datetime.utcnow().date(),
        criado_em=datetime.utcnow()
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a
def listar_andamentos(db: Session):
    return db.query(Andamento).all()

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
