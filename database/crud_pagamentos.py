from database.models import Pagamento
from sqlalchemy.orm import Session
from datetime import date


def criar_pagamento(db: Session, descricao: str, valor: float, tipo: str, processo_id: int, data_pagamento=date.today()):
    pagamento = Pagamento(descricao=descricao, valor=valor, tipo=tipo,
                          processo_id=processo_id, data_pagamento=data_pagamento)
    db.add(pagamento)
    db.commit()
    db.refresh(pagamento)
    return pagamento


def listar_pagamentos(db: Session):
    return db.query(Pagamento).all()


def buscar_pagamento_por_id(db: Session, pagamento_id: int):
    return db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()


def atualizar_pagamento(db: Session, pagamento_id: int, **kwargs):
    pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if pagamento:
        for key, value in kwargs.items():
            setattr(pagamento, key, value)
        db.commit()
        db.refresh(pagamento)
    return pagamento


def deletar_pagamento(db: Session, pagamento_id: int):
    pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if pagamento:
        db.delete(pagamento)
        db.commit()
        return True
    return False
