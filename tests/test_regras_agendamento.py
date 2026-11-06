from datetime import datetime

import pytest

from app.models.agendamento import calcular_fim, dentro_do_expediente, montar_inicio

SEGUNDA = datetime(2030, 1, 7)


def test_fim_e_calculado_pela_duracao_do_servico():
    inicio = SEGUNDA.replace(hour=9, minute=40)
    assert calcular_fim(inicio, 50) == SEGUNDA.replace(hour=10, minute=30)


@pytest.mark.parametrize(
    "hora_inicio, duracao, esperado",
    [
        ((8, 0), 30, True),
        ((19, 30), 30, True),
        ((7, 59), 30, False),
        ((19, 45), 30, False),
    ],
)
def test_expediente_de_segunda_a_sabado(hora_inicio, duracao, esperado):
    inicio = SEGUNDA.replace(hour=hora_inicio[0], minute=hora_inicio[1])
    assert dentro_do_expediente(inicio, calcular_fim(inicio, duracao), 8, 20) is esperado


def test_domingo_esta_fora_do_expediente():
    domingo = datetime(2030, 1, 13, 10, 0)
    assert dentro_do_expediente(domingo, calcular_fim(domingo, 30), 8, 20) is False


def test_sabado_esta_dentro_do_expediente():
    sabado = datetime(2030, 1, 12, 10, 0)
    assert dentro_do_expediente(sabado, calcular_fim(sabado, 30), 8, 20) is True


@pytest.mark.parametrize("data, hora", [("2030-02-30", "10:00"), ("", "10:00"), ("2030-01-07", "25:00"), (None, None)])
def test_data_ou_hora_invalida_retorna_none(data, hora):
    assert montar_inicio(data, hora) is None


def test_hora_com_segundos_e_aceita():
    assert montar_inicio("2030-01-07", "10:15:00") == datetime(2030, 1, 7, 10, 15)
