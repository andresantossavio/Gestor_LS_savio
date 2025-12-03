"""
Migração: Criar lançamentos contábeis para aportes de capital existentes
Data: 2024-12-02
Objetivo: Retroagir lançamentos contábeis para todos os aportes já registrados
"""
import sys
sys.path.insert(0, '.')

from database.database import SessionLocal
from database import models
from database.crud_plano_contas import buscar_conta_por_codigo

def migrar_lancamentos_aportes():
    db = SessionLocal()
    
    print("=" * 80)
    print("MIGRAÇÃO: Criar lançamentos contábeis para aportes existentes")
    print("=" * 80)
    
    try:
        # Buscar todas as contas necessárias
        conta_capital = buscar_conta_por_codigo(db, "3.1")
        conta_caixa = buscar_conta_por_codigo(db, "1.1.1")
        conta_equipamentos = buscar_conta_por_codigo(db, "1.2.1.1")
        conta_servicos = buscar_conta_por_codigo(db, "1.2.2.1")
        
        if not all([conta_capital, conta_caixa, conta_equipamentos]):
            print("❌ ERRO: Contas contábeis necessárias não encontradas!")
            print("Execute primeiro: python database/init_all_data.py")
            return
        
        if not conta_servicos:
            print("⚠️  AVISO: Conta 1.2.2.1 (Serviços Capitalizados) não encontrada.")
            print("   Aportes de serviço não serão migrados.")
        
        # Buscar todos os aportes
        aportes = db.query(models.AporteCapital).order_by(models.AporteCapital.data).all()
        print(f"\nTotal de aportes encontrados: {len(aportes)}")
        
        criados = 0
        ignorados = 0
        erros = 0
        
        for aporte in aportes:
            # Verificar se já existe lançamento para este aporte
            lanc_existente = db.query(models.LancamentoContabil).filter(
                models.LancamentoContabil.tipo_lancamento == 'aporte_capital',
                models.LancamentoContabil.data == aporte.data,
                models.LancamentoContabil.valor == aporte.valor,
                models.LancamentoContabil.historico.like(f'%{aporte.socio.nome}%')
            ).first()
            
            if lanc_existente:
                ignorados += 1
                print(f"  ⏭️  {aporte.socio.nome} - {aporte.data} - R$ {aporte.valor:.2f} ({aporte.tipo_aporte}) - JÁ EXISTE")
                continue
            
            # Criar lançamento baseado no tipo
            try:
                if aporte.tipo_aporte == 'dinheiro':
                    conta_debito = conta_caixa
                    conta_credito = conta_capital
                    historico = f"Aporte de capital em dinheiro - {aporte.socio.nome}"
                    
                elif aporte.tipo_aporte == 'bens':
                    conta_debito = conta_equipamentos
                    conta_credito = conta_capital
                    historico = f"Aporte de capital em bens - {aporte.socio.nome}"
                    
                elif aporte.tipo_aporte == 'servicos':
                    if not conta_servicos:
                        print(f"  ❌ {aporte.socio.nome} - Tipo 'servicos' mas conta 1.2.2.1 não existe")
                        erros += 1
                        continue
                    conta_debito = conta_servicos
                    conta_credito = conta_capital
                    historico = f"Aporte de capital em serviços - {aporte.socio.nome}"
                    
                elif aporte.tipo_aporte == 'retirada':
                    conta_debito = conta_capital
                    conta_credito = conta_caixa
                    historico = f"Retirada de capital - {aporte.socio.nome}"
                    
                else:
                    print(f"  ❌ {aporte.socio.nome} - Tipo inválido: {aporte.tipo_aporte}")
                    erros += 1
                    continue
                
                if aporte.descricao:
                    historico += f" - {aporte.descricao}"
                
                # Criar lançamento
                lanc = models.LancamentoContabil(
                    data=aporte.data,
                    conta_debito_id=conta_debito.id,
                    conta_credito_id=conta_credito.id,
                    valor=aporte.valor,
                    historico=historico,
                    automatico=True,
                    editavel=False,
                    tipo_lancamento='aporte_capital'
                )
                db.add(lanc)
                db.flush()
                
                criados += 1
                print(f"  ✅ {aporte.socio.nome} - {aporte.data} - R$ {aporte.valor:.2f} ({aporte.tipo_aporte})")
                
            except Exception as e:
                erros += 1
                print(f"  ❌ {aporte.socio.nome} - ERRO: {str(e)}")
                continue
        
        db.commit()
        
        print("\n" + "=" * 80)
        print("MIGRAÇÃO CONCLUÍDA")
        print("=" * 80)
        print(f"Lançamentos criados: {criados}")
        print(f"Já existentes (ignorados): {ignorados}")
        print(f"Erros: {erros}")
        
        if erros == 0 and criados > 0:
            print("\n✅ Migração bem-sucedida! Todos os aportes agora têm lançamentos contábeis.")
        elif criados == 0 and ignorados > 0:
            print("\n✅ Nenhuma ação necessária - todos os lançamentos já existem.")
        
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrar_lancamentos_aportes()
