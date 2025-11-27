from sqlalchemy.orm import Session
from . import models


def criar_cliente(db: Session, **kwargs):
    """Cria um novo cliente com base nos dados fornecidos."""
    cliente = models.Cliente(**kwargs)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def listar_clientes(db: Session):
    return db.query(models.Cliente).order_by(models.Cliente.nome).all()


def buscar_cliente_por_id(cliente_id: int, db: Session):
    return db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()

# Função que estava faltando, usada por outros módulos (como processos)
def buscar_cliente(db: Session, cliente_id: int):
    """Busca um cliente pelo ID."""
    return db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()

def atualizar_cliente(cliente_id: int, db: Session, **kwargs):
    cliente = buscar_cliente_por_id(cliente_id, db)
    if cliente:
        for key, value in kwargs.items():
            setattr(cliente, key, value)
        db.commit()
        db.refresh(cliente)
    return cliente


def deletar_cliente(cliente_id: int, db: Session):
    cliente = buscar_cliente_por_id(cliente_id, db)
    if cliente:
        db.delete(cliente)
        db.commit()
        return True
    return False
