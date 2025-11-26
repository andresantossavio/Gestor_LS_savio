from sqlalchemy.orm import Session
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
    db: Session,
):
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
        cliente_id=cliente_id,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


def listar_processos(db: Session):
    return db.query(Processo).order_by(Processo.id.desc()).all()


def buscar_processo_por_id(processo_id: int, db: Session):
    return db.query(Processo).filter(Processo.id == processo_id).first()


def atualizar_processo(processo_id: int, db: Session, **kwargs):
    processo = db.query(Processo).filter(Processo.id == processo_id).first()
    if processo:
        for key, value in kwargs.items():
            setattr(processo, key, value)
        db.commit()
        db.refresh(processo)
    return processo


def deletar_processo(processo_id: int, db: Session):
    processo = db.query(Processo).filter(Processo.id == processo_id).first()
    if processo:
        db.delete(processo)
        db.commit()
        return True
    return False
