import sqlite3
from datetime import date, datetime, time, timedelta
from pathlib import Path

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash

from .models.validacao import ErroValidacao

FORMATO_DATA_HORA = "%Y-%m-%d %H:%M"
PASTA = Path(__file__).parent


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(erro=None):
    conexao = g.pop("db", None)
    if conexao is not None:
        conexao.close()


def gravar(sql, parametros, erro_unicidade):
    conexao = get_db()
    try:
        cursor = conexao.execute(sql, parametros)
        conexao.commit()
    except sqlite3.IntegrityError as erro:
        conexao.rollback()
        raise ErroValidacao(erro_unicidade) from erro
    return cursor.lastrowid


def init_db():
    get_db().executescript((PASTA / "schema.sql").read_text(encoding="utf-8"))


def seed_db():
    conexao = get_db()
    conexao.executescript((PASTA / "seed.sql").read_text(encoding="utf-8"))
    conexao.execute(
        "INSERT INTO usuario (nome, email, senha_hash) VALUES (?, ?, ?)",
        ("Administrador", "admin@agendacorte.local", generate_password_hash("admin123")),
    )
    hoje = date.today()
    amanha = hoje + timedelta(days=1)
    exemplos = [
        (1, 1, 1, hoje, "09:00"),
        (2, 1, 3, hoje, "10:00"),
        (3, 2, 2, hoje, "09:30"),
        (4, 2, 1, hoje, "14:30"),
        (5, 3, 4, hoje, "11:00"),
        (1, 3, 2, amanha, "16:00"),
    ]
    for cliente_id, barbeiro_id, servico_id, dia, hora in exemplos:
        servico = conexao.execute(
            "SELECT preco_centavos, duracao_min FROM servico WHERE id = ?", (servico_id,)
        ).fetchone()
        inicio = datetime.combine(dia, time.fromisoformat(hora))
        fim = inicio + timedelta(minutes=servico["duracao_min"])
        conexao.execute(
            "INSERT INTO agendamento (cliente_id, barbeiro_id, servico_id, inicio, fim, preco_centavos) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                cliente_id,
                barbeiro_id,
                servico_id,
                inicio.strftime(FORMATO_DATA_HORA),
                fim.strftime(FORMATO_DATA_HORA),
                servico["preco_centavos"],
            ),
        )
    conexao.commit()


@click.command("init-db")
@click.option("--seed", is_flag=True, help="Inclui dados de exemplo e o usuário administrador.")
def init_db_command(seed):
    init_db()
    if seed:
        seed_db()
    click.echo("Banco de dados criado.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
