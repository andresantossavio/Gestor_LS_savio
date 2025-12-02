"""
Script de Migração: Geração de Pagamentos Pendentes Retroativos

Este script:
1. Identifica todos os meses com entradas no sistema
2. Para cada mês não consolidado:
   - Calcula DRE em tempo real
   - Gera pagamentos pendentes (SIMPLES, INSS, PRO_LABORE, LUCRO_SOCIO, FUNDO_RESERVA)
3. Para cada mês consolidado:
   - Usa valores da DRE consolidada
   - Gera pagamentos pendentes

IMPORTANTE: 
- Não gera pagamentos se já existirem para o mês
- Respeita valores zerados (não gera pendente se valor < R$ 0,01)
- Meses com prejuízo não geram distribuições de lucro

Uso:
    python -m database.migrations.gerar_pagamentos_retroativos
"""

from database.database import SessionLocal
from database import crud_pagamentos_pendentes, crud_contabilidade
from database.models import Entrada, PagamentoPendente
from sqlalchemy import extract, func
from datetime import datetime
import sys


def obter_meses_com_entradas(db: SessionLocal):
    """Retorna lista de meses (YYYY-MM) que possuem entradas"""
    print("\n1. Identificando meses com entradas...")
    
    # Query para obter anos e meses únicos com entradas
    meses_query = db.query(
        extract('year', Entrada.data).label('ano'),
        extract('month', Entrada.data).label('mes')
    ).distinct().order_by('ano', 'mes').all()
    
    meses = [f"{int(ano)}-{int(mes):02d}" for ano, mes in meses_query]
    
    print(f"   ✓ Encontrados {len(meses)} meses com entradas:")
    for mes in meses:
        qtd_entradas = db.query(func.count(Entrada.id)).filter(
            extract('year', Entrada.data) == int(mes.split('-')[0]),
            extract('month', Entrada.data) == int(mes.split('-')[1])
        ).scalar()
        print(f"     - {mes}: {qtd_entradas} entrada(s)")
    
    return meses


def verificar_pagamentos_existentes(db: SessionLocal, mes: str):
    """Verifica se já existem pagamentos pendentes para o mês"""
    ano_ref, mes_ref = map(int, mes.split('-'))
    
    count = db.query(func.count(PagamentoPendente.id)).filter(
        PagamentoPendente.mes_ref == mes_ref,
        PagamentoPendente.ano_ref == ano_ref
    ).scalar()
    
    return count > 0


def gerar_pagamentos_para_mes(db: SessionLocal, mes: str, forcar: bool = False):
    """Gera pagamentos pendentes para um mês específico"""
    ano_ref, mes_ref = map(int, mes.split('-'))
    
    # Verificar se já existem pagamentos
    if not forcar and verificar_pagamentos_existentes(db, mes):
        print(f"   ⏭️  {mes}: Pagamentos já existem (use --force para regenerar)")
        return None
    
    try:
        # Verificar se DRE está consolidada
        dre = crud_contabilidade.get_dre_mensal(db, mes)
        status = "consolidado" if dre and dre.consolidado else "provisório"
        
        # Gerar pagamentos
        resultado = crud_pagamentos_pendentes.gerar_pagamentos_mes_dre(db, mes)
        
        print(f"   ✓ {mes} ({status}): {resultado['qtd_criada']} pagamento(s) gerado(s)")
        
        # Mostrar breakdown por tipo
        if resultado['total_por_tipo']:
            for tipo, valor in resultado['total_por_tipo'].items():
                print(f"      - {tipo}: R$ {valor:.2f}")
        
        return resultado
        
    except Exception as e:
        print(f"   ❌ {mes}: Erro ao gerar pagamentos - {e}")
        return None


def executar_migracao(forcar: bool = False, mes_especifico: str = None):
    """Executa a migração completa"""
    print("=" * 70)
    print("MIGRAÇÃO: Geração de Pagamentos Pendentes Retroativos")
    print("=" * 70)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Modo: {'FORÇAR REGENERAÇÃO' if forcar else 'NORMAL (pula se existir)'}")
    
    db = SessionLocal()
    
    try:
        # Obter meses com entradas
        if mes_especifico:
            meses = [mes_especifico]
            print(f"\n🎯 Processando mês específico: {mes_especifico}")
        else:
            meses = obter_meses_com_entradas(db)
        
        if not meses:
            print("\n⚠️  Nenhum mês com entradas encontrado!")
            return
        
        # Gerar pagamentos para cada mês
        print("\n2. Gerando pagamentos pendentes...")
        
        resultados = {
            'sucesso': 0,
            'pulados': 0,
            'erros': 0,
            'total_pagamentos': 0
        }
        
        for mes in meses:
            resultado = gerar_pagamentos_para_mes(db, mes, forcar)
            
            if resultado:
                resultados['sucesso'] += 1
                resultados['total_pagamentos'] += resultado['qtd_criada']
            elif resultado is None:
                resultados['pulados'] += 1
            else:
                resultados['erros'] += 1
        
        # Resumo final
        print("\n" + "=" * 70)
        print("RESUMO DA MIGRAÇÃO")
        print("=" * 70)
        print(f"Meses processados: {len(meses)}")
        print(f"  ✓ Sucesso: {resultados['sucesso']}")
        print(f"  ⏭️  Pulados: {resultados['pulados']}")
        print(f"  ❌ Erros: {resultados['erros']}")
        print(f"\nTotal de pagamentos gerados: {resultados['total_pagamentos']}")
        
        # Estatísticas finais
        total_pendentes = db.query(func.count(PagamentoPendente.id)).scalar()
        total_confirmados = db.query(func.count(PagamentoPendente.id)).filter(
            PagamentoPendente.confirmado == True
        ).scalar()
        
        print(f"\nEstado atual do sistema:")
        print(f"  Total de pagamentos pendentes: {total_pendentes}")
        print(f"  Confirmados: {total_confirmados}")
        print(f"  Pendentes: {total_pendentes - total_confirmados}")
        
        print("\n✅ Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gera pagamentos pendentes retroativos')
    parser.add_argument('--force', action='store_true', 
                       help='Força regeneração mesmo se pagamentos já existirem')
    parser.add_argument('--mes', type=str,
                       help='Gera apenas para um mês específico (formato: YYYY-MM)')
    
    args = parser.parse_args()
    
    # Validar formato do mês se fornecido
    if args.mes:
        import re
        if not re.match(r'^\d{4}-\d{2}$', args.mes):
            print("❌ Erro: Formato de mês inválido. Use YYYY-MM (ex: 2024-11)")
            sys.exit(1)
    
    executar_migracao(forcar=args.force, mes_especifico=args.mes)
