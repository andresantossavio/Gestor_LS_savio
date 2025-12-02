"""
Script para adicionar contas contábeis necessárias para o sistema de pagamentos pendentes
"""
from database.database import SessionLocal
from database.models import PlanoDeContas

db = SessionLocal()

print("=" * 80)
print("ADICIONANDO CONTAS PARA SISTEMA DE PAGAMENTOS PENDENTES")
print("=" * 80)

def buscar_conta_por_codigo(codigo: str):
    return db.query(PlanoDeContas).filter(PlanoDeContas.codigo == codigo).first()

def criar_conta_se_nao_existe(codigo, descricao, tipo, natureza, nivel, pai_codigo=None, aceita_lancamento=True):
    conta = buscar_conta_por_codigo(codigo)
    if conta:
        print(f"✓ Conta {codigo} já existe: {conta.descricao}")
        return conta
    
    pai = None
    if pai_codigo:
        pai = buscar_conta_por_codigo(pai_codigo)
        if not pai:
            print(f"⚠️  Conta pai {pai_codigo} não encontrada para {codigo}")
            return None
    
    conta = PlanoDeContas(
        codigo=codigo,
        descricao=descricao,
        tipo=tipo,
        natureza=natureza,
        nivel=nivel,
        pai_id=pai.id if pai else None,
        aceita_lancamento=aceita_lancamento,
        ativo=True
    )
    db.add(conta)
    db.flush()
    print(f"✓ Conta {codigo} criada: {descricao}")
    return conta

try:
    # Contas no Passivo para provisões
    print("\n1. Criando contas de Passivo:")
    criar_conta_se_nao_existe("2.1.4", "Simples a Pagar", "Passivo", "Credora", 3, "2.1", True)
    criar_conta_se_nao_existe("2.1.5", "INSS a Pagar", "Passivo", "Credora", 3, "2.1", True)
    criar_conta_se_nao_existe("2.1.6", "Lucros a Pagar", "Passivo", "Credora", 3, "2.1", True)
    
    # Contas no PL para distribuição
    print("\n2. Verificando/atualizando contas de PL:")
    
    # Atualizar conta 3.2.1 se existir
    conta_321 = buscar_conta_por_codigo("3.2.1")
    if conta_321:
        conta_321.descricao = "Reserva de Lucros (Fundo Reserva)"
        print(f"✓ Conta 3.2.1 atualizada: {conta_321.descricao}")
    
    # Verificar/criar estrutura 3.4
    conta_34 = buscar_conta_por_codigo("3.4")
    if not conta_34:
        criar_conta_se_nao_existe("3.4", "Lucros Distribuídos", "PL", "Devedora", 2, "3", False)
    else:
        # Atualizar para não aceitar lançamento
        conta_34.aceita_lancamento = False
        conta_34.descricao = "Lucros Distribuídos"
        print(f"✓ Conta 3.4 atualizada: {conta_34.descricao}")
    
    criar_conta_se_nao_existe("3.4.1", "Lucros Distribuídos (Sócios)", "PL", "Devedora", 3, "3.4", True)
    
    db.commit()
    print("\n" + "=" * 80)
    print("✅ Contas adicionadas/atualizadas com sucesso!")
    print("=" * 80)
    
    # Listar contas relevantes
    print("\nContas relevantes para pagamentos pendentes:")
    print("-" * 80)
    for codigo in ["2.1.4", "2.1.5", "2.1.6", "3.2.1", "3.4", "3.4.1", "5.1.3", "5.3.1"]:
        conta = buscar_conta_por_codigo(codigo)
        if conta:
            print(f"{conta.codigo:8s} - {conta.descricao:50s} ({conta.tipo}, {conta.natureza})")
        else:
            print(f"{codigo:8s} - ⚠️  NÃO ENCONTRADA")

except Exception as e:
    print(f"\n❌ Erro: {e}")
    db.rollback()
finally:
    db.close()
