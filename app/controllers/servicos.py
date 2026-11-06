from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..models import servico
from ..models.validacao import ErroValidacao, formatar_preco_campo
from .auth import login_obrigatorio

bp = Blueprint("servicos", __name__, url_prefix="/servicos")


def _formulario(titulo, dados, erros, status=200, servico_id=None):
    return (
        render_template("servicos/form.html", titulo=titulo, dados=dados, erros=erros, servico_id=servico_id),
        status,
    )


@bp.route("/")
@login_obrigatorio
def lista():
    return render_template("servicos/lista.html", servicos=servico.listar())


@bp.route("/novo", methods=("GET", "POST"))
@login_obrigatorio
def novo():
    if request.method == "POST":
        try:
            servico.criar(request.form)
        except ErroValidacao as erro:
            return _formulario("Novo serviço", request.form, erro.erros, 422)
        flash("Serviço cadastrado.", "ok")
        return redirect(url_for("servicos.lista"))
    return _formulario("Novo serviço", {"ativo": 1}, {})


@bp.route("/<int:servico_id>/editar", methods=("GET", "POST"))
@login_obrigatorio
def editar(servico_id):
    existente = servico.buscar(servico_id)
    if existente is None:
        abort(404)
    if request.method == "POST":
        try:
            servico.atualizar(servico_id, request.form)
        except ErroValidacao as erro:
            return _formulario("Editar serviço", request.form, erro.erros, 422, servico_id)
        flash("Serviço atualizado.", "ok")
        return redirect(url_for("servicos.lista"))
    dados = dict(existente)
    dados["preco"] = formatar_preco_campo(existente["preco_centavos"])
    return _formulario("Editar serviço", dados, {}, 200, servico_id)
