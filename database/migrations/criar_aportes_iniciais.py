"""
Script de migração: Criar aportes iniciais para sócios com capital existente.
Data de abertura da empresa: 24/11/2024
"""

import sys
sys.path.insert(0, r'c:\PythonProjects\GESTOR_LS')

from database.database import SessionLocal
from database import models, crud_contabilidade
from datetime import date

def criar_aportes_iniciais():
    """Cria aportes iniciais para todos os sócios com capital_social > 0."""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("CRIAÇÃO DE APORTES INICIAIS")
        print("=" * 80)
        print()
        
        # Data de abertura da empresa
        data_abertura = date(2024, 11, 24)
        
        # Buscar todos os sócios
        socios = db.query(models.Socio).all()
        print(f"Total de sócios encontrados: {len(socios)}")
        print()
        
        aportes_criados = 0
        
        for socio in socios:
            capital_atual = socio.capital_social or 0.0
            
            if capital_atual <= 0:
                print(f"⊘ {socio.nome}: Capital R$ 0,00 - pulando")
                continue
            
            # Verificar se já existe aporte
            aportes_existentes = crud_contabilidade.get_aportes_socio(db, socio.id)
            if aportes_existentes:
                print(f"⊘ {socio.nome}: Já possui {len(aportes_existentes)} aporte(s) - pulando")
                continue
            
            # Criar aporte inicial
            aporte = crud_contabilidade.create_aporte_capital(
                db=db,
                socio_id=socio.id,
                data=data_abertura,
                valor=capital_atual,
                tipo_aporte='dinheiro',
                descricao='Aporte inicial - Abertura da empresa 24/11/2024'
            )
            
            aportes_criados += 1
            print(f"✓ {socio.nome}: Criado aporte de R$ {capital_atual:,.2f}")
            
            # Validar que capital_social foi mantido
            db.refresh(socio)
            if abs(socio.capital_social - capital_atual) > 0.01:
                print(f"  ⚠️  AVISO: Capital recalculado difere! Original: R$ {capital_atual:,.2f}, Novo: R$ {socio.capital_social:,.2f}")
        
        print()
        print("=" * 80)
        print(f"MIGRAÇÃO CONCLUÍDA: {aportes_criados} aporte(s) criado(s)")
        print("=" * 80)
        
        # Exibir resumo
        print()
        print("Resumo de Capital Social por Sócio:")
        print("-" * 80)
        
        for socio in socios:
            aportes = crud_contabilidade.get_aportes_socio(db, socio.id)
            total_aportes = sum(a.valor for a in aportes if a.tipo_aporte != 'retirada')
            total_retiradas = sum(a.valor for a in aportes if a.tipo_aporte == 'retirada')
            
            print(f"{socio.nome}:")
            print(f"  Capital Social: R$ {socio.capital_social:,.2f}")
            print(f"  Aportes: {len([a for a in aportes if a.tipo_aporte != 'retirada'])} (R$ {total_aportes:,.2f})")
            if total_retiradas > 0:
                print(f"  Retiradas: {len([a for a in aportes if a.tipo_aporte == 'retirada'])} (R$ {total_retiradas:,.2f})")
            print()
        
    except Exception as e:
        db.rollback()
        print()
        print("=" * 80)
        print("ERRO durante a migração:")
        print("=" * 80)
        print(str(e))
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    criar_aportes_iniciais()
