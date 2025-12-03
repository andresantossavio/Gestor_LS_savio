"""
Script de teste: Validar padrão UPDATE de lançamentos
Testa se IDs são preservados no ciclo desconsolidar→consolidar
"""
from database.database import SessionLocal
from database.models import LancamentoContabil, DREMensal, Entrada, Despesa
from database.crud_contabilidade import (
    atualizar_lancamentos_mes,
    consolidar_dre_mes,
    desconsolidar_dre_mes
)
from datetime import date


def capturar_ids_lancamentos(db, mes: str) -> dict:
    """Captura os IDs de todos os lançamentos automáticos do mês."""
    lancamentos = db.query(LancamentoContabil).filter(
        LancamentoContabil.referencia_mes == mes,
        LancamentoContabil.automatico == True
    ).all()
    
    ids_por_tipo = {}
    for lanc in lancamentos:
        chave = f"{lanc.tipo_lancamento}|D:{lanc.conta_debito_id}|C:{lanc.conta_credito_id}"
        ids_por_tipo[chave] = {
            'id': lanc.id,
            'valor': float(lanc.valor),
            'data': lanc.data,
            'editado_em': lanc.editado_em
        }
    
    return ids_por_tipo


def testar_preservacao_ids():
    """
    Testa se IDs são preservados durante:
    1. Criação inicial
    2. Atualização por edição de entrada
    3. Consolidação
    4. Desconsolidação
    5. Nova consolidação
    """
    db = SessionLocal()
    mes_teste = "2025-12"
    
    try:
        print("🧪 TESTE: Preservação de IDs no ciclo desconsolidar→consolidar")
        print("=" * 70)
        print()
        
        # SETUP: Limpar mês de teste
        print("🧹 Limpando dados de teste anteriores...")
        db.query(DREMensal).filter(DREMensal.mes == mes_teste).delete()
        db.query(LancamentoContabil).filter(LancamentoContabil.referencia_mes == mes_teste).delete()
        db.query(Entrada).filter(Entrada.data >= date(2025, 12, 1), Entrada.data <= date(2025, 12, 31)).delete()
        db.query(Despesa).filter(Despesa.data >= date(2025, 12, 1), Despesa.data <= date(2025, 12, 31)).delete()
        db.commit()
        print("   ✅ Dados limpos")
        print()
        
        # PASSO 1: Criar entrada inicial
        print("📝 PASSO 1: Criar entrada inicial (R$ 10.000,00)")
        entrada1 = Entrada(
            data=date(2025, 12, 15),
            valor=10000.0,
            cliente="Teste - Cliente",
            cliente_id=1
        )
        db.add(entrada1)
        db.commit()
        
        # Chamar atualizar_lancamentos_mes
        resultado1 = atualizar_lancamentos_mes(db, mes_teste)
        db.commit()
        
        ids_passo1 = capturar_ids_lancamentos(db, mes_teste)
        print(f"   ✅ Criados {len(ids_passo1)} lançamentos automáticos")
        print(f"   💰 Lucro líquido: R$ {resultado1['lucro_liquido']:.2f}")
        
        # Exibir IDs criados
        print("\n   📋 IDs dos lançamentos:")
        for tipo, info in sorted(ids_passo1.items()):
            print(f"      {tipo}: ID {info['id']} (R$ {info['valor']:.2f})")
        print()
        
        # PASSO 2: Editar entrada (aumentar valor)
        print("✏️  PASSO 2: Editar entrada (aumentar para R$ 15.000,00)")
        entrada1.valor = 15000.0
        db.commit()
        
        # Chamar atualizar_lancamentos_mes novamente
        resultado2 = atualizar_lancamentos_mes(db, mes_teste)
        db.commit()
        
        ids_passo2 = capturar_ids_lancamentos(db, mes_teste)
        print(f"   ✅ Lançamentos atualizados: {len(ids_passo2)}")
        print(f"   💰 Novo lucro líquido: R$ {resultado2['lucro_liquido']:.2f}")
        
        # Verificar se IDs foram preservados
        print("\n   🔍 Verificando preservação de IDs:")
        ids_preservados = 0
        ids_alterados = 0
        valores_atualizados = 0
        
        for tipo, info_passo1 in ids_passo1.items():
            if tipo in ids_passo2:
                info_passo2 = ids_passo2[tipo]
                if info_passo1['id'] == info_passo2['id']:
                    ids_preservados += 1
                    if info_passo1['valor'] != info_passo2['valor']:
                        valores_atualizados += 1
                        print(f"      ✅ {tipo}: ID {info_passo2['id']} preservado (valor atualizado: R$ {info_passo1['valor']:.2f} → R$ {info_passo2['valor']:.2f})")
                    else:
                        print(f"      ✅ {tipo}: ID {info_passo2['id']} preservado (valor inalterado)")
                else:
                    ids_alterados += 1
                    print(f"      ❌ {tipo}: ID mudou de {info_passo1['id']} para {info_passo2['id']}")
        
        print(f"\n   📊 Resultado: {ids_preservados} IDs preservados, {ids_alterados} IDs alterados, {valores_atualizados} valores atualizados")
        
        if ids_alterados > 0:
            print("   ⚠️  FALHA: Alguns IDs foram alterados (deveria usar UPDATE)")
            return False
        
        print()
        
        # PASSO 3: Consolidar DRE
        print("🔒 PASSO 3: Consolidar DRE")
        dre = consolidar_dre_mes(db, mes_teste)
        db.commit()
        
        ids_passo3 = capturar_ids_lancamentos(db, mes_teste)
        print(f"   ✅ DRE consolidada")
        print(f"   📊 Total de lançamentos: {len(ids_passo3)} (provisões + consolidação)")
        
        # Verificar novamente se IDs das provisões foram preservados
        print("\n   🔍 Verificando se consolidação preservou IDs das provisões:")
        ids_provisoes_preservados = 0
        for tipo, info_passo2 in ids_passo2.items():
            if tipo in ids_passo3:
                info_passo3 = ids_passo3[tipo]
                if info_passo2['id'] == info_passo3['id']:
                    ids_provisoes_preservados += 1
                    print(f"      ✅ {tipo}: ID {info_passo3['id']} preservado")
                else:
                    print(f"      ❌ {tipo}: ID mudou de {info_passo2['id']} para {info_passo3['id']}")
        
        # Mostrar lançamentos de consolidação (novos)
        print("\n   📋 Novos lançamentos de consolidação:")
        for tipo, info in sorted(ids_passo3.items()):
            if tipo not in ids_passo2:
                print(f"      {tipo}: ID {info['id']} (R$ {info['valor']:.2f})")
        
        print()
        
        # PASSO 4: Desconsolidar DRE
        print("🔓 PASSO 4: Desconsolidar DRE")
        desconsolidar_dre_mes(db, mes_teste)
        db.commit()
        
        ids_passo4 = capturar_ids_lancamentos(db, mes_teste)
        print(f"   ✅ DRE desconsolidada")
        print(f"   📊 Total de lançamentos: {len(ids_passo4)} (apenas provisões)")
        
        # Verificar se IDs das provisões continuam preservados
        print("\n   🔍 Verificando se desconsolidação manteve IDs das provisões:")
        for tipo, info_passo2 in ids_passo2.items():
            if tipo in ids_passo4:
                info_passo4 = ids_passo4[tipo]
                if info_passo2['id'] == info_passo4['id']:
                    print(f"      ✅ {tipo}: ID {info_passo4['id']} ainda preservado")
                else:
                    print(f"      ❌ {tipo}: ID mudou de {info_passo2['id']} para {info_passo4['id']}")
        
        print()
        
        # PASSO 5: Consolidar novamente
        print("🔒 PASSO 5: Consolidar DRE novamente")
        dre2 = consolidar_dre_mes(db, mes_teste, forcar_recalculo=True)
        db.commit()
        
        ids_passo5 = capturar_ids_lancamentos(db, mes_teste)
        print(f"   ✅ DRE consolidada novamente")
        print(f"   📊 Total de lançamentos: {len(ids_passo5)}")
        
        # VERIFICAÇÃO FINAL: IDs das provisões devem ser os mesmos desde o PASSO 2
        print("\n   🔍 VERIFICAÇÃO FINAL: Comparando IDs com PASSO 2 (após primeira edição):")
        todos_preservados = True
        
        for tipo, info_passo2 in ids_passo2.items():
            if tipo in ids_passo5:
                info_passo5 = ids_passo5[tipo]
                if info_passo2['id'] == info_passo5['id']:
                    print(f"      ✅ {tipo}: ID {info_passo5['id']} PRESERVADO desde o início!")
                else:
                    print(f"      ❌ {tipo}: ID mudou de {info_passo2['id']} para {info_passo5['id']}")
                    todos_preservados = False
        
        print()
        print("=" * 70)
        
        if todos_preservados:
            print("✅ SUCESSO: Todos os IDs foram preservados durante todo o ciclo!")
            print("   Padrão UPDATE está funcionando corretamente.")
            return True
        else:
            print("❌ FALHA: Alguns IDs foram alterados durante o ciclo.")
            print("   Padrão UPDATE não está funcionando como esperado.")
            return False
        
    except Exception as e:
        db.rollback()
        print(f"❌ ERRO durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def testar_duplicatas():
    """
    Testa se há duplicatas após múltiplas consolidações.
    """
    db = SessionLocal()
    
    try:
        print("\n🧪 TESTE: Verificar ausência de duplicatas")
        print("=" * 70)
        print()
        
        # Buscar duplicatas
        from sqlalchemy import func, and_
        
        duplicatas = db.query(
            LancamentoContabil.referencia_mes,
            LancamentoContabil.tipo_lancamento,
            LancamentoContabil.conta_debito_id,
            LancamentoContabil.conta_credito_id,
            func.count(LancamentoContabil.id).label('total')
        ).filter(
            LancamentoContabil.automatico == True
        ).group_by(
            LancamentoContabil.referencia_mes,
            LancamentoContabil.tipo_lancamento,
            LancamentoContabil.conta_debito_id,
            LancamentoContabil.conta_credito_id
        ).having(
            func.count(LancamentoContabil.id) > 1
        ).all()
        
        if not duplicatas:
            print("✅ SUCESSO: Nenhuma duplicata encontrada no banco!")
            return True
        else:
            print(f"❌ FALHA: Encontradas {len(duplicatas)} grupos com duplicatas:")
            for dup in duplicatas:
                print(f"   {dup.referencia_mes} | {dup.tipo_lancamento} | D:{dup.conta_debito_id} C:{dup.conta_credito_id} | Total: {dup.total}")
            return False
        
    except Exception as e:
        print(f"❌ ERRO durante teste: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🚀 Iniciando testes de validação do padrão UPDATE")
    print()
    
    # Teste 1: Preservação de IDs
    sucesso1 = testar_preservacao_ids()
    
    # Teste 2: Ausência de duplicatas
    sucesso2 = testar_duplicatas()
    
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70)
    print(f"Teste 1 - Preservação de IDs: {'✅ PASSOU' if sucesso1 else '❌ FALHOU'}")
    print(f"Teste 2 - Ausência de duplicatas: {'✅ PASSOU' if sucesso2 else '❌ FALHOU'}")
    print()
    
    if sucesso1 and sucesso2:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("   O sistema está funcionando corretamente com o padrão UPDATE.")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
        print("   Revisar implementação do padrão UPDATE.")
