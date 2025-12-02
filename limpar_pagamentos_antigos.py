"""
Script para limpar pagamentos pendentes antigos (mantém apenas integralização de capital)
"""
from database.database import SessionLocal
from database.models import PagamentoPendente

db = SessionLocal()

print("=" * 80)
print("LIMPEZA DE PAGAMENTOS PENDENTES")
print("=" * 80)

try:
    # Buscar todos os pagamentos pendentes
    todos_pagamentos = db.query(PagamentoPendente).all()
    
    print(f"\nTotal de pagamentos pendentes: {len(todos_pagamentos)}")
    
    # Separar por tipo
    por_tipo = {}
    for p in todos_pagamentos:
        if p.tipo not in por_tipo:
            por_tipo[p.tipo] = []
        por_tipo[p.tipo].append(p)
    
    print("\nBreakdown por tipo:")
    for tipo, lista in por_tipo.items():
        print(f"  {tipo}: {len(lista)}")
    
    # Identificar tipos a deletar (tudo exceto integralização)
    tipos_deletar = [tipo for tipo in por_tipo.keys() if tipo != "INTEGRALIZACAO_CAPITAL"]
    
    if not tipos_deletar:
        print("\n✅ Não há pagamentos para deletar (apenas integralização)")
        db.close()
        exit(0)
    
    print(f"\nTipos a deletar: {', '.join(tipos_deletar)}")
    
    # Contar quantos serão deletados
    total_deletar = sum(len(por_tipo[tipo]) for tipo in tipos_deletar if tipo in por_tipo)
    
    print(f"\n⚠️  {total_deletar} pagamentos serão DELETADOS")
    print("\nDeseja continuar? (digite 'SIM' para confirmar)")
    resposta = input("> ").strip().upper()
    
    if resposta != "SIM":
        print("\n❌ Operação cancelada pelo usuário")
        db.close()
        exit(0)
    
    # Deletar pagamentos
    print("\nDeletando pagamentos...")
    deletados = 0
    
    for tipo in tipos_deletar:
        if tipo in por_tipo:
            for p in por_tipo[tipo]:
                db.delete(p)
                deletados += 1
    
    db.commit()
    
    print(f"\n✅ {deletados} pagamentos deletados com sucesso!")
    
    # Verificar o que sobrou
    restantes = db.query(PagamentoPendente).all()
    print(f"\nPagamentos restantes: {len(restantes)}")
    
    if restantes:
        print("\nTipos restantes:")
        por_tipo_restante = {}
        for p in restantes:
            if p.tipo not in por_tipo_restante:
                por_tipo_restante[p.tipo] = 0
            por_tipo_restante[p.tipo] += 1
        
        for tipo, count in por_tipo_restante.items():
            print(f"  {tipo}: {count}")

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
