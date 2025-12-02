"""
Script para validar se os cálculos de pagamentos pendentes estão corretos
comparando com a API de pró-labore
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database.database import SessionLocal
from database.models import Entrada, EntradaSocio, PagamentoPendente
from database import crud_contabilidade
from utils.simples import calcular_faixa_simples, calcular_imposto_simples
from datetime import date
from sqlalchemy import func

def validar_entrada(db, entrada_id):
    """Valida os cálculos de uma entrada específica"""
    entrada = db.query(Entrada).filter(Entrada.id == entrada_id).first()
    if not entrada:
        print(f"❌ Entrada {entrada_id} não encontrada")
        return False
    
    print(f"\n{'='*80}")
    print(f"VALIDANDO ENTRADA {entrada.id}")
    print(f"Cliente: {entrada.cliente}")
    print(f"Data: {entrada.data}")
    print(f"Valor: R$ {entrada.valor:.2f}")
    print(f"{'='*80}")
    
    # Buscar mês/ano de referência
    mes = entrada.data.month
    ano = entrada.data.year
    mes_ref = f"{ano}-{mes:02d}"
    
    # Buscar sócios e percentuais
    entradas_socios = db.query(EntradaSocio).filter(
        EntradaSocio.entrada_id == entrada.id
    ).all()
    
    print(f"\nSÓCIOS:")
    for es in entradas_socios:
        socio = db.query(crud_contabilidade.models.Socio).filter(
            crud_contabilidade.models.Socio.id == es.socio_id
        ).first()
        print(f"  - {socio.nome}: {es.percentual}% {'[ADMIN]' if socio.funcao and 'Administrador' in socio.funcao else ''}")
    
    # Calcular receita 12 meses
    data_inicio = date(ano, mes, 1)
    # Calcular receita acumulada dos últimos 12 meses
    mes_inicio_12m = mes - 11 if mes > 11 else mes + 1
    ano_inicio_12m = ano if mes > 11 else ano - 1
    
    receita_12m = db.query(func.sum(Entrada.valor)).filter(
        Entrada.data >= date(ano_inicio_12m, mes_inicio_12m, 1),
        Entrada.data <= entrada.data
    ).scalar() or 0.0
    
    print(f"\nRECEITA 12 MESES: R$ {receita_12m:.2f}")
    
    # 1. Simples Nacional
    aliquota, deducao, aliquota_efetiva = calcular_faixa_simples(receita_12m, data_inicio, db)
    imposto_simples = calcular_imposto_simples(entrada.valor, aliquota_efetiva)
    print(f"\nSIMPLES NACIONAL:")
    print(f"  Alíquota efetiva: {aliquota_efetiva*100:.2f}%")
    print(f"  Imposto: R$ {imposto_simples:.2f}")
    
    # Buscar pagamento SIMPLES gerado
    pag_simples = db.query(PagamentoPendente).filter(
        PagamentoPendente.entrada_id == entrada.id,
        PagamentoPendente.tipo == "SIMPLES"
    ).first()
    
    if pag_simples:
        print(f"  ✓ Gerado: R$ {pag_simples.valor:.2f} {'✅' if abs(pag_simples.valor - imposto_simples) < 0.01 else '❌'}")
    else:
        print(f"  ❌ Não encontrado!")
    
    # 2. Calcular lucro bruto (entrada - simples)
    lucro_bruto = entrada.valor - imposto_simples
    print(f"\nLUCRO BRUTO (entrada - simples): R$ {lucro_bruto:.2f}")
    
    # 3. Buscar administrador e percentual
    admin_socio = None
    percentual_admin = 0.0
    
    for es in entradas_socios:
        socio = db.query(crud_contabilidade.models.Socio).filter(
            crud_contabilidade.models.Socio.id == es.socio_id
        ).first()
        if socio.funcao and 'Administrador' in socio.funcao:
            admin_socio = socio
            percentual_admin = es.percentual
            break
    
    # 4. Calcular pró-labore usando função de crud_contabilidade
    if admin_socio:
        pro_labore, inss_patronal, inss_pessoal, lucro_liquido = crud_contabilidade.calcular_pro_labore_iterativo(
            lucro_bruto, percentual_admin, 1518.0
        )
        
        print(f"\nPRÓ-LABORE (admin {admin_socio.nome} - {percentual_admin}%):")
        print(f"  Pró-labore bruto: R$ {pro_labore:.2f}")
        print(f"  INSS patronal (20%): R$ {inss_patronal:.2f}")
        print(f"  INSS pessoal (11%): R$ {inss_pessoal:.2f}")
        print(f"  INSS total: R$ {inss_patronal + inss_pessoal:.2f}")
        print(f"  Lucro líquido (bruto - INSS patronal): R$ {lucro_liquido:.2f}")
        
        # Buscar pagamento INSS gerado
        pag_inss = db.query(PagamentoPendente).filter(
            PagamentoPendente.entrada_id == entrada.id,
            PagamentoPendente.tipo == "INSS"
        ).first()
        
        inss_total = inss_patronal + inss_pessoal
        if pag_inss:
            print(f"  ✓ INSS Gerado: R$ {pag_inss.valor:.2f} {'✅' if abs(pag_inss.valor - inss_total) < 0.01 else '❌ ERRO!'}")
            if abs(pag_inss.valor - inss_total) >= 0.01:
                print(f"    Diferença: R$ {pag_inss.valor - inss_total:.2f}")
        else:
            print(f"  ❌ INSS não encontrado!")
        
        # 5. Fundo de reserva (10% do lucro líquido)
        fundo_reserva = lucro_liquido * 0.10
        print(f"\nFUNDO DE RESERVA (10% lucro líquido):")
        print(f"  Calculado: R$ {fundo_reserva:.2f}")
        
        pag_fundo = db.query(PagamentoPendente).filter(
            PagamentoPendente.entrada_id == entrada.id,
            PagamentoPendente.tipo == "FUNDO_RESERVA"
        ).first()
        
        if pag_fundo:
            print(f"  ✓ Gerado: R$ {pag_fundo.valor:.2f} {'✅' if abs(pag_fundo.valor - fundo_reserva) < 0.01 else '❌ ERRO!'}")
            if abs(pag_fundo.valor - fundo_reserva) >= 0.01:
                print(f"    Diferença: R$ {pag_fundo.valor - fundo_reserva:.2f}")
        else:
            print(f"  ❌ Fundo não encontrado!")
        
        # 6. Lucro para distribuir
        lucro_para_distribuir = lucro_liquido - fundo_reserva
        print(f"\nLUCRO PARA DISTRIBUIR: R$ {lucro_para_distribuir:.2f}")
        
        # 7. Distribuição por sócio
        print(f"\nDISTRIBUIÇÃO DE LUCROS:")
        for es in entradas_socios:
            socio = db.query(crud_contabilidade.models.Socio).filter(
                crud_contabilidade.models.Socio.id == es.socio_id
            ).first()
            
            lucro_socio_bruto = lucro_para_distribuir * (es.percentual / 100.0)
            
            # Se é admin, desconta INSS 11%
            if socio.id == admin_socio.id:
                lucro_socio_liquido = lucro_socio_bruto - inss_pessoal
                print(f"  {socio.nome} ({es.percentual}%) [ADMIN]:")
                print(f"    Bruto: R$ {lucro_socio_bruto:.2f}")
                print(f"    INSS 11%: -R$ {inss_pessoal:.2f}")
                print(f"    Líquido: R$ {lucro_socio_liquido:.2f}")
            else:
                lucro_socio_liquido = lucro_socio_bruto
                print(f"  {socio.nome} ({es.percentual}%):")
                print(f"    Líquido: R$ {lucro_socio_liquido:.2f}")
            
            # Buscar pagamento gerado
            pag_lucro = db.query(PagamentoPendente).filter(
                PagamentoPendente.entrada_id == entrada.id,
                PagamentoPendente.tipo == "LUCRO_SOCIO",
                PagamentoPendente.socio_id == socio.id
            ).first()
            
            if pag_lucro:
                print(f"    ✓ Gerado: R$ {pag_lucro.valor:.2f} {'✅' if abs(pag_lucro.valor - lucro_socio_liquido) < 0.01 else '❌ ERRO!'}")
                if abs(pag_lucro.valor - lucro_socio_liquido) >= 0.01:
                    print(f"      Diferença: R$ {pag_lucro.valor - lucro_socio_liquido:.2f}")
            else:
                print(f"    ❌ Lucro não encontrado!")
    
    return True


def main():
    db = SessionLocal()
    
    try:
        # Buscar todas as entradas que têm pagamentos gerados
        entradas_com_pagamentos = db.query(Entrada).join(
            PagamentoPendente, PagamentoPendente.entrada_id == Entrada.id
        ).distinct().order_by(Entrada.data).all()
        
        print(f"\n🔍 VALIDANDO {len(entradas_com_pagamentos)} ENTRADAS COM PAGAMENTOS\n")
        
        for entrada in entradas_com_pagamentos:
            validar_entrada(db, entrada.id)
        
        print(f"\n{'='*80}")
        print("✅ VALIDAÇÃO CONCLUÍDA")
        print(f"{'='*80}\n")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
