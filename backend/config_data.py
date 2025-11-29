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
