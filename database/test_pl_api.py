#!/usr/bin/env python3
import sys
import os
import warnings
sys.path.insert(0, '/app')

# Suppress all warnings
warnings.filterwarnings('ignore')

# Suppress SQLAlchemy logging
import logging
logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)

from database.database import SessionLocal
from database.crud_plano_contas import gerar_balanco_patrimonial

db = SessionLocal()
balanco = gerar_balanco_patrimonial(db, 12, 2025)

# Find PL section
pl = balanco.get('patrimonioLiquido', [{}])[0]
print(f"Total PL: R$ {pl.get('saldo', 0):.2f}")
print()

for sub in pl.get('subgrupos', []):
    print(f"{sub['codigo']} {sub['nome']}: R$ {sub['saldo']:.2f}")

db.close()
