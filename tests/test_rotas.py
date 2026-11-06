from conftest import EMAIL_TESTE


def agendar(cliente_http, dia, **alteracoes):
    dados = {"cliente_id": "1", "barbeiro_id": "1", "servico_id": "1", "data": dia.isoformat(), "hora": "10:00"}
    dados.update(alteracoes)
    return cliente_http.post("/agendamentos/novo", data=dados, follow_redirects=True)


def test_paginas_internas_exigem_login(cliente_http):
    for caminho in ("/", "/clientes/", "/barbeiros/", "/servicos/", "/agendamentos/"):
        resposta = cliente_http.get(caminho)
        assert resposta.status_code == 302
        assert "/login" in resposta.headers["Location"]


def test_login_com_senha_errada_mostra_mensagem(cliente_http):
    resposta = cliente_http.post("/login", data={"email": EMAIL_TESTE, "senha": "errada"})
    assert resposta.status_code == 401
    assert "E-mail ou senha incorretos." in resposta.get_data(as_text=True)


def test_login_volta_para_a_pagina_pedida(cliente_http):
    resposta = cliente_http.post(
        "/login?proximo=/clientes/", data={"email": EMAIL_TESTE, "senha": "senha-de-teste"}
    )
    assert resposta.headers["Location"] == "/clientes/"


def test_login_ignora_destino_externo(cliente_http):
    resposta = cliente_http.post(
        "/login?proximo=//site-malicioso.com", data={"email": EMAIL_TESTE, "senha": "senha-de-teste"}
    )
    assert resposta.headers["Location"] == "/"


def test_painel_mostra_colunas_dos_barbeiros(logado):
    pagina = logado.get("/").get_data(as_text=True)
    assert "Carlos Lima" in pagina
    assert "Davi Melo" in pagina


def test_cadastro_de_cliente_pelo_formulario(logado):
    resposta = logado.post(
        "/clientes/novo", data={"nome": "Caio Nunes", "telefone": "(85) 96666-5555"}, follow_redirects=True
    )
    pagina = resposta.get_data(as_text=True)
    assert "Cliente cadastrado." in pagina
    assert "Caio Nunes" in pagina
    assert "(85) 96666-5555" in pagina


def test_formulario_de_cliente_mostra_erros_e_mantem_valores(logado):
    resposta = logado.post("/clientes/novo", data={"nome": "Caio Nunes", "telefone": "123"})
    pagina = resposta.get_data(as_text=True)
    assert resposta.status_code == 422
    assert "O telefone precisa de DDD e 8 ou 9 dígitos." in pagina
    assert 'value="Caio Nunes"' in pagina


def test_cliente_inexistente_retorna_404(logado):
    resposta = logado.get("/clientes/999/editar")
    assert resposta.status_code == 404
    assert "A página procurada não existe." in resposta.get_data(as_text=True)


def test_cadastro_e_edicao_de_servico(logado):
    logado.post("/servicos/novo", data={"nome": "Sobrancelha", "preco": "12,50", "duracao_min": "10", "ativo": "1"})
    pagina = logado.get("/servicos/").get_data(as_text=True)
    assert "Sobrancelha" in pagina and "R$ 12,50" in pagina
    edicao = logado.get("/servicos/3/editar").get_data(as_text=True)
    assert 'value="12,50"' in edicao


def test_agendamento_pelo_formulario_aparece_no_painel(logado, proxima_segunda):
    pagina = agendar(logado, proxima_segunda).get_data(as_text=True)
    assert "Agendamento registrado." in pagina
    assert "Ana Souza" in pagina
    assert "10:00" in pagina


def test_conflito_de_horario_e_explicado_no_formulario(logado, proxima_segunda):
    agendar(logado, proxima_segunda)
    resposta = agendar(logado, proxima_segunda, cliente_id="2", hora="10:20")
    assert resposta.status_code == 422
    assert "O barbeiro já tem um atendimento nesse horário." in resposta.get_data(as_text=True)


def test_concluir_atendimento_pelo_painel(logado, proxima_segunda):
    agendar(logado, proxima_segunda)
    voltar = f"/?data={proxima_segunda.isoformat()}"
    resposta = logado.post(
        "/agendamentos/1/status", data={"status": "CONCLUIDO", "voltar": voltar}, follow_redirects=True
    )
    pagina = resposta.get_data(as_text=True)
    assert "Agendamento marcado como concluído." in pagina
    assert "Faturado: R$ 35,00" in pagina


def test_lista_de_agendamentos_filtra_por_situacao(logado, proxima_segunda):
    agendar(logado, proxima_segunda)
    agendar(logado, proxima_segunda, cliente_id="2", barbeiro_id="2")
    logado.post("/agendamentos/2/status", data={"status": "CANCELADO"})
    pagina = logado.get("/agendamentos/?status=CANCELADO").get_data(as_text=True)
    assert "Bruno Rocha" in pagina
    assert "Ana Souza" not in pagina


def test_logout_encerra_a_sessao(logado):
    logado.post("/logout")
    assert logado.get("/").status_code == 302
