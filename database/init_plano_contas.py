"""
Inicialização do Plano de Contas Padrão para Escritório de Advocacia
Baseado em padrões contábeis brasileiros
"""
from database.models import PlanoDeContas
from sqlalchemy.orm import Session


def inicializar_plano_contas(db: Session):
    """Cria o plano de contas padrão se não existir"""
    
    # Verificar se já existe
    existing_count = db.query(PlanoDeContas).count()
    if existing_count > 0:
        resposta = input(f"⚠️  Já existem {existing_count} contas cadastradas.\nDeseja recriar todas as contas? (s/N): ")
        if resposta.lower() != 's':
            print("Operação cancelada.")
            return
        # Deletar todas as contas
        print("🗑️  Removendo contas anteriores...")
        db.query(PlanoDeContas).delete()
        db.commit()
        print("✅ Contas anteriores removidas.")
    
    contas = [
        # 1. ATIVO
        {"codigo": "1", "descricao": "ATIVO", "tipo": "Ativo", "natureza": "Devedora", "nivel": 1, "aceita_lancamento": False},
        {"codigo": "1.1", "descricao": "Ativo Circulante", "tipo": "Ativo", "natureza": "Devedora", "nivel": 2, "aceita_lancamento": False, "pai_codigo": "1"},
        {"codigo": "1.1.1", "descricao": "Caixa e Bancos", "tipo": "Ativo", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": False, "pai_codigo": "1.1"},  # Sintética - subcontas de caixa
        {"codigo": "1.1.1.1", "descricao": "Caixa Corrente", "tipo": "Ativo", "natureza": "Devedora", "nivel": 4, "aceita_lancamento": True, "pai_codigo": "1.1.1"},
        {"codigo": "1.1.1.2", "descricao": "Aplicações Financeiras (CDB)", "tipo": "Ativo", "natureza": "Devedora", "nivel": 4, "aceita_lancamento": False, "pai_codigo": "1.1.1"},  # Sintética - subcontas de CDB
        {"codigo": "1.1.1.2.1", "descricao": "CDB - Obrigações Fiscais", "tipo": "Ativo", "natureza": "Devedora", "nivel": 5, "aceita_lancamento": True, "pai_codigo": "1.1.1.2"},
        {"codigo": "1.1.1.2.2", "descricao": "CDB - Reserva de Lucros", "tipo": "Ativo", "natureza": "Devedora", "nivel": 5, "aceita_lancamento": True, "pai_codigo": "1.1.1.2"},
        {"codigo": "1.1.1.2.3", "descricao": "CDB - Reserva Legal", "tipo": "Ativo", "natureza": "Devedora", "nivel": 5, "aceita_lancamento": True, "pai_codigo": "1.1.1.2"},
        {"codigo": "1.1.2", "descricao": "Clientes (Honorários a Receber)", "tipo": "Ativo", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "1.1"},
        {"codigo": "1.1.3", "descricao": "Adiantamentos a Sócios", "tipo": "Ativo", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "1.1"},
        
        {"codigo": "1.2", "descricao": "Ativo Não Circulante", "tipo": "Ativo", "natureza": "Devedora", "nivel": 2, "aceita_lancamento": False, "pai_codigo": "1"},
        {"codigo": "1.2.1", "descricao": "Imobilizado", "tipo": "Ativo", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": False, "pai_codigo": "1.2"},
        {"codigo": "1.2.1.1", "descricao": "Equipamentos e Móveis", "tipo": "Ativo", "natureza": "Devedora", "nivel": 4, "aceita_lancamento": True, "pai_codigo": "1.2.1"},
        {"codigo": "1.2.1.2", "descricao": "(-) Depreciação Acumulada", "tipo": "Ativo", "natureza": "Credora", "nivel": 4, "aceita_lancamento": True, "pai_codigo": "1.2.1"},
        
        {"codigo": "1.2.2", "descricao": "Intangível", "tipo": "Ativo", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": False, "pai_codigo": "1.2"},
        {"codigo": "1.2.2.1", "descricao": "Serviços Capitalizados", "tipo": "Ativo", "natureza": "Devedora", "nivel": 4, "aceita_lancamento": True, "pai_codigo": "1.2.2"},
        
        # 2. PASSIVO
        {"codigo": "2", "descricao": "PASSIVO", "tipo": "Passivo", "natureza": "Credora", "nivel": 1, "aceita_lancamento": False},
        {"codigo": "2.1", "descricao": "Passivo Circulante", "tipo": "Passivo", "natureza": "Credora", "nivel": 2, "aceita_lancamento": False, "pai_codigo": "2"},
        {"codigo": "2.1.1", "descricao": "Fornecedores e Contas a Pagar", "tipo": "Passivo", "natureza": "Credora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "2.1"},
        {"codigo": "2.1.2", "descricao": "Obrigações Fiscais", "tipo": "Passivo", "natureza": "Credora", "nivel": 3, "aceita_lancamento": False, "pai_codigo": "2.1"},
        {"codigo": "2.1.2.1", "descricao": "Simples Nacional a Recolher", "tipo": "Passivo", "natureza": "Credora", "nivel": 4, "aceita_lancamento": True, "pai_codigo": "2.1.2"},
        {"codigo": "2.1.2.2", "descricao": "INSS a Recolher", "tipo": "Passivo", "natureza": "Credora", "nivel": 4, "aceita_lancamento": True, "pai_codigo": "2.1.2"},
        {"codigo": "2.1.3", "descricao": "Obrigações Trabalhistas", "tipo": "Passivo", "natureza": "Credora", "nivel": 3, "aceita_lancamento": False, "pai_codigo": "2.1"},
        {"codigo": "2.1.3.1", "descricao": "Pró-labore a Pagar", "tipo": "Passivo", "natureza": "Credora", "nivel": 4, "aceita_lancamento": True, "pai_codigo": "2.1.3"},
        
        # 3. PATRIMÔNIO LÍQUIDO
        {"codigo": "3", "descricao": "PATRIMÔNIO LÍQUIDO", "tipo": "PL", "natureza": "Credora", "nivel": 1, "aceita_lancamento": False},
        {"codigo": "3.1", "descricao": "Capital Social", "tipo": "PL", "natureza": "Credora", "nivel": 2, "aceita_lancamento": True, "pai_codigo": "3"},
        {"codigo": "3.2", "descricao": "Reservas de Lucros", "tipo": "PL", "natureza": "Credora", "nivel": 2, "aceita_lancamento": False, "pai_codigo": "3"},
        {"codigo": "3.2.1", "descricao": "Reservas Individuais dos Sócios", "tipo": "PL", "natureza": "Credora", "nivel": 3, "aceita_lancamento": False, "pai_codigo": "3.2"},  # Sintética - subcontas por sócio (3.2.1.{socio_id})
        {"codigo": "3.3", "descricao": "Lucros Acumulados", "tipo": "PL", "natureza": "Credora", "nivel": 2, "aceita_lancamento": True, "pai_codigo": "3"},
        {"codigo": "3.4", "descricao": "Lucros Distribuídos", "tipo": "PL", "natureza": "Devedora", "nivel": 2, "aceita_lancamento": False, "pai_codigo": "3"},
        {"codigo": "3.4.1", "descricao": "Lucros Distribuídos (Sócios)", "tipo": "PL", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "3.4"},
        
        # 4. RECEITAS
        {"codigo": "4", "descricao": "RECEITAS", "tipo": "Receita", "natureza": "Credora", "nivel": 1, "aceita_lancamento": False},
        {"codigo": "4.1", "descricao": "Receitas Operacionais", "tipo": "Receita", "natureza": "Credora", "nivel": 2, "aceita_lancamento": False, "pai_codigo": "4"},
        {"codigo": "4.1.1", "descricao": "Receita de Honorários", "tipo": "Receita", "natureza": "Credora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "4.1"},
        
        {"codigo": "4.2", "descricao": "Receitas Financeiras", "tipo": "Receita", "natureza": "Credora", "nivel": 2, "aceita_lancamento": False, "pai_codigo": "4"},
        {"codigo": "4.2.1", "descricao": "Rendimento de CDB", "tipo": "Receita", "natureza": "Credora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "4.2"},
        
        # 5. DESPESAS
        {"codigo": "5", "descricao": "DESPESAS", "tipo": "Despesa", "natureza": "Devedora", "nivel": 1, "aceita_lancamento": False},
        {"codigo": "5.1", "descricao": "Despesas com Pessoal", "tipo": "Despesa", "natureza": "Devedora", "nivel": 2, "aceita_lancamento": False, "pai_codigo": "5"},
        {"codigo": "5.1.1", "descricao": "INSS Pessoal", "tipo": "Despesa", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "5.1"},
        {"codigo": "5.1.2", "descricao": "Salários", "tipo": "Despesa", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "5.1"},
        {"codigo": "5.1.3", "descricao": "INSS Patronal", "tipo": "Despesa", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "5.1"},
        
        {"codigo": "5.2", "descricao": "Despesas Administrativas", "tipo": "Despesa", "natureza": "Devedora", "nivel": 2, "aceita_lancamento": False, "pai_codigo": "5"},
        {"codigo": "5.2.1", "descricao": "Aluguel", "tipo": "Despesa", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "5.2"},
        {"codigo": "5.2.2", "descricao": "Água e Luz", "tipo": "Despesa", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "5.2"},
        {"codigo": "5.2.3", "descricao": "Internet e Telefone", "tipo": "Despesa", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "5.2"},
        {"codigo": "5.2.4", "descricao": "Material de Escritório", "tipo": "Despesa", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "5.2"},
        {"codigo": "5.2.5", "descricao": "Depreciação", "tipo": "Despesa", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "5.2"},
        
        {"codigo": "5.3", "descricao": "Impostos e Contribuições", "tipo": "Despesa", "natureza": "Devedora", "nivel": 2, "aceita_lancamento": False, "pai_codigo": "5"},
        {"codigo": "5.3.1", "descricao": "Simples Nacional", "tipo": "Despesa", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "5.3"},
        {"codigo": "5.3.2", "descricao": "Outras Taxas", "tipo": "Despesa", "natureza": "Devedora", "nivel": 3, "aceita_lancamento": True, "pai_codigo": "5.3"},
    ]
    
    # Criar contas em duas passadas (primeiro sem pai, depois com pai)
    contas_criadas = {}
    
    # Primeira passada: criar contas sem relacionamento pai
    for conta_data in contas:
        conta = PlanoDeContas(
            codigo=conta_data["codigo"],
            descricao=conta_data["descricao"],
            tipo=conta_data["tipo"],
            natureza=conta_data["natureza"],
            nivel=conta_data["nivel"],
            aceita_lancamento=conta_data["aceita_lancamento"],
            ativo=True
        )
        db.add(conta)
        db.flush()  # Garante que o ID seja gerado
        contas_criadas[conta_data["codigo"]] = conta
    
    # Segunda passada: atualizar relacionamentos pai
    for conta_data in contas:
        if "pai_codigo" in conta_data:
            conta = contas_criadas[conta_data["codigo"]]
            pai = contas_criadas[conta_data["pai_codigo"]]
            conta.pai_id = pai.id
    
    db.commit()
    print(f"✅ Plano de contas inicializado com {len(contas)} contas")
