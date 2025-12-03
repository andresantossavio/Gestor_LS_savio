from __future__ import annotations
from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from typing import Literal

class ClienteBase(BaseModel):
    nome: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    tipo_pessoa: Optional[str] = None
    tipo_pj: Optional[str] = None
    subtipo_pj: Optional[str] = None
    capacidade: Optional[str] = None
    responsavel_nome: Optional[str] = None
    responsavel_cpf: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
    cep: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(ClienteBase):
    pass

class Cliente(ClienteBase):
    id: int

    class Config:
        from_attributes = True


# ==================== SCHEMAS DE MUNICÍPIO (ANTES DE PROCESSO) ====================

class MunicipioBase(BaseModel):
    nome: str
    uf: str
    codigo_ibge: str

class MunicipioCreate(MunicipioBase):
    pass

class MunicipioResponse(MunicipioBase):
    id: int
    
    class Config:
        from_attributes = True


# ==================== SCHEMAS DE PROCESSO ====================

class ProcessoBase(BaseModel):
    numero: Optional[str] = None
    autor: Optional[str] = None
    reu: Optional[str] = None
    fase: Optional[str] = None
    municipio_id: Optional[int] = None  # Substituindo uf/comarca
    vara: Optional[str] = None
    categoria: Optional[str] = None
    tribunal_originario: Optional[str] = None
    esfera_justica: Optional[str] = None
    tipo: Optional[str] = None
    rito: Optional[str] = None
    classe: Optional[str] = None
    sub_classe: Optional[str] = None
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
    cliente: Optional[Cliente] = None
    municipio: Optional[MunicipioResponse] = None

    class Config:
        from_attributes = True


# Schemas de Tarefa e Andamento movidos para o final do arquivo com correções


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
    usuario_id: Optional[int] = None
    funcao: Optional[str] = None
    capital_social: Optional[float] = None
    percentual: Optional[float] = None

class SocioCreate(SocioBase):
    pass

class SocioUpdate(SocioBase):
    nome: Optional[str] = None

class Socio(SocioBase):
    id: int
    usuario: Optional[Usuario] = None
    class Config:
        from_attributes = True


# Aportes de Capital
from typing import Literal

class AporteCapitalBase(BaseModel):
    data: date
    valor: float
    tipo_aporte: Literal['dinheiro', 'bens', 'servicos', 'retirada']
    descricao: Optional[str] = None

class AporteCapitalCreate(AporteCapitalBase):
    pass

class AporteCapitalUpdate(BaseModel):
    data: Optional[date] = None
    valor: Optional[float] = None
    tipo_aporte: Optional[Literal['dinheiro', 'bens', 'servicos', 'retirada']] = None
    descricao: Optional[str] = None

class AporteCapitalResponse(AporteCapitalBase):
    id: int
    socio_id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class RelatorioIntegralizacao(BaseModel):
    socios: List[dict]
    total_geral: float

class AporteCapitalOldCreate(BaseModel):
    valor: float
    data: date
    forma: Literal['dinheiro', 'bens']


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
    cliente_id: Optional[int] = None
    data: date
    valor: float

class EntradaCreate(EntradaBase):
    socios: List[EntradaSocioCreate] = []

class Entrada(EntradaBase):
    id: int
    socios: List[EntradaSocio] = []
    cliente_rel: Optional[Cliente] = None
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


# ==================== SCHEMAS DE FERIADO ====================

class TipoFeriado(str, Enum):
    NACIONAL = "nacional"
    ESTADUAL = "estadual"
    MUNICIPAL = "municipal"

class FeriadoBase(BaseModel):
    data: date
    nome: str
    tipo: TipoFeriado
    uf: Optional[str] = None
    municipio_id: Optional[int] = None
    recorrente: bool = False

class FeriadoCreate(FeriadoBase):
    @field_validator('uf', 'municipio_id')
    @classmethod
    def validar_campos_condicionais(cls, v, info):
        values = info.data
        if 'tipo' in values:
            if values['tipo'] == TipoFeriado.ESTADUAL and info.field_name == 'uf' and not v:
                raise ValueError('UF é obrigatória para feriados estaduais')
            if values['tipo'] == TipoFeriado.MUNICIPAL and info.field_name == 'municipio_id' and not v:
                raise ValueError('Município é obrigatório para feriados municipais')
        return v

class FeriadoUpdate(BaseModel):
    data: Optional[date] = None
    nome: Optional[str] = None
    tipo: Optional[TipoFeriado] = None
    uf: Optional[str] = None
    municipio_id: Optional[int] = None
    recorrente: Optional[bool] = None

class FeriadoResponse(FeriadoBase):
    id: int
    municipio: Optional[MunicipioResponse] = None
    criado_por: Optional[int] = None
    criado_em: datetime
    
    class Config:
        from_attributes = True

class CalendarioDiaResponse(BaseModel):
    dia: int
    data: str  # ISO format
    dia_util: bool
    feriado: bool
    nome_feriado: Optional[str] = None
    fim_semana: bool


# ==================== SCHEMAS DE TAREFAS COM WORKFLOW ====================

class ClassificacaoIntimacao(str, Enum):
    NADA_A_FAZER = "Nada a fazer"
    INTIMACAO_AO_AUTOR = "Intimação ao autor"
    DECISAO_INTERLOCUTORIA = "Decisão Interlocutória"
    OUTRAS = "Outras"
    SENTENCA = "Sentença"

class TipoTarefaResponse(BaseModel):
    id: int
    nome: str
    descricao_padrao: Optional[str] = None
    
    class Config:
        from_attributes = True

class TipoAndamentoResponse(BaseModel):
    id: int
    nome: str
    descricao_padrao: Optional[str] = None
    
    class Config:
        from_attributes = True

# Corrigir TarefaBase para corresponder ao modelo
class TarefaBase(BaseModel):
    tipo_tarefa_id: int
    processo_id: Optional[int] = None
    descricao_complementar: Optional[str] = None
    responsavel_id: Optional[int] = None
    prazo_administrativo: Optional[date] = None
    prazo_fatal: Optional[date] = None
    status: str = "pendente"

class TarefaCreate(TarefaBase):
    """Schema para criação manual de tarefas via botão."""
    pass

class TarefaIntimacaoCreate(BaseModel):
    """Schema para criação de tarefa de análise de intimação."""
    processo_id: int
    conteudo_intimacao: str
    responsavel_id: int

class TarefaIntimacaoClassificar(BaseModel):
    """Schema para classificar uma intimação."""
    classificacao_intimacao: ClassificacaoIntimacao
    conteudo_decisao: Optional[str] = None
    criar_tarefa_derivada: bool = False
    tipo_tarefa_derivada_id: Optional[int] = None
    responsavel_derivado_id: Optional[int] = None
    prazo_fatal_derivada: Optional[date] = None  # Obrigatório para Petição/Recurso
    
    @field_validator('conteudo_decisao')
    @classmethod
    def validar_conteudo_decisao(cls, v, info):
        values = info.data
        if 'classificacao_intimacao' in values:
            classificacao = values['classificacao_intimacao']
            if classificacao in [ClassificacaoIntimacao.DECISAO_INTERLOCUTORIA, ClassificacaoIntimacao.SENTENCA]:
                if not v:
                    raise ValueError('Conteúdo da decisão é obrigatório para esta classificação')
        return v

class TarefaWorkflowAvancar(BaseModel):
    """Schema para avançar workflow de uma tarefa."""
    nova_etapa: str
    acao: str

class TarefaUpdate(BaseModel):
    """Schema para atualização geral de tarefa."""
    tipo_tarefa_id: Optional[int] = None
    descricao_complementar: Optional[str] = None
    responsavel_id: Optional[int] = None
    prazo_administrativo: Optional[date] = None
    prazo_fatal: Optional[date] = None
    status: Optional[str] = None
    etapa_workflow_atual: Optional[str] = None

class WorkflowHistoricoItem(BaseModel):
    etapa_anterior: str
    etapa_nova: str
    usuario_id: int
    usuario_nome: str
    timestamp: str
    acao: str

class TarefaResponse(TarefaBase):
    id: int
    etapa_workflow_atual: str
    workflow_historico: Optional[List[WorkflowHistoricoItem]] = None
    conteudo_intimacao: Optional[str] = None
    classificacao_intimacao: Optional[str] = None
    conteudo_decisao: Optional[str] = None
    tarefa_origem_id: Optional[int] = None
    criado_em: datetime
    atualizado_em: datetime
    tipo_tarefa: Optional[TipoTarefaResponse] = None
    responsavel: Optional[Usuario] = None
    
    class Config:
        from_attributes = True


# Alias para compatibilidade
Tarefa = TarefaResponse


class TarefaFiltros(BaseModel):
    """Schema para filtros avançados de tarefas."""
    tipo_tarefa_id: Optional[int] = None
    processo_id: Optional[int] = None
    cliente_id: Optional[int] = None
    classe: Optional[str] = None
    esfera_justica: Optional[str] = None
    municipio_id: Optional[int] = None
    uf: Optional[str] = None
    responsavel_id: Optional[int] = None
    status: Optional[str] = None
    prazo_vencido: bool = False
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None


# ==================== SCHEMAS DE ANDAMENTO CORRIGIDOS ====================

class AndamentoBase(BaseModel):
    processo_id: int
    tipo_andamento_id: int  # Corrigido para usar tipo
    descricao_complementar: Optional[str] = None
    data: Optional[date] = None
    criado_por: Optional[int] = None

class AndamentoCreate(AndamentoBase):
    pass

class AndamentoUpdate(BaseModel):
    tipo_andamento_id: Optional[int] = None
    descricao_complementar: Optional[str] = None
    data: Optional[date] = None

class AndamentoResponse(AndamentoBase):
    id: int
    criado_em: datetime
    tipo_andamento: Optional[TipoAndamentoResponse] = None
    
    class Config:
        from_attributes = True


# Alias para compatibilidade
Andamento = AndamentoResponse


# ==================== SCHEMAS DE ESTATÍSTICAS ====================

class EstatisticasPorTipo(BaseModel):
    tipo: str
    quantidade: int

class EstatisticasTarefas(BaseModel):
    total: int
    por_status: dict
    vencidas: int
    proximas_vencer: int
    por_tipo: List[EstatisticasPorTipo]

class MetricasResponsavel(BaseModel):
    responsavel: str
    responsavel_id: int
    total: int
    concluidas: int
    pendentes: int
    em_andamento: int
    taxa_conclusao: float

class TempoMedioPorTipo(BaseModel):
    tipo: str
    tempo_medio_dias: float
    quantidade_concluidas: int


# ==================== SCHEMAS PARA SISTEMA DE PROVISÕES ====================

class PagamentoProLaboreCreate(BaseModel):
    """Schema para registrar pagamento parcial de pró-labore"""
    mes: int
    ano: int
    valor: float
    data_pagamento: date
    observacao: Optional[str] = None

class PagamentoINSSCreate(BaseModel):
    """Schema para registrar pagamento de INSS (patronal + pessoal)"""
    mes: int
    ano: int
    valor: float
    data_pagamento: date
    observacao: Optional[str] = None

class PagamentoSimplesCreate(BaseModel):
    """Schema para registrar pagamento de Simples Nacional"""
    mes: int
    ano: int
    valor: float
    data_pagamento: date
    observacao: Optional[str] = None

class PagamentoLucroSocioCreate(BaseModel):
    """Schema para registrar saque de lucro de um sócio"""
    mes: int
    ano: int
    socio_id: int
    valor: float
    data_pagamento: date
    observacao: Optional[str] = None

class SaldoDisponivel(BaseModel):
    """Schema para resposta de saldos disponíveis"""
    previsto: float
    pago: float
    disponivel: float

class LucroSocioDisponivel(BaseModel):
    """Schema para lucro disponível de um sócio"""
    socio_id: int
    nome: str
    previsto: float
    pago: float
    disponivel: float

class SaldosDisponiveisMes(BaseModel):
    """Schema para resposta completa de saldos disponíveis do mês"""
    mes: int
    ano: int
    mes_referencia: str
    pro_labore: SaldoDisponivel
    inss: dict  # Contém previsto, patronal_previsto, pessoal_previsto, pago, disponivel
    simples: SaldoDisponivel
    fundo_reserva: dict  # Contém previsto
    lucros_por_socio: List[LucroSocioDisponivel]

class ProvisaoEntradaDetalhada(BaseModel):
    """Schema para exibir detalhes de uma provisão"""
    provisao_id: int
    entrada_id: int
    data: str
    cliente: str
    valor_entrada: float
    imposto_provisionado: float
    pro_labore_previsto: float
    inss_total_previsto: float
    fundo_reserva_previsto: float
    distribuicao_socios: List[dict]


# ==================== SCHEMAS DE PAGAMENTOS PENDENTES (SISTEMA SIMPLIFICADO) ====================

class PagamentoPendenteBase(BaseModel):
    tipo: str
    descricao: str
    valor: float
    mes_ref: int
    ano_ref: int
    socio_id: Optional[int] = None
    entrada_id: Optional[int] = None

class PagamentoPendenteCreate(PagamentoPendenteBase):
    pass

class PagamentoPendente(PagamentoPendenteBase):
    id: int
    confirmado: bool
    data_confirmacao: Optional[date] = None
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True

class ConfirmarPagamento(BaseModel):
    data_confirmacao: date


# ==================== SCHEMAS DE ATIVOS IMOBILIZADOS ====================

class AtivoImobilizadoBase(BaseModel):
    descricao: str
    categoria: str
    valor_aquisicao: float
    data_aquisicao: date
    elegivel_depreciacao: bool = True
    conta_ativo_id: Optional[int] = None
    observacoes: Optional[str] = None

class AtivoImobilizadoCreate(AtivoImobilizadoBase):
    criado_por: Optional[str] = None

class AtivoImobilizadoUpdate(BaseModel):
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    valor_aquisicao: Optional[float] = None
    data_aquisicao: Optional[date] = None
    elegivel_depreciacao: Optional[bool] = None
    conta_ativo_id: Optional[int] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None

class AtivoImobilizadoResponse(AtivoImobilizadoBase):
    id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
    criado_por: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== SCHEMAS DE SAQUES DE FUNDOS ====================

class SaqueFundoBase(BaseModel):
    data: date
    valor: float
    tipo_fundo: Literal['reserva', 'investimento']
    beneficiario_id: int
    motivo: str
    comprovante_path: Optional[str] = None

class SaqueFundoCreate(SaqueFundoBase):
    criado_por: Optional[str] = None

class SaqueFundoResponse(SaqueFundoBase):
    id: int
    lancamento_id: Optional[int] = None
    criado_em: datetime
    criado_por: Optional[str] = None

    class Config:
        from_attributes = True
