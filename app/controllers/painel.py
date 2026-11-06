from datetime import date, timedelta

from flask import Blueprint, render_template, request

from ..models import agendamento
from .auth import login_obrigatorio

bp = Blueprint("painel", __name__)


@bp.route("/")
@login_obrigatorio
def inicio():
    dia = agendamento.converter_data(request.args.get("data")) or date.today()
    return render_template(
        "painel/inicio.html",
        dia=dia,
        hoje=date.today(),
        anterior=dia - timedelta(days=1),
        seguinte=dia + timedelta(days=1),
        colunas=agendamento.agenda_do_dia(dia),
        resumo=agendamento.resumo_do_dia(dia),
    )
