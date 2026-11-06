import os

from flask import Flask, render_template

from . import db
from .controllers import agendamentos, auth, barbeiros, clientes, painel, servicos
from .models.agendamento import ROTULOS
from .models.validacao import formatar_preco, formatar_telefone


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True, template_folder="views")
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("AGENDACORTE_SECRET", "troque-esta-chave-em-producao"),
        DATABASE=os.path.join(app.instance_path, "agendacorte.sqlite"),
        HORA_ABERTURA=8,
        HORA_FECHAMENTO=20,
        INICIALIZAR_BANCO=True,
    )
    if config:
        app.config.update(config)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    for modulo in (auth, painel, clientes, barbeiros, servicos, agendamentos):
        app.register_blueprint(modulo.bp)

    app.jinja_env.filters["preco"] = formatar_preco
    app.jinja_env.filters["telefone"] = formatar_telefone
    app.jinja_env.filters["status"] = lambda valor: ROTULOS.get(valor, valor)
    app.jinja_env.filters["hora"] = lambda valor: (valor or "")[11:16]

    @app.errorhandler(404)
    def pagina_nao_encontrada(erro):
        return render_template("erro.html", codigo=404, mensagem="A página procurada não existe."), 404

    @app.errorhandler(500)
    def erro_interno(erro):
        return render_template("erro.html", codigo=500, mensagem="Ocorreu um erro inesperado. Tente de novo em instantes."), 500

    if app.config["INICIALIZAR_BANCO"] and not os.path.exists(app.config["DATABASE"]):
        with app.app_context():
            db.init_db()
            db.seed_db()

    return app
