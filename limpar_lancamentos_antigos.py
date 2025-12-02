"""
Script para limpar lançamentos contábeis antigos (mantém apenas integralização de capital)
"""
from database.database import SessionLocal
from database.models import LancamentoContabil, PlanoDeContas

db = SessionLocal()

print("=" * 80)
print("LIMPEZA DE LANÇAMENTOS CONTÁBEIS")
print("=" * 80)

try:
    # Buscar todos os lançamentos
    todos_lancamentos = db.query(LancamentoContabil).all()
    
    print(f"\nTotal de lançamentos contábeis: {len(todos_lancamentos)}")
    
    # Identificar lançamentos de integralização de capital
    # (envolvem conta 1.1.1 Caixa e 3.1 Capital Social)
    conta_caixa = db.query(PlanoDeContas).filter(PlanoDeContas.codigo == "1.1.1").first()
    conta_capital = db.query(PlanoDeContas).filter(PlanoDeContas.codigo == "3.1").first()
    
    if not conta_caixa or not conta_capital:
        print("❌ Contas de Caixa ou Capital Social não encontradas")
        db.close()
        exit(1)
    
    # Separar lançamentos
    lancamentos_capital = []
    lancamentos_outros = []
    
    for lanc in todos_lancamentos:
        # Integralização: D: 1.1.1 (Caixa) / C: 3.1 (Capital Social)
        eh_capital = (
            lanc.conta_debito_id == conta_caixa.id and 
            lanc.conta_credito_id == conta_capital.id and
            "capital" in lanc.historico.lower()
        )
        
        if eh_capital:
            lancamentos_capital.append(lanc)
        else:
            lancamentos_outros.append(lanc)
    
    print(f"\nLançamentos de integralização de capital: {len(lancamentos_capital)}")
    print(f"Outros lançamentos: {len(lancamentos_outros)}")
    
    if lancamentos_capital:
        print("\nLançamentos de capital (serão MANTIDOS):")
        for lanc in lancamentos_capital:
            print(f"  - {lanc.data} | R$ {lanc.valor:,.2f} | {lanc.historico}")
    
    if not lancamentos_outros:
        print("\n✅ Não há lançamentos para deletar")
        db.close()
        exit(0)
    
    # Agrupar outros lançamentos por tipo
    print("\nOutros lançamentos por tipo:")
    por_tipo = {}
    for lanc in lancamentos_outros:
        tipo = lanc.tipo_lancamento or "sem_tipo"
        if tipo not in por_tipo:
            por_tipo[tipo] = []
        por_tipo[tipo].append(lanc)
    
    for tipo, lista in por_tipo.items():
        print(f"  {tipo}: {len(lista)}")
    
    print(f"\n⚠️  {len(lancamentos_outros)} lançamentos serão DELETADOS")
    print("\nDeseja continuar? (digite 'SIM' para confirmar)")
    resposta = input("> ").strip().upper()
    
    if resposta != "SIM":
        print("\n❌ Operação cancelada pelo usuário")
        db.close()
        exit(0)
    
    # Deletar lançamentos
    print("\nDeletando lançamentos...")
    deletados = 0
    
    for lanc in lancamentos_outros:
        db.delete(lanc)
        deletados += 1
    
    db.commit()
    
    print(f"\n✅ {deletados} lançamentos deletados com sucesso!")
    
    # Verificar o que sobrou
    restantes = db.query(LancamentoContabil).all()
    print(f"\nLançamentos restantes: {len(restantes)}")
    
    if restantes:
        print("\nLançamentos restantes:")
        for lanc in restantes:
            debito = db.query(PlanoDeContas).filter(PlanoDeContas.id == lanc.conta_debito_id).first()
            credito = db.query(PlanoDeContas).filter(PlanoDeContas.id == lanc.conta_credito_id).first()
            print(f"  - {lanc.data} | D: {debito.codigo} / C: {credito.codigo} | R$ {lanc.valor:,.2f}")
            print(f"    {lanc.historico}")

except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n" + "=" * 80)
print("Operação concluída")
print("=" * 80)
