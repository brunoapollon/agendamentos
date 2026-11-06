from werkzeug.security import check_password_hash, generate_password_hash

from ..db import get_db


def buscar(usuario_id):
    return get_db().execute("SELECT id, nome, email FROM usuario WHERE id = ?", (usuario_id,)).fetchone()


def autenticar(email, senha):
    linha = get_db().execute(
        "SELECT * FROM usuario WHERE email = ?", ((email or "").strip().lower(),)
    ).fetchone()
    if linha is None or not check_password_hash(linha["senha_hash"], senha or ""):
        return None
    return linha


def criar(nome, email, senha):
    conexao = get_db()
    cursor = conexao.execute(
        "INSERT INTO usuario (nome, email, senha_hash) VALUES (?, ?, ?)",
        (nome, email.strip().lower(), generate_password_hash(senha)),
    )
    conexao.commit()
    return cursor.lastrowid
