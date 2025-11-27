from database.database import Base, engine
from database.models import Usuario, Cliente, Processo, Pagamento, Andamento, Tarefa, Anexo, TipoAndamento, TipoTarefa, Socio, ConfiguracaoContabil, Entrada, Despesa, EntradaSocio, DespesaSocio, PlanoDeContas, LancamentoContabil, Fundo

print("Criando tabelas...")
Base.metadata.create_all(bind=engine)
print("Banco criado com sucesso!")
