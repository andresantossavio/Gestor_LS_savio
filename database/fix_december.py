#!/usr/bin/env python3
"""Script para consolidar dezembro de 2025 e corrigir o PL."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database import crud_contabilidade

db = SessionLocal()

try:
    # Verificar status de dezembro
    dre_dez = crud_contabilidade.buscar_dre_mes(db, "2025-12")
    
    if dre_dez:
        print(f"DRE dezembro 2025:")
        print(f"  Lucro líquido: R$ {dre_dez.lucro_liquido:.2f}")
        print(f"  Consolidado: {dre_dez.consolidado}")
    else:
        print("DRE dezembro 2025: NÃO EXISTE")
    
    print("\n--- Consolidando dezembro 2025 ---")
    dre = crud_contabilidade.consolidar_dre_mes(db, "2025-12", forcar_recalculo=True)
    
    print(f"\nDezembro consolidado com sucesso:")
    print(f"  Lucro líquido: R$ {dre.lucro_liquido:.2f}")
    print(f"  Consolidado: {dre.consolidado}")
    
    # Verificar se fechamento foi criado
    from database.models import LancamentoContabil
    fechamento = db.query(LancamentoContabil).filter_by(
        tipo_lancamento='fechamento_resultado',
        referencia_mes='2025-12'
    ).first()
    
    if fechamento:
        print(f"\nFechamento criado:")
        print(f"  Data: {fechamento.data}")
        print(f"  Valor: R$ {fechamento.valor:.2f}")
        print(f"  Histórico: {fechamento.historico}")
    else:
        print("\nERRO: Fechamento NÃO foi criado!")
    
    # Testar gerar_balanco_patrimonial agora
    from database.crud_plano_contas import gerar_balanco_patrimonial
    print("\n--- Testando gerar_balanco_patrimonial após consolidação ---")
    resultado = gerar_balanco_patrimonial(db, 12, 2025)
    
    # Encontrar 3.3 no resultado
    for item in resultado:
        if item['codigo'] == '3.3':
            print(f"3.3 Lucros Acumulados: R$ {item['saldo']:.2f}")
            break
    
    total_pl = sum(item['saldo'] for item in resultado if item['codigo'].startswith('3.'))
    print(f"Total PL: R$ {total_pl:.2f}")
    
finally:
    db.close()
