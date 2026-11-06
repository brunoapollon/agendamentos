from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..models import cliente
from ..models.validacao import ErroValidacao
from .auth import login_obrigatorio

bp = Blueprint("clientes", __name__, url_prefix="/clientes")


def _formulario(titulo, dados, erros, status=200, cliente_id=None):
    return (
        render_template("clientes/form.html", titulo=titulo, dados=dados, erros=erros, cliente_id=cliente_id),
        status,
    )


@bp.route("/")
@login_obrigatorio
def lista():
    busca = request.args.get("busca", "")
    return render_template("clientes/lista.html", clientes=cliente.listar(busca), busca=busca)


@bp.route("/novo", methods=("GET", "POST"))
@login_obrigatorio
def novo():
    if request.method == "POST":
        try:
            cliente.criar(request.form)
        except ErroValidacao as erro:
            return _formulario("Novo cliente", request.form, erro.erros, 422)
        flash("Cliente cadastrado.", "ok")
        return redirect(url_for("clientes.lista"))
    return _formulario("Novo cliente", {}, {})


@bp.route("/<int:cliente_id>/editar", methods=("GET", "POST"))
@login_obrigatorio
def editar(cliente_id):
    existente = cliente.buscar(cliente_id)
    if existente is None:
        abort(404)
    if request.method == "POST":
        try:
            cliente.atualizar(cliente_id, request.form)
        except ErroValidacao as erro:
            return _formulario("Editar cliente", request.form, erro.erros, 422, cliente_id)
        flash("Cliente atualizado.", "ok")
        return redirect(url_for("clientes.lista"))
    return _formulario("Editar cliente", dict(existente), {}, 200, cliente_id)


@bp.route("/<int:cliente_id>/excluir", methods=("POST",))
@login_obrigatorio
def excluir(cliente_id):
    if cliente.buscar(cliente_id) is None:
        abort(404)
    try:
        cliente.excluir(cliente_id)
    except ErroValidacao as erro:
        flash(erro.erros["geral"], "erro")
        return redirect(url_for("clientes.editar", cliente_id=cliente_id))
    flash("Cliente excluído.", "ok")
    return redirect(url_for("clientes.lista"))
