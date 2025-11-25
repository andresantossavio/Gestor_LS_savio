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

def atualizar_usuario(db: Session, usuario_id: int, nome: str, email: str, login: str, senha: str, perfil: str):
    usuario = db.query(Usuario).filter_by(id=usuario_id).first()
    if usuario:
        usuario.nome = nome
        usuario.email = email
        usuario.login = login
        if senha:
            usuario.senha = hashlib.sha256(senha.encode()).hexdigest()
        usuario.admin = True if perfil == "Administrador" else False
        db.commit()
        db.refresh(usuario)
    return usuario

def excluir_usuario(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter_by(id=usuario_id).first()
    if usuario:
        db.delete(usuario)
        db.commit()


            
