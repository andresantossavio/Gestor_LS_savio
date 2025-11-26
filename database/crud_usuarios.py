from sqlalchemy.orm import Session
from . import models

# Futuramente, para segurança, a senha deve ser "hasheada"
# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def buscar_usuario(db: Session, usuario_id: int):
    """Busca um usuário pelo ID."""
    return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

def buscar_usuario_por_login(db: Session, login: str):
    """Busca um usuário pelo login."""
    return db.query(models.Usuario).filter(models.Usuario.login == login).first()

def listar_usuarios(db: Session):
    """Lista todos os usuários."""
    return db.query(models.Usuario).all()

def criar_usuario(db: Session, **kwargs):
    """Cria um novo usuário."""
    # hashed_password = pwd_context.hash(senha) # Exemplo de como hashear a senha
    # A função agora recebe todos os dados em kwargs e os passa diretamente para o modelo
    db_usuario = models.Usuario(**kwargs)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def atualizar_usuario(db: Session, usuario_id: int, dados_usuario: dict):
    """Atualiza os dados de um usuário."""
    db_usuario = buscar_usuario(db, usuario_id)
    if not db_usuario:
        return None
    
    for key, value in dados_usuario.items():
        setattr(db_usuario, key, value)
    
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def deletar_usuario(db: Session, usuario_id: int):
    """Deleta um usuário."""
    db_usuario = buscar_usuario(db, usuario_id)
    if db_usuario:
        db.delete(db_usuario)
        db.commit()
    return db_usuario