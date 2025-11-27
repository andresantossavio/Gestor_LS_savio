import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Define o diretório raiz do projeto (uma pasta acima do diretório atual 'database')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define a URL do banco de dados para criar o arquivo 'gestor_ls.db' na raiz do projeto
DATABASE_URL = f"sqlite:///{os.path.join(PROJECT_ROOT, 'gestor_ls.db')}"

# Cria o motor do banco de dados.
# echo=True é ótimo para debug, pois mostra os comandos SQL executados.
# Pode ser removido ou definido como False para "silenciar" o log.
engine = create_engine(DATABASE_URL, echo=True)

# Abordagem moderna para criar a classe Base declarativa no SQLAlchemy 2.0+
class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
