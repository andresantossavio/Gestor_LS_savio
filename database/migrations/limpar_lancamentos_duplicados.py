"""
Migration: Limpar lançamentos contábeis duplicados
Remove lançamentos automáticos duplicados, mantendo apenas o mais recente por chave composta.
Chave: (referencia_mes, tipo_lancamento, conta_debito_id, conta_credito_id, automatico=True)
"""
from database.database import SessionLocal
from database.models import LancamentoContabil
from sqlalchemy import func, and_
from typing import Dict, List, Tuple


def identificar_duplicatas(db) -> List[Tuple]:
    """
    Identifica grupos de lançamentos duplicados.
    
    Returns:
        Lista de tuplas: (referencia_mes, tipo_lancamento, conta_debito_id, conta_credito_id, count)
    """
    # Query que agrupa lançamentos automáticos pela chave composta e conta quantos há
    duplicatas = db.query(
        LancamentoContabil.referencia_mes,
        LancamentoContabil.tipo_lancamento,
        LancamentoContabil.conta_debito_id,
        LancamentoContabil.conta_credito_id,
        func.count(LancamentoContabil.id).label('total')
    ).filter(
        LancamentoContabil.automatico == True,
        # Não considerar aportes de capital: são legítimos por sócio e não devem ser consolidados
        LancamentoContabil.tipo_lancamento != 'aporte_capital'
    ).group_by(
        LancamentoContabil.referencia_mes,
        LancamentoContabil.tipo_lancamento,
        LancamentoContabil.conta_debito_id,
        LancamentoContabil.conta_credito_id
    ).having(
        func.count(LancamentoContabil.id) > 1
    ).all()
    
    return duplicatas


def remover_duplicatas_grupo(db, mes: str, tipo: str, debito_id: int, credito_id: int) -> int:
    """
    Remove duplicatas de um grupo específico, mantendo apenas o mais recente (maior ID).
    
    Args:
        db: Sessão do banco
        mes: Mês de referência
        tipo: Tipo de lançamento
        debito_id: ID da conta débito
        credito_id: ID da conta crédito
    
    Returns:
        Quantidade de lançamentos deletados
    """
    # Buscar todos os lançamentos deste grupo
    lancamentos = db.query(LancamentoContabil).filter(
        and_(
            LancamentoContabil.referencia_mes == mes,
            LancamentoContabil.tipo_lancamento == tipo,
            LancamentoContabil.conta_debito_id == debito_id,
            LancamentoContabil.conta_credito_id == credito_id,
            LancamentoContabil.automatico == True
        )
    ).order_by(LancamentoContabil.id.desc()).all()
    
    if len(lancamentos) <= 1:
        return 0
    
    # Manter o primeiro (mais recente, maior ID), deletar os outros
    mais_recente = lancamentos[0]
    duplicados = lancamentos[1:]
    
    print(f"   📋 Grupo: {mes} | {tipo} | D:{debito_id} C:{credito_id}")
    print(f"      ✅ Mantendo: ID {mais_recente.id} (valor: R$ {mais_recente.valor:.2f})")
    
    ids_deletados = []
    for dup in duplicados:
        print(f"      ❌ Deletando: ID {dup.id} (valor: R$ {dup.valor:.2f})")
        ids_deletados.append(dup.id)
        db.delete(dup)
    
    return len(ids_deletados)


def limpar_duplicatas():
    """
    Executa a limpeza de todos os lançamentos duplicados.
    """
    db = SessionLocal()
    
    try:
        print("🔍 Buscando lançamentos duplicados...")
        print()
        
        duplicatas = identificar_duplicatas(db)
        
        if not duplicatas:
            print("✅ Nenhuma duplicata encontrada! Banco de dados está limpo.")
            return
        
        print(f"⚠️  Encontrados {len(duplicatas)} grupos com duplicatas:")
        print()
        
        total_deletados = 0
        
        for dup in duplicatas:
            mes, tipo, debito_id, credito_id, total = dup
            print(f"🔄 Processando grupo: {mes} | {tipo} | {total} lançamentos")
            
            deletados = remover_duplicatas_grupo(db, mes, tipo, debito_id, credito_id)
            total_deletados += deletados
            print()
        
        # Confirmar mudanças
        db.commit()
        
        print(f"✅ Migration concluída!")
        print(f"   📊 Grupos processados: {len(duplicatas)}")
        print(f"   🗑️  Lançamentos deletados: {total_deletados}")
        print(f"   ✅ Lançamentos mantidos: {len(duplicatas)}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro durante migration: {e}")
        raise
    finally:
        db.close()


def gerar_relatorio_pre_limpeza():
    """
    Gera um relatório de duplicatas sem modificar o banco.
    Útil para análise antes de executar a limpeza.
    """
    db = SessionLocal()
    
    try:
        print("📊 RELATÓRIO DE DUPLICATAS (modo somente leitura)")
        print("=" * 70)
        print()
        
        duplicatas = identificar_duplicatas(db)
        
        if not duplicatas:
            print("✅ Nenhuma duplicata encontrada!")
            return
        
        print(f"⚠️  Encontrados {len(duplicatas)} grupos com duplicatas:")
        print()
        
        total_lancamentos_duplicados = 0
        
        for idx, dup in enumerate(duplicatas, 1):
            mes, tipo, debito_id, credito_id, total = dup
            total_lancamentos_duplicados += total
            
            print(f"{idx}. Mês: {mes} | Tipo: {tipo}")
            print(f"   Débito: {debito_id} | Crédito: {credito_id}")
            print(f"   Total de lançamentos: {total}")
            
            # Buscar valores para comparação
            lancamentos = db.query(LancamentoContabil).filter(
                and_(
                    LancamentoContabil.referencia_mes == mes,
                    LancamentoContabil.tipo_lancamento == tipo,
                    LancamentoContabil.conta_debito_id == debito_id,
                    LancamentoContabil.conta_credito_id == credito_id,
                    LancamentoContabil.automatico == True
                )
            ).order_by(LancamentoContabil.id.desc()).all()
            
            for lanc in lancamentos:
                status = "✅ (será mantido)" if lanc == lancamentos[0] else "❌ (será deletado)"
                print(f"      ID {lanc.id}: R$ {lanc.valor:.2f} - {lanc.data} {status}")
            
            print()
        
        print("=" * 70)
        print(f"📊 Resumo:")
        print(f"   Grupos com duplicatas: {len(duplicatas)}")
        print(f"   Total de lançamentos: {total_lancamentos_duplicados}")
        print(f"   Serão mantidos: {len(duplicatas)} (1 por grupo)")
        print(f"   Serão deletados: {total_lancamentos_duplicados - len(duplicatas)}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--relatorio":
        print("🚀 Gerando relatório de duplicatas (somente leitura)")
        print()
        gerar_relatorio_pre_limpeza()
    else:
        print("🚀 Iniciando migration: limpar_lancamentos_duplicados")
        print("⚠️  ATENÇÃO: Esta operação deletará lançamentos duplicados!")
        print("   Execute com --relatorio primeiro para visualizar o que será deletado.")
        print()
        
        resposta = input("Deseja continuar? (sim/não): ").strip().lower()
        if resposta not in ['sim', 's', 'yes', 'y']:
            print("❌ Operação cancelada pelo usuário.")
            sys.exit(0)
        
        print()
        limpar_duplicatas()
        print()
        print("✅ Migration finalizada com sucesso!")
