# Manual de uso

## Instalação

Requisitos: Python 3.10 ou superior e Git. Node.js 18 ou superior apenas para rodar os testes do front-end.

```bash
git clone https://github.com/brunoapollon/agendamentos.git
cd agendamentos
python -m venv .venv
```

Ative o ambiente virtual. No Windows:

```bash
.venv\Scripts\activate
```

No Linux e no macOS:

```bash
source .venv/bin/activate
```

Instale as dependências e rode:

```bash
pip install -r requirements.txt
flask --app app run
```

Acesse `http://127.0.0.1:5000`. Na primeira execução o banco é criado em `instance/agendacorte.sqlite` com dados de exemplo e o usuário administrador:

| E-mail | Senha |
|---|---|
| admin@agendacorte.local | admin123 |

Para recriar o banco do zero:

```bash
flask --app app init-db --seed
```

## Uso

### Entrar

Informe e-mail e senha e clique em "Entrar". Para sair, use "Sair" no rodapé do menu.

### Agenda do dia

Tela inicial. Mostra uma coluna por barbeiro disponível com os atendimentos do dia em ordem de horário.

- "Anterior" e "Próximo" mudam o dia; o campo de data vai direto para qualquer dia.
- "Agendar", no topo da coluna, abre um novo agendamento já com o barbeiro e o dia.
- Em cada atendimento em aberto: "Concluir" registra que foi feito e soma ao faturado; "Remarcar" abre o formulário para mudar horário, barbeiro ou serviço; "Cancelar" pede confirmação e libera o horário.

### Novo agendamento

1. Escolha cliente, barbeiro e serviço.
2. Escolha data e horário de início. O término previsto e o valor aparecem abaixo.
3. Clique em "Agendar".

O sistema recusa e explica quando o horário já passou, quando o atendimento não cabe no expediente (segunda a sábado, 8h às 20h) ou quando o barbeiro ou o cliente já têm atendimento no período.

### Agendamentos

Lista de hoje em diante. Filtre por dia, barbeiro e situação e clique em "Filtrar". "Limpar" volta ao padrão.

### Clientes

Busque por parte do nome ou do telefone. "Agendar" na linha abre um agendamento para o cliente. "Editar" abre o cadastro, onde também fica "Excluir cliente", permitido só para quem não tem agendamentos.

### Barbeiros e serviços

Cadastre e edite pelo menu. Para tirar alguém ou um serviço da agenda sem perder o histórico, desmarque "Disponível para agendamentos".

## Testes

```bash
python -m pytest -v
npm test
```

## Problemas comuns

| Sintoma | Solução |
|---|---|
| `flask: command not found` | Ative o ambiente virtual ou use `python -m flask --app app run`. |
| Porta 5000 ocupada | `flask --app app run --port 5050`. |
| Quero começar sem os dados de exemplo | `flask --app app init-db` (sem `--seed`) e crie um usuário pelo `flask --app app shell`. |
