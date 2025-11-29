"""
Script para inicializar TODOS os dados necessários do sistema
Executa os scripts de inicialização em sequência
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from database.database import SessionLocal, engine, Base
from database.models import Municipio, Feriado, TipoTarefa, WorkflowTemplate
from datetime import date, datetime
import json

def criar_tipos_tarefa(db):
    """Cria os tipos de tarefa padrão"""
    print("\n=== CRIANDO TIPOS DE TAREFA ===")
    
    tipos = [
        {"nome": "Intimação", "descricao_padrao": "Análise de intimação recebida"},
        {"nome": "Petição", "descricao_padrao": "Elaboração e protocolo de petição"},
        {"nome": "Recurso", "descricao_padrao": "Elaboração e protocolo de recurso"},
        {"nome": "Audiência", "descricao_padrao": "Comparecimento em audiência"},
        {"nome": "Cumprimento", "descricao_padrao": "Cumprimento de determinação judicial"},
        {"nome": "Prazo Fatal", "descricao_padrao": "Prazo fatal a cumprir"},
        {"nome": "Outro", "descricao_padrao": "Tarefa genérica"}
    ]
    
    for tipo_data in tipos:
        tipo_existente = db.query(TipoTarefa).filter(TipoTarefa.nome == tipo_data["nome"]).first()
        if not tipo_existente:
            tipo = TipoTarefa(**tipo_data)
            db.add(tipo)
            print(f"  ✓ Criado: {tipo_data['nome']}")
        else:
            print(f"  - Já existe: {tipo_data['nome']}")
    
    db.commit()
    print("✅ Tipos de tarefa criados com sucesso!")


def criar_feriados_nacionais(db):
    """Cria feriados nacionais de 2024 e 2025"""
    print("\n=== CRIANDO FERIADOS NACIONAIS ===")
    
    feriados = [
        # 2024
        {"data": date(2024, 1, 1), "nome": "Ano Novo", "tipo": "nacional", "recorrente": True},
        {"data": date(2024, 2, 13), "nome": "Carnaval", "tipo": "nacional", "recorrente": False},
        {"data": date(2024, 3, 29), "nome": "Sexta-feira Santa", "tipo": "nacional", "recorrente": False},
        {"data": date(2024, 4, 21), "nome": "Tiradentes", "tipo": "nacional", "recorrente": True},
        {"data": date(2024, 5, 1), "nome": "Dia do Trabalho", "tipo": "nacional", "recorrente": True},
        {"data": date(2024, 5, 30), "nome": "Corpus Christi", "tipo": "nacional", "recorrente": False},
        {"data": date(2024, 9, 7), "nome": "Independência do Brasil", "tipo": "nacional", "recorrente": True},
        {"data": date(2024, 10, 12), "nome": "Nossa Senhora Aparecida", "tipo": "nacional", "recorrente": True},
        {"data": date(2024, 11, 2), "nome": "Finados", "tipo": "nacional", "recorrente": True},
        {"data": date(2024, 11, 15), "nome": "Proclamação da República", "tipo": "nacional", "recorrente": True},
        {"data": date(2024, 11, 20), "nome": "Consciência Negra", "tipo": "nacional", "recorrente": True},
        {"data": date(2024, 12, 25), "nome": "Natal", "tipo": "nacional", "recorrente": True},
        
        # 2025
        {"data": date(2025, 1, 1), "nome": "Ano Novo", "tipo": "nacional", "recorrente": True},
        {"data": date(2025, 3, 4), "nome": "Carnaval", "tipo": "nacional", "recorrente": False},
        {"data": date(2025, 4, 18), "nome": "Sexta-feira Santa", "tipo": "nacional", "recorrente": False},
        {"data": date(2025, 4, 21), "nome": "Tiradentes", "tipo": "nacional", "recorrente": True},
        {"data": date(2025, 5, 1), "nome": "Dia do Trabalho", "tipo": "nacional", "recorrente": True},
        {"data": date(2025, 6, 19), "nome": "Corpus Christi", "tipo": "nacional", "recorrente": False},
        {"data": date(2025, 9, 7), "nome": "Independência do Brasil", "tipo": "nacional", "recorrente": True},
        {"data": date(2025, 10, 12), "nome": "Nossa Senhora Aparecida", "tipo": "nacional", "recorrente": True},
        {"data": date(2025, 11, 2), "nome": "Finados", "tipo": "nacional", "recorrente": True},
        {"data": date(2025, 11, 15), "nome": "Proclamação da República", "tipo": "nacional", "recorrente": True},
        {"data": date(2025, 11, 20), "nome": "Consciência Negra", "tipo": "nacional", "recorrente": True},
        {"data": date(2025, 12, 25), "nome": "Natal", "tipo": "nacional", "recorrente": True},
        
        # 2026
        {"data": date(2026, 1, 1), "nome": "Ano Novo", "tipo": "nacional", "recorrente": True},
        {"data": date(2026, 4, 21), "nome": "Tiradentes", "tipo": "nacional", "recorrente": True},
        {"data": date(2026, 5, 1), "nome": "Dia do Trabalho", "tipo": "nacional", "recorrente": True},
        {"data": date(2026, 9, 7), "nome": "Independência do Brasil", "tipo": "nacional", "recorrente": True},
        {"data": date(2026, 10, 12), "nome": "Nossa Senhora Aparecida", "tipo": "nacional", "recorrente": True},
        {"data": date(2026, 11, 2), "nome": "Finados", "tipo": "nacional", "recorrente": True},
        {"data": date(2026, 11, 15), "nome": "Proclamação da República", "tipo": "nacional", "recorrente": True},
        {"data": date(2026, 11, 20), "nome": "Consciência Negra", "tipo": "nacional", "recorrente": True},
        {"data": date(2026, 12, 25), "nome": "Natal", "tipo": "nacional", "recorrente": True},
    ]
    
    for feriado_data in feriados:
        feriado_existente = db.query(Feriado).filter(
            Feriado.data == feriado_data["data"],
            Feriado.tipo == "nacional"
        ).first()
        
        if not feriado_existente:
            feriado = Feriado(
                **feriado_data,
                criado_em=datetime.now()
            )
            db.add(feriado)
            print(f"  ✓ {feriado_data['data']}: {feriado_data['nome']}")
        else:
            print(f"  - Já existe: {feriado_data['nome']} em {feriado_data['data']}")
    
    db.commit()
    print(f"✅ {len(feriados)} feriados nacionais criados!")


def criar_workflows_intimacao(db):
    """Cria o template de workflow para intimação"""
    print("\n=== CRIANDO WORKFLOW DE INTIMAÇÃO ===")
    
    # Busca o tipo de tarefa "Intimação"
    tipo_intimacao = db.query(TipoTarefa).filter(TipoTarefa.nome == "Intimação").first()
    if not tipo_intimacao:
        print("❌ Tipo de tarefa 'Intimação' não encontrado!")
        return
    
    # Verifica se já existe
    workflow_existente = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tipo_tarefa_id == tipo_intimacao.id
    ).first()
    
    if workflow_existente:
        print("  - Workflow já existe")
        return
    
    # Define as etapas do workflow
    etapas = [
        {
            "ordem": 1,
            "nome": "Recebimento",
            "descricao": "Intimação recebida, aguardando análise",
            "prazo_dias": None
        },
        {
            "ordem": 2,
            "nome": "Análise",
            "descricao": "Em análise pelo responsável",
            "prazo_dias": 2
        },
        {
            "ordem": 3,
            "nome": "Classificação",
            "descricao": "Intimação classificada, verificando necessidade de ação",
            "prazo_dias": 1
        },
        {
            "ordem": 4,
            "nome": "Ação Necessária",
            "descricao": "Ação necessária (Petição/Recurso) em andamento",
            "prazo_dias": None
        },
        {
            "ordem": 5,
            "nome": "Concluída",
            "descricao": "Intimação concluída",
            "prazo_dias": None
        }
    ]
    
    workflow = WorkflowTemplate(
        tipo_tarefa_id=tipo_intimacao.id,
        etapas=etapas
    )
    db.add(workflow)
    db.commit()
    
    print(f"  ✓ Workflow criado com {len(etapas)} etapas")
    for etapa in etapas:
        print(f"    {etapa['ordem']}. {etapa['nome']}")
    
    print("✅ Workflow de intimação criado com sucesso!")


def criar_alguns_municipios(db):
    """Cria alguns municípios para teste (capitais)"""
    print("\n=== CRIANDO MUNICÍPIOS DE TESTE (CAPITAIS) ===")
    
    capitais = [
        {"nome": "Rio Branco", "uf": "AC", "codigo_ibge": "1200401"},
        {"nome": "Maceió", "uf": "AL", "codigo_ibge": "2704302"},
        {"nome": "Macapá", "uf": "AP", "codigo_ibge": "1600303"},
        {"nome": "Manaus", "uf": "AM", "codigo_ibge": "1302603"},
        {"nome": "Salvador", "uf": "BA", "codigo_ibge": "2927408"},
        {"nome": "Fortaleza", "uf": "CE", "codigo_ibge": "2304400"},
        {"nome": "Brasília", "uf": "DF", "codigo_ibge": "5300108"},
        {"nome": "Vitória", "uf": "ES", "codigo_ibge": "3205309"},
        {"nome": "Goiânia", "uf": "GO", "codigo_ibge": "5208707"},
        {"nome": "São Luís", "uf": "MA", "codigo_ibge": "2111300"},
        {"nome": "Cuiabá", "uf": "MT", "codigo_ibge": "5103403"},
        {"nome": "Campo Grande", "uf": "MS", "codigo_ibge": "5002704"},
        {"nome": "Belo Horizonte", "uf": "MG", "codigo_ibge": "3106200"},
        {"nome": "Belém", "uf": "PA", "codigo_ibge": "1501402"},
        {"nome": "João Pessoa", "uf": "PB", "codigo_ibge": "2507507"},
        {"nome": "Curitiba", "uf": "PR", "codigo_ibge": "4106902"},
        {"nome": "Recife", "uf": "PE", "codigo_ibge": "2611606"},
        {"nome": "Teresina", "uf": "PI", "codigo_ibge": "2211001"},
        {"nome": "Rio de Janeiro", "uf": "RJ", "codigo_ibge": "3304557"},
        {"nome": "Natal", "uf": "RN", "codigo_ibge": "2408102"},
        {"nome": "Porto Alegre", "uf": "RS", "codigo_ibge": "4314902"},
        {"nome": "Porto Velho", "uf": "RO", "codigo_ibge": "1100205"},
        {"nome": "Boa Vista", "uf": "RR", "codigo_ibge": "1400100"},
        {"nome": "Florianópolis", "uf": "SC", "codigo_ibge": "4205407"},
        {"nome": "São Paulo", "uf": "SP", "codigo_ibge": "3550308"},
        {"nome": "Aracaju", "uf": "SE", "codigo_ibge": "2800308"},
        {"nome": "Palmas", "uf": "TO", "codigo_ibge": "1721000"},
    ]
    
    for mun_data in capitais:
        mun_existente = db.query(Municipio).filter(
            Municipio.codigo_ibge == mun_data["codigo_ibge"]
        ).first()
        
        if not mun_existente:
            municipio = Municipio(**mun_data)
            db.add(municipio)
            print(f"  ✓ {mun_data['nome']}/{mun_data['uf']}")
        else:
            print(f"  - Já existe: {mun_data['nome']}/{mun_data['uf']}")
    
    db.commit()
    print(f"✅ {len(capitais)} capitais criadas!")


def main():
    print("=" * 70)
    print("INICIALIZAÇÃO COMPLETA DO SISTEMA")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # 1. Criar tipos de tarefa
        criar_tipos_tarefa(db)
        
        # 2. Criar feriados nacionais
        criar_feriados_nacionais(db)
        
        # 3. Criar workflows
        criar_workflows_intimacao(db)
        
        # 4. Criar municípios de teste (capitais)
        criar_alguns_municipios(db)
        
        print("\n" + "=" * 70)
        print("✅ INICIALIZAÇÃO COMPLETA COM SUCESSO!")
        print("=" * 70)
        
        # Resumo
        print("\nRESUMO:")
        print(f"  - Tipos de Tarefa: {db.query(TipoTarefa).count()}")
        print(f"  - Feriados: {db.query(Feriado).count()}")
        print(f"  - Workflows: {db.query(WorkflowTemplate).count()}")
        print(f"  - Municípios: {db.query(Municipio).count()}")
        
    except Exception as e:
        print(f"\n❌ Erro durante inicialização: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
