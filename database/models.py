from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
    Index,
    JSON
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

class Municipio(Base):
    __tablename__ = "municipios"
    __table_args__ = (
        UniqueConstraint('nome', 'uf', name='uq_municipio_nome_uf'),
        Index('idx_municipio_uf', 'uf'),
        Index('idx_municipio_codigo_ibge', 'codigo_ibge'),
    )

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    uf = Column(String(2), nullable=False)
    codigo_ibge = Column(String(7), unique=True, nullable=False)
    
    # Relationships
    processos = relationship("Processo", back_populates="municipio")
    feriados = relationship("Feriado", back_populates="municipio")

class Feriado(Base):
    __tablename__ = "feriados"
    __table_args__ = (
        Index('idx_feriado_data', 'data'),
        Index('idx_feriado_tipo', 'tipo'),
        Index('idx_feriado_municipio', 'municipio_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False)
    nome = Column(String(200), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'nacional', 'estadual', 'municipal'
    uf = Column(String(2), nullable=True)  # Obrigatório se tipo='estadual'
    municipio_id = Column(Integer, ForeignKey("municipios.id"), nullable=True)  # Obrigatório se tipo='municipal'
    recorrente = Column(Boolean, default=False, nullable=False)  # Se repete anualmente
    criado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    municipio = relationship("Municipio", back_populates="feriados")
    criado_por_usuario = relationship("Usuario")

class Processo(Base):
    __tablename__ = "processos"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String)
    autor = Column(String)
    reu = Column(String)
    municipio_id = Column(Integer, ForeignKey("municipios.id"), nullable=True)  # Substituindo uf/comarca/cidade
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
    municipio = relationship("Municipio", back_populates="processos")
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
    __table_args__ = (
        Index('idx_tarefa_prazo_fatal', 'prazo_fatal'),
        Index('idx_tarefa_status', 'status'),
        Index('idx_tarefa_responsavel', 'responsavel_id'),
    )

    id = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey("processos.id"), nullable=True)
    tipo_tarefa_id = Column(Integer, ForeignKey("tipos_tarefa.id"), nullable=False)
    descricao_complementar = Column(Text, nullable=True)
    
    # Campos de prazos
    prazo = Column(Date, nullable=True)  # Mantido para compatibilidade
    prazo_administrativo = Column(Date, nullable=True)
    prazo_fatal = Column(Date, nullable=True)
    
    # Campos de workflow
    etapa_workflow_atual = Column(String(50), default="analise_pendente")
    workflow_historico = Column(JSON, nullable=True)  # [{etapa, usuario_id, usuario_nome, timestamp, acao}]
    
    # Campos específicos de intimação
    conteudo_intimacao = Column(Text, nullable=True)
    classificacao_intimacao = Column(String(100), nullable=True)
    conteudo_decisao = Column(Text, nullable=True)
    
    # Relacionamento pai-filho para tarefas derivadas
    tarefa_origem_id = Column(Integer, ForeignKey("tarefas.id"), nullable=True)
    
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    status = Column(String(40), default="pendente")
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    processo = relationship("Processo", back_populates="tarefas")
    tipo_tarefa = relationship("TipoTarefa")
    responsavel = relationship("Usuario", back_populates="tarefas")
    tarefa_origem = relationship("Tarefa", remote_side=[id], backref="tarefas_derivadas")

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
    
    # Relationship
    workflow_template = relationship("WorkflowTemplate", back_populates="tipo_tarefa", uselist=False)

class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"

    id = Column(Integer, primary_key=True, index=True)
    tipo_tarefa_id = Column(Integer, ForeignKey("tipos_tarefa.id"), unique=True, nullable=False)
    etapas = Column(JSON, nullable=False)  # [{nome, ordem, acao_label, pode_criar_tarefa}]
    
    # Relationship
    tipo_tarefa = relationship("TipoTarefa", back_populates="workflow_template")


# Modelos de Contabilidade
class Socio(Base):
    __tablename__ = "socios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False, unique=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)  # Link opcional para usuário
    funcao = Column(String(80), nullable=True)
    capital_social = Column(Float, nullable=True)
    percentual = Column(Float, nullable=True) # Percentual padrão na sociedade
    saldo = Column(Float, default=0.0, nullable=False) # Saldo de lucros distribuídos

    # Relacionamentos para despesas e entradas
    despesas = relationship("DespesaSocio", back_populates="socio")
    entradas = relationship("EntradaSocio", back_populates="socio")
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    pagamentos_pendentes = relationship("PagamentoPendente", back_populates="socio")
    aportes = relationship("AporteCapital", back_populates="socio", cascade="all, delete-orphan")
    saques_fundos = relationship("SaqueFundo", back_populates="beneficiario")

class AporteCapital(Base):
    __tablename__ = "aportes_capital"
    __table_args__ = (
        Index('idx_aporte_socio_data', 'socio_id', 'data'),
    )

    id = Column(Integer, primary_key=True, index=True)
    socio_id = Column(Integer, ForeignKey("socios.id"), nullable=False)
    data = Column(Date, nullable=False, index=True)
    valor = Column(Float, nullable=False)
    tipo_aporte = Column(String(20), nullable=False)  # 'dinheiro', 'bens', 'servicos', 'retirada'
    descricao = Column(String(500), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    socio = relationship("Socio", back_populates="aportes")

class ConfiguracaoContabil(Base):
    __tablename__ = "configuracao_contabil"

    id = Column(Integer, primary_key=True, index=True)
    percentual_administrador = Column(Float, default=0.05)
    percentual_fundo_reserva = Column(Float, default=0.10)
    salario_minimo = Column(Float, default=1518.0)  # Salário mínimo nacional

class Entrada(Base):
    __tablename__ = "entradas"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String(255), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)  # Link opcional para cliente cadastrado
    data = Column(Date, nullable=False, default=datetime.utcnow)
    valor = Column(Float, nullable=False)
    
    # Relacionamento com os sócios e seus percentuais para esta entrada
    socios = relationship("EntradaSocio", back_populates="entrada", cascade="all, delete-orphan")
    lancamentos = relationship("LancamentoContabil", back_populates="entrada", cascade="all, delete-orphan")
    cliente_rel = relationship("Cliente")


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
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    descricao = Column(String(255), nullable=False)
    tipo = Column(String(50), nullable=False)  # Ativo, Passivo, PL, Receita, Despesa
    natureza = Column(String(20), nullable=False)  # Devedora ou Credora
    pai_id = Column(Integer, ForeignKey("plano_de_contas.id"), nullable=True)  # Hierarquia
    nivel = Column(Integer, nullable=False, default=1)  # Nível hierárquico (1, 2, 3...)
    aceita_lancamento = Column(Boolean, default=True, nullable=False)  # Contas sintéticas não aceitam
    ativo = Column(Boolean, default=True, nullable=False)  # Conta ativa ou inativa
    
    # Relacionamentos
    pai = relationship("PlanoDeContas", remote_side=[id], backref="filhos")


class LancamentoContabil(Base):
    __tablename__ = "lancamentos_contabeis"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False, default=datetime.utcnow, index=True)
    conta_debito_id = Column(Integer, ForeignKey("plano_de_contas.id"), nullable=False)
    conta_credito_id = Column(Integer, ForeignKey("plano_de_contas.id"), nullable=False)
    valor = Column(Float, nullable=False)
    historico = Column(Text)
    automatico = Column(Boolean, default=True, nullable=False)  # True = gerado automaticamente
    editavel = Column(Boolean, default=True, nullable=False)  # True = pode ser editado
    criado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    editado_em = Column(DateTime, nullable=True)

    # Relacionamentos para rastrear a origem do lançamento
    entrada_id = Column(Integer, ForeignKey("entradas.id"), nullable=True)
    despesa_id = Column(Integer, ForeignKey("despesas.id"), nullable=True)
    
    # Campos para sistema de provisões
    tipo_lancamento = Column(String(30), default='efetivo', nullable=False)  # 'efetivo', 'provisao', 'pagamento_pro_labore', 'pagamento_lucro', 'pagamento_imposto'
    referencia_mes = Column(String(7), nullable=True, index=True)  # YYYY-MM para agrupamento por competência
    
    # Controle de pagamento de provisões
    pago = Column(Boolean, default=False, nullable=False)  # True = provisão já foi paga
    data_pagamento = Column(Date, nullable=True)  # Data em que o pagamento foi efetivado
    valor_pago = Column(Float, nullable=True)  # Valor efetivamente pago (pode ser parcial)
    lancamento_origem_id = Column(Integer, ForeignKey("lancamentos_contabeis.id"), nullable=True)  # Ref. ao lançamento que originou este (para pagamentos parciais)
    
    entrada = relationship("Entrada", back_populates="lancamentos")
    despesa = relationship("Despesa", back_populates="lancamentos")
    conta_debito = relationship("PlanoDeContas", foreign_keys=[conta_debito_id])
    conta_credito = relationship("PlanoDeContas", foreign_keys=[conta_credito_id])
    usuario_criador = relationship("Usuario", foreign_keys=[criado_por])
    lancamento_origem = relationship("LancamentoContabil", remote_side="LancamentoContabil.id", foreign_keys=[lancamento_origem_id])


class ProvisaoEntrada(Base):
    """Tabela para rastrear provisões calculadas por entrada de honorários"""
    __tablename__ = "provisoes_entradas"

    id = Column(Integer, primary_key=True, index=True)
    entrada_id = Column(Integer, ForeignKey("entradas.id"), nullable=False, unique=True)
    mes_referencia = Column(String(7), nullable=False, index=True)  # YYYY-MM
    data_calculo = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Base de cálculo
    receita_12m_base = Column(Float, nullable=False)
    aliquota_simples = Column(Float, nullable=False)
    imposto_provisionado = Column(Float, nullable=False)
    lucro_bruto = Column(Float, nullable=False)
    
    # Provisões calculadas
    pro_labore_previsto = Column(Float, nullable=False)
    inss_patronal_previsto = Column(Float, nullable=False)
    inss_pessoal_previsto = Column(Float, nullable=False)
    fundo_reserva_previsto = Column(Float, nullable=False)
    lucro_disponivel_total = Column(Float, nullable=False)
    
    # Distribuição por sócio (JSON)
    # Estrutura: [{"socio_id": 1, "nome": "André", "percentual_entrada": 50.0, "lucro_disponivel": 500.0}, ...]
    distribuicao_socios = Column(JSON, nullable=False)
    
    # Relacionamento
    entrada = relationship("Entrada", backref="provisao")


class Ativo(Base):
    """Tabela para controle de ativos imobilizados (equipamentos, móveis, etc)"""
    __tablename__ = "ativos"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(255), nullable=False)
    data_aquisicao = Column(Date, nullable=False)
    valor_aquisicao = Column(Float, nullable=False)
    vida_util_meses = Column(Integer, nullable=False)  # Vida útil em meses
    taxa_depreciacao_anual = Column(Float, nullable=False)  # % ao ano (ex: 0.10 = 10%)
    valor_residual = Column(Float, default=0.0)  # Valor residual ao fim da vida útil
    depreciacao_acumulada = Column(Float, default=0.0, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)  # Ativo em uso ou baixado
    data_baixa = Column(Date, nullable=True)
    motivo_baixa = Column(Text, nullable=True)  # Venda, descarte, doação, etc
    conta_ativo_id = Column(Integer, ForeignKey("plano_de_contas.id"), nullable=False)
    conta_depreciacao_id = Column(Integer, ForeignKey("plano_de_contas.id"), nullable=False)
    
    # Relacionamentos
    conta_ativo = relationship("PlanoDeContas", foreign_keys=[conta_ativo_id])
    conta_depreciacao = relationship("PlanoDeContas", foreign_keys=[conta_depreciacao_id])
    depreciacoes = relationship("DepreciacaoMensal", back_populates="ativo", cascade="all, delete-orphan")


class DepreciacaoMensal(Base):
    """Registro mensal de depreciação de ativos"""
    __tablename__ = "depreciacoes_mensais"

    id = Column(Integer, primary_key=True, index=True)
    ativo_id = Column(Integer, ForeignKey("ativos.id"), nullable=False)
    mes = Column(String(7), nullable=False, index=True)  # YYYY-MM
    valor_depreciacao = Column(Float, nullable=False)
    lancamento_id = Column(Integer, ForeignKey("lancamentos_contabeis.id"), nullable=True)
    
    # Relacionamentos
    ativo = relationship("Ativo", back_populates="depreciacoes")
    lancamento = relationship("LancamentoContabil")


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
    inss_pessoal = Column(Float, nullable=False, default=0.0)  # INSS 11% sobre pró-labore
    pro_labore = Column(Float, nullable=False, default=0.0)  # Pró-labore calculado (5% lucro líquido)
    despesas_gerais = Column(Float, nullable=False, default=0.0)  # Água, luz, etc.
    lucro_liquido = Column(Float, nullable=False, default=0.0)  # Receita - impostos - despesas
    reserva_10p = Column(Float, nullable=False, default=0.0)  # 10% do lucro líquido
    consolidado = Column(Boolean, default=False, nullable=False)  # Flag de consolidação
    data_consolidacao = Column(DateTime, nullable=True)  # Timestamp da consolidação


class PagamentoPendente(Base):
    """Modelo simplificado de pagamentos pendentes - substitui a complexidade do sistema contábil"""
    __tablename__ = "pagamentos_pendentes"
    __table_args__ = (
        Index('idx_pendente_tipo', 'tipo'),
        Index('idx_pendente_mes_ano', 'mes_ref', 'ano_ref'),
        Index('idx_pendente_confirmado', 'confirmado'),
        Index('idx_pendente_socio', 'socio_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False)  # 'INSS', 'SIMPLES', 'LUCRO_SOCIO', 'FUNDO_RESERVA', 'DESPESA'
    descricao = Column(String(255), nullable=False)  # Ex: "INSS sobre honorários de Jun/2024"
    valor = Column(Float, nullable=False)
    mes_ref = Column(Integer, nullable=False)  # Mês de referência (1-12)
    ano_ref = Column(Integer, nullable=False)  # Ano de referência
    
    # Confirmação
    confirmado = Column(Boolean, default=False, nullable=False)
    data_confirmacao = Column(Date, nullable=True)  # Data em que foi marcado como pago
    
    # Relacionamentos opcionais
    socio_id = Column(Integer, ForeignKey("socios.id"), nullable=True)  # Para pagamentos de lucro
    entrada_id = Column(Integer, ForeignKey("entradas.id"), nullable=True)  # Entrada que gerou o pagamento
    
    # Metadata
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    socio = relationship("Socio", back_populates="pagamentos_pendentes")
    entrada = relationship("Entrada")


class AtivoImobilizado(Base):
    """Ativos imobilizados sujeitos à depreciação"""
    __tablename__ = "ativos_imobilizados"
    __table_args__ = (
        Index('idx_ativo_categoria', 'categoria'),
        Index('idx_ativo_ativo', 'ativo'),
        Index('idx_ativo_elegivel', 'elegivel_depreciacao'),
    )

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(255), nullable=False)  # Ex: "Notebook Dell Inspiron"
    categoria = Column(String(50), nullable=False)  # equipamentos, moveis, veiculos, computadores, etc
    valor_aquisicao = Column(Float, nullable=False)  # Valor original de compra
    data_aquisicao = Column(Date, nullable=False)  # Data da aquisição
    elegivel_depreciacao = Column(Boolean, default=True, nullable=False)  # Se deve depreciar
    conta_ativo_id = Column(Integer, ForeignKey("plano_de_contas.id"), nullable=True)  # Conta no plano de contas (1.2.x)
    ativo = Column(Boolean, default=True, nullable=False)  # Se ainda está em uso
    observacoes = Column(Text, nullable=True)  # Notas adicionais
    
    # Metadata
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    conta_ativo = relationship("PlanoDeContas", foreign_keys=[conta_ativo_id])


class SaqueFundo(Base):
    """Registro de saques dos fundos de reserva ou investimento"""
    __tablename__ = "saques_fundos"
    __table_args__ = (
        Index('idx_saque_tipo', 'tipo_fundo'),
        Index('idx_saque_data', 'data'),
        Index('idx_saque_beneficiario', 'beneficiario_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False)  # Data do saque
    valor = Column(Float, nullable=False)  # Valor sacado
    tipo_fundo = Column(String(20), nullable=False)  # 'reserva' ou 'investimento'
    beneficiario_id = Column(Integer, ForeignKey("socios.id"), nullable=False)  # Quem recebeu
    motivo = Column(Text, nullable=False)  # Justificativa do saque
    comprovante_path = Column(String(500), nullable=True)  # Caminho do arquivo de comprovante
    lancamento_id = Column(Integer, ForeignKey("lancamentos_contabeis.id"), nullable=True)  # Lançamento contábil gerado
    
    # Metadata
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    criado_por = Column(String(80), nullable=True)  # Login do usuário que registrou
    
    # Relationships
    beneficiario = relationship("Socio", back_populates="saques_fundos")
    lancamento = relationship("LancamentoContabil")
