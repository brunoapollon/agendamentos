import pytest

from app.models.validacao import (
    converter_inteiro,
    converter_preco,
    formatar_preco,
    formatar_telefone,
    validar_email,
    validar_nome,
    validar_telefone,
)


def test_telefone_com_mascara_e_guardado_so_com_digitos():
    erros = {}
    assert validar_telefone("(85) 98888-7777", "telefone", erros) == "85988887777"
    assert erros == {}


@pytest.mark.parametrize("entrada", ["123", "859888877771", "(85) 9999"])
def test_telefone_com_tamanho_errado_gera_erro(entrada):
    erros = {}
    validar_telefone(entrada, "telefone", erros)
    assert "telefone" in erros


def test_telefone_vazio_so_gera_erro_quando_obrigatorio():
    erros = {}
    assert validar_telefone("", "telefone", erros, obrigatorio=False) is None
    assert erros == {}
    validar_telefone("", "telefone", erros)
    assert erros["telefone"] == "Informe o telefone com DDD."


@pytest.mark.parametrize(
    "entrada, esperado",
    [("35,00", 3500), ("35.5", 3550), ("R$ 1.200,90", 120090), ("40", 4000), ("0,01", 1)],
)
def test_preco_valido_vira_centavos(entrada, esperado):
    erros = {}
    assert converter_preco(entrada, "preco", erros) == esperado
    assert erros == {}


@pytest.mark.parametrize("entrada", ["", "abc", "0", "-10", "nan", "inf", "10000,01"])
def test_preco_invalido_gera_erro(entrada):
    erros = {}
    assert converter_preco(entrada, "preco", erros) is None
    assert "preco" in erros


@pytest.mark.parametrize("entrada", ["ana@email.com", "  ANA@Email.COM  "])
def test_email_valido_e_normalizado(entrada):
    erros = {}
    assert validar_email(entrada, "email", erros) == "ana@email.com"
    assert erros == {}


@pytest.mark.parametrize("entrada", ["ana", "ana@", "ana@email", "a b@email.com"])
def test_email_invalido_gera_erro(entrada):
    erros = {}
    validar_email(entrada, "email", erros)
    assert "email" in erros


def test_nome_remove_espacos_extras_e_exige_tamanho_minimo():
    erros = {}
    assert validar_nome("  Ana   Souza ", "nome", erros) == "Ana Souza"
    assert erros == {}
    validar_nome("A", "nome", erros)
    assert "nome" in erros


@pytest.mark.parametrize("entrada", ["4", "241", "abc", None])
def test_duracao_fora_do_intervalo_gera_erro(entrada):
    erros = {}
    assert converter_inteiro(entrada, "duracao_min", erros, 5, 240, "fora") is None
    assert erros["duracao_min"] == "fora"


def test_formatacoes_para_exibicao():
    assert formatar_preco(3500) == "R$ 35,00"
    assert formatar_preco(120090) == "R$ 1.200,90"
    assert formatar_telefone("85988887777") == "(85) 98888-7777"
    assert formatar_telefone("8532110004") == "(85) 3211-0004"
