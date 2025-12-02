"""
Teste da nova lógica de INSS do administrador
"""
from database.database import SessionLocal
from database.models import Socio
from database.crud_pagamentos_pendentes import gerar_pendencias_entrada
from datetime import date

db = SessionLocal()

print("=" * 80)
print("TESTE DA NOVA LÓGICA DE PAGAMENTOS PENDENTES")
print("=" * 80)

# Cenário de teste
valor_entrada = 10000.00  # R$ 10.000,00
receita_12m = 100000.00   # R$ 100.000,00 (para calcular Simples)

# Busca sócios
socios = db.query(Socio).all()
print(f"\n1. Sócios cadastrados: {len(socios)}")
for s in socios:
    print(f"   - {s.nome}: {s.funcao}, {s.percentual}%")

# Simula dados de sócios para teste - PERCENTUAIS POR ENTRADA
# André contribuiu 80%, Bruna 20% nesta entrada específica
socios_data = [
    {"id": 1, "nome": "André (Admin)", "percentual": 80.0, "funcao": "Administrador", "is_admin": True},
    {"id": 2, "nome": "Bruna", "percentual": 20.0, "funcao": "Sócio", "is_admin": False}
]

print("\n2. Simulando entrada de R$ 10.000,00")
print(f"   Contribuição: André 80%, Bruna 20%")
print(f"   Receita 12m: R$ {receita_12m:,.2f}")

# Testa geração de pendências
try:
    pendencias = gerar_pendencias_entrada(
        db=db,
        entrada_id=999,  # ID fictício para teste
        valor_entrada=valor_entrada,
        mes=12,
        ano=2025,
        receita_12m=receita_12m,
        socios=socios_data,
        administrador_id=1
    )
    
    print(f"\n3. Pendências geradas: {len(pendencias)}")
    print("\n" + "-" * 80)
    
    total_pendencias = 0.0
    for p in pendencias:
        print(f"\n{p.tipo}: {p.descricao}")
        print(f"   Valor: R$ {p.valor:,.2f}")
        total_pendencias += p.valor
    
    print("\n" + "-" * 80)
    print(f"\n4. RESUMO:")
    print(f"   Entrada: R$ {valor_entrada:,.2f}")
    print(f"   Total Pendências: R$ {total_pendencias:,.2f}")
    print(f"   Diferença: R$ {(valor_entrada - total_pendencias):,.2f}")
    
    # Verifica a lógica específica do INSS
    inss_pendencia = next((p for p in pendencias if p.tipo == "INSS"), None)
    if inss_pendencia:
        print(f"\n5. VALIDAÇÃO INSS:")
        print(f"   INSS Total na guia: R$ {inss_pendencia.valor:,.2f}")
        print(f"   Descrição: {inss_pendencia.descricao}")
        
        # Cálculo esperado
        lucro_apos_simples = valor_entrada * 0.955  # Aproximado (depende da faixa)
        pro_labore_bruto = lucro_apos_simples * 0.05
        pro_labore_admin = min(pro_labore_bruto, 1518.00)
        inss_patronal = pro_labore_admin * 0.20
        inss_retido = pro_labore_admin * 0.11
        inss_total_esperado = inss_patronal + inss_retido
        
        print(f"\n   Cálculo esperado:")
        print(f"   - Lucro após Simples: R$ {lucro_apos_simples:,.2f}")
        print(f"   - Pró-labore bruto (5%): R$ {pro_labore_bruto:,.2f}")
        print(f"   - Pró-labore admin (limitado): R$ {pro_labore_admin:,.2f}")
        print(f"   - INSS 20% patronal: R$ {inss_patronal:,.2f}")
        print(f"   - INSS 11% admin: R$ {inss_retido:,.2f}")
        print(f"   - INSS Total: R$ {inss_total_esperado:,.2f}")
        
        diferenca = abs(inss_pendencia.valor - inss_total_esperado)
        if diferenca < 0.01:  # Tolerância de 1 centavo
            print(f"\n   ✓ INSS calculado corretamente!")
        else:
            print(f"\n   ⚠ Diferença: R$ {diferenca:.2f}")
    
    # Rollback para não salvar no banco
    db.rollback()
    print("\n" + "=" * 80)
    print("✓ Teste concluído (rollback aplicado, nada foi salvo)")
    print("=" * 80)
    
except Exception as e:
    print(f"\n✗ ERRO: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
