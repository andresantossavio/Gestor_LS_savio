# backend/config_data.py

UFS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO"
]

TIPOS_PROCESSO = ["Judicial", "Extrajudicial", "Arbitral", "Administrativo"]

CATEGORIAS_PROCESSO = ["Comum", "Originário"]

TRIBUNAIS = ["STF", "STJ", "TRF", "TRT", "TRE", "TJ", "TRM"]

ESFERAS_JUSTICA = [
    "Justiça Estadual",
    "Justiça Federal",
    "Justiça Trabalhista",
    "Justiça Eleitoral",
    "Justiça Militar"
]

# Baseado na lógica do frontend
CLASSES_JURIDICAS = {
    "Cível": ["Comum", "Consumidor", "Família", "Inventário"],
    "Criminal": ["Ação Penal Pública Incondicionada", "Ação Penal Pública Condicionada", "Ação Penal Privada"],
    "Trabalhista": [],
    "Tributário": [],
    "Previdenciário": [],
    "Empresarial": ["Falência e Recuperação", "Societário"],
    "Eleitoral": ["Eleitoral Cível", "Eleitoral Criminal"],
    "Administrativo": [],
    "Constitucional": []
}

# Ritos processuais (apenas para tipo Judicial)
RITOS = {
    "Cível": ["Ordinário", "Juizado Especial Cível", "Inventário"],
    "Criminal": [
        # Ritos Comuns
        "Ordinário",
        "Sumário",
        "Sumaríssimo",
        # Ritos Especiais
        "Tribunal do Júri",
        "Lei de Drogas",
        "Juizado Especial Criminal",
        "Funcionário Público",
        "Eleitoral",
        "Militar",
        "Propriedade Imaterial",
        "Maria da Penha",
        "Terrorismo / Segurança Nacional"
    ],
    "Constitucional": [
        "Mandado de segurança",
        "Habeas Data"
    ],
    "Administrativo": [
        "Ação popular",
        "Ação Civil Pública",
        "Improbidade",
        "Desapropriação",
        "Registros Públicos"
    ],
    "Tributário": [
        "Comum",
        "Execução Fiscal"
    ],
    "Trabalhista": ["Comum"],
    "Previdenciário": ["Comum"],
    "Empresarial": ["Comum"],
    "Eleitoral": ["Comum"]
}

# ==================== CONFIGURAÇÕES DE DEPRECIAÇÃO ====================

# Taxas de depreciação padrão Brasil (anuais)
# Fonte: Receita Federal - Tabela de vida útil e taxa de depreciação
DEPRECIACAO_PADRAO_BR = {
    'equipamentos': 0.20,      # 20% a.a. (5 anos)
    'moveis': 0.10,            # 10% a.a. (10 anos)
    'veiculos': 0.20,          # 20% a.a. (5 anos)
    'computadores': 0.20,      # 20% a.a. (5 anos)
    'imoveis': 0.04,           # 4% a.a. (25 anos)
    'maquinas': 0.10,          # 10% a.a. (10 anos)
    'ferramentas': 0.15,       # 15% a.a. (6-7 anos)
    'instalacoes': 0.10,       # 10% a.a. (10 anos)
    'imobilizado_geral': 0.10  # 10% a.a. (fallback)
}

# Códigos de contas para depreciação
CONTAS_DEPRECIACAO = {
    'despesa': '5.2.9',        # Despesa de Depreciação
    'redutora': '1.2.9'        # Depreciação Acumulada (contra-ativo)
}

# Mapeamento de palavras-chave para categorias de ativos
CATEGORIAS_ATIVOS = {
    'equipamentos': ['equipamento', 'aparelho', 'instrumento'],
    'moveis': ['movel', 'móvel', 'mesa', 'cadeira', 'armario', 'armário', 'estante'],
    'veiculos': ['veiculo', 'veículo', 'carro', 'moto', 'caminhao', 'caminhão'],
    'computadores': ['computador', 'notebook', 'servidor', 'desktop', 'laptop', 'pc'],
    'imoveis': ['imovel', 'imóvel', 'sala', 'edificio', 'edifício', 'construcao', 'construção'],
    'maquinas': ['maquina', 'máquina', 'torno', 'prensa'],
    'ferramentas': ['ferramenta', 'chave', 'martelo', 'furadeira'],
    'instalacoes': ['instalacao', 'instalação', 'ar-condicionado', 'elétrica', 'hidraulica', 'hidráulica']
}

# Configurações de alertas
ALERTAS_CONFIG = {
    'saldo_minimo_caixa': 1000.00,      # Alertar se caixa < R$ 1.000
    'saldo_minimo_fundo': 5000.00,      # Alertar se fundo < R$ 5.000
    'percentual_uso_fundo': 0.50        # Alertar se usar > 50% do fundo
}
