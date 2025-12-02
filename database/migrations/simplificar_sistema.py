"""
Script de Migração: Simplificação do Sistema Contábil

Este script:
1. Remove todos os lançamentos contábeis complexos
2. Mantém apenas lançamentos de:
   - Recebimento de honorários (Entrada)
   - Capital Social
3. Remove provisões antigas
4. Cria a tabela de pagamentos_pendentes
5. Gera pendências retroativas para todas as entradas existentes

ATENÇÃO: Este script faz alterações irreversíveis. Faça backup antes de executar!
"""

from database.database import SessionLocal, engine
from database.models import (
    Base, LancamentoContabil, Entrada, ProvisaoEntrada, 
    PagamentoPendente, Socio, EntradaSocio
)
from database.crud_pagamentos_pendentes import gerar_pendencias_entrada
from sqlalchemy import extract
import sys
from datetime import datetime


def criar_tabela_pagamentos_pendentes():
    """Cria a tabela de pagamentos pendentes"""
    print("\n1. Criando tabela pagamentos_pendentes...")
    Base.metadata.create_all(bind=engine)
    print("   ✓ Tabela criada com sucesso")


def limpar_lancamentos_complexos(db: SessionLocal):
    """Remove lançamentos complexos, mantendo apenas honorários e capital"""
    print("\n2. Limpando lançamentos contábeis complexos...")
    
    # Conta os lançamentos antes
    total_antes = db.query(LancamentoContabil).count()
    print(f"   Total de lançamentos antes: {total_antes}")
    
    # Remove todos os lançamentos que não são de entrada ou capital social
    # Mantém apenas:
    # - Lançamentos de entrada (D: 1.1.1 / C: 4.1.1)
    # - Lançamentos de capital social (D: 1.1.1 / C: 3.1)
    
    # IDs das contas que queremos manter
    CONTA_CAIXA = "1.1.1"
    CONTA_RECEITA = "4.1.1"
    CONTA_CAPITAL = "3.1"
    
    # Busca lançamentos a manter
    from database.models import PlanoDeContas
    
    conta_caixa_id = db.query(PlanoDeContas).filter(PlanoDeContas.codigo == CONTA_CAIXA).first().id
    conta_receita_id = db.query(PlanoDeContas).filter(PlanoDeContas.codigo == CONTA_RECEITA).first().id
    conta_capital_id = db.query(PlanoDeContas).filter(PlanoDeContas.codigo == CONTA_CAPITAL).first().id
    
    # Lançamentos a manter:
    # 1. Entradas: (D: Caixa / C: Receita) OU (entrada_id IS NOT NULL)
    # 2. Capital: (D: Caixa / C: Capital) OU (historico LIKE '%Capital Social%')
    
    lancamentos_entrada = db.query(LancamentoContabil).filter(
        LancamentoContabil.entrada_id.isnot(None)
    ).all()
    
    lancamentos_capital = db.query(LancamentoContabil).filter(
        LancamentoContabil.historico.like('%Capital Social%')
    ).all()
    
    ids_manter = set()
    for lanc in lancamentos_entrada + lancamentos_capital:
        ids_manter.add(lanc.id)
    
    print(f"   Lançamentos a manter: {len(ids_manter)}")
    print(f"   - Entradas: {len(lancamentos_entrada)}")
    print(f"   - Capital Social: {len(lancamentos_capital)}")
    
    # Remove todos os outros
    lancamentos_remover = db.query(LancamentoContabil).filter(
        ~LancamentoContabil.id.in_(ids_manter)
    ).all()
    
    print(f"   Lançamentos a remover: {len(lancamentos_remover)}")
    
    if len(lancamentos_remover) > 0:
        resposta = input(f"   Deseja remover {len(lancamentos_remover)} lançamentos? (sim/não): ")
        if resposta.lower() == 'sim':
            for lanc in lancamentos_remover:
                db.delete(lanc)
            db.commit()
            print(f"   ✓ {len(lancamentos_remover)} lançamentos removidos")
        else:
            print("   ✗ Operação cancelada")
            return False
    else:
        print("   ✓ Nenhum lançamento para remover")
    
    total_depois = db.query(LancamentoContabil).count()
    print(f"   Total de lançamentos após: {total_depois}")
    
    return True


def limpar_provisoes(db: SessionLocal):
    """Remove todas as provisões antigas"""
    print("\n3. Limpando provisões antigas...")
    
    total_provisoes = db.query(ProvisaoEntrada).count()
    print(f"   Total de provisões: {total_provisoes}")
    
    if total_provisoes > 0:
        resposta = input(f"   Deseja remover {total_provisoes} provisões? (sim/não): ")
        if resposta.lower() == 'sim':
            db.query(ProvisaoEntrada).delete()
            db.commit()
            print(f"   ✓ {total_provisoes} provisões removidas")
        else:
            print("   ✗ Operação cancelada")
            return False
    else:
        print("   ✓ Nenhuma provisão para remover")
    
    return True


def gerar_pendencias_retroativas(db: SessionLocal):
    """Gera pendências para todas as entradas existentes"""
    print("\n4. Gerando pendências retroativas para entradas existentes...")
    
    # Busca todas as entradas
    entradas = db.query(Entrada).order_by(Entrada.data).all()
    print(f"   Total de entradas: {len(entradas)}")
    
    if len(entradas) == 0:
        print("   ✗ Nenhuma entrada encontrada")
        return True
    
    # Busca todos os sócios
    socios = db.query(Socio).all()
    print(f"   Total de sócios: {len(socios)}")
    
    if len(socios) == 0:
        print("   ✗ Nenhum sócio encontrado")
        return False
    
    resposta = input(f"   Deseja gerar pendências para {len(entradas)} entradas? (sim/não): ")
    if resposta.lower() != 'sim':
        print("   ✗ Operação cancelada")
        return False
    
    # Calcula receita 12 meses acumulada
    receita_12m = 0.0
    pendencias_criadas = 0
    
    for entrada in entradas:
        mes = entrada.data.month
        ano = entrada.data.year
        
        # Atualiza receita 12 meses
        receita_12m += entrada.valor
        
        # Busca percentuais dos sócios na entrada
        socios_entrada = db.query(EntradaSocio).filter(
            EntradaSocio.entrada_id == entrada.id
        ).all()
        
        administrador_id = None
        
        if not socios_entrada:
            # Usa percentual padrão dos sócios
            socios_data = []
            for socio in socios:
                if socio.percentual:
                    is_admin = socio.funcao and "administrador" in socio.funcao.lower()
                    if is_admin:
                        administrador_id = socio.id
                    
                    socios_data.append({
                        "id": socio.id,
                        "nome": socio.nome,
                        "percentual": socio.percentual,
                        "funcao": socio.funcao,
                        "is_admin": is_admin
                    })
        else:
            socios_data = []
            for se in socios_entrada:
                socio = db.query(Socio).filter(Socio.id == se.socio_id).first()
                is_admin = socio.funcao and "administrador" in socio.funcao.lower()
                if is_admin:
                    administrador_id = socio.id
                
                socios_data.append({
                    "id": socio.id,
                    "nome": socio.nome,
                    "percentual": se.percentual,
                    "funcao": socio.funcao,
                    "is_admin": is_admin
                })
        
        if not socios_data:
            print(f"   ⚠ Entrada {entrada.id} sem sócios definidos, pulando...")
            continue
        
        # Gera pendências
        try:
            pendencias = gerar_pendencias_entrada(
                db=db,
                entrada_id=entrada.id,
                valor_entrada=entrada.valor,
                mes=mes,
                ano=ano,
                receita_12m=receita_12m,
                socios=socios_data,
                administrador_id=administrador_id
            )
            pendencias_criadas += len(pendencias)
            print(f"   ✓ Entrada {entrada.id} ({mes}/{ano}): {len(pendencias)} pendências criadas")
        except Exception as e:
            print(f"   ✗ Erro ao gerar pendências para entrada {entrada.id}: {e}")
    
    print(f"\n   ✓ Total de pendências criadas: {pendencias_criadas}")
    return True


def exibir_resumo_final(db: SessionLocal):
    """Exibe resumo final da migração"""
    print("\n" + "="*60)
    print("RESUMO FINAL DA MIGRAÇÃO")
    print("="*60)
    
    total_lancamentos = db.query(LancamentoContabil).count()
    total_provisoes = db.query(ProvisaoEntrada).count()
    total_pendencias = db.query(PagamentoPendente).count()
    total_pendencias_confirmadas = db.query(PagamentoPendente).filter(
        PagamentoPendente.confirmado == True
    ).count()
    total_pendencias_pendentes = db.query(PagamentoPendente).filter(
        PagamentoPendente.confirmado == False
    ).count()
    
    print(f"\nLançamentos Contábeis: {total_lancamentos}")
    print(f"Provisões: {total_provisoes}")
    print(f"Pagamentos Pendentes: {total_pendencias}")
    print(f"  - Confirmados: {total_pendencias_confirmadas}")
    print(f"  - Pendentes: {total_pendencias_pendentes}")
    
    # Breakdown por tipo
    from sqlalchemy import func
    breakdown = db.query(
        PagamentoPendente.tipo,
        func.count(PagamentoPendente.id).label('qtd'),
        func.sum(PagamentoPendente.valor).label('total')
    ).group_by(PagamentoPendente.tipo).all()
    
    print("\nBreakdown por tipo de pendência:")
    for tipo, qtd, total in breakdown:
        print(f"  - {tipo}: {qtd} ({total:.2f})")
    
    print("\n" + "="*60)
    print("✓ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)


def main():
    """Executa a migração completa"""
    print("="*60)
    print("SIMPLIFICAÇÃO DO SISTEMA CONTÁBIL")
    print("="*60)
    print("\nEste script irá:")
    print("1. Criar a tabela de pagamentos_pendentes")
    print("2. Remover lançamentos contábeis complexos")
    print("3. Remover provisões antigas")
    print("4. Gerar pendências retroativas")
    print("\n⚠ ATENÇÃO: Esta operação é IRREVERSÍVEL!")
    print("⚠ Faça backup do banco de dados antes de continuar!")
    
    resposta = input("\nDeseja continuar? (sim/não): ")
    if resposta.lower() != 'sim':
        print("\n✗ Operação cancelada pelo usuário")
        sys.exit(0)
    
    db = SessionLocal()
    try:
        # 1. Criar tabela
        criar_tabela_pagamentos_pendentes()
        
        # 2. Limpar lançamentos
        if not limpar_lancamentos_complexos(db):
            print("\n✗ Migração cancelada")
            sys.exit(1)
        
        # 3. Limpar provisões
        if not limpar_provisoes(db):
            print("\n✗ Migração cancelada")
            sys.exit(1)
        
        # 4. Gerar pendências retroativas
        if not gerar_pendencias_retroativas(db):
            print("\n✗ Migração cancelada")
            sys.exit(1)
        
        # 5. Exibir resumo
        exibir_resumo_final(db)
        
    except Exception as e:
        print(f"\n✗ ERRO durante a migração: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
