from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..models import barbeiro
from ..models.validacao import ErroValidacao
from .auth import login_obrigatorio

bp = Blueprint("barbeiros", __name__, url_prefix="/barbeiros")


def _formulario(titulo, dados, erros, status=200, barbeiro_id=None):
    return (
        render_template("barbeiros/form.html", titulo=titulo, dados=dados, erros=erros, barbeiro_id=barbeiro_id),
        status,
    )


@bp.route("/")
@login_obrigatorio
def lista():
    return render_template("barbeiros/lista.html", barbeiros=barbeiro.listar())


@bp.route("/novo", methods=("GET", "POST"))
@login_obrigatorio
def novo():
    if request.method == "POST":
        try:
            barbeiro.criar(request.form)
        except ErroValidacao as erro:
            return _formulario("Novo barbeiro", request.form, erro.erros, 422)
        flash("Barbeiro cadastrado.", "ok")
        return redirect(url_for("barbeiros.lista"))
    return _formulario("Novo barbeiro", {"ativo": 1}, {})


@bp.route("/<int:barbeiro_id>/editar", methods=("GET", "POST"))
@login_obrigatorio
def editar(barbeiro_id):
    existente = barbeiro.buscar(barbeiro_id)
    if existente is None:
        abort(404)
    if request.method == "POST":
        try:
            barbeiro.atualizar(barbeiro_id, request.form)
        except ErroValidacao as erro:
            return _formulario("Editar barbeiro", request.form, erro.erros, 422, barbeiro_id)
        flash("Barbeiro atualizado.", "ok")
        return redirect(url_for("barbeiros.lista"))
    return _formulario("Editar barbeiro", dict(existente), {}, 200, barbeiro_id)
