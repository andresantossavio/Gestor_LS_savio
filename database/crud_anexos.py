from database.database import SessionLocal
from database.models import Anexo
from sqlalchemy.orm import Session
from datetime import datetime
import os

def criar_anexo(processo_id: int = None, andamento_id: int = None,
                nome_original: str = None, caminho_arquivo: str = None,
                mime: str = None, tamanho: int = None, criado_por: int = None, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        a = Anexo(
            processo_id=processo_id,
            andamento_id=andamento_id,
            nome_original=nome_original,
            caminho_arquivo=caminho_arquivo,
            mime=mime,
            tamanho=tamanho,
            criado_por=criado_por,
            criado_em=datetime.utcnow()
        )
        db.add(a)
        db.commit()
        db.refresh(a)
        return a
    finally:
        if created_local_db:
            db.close()

def listar_anexos_do_processo(processo_id: int, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        return db.query(Anexo).filter(Anexo.processo_id == processo_id).order_by(Anexo.criado_em.desc()).all()
    finally:
        if created_local_db:
            db.close()

def listar_anexos_do_andamento(andamento_id: int, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        return db.query(Anexo).filter(Anexo.andamento_id == andamento_id).order_by(Anexo.criado_em.desc()).all()
    finally:
        if created_local_db:
            db.close()

def buscar_anexo(id: int, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        return db.query(Anexo).filter(Anexo.id == id).first()
    finally:
        if created_local_db:
            db.close()

def deletar_anexo(id: int, db: Session | None = None):
    created_local_db = False
    if db is None:
        db = SessionLocal()
        created_local_db = True
    try:
        a = db.query(Anexo).filter(Anexo.id == id).first()
        if not a:
            return False
        caminho = a.caminho_arquivo
        db.delete(a)
        db.commit()
        try:
            if caminho and os.path.exists(caminho):
                os.remove(caminho)
        except Exception:
            pass
        return True
    finally:
        if created_local_db:
            db.close()
