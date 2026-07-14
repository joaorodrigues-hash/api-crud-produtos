# CAMADA R: só as rotas da API ficam aqui
# Importa tudo dos outros arquivos e monta a aplicação

from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db, engine
from models import Base, Produto
from schemas import ProdutoCreate, ProdutoResposta


Base.metadata.create_all(bind=engine)

app = FastAPI()

#  SEGURANÇA
chave_api = APIKeyHeader(name="Token-Acesso")

def verificar_senha(token_digitado: str = Security(chave_api)):
    SENHA_CORRETA = "teste123"
    if token_digitado != SENHA_CORRETA:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso Negado! Senha incorreta."
        )

# MENSAGEM DE ERRO AQUI: 
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    erros = []
    for erro in exc.errors():
        campo = " → ".join(str(c) for c in erro["loc"] if c != "body")
        mensagem = erro["msg"].replace("Value error, ", "")
        erros.append(f"Campo '{campo}': {mensagem}")

    return JSONResponse(
        status_code=422,
        content={"erros_de_validacao": erros}
    )



# CREATE — Criar novo produto
@app.post("/produtos/", response_model=ProdutoResposta, dependencies=[Depends(verificar_senha)])
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    novo_produto = Produto(
        nome=produto.nome,
        codigo=produto.codigo,
        valor=produto.valor,
        excluido=produto.excluido,
        imagem=produto.imagem
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto

# READ — Listar todos os produtos ativos
@app.get("/produtos/", response_model=list[ProdutoResposta], dependencies=[Depends(verificar_senha)])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(Produto).filter(Produto.excluido == False).all()

# UPDATE — Atualizar produto existente
@app.put("/produtos/{produto_id}", response_model=ProdutoResposta, dependencies=[Depends(verificar_senha)])
def atualizar_produto(produto_id: int, produto_atualizado: ProdutoCreate, db: Session = Depends(get_db)):
    produto_salvo = db.query(Produto).filter(Produto.id == produto_id).first()

    if not produto_salvo:
        raise HTTPException(status_code=404, detail=f"Produto com ID {produto_id} não encontrado.")

    produto_salvo.nome           = produto_atualizado.nome
    produto_salvo.codigo         = produto_atualizado.codigo
    produto_salvo.valor          = produto_atualizado.valor
    produto_salvo.excluido       = produto_atualizado.excluido
    produto_salvo.imagem         = produto_atualizado.imagem
    produto_salvo.data_alteracao = datetime.now()

    db.commit()
    db.refresh(produto_salvo)
    return produto_salvo

# DELETE — Soft delete (marca como excluído)
@app.delete("/produtos/{produto_id}", dependencies=[Depends(verificar_senha)])
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto_salvo = db.query(Produto).filter(Produto.id == produto_id).first()

    if not produto_salvo:
        raise HTTPException(status_code=404, detail=f"Produto com ID {produto_id} não encontrado.")

    produto_salvo.excluido       = True
    produto_salvo.data_alteracao = datetime.now()
    db.commit()

    return {"mensagem": f"Produto {produto_id} marcado como excluído com sucesso!"}
