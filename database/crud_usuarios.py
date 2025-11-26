from database.models import Usuario
from sqlalchemy.orm import Session
import hashlib


def criar_usuario(db: Session, nome, email, login, senha, perfil):
    usuario = Usuario(
        nome=nome,
        email=email,
        login=login,
        senha=senha,
        perfil=perfil
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def listar_usuarios(db: Session):
    return db.query(Usuario).all()


def atualizar_usuario(db: Session, usuario_id: int, **kwargs):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario:
        for key, value in kwargs.items():
            if key == "senha" and value:
                # Criptografa a senha apenas se uma nova for fornecida
                setattr(usuario, key, hashlib.sha256(value.encode()).hexdigest())
            elif hasattr(usuario, key):
                setattr(usuario, key, value)
        db.commit()
        db.refresh(usuario)
    return usuario


def excluir_usuario(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario:
        db.delete(usuario)
        db.commit()
        return True
    return False
