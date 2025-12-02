#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.database import SessionLocal
from database import models
from datetime import date

db = SessionLocal()

try:
    # Buscar todas as provisões não pagas
    provisoes = db.query(models.LancamentoContabil).filter(
        models.LancamentoContabil.conta_debito_id == 23,  # 3.3 Lucros Acumulados
        models.LancamentoContabil.tipo_lancamento == 'provisao',
        models.LancamentoContabil.pago == False
    ).all()
    
    print(f"=== MARCANDO {len(provisoes)} PROVISÕES COMO PAGAS ===\n")
    
    for prov in provisoes:
        conta_credito = db.query(models.PlanoDeContas).get(prov.conta_credito_id)
        print(f"ID {prov.id}: {prov.data} - R$ {prov.valor:.2f} - D 3.3 / C {conta_credito.codigo}")
        print(f"  Histórico: {prov.historico}")
        
        # Marcar como pago
        prov.pago = True
        prov.data_pagamento = prov.data  # Usar a mesma data da provisão
        prov.valor_pago = prov.valor
        print(f"  ✓ Marcado como pago em {prov.data}")
        print()
    
    # Confirmar as mudanças
    db.commit()
    print(f"\n✓ {len(provisoes)} provisões marcadas como pagas com sucesso!")
    
except Exception as e:
    db.rollback()
    print(f"\n✗ Erro: {e}")
    raise
finally:
    db.close()
