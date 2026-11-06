# Escopo do projeto AgendaCorte

## Problema

Barbearias pequenas controlam horários em caderno ou por mensagens no WhatsApp. O resultado são horários marcados em dobro para o mesmo barbeiro, atendimentos esquecidos e nenhuma visão do faturamento do dia.

## Solução

Aplicação web para a recepção e os barbeiros organizarem a agenda: cadastro de clientes, barbeiros e serviços, marcação de horários com bloqueio automático de conflitos e acompanhamento do dia em um quadro por barbeiro.

## Usuários

| Perfil | Uso |
|---|---|
| Atendente ou dono da barbearia | Cadastra clientes, barbeiros e serviços; marca, remarca, conclui e cancela atendimentos; acompanha o faturamento do dia. |
| Barbeiro | Consulta a própria coluna na agenda do dia. Usa o mesmo login da recepção nesta versão. |

## Dentro do escopo

- Login de acesso ao sistema.
- Cadastro, edição, busca e exclusão de clientes.
- Cadastro e edição de barbeiros e serviços, com opção de tirá-los da agenda sem apagar o histórico.
- Agendamento com cálculo automático do horário de término pela duração do serviço.
- Bloqueio de horários sobrepostos para o mesmo barbeiro e para o mesmo cliente.
- Bloqueio de horários no passado e fora do expediente (segunda a sábado, 8h às 20h).
- Agenda do dia em colunas por barbeiro, com navegação entre dias.
- Conclusão, cancelamento e remarcação de atendimentos.
- Resumo diário: atendimentos em aberto, concluídos, cancelados e valor faturado.
- Lista de agendamentos com filtros por dia, barbeiro e situação.

## Fora do escopo desta versão

- Agendamento feito pelo próprio cliente pela internet.
- Envio de lembretes por WhatsApp ou SMS.
- Pagamentos, comissões e controle de caixa.
- Perfis de acesso diferentes para barbeiro e recepção.
- Horário de expediente diferente por barbeiro.

## Tecnologias

| Camada | Escolha | Motivo |
|---|---|---|
| Front-end | HTML, CSS e JavaScript puro, com templates Jinja | Sem etapa de build; roda em qualquer navegador. |
| Back-end | Python 3 com Flask, padrão MVC | Linguagem sugerida pela disciplina; Flask expõe com clareza a separação entre rotas, regras e telas. |
| Banco de dados | SQLite 3 | SGBD relacional mais usado do mundo, sem servidor para instalar, arquivo único fácil de copiar e versionar. O SQL usado é padrão e migra para PostgreSQL ou MySQL com poucas mudanças. |
| Testes | pytest (back-end) e node:test (front-end) | Ferramentas padrão de cada linguagem, sem configuração extra. |
| Versionamento | Git e GitHub | Exigência da disciplina. |

## Controle de versões deste documento

| Versão | Data | Alteração |
|---|---|---|
| 1.0 | 06/11/2026 | Escopo definido para a execução do PIT II. |
