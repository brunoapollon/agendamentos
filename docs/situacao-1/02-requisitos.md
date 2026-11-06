# Requisitos

## Requisitos funcionais

| Código | Requisito | Caso de uso |
|---|---|---|
| RF01 | O sistema deve exigir e-mail e senha para acesso a qualquer tela interna. | UC01 |
| RF02 | O sistema deve permitir cadastrar, editar, buscar e excluir clientes. | UC02 |
| RF03 | O sistema deve permitir cadastrar e editar barbeiros, marcando se estão disponíveis para agendamento. | UC03 |
| RF04 | O sistema deve permitir cadastrar e editar serviços com nome, preço e duração. | UC04 |
| RF05 | O sistema deve registrar agendamentos ligando cliente, barbeiro, serviço, data e hora de início. | UC05 |
| RF06 | O sistema deve calcular o horário de término somando a duração do serviço ao início. | UC05 |
| RF07 | O sistema deve permitir remarcar agendamentos em aberto. | UC06 |
| RF08 | O sistema deve permitir marcar um agendamento como concluído ou cancelado. | UC07 |
| RF09 | O sistema deve exibir a agenda de um dia em colunas, uma por barbeiro disponível. | UC08 |
| RF10 | O sistema deve exibir o resumo do dia com quantidades por situação e valor faturado. | UC08 |
| RF11 | O sistema deve listar agendamentos com filtros por dia, barbeiro e situação. | UC09 |

## Regras de negócio

| Código | Regra |
|---|---|
| RN01 | Um barbeiro não pode ter dois atendimentos em aberto ou concluídos com horários sobrepostos. |
| RN02 | Um cliente não pode ter dois atendimentos com horários sobrepostos. |
| RN03 | Atendimentos cancelados não ocupam horário. |
| RN04 | O atendimento inteiro precisa caber no expediente: segunda a sábado, das 8h às 20h. |
| RN05 | Não é possível agendar para um horário que já passou. |
| RN06 | O preço do serviço é copiado para o agendamento no momento da marcação. Reajustes posteriores não alteram atendimentos já marcados. |
| RN07 | Só agendamentos com situação "Agendado" podem ser remarcados, concluídos ou cancelados. Concluído e cancelado são situações finais. |
| RN08 | Cliente com agendamento registrado não pode ser excluído. |
| RN09 | Barbeiros e serviços não são excluídos; ficam indisponíveis para novos agendamentos e continuam no histórico. |
| RN10 | O telefone do cliente é único e tem DDD com 8 ou 9 dígitos. |
| RN11 | O nome do serviço é único. O preço vai de R$ 0,01 a R$ 10.000,00 e a duração de 5 a 240 minutos. |

## Requisitos não funcionais

| Código | Categoria | Requisito |
|---|---|---|
| RNF01 | Segurança | Senhas guardadas apenas como hash (PBKDF2 do Werkzeug). |
| RNF02 | Segurança | Consultas ao banco feitas só com parâmetros, sem concatenar texto digitado pelo usuário. |
| RNF03 | Segurança | Redirecionamento após login aceita apenas caminhos internos. |
| RNF04 | Integridade | Regras de domínio repetidas no banco (CHECK, UNIQUE, FOREIGN KEY) para barrar dados inválidos mesmo fora da aplicação. |
| RNF05 | Usabilidade | Mensagens de erro ao lado do campo, dizendo o que corrigir, com os valores digitados preservados. |
| RNF06 | Usabilidade | Ações destrutivas (cancelar atendimento, excluir cliente) pedem confirmação. |
| RNF07 | Usabilidade | Layout utilizável em telas a partir de 360 px de largura. |
| RNF08 | Acessibilidade | Campos com rótulo associado, foco visível e mensagens anunciadas por leitor de tela. |
| RNF09 | Manutenibilidade | Código organizado em MVC, sem lógica de negócio nas telas nem nas rotas. |
| RNF10 | Testabilidade | Regras de negócio cobertas por testes automatizados executáveis com um comando. |
| RNF11 | Portabilidade | Executa em Windows, Linux e macOS com Python 3.10 ou superior. |
