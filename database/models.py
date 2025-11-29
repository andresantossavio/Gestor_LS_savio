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
    rito = Column(String, nullable=True) # Ex: Comum, Sumário, Sumaríssimo
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

class Recebimento(Base):
    __tablename__ = "recebimentos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_nome = Column(String, nullable=True)
    data = Column(Date, nullable=True)
    valor_centavos = Column(Integer, nullable=True)
    observacao = Column(String, nullable=True)

    participacoes = relationship("ParticipacaoSocio", back_populates="recebimento", cascade="all, delete-orphan")

class ParticipacaoSocio(Base):
    __tablename__ = "participacoes_socio"

    id = Column(Integer, primary_key=True, index=True)
    recebimento_id = Column(Integer, ForeignKey("recebimentos.id"), index=True)
    usuario_id = Column(Integer, nullable=True)
    socio_nome = Column(String, nullable=True)
    percentual_mil = Column(Integer, nullable=True)

    recebimento = relationship("Recebimento", back_populates="participacoes")

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


# Modelos de Contabilidade
class Socio(Base):
    __tablename__ = "socios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False, unique=True)
    funcao = Column(String(80), nullable=True)
    capital_social = Column(Float, nullable=True)
    percentual = Column(Float, nullable=True) # Percentual padrão na sociedade
    saldo = Column(Float, default=0.0, nullable=False) # Saldo de lucros distribuídos

    # Relacionamentos para despesas e entradas
    despesas = relationship("DespesaSocio", back_populates="socio")
    entradas = relationship("EntradaSocio", back_populates="socio")

class ConfiguracaoContabil(Base):
    __tablename__ = "configuracao_contabil"

    id = Column(Integer, primary_key=True, index=True)
    percentual_administrador = Column(Float, default=0.05)
    percentual_fundo_reserva = Column(Float, default=0.10)

class Entrada(Base):
    __tablename__ = "entradas"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String(255), nullable=False)
    data = Column(Date, nullable=False, default=datetime.utcnow)
    valor = Column(Float, nullable=False)
    
    # Relacionamento com os sócios e seus percentuais para esta entrada
    socios = relationship("EntradaSocio", back_populates="entrada", cascade="all, delete-orphan")
    lancamentos = relationship("LancamentoContabil", back_populates="entrada", cascade="all, delete-orphan")


class Despesa(Base):
    __tablename__ = "despesas"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False, default=datetime.utcnow)
    especie = Column(String(100)) # Ex: Estrutura, Individual/Setor
    tipo = Column(String(100)) # Ex: Internet, Estagiário
    descricao = Column(Text, nullable=True)
    valor = Column(Float, nullable=False)

    # Relacionamento com os sócios responsáveis
    responsaveis = relationship("DespesaSocio", back_populates="despesa", cascade="all, delete-orphan")
    lancamentos = relationship("LancamentoContabil", back_populates="despesa", cascade="all, delete-orphan")


class EntradaSocio(Base):
    __tablename__ = "entradas_socios"

    entrada_id = Column(Integer, ForeignKey("entradas.id"), primary_key=True)
    socio_id = Column(Integer, ForeignKey("socios.id"), primary_key=True)
    percentual = Column(Float, nullable=False)

    entrada = relationship("Entrada", back_populates="socios")
    socio = relationship("Socio", back_populates="entradas")


class DespesaSocio(Base):
    __tablename__ = "despesas_socios"

    despesa_id = Column(Integer, ForeignKey("despesas.id"), primary_key=True)
    socio_id = Column(Integer, ForeignKey("socios.id"), primary_key=True)

    despesa = relationship("Despesa", back_populates="responsaveis")
    socio = relationship("Socio", back_populates="despesas")


class PlanoDeContas(Base):
    __tablename__ = "plano_de_contas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)
    descricao = Column(String(255), nullable=False)
    tipo = Column(String(50), nullable=False) # Ativo, Passivo, PL, Receita, Despesa


class LancamentoContabil(Base):
    __tablename__ = "lancamentos_contabeis"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False, default=datetime.utcnow)
    conta_debito_id = Column(Integer, ForeignKey("plano_de_contas.id"), nullable=False)
    conta_credito_id = Column(Integer, ForeignKey("plano_de_contas.id"), nullable=False)
    valor = Column(Float, nullable=False)
    historico = Column(Text)

    # Relacionamentos para rastrear a origem do lançamento
    entrada_id = Column(Integer, ForeignKey("entradas.id"), nullable=True)
    despesa_id = Column(Integer, ForeignKey("despesas.id"), nullable=True)
    
    entrada = relationship("Entrada", back_populates="lancamentos")
    despesa = relationship("Despesa", back_populates="lancamentos")
    conta_debito = relationship("PlanoDeContas", foreign_keys=[conta_debito_id])
    conta_credito = relationship("PlanoDeContas", foreign_keys=[conta_credito_id])

class Fundo(Base):
    __tablename__ = "fundos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False)
    saldo = Column(Float, default=0.0, nullable=False)


class SimplesFaixa(Base):
    __tablename__ = "simples_faixas"

    id = Column(Integer, primary_key=True, index=True)
    limite_superior = Column(Float, nullable=False)  # Limite superior da faixa (ex: 180000.00)
    aliquota = Column(Float, nullable=False)  # Alíquota nominal (ex: 0.045 para 4.5%)
    deducao = Column(Float, nullable=False, default=0.0)  # Dedução em reais (ex: 8100.00)
    vigencia_inicio = Column(Date, nullable=False)  # Data de início da vigência
    vigencia_fim = Column(Date, nullable=True)  # Data de fim da vigência (NULL = vigente)
    ordem = Column(Integer, nullable=False)  # Ordem da faixa (1, 2, 3...)


class DREMensal(Base):
    __tablename__ = "dre_mensal"

    id = Column(Integer, primary_key=True, index=True)
    mes = Column(String(7), nullable=False, unique=True, index=True)  # YYYY-MM
    receita_bruta = Column(Float, nullable=False, default=0.0)
    receita_12m = Column(Float, nullable=False, default=0.0)  # Acumulado 12 meses
    aliquota = Column(Float, nullable=False, default=0.0)  # Alíquota nominal aplicada
    aliquota_efetiva = Column(Float, nullable=False, default=0.0)  # Alíquota após dedução
    deducao = Column(Float, nullable=False, default=0.0)  # Valor da dedução
    imposto = Column(Float, nullable=False, default=0.0)  # Imposto do mês (Simples)
    inss_patronal = Column(Float, nullable=False, default=0.0)  # INSS 20% sobre pró-labore
    despesas_gerais = Column(Float, nullable=False, default=0.0)  # Água, luz, etc.
    lucro_liquido = Column(Float, nullable=False, default=0.0)  # Receita - impostos - despesas
    reserva_10p = Column(Float, nullable=False, default=0.0)  # 10% do lucro líquido
    consolidado = Column(Boolean, default=False, nullable=False)  # Flag de consolidação
    data_consolidacao = Column(DateTime, nullable=True)  # Timestamp da consolidação
