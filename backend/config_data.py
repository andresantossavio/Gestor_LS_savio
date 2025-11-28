# backend/config_data.py

UFS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO"
]

TIPOS_PROCESSO = ["Judicial", "Administrativo"]

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
    "Cível": ["Família", "Contratos", "Consumidor", "Imobiliário"],
    "Criminal": [],
    "Trabalhista": [],
    "Tributário": [],
    "Previdenciário": [],
    "Empresarial": ["Falência e Recuperação", "Societário"],
    "Eleitoral": ["Eleitoral Cível", "Eleitoral Criminal"]
}
