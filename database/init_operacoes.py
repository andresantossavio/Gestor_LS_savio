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
                "codigo": "APLICAR_RESERVA_CDB",
                "nome": "Aplicar Reserva Legal em CDB",
                "descricao": "Destinar 10% do lucro líquido para reserva legal (PL) e aplicar em CDB. Lançamentos: 1) D-Lucros Acum / C-Reserva (sócio); 2) D-Aplicação CDB / C-Caixa Corrente. Exige informar sócio.",
                "ativo": True,
                "ordem": 2
            },
            {
                "codigo": "PROVISIONAR_SIMPLES",
                "nome": "Provisionar Simples Nacional",
                "descricao": "Registrar despesa de Simples Nacional do mês. Lançamento: D-Despesa Simples / C-Simples a Recolher. Valor: imposto calculado (informado manualmente).",
                "ativo": True,
                "ordem": 3
            },
            {
                "codigo": "SEPARAR_OBRIGACOES_FISCAIS",
                "nome": "Separar Obrigações Fiscais",
                "descricao": "Separar dinheiro para INSS e Simples Nacional, aplicando direto em CDB. Lançamento: D-CDB - Obrigações Fiscais / C-Caixa Corrente. Valor: soma de INSS + Simples.",
                "ativo": True,
                "ordem": 4
            },
            {
                "codigo": "SEPARAR_PRO_LABORE",
                "nome": "Separar Pró-labore",
                "descricao": "Separar dinheiro para pró-labore, aplicando direto em CDB - Reserva de Lucros. Lançamento: D-CDB - Reserva de Lucros / C-Caixa Corrente. Não afeta DRE.",
                "ativo": True,
                "ordem": 5
            },
            {
                "codigo": "RESGATAR_CDB_OBRIGACOES_FISCAIS",
                "nome": "Resgatar CDB - Obrigações Fiscais",
                "descricao": "Resgatar CDB de obrigações fiscais para caixa corrente. Lançamento: D-Caixa Corrente / C-CDB - Obrigações Fiscais. Executar antes de pagar INSS/Simples.",
                "ativo": True,
                "ordem": 6
            },
            {
                "codigo": "RESGATAR_CDB_LUCROS",
                "nome": "Resgatar CDB - Reserva de Lucros",
                "descricao": "Resgatar CDB de reserva de lucros para caixa corrente. Lançamento: D-Caixa Corrente / C-CDB - Reserva de Lucros. Executar antes de pagar pró-labore ou distribuir lucros.",
                "ativo": True,
                "ordem": 7
            },
            {
                "codigo": "PAGAR_SIMPLES",
                "nome": "Pagar Simples Nacional",
                "descricao": "Efetuar pagamento do Simples Nacional. Lançamento: D-Simples a Recolher / C-Caixa Corrente. Validação: verifica saldo em 'Simples a Recolher' e Caixa. Resgatar CDB antes se necessário.",
                "ativo": True,
                "ordem": 8
            },
            {
                "codigo": "PAGAR_PRO_LABORE",
                "nome": "Pagar Pró-labore ao Sócio",
                "descricao": "Efetuar pagamento de pró-labore provisionado. Lançamento: D-Pró-labore a Pagar / C-Caixa Corrente. Validação: verifica saldo em 'Pró-labore a Pagar' e Caixa. Resgatar CDB antes se necessário.",
                "ativo": True,
                "ordem": 9
            },
            {
                "codigo": "PRO_LABORE",
                "nome": "Provisionar Pró-labore",
                "descricao": "Registrar despesa de pró-labore (valor bruto). Lançamento: D-Despesa Pró-labore / C-Pró-labore a Pagar. Não paga, apenas provisiona.",
                "ativo": True,
                "ordem": 11
            },
            {
                "codigo": "INSS_PESSOAL",
                "nome": "INSS Pessoal (sobre Pró-labore)",
                "descricao": "Provisionar INSS retido do pró-labore. Lançamento: D-Despesa Pró-labore / C-INSS a Recolher",
                "ativo": True,
                "ordem": 12
            },
            {
                "codigo": "INSS_PATRONAL",
                "nome": "INSS Patronal",
                "descricao": "Provisionar INSS patronal sobre pró-labore. Lançamento: D-Despesa INSS patronal / C-INSS a Recolher",
                "ativo": True,
                "ordem": 13
            },
            {
                "codigo": "PAGAR_INSS",
                "nome": "Pagar INSS",
                "descricao": "Efetuar pagamento do INSS acumulado. Lançamento: D-INSS a Recolher / C-Caixa Corrente. Validação: verifica saldo em 'INSS a Recolher' e Caixa. Resgatar CDB antes se necessário.",
                "ativo": True,
                "ordem": 10
            },
            {
                "codigo": "APLICAR_LUCROS_CDB",
                "nome": "Aplicar Lucros em CDB",
                "descricao": "Guardar dinheiro destinado à distribuição de lucros em CDB - Reserva de Lucros. Lançamento: D-CDB - Reserva de Lucros / C-Caixa Corrente. Executar após apuração, antes da distribuição.",
                "ativo": True,
                "ordem": 14
            },
            {
                "codigo": "ADIANTAR_LUCROS",
                "nome": "Adiantar Lucros ao Sócio",
                "descricao": "Distribuir lucros antecipadamente (antes da apuração) usando reserva individual do sócio. Lançamento: D-Reserva do Sócio / C-Caixa Corrente. Exige informar sócio. Não depende de lucros acumulados.",
                "ativo": True,
                "ordem": 15
            },
            {
                "codigo": "DISTRIBUIR_LUCROS",
                "nome": "Distribuir Lucros",
                "descricao": "Distribuir lucros aos sócios. Lançamento: D-Lucros Acum. / C-Caixa Corrente. Validação: verifica saldo em 'Lucros Acumulados'",
                "ativo": True,
                "ordem": 16
            },
            {
                "codigo": "PAGAR_DESPESA_FUNDO",
                "nome": "Pagar Despesa Geral",
                "descricao": "Registrar pagamento de despesas diversas. Lançamento: D-Despesa (escolher subconta) / C-Caixa Corrente",
                "ativo": True,
                "ordem": 17
            },
            {
                "codigo": "RESGATAR_CDB_RESERVA",
                "nome": "Resgatar CDB da Reserva Legal",
                "descricao": "Resgatar aplicação CDB e reverter reserva legal. Lançamentos: 1) D-Caixa Corrente / C-Aplicação CDB; 2) D-Reserva (sócio) / C-Lucros Acum. Exige informar sócio.",
                "ativo": True,
                "ordem": 18
            },
            {
                "codigo": "RECONHECER_RENDIMENTO_CDB",
                "nome": "Reconhecer Rendimento de CDB",
                "descricao": "Contabilizar juros/rendimentos ganhos nas aplicações CDB. Usuário escolhe qual CDB teve rendimento. Lançamento: D-CDB [específico] / C-Receitas Financeiras. Aumenta saldo do CDB e reconhece receita.",
                "ativo": True,
                "ordem": 19
            },
            {
                "codigo": "APURAR_RESULTADO",
                "nome": "Apurar Resultado do Período",
                "descricao": "Transferir o lucro líquido da DRE para Lucros Acumulados. Executar ao final do mês. Lançamento: D-4.9.9 (conta técnica) / C-3.3 (Lucros Acumulados). Valor: lucro líquido apurado (informado manualmente).",
                "ativo": True,
                "ordem": 20
            },
            {
                "codigo": "RECONHECER_RESERVA_LEGAL",
                "nome": "Reconhecer Reserva Legal no PL",
                "descricao": "Transferir lucros apurados para reserva legal do sócio. Lançamento: D-Lucros Acumulados / C-Reserva do Sócio (3.2.1.X). Executar após APURAR_RESULTADO para reconhecer no patrimônio líquido os valores aplicados em CDB de Reserva Legal durante o mês. Exige informar sócio.",
                "ativo": True,
                "ordem": 21
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
