from datetime import datetime, timedelta

from flask import current_app

from ..db import FORMATO_DATA_HORA, get_db
from . import barbeiro
from .validacao import ErroValidacao, converter_id

ROTULOS = {"AGENDADO": "Agendado", "CONCLUIDO": "Concluído", "CANCELADO": "Cancelado"}
TRANSICOES = {"AGENDADO": {"CONCLUIDO", "CANCELADO"}, "CONCLUIDO": set(), "CANCELADO": set()}
DOMINGO = 6

CONSULTA_BASE = """
    SELECT a.*, c.nome AS cliente_nome, c.telefone AS cliente_telefone,
           b.nome AS barbeiro_nome, s.nome AS servico_nome
    FROM agendamento a
    JOIN cliente c ON c.id = a.cliente_id
    JOIN barbeiro b ON b.id = a.barbeiro_id
    JOIN servico s ON s.id = a.servico_id
    WHERE 1 = 1
"""


def converter_data(texto):
    try:
        return datetime.strptime((texto or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def montar_inicio(data_texto, hora_texto):
    try:
        return datetime.strptime(f"{(data_texto or '').strip()} {(hora_texto or '').strip()[:5]}", FORMATO_DATA_HORA)
    except ValueError:
        return None


def calcular_fim(inicio, duracao_min):
    return inicio + timedelta(minutes=duracao_min)


def dentro_do_expediente(inicio, fim, abertura, fechamento):
    if inicio.weekday() == DOMINGO or fim.date() != inicio.date():
        return False
    return inicio.hour >= abertura and (fim.hour, fim.minute) <= (fechamento, 0)


def _tem_conflito(conexao, coluna, valor, inicio, fim, ignorar_id):
    linha = conexao.execute(
        f"SELECT 1 FROM agendamento WHERE {coluna} = ? AND status <> 'CANCELADO' "
        "AND inicio < ? AND fim > ? AND id <> ? LIMIT 1",
        (valor, fim.strftime(FORMATO_DATA_HORA), inicio.strftime(FORMATO_DATA_HORA), ignorar_id or 0),
    ).fetchone()
    return linha is not None


def validar(dados, agora, ignorar_id=None):
    conexao = get_db()
    erros = {}
    cliente_id = converter_id(dados.get("cliente_id"), "cliente_id", erros, "Selecione o cliente.")
    barbeiro_id = converter_id(dados.get("barbeiro_id"), "barbeiro_id", erros, "Selecione o barbeiro.")
    servico_id = converter_id(dados.get("servico_id"), "servico_id", erros, "Selecione o serviço.")
    inicio = montar_inicio(dados.get("data"), dados.get("hora"))
    if inicio is None:
        erros["inicio"] = "Informe data e hora válidas."

    if cliente_id and conexao.execute("SELECT 1 FROM cliente WHERE id = ?", (cliente_id,)).fetchone() is None:
        erros["cliente_id"] = "Cliente não encontrado."
    profissional = barbeiro.buscar(barbeiro_id) if barbeiro_id else None
    if barbeiro_id and (profissional is None or not profissional["ativo"]):
        erros["barbeiro_id"] = "Este barbeiro não está disponível."
    servico = (
        conexao.execute("SELECT * FROM servico WHERE id = ?", (servico_id,)).fetchone() if servico_id else None
    )
    if servico_id and (servico is None or not servico["ativo"]):
        erros["servico_id"] = "Este serviço não está disponível."
    if erros:
        raise ErroValidacao(erros)

    fim = calcular_fim(inicio, servico["duracao_min"])
    abertura = current_app.config["HORA_ABERTURA"]
    fechamento = current_app.config["HORA_FECHAMENTO"]
    if inicio <= agora:
        raise ErroValidacao({"inicio": "Escolha um horário que ainda não passou."})
    if not dentro_do_expediente(inicio, fim, abertura, fechamento):
        raise ErroValidacao(
            {"inicio": f"O atendimento precisa caber no expediente: segunda a sábado, das {abertura}h às {fechamento}h."}
        )
    if _tem_conflito(conexao, "barbeiro_id", barbeiro_id, inicio, fim, ignorar_id):
        raise ErroValidacao({"inicio": "O barbeiro já tem um atendimento nesse horário."})
    if _tem_conflito(conexao, "cliente_id", cliente_id, inicio, fim, ignorar_id):
        raise ErroValidacao({"inicio": "O cliente já tem um atendimento nesse horário."})

    return {
        "cliente_id": cliente_id,
        "barbeiro_id": barbeiro_id,
        "servico_id": servico_id,
        "inicio": inicio.strftime(FORMATO_DATA_HORA),
        "fim": fim.strftime(FORMATO_DATA_HORA),
        "preco_centavos": servico["preco_centavos"],
    }


def buscar(agendamento_id):
    return get_db().execute(CONSULTA_BASE + " AND a.id = ?", (agendamento_id,)).fetchone()


def listar(dia=None, barbeiro_id=None, status=None, a_partir_de=None):
    condicoes, parametros = [], []
    if dia:
        condicoes.append("AND date(a.inicio) = ?")
        parametros.append(dia.isoformat())
    if a_partir_de:
        condicoes.append("AND date(a.inicio) >= ?")
        parametros.append(a_partir_de.isoformat())
    if barbeiro_id:
        condicoes.append("AND a.barbeiro_id = ?")
        parametros.append(barbeiro_id)
    if status:
        condicoes.append("AND a.status = ?")
        parametros.append(status)
    consulta = CONSULTA_BASE + " ".join(condicoes) + " ORDER BY a.inicio, b.nome"
    return get_db().execute(consulta, parametros).fetchall()


def criar(dados, agora=None):
    registro = validar(dados, agora or datetime.now())
    conexao = get_db()
    cursor = conexao.execute(
        "INSERT INTO agendamento (cliente_id, barbeiro_id, servico_id, inicio, fim, preco_centavos) "
        "VALUES (:cliente_id, :barbeiro_id, :servico_id, :inicio, :fim, :preco_centavos)",
        registro,
    )
    conexao.commit()
    return cursor.lastrowid


def atualizar(agendamento_id, dados, agora=None):
    atual = buscar(agendamento_id)
    if atual is None or atual["status"] != "AGENDADO":
        raise ErroValidacao({"geral": "Somente agendamentos em aberto podem ser alterados."})
    registro = validar(dados, agora or datetime.now(), ignorar_id=agendamento_id)
    registro["id"] = agendamento_id
    conexao = get_db()
    conexao.execute(
        "UPDATE agendamento SET cliente_id = :cliente_id, barbeiro_id = :barbeiro_id, servico_id = :servico_id, "
        "inicio = :inicio, fim = :fim, preco_centavos = :preco_centavos WHERE id = :id",
        registro,
    )
    conexao.commit()


def alterar_status(agendamento_id, novo_status):
    atual = buscar(agendamento_id)
    if atual is None:
        raise ErroValidacao({"geral": "Agendamento não encontrado."})
    if novo_status not in ROTULOS:
        raise ErroValidacao({"geral": "Status inválido."})
    if novo_status not in TRANSICOES[atual["status"]]:
        raise ErroValidacao(
            {"geral": f"Um agendamento {ROTULOS[atual['status']].lower()} não pode passar para {ROTULOS[novo_status].lower()}."}
        )
    conexao = get_db()
    conexao.execute("UPDATE agendamento SET status = ? WHERE id = ?", (novo_status, agendamento_id))
    conexao.commit()


def agenda_do_dia(dia):
    colunas = {linha["id"]: {"barbeiro": linha, "itens": []} for linha in barbeiro.listar(apenas_ativos=True)}
    for item in listar(dia=dia):
        if item["barbeiro_id"] not in colunas:
            colunas[item["barbeiro_id"]] = {"barbeiro": barbeiro.buscar(item["barbeiro_id"]), "itens": []}
        colunas[item["barbeiro_id"]]["itens"].append(item)
    return list(colunas.values())


def resumo_do_dia(dia):
    linhas = get_db().execute(
        "SELECT status, COUNT(*) AS quantidade, SUM(preco_centavos) AS total "
        "FROM agendamento WHERE date(inicio) = ? GROUP BY status",
        (dia.isoformat(),),
    ).fetchall()
    por_status = {linha["status"]: linha for linha in linhas}
    return {
        "agendados": por_status["AGENDADO"]["quantidade"] if "AGENDADO" in por_status else 0,
        "concluidos": por_status["CONCLUIDO"]["quantidade"] if "CONCLUIDO" in por_status else 0,
        "cancelados": por_status["CANCELADO"]["quantidade"] if "CANCELADO" in por_status else 0,
        "faturamento": por_status["CONCLUIDO"]["total"] if "CONCLUIDO" in por_status else 0,
    }
