"""
Script para gerar pagamentos pendentes retroativos de todas as entradas existentes
"""
from database.database import SessionLocal
from database.models import Entrada, EntradaSocio, Socio
from database.crud_pagamentos_pendentes import gerar_pendencias_entrada
from utils.simples import calcular_receita_12_meses
from datetime import datetime

db = SessionLocal()

print("=" * 80)
print("GERAÇÃO RETROATIVA DE PAGAMENTOS PENDENTES")
print("=" * 80)

try:
    # Buscar todas as entradas (exceto teste de integração)
    entradas = db.query(Entrada).filter(
        ~Entrada.cliente.like('%Teste Integração%')
    ).order_by(Entrada.data).all()
    
    print(f"\nTotal de entradas encontradas: {len(entradas)}")
    
    if not entradas:
        print("\n✅ Não há entradas para processar")
        db.close()
        exit(0)
    
    print("\nEntradas:")
    for e in entradas:
        print(f"  - {e.id}: {e.data} | {e.cliente} | R$ {e.valor:,.2f}")
    
    print(f"\n⚠️  Serão geradas pendências para {len(entradas)} entradas")
    print("\nDeseja continuar? (digite 'SIM' para confirmar)")
    resposta = input("> ").strip().upper()
    
    if resposta != "SIM":
        print("\n❌ Operação cancelada pelo usuário")
        db.close()
        exit(0)
    
    # Processar cada entrada
    print("\nProcessando entradas...")
    total_pendencias = 0
    erros = []
    
    for entrada in entradas:
        try:
            # Buscar sócios da entrada
            socios_entrada = db.query(EntradaSocio).filter(
                EntradaSocio.entrada_id == entrada.id
            ).all()
            
            if not socios_entrada:
                print(f"  ⚠️  Entrada {entrada.id} sem sócios associados - PULANDO")
                continue
            
            # Calcular receita 12 meses
            receita_12m = calcular_receita_12_meses(db, entrada.data)
            
            # Montar dados dos sócios
            socios_data = []
            administrador_id = None
            
            for se in socios_entrada:
                socio = db.query(Socio).filter(Socio.id == se.socio_id).first()
                if not socio:
                    continue
                
                is_admin = socio.funcao and "administrador" in socio.funcao.lower()
                if is_admin:
                    administrador_id = socio.id
                
                socios_data.append({
                    "id": socio.id,
                    "nome": socio.nome,
                    "percentual": se.percentual,
                    "funcao": socio.funcao,
                    "is_admin": is_admin
                })
            
            if not socios_data:
                print(f"  ⚠️  Entrada {entrada.id} sem sócios válidos - PULANDO")
                continue
            
            # Gerar pendências
            pendencias = gerar_pendencias_entrada(
                db=db,
                entrada_id=entrada.id,
                valor_entrada=entrada.valor,
                mes=entrada.data.month,
                ano=entrada.data.year,
                receita_12m=receita_12m,
                socios=socios_data,
                administrador_id=administrador_id
            )
            
            total_pendencias += len(pendencias)
            print(f"  ✓ Entrada {entrada.id} ({entrada.data}): {len(pendencias)} pendências geradas")
            
        except Exception as e:
            erro_msg = f"Entrada {entrada.id}: {str(e)}"
            erros.append(erro_msg)
            print(f"  ❌ {erro_msg}")
    
    print("\n" + "=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)
    print(f"Total de pendências geradas: {total_pendencias}")
    print(f"Entradas processadas com sucesso: {len(entradas) - len(erros)}")
    print(f"Erros: {len(erros)}")
    
    if erros:
        print("\nDetalhes dos erros:")
        for erro in erros:
            print(f"  - {erro}")
    
    print("\n✅ Migração concluída!")

except Exception as e:
    print(f"\n❌ Erro fatal: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n" + "=" * 80)
print("Operação concluída")
print("=" * 80)
