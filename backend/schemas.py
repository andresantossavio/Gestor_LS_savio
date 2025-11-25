from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class ClienteBase(BaseModel):
    nome: str
    cpf_cnpj: str
    telefone: str | None = None
    email: str | None = None

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(ClienteBase):
    pass

class Cliente(ClienteBase):
    id: int

    class Config:
        from_attributes = True


class ProcessoBase(BaseModel):
    numero: Optional[str] = None
    autor: Optional[str] = None
    reu: Optional[str] = None
    fase: Optional[str] = None
    uf: Optional[str] = None
    comarca: Optional[str] = None
    vara: Optional[str] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None
    data_abertura: Optional[str] = None
    data_fechamento: Optional[str] = None
    cliente_id: Optional[int] = None

class ProcessoCreate(ProcessoBase):
    pass

class ProcessoUpdate(ProcessoBase):
    pass

class Processo(ProcessoBase):
    id: int
    cliente: Optional["Cliente"] = None

    class Config:
        from_attributes = True

# Adicione esta linha no final do arquivo para resolver a referência circular
Processo.model_rebuild()


class TarefaBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    prazo: Optional[date] = None
    responsavel_id: Optional[int] = None
    processo_id: Optional[int] = None
    status: Optional[str] = "pendente"

class TarefaCreate(TarefaBase):
    pass

class TarefaUpdate(TarefaBase):
    pass

class Tarefa(TarefaBase):
    id: int
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class AndamentoBase(BaseModel):
    processo_id: int
    descricao: str
    tipo: Optional[str] = None
    criado_por: Optional[int] = None
    data: Optional[date] = None

class AndamentoCreate(AndamentoBase):
    pass

class AndamentoUpdate(AndamentoBase):
    pass

class Andamento(AndamentoBase):
    id: int
    criado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnexoBase(BaseModel):
    processo_id: Optional[int] = None
    andamento_id: Optional[int] = None
    nome_original: Optional[str] = None
    caminho_arquivo: Optional[str] = None
    mime: Optional[str] = None
    tamanho: Optional[int] = None
    criado_por: Optional[int] = None

class AnexoCreate(AnexoBase):
    pass

class Anexo(AnexoBase):
    id: int
    criado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class PagamentoBase(BaseModel):
    descricao: Optional[str] = None
    valor: float
    data_pagamento: Optional[date] = None
    tipo: Optional[str] = None
    processo_id: Optional[int] = None

class PagamentoCreate(PagamentoBase):
    pass

class Pagamento(PagamentoBase):
    id: int

    class Config:
        from_attributes = True


class UsuarioBase(BaseModel):
    nome: str
    email: Optional[str] = None
    login: str
    perfil: Optional[str] = "Administrador"

class UsuarioCreate(UsuarioBase):
    senha: str

class Usuario(UsuarioBase):
    id: int

    class Config:
        from_attributes = True
