#!/usr/bin/env python
"""
Script para testar o balanço com ajustes em tempo real
"""
from database.database import SessionLocal
from database.crud_plano_contas import gerar_balanco_patrimonial
import json

db = SessionLocal()

print("=" * 60)
print("TESTE: Balanço de Novembro 2025 (Desconsolidado)")
print("=" * 60)

bal = gerar_balanco_patrimonial(db, 11, 2025)

print("\n📊 METADADOS:")
print(json.dumps(bal['metadata'], indent=2))

print("\n💰 PASSIVO - Impostos a Pagar:")
passivo_circulante = next((x for x in bal['passivo'][0]['subgrupos'] if x['codigo']=='2.1'), None)

if passivo_circulante:
    # Simples a Pagar
    c214 = next((x for x in passivo_circulante['subgrupos'] if x['codigo']=='2.1.4'), None)
    if c214:
        print(f"  2.1.4 - Simples a Pagar: R$ {c214['saldo']:.2f}")
    else:
        print("  2.1.4 - Simples a Pagar: não encontrado")
    
    # INSS a Recolher
    c215 = next((x for x in passivo_circulante['subgrupos'] if x['codigo']=='2.1.5'), None)
    if c215:
        print(f"  2.1.5 - INSS a Recolher: R$ {c215['saldo']:.2f}")
    else:
        print("  2.1.5 - INSS a Recolher: não encontrado")

print("\n" + "=" * 60)
print("TESTE: Balanço de Dezembro 2025")
print("=" * 60)

bal_dez = gerar_balanco_patrimonial(db, 12, 2025)

print("\n📊 METADADOS:")
print(json.dumps(bal_dez['metadata'], indent=2))

print("\n💰 PASSIVO - Impostos a Pagar:")
passivo_circulante_dez = next((x for x in bal_dez['passivo'][0]['subgrupos'] if x['codigo']=='2.1'), None)

if passivo_circulante_dez:
    # Simples a Pagar
    c214_dez = next((x for x in passivo_circulante_dez['subgrupos'] if x['codigo']=='2.1.4'), None)
    if c214_dez:
        print(f"  2.1.4 - Simples a Pagar: R$ {c214_dez['saldo']:.2f}")
    
    # INSS a Recolher
    c215_dez = next((x for x in passivo_circulante_dez['subgrupos'] if x['codigo']=='2.1.5'), None)
    if c215_dez:
        print(f"  2.1.5 - INSS a Recolher: R$ {c215_dez['saldo']:.2f}")

db.close()
