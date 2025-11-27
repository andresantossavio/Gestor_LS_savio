from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

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

class UsuarioUpdate(UsuarioBase):
    nome: Optional[str] = None
    login: Optional[str] = None
    senha: Optional[str] = None

class Usuario(UsuarioBase):
    id: int

    class Config:
        from_attributes = True


# Schemas de Contabilidade

# Schemas para Socio
class SocioBase(BaseModel):
    nome: str
    funcao: Optional[str] = None
    capital_social: Optional[float] = None
    percentual: Optional[float] = None

class SocioCreate(SocioBase):
    pass

class SocioUpdate(SocioBase):
    nome: Optional[str] = None

class Socio(SocioBase):
    id: int
    class Config:
        from_attributes = True


# --- Schemas para Criação ---
class EntradaSocioCreate(BaseModel):
    socio_id: int
    percentual: float

class DespesaSocioCreate(BaseModel):
    socio_id: int

# --- Schemas para Leitura (com dados aninhados) ---
class EntradaSocio(BaseModel):
    percentual: float
    socio: Socio
    class Config:
        from_attributes = True

class DespesaSocio(BaseModel):
    socio: Socio
    class Config:
        from_attributes = True


# Schemas para Entrada
class EntradaBase(BaseModel):
    cliente: str
    data: date
    valor: float

class EntradaCreate(EntradaBase):
    socios: List[EntradaSocioCreate] = []

class Entrada(EntradaBase):
    id: int
    socios: List[EntradaSocio] = []
    class Config:
        from_attributes = True


# Schemas para Despesa
class DespesaBase(BaseModel):
    data: date
    especie: str
    tipo: str
    descricao: Optional[str] = None
    valor: float

class DespesaCreate(DespesaBase):
    responsaveis: List[DespesaSocioCreate] = []

class Despesa(DespesaBase):
    id: int
    responsaveis: List[DespesaSocio] = []
    class Config:
        from_attributes = True


# Schemas para PlanoDeContas
class PlanoDeContasBase(BaseModel):
    codigo: str
    descricao: str
    tipo: str

class PlanoDeContasCreate(PlanoDeContasBase):
    pass

class PlanoDeContas(PlanoDeContasBase):
    id: int
    class Config:
        from_attributes = True


# Schemas para LancamentoContabil
class LancamentoContabilBase(BaseModel):
    data: date
    conta_debito_id: int
    conta_credito_id: int
    valor: float
    historico: Optional[str] = None
    entrada_id: Optional[int] = None
    despesa_id: Optional[int] = None

class LancamentoContabilCreate(LancamentoContabilBase):
    pass

class LancamentoContabil(LancamentoContabilBase):
    id: int
    class Config:
        from_attributes = True
