from database.models import Tarefa
from sqlalchemy.orm import Session
from datetime import datetime, date


def criar_tarefa(titulo: str, db: Session, descricao: str = None, prazo: date = None,
                 responsavel_id: int = None, processo_id: int = None, status: str = "pendente"):
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


def listar_tarefas_do_processo(processo_id: int, db: Session):
    return db.query(Tarefa).filter(Tarefa.processo_id == processo_id).order_by(Tarefa.prazo).all()


def listar_tarefas_gerais(db: Session):
    return db.query(Tarefa).filter(Tarefa.processo_id == None).order_by(Tarefa.prazo).all()


def listar_tarefas_por_responsavel(responsavel_id: int, db: Session):
    return db.query(Tarefa).filter(Tarefa.responsavel_id == responsavel_id).order_by(Tarefa.prazo).all()


def buscar_tarefa(tarefa_id: int, db: Session):
    return db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()


def atualizar_tarefa(tarefa_id: int, db: Session, **kwargs):
    t = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not t:
        return None
    for k, v in kwargs.items():
        if hasattr(t, k):
            setattr(t, k, v)
    t.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(t)
    return t


def deletar_tarefa(tarefa_id: int, db: Session):
    t = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not t:
        return False
    db.delete(t)
    db.commit()
    return True


def listar_tarefas_por_prazo(inicio: date, fim: date, db: Session):
    return db.query(Tarefa).filter(Tarefa.prazo >= inicio, Tarefa.prazo <= fim).all()
