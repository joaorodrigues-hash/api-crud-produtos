# cama que define como os dados são guardados no banco de dados

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Produto(Base):
    __tablename__ = "produtos"

    id             = Column(Integer, primary_key=True, index=True)
    nome           = Column(String, nullable=False)
    codigo         = Column(String, unique=True, nullable=False)
    valor          = Column(Float, nullable=False)
    excluido       = Column(Boolean, default=False)
    data_alteracao = Column(DateTime, default=datetime.now)
    imagem         = Column(String, nullable=True)
