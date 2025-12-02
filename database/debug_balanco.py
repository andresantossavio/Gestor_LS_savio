import warnings
warnings.filterwarnings('ignore')
import sys
import logging
sys.path.insert(0, '/app')
logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)

from database.database import SessionLocal
from database import models

db = SessionLocal()

# Check all closing entries
entries = db.query(models.LancamentoContabil).filter_by(
    tipo_lancamento='fechamento_resultado'
).all()

print(f"Total fechamentos: {len(entries)}")
print("\nFormato usado nas referências:")
for e in entries[:5]:
    print(f"  {e.referencia_mes}: {e.historico[:60]}")

print("\nCheck específico para 2025-12:")
f = db.query(models.LancamentoContabil).filter_by(
    tipo_lancamento='fechamento_resultado',
    referencia_mes='2025-12'
).first()
print(f"  Existe: {f is not None}")

db.close()
