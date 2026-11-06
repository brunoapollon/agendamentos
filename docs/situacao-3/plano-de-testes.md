# Plano e registro de testes

Os testes seguem o modelo em V: cada nível de construção tem um nível de teste correspondente.

| Construção | Teste | Onde |
|---|---|---|
| Código | Unitário | `tests/test_validacao.py`, `tests/test_regras_agendamento.py`, `tests/front/app.test.js` |
| Arquitetura | Integração | `tests/test_modelos.py` (model + banco), `tests/test_rotas.py` (controller + view + model) |
| Análise | Sistema | Roteiro manual da seção "Casos de teste de sistema" |
| Requisito | Aceitação | Testes com cinco usuários, formulário em `formulario-teste-usuario.md` |

## Verificação

| Atividade | Como foi feita |
|---|---|
| Revisão de requisitos | Cada RF e RN tem caso de uso e pelo menos um teste automatizado ou manual (tabela de rastreabilidade abaixo). |
| Revisão do modelo de dados | Restrições do dicionário de dados conferidas contra `schema.sql`. |
| Revisão de código | Lógica de negócio só em `app/models`; rotas sem SQL; templates sem regra de negócio. |
| Testes automatizados | 77 testes em Python e 7 em JavaScript, executados a cada alteração. |

## Execução dos testes automatizados

```bash
python -m pytest -v
npm test
```

Resultado da execução em 06/11/2026:

| Suíte | Testes | Aprovados | Falhas |
|---|---|---|---|
| pytest (back-end) | 77 | 77 | 0 |
| node:test (front-end) | 7 | 7 | 0 |

## Rastreabilidade

| Requisito | Testes automatizados |
|---|---|
| RF01 | test_paginas_internas_exigem_login, test_login_com_senha_errada_mostra_mensagem, test_login_volta_para_a_pagina_pedida, test_logout_encerra_a_sessao |
| RF02, RN08, RN10 | test_cliente_com_telefone_repetido_e_recusado, test_cliente_e_encontrado_por_nome_ou_telefone, test_cadastro_de_cliente_pelo_formulario, test_cliente_com_agendamento_nao_pode_ser_excluido, testes de telefone em test_validacao.py |
| RF03, RN09 | test_barbeiro_inativo_nao_recebe_agendamento |
| RF04, RN11 | test_servico_com_nome_repetido_e_recusado, test_cadastro_e_edicao_de_servico, testes de preço e duração em test_validacao.py |
| RF05, RF06 | test_agendamento_calcula_fim_e_copia_preco_do_servico, test_fim_e_calculado_pela_duracao_do_servico, test_agendamento_pelo_formulario_aparece_no_painel |
| RF07 | test_remarcacao_ignora_o_proprio_horario_no_conflito, test_agendamento_concluido_nao_pode_ser_remarcado |
| RF08, RN07 | test_concluido_nao_pode_ser_cancelado, test_status_desconhecido_e_recusado, test_concluir_atendimento_pelo_painel |
| RF09, RF10 | test_agenda_do_dia_agrupa_por_barbeiro, test_resumo_do_dia_soma_apenas_concluidos, test_painel_mostra_colunas_dos_barbeiros |
| RF11 | test_lista_de_agendamentos_filtra_por_situacao |
| RN01 | test_mesmo_barbeiro_nao_atende_dois_clientes_ao_mesmo_tempo, test_horario_colado_ao_anterior_e_permitido, test_outro_barbeiro_pode_atender_no_mesmo_horario, test_conflito_de_horario_e_explicado_no_formulario |
| RN02 | test_cliente_nao_fica_em_dois_atendimentos_ao_mesmo_tempo |
| RN03 | test_cancelamento_libera_o_horario |
| RN04 | test_atendimento_que_passa_do_fechamento_e_recusado, test_expediente_de_segunda_a_sabado, test_domingo_esta_fora_do_expediente |
| RN05 | test_horario_que_ja_passou_e_recusado |
| RN06 | test_preco_do_agendamento_nao_muda_quando_servico_e_reajustado |
| RNF03 | test_login_ignora_destino_externo |
| RNF05 | test_formulario_de_cliente_mostra_erros_e_mantem_valores |

## Casos de teste de sistema

Executar com o banco recriado por `flask --app app init-db --seed`. Preencher "Resultado obtido" e "Situação" na execução.

| Código | Objetivo | Passos | Resultado esperado | Resultado obtido | Situação |
|---|---|---|---|---|---|
| CT01 | Login válido | Entrar com o usuário administrador | Abre a agenda do dia | | |
| CT02 | Login inválido | Entrar com senha errada | Mensagem "E-mail ou senha incorretos." | | |
| CT03 | Cadastrar cliente | Clientes > Cadastrar cliente, nome e telefone válidos | Cliente aparece na lista com telefone formatado | | |
| CT04 | Telefone repetido | Cadastrar cliente com telefone de outro | Erro no campo telefone; dados mantidos | | |
| CT05 | Agendar | Agendar Corte para amanhã às 10:00 com barbeiro livre | Aparece na coluna do barbeiro no dia escolhido | | |
| CT06 | Previsão de término | No formulário, escolher "Corte e barba" e 10:00 | Mostra término às 10:50 e valor R$ 55,00 | | |
| CT07 | Conflito de barbeiro | Agendar outro cliente com o mesmo barbeiro às 10:15 | Erro "O barbeiro já tem um atendimento nesse horário." | | |
| CT08 | Fora do expediente | Agendar às 19:45 um serviço de 30 min | Erro de expediente | | |
| CT09 | Domingo | Agendar para um domingo | Erro de expediente | | |
| CT10 | Concluir | Concluir um atendimento na agenda | Horário fica verde; faturado aumenta | | |
| CT11 | Cancelar | Cancelar um atendimento e confirmar | Horário riscado; horário volta a aceitar agendamento | | |
| CT12 | Remarcar | Remarcar um atendimento para outro horário livre | Atendimento muda de posição na agenda | | |
| CT13 | Excluir cliente com histórico | Tentar excluir cliente com agendamento | Exclusão recusada com mensagem | | |
| CT14 | Desativar barbeiro | Desmarcar "Disponível" de um barbeiro | Coluna some da agenda e o nome some das opções de agendamento | | |
| CT15 | Celular | Abrir a agenda com largura de 390 px | Menu no topo, colunas empilhadas, sem rolagem lateral | | |

## Validação com usuários

Cinco pessoas testam o sistema publicado ou rodando localmente e preenchem o formulário `formulario-teste-usuario.md`. As respostas e as correções feitas ficam em `consolidacao-feedback.md`, e os formulários preenchidos em `docs/situacao-3/avaliacoes/`.
