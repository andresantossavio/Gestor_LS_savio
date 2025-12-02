"""
Teste completo da integração: Pagamentos Pendentes → Lançamentos Contábeis
"""
from database.database import SessionLocal
from database.models import Entrada, EntradaSocio, Socio, PagamentoPendente, LancamentoContabil
from database.crud_pagamentos_pendentes import gerar_pendencias_entrada, confirmar_pagamento
from utils.simples import calcular_receita_12_meses
from datetime import date

db = SessionLocal()

print("=" * 80)
print("TESTE: INTEGRAÇÃO PAGAMENTOS PENDENTES → LANÇAMENTOS CONTÁBEIS")
print("=" * 80)

try:
    # 1. Criar entrada de teste
    print("\n1. Criando entrada de teste...")
    entrada = Entrada(
        cliente="Cliente Teste Integração",
        data=date(2025, 12, 1),
        valor=10000.00
    )
    db.add(entrada)
    db.flush()
    
    # 2. Associar sócios (80% André, 20% Bruna)
    print("   Associando sócios...")
    socios = db.query(Socio).limit(2).all()
    if len(socios) < 2:
        print("❌ Não há sócios suficientes no banco")
        db.rollback()
        exit(1)
    
    EntradaSocio(entrada_id=entrada.id, socio_id=socios[0].id, percentual=80.0)
    EntradaSocio(entrada_id=entrada.id, socio_id=socios[1].id, percentual=20.0)
    db.add(EntradaSocio(entrada_id=entrada.id, socio_id=socios[0].id, percentual=80.0))
    db.add(EntradaSocio(entrada_id=entrada.id, socio_id=socios[1].id, percentual=20.0))
    db.commit()
    
    print(f"   ✓ Entrada {entrada.id} criada")
    print(f"   ✓ {socios[0].nome}: 80%")
    print(f"   ✓ {socios[1].nome}: 20%")
    
    # 3. Gerar pendências (já cria lançamentos de provisão)
    print("\n2. Gerando pendências e lançamentos de provisão...")
    
    receita_12m = calcular_receita_12_meses(db, entrada.data)
    
    socios_data = []
    administrador_id = None
    for se in db.query(EntradaSocio).filter(EntradaSocio.entrada_id == entrada.id).all():
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
    
    pendencias = gerar_pendencias_entrada(
        db=db,
        entrada_id=entrada.id,
        valor_entrada=entrada.valor,
        mes=entrada.data.month,
        ano=entrada.data.year,
        receita_12m=receita_12m,
        socios=socios_data,
        administrador_id=administrador_id
    )
    
    print(f"   ✓ {len(pendencias)} pendências geradas")
    
    # 4. Verificar lançamentos de provisão criados
    print("\n3. Verificando lançamentos de provisão criados:")
    lancamentos_provisao = db.query(LancamentoContabil).filter(
        LancamentoContabil.tipo_lancamento == 'provisao',
        LancamentoContabil.referencia_mes == f"{entrada.data.year}-{entrada.data.month:02d}"
    ).all()
    
    print(f"   {len(lancamentos_provisao)} lançamentos de provisão encontrados:")
    for lanc in lancamentos_provisao:
        print(f"   - D: {lanc.conta_debito.codigo} / C: {lanc.conta_credito.codigo} | R$ {lanc.valor:,.2f}")
        print(f"     {lanc.historico}")
    
    # 5. Confirmar um pagamento (deve criar lançamento de pagamento)
    print("\n4. Confirmando pagamento de SIMPLES...")
    pendencia_simples = next((p for p in pendencias if p.tipo == "SIMPLES"), None)
    if pendencia_simples:
        data_pagamento = date(2025, 12, 20)
        confirmar_pagamento(db, pendencia_simples.id, data_pagamento)
        
        # Verificar lançamento de pagamento
        lancamentos_pagamento = db.query(LancamentoContabil).filter(
            LancamentoContabil.tipo_lancamento == 'pagamento_provisao',
            LancamentoContabil.data_pagamento == data_pagamento
        ).all()
        
        print(f"   ✓ Pagamento confirmado")
        print(f"   {len(lancamentos_pagamento)} lançamentos de pagamento criados:")
        for lanc in lancamentos_pagamento:
            print(f"   - D: {lanc.conta_debito.codigo} / C: {lanc.conta_credito.codigo} | R$ {lanc.valor:,.2f}")
            print(f"     {lanc.historico}")
    
    # 6. Resumo final
    print("\n5. RESUMO FINAL:")
    print("-" * 80)
    
    total_provisoes = sum(l.valor for l in lancamentos_provisao)
    total_pagamentos = sum(l.valor for l in db.query(LancamentoContabil).filter(
        LancamentoContabil.tipo_lancamento == 'pagamento_provisao'
    ).all())
    
    pendencias_confirmadas = db.query(PagamentoPendente).filter(
        PagamentoPendente.entrada_id == entrada.id,
        PagamentoPendente.confirmado == True
    ).count()
    
    pendencias_pendentes = db.query(PagamentoPendente).filter(
        PagamentoPendente.entrada_id == entrada.id,
        PagamentoPendente.confirmado == False
    ).count()
    
    print(f"Pendências: {pendencias_confirmadas} confirmadas, {pendencias_pendentes} pendentes")
    print(f"Lançamentos de provisão: {len(lancamentos_provisao)} (R$ {total_provisoes:,.2f})")
    print(f"Lançamentos de pagamento: {len(lancamentos_pagamento)} (R$ {total_pagamentos:,.2f})")
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    print("\n⚠️  Executando ROLLBACK (dados de teste não serão salvos)")
    
    db.rollback()

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
