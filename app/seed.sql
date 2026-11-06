INSERT INTO barbeiro (nome, telefone, ativo) VALUES
    ('Carlos Menezes', '85991230001', 1),
    ('Rafael Pinheiro', '85991230002', 1),
    ('Diego Albuquerque', NULL, 1);

INSERT INTO servico (nome, preco_centavos, duracao_min, ativo) VALUES
    ('Corte', 3500, 30, 1),
    ('Barba', 2500, 20, 1),
    ('Corte e barba', 5500, 50, 1),
    ('Pezinho', 1500, 10, 1);

INSERT INTO cliente (nome, telefone, email, observacao) VALUES
    ('João Victor Lima', '85988110001', 'joao.lima@email.com', 'Prefere máquina 2 nas laterais.'),
    ('Marcos Andrade', '85988110002', NULL, NULL),
    ('Pedro Henrique Sales', '85988110003', 'pedro.sales@email.com', NULL),
    ('Lucas Feitosa', '8532110004', NULL, 'Telefone fixo do trabalho.'),
    ('Thiago Bezerra', '85988110005', NULL, NULL);
