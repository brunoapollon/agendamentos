PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS agendamento;
DROP TABLE IF EXISTS servico;
DROP TABLE IF EXISTS barbeiro;
DROP TABLE IF EXISTS cliente;
DROP TABLE IF EXISTS usuario;

CREATE TABLE usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL CHECK (length(trim(nome)) BETWEEN 2 AND 80),
    email TEXT NOT NULL UNIQUE CHECK (email LIKE '%_@_%._%'),
    senha_hash TEXT NOT NULL,
    criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE cliente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL CHECK (length(trim(nome)) BETWEEN 2 AND 80),
    telefone TEXT NOT NULL UNIQUE CHECK (length(telefone) IN (10, 11) AND telefone NOT GLOB '*[^0-9]*'),
    email TEXT CHECK (email IS NULL OR email LIKE '%_@_%._%'),
    observacao TEXT CHECK (observacao IS NULL OR length(observacao) <= 300),
    criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE barbeiro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL CHECK (length(trim(nome)) BETWEEN 2 AND 80),
    telefone TEXT CHECK (telefone IS NULL OR (length(telefone) IN (10, 11) AND telefone NOT GLOB '*[^0-9]*')),
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

CREATE TABLE servico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE CHECK (length(trim(nome)) BETWEEN 2 AND 60),
    preco_centavos INTEGER NOT NULL CHECK (preco_centavos BETWEEN 1 AND 1000000),
    duracao_min INTEGER NOT NULL CHECK (duracao_min BETWEEN 5 AND 240),
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

CREATE TABLE agendamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL REFERENCES cliente (id) ON DELETE RESTRICT,
    barbeiro_id INTEGER NOT NULL REFERENCES barbeiro (id) ON DELETE RESTRICT,
    servico_id INTEGER NOT NULL REFERENCES servico (id) ON DELETE RESTRICT,
    inicio TEXT NOT NULL,
    fim TEXT NOT NULL,
    preco_centavos INTEGER NOT NULL CHECK (preco_centavos > 0),
    status TEXT NOT NULL DEFAULT 'AGENDADO' CHECK (status IN ('AGENDADO', 'CONCLUIDO', 'CANCELADO')),
    criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    CHECK (fim > inicio)
);

CREATE INDEX idx_agendamento_barbeiro_inicio ON agendamento (barbeiro_id, inicio);
CREATE INDEX idx_agendamento_cliente_inicio ON agendamento (cliente_id, inicio);
CREATE INDEX idx_agendamento_inicio ON agendamento (inicio);
