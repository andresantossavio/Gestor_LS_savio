"""
Migration: Adicionar contas de receitas, impostos e lucros a distribuir
Adiciona contas necessárias para integração DRE → Balanço Patrimonial
"""
from database.database import SessionLocal
from database.models import PlanoDeContas, Socio


def adicionar_contas_faltantes():
    """Adiciona contas que faltam no plano de contas"""
    db = SessionLocal()
    
    try:
        # Verificar se conta 2.1.7 já existe (última conta da migration)
        conta_2_1_7 = db.query(PlanoDeContas).filter_by(codigo="2.1.7").first()
        if conta_2_1_7:
            print("⚠️  Contas já foram adicionadas anteriormente")
            return
        
        # Buscar contas pai existentes
        conta_4 = db.query(PlanoDeContas).filter_by(codigo="4").first()
        conta_5_1 = db.query(PlanoDeContas).filter_by(codigo="5.1").first()
        conta_5_3 = db.query(PlanoDeContas).filter_by(codigo="5.3").first()
        conta_2_1 = db.query(PlanoDeContas).filter_by(codigo="2.1").first()
        
        if not all([conta_4, conta_5_1, conta_5_3, conta_2_1]):
            print("❌ Erro: Contas pai não encontradas no plano de contas")
            return
        
        contas_novas = []
        
        # Verificar e criar apenas contas que não existem
        # 1. Receitas Operacionais (4.1)
        conta_4_1_obj = db.query(PlanoDeContas).filter_by(codigo="4.1").first()
        if not conta_4_1_obj:
            conta_4_1_obj = PlanoDeContas(
                codigo="4.1",
                descricao="Receitas Operacionais",
                tipo="Receita",
                natureza="Credora",
                nivel=2,
                aceita_lancamento=False,
                pai_id=conta_4.id,
                ativo=True
            )
            db.add(conta_4_1_obj)
            db.flush()
            contas_novas.append("4.1 - Receitas Operacionais")
        
        # 2. Receita de Honorários (4.1.1)
        conta_4_1_1 = db.query(PlanoDeContas).filter_by(codigo="4.1.1").first()
        if not conta_4_1_1:
            conta_4_1_1 = PlanoDeContas(
                codigo="4.1.1",
                descricao="Receita de Honorários",
                tipo="Receita",
                natureza="Credora",
                nivel=3,
                aceita_lancamento=True,
                pai_id=conta_4_1_obj.id,
                ativo=True
            )
            db.add(conta_4_1_1)
            contas_novas.append("4.1.1 - Receita de Honorários")
        
        # 3. INSS Patronal (5.1.3)
        conta_5_1_3 = db.query(PlanoDeContas).filter_by(codigo="5.1.3").first()
        if not conta_5_1_3:
            conta_5_1_3 = PlanoDeContas(
                codigo="5.1.3",
                descricao="Encargos Sociais (INSS Patronal)",
                tipo="Despesa",
                natureza="Devedora",
                nivel=3,
                aceita_lancamento=True,
                pai_id=conta_5_1.id,
                ativo=True
            )
            db.add(conta_5_1_3)
            contas_novas.append("5.1.3 - Encargos Sociais (INSS Patronal)")
        
        # 4. Simples Nacional (5.3.1)
        conta_5_3_1 = db.query(PlanoDeContas).filter_by(codigo="5.3.1").first()
        if not conta_5_3_1:
            conta_5_3_1 = PlanoDeContas(
                codigo="5.3.1",
                descricao="Simples Nacional",
                tipo="Despesa",
                natureza="Devedora",
                nivel=3,
                aceita_lancamento=True,
                pai_id=conta_5_3.id,
                ativo=True
            )
            db.add(conta_5_3_1)
            contas_novas.append("5.3.1 - Simples Nacional")
        
        # 5. INSS a Recolher (2.1.5)
        conta_2_1_5 = db.query(PlanoDeContas).filter_by(codigo="2.1.5").first()
        if not conta_2_1_5:
            conta_2_1_5 = PlanoDeContas(
                codigo="2.1.5",
                descricao="INSS a Recolher",
                tipo="Passivo",
                natureza="Credora",
                nivel=3,
                aceita_lancamento=True,
                pai_id=conta_2_1.id,
                ativo=True
            )
            db.add(conta_2_1_5)
            contas_novas.append("2.1.5 - INSS a Recolher")
        
        # 6. Lucros a Distribuir (2.1.7) - Sintética
        conta_2_1_7 = PlanoDeContas(
            codigo="2.1.7",
            descricao="Lucros a Distribuir",
            tipo="Passivo",
            natureza="Credora",
            nivel=3,
            aceita_lancamento=False,
            pai_id=conta_2_1.id,
            ativo=True
        )
        db.add(conta_2_1_7)
        db.flush()
        contas_novas.append("2.1.7 - Lucros a Distribuir (sintética)")
        
        # 7. Contas individuais por sócio (2.1.7.X)
        socios = db.query(Socio).order_by(Socio.id).all()
        for idx, socio in enumerate(socios, start=1):
            codigo_socio = f"2.1.7.{idx}"
            conta_socio = PlanoDeContas(
                codigo=codigo_socio,
                descricao=f"Lucros a Distribuir - {socio.nome}",
                tipo="Passivo",
                natureza="Credora",
                nivel=4,
                aceita_lancamento=True,
                pai_id=conta_2_1_7.id,
                ativo=True
            )
            db.add(conta_socio)
            contas_novas.append(f"{codigo_socio} - Lucros a Distribuir - {socio.nome}")
        
        db.commit()
        
        print(f"✅ Migration concluída! {len(contas_novas)} contas adicionadas:")
        for conta in contas_novas:
            print(f"   - {conta}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro durante migration: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Iniciando migration: adicionar_contas_receitas_impostos")
    adicionar_contas_faltantes()
    print("✅ Migration finalizada")
