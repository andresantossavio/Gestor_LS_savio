from database.models import Anexo
from sqlalchemy.orm import Session
from datetime import datetime
import os


def criar_anexo(processo_id: int = None, andamento_id: int = None,
                nome_original: str = None, caminho_arquivo: str = None,
                mime: str = None, tamanho: int = None, criado_por: int = None, db: Session = None) -> Anexo:
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


def listar_anexos_do_processo(processo_id: int, db: Session):
    return db.query(Anexo).filter(Anexo.processo_id == processo_id).order_by(Anexo.criado_em.desc()).all()


def listar_anexos_do_andamento(andamento_id: int, db: Session):
    return db.query(Anexo).filter(Anexo.andamento_id == andamento_id).order_by(Anexo.criado_em.desc()).all()


def buscar_anexo(id: int, db: Session):
    return db.query(Anexo).filter(Anexo.id == id).first()


def deletar_anexo(id: int, db: Session):
    a = db.query(Anexo).filter(Anexo.id == id).first()
    if not a:
        return False
    caminho = a.caminho_arquivo
    db.delete(a)
    db.commit()
    try:
        if caminho and os.path.exists(caminho):
            os.remove(caminho)
    except Exception as e:
        # Log o erro seria uma boa prática aqui
        print(f"Erro ao deletar arquivo físico: {e}")
        pass
    return True
