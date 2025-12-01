from sqlalchemy.orm import Session, joinedload
from . import models, crud_clientes

def buscar_processo(db: Session, processo_id: int):
    """Busca um processo pelo ID."""
    return db.query(models.Processo).options(
        joinedload(models.Processo.cliente),
        joinedload(models.Processo.municipio)
    ).filter(models.Processo.id == processo_id).first()

def listar_processos(db: Session):
    """Lista todos os processos."""
    # A relação com o cliente é carregada automaticamente pelo SQLAlchemy/Pydantic.
    return db.query(models.Processo).all()

def criar_processo(db: Session, **kwargs):
    """Cria um novo processo."""
    db_processo = models.Processo(**kwargs)
    db.add(db_processo)
    db.commit()
    db.refresh(db_processo)
    return db_processo

def atualizar_processo(db: Session, processo_id: int, dados_processo: dict):
    """Atualiza os dados de um processo."""
    db_processo = buscar_processo(db, processo_id)
    if not db_processo:
        return None
    
    for key, value in dados_processo.items():
        setattr(db_processo, key, value)
    
    db.commit()
    db.refresh(db_processo)
    return db_processo

def deletar_processo(db: Session, processo_id: int):
    """Deleta um processo."""
    db_processo = buscar_processo(db, processo_id)
    if db_processo:
        db.delete(db_processo)
        db.commit()
    return db_processo