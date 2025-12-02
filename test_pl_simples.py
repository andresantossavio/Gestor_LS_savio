#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.stderr = open('/dev/null', 'w')  # Supress warnings

from database.database import SessionLocal
from database.crud_plano_contas import gerar_balanco_patrimonial
import json

db = SessionLocal()
balanco = gerar_balanco_patrimonial(db, 12, 2025)
db.close()

pl = balanco.get('patrimonio_liquido', [])
if pl and len(pl) > 0:
    print(f"3 - PATRIMÔNIO LÍQUIDO: R$ {pl[0]['saldo']:.2f}")
    for sub in pl[0].get('subgrupos', []):
        print(f"  {sub['codigo']} - {sub['nome']}: R$ {sub['saldo']:.2f}")
        for subsub in sub.get('subgrupos', []):
            print(f"    {subsub['codigo']} - {subsub['nome']}: R$ {subsub['saldo']:.2f}")
