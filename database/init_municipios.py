"""
Script para popular a tabela de municípios com todos os municípios brasileiros.
Fonte: API do IBGE - 5570 municípios
"""
import sys
from pathlib import Path
import requests

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from database.database import SessionLocal, engine
from database.models import Base, Municipio


def fetch_municipios_ibge():
    """
    Busca todos os municípios brasileiros da API do IBGE.
    
    Returns:
        list: Lista de dicionários com dados dos municípios
    """
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    
    print("🌐 Buscando municípios da API do IBGE...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        municipios_raw = response.json()
        print(f"✅ {len(municipios_raw)} municípios obtidos da API do IBGE")
        
        # Converte para o formato do banco de dados
        municipios_formatados = []
        
        for mun in municipios_raw:
            try:
                municipio = {
                    "codigo_ibge": str(mun["id"]),
                    "nome": mun["nome"],
                    "uf": mun["microrregiao"]["mesorregiao"]["UF"]["sigla"]
                }
                municipios_formatados.append(municipio)
            except (KeyError, TypeError) as e:
                print(f"⚠️  Município com dados incompletos: {mun.get('nome', 'desconhecido')} - {e}")
                continue
        
        # Estatísticas por UF
        ufs = {}
        for m in municipios_formatados:
            uf = m["uf"]
            ufs[uf] = ufs.get(uf, 0) + 1
        
        print(f"\n📊 Municípios por UF obtidos:")
        for uf in sorted(ufs.keys()):
            print(f"   {uf}: {ufs[uf]} municípios")
        
        return municipios_formatados
        
    except requests.RequestException as e:
        print(f"❌ Erro ao buscar dados da API do IBGE: {e}")
        return []


def popular_municipios(db: Session):
    """
    Popula a tabela de municípios com dados do IBGE.
    """
    print("\n" + "=" * 60)
    print("IMPORTAÇÃO DE MUNICÍPIOS")
    print("=" * 60 + "\n")
    
    # Busca dados da API
    municipios = fetch_municipios_ibge()
    
    if not municipios:
        print("❌ Nenhum município obtido da API. Encerrando.")
        return
    
    print(f"\n💾 Iniciando inserção de {len(municipios)} municípios no banco de dados...")
    
    # Verifica se já existem municípios
    count_existente = db.query(Municipio).count()
    if count_existente > 0:
        print(f"⚠️  Já existem {count_existente} municípios cadastrados.")
        resposta = input("Deseja continuar e adicionar apenas os novos? (s/n): ")
        if resposta.lower() != 's':
            print("Operação cancelada.")
            return
    
    # Insere municípios em lote
    municipios_novos = []
    municipios_duplicados = 0
    
    for mun_data in municipios:
        # Verifica se já existe pelo nome e UF (devido à constraint UNIQUE)
        existe = db.query(Municipio).filter(
            Municipio.nome == mun_data["nome"],
            Municipio.uf == mun_data["uf"]
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
    print("\n📍 Municípios por UF no banco:")
    from sqlalchemy import func
    stats = db.query(
        Municipio.uf,
        func.count(Municipio.id).label('count')
    ).group_by(Municipio.uf).order_by(Municipio.uf).all()
    
    for uf, count in stats:
        print(f"   {uf}: {count} municípios")
    
    # Destaque para RS
    total_rs = db.query(Municipio).filter(Municipio.uf == "RS").count()
    print(f"\n🎯 Total de municípios do RS: {total_rs}")


def main():
    """Função principal para executar o script."""
    print("=" * 60)
    print("INICIALIZAÇÃO DA BASE DE MUNICÍPIOS BRASILEIROS - IBGE")
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


if __name__ == "__main__":
    main()
