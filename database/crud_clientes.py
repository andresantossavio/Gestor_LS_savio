from sqlalchemy.orm import Session
from database.models import Cliente


def criar_cliente(nome: str, cpf_cnpj: str, telefone: str, email: str, db: Session):
    cliente = Cliente(
        nome=nome,
        cpf_cnpj=cpf_cnpj,
        telefone=telefone,
        email=email
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def listar_clientes(db: Session):
    return db.query(Cliente).order_by(Cliente.nome).all()


def buscar_cliente_por_id(cliente_id: int, db: Session):
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()


def atualizar_cliente(cliente_id: int, db: Session, **kwargs):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente:
        for key, value in kwargs.items():
            setattr(cliente, key, value)
        db.commit()
        db.refresh(cliente)
    return cliente


def deletar_cliente(cliente_id: int, db: Session):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente:
        db.delete(cliente)
        db.commit()
        return True
    return False
