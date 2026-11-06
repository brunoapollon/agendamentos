from ..db import get_db, gravar
from .validacao import ErroValidacao, converter_inteiro, converter_preco, validar_nome

NOME_DUPLICADO = {"nome": "Já existe um serviço com este nome."}


def validar(dados):
    erros = {}
    registro = {
        "nome": validar_nome(dados.get("nome"), "nome", erros, maximo=60),
        "preco_centavos": converter_preco(dados.get("preco"), "preco", erros),
        "duracao_min": converter_inteiro(
            dados.get("duracao_min"), "duracao_min", erros, 5, 240,
            "A duração precisa estar entre 5 e 240 minutos.",
        ),
        "ativo": 1 if dados.get("ativo") else 0,
    }
    if erros:
        raise ErroValidacao(erros)
    return registro


def listar(apenas_ativos=False):
    filtro = "WHERE ativo = 1" if apenas_ativos else ""
    return get_db().execute(f"SELECT * FROM servico {filtro} ORDER BY ativo DESC, nome").fetchall()


def buscar(servico_id):
    return get_db().execute("SELECT * FROM servico WHERE id = ?", (servico_id,)).fetchone()


def criar(dados):
    return gravar(
        "INSERT INTO servico (nome, preco_centavos, duracao_min, ativo) "
        "VALUES (:nome, :preco_centavos, :duracao_min, :ativo)",
        validar(dados),
        NOME_DUPLICADO,
    )


def atualizar(servico_id, dados):
    registro = validar(dados)
    registro["id"] = servico_id
    gravar(
        "UPDATE servico SET nome = :nome, preco_centavos = :preco_centavos, "
        "duracao_min = :duracao_min, ativo = :ativo WHERE id = :id",
        registro,
        NOME_DUPLICADO,
    )
