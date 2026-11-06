from datetime import date, timedelta

import pytest

from app import create_app
from app.db import init_db
from app.models import barbeiro, cliente, servico, usuario

EMAIL_TESTE = "admin@teste.local"
SENHA_TESTE = "senha-de-teste"


@pytest.fixture
def app(tmp_path):
    aplicacao = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "chave-de-teste",
            "DATABASE": str(tmp_path / "teste.sqlite"),
            "INICIALIZAR_BANCO": False,
        }
    )
    with aplicacao.app_context():
        init_db()
        usuario.criar("Admin Teste", EMAIL_TESTE, SENHA_TESTE)
        cliente.criar({"nome": "Ana Souza", "telefone": "85988887777"})
        cliente.criar({"nome": "Bruno Rocha", "telefone": "85977776666"})
        barbeiro.criar({"nome": "Carlos Lima", "ativo": "1"})
        barbeiro.criar({"nome": "Davi Melo", "ativo": "1"})
        servico.criar({"nome": "Corte", "preco": "35,00", "duracao_min": "30", "ativo": "1"})
        servico.criar({"nome": "Corte e barba", "preco": "55,00", "duracao_min": "50", "ativo": "1"})
    return aplicacao


@pytest.fixture
def contexto(app):
    with app.app_context():
        yield app


@pytest.fixture
def cliente_http(app):
    return app.test_client()


@pytest.fixture
def logado(cliente_http):
    cliente_http.post("/login", data={"email": EMAIL_TESTE, "senha": SENHA_TESTE})
    return cliente_http


@pytest.fixture
def proxima_segunda():
    hoje = date.today()
    return hoje + timedelta(days=(7 - hoje.weekday()) or 7)
