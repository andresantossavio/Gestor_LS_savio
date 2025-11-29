"""
Script para popular a tabela de municípios com todos os municípios brasileiros.
Fonte: IBGE - 5570 municípios
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from database.database import SessionLocal, engine
from database.models import Base, Municipio

# Lista completa de municípios brasileiros (amostra - em produção usar arquivo JSON/CSV completo)
# Este é um subset para exemplo. Em produção, carregar de arquivo CSV do IBGE
MUNICIPIOS_BRASIL = [
    # Acre
    {"codigo_ibge": "1200013", "nome": "Acrelândia", "uf": "AC"},
    {"codigo_ibge": "1200054", "nome": "Assis Brasil", "uf": "AC"},
    {"codigo_ibge": "1200104", "nome": "Brasiléia", "uf": "AC"},
    {"codigo_ibge": "1200138", "nome": "Bujari", "uf": "AC"},
    {"codigo_ibge": "1200179", "nome": "Capixaba", "uf": "AC"},
    {"codigo_ibge": "1200203", "nome": "Cruzeiro do Sul", "uf": "AC"},
    {"codigo_ibge": "1200252", "nome": "Epitaciolândia", "uf": "AC"},
    {"codigo_ibge": "1200302", "nome": "Feijó", "uf": "AC"},
    {"codigo_ibge": "1200328", "nome": "Jordão", "uf": "AC"},
    {"codigo_ibge": "1200336", "nome": "Mâncio Lima", "uf": "AC"},
    {"codigo_ibge": "1200344", "nome": "Manoel Urbano", "uf": "AC"},
    {"codigo_ibge": "1200351", "nome": "Marechal Thaumaturgo", "uf": "AC"},
    {"codigo_ibge": "1200385", "nome": "Plácido de Castro", "uf": "AC"},
    {"codigo_ibge": "1200393", "nome": "Porto Acre", "uf": "AC"},
    {"codigo_ibge": "1200401", "nome": "Porto Walter", "uf": "AC"},
    {"codigo_ibge": "1200427", "nome": "Rio Branco", "uf": "AC"},
    {"codigo_ibge": "1200435", "nome": "Rodrigues Alves", "uf": "AC"},
    {"codigo_ibge": "1200450", "nome": "Santa Rosa do Purus", "uf": "AC"},
    {"codigo_ibge": "1200500", "nome": "Sena Madureira", "uf": "AC"},
    {"codigo_ibge": "1200542", "nome": "Senador Guiomard", "uf": "AC"},
    {"codigo_ibge": "1200559", "nome": "Tarauacá", "uf": "AC"},
    {"codigo_ibge": "1200609", "nome": "Xapuri", "uf": "AC"},
    
    # Principais capitais e cidades grandes (adicionar mais conforme necessário)
    {"codigo_ibge": "3550308", "nome": "São Paulo", "uf": "SP"},
    {"codigo_ibge": "3304557", "nome": "Rio de Janeiro", "uf": "RJ"},
    {"codigo_ibge": "3106200", "nome": "Belo Horizonte", "uf": "MG"},
    {"codigo_ibge": "4106902", "nome": "Curitiba", "uf": "PR"},
    {"codigo_ibge": "4314902", "nome": "Porto Alegre", "uf": "RS"},
    {"codigo_ibge": "2927408", "nome": "Salvador", "uf": "BA"},
    {"codigo_ibge": "2304400", "nome": "Fortaleza", "uf": "CE"},
    {"codigo_ibge": "5300108", "nome": "Brasília", "uf": "DF"},
    {"codigo_ibge": "1302603", "nome": "Manaus", "uf": "AM"},
    {"codigo_ibge": "2611606", "nome": "Recife", "uf": "PE"},
    {"codigo_ibge": "5208707", "nome": "Goiânia", "uf": "GO"},
    {"codigo_ibge": "1501402", "nome": "Belém", "uf": "PA"},
    {"codigo_ibge": "2111300", "nome": "São Luís", "uf": "MA"},
    {"codigo_ibge": "2704302", "nome": "Maceió", "uf": "AL"},
    {"codigo_ibge": "2507507", "nome": "João Pessoa", "uf": "PB"},
    {"codigo_ibge": "2800308", "nome": "Aracaju", "uf": "SE"},
    {"codigo_ibge": "2211001", "nome": "Teresina", "uf": "PI"},
    {"codigo_ibge": "5103403", "nome": "Cuiabá", "uf": "MT"},
    {"codigo_ibge": "2408102", "nome": "Natal", "uf": "RN"},
    {"codigo_ibge": "1100205", "nome": "Porto Velho", "uf": "RO"},
    {"codigo_ibge": "1400100", "nome": "Boa Vista", "uf": "RR"},
    {"codigo_ibge": "1600303", "nome": "Macapá", "uf": "AP"},
    {"codigo_ibge": "1721000", "nome": "Palmas", "uf": "TO"},
    {"codigo_ibge": "5002704", "nome": "Campo Grande", "uf": "MS"},
    {"codigo_ibge": "1200401", "nome": "Rio Branco", "uf": "AC"},
]


def popular_municipios(db: Session):
    """
    Popula a tabela de municípios com dados do IBGE.
    """
    print("Iniciando população da tabela de municípios...")
    
    # Verifica se já existem municípios
    count_existente = db.query(Municipio).count()
    if count_existente > 0:
        print(f"⚠️  Já existem {count_existente} municípios cadastrados.")
        resposta = input("Deseja continuar e adicionar os novos? (s/n): ")
        if resposta.lower() != 's':
            print("Operação cancelada.")
            return
    
    # Insere municípios em lote
    municipios_novos = []
    municipios_duplicados = 0
    
    for mun_data in MUNICIPIOS_BRASIL:
        # Verifica se já existe
        existe = db.query(Municipio).filter(
            Municipio.codigo_ibge == mun_data["codigo_ibge"]
        ).first()
        
        if not existe:
            municipios_novos.append(mun_data)
        else:
            municipios_duplicados += 1
    
    if municipios_novos:
        try:
            db.bulk_insert_mappings(Municipio, municipios_novos)
            db.commit()
            print(f"✅ {len(municipios_novos)} municípios inseridos com sucesso!")
        except Exception as e:
            db.rollback()
            print(f"❌ Erro ao inserir municípios: {e}")
            raise
    else:
        print("ℹ️  Nenhum município novo para inserir.")
    
    if municipios_duplicados > 0:
        print(f"ℹ️  {municipios_duplicados} municípios já existiam no banco.")
    
    # Estatísticas finais
    total = db.query(Municipio).count()
    print(f"\n📊 Total de municípios no banco: {total}")
    
    # Contagem por UF
    print("\n📍 Municípios por UF:")
    from sqlalchemy import func
    stats = db.query(
        Municipio.uf,
        func.count(Municipio.id).label('count')
    ).group_by(Municipio.uf).order_by(Municipio.uf).all()
    
    for uf, count in stats:
        print(f"   {uf}: {count} municípios")


def main():
    """Função principal para executar o script."""
    print("=" * 60)
    print("INICIALIZAÇÃO DA BASE DE MUNICÍPIOS BRASILEIROS")
    print("=" * 60)
    print()
    
    # Cria as tabelas se não existirem
    print("Verificando estrutura do banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Estrutura verificada.")
    print()
    
    # Cria sessão e popula
    db = SessionLocal()
    try:
        popular_municipios(db)
    finally:
        db.close()
    
    print()
    print("=" * 60)
    print("INICIALIZAÇÃO CONCLUÍDA")
    print("=" * 60)
    print()
    print("⚠️  IMPORTANTE: Este script contém apenas uma amostra de municípios.")
    print("   Para produção, importe o arquivo completo do IBGE com 5570 municípios.")
    print("   Arquivo pode ser obtido em: https://servicodados.ibge.gov.br/api/v1/localidades/municipios")


if __name__ == "__main__":
    main()
