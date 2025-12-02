import warnings
warnings.filterwarnings('ignore')
import sys
sys.path.insert(0, '/app')

from database.database import SessionLocal
from database import models

db = SessionLocal()
contas = db.query(models.PlanoDeContas).filter(
    models.PlanoDeContas.codigo.like('3.%')
).order_by(models.PlanoDeContas.codigo).all()

for c in contas:
    print(f"{c.codigo} {c.descricao}: aceita={c.aceita_lancamento}")

db.close()
