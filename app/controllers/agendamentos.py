from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..models import agendamento, barbeiro, cliente, servico
from ..models.validacao import ErroValidacao
from .auth import destino_seguro, login_obrigatorio

bp = Blueprint("agendamentos", __name__, url_prefix="/agendamentos")


def _formulario(titulo, dados, erros, status=200, agendamento_id=None):
    return (
        render_template(
            "agendamentos/form.html",
            titulo=titulo,
            dados=dados,
            erros=erros,
            agendamento_id=agendamento_id,
            clientes=cliente.listar(),
            barbeiros=barbeiro.listar(apenas_ativos=True),
            servicos=servico.listar(apenas_ativos=True),
        ),
        status,
    )


@bp.route("/")
@login_obrigatorio
def lista():
    dia = agendamento.converter_data(request.args.get("data"))
    barbeiro_id = request.args.get("barbeiro_id", type=int)
    status = request.args.get("status")
    status = status if status in agendamento.ROTULOS else None
    itens = agendamento.listar(
        dia=dia, barbeiro_id=barbeiro_id, status=status, a_partir_de=None if dia else date.today()
    )
    return render_template(
        "agendamentos/lista.html",
        itens=itens,
        barbeiros=barbeiro.listar(),
        rotulos=agendamento.ROTULOS,
        filtro={"data": dia.isoformat() if dia else "", "barbeiro_id": barbeiro_id, "status": status},
    )


@bp.route("/novo", methods=("GET", "POST"))
@login_obrigatorio
def novo():
    if request.method == "POST":
        try:
            agendamento.criar(request.form)
        except ErroValidacao as erro:
            return _formulario("Novo agendamento", request.form, erro.erros, 422)
        flash("Agendamento registrado.", "ok")
        return redirect(url_for("painel.inicio", data=request.form.get("data")))
    dados = {
        "data": request.args.get("data") or date.today().isoformat(),
        "hora": request.args.get("hora", ""),
        "barbeiro_id": request.args.get("barbeiro_id", ""),
        "cliente_id": request.args.get("cliente_id", ""),
    }
    return _formulario("Novo agendamento", dados, {})


@bp.route("/<int:agendamento_id>/editar", methods=("GET", "POST"))
@login_obrigatorio
def editar(agendamento_id):
    existente = agendamento.buscar(agendamento_id)
    if existente is None:
        abort(404)
    if existente["status"] != "AGENDADO":
        flash("Somente agendamentos em aberto podem ser alterados.", "erro")
        return redirect(url_for("agendamentos.lista"))
    if request.method == "POST":
        try:
            agendamento.atualizar(agendamento_id, request.form)
        except ErroValidacao as erro:
            return _formulario("Remarcar agendamento", request.form, erro.erros, 422, agendamento_id)
        flash("Agendamento atualizado.", "ok")
        return redirect(url_for("painel.inicio", data=request.form.get("data")))
    dados = {
        "cliente_id": existente["cliente_id"],
        "barbeiro_id": existente["barbeiro_id"],
        "servico_id": existente["servico_id"],
        "data": existente["inicio"][:10],
        "hora": existente["inicio"][11:16],
    }
    return _formulario("Remarcar agendamento", dados, {}, 200, agendamento_id)


@bp.route("/<int:agendamento_id>/status", methods=("POST",))
@login_obrigatorio
def status(agendamento_id):
    if agendamento.buscar(agendamento_id) is None:
        abort(404)
    novo_status = request.form.get("status", "")
    try:
        agendamento.alterar_status(agendamento_id, novo_status)
    except ErroValidacao as erro:
        flash(erro.erros["geral"], "erro")
    else:
        flash(f"Agendamento marcado como {agendamento.ROTULOS[novo_status].lower()}.", "ok")
    return redirect(destino_seguro(request.form.get("voltar"), url_for("agendamentos.lista")))
