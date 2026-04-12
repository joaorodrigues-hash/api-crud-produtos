from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel

# CONFIGURAÇÃO DO BANCO DE DADOS

URL_DO_BANCO = "sqlite:///./produtos.db"
engine = create_engine(URL_DO_BANCO, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    codigo = Column(String, unique=True)
    valor = Column(Float)
    excluido = Column(Boolean, default=False)
    data_alteracao = Column(DateTime, default=datetime.now)
    imagem = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. MOLDE DOS DADOS 
class ProdutoCreate(BaseModel):
    nome: str
    codigo: str
    valor: float
    excluido: bool = False
    imagem: str

# 3. A API (ROTAS)

# SEGURANÇA DA API
chave_api = APIKeyHeader(name="Token-Acesso")

def verificar_senha(token_digitado: str = Security(chave_api)):
    SENHA_CORRETA = "teste123" # A senha que vai exigir
    if token_digitado != SENHA_CORRETA:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso Negado! Senha incorreta."
        )
app = FastAPI()

# CREATE (Criar e salvar no banco)
@app.post("/produtos/", dependencies=[Depends(verificar_senha)])
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    novo_produto = Produto(
        nome=produto.nome,
        codigo=produto.codigo,
        valor=produto.valor,
        excluido=produto.excluido,
        imagem=produto.imagem
    )
    db.add(novo_produto)
    db.commit() # Salva definitivamente no banco!
    db.refresh(novo_produto)
    return novo_produto

# READ (Listar todos os produtos)
@app.get("/produtos/", dependencies=[Depends(verificar_senha)])
def listar_produtos(db: Session = Depends(get_db)):
    produtos = db.query(Produto).all() # Busca tudo na tabela Produtos
    return produtos

# UPDATE (Atualizar um produto existente)
@app.put("/produtos/{produto_id}", dependencies=[Depends(verificar_senha)])
def atualizar_produto(produto_id: int, produto_atualizado: ProdutoCreate, db: Session = Depends(get_db)):
    # 1. Procura o produto pelo ID no banco
    produto_salvo = db.query(Produto).filter(Produto.id == produto_id).first()
    
    # Se não achar, avisa que deu erro
    if not produto_salvo:
        return {"erro": "Produto não encontrado"}
    
    # 2. Se achar, troca os dados antigos pelos novos
    produto_salvo.nome = produto_atualizado.nome
    produto_salvo.codigo = produto_atualizado.codigo
    produto_salvo.valor = produto_atualizado.valor
    produto_salvo.excluido = produto_atualizado.excluido
    produto_salvo.imagem = produto_atualizado.imagem
    produto_salvo.data_alteracao = datetime.now() # Atualiza a hora da modificação!
    
    db.commit() # Salva no banco
    db.refresh(produto_salvo)
    return produto_salvo

# DELETE (Excluir um produto)
@app.delete("/produtos/{produto_id}", dependencies=[Depends(verificar_senha)])
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    # 1. Procura o produto
    produto_salvo = db.query(Produto).filter(Produto.id == produto_id).first()
    
    if not produto_salvo:
        return {"erro": "Produto não encontrado"}
    
    # 2. "Soft Delete" - Em vez de apagar para sempre, só mudamos o campo "excluido" para True
    produto_salvo.excluido = True
    produto_salvo.data_alteracao = datetime.now()
    
    db.commit()
    return {"mensagem": f"Produto {produto_id} marcado como excluído com sucesso!"}