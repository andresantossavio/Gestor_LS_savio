from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Text
)
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(120), nullable=True)
    login = Column(String(80), unique=True, nullable=False)
    senha = Column(String(200), nullable=False)
    perfil = Column(String(50), default="Administrador")
    tarefas = relationship("Tarefa", back_populates="responsavel")
    andamentos = relationship("Andamento")
    anexos = relationship("Anexo")

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    nome_fantasia = Column(String, nullable=True)
    cpf_cnpj = Column(String, nullable=False)
    tipo_pessoa = Column(String) # Pessoa Física ou Pessoa Jurídica
    tipo_pj = Column(String) # Direito Público ou Direito Privado
    subtipo_pj = Column(String) # MEI, LTDA, Autarquia, etc.
    capacidade = Column(String, nullable=True) # Capaz, Relativamente Incapaz, Incapaz
    responsavel_nome = Column(String, nullable=True)
    responsavel_cpf = Column(String, nullable=True)
    telefone = Column(String)
    email = Column(String)
    logradouro = Column(String)
    numero = Column(String)
    complemento = Column(String)
    bairro = Column(String)
    cidade = Column(String)
    uf = Column(String(2))
    cep = Column(String)
    processos = relationship("Processo", back_populates="cliente", cascade="all, delete-orphan")

class Processo(Base):
    __tablename__ = "processos"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String)
    autor = Column(String)
    reu = Column(String)
    uf = Column(String)
    comarca = Column(String)
    vara = Column(String)
    fase = Column(String)
    categoria = Column(String, nullable=True) # Ex: Comum, Originário
    tribunal_originario = Column(String, nullable=True) # Ex: STJ, STF, etc.
    esfera_justica = Column(String, nullable=True) # Ex: Justiça Federal, Justiça Estadual
    tipo = Column(String, nullable=True) # Ex: Judicial, Extrajudicial, etc.
    classe = Column(String, nullable=True) # Ex: Cível, Criminal, Trabalhista
    sub_classe = Column(String, nullable=True) # Ex: Ação Pública, Ação Privada
    status = Column(String)
    observacoes = Column(String)
    data_abertura = Column(String)
    data_fechamento = Column(String)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    cliente = relationship("Cliente", back_populates="processos")
    andamentos = relationship("Andamento", cascade="all, delete-orphan")
    tarefas = relationship("Tarefa", cascade="all, delete-orphan")
    anexos = relationship("Anexo", cascade="all, delete-orphan")
    pagamentos = relationship("Pagamento", cascade="all, delete-orphan")

class Pagamento(Base):
    __tablename__ = "pagamentos"
    
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String)
    valor = Column(Float, nullable=False)
    data_pagamento = Column(Date)
    tipo = Column(String)
    processo_id = Column(Integer, ForeignKey("processos.id"))
    processo = relationship("Processo")

class Andamento(Base):
    __tablename__ = "andamentos"

    id = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey("processos.id"))
    tipo_andamento_id = Column(Integer, ForeignKey("tipos_andamento.id"), nullable=False)
    data = Column(Date, default=datetime.utcnow, nullable=False)
    descricao_complementar = Column(Text, nullable=True) # Para notas adicionais do usuário
    criado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    processo = relationship("Processo")
    tipo_andamento = relationship("TipoAndamento")
    criado_por_usuario = relationship("Usuario")
    anexos = relationship("Anexo", cascade="all, delete-orphan")

class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey("processos.id"))
    tipo_tarefa_id = Column(Integer, ForeignKey("tipos_tarefa.id"), nullable=False)
    descricao_complementar = Column(Text, nullable=True) # Para notas adicionais do usuário
    prazo = Column(Date, nullable=True)
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    status = Column(String(40), default="pendente")
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    processo = relationship("Processo")
    tipo_tarefa = relationship("TipoTarefa")
    responsavel = relationship("Usuario", back_populates="tarefas")

class Anexo(Base):
    __tablename__ = "anexos"

    id = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey("processos.id"), nullable=True)
    andamento_id = Column(Integer, ForeignKey("andamentos.id"), nullable=True)
    nome_arquivo = Column(String(255)) # Renomeado para consistência
    caminho_arquivo = Column(String(500), nullable=False)
    mime = Column(String(100))
    tamanho = Column(Integer)
    criado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    processo = relationship("Processo")
    andamento = relationship("Andamento")
    criado_por_usuario = relationship("Usuario")

class TipoAndamento(Base):
    __tablename__ = "tipos_andamento"

    id = Column(Integer, primary_key=True)
    nome = Column(String(150), unique=True, nullable=False)
    descricao_padrao = Column(Text, nullable=True)

class TipoTarefa(Base):
    __tablename__ = "tipos_tarefa"

    id = Column(Integer, primary_key=True)
    nome = Column(String(150), unique=True, nullable=False)
    descricao_padrao = Column(Text, nullable=True)
