"""
Script para popular feriados nacionais brasileiros.
Inclui feriados fixos e móveis (Carnaval, Páscoa, Corpus Christi).
"""
import sys
from pathlib import Path
from datetime import date, timedelta
from typing import List, Tuple

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from database.database import SessionLocal, engine
from database.models import Base, Feriado


def calcular_pascoa(ano: int) -> date:
    """
    Calcula a data da Páscoa usando o algoritmo de Meeus/Jones/Butcher.
    
    Args:
        ano: Ano para calcular a Páscoa
    
    Returns:
        Data da Páscoa
    """
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    
    return date(ano, mes, dia)


def calcular_feriados_moveis(ano: int) -> List[Tuple[date, str]]:
    """
    Calcula feriados móveis brasileiros para um ano específico.
    
    Args:
        ano: Ano para calcular os feriados
    
    Returns:
        Lista de tuplas (data, nome_feriado)
    """
    pascoa = calcular_pascoa(ano)
    
    feriados = []
    
    # Carnaval (47 dias antes da Páscoa - terça-feira)
    carnaval = pascoa - timedelta(days=47)
    feriados.append((carnaval, "Carnaval"))
    
    # Segunda de Carnaval (48 dias antes da Páscoa)
    segunda_carnaval = pascoa - timedelta(days=48)
    feriados.append((segunda_carnaval, "Segunda-feira de Carnaval"))
    
    # Sexta-feira Santa (2 dias antes da Páscoa)
    sexta_santa = pascoa - timedelta(days=2)
    feriados.append((sexta_santa, "Sexta-feira Santa"))
    
    # Corpus Christi (60 dias depois da Páscoa)
    corpus_christi = pascoa + timedelta(days=60)
    feriados.append((corpus_christi, "Corpus Christi"))
    
    return feriados


def obter_feriados_fixos_nacionais(ano: int) -> List[Tuple[date, str, bool]]:
    """
    Retorna lista de feriados nacionais fixos.
    
    Args:
        ano: Ano dos feriados
    
    Returns:
        Lista de tuplas (data, nome, recorrente)
    """
    return [
        (date(ano, 1, 1), "Ano Novo", True),
        (date(ano, 4, 21), "Tiradentes", True),
        (date(ano, 5, 1), "Dia do Trabalho", True),
        (date(ano, 9, 7), "Independência do Brasil", True),
        (date(ano, 10, 12), "Nossa Senhora Aparecida", True),
        (date(ano, 11, 2), "Finados", True),
        (date(ano, 11, 15), "Proclamação da República", True),
        (date(ano, 11, 20), "Dia da Consciência Negra", True),  # Feriado nacional desde 2024
        (date(ano, 12, 25), "Natal", True),
    ]


def popular_feriados_nacionais(db: Session, anos: List[int] = None):
    """
    Popula feriados nacionais para os anos especificados.
    
    Args:
        db: Sessão do banco de dados
        anos: Lista de anos (padrão: ano atual + próximos 2 anos)
    """
    if anos is None:
        ano_atual = date.today().year
        anos = [ano_atual, ano_atual + 1, ano_atual + 2]
    
    print(f"Populando feriados nacionais para os anos: {', '.join(map(str, anos))}")
    
    total_inseridos = 0
    total_existentes = 0
    
    for ano in anos:
        print(f"\n  Processando ano {ano}...")
        
        # Feriados fixos
        feriados_fixos = obter_feriados_fixos_nacionais(ano)
        for data_feriado, nome, recorrente in feriados_fixos:
            # Verifica se já existe
            existe = db.query(Feriado).filter(
                Feriado.data == data_feriado,
                Feriado.tipo == "nacional",
                Feriado.nome == nome
            ).first()
            
            if not existe:
                feriado = Feriado(
                    data=data_feriado,
                    nome=nome,
                    tipo="nacional",
                    recorrente=recorrente
                )
                db.add(feriado)
                total_inseridos += 1
            else:
                total_existentes += 1
        
        # Feriados móveis
        feriados_moveis = calcular_feriados_moveis(ano)
        for data_feriado, nome in feriados_moveis:
            # Verifica se já existe
            existe = db.query(Feriado).filter(
                Feriado.data == data_feriado,
                Feriado.tipo == "nacional",
                Feriado.nome == nome
            ).first()
            
            if not existe:
                feriado = Feriado(
                    data=data_feriado,
                    nome=nome,
                    tipo="nacional",
                    recorrente=True  # Móveis também são recorrentes
                )
                db.add(feriado)
                total_inseridos += 1
            else:
                total_existentes += 1
    
    try:
        db.commit()
        print(f"\n✅ {total_inseridos} feriados inseridos com sucesso!")
        if total_existentes > 0:
            print(f"ℹ️  {total_existentes} feriados já existiam no banco.")
    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro ao inserir feriados: {e}")
        raise


def listar_feriados_ano(db: Session, ano: int):
    """Lista todos os feriados nacionais de um ano."""
    feriados = db.query(Feriado).filter(
        Feriado.tipo == "nacional",
        Feriado.data >= date(ano, 1, 1),
        Feriado.data <= date(ano, 12, 31)
    ).order_by(Feriado.data).all()
    
    if feriados:
        print(f"\n📅 Feriados Nacionais de {ano}:")
        print("   " + "-" * 60)
        for f in feriados:
            dia_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"][f.data.weekday()]
            print(f"   {f.data.strftime('%d/%m/%Y')} ({dia_semana}) - {f.nome}")
        print("   " + "-" * 60)
    else:
        print(f"\nℹ️  Nenhum feriado encontrado para {ano}.")


def main():
    """Função principal para executar o script."""
    print("=" * 60)
    print("INICIALIZAÇÃO DE FERIADOS NACIONAIS")
    print("=" * 60)
    print()
    
    # Cria as tabelas se não existirem
    print("Verificando estrutura do banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Estrutura verificada.")
    print()
    
    # Anos para popular
    ano_atual = date.today().year
    anos = [ano_atual - 1, ano_atual, ano_atual + 1, ano_atual + 2]
    
    # Cria sessão e popula
    db = SessionLocal()
    try:
        popular_feriados_nacionais(db, anos)
        
        # Lista feriados do ano atual como exemplo
        print()
        listar_feriados_ano(db, ano_atual)
        
    finally:
        db.close()
    
    print()
    print("=" * 60)
    print("INICIALIZAÇÃO CONCLUÍDA")
    print("=" * 60)
    print()
    print("ℹ️  Para adicionar feriados estaduais e municipais,")
    print("   use a interface de Gestão de Feriados no sistema.")


if __name__ == "__main__":
    main()
