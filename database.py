# CAMADA DE BANCO DE DADOS: configura a conexão com o banco
# Separamos aqui para não misturar com as rotas

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

URL_DO_BANCO = "sqlite:///./produtos.db"

engine = create_engine(URL_DO_BANCO, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Essa função entrega uma conexão com o banco para cada requisição e fecha automaticamente quando termina
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
