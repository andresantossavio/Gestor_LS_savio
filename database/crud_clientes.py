from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Cliente

def criar_cliente(nome, cpf_cnpj, telefone, email, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    cliente = Cliente(
        nome=nome,
        cpf_cnpj=cpf_cnpj,
        telefone=telefone,
        email=email
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    if created_local_db:
        db.close()
    return cliente

def listar_clientes(db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    result = db.query(Cliente).all()
    if created_local_db:
        db.close()
    return result

def atualizar_cliente(id, nome, cpf_cnpj, telefone, email, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    cliente = db.query(Cliente).filter_by(id=id).first()
    if cliente:
        cliente.nome = nome
        cliente.cpf_cnpj = cpf_cnpj
        cliente.telefone = telefone
        cliente.email = email
        db.commit()
        db.refresh(cliente)
    if created_local_db:
        db.close()
    return cliente

def deletar_cliente(id, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    cliente = db.query(Cliente).filter_by(id=id).first()
    if cliente:
        db.delete(cliente)
        db.commit()
    if created_local_db:
        db.close()
    
