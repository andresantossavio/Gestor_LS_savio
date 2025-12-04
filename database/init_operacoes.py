"""
Script para popular a tabela Operacao com as 8 operações contábeis padronizadas.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database import SessionLocal
from database.models import Operacao


def seed_operacoes():
    """Popula tabela Operacao com as 8 operações padronizadas."""
    
    db = SessionLocal()
    
    try:
        # Verificar se já existem operações
        existing = db.query(Operacao).count()
        if existing > 0:
            print(f"⚠️  Já existem {existing} operações cadastradas.")
            resposta = input("Deseja recriar todas as operações? (s/N): ").strip().lower()
            if resposta != 's':
                print("Operação cancelada.")
                return
            
            # Deletar operações existentes
            db.query(Operacao).delete()
            db.commit()
            print("✅ Operações anteriores removidas.")
        
        # Definir as 8 operações padronizadas
        operacoes = [
            {
                "codigo": "REC_HON",
                "nome": "Receber Honorários",
                "descricao": "Registrar recebimento de honorários de clientes. Lançamento: D-Caixa / C-Receita",
                "ativo": True,
                "ordem": 1
            },
            {
                "codigo": "RESERVAR_FUNDO",
                "nome": "Reservar Fundo",
                "descricao": "Transferir parte dos lucros para fundo de reserva (geralmente 10%). Lançamento: D-Lucros Acum. / C-Reserva",
                "ativo": True,
                "ordem": 2
            },
            {
                "codigo": "PRO_LABORE",
                "nome": "Pró-labore (bruto)",
                "descricao": "Registrar pagamento de pró-labore (valor bruto). Lançamento: D-Despesa Pró-labore / C-Caixa",
                "ativo": True,
                "ordem": 3
            },
            {
                "codigo": "INSS_PESSOAL",
                "nome": "INSS Pessoal (sobre Pró-labore)",
                "descricao": "Provisionar INSS retido do pró-labore. Lançamento: D-Despesa Pró-labore / C-INSS a Recolher",
                "ativo": True,
                "ordem": 4
            },
            {
                "codigo": "INSS_PATRONAL",
                "nome": "INSS Patronal",
                "descricao": "Provisionar INSS patronal sobre pró-labore. Lançamento: D-Despesa INSS patronal / C-INSS a Recolher",
                "ativo": True,
                "ordem": 5
            },
            {
                "codigo": "PAGAR_INSS",
                "nome": "Pagar INSS",
                "descricao": "Efetuar pagamento do INSS acumulado. Lançamento: D-INSS a Recolher / C-Caixa. Validação: verifica saldo em 'INSS a Recolher'",
                "ativo": True,
                "ordem": 6
            },
            {
                "codigo": "DISTRIBUIR_LUCROS",
                "nome": "Distribuir Lucros",
                "descricao": "Distribuir lucros aos sócios. Lançamento: D-Lucros Acum. / C-Caixa. Validação: verifica saldo em 'Lucros Acumulados'",
                "ativo": True,
                "ordem": 7
            },
            {
                "codigo": "PAGAR_DESPESA_FUNDO",
                "nome": "Pagar Despesa via Fundo",
                "descricao": "Registrar pagamento de despesas diversas. Lançamento: D-Outras Despesas / C-Caixa",
                "ativo": True,
                "ordem": 8
            },
            {
                "codigo": "BAIXAR_FUNDO",
                "nome": "Baixa do Fundo",
                "descricao": "Transferir recursos do fundo de reserva de volta para lucros. Lançamento: D-Reserva / C-Lucros Acum. Validação: verifica saldo em 'Reserva'",
                "ativo": True,
                "ordem": 9
            }
        ]
        
        # Inserir operações
        for op_data in operacoes:
            operacao = Operacao(**op_data)
            db.add(operacao)
        
        db.commit()
        print(f"✅ {len(operacoes)} operações cadastradas com sucesso!")
        
        # Listar operações criadas
        print("\n📋 Operações cadastradas:")
        for op in db.query(Operacao).order_by(Operacao.ordem).all():
            print(f"  {op.ordem}. [{op.codigo}] {op.nome}")
            print(f"     {op.descricao}\n")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao cadastrar operações: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Iniciando seed de operações contábeis...\n")
    seed_operacoes()
    print("\n✨ Processo concluído!")
