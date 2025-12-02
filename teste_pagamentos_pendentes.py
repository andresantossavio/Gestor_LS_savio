"""
Script de teste rápido para o sistema de pagamentos pendentes
"""
from database.database import SessionLocal
from database.models import Entrada, Socio, PagamentoPendente
from datetime import date
from sqlalchemy import func

db = SessionLocal()

print("=" * 60)
print("TESTE DO SISTEMA DE PAGAMENTOS PENDENTES")
print("=" * 60)

# 1. Verificar entradas
print("\n1. Verificando entradas...")
total_entradas = db.query(Entrada).count()
print(f"   Total de entradas: {total_entradas}")

if total_entradas > 0:
    # Mostrar algumas entradas
    entradas = db.query(Entrada).order_by(Entrada.data.desc()).limit(3).all()
    for e in entradas:
        print(f"   - ID {e.id}: R$ {e.valor:.2f} em {e.data}")

# 2. Verificar sócios
print("\n2. Verificando sócios...")
socios = db.query(Socio).all()
print(f"   Total de sócios: {len(socios)}")
for s in socios:
    print(f"   - {s.nome}: {s.percentual}%")

# 3. Verificar pagamentos pendentes
print("\n3. Verificando pagamentos pendentes...")
total_pendentes = db.query(PagamentoPendente).count()
print(f"   Total de pagamentos pendentes: {total_pendentes}")

if total_pendentes > 0:
    # Breakdown por tipo
    breakdown = db.query(
        PagamentoPendente.tipo,
        func.count(PagamentoPendente.id).label('qtd'),
        func.sum(PagamentoPendente.valor).label('total'),
        func.sum(func.case([(PagamentoPendente.confirmado == True, 1)], else_=0)).label('confirmados')
    ).group_by(PagamentoPendente.tipo).all()
    
    print("\n   Breakdown por tipo:")
    for tipo, qtd, total, confirmados in breakdown:
        print(f"   - {tipo}: {qtd} pagamentos, R$ {total:.2f}, {confirmados} confirmados")
    
    # Mostrar alguns pagamentos
    print("\n   Últimos 5 pagamentos pendentes:")
    pendentes = db.query(PagamentoPendente).order_by(
        PagamentoPendente.ano_ref.desc(),
        PagamentoPendente.mes_ref.desc(),
        PagamentoPendente.id.desc()
    ).limit(5).all()
    
    for p in pendentes:
        status = "✓ Confirmado" if p.confirmado else "⏳ Pendente"
        print(f"   - {p.descricao}: R$ {p.valor:.2f} - {status}")

# 4. Resumo geral
print("\n4. Resumo Geral")
print("=" * 60)

total_valor_pendente = db.query(func.sum(PagamentoPendente.valor)).filter(
    PagamentoPendente.confirmado == False
).scalar() or 0.0

total_valor_confirmado = db.query(func.sum(PagamentoPendente.valor)).filter(
    PagamentoPendente.confirmado == True
).scalar() or 0.0

print(f"Total Pendente: R$ {total_valor_pendente:.2f}")
print(f"Total Confirmado: R$ {total_valor_confirmado:.2f}")
print(f"Total Geral: R$ {(total_valor_pendente + total_valor_confirmado):.2f}")

print("\n" + "=" * 60)
print("✓ Teste concluído!")
print("=" * 60)

db.close()
