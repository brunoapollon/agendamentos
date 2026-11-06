from ..db import get_db, gravar
from .validacao import (
    ErroValidacao,
    somente_digitos,
    validar_email,
    validar_nome,
    validar_telefone,
    validar_texto_opcional,
)

TELEFONE_DUPLICADO = {"telefone": "Já existe um cliente com este telefone."}


def validar(dados):
    erros = {}
    registro = {
        "nome": validar_nome(dados.get("nome"), "nome", erros),
        "telefone": validar_telefone(dados.get("telefone"), "telefone", erros),
        "email": validar_email(dados.get("email"), "email", erros),
        "observacao": validar_texto_opcional(dados.get("observacao"), "observacao", erros, 300),
    }
    if erros:
        raise ErroValidacao(erros)
    return registro


def listar(busca=""):
    texto = (busca or "").strip()
    digitos = somente_digitos(texto)
    if digitos:
        return get_db().execute(
            "SELECT * FROM cliente WHERE nome LIKE ? OR telefone LIKE ? ORDER BY nome",
            (f"%{texto}%", f"%{digitos}%"),
        ).fetchall()
    return get_db().execute(
        "SELECT * FROM cliente WHERE nome LIKE ? ORDER BY nome", (f"%{texto}%",)
    ).fetchall()


def buscar(cliente_id):
    return get_db().execute("SELECT * FROM cliente WHERE id = ?", (cliente_id,)).fetchone()


def criar(dados):
    return gravar(
        "INSERT INTO cliente (nome, telefone, email, observacao) VALUES (:nome, :telefone, :email, :observacao)",
        validar(dados),
        TELEFONE_DUPLICADO,
    )


def atualizar(cliente_id, dados):
    registro = validar(dados)
    registro["id"] = cliente_id
    gravar(
        "UPDATE cliente SET nome = :nome, telefone = :telefone, email = :email, observacao = :observacao WHERE id = :id",
        registro,
        TELEFONE_DUPLICADO,
    )


def excluir(cliente_id):
    conexao = get_db()
    if conexao.execute("SELECT 1 FROM agendamento WHERE cliente_id = ? LIMIT 1", (cliente_id,)).fetchone():
        raise ErroValidacao({"geral": "Este cliente tem agendamentos registrados e não pode ser excluído."})
    conexao.execute("DELETE FROM cliente WHERE id = ?", (cliente_id,))
    conexao.commit()
