#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

resp = requests.get('http://localhost:8000/api/contabilidade/balanco?mes=12&ano=2025')
data = resp.json()

pl = data['patrimonio_liquido'][0]
print(f"Total PL API: R$ {pl['saldo']:.2f}\n")

for sub in pl['subgrupos']:
    print(f"{sub['codigo']} {sub['nome']}: R$ {sub['saldo']:.2f}")
    if sub.get('subgrupos'):
        for subsub in sub['subgrupos']:
            print(f"  {subsub['codigo']} {subsub['nome']}: R$ {subsub['saldo']:.2f}")
