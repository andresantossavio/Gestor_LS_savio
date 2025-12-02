#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.database import SessionLocal
from database.crud_plano_contas import gerar_balanco_patrimonial
import json

db = SessionLocal()

try:
    balanco = gerar_balanco_patrimonial(db, 12, 2025)
    
    print("=== BALANÇO PATRIMONIAL DEZEMBRO 2025 ===\n")
    
    # Extrair contas do PL
    pl_data = balanco.get('patrimonio_liquido', [])
    
    def mostrar_contas(grupos, indent=0):
        for grupo in grupos:
            espacos = "  " * indent
            print(f"{espacos}{grupo['codigo']} - {grupo['nome']}: R$ {grupo['saldo']:.2f}")
            if grupo.get('subgrupos'):
                mostrar_contas(grupo['subgrupos'], indent + 1)
    
    print("\nPATRIMÔNIO LÍQUIDO:")
    mostrar_contas(pl_data)
    
    print(f"\n\nTotal PL: R$ {balanco.get('totais', {}).get('patrimonio_liquido', 0):.2f}")
    print(f"Total Ativo: R$ {balanco.get('totais', {}).get('ativo', 0):.2f}")
    print(f"Total Passivo: R$ {balanco.get('totais', {}).get('passivo', 0):.2f}")
    
    print("\n=== JSON completo ===")
    print(json.dumps(balanco, indent=2, ensure_ascii=False))
    
finally:
    db.close()
