import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import get_db
from models import Base

# cria um BD SEPARADO só para os testes assim os testes não afetam o banco real
BANCO_DE_TESTE = "sqlite:///./teste.db"
engine_teste = create_engine(BANCO_DE_TESTE, connect_args={"check_same_thread": False})
SessionTeste = sessionmaker(autocommit=False, autoflush=False, bind=engine_teste)

# Substitui o banco real pelo banco de teste durante os testes
def get_db_teste():
    db = SessionTeste()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = get_db_teste

# cria as tabelas no teste
Base.metadata.create_all(bind=engine_teste)

# o cliente que simula requisições para a API
cliente = TestClient(app)

# cabeçalho c/ token de acesso
cabecalho = {"Token-Acesso": "teste123"}


#testes:

def test_criar_produto():
    """Testa se consegue criar um produto com dados válidos"""
    resposta = cliente.post("/produtos/", headers=cabecalho, json={
        "nome": "Produto Teste",
        "codigo": "TESTE-001",
        "valor": 29.90,
        "imagem": ""
    })
    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Produto Teste"
    assert resposta.json()["codigo"] == "TESTE-001"


def test_listar_produtos():
    """Testa se consegue listar os produtos cadastrados"""
    resposta = cliente.get("/produtos/", headers=cabecalho)
    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)  # Deve retornar uma lista


def test_atualizar_produto():
    """Testa se consegue atualizar um produto existente"""
    # cria um produto
    criar = cliente.post("/produtos/", headers=cabecalho, json={
        "nome": "Produto Antigo",
        "codigo": "TESTE-002",
        "valor": 10.00,
        "imagem": ""
    })
    produto_id = criar.json()["id"]

    # atualiza
    resposta = cliente.put(f"/produtos/{produto_id}", headers=cabecalho, json={
        "nome": "Produto Atualizado",
        "codigo": "TESTE-002",
        "valor": 20.00,
        "imagem": ""
    })
    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Produto Atualizado"
    assert resposta.json()["valor"] == 20.00


def test_deletar_produto():
    """Testa se o soft delete funciona corretamente"""
    # cria um produto
    criar = cliente.post("/produtos/", headers=cabecalho, json={
        "nome": "Produto para Deletar",
        "codigo": "TESTE-003",
        "valor": 5.00,
        "imagem": ""
    })
    produto_id = criar.json()["id"]

    # deleta
    resposta = cliente.delete(f"/produtos/{produto_id}", headers=cabecalho)
    assert resposta.status_code == 200
    assert "excluído" in resposta.json()["mensagem"]


def test_produto_nao_encontrado():
    """Testa se retorna erro 404 quando o produto não existe"""
    resposta = cliente.put("/produtos/99999", headers=cabecalho, json={
        "nome": "Qualquer",
        "codigo": "X",
        "valor": 1.00,
        "imagem": ""
    })
    assert resposta.status_code == 404


def test_acesso_sem_token():
    """Testa se bloqueia acesso sem o token de segurança"""
    resposta = cliente.get("/produtos/")  # Sem o cabeçalho Token-Acesso
    assert resposta.status_code == 403


def test_validacao_valor_negativo():
    """Testa se rejeita valor negativo com mensagem clara"""
    resposta = cliente.post("/produtos/", headers=cabecalho, json={
        "nome": "Produto Inválido",
        "codigo": "TESTE-004",
        "valor": -5.00,
        "imagem": ""
    })
    assert resposta.status_code == 422
    assert "erros_de_validacao" in resposta.json()


def test_validacao_nome_vazio():
    """Testa se rejeita nome vazio com mensagem clara"""
    resposta = cliente.post("/produtos/", headers=cabecalho, json={
        "nome": "",
        "codigo": "TESTE-005",
        "valor": 10.00,
        "imagem": ""
    })
    assert resposta.status_code == 422
    assert "erros_de_validacao" in resposta.json()
