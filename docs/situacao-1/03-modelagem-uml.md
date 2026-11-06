# Modelagem UML

Os diagramas estão em Mermaid, formato que o GitHub desenha direto na página do repositório.

## Diagrama de casos de uso

```mermaid
flowchart LR
    atendente(["Atendente"])
    subgraph sistema["AgendaCorte"]
        uc01(["UC01 Entrar no sistema"])
        uc02(["UC02 Manter clientes"])
        uc03(["UC03 Manter barbeiros"])
        uc04(["UC04 Manter serviços"])
        uc05(["UC05 Agendar atendimento"])
        uc06(["UC06 Remarcar atendimento"])
        uc07(["UC07 Concluir ou cancelar atendimento"])
        uc08(["UC08 Consultar agenda do dia"])
        uc09(["UC09 Consultar agendamentos"])
        validar(["Validar disponibilidade"])
    end
    atendente --- uc01
    atendente --- uc02
    atendente --- uc03
    atendente --- uc04
    atendente --- uc05
    atendente --- uc06
    atendente --- uc07
    atendente --- uc08
    atendente --- uc09
    uc05 -. include .-> validar
    uc06 -. include .-> validar
```

### Especificação: UC05 Agendar atendimento

| Item | Descrição |
|---|---|
| Ator | Atendente |
| Pré-condição | Usuário autenticado; ao menos um cliente, um barbeiro disponível e um serviço disponível cadastrados. |
| Fluxo principal | 1. Atendente abre "Novo agendamento" pelo menu, pela coluna de um barbeiro ou pela lista de clientes. 2. Sistema mostra o formulário já preenchido com o que veio da origem (dia, barbeiro ou cliente). 3. Atendente escolhe cliente, barbeiro, serviço, data e hora. 4. Sistema mostra o término previsto e o valor. 5. Atendente confirma. 6. Sistema valida (RN01 a RN05), grava e volta para a agenda do dia escolhido. |
| Fluxo alternativo A1 | Faltam cadastros: sistema mostra o que falta e oferece links para cadastrar. |
| Exceção E1 | Campo obrigatório vazio ou inválido: sistema marca o campo e explica o erro. |
| Exceção E2 | Horário no passado, fora do expediente ou em conflito: sistema mantém os dados e explica o motivo. |
| Pós-condição | Agendamento gravado com situação "Agendado", término calculado e preço copiado do serviço. |

### Especificação: UC07 Concluir ou cancelar atendimento

| Item | Descrição |
|---|---|
| Ator | Atendente |
| Pré-condição | Agendamento com situação "Agendado". |
| Fluxo principal | 1. Na agenda do dia, atendente clica em "Concluir" ou "Cancelar". 2. Para cancelar, sistema pede confirmação. 3. Sistema muda a situação e atualiza o resumo do dia. |
| Exceção E1 | Agendamento já concluído ou cancelado: sistema recusa e informa a situação atual. |

## Diagrama de classes

```mermaid
classDiagram
    class Usuario {
        +int id
        +str nome
        +str email
        -str senha_hash
        +autenticar(email, senha) Usuario
    }
    class Cliente {
        +int id
        +str nome
        +str telefone
        +str email
        +str observacao
        +validar(dados)
        +listar(busca)
        +criar(dados) int
        +atualizar(id, dados)
        +excluir(id)
    }
    class Barbeiro {
        +int id
        +str nome
        +str telefone
        +bool ativo
        +listar(apenas_ativos)
        +criar(dados) int
        +atualizar(id, dados)
    }
    class Servico {
        +int id
        +str nome
        +int preco_centavos
        +int duracao_min
        +bool ativo
        +listar(apenas_ativos)
        +criar(dados) int
        +atualizar(id, dados)
    }
    class Agendamento {
        +int id
        +datetime inicio
        +datetime fim
        +int preco_centavos
        +Status status
        +validar(dados, agora)
        +criar(dados) int
        +atualizar(id, dados)
        +alterar_status(id, novo)
        +agenda_do_dia(dia)
        +resumo_do_dia(dia)
    }
    class Status {
        <<enumeration>>
        AGENDADO
        CONCLUIDO
        CANCELADO
    }
    Cliente "1" --> "0..*" Agendamento : solicita
    Barbeiro "1" --> "0..*" Agendamento : atende
    Servico "1" --> "0..*" Agendamento : define duração e preço
    Agendamento --> Status
```

## Diagrama de sequência: agendar atendimento

```mermaid
sequenceDiagram
    actor A as Atendente
    participant V as View agendamentos/form.html
    participant C as Controller agendamentos.novo
    participant M as Model agendamento
    participant BD as SQLite

    A->>V: Preenche cliente, barbeiro, serviço, data e hora
    V->>V: app.js mostra término previsto e valor
    A->>C: POST /agendamentos/novo
    C->>M: criar(request.form)
    M->>BD: Busca cliente, barbeiro e serviço
    BD-->>M: Registros
    M->>M: Calcula fim, checa passado e expediente
    M->>BD: Procura sobreposição do barbeiro e do cliente
    BD-->>M: Nenhum conflito
    M->>BD: INSERT INTO agendamento
    M-->>C: id do agendamento
    C-->>A: Redireciona para a agenda do dia com "Agendamento registrado."
    alt Dados inválidos ou conflito
        M-->>C: ErroValidacao com mensagem por campo
        C-->>V: Reexibe o formulário com status 422
        V-->>A: Erro ao lado do campo e dados preservados
    end
```

## Diagrama de atividades: validação do agendamento

```mermaid
flowchart TD
    inicio([Recebe formulário]) --> obrig{Campos preenchidos e válidos?}
    obrig -- Não --> erroCampo[Erro em cada campo inválido] --> fim([Reexibe formulário])
    obrig -- Sim --> existe{Cliente existe, barbeiro e serviço disponíveis?}
    existe -- Não --> erroCad[Erro no campo correspondente] --> fim
    existe -- Sim --> calc[Calcula término pela duração do serviço]
    calc --> passado{Início já passou?}
    passado -- Sim --> erroPassado[Erro: horário que já passou] --> fim
    passado -- Não --> expediente{Cabe no expediente?}
    expediente -- Não --> erroExp[Erro: fora do expediente] --> fim
    expediente -- Sim --> confBarb{Barbeiro livre?}
    confBarb -- Não --> erroBarb[Erro: barbeiro ocupado] --> fim
    confBarb -- Sim --> confCli{Cliente livre?}
    confCli -- Não --> erroCli[Erro: cliente ocupado] --> fim
    confCli -- Sim --> grava[Grava com preço copiado do serviço] --> ok([Volta para a agenda do dia])
```

## Diagrama de estados do agendamento

```mermaid
stateDiagram-v2
    [*] --> Agendado : criar
    Agendado --> Agendado : remarcar
    Agendado --> Concluido : concluir
    Agendado --> Cancelado : cancelar
    Concluido --> [*]
    Cancelado --> [*]
```
