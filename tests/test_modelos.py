from datetime import datetime

import pytest

from app.models import agendamento, barbeiro, cliente, servico
from app.models.validacao import ErroValidacao

AGORA = datetime(2030, 1, 7, 7, 0)


def dados_agendamento(**alteracoes):
    dados = {"cliente_id": "1", "barbeiro_id": "1", "servico_id": "1", "data": "2030-01-07", "hora": "10:00"}
    dados.update(alteracoes)
    return dados


def test_cliente_com_telefone_repetido_e_recusado(contexto):
    with pytest.raises(ErroValidacao) as erro:
        cliente.criar({"nome": "Outra Pessoa", "telefone": "(85) 98888-7777"})
    assert erro.value.erros == {"telefone": "Já existe um cliente com este telefone."}


def test_cliente_e_encontrado_por_nome_ou_telefone(contexto):
    assert [c["nome"] for c in cliente.listar("ana")] == ["Ana Souza"]
    assert [c["nome"] for c in cliente.listar("97777")] == ["Bruno Rocha"]
    assert len(cliente.listar("")) == 2


def test_servico_com_nome_repetido_e_recusado(contexto):
    with pytest.raises(ErroValidacao) as erro:
        servico.criar({"nome": "Corte", "preco": "10", "duracao_min": "10", "ativo": "1"})
    assert "nome" in erro.value.erros


def test_agendamento_calcula_fim_e_copia_preco_do_servico(contexto):
    novo_id = agendamento.criar(dados_agendamento(servico_id="2"), agora=AGORA)
    registro = agendamento.buscar(novo_id)
    assert registro["inicio"] == "2030-01-07 10:00"
    assert registro["fim"] == "2030-01-07 10:50"
    assert registro["preco_centavos"] == 5500
    assert registro["status"] == "AGENDADO"


def test_preco_do_agendamento_nao_muda_quando_servico_e_reajustado(contexto):
    novo_id = agendamento.criar(dados_agendamento(), agora=AGORA)
    servico.atualizar(1, {"nome": "Corte", "preco": "40,00", "duracao_min": "30", "ativo": "1"})
    assert agendamento.buscar(novo_id)["preco_centavos"] == 3500


def test_mesmo_barbeiro_nao_atende_dois_clientes_ao_mesmo_tempo(contexto):
    agendamento.criar(dados_agendamento(), agora=AGORA)
    with pytest.raises(ErroValidacao) as erro:
        agendamento.criar(dados_agendamento(cliente_id="2", hora="10:15"), agora=AGORA)
    assert erro.value.erros["inicio"] == "O barbeiro já tem um atendimento nesse horário."


def test_horario_colado_ao_anterior_e_permitido(contexto):
    agendamento.criar(dados_agendamento(), agora=AGORA)
    assert agendamento.criar(dados_agendamento(cliente_id="2", hora="10:30"), agora=AGORA)


def test_outro_barbeiro_pode_atender_no_mesmo_horario(contexto):
    agendamento.criar(dados_agendamento(), agora=AGORA)
    assert agendamento.criar(dados_agendamento(cliente_id="2", barbeiro_id="2"), agora=AGORA)


def test_cliente_nao_fica_em_dois_atendimentos_ao_mesmo_tempo(contexto):
    agendamento.criar(dados_agendamento(), agora=AGORA)
    with pytest.raises(ErroValidacao) as erro:
        agendamento.criar(dados_agendamento(barbeiro_id="2", hora="10:10"), agora=AGORA)
    assert erro.value.erros["inicio"] == "O cliente já tem um atendimento nesse horário."


def test_cancelamento_libera_o_horario(contexto):
    primeiro = agendamento.criar(dados_agendamento(), agora=AGORA)
    agendamento.alterar_status(primeiro, "CANCELADO")
    assert agendamento.criar(dados_agendamento(cliente_id="2"), agora=AGORA)


def test_horario_que_ja_passou_e_recusado(contexto):
    with pytest.raises(ErroValidacao) as erro:
        agendamento.criar(dados_agendamento(hora="06:30"), agora=AGORA)
    assert erro.value.erros["inicio"] == "Escolha um horário que ainda não passou."


def test_atendimento_que_passa_do_fechamento_e_recusado(contexto):
    with pytest.raises(ErroValidacao) as erro:
        agendamento.criar(dados_agendamento(servico_id="2", hora="19:30"), agora=AGORA)
    assert "expediente" in erro.value.erros["inicio"]


def test_campos_obrigatorios_ausentes_geram_um_erro_por_campo(contexto):
    with pytest.raises(ErroValidacao) as erro:
        agendamento.criar({}, agora=AGORA)
    assert set(erro.value.erros) == {"cliente_id", "barbeiro_id", "servico_id", "inicio"}


def test_barbeiro_inativo_nao_recebe_agendamento(contexto):
    barbeiro.atualizar(1, {"nome": "Carlos Lima"})
    with pytest.raises(ErroValidacao) as erro:
        agendamento.criar(dados_agendamento(), agora=AGORA)
    assert erro.value.erros["barbeiro_id"] == "Este barbeiro não está disponível."


def test_cliente_inexistente_e_recusado(contexto):
    with pytest.raises(ErroValidacao) as erro:
        agendamento.criar(dados_agendamento(cliente_id="999"), agora=AGORA)
    assert erro.value.erros["cliente_id"] == "Cliente não encontrado."


def test_concluido_nao_pode_ser_cancelado(contexto):
    novo_id = agendamento.criar(dados_agendamento(), agora=AGORA)
    agendamento.alterar_status(novo_id, "CONCLUIDO")
    with pytest.raises(ErroValidacao):
        agendamento.alterar_status(novo_id, "CANCELADO")
    assert agendamento.buscar(novo_id)["status"] == "CONCLUIDO"


def test_status_desconhecido_e_recusado(contexto):
    novo_id = agendamento.criar(dados_agendamento(), agora=AGORA)
    with pytest.raises(ErroValidacao) as erro:
        agendamento.alterar_status(novo_id, "PERDIDO")
    assert erro.value.erros["geral"] == "Status inválido."


def test_remarcacao_ignora_o_proprio_horario_no_conflito(contexto):
    novo_id = agendamento.criar(dados_agendamento(), agora=AGORA)
    agendamento.atualizar(novo_id, dados_agendamento(hora="10:15"), agora=AGORA)
    assert agendamento.buscar(novo_id)["inicio"] == "2030-01-07 10:15"


def test_agendamento_concluido_nao_pode_ser_remarcado(contexto):
    novo_id = agendamento.criar(dados_agendamento(), agora=AGORA)
    agendamento.alterar_status(novo_id, "CONCLUIDO")
    with pytest.raises(ErroValidacao):
        agendamento.atualizar(novo_id, dados_agendamento(hora="11:00"), agora=AGORA)


def test_cliente_com_agendamento_nao_pode_ser_excluido(contexto):
    agendamento.criar(dados_agendamento(), agora=AGORA)
    with pytest.raises(ErroValidacao):
        cliente.excluir(1)
    cliente.excluir(2)
    assert cliente.buscar(2) is None


def test_resumo_do_dia_soma_apenas_concluidos(contexto):
    primeiro = agendamento.criar(dados_agendamento(), agora=AGORA)
    segundo = agendamento.criar(dados_agendamento(cliente_id="2", barbeiro_id="2", servico_id="2"), agora=AGORA)
    agendamento.criar(dados_agendamento(hora="15:00"), agora=AGORA)
    agendamento.alterar_status(primeiro, "CONCLUIDO")
    agendamento.alterar_status(segundo, "CANCELADO")
    resumo = agendamento.resumo_do_dia(AGORA.date())
    assert resumo == {"agendados": 1, "concluidos": 1, "cancelados": 1, "faturamento": 3500}


def test_agenda_do_dia_agrupa_por_barbeiro(contexto):
    agendamento.criar(dados_agendamento(), agora=AGORA)
    agendamento.criar(dados_agendamento(cliente_id="2", barbeiro_id="2"), agora=AGORA)
    colunas = agendamento.agenda_do_dia(AGORA.date())
    assert [c["barbeiro"]["nome"] for c in colunas] == ["Carlos Lima", "Davi Melo"]
    assert [len(c["itens"]) for c in colunas] == [1, 1]
