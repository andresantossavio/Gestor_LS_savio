"""
CRUD operations para Municípios.
"""
from sqlalchemy.orm import Session
from database.models import Municipio
from typing import List, Optional


def listar_municipios(db: Session, limit: int = 6000) -> List[Municipio]:
    """
    Lista todos os municípios.
    
    Args:
        db: Sessão do banco de dados
        limit: Limite de registros (padrão 6000 para cobrir todos)
    
    Returns:
        Lista de municípios ordenada por UF e nome
    """
    return db.query(Municipio).order_by(
        Municipio.uf, Municipio.nome
    ).limit(limit).all()


def listar_municipios_por_uf(uf: str, db: Session) -> List[Municipio]:
    """
    Lista municípios de uma UF específica.
    
    Args:
        uf: Sigla da UF (ex: 'SP', 'RJ')
        db: Sessão do banco de dados
    
    Returns:
        Lista de municípios da UF ordenada por nome
    """
    return db.query(Municipio).filter(
        Municipio.uf == uf.upper()
    ).order_by(Municipio.nome).all()


def buscar_municipio_por_id(municipio_id: int, db: Session) -> Optional[Municipio]:
    """
    Busca município por ID.
    
    Args:
        municipio_id: ID do município
        db: Sessão do banco de dados
    
    Returns:
        Município encontrado ou None
    """
    return db.query(Municipio).filter(Municipio.id == municipio_id).first()


def buscar_por_codigo_ibge(codigo_ibge: str, db: Session) -> Optional[Municipio]:
    """
    Busca município por código IBGE.
    
    Args:
        codigo_ibge: Código IBGE de 7 dígitos
        db: Sessão do banco de dados
    
    Returns:
        Município encontrado ou None
    """
    return db.query(Municipio).filter(
        Municipio.codigo_ibge == codigo_ibge
    ).first()


def buscar_municipio_por_nome_uf(nome: str, uf: str, db: Session) -> Optional[Municipio]:
    """
    Busca município por nome e UF.
    
    Args:
        nome: Nome do município
        uf: Sigla da UF
        db: Sessão do banco de dados
    
    Returns:
        Município encontrado ou None
    """
    return db.query(Municipio).filter(
        Municipio.nome == nome,
        Municipio.uf == uf.upper()
    ).first()


def criar_municipio(nome: str, uf: str, codigo_ibge: str, db: Session) -> Municipio:
    """
    Cria um novo município (uso administrativo).
    
    Args:
        nome: Nome do município
        uf: Sigla da UF
        codigo_ibge: Código IBGE
        db: Sessão do banco de dados
    
    Returns:
        Município criado
    """
    municipio = Municipio(
        nome=nome,
        uf=uf.upper(),
        codigo_ibge=codigo_ibge
    )
    db.add(municipio)
    db.commit()
    db.refresh(municipio)
    return municipio


def contar_municipios_por_uf(db: Session) -> dict:
    """
    Conta quantos municípios existem por UF.
    
    Args:
        db: Sessão do banco de dados
    
    Returns:
        Dicionário {UF: quantidade}
    """
    from sqlalchemy import func
    
    resultado = db.query(
        Municipio.uf,
        func.count(Municipio.id).label('count')
    ).group_by(Municipio.uf).order_by(Municipio.uf).all()
    
    return {uf: count for uf, count in resultado}
