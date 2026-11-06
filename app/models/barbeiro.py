from ..db import get_db, gravar
from .validacao import ErroValidacao, validar_nome, validar_telefone

ERRO_GRAVACAO = {"geral": "Não foi possível salvar o barbeiro. Confira os dados."}


def validar(dados):
    erros = {}
    registro = {
        "nome": validar_nome(dados.get("nome"), "nome", erros),
        "telefone": validar_telefone(dados.get("telefone"), "telefone", erros, obrigatorio=False),
        "ativo": 1 if dados.get("ativo") else 0,
    }
    if erros:
        raise ErroValidacao(erros)
    return registro


def listar(apenas_ativos=False):
    filtro = "WHERE ativo = 1" if apenas_ativos else ""
    return get_db().execute(f"SELECT * FROM barbeiro {filtro} ORDER BY ativo DESC, nome").fetchall()


def buscar(barbeiro_id):
    return get_db().execute("SELECT * FROM barbeiro WHERE id = ?", (barbeiro_id,)).fetchone()


def criar(dados):
    return gravar(
        "INSERT INTO barbeiro (nome, telefone, ativo) VALUES (:nome, :telefone, :ativo)",
        validar(dados),
        ERRO_GRAVACAO,
    )


def atualizar(barbeiro_id, dados):
    registro = validar(dados)
    registro["id"] = barbeiro_id
    gravar(
        "UPDATE barbeiro SET nome = :nome, telefone = :telefone, ativo = :ativo WHERE id = :id",
        registro,
        ERRO_GRAVACAO,
    )
