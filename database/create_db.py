from database.database import Base, engine
from database.models import Usuario, Cliente, Processo, Pagamento

print("Criando tabelas...")
Base.metadata.create_all(bind=engine)
print("Banco criado com sucesso!")
