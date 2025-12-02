"""Script de migração para padronizar percentuais de EntradaSocio.

Objetivo: Converter registros antigos onde o percentual foi salvo como fração (ex: 0.5 para 50%)
para o novo padrão inteiro (0-100). Critério: valores <= 1.0 serão multiplicados por 100.

Uso:
    python standardize_percentuais.py

Recomendações:
 - Execute com backup do banco.
 - Pode ser reaplicado sem efeitos colaterais significativos (idempotente para valores >1).
"""

from database.database import SessionLocal
from database import models

def run():
    db = SessionLocal()
    try:
        registros = db.query(models.EntradaSocio).all()
        alterados = 0
        for r in registros:
            if r.percentual is not None and r.percentual <= 1.0:
                # Considera que era fração e converte para inteiro
                r.percentual = r.percentual * 100.0
                alterados += 1
        db.commit()
        print(f"Percentuais padronizados. Registros alterados: {alterados}")
    finally:
        db.close()

if __name__ == "__main__":
    run()
