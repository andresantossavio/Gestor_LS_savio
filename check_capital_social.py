#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.database import SessionLocal
from database import models

db = SessionLocal()

# Check account 3.1
conta_31 = db.query(models.PlanoDeContas).filter(models.PlanoDeContas.id == 20).first()
print(f"Conta 3.1 - {conta_31.descricao}")
print(f"Código: {conta_31.codigo}")
print(f"Natureza: {conta_31.natureza}")
print(f"Aceita lançamento: {conta_31.aceita_lancamento}")
print()

# Check for any ledger entries
debitos = db.query(models.LancamentoContabil).filter(models.LancamentoContabil.conta_debito_id == 20).all()
creditos = db.query(models.LancamentoContabil).filter(models.LancamentoContabil.conta_credito_id == 20).all()

print(f"Débitos em 3.1: {len(debitos)}")
for lanc in debitos:
    print(f"  {lanc.data} - R$ {lanc.valor:.2f} - {lanc.historico}")

print(f"\nCréditos em 3.1: {len(creditos)}")
for lanc in creditos:
    print(f"  {lanc.data} - R$ {lanc.valor:.2f} - {lanc.historico}")

db.close()
