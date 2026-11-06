import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from ..models import usuario

bp = Blueprint("auth", __name__)


def destino_seguro(destino, padrao):
    if destino and destino.startswith("/") and not destino.startswith("//"):
        return destino
    return padrao


def login_obrigatorio(view):
    @functools.wraps(view)
    def protegida(*args, **kwargs):
        if g.usuario is None:
            return redirect(url_for("auth.login", proximo=request.path))
        return view(*args, **kwargs)

    return protegida


@bp.before_app_request
def carregar_usuario():
    usuario_id = session.get("usuario_id")
    g.usuario = usuario.buscar(usuario_id) if usuario_id else None


@bp.route("/login", methods=("GET", "POST"))
def login():
    if g.usuario is not None:
        return redirect(url_for("painel.inicio"))
    if request.method == "POST":
        email = request.form.get("email", "")
        encontrado = usuario.autenticar(email, request.form.get("senha", ""))
        if encontrado is None:
            flash("E-mail ou senha incorretos.", "erro")
            return render_template("auth/login.html", email=email), 401
        session.clear()
        session["usuario_id"] = encontrado["id"]
        return redirect(destino_seguro(request.args.get("proximo"), url_for("painel.inicio")))
    return render_template("auth/login.html", email="")


@bp.route("/logout", methods=("POST",))
def logout():
    session.clear()
    flash("Sessão encerrada.", "ok")
    return redirect(url_for("auth.login"))
