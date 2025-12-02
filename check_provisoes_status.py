#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.database import SessionLocal
from database import models

db = SessionLocal()

# Buscar todos os lançamentos de provisão (débito em 3.3)
provisoes = db.query(models.LancamentoContabil).filter(
    models.LancamentoContabil.conta_debito_id == 23,  # 3.3 Lucros Acumulados
    models.LancamentoContabil.tipo_lancamento == 'provisao'
).order_by(models.LancamentoContabil.data).all()

print("=== LANÇAMENTOS DE PROVISÃO (Débito em 3.3) ===\n")
for lanc in provisoes:
    conta_credito = db.query(models.PlanoDeContas).get(lanc.conta_credito_id)
    status = "✓ PAGO" if lanc.pago else "✗ NÃO PAGO"
    data_pag = f" em {lanc.data_pagamento}" if lanc.data_pagamento else ""
    print(f"{lanc.data} - R$ {lanc.valor:8.2f} - D 3.3 / C {conta_credito.codigo} - {status}{data_pag}")
    print(f"  Histórico: {lanc.historico}")
    print(f"  ID: {lanc.id}, Tipo: {lanc.tipo_lancamento}")
    print()

print(f"\nTotal de provisões: {len(provisoes)}")
print(f"Provisões pagas: {sum(1 for p in provisoes if p.pago)}")
print(f"Provisões não pagas: {sum(1 for p in provisoes if not p.pago)}")

# Calcular saldo considerando apenas os pagos
total_provisoes = sum(p.valor for p in provisoes)
provisoes_pagas = sum(p.valor for p in provisoes if p.pago)
provisoes_pendentes = sum(p.valor for p in provisoes if not p.pago)

print(f"\nValor total provisionado: R$ {total_provisoes:.2f}")
print(f"Valor já pago: R$ {provisoes_pagas:.2f}")
print(f"Valor pendente: R$ {provisoes_pendentes:.2f}")

db.close()
