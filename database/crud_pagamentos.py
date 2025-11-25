from database.database import SessionLocal
from database.models import Pagamento
from sqlalchemy.orm import Session
from datetime import date


def criar_pagamento(db: Session | None, descricao, valor, tipo, processo_id, data_pagamento=date.today()):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    pagamento = Pagamento(descricao=descricao, valor=valor, tipo=tipo,
                          processo_id=processo_id, data_pagamento=data_pagamento)
    db.add(pagamento)
    db.commit()
    db.refresh(pagamento)
    if created_local_db:
        db.close()
    return pagamento

def listar_pagamentos(db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    pagamentos = db.query(Pagamento).all()
    if created_local_db:
        db.close()
    return pagamentos

def buscar_pagamento_por_id(db: Session | None, pagamento_id):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if created_local_db:
        db.close()
    return pagamento

def atualizar_pagamento(db: Session | None, pagamento_id, **kwargs):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if pagamento:
        for key, value in kwargs.items():
            setattr(pagamento, key, value)
        db.commit()
        db.refresh(pagamento)
    if created_local_db:
        db.close()
    return pagamento

def deletar_pagamento(db: Session | None, pagamento_id):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if pagamento:
        db.delete(pagamento)
        db.commit()
    if created_local_db:
        db.close()
    return pagamento
