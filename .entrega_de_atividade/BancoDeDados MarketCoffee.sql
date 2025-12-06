-- ================================
-- CONFIGURAÇÃO DO MERCADO
-- ================================
CREATE TABLE IF NOT EXISTS configuracao_mercado (
    id_config INTEGER PRIMARY KEY,
    cnpj VARCHAR(18) NOT NULL UNIQUE,
    razao_social VARCHAR(150) NOT NULL,
    endereco TEXT,
    contato VARCHAR(15)
);

-- ================================
-- TIPOS DE FUNCIONÁRIOS (CARGOS)
-- ================================
CREATE TABLE IF NOT EXISTS tipo_funcionario (
    id_tipo_funcionario INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cargo VARCHAR(100) NOT NULL UNIQUE
);

-- ================================
-- LOCALIZAÇÃO (Endereços reutilizáveis)
-- ================================
CREATE TABLE IF NOT EXISTS localizacao (
    id_localizacao INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cep VARCHAR(10) NOT NULL,
    logradouro VARCHAR(150),
    numero VARCHAR(10),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    uf CHAR(2),
    CONSTRAINT uk_cep_log UNIQUE (cep, logradouro, numero)
);

-- ================================
-- FUNCIONÁRIOS
-- ================================
CREATE TABLE IF NOT EXISTS funcionario (
    cpf VARCHAR(11) PRIMARY KEY,
    sexo CHAR(1),
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    sobrenome VARCHAR(100),
    nome_social VARCHAR(100),
    telefone VARCHAR(15),
    id_tipo_funcionario INTEGER NOT NULL,
    id_localizacao INTEGER
);

-- ================================
-- CLIENTES
-- ================================
CREATE TABLE IF NOT EXISTS cliente (
    id_cliente INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cpf_cnpj VARCHAR(18) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    sexo CHAR(1),
    telefone VARCHAR(15),
    email VARCHAR(100) UNIQUE,
    id_localizacao INTEGER
);
-- ================================
-- PRODUTO
-- ================================
CREATE TABLE IF NOT EXISTS produto (
    codigo_produto INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    preco NUMERIC(10,2) NOT NULL CHECK (preco > 0),
    codigo_barras VARCHAR(50) UNIQUE
);

-- ================================
-- ESTOQUE (1 produto → 1 estoque)
-- ================================
CREATE TABLE IF NOT EXISTS estoque (
    codigo_produto INTEGER PRIMARY KEY,
    quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0)
);

-- ================================
-- FORNECEDOR (Faltava no seu script)
-- ================================
CREATE TABLE IF NOT EXISTS fornecedor (
    id_fornecedor INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    cnpj VARCHAR(18) UNIQUE,
    telefone VARCHAR(15),
    email VARCHAR(100),
    id_localizacao INTEGER
);
-- ================================
-- COMPRA - CABEÇALHO
-- ================================
CREATE TABLE IF NOT EXISTS compra (
    id_compra INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_compra DATE NOT NULL DEFAULT CURRENT_DATE,
    valor_total_compra NUMERIC(10,2) NOT NULL CHECK (valor_total_compra > 0),
    id_fornecedor INTEGER NOT NULL
);

-- ================================
-- ITENS DA COMPRA
-- ================================
CREATE TABLE IF NOT EXISTS compra_item (
    id_compra INTEGER NOT NULL,
    codigo_produto INTEGER NOT NULL,
    quantidade_comprada INTEGER NOT NULL,
    custo_unitario NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (id_compra, codigo_produto)
);
-- ================================
-- TIPOS DE PAGAMENTO
-- ================================
CREATE TABLE IF NOT EXISTS tipo_pagamento (
    id_tipo INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    descricao VARCHAR(50) NOT NULL UNIQUE
);

-- ================================
-- VENDA - CABEÇALHO
-- ================================
CREATE TABLE IF NOT EXISTS venda (
    id_venda INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_venda TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valor_total NUMERIC(10,2) NOT NULL CHECK (valor_total > 0),
    cpf_cnpj_cliente VARCHAR(11),
    status VARCHAR(50) NOT NULL DEFAULT 'Aprovada',
    id_cliente INTEGER,
    cpf_funcionario VARCHAR(11) NOT NULL,
    id_tipo_pagamento INTEGER,
    valor_pago NUMERIC(10,2),
    troco NUMERIC(10,2)
);
-- ================================
-- CABEÇALHO DA DEVOLUÇÃO
-- ================================
CREATE TABLE IF NOT EXISTS devolucao (
    id_devolucao INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    motivo TEXT,
    data_devolucao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_venda INTEGER NOT NULL,
    cpf_funcionario VARCHAR(11) NOT NULL
);

-- ================================
-- ITENS DA DEVOLUÇÃO
-- ================================
CREATE TABLE IF NOT EXISTS devolucao_item (
    id_devolucao INTEGER NOT NULL,
    codigo_produto INTEGER NOT NULL,
    quantidade_devolvida INTEGER NOT NULL,
    valor_unitario NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (id_devolucao, codigo_produto)
);

-- ================================
-- VALE CRÉDITO
-- ================================
CREATE TABLE IF NOT EXISTS devolucao_credito (
    id_devolucao INTEGER PRIMARY KEY,
    codigo_vale_credito VARCHAR(50) NOT NULL UNIQUE,
    data_validade DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ATIVO',
    valor_credito NUMERIC(10,2) NOT NULL DEFAULT 0,
    cpf_cliente VARCHAR(11) NOT NULL
);
-- ================================
-- FLUXO DE CAIXA (TURNO)
-- ================================
CREATE TABLE IF NOT EXISTS fluxo_caixa (
    id_fluxo INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status VARCHAR(10) NOT NULL DEFAULT 'ABERTO',
    saldo_inicial NUMERIC(10,2) NOT NULL CHECK (saldo_inicial >= 0),
    data_hora_abertura TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cpf_funcionario_abertura VARCHAR(11) NOT NULL,
    data_hora_fechamento TIMESTAMP,
    saldo_contado NUMERIC(10,2)
);

-- ================================
-- MOVIMENTAÇÃO DE CAIXA
-- ================================
CREATE TABLE IF NOT EXISTS fluxo_caixa_movimento (
    id_movimento INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_fluxo INTEGER NOT NULL,
    id_venda INTEGER,
    valor NUMERIC(10,2) NOT NULL CHECK (valor != 0),
    tipo VARCHAR(20) NOT NULL,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- FUNCIONÁRIO
ALTER TABLE funcionario
  ADD FOREIGN KEY (id_tipo_funcionario) REFERENCES tipo_funcionario(id_tipo_funcionario),
  ADD FOREIGN KEY (id_localizacao) REFERENCES localizacao(id_localizacao);

-- CLIENTE
ALTER TABLE cliente
  ADD FOREIGN KEY (id_localizacao) REFERENCES localizacao(id_localizacao);

-- FORNECEDOR
ALTER TABLE fornecedor
  ADD FOREIGN KEY (id_localizacao) REFERENCES localizacao(id_localizacao);

-- ESTOQUE
ALTER TABLE estoque
  ADD FOREIGN KEY (codigo_produto) REFERENCES produto(codigo_produto);

-- COMPRA
ALTER TABLE compra
  ADD FOREIGN KEY (id_fornecedor) REFERENCES fornecedor(id_fornecedor);

ALTER TABLE compra_item
  ADD FOREIGN KEY (id_compra) REFERENCES compra(id_compra) ON DELETE CASCADE,
  ADD FOREIGN KEY (codigo_produto) REFERENCES produto(codigo_produto);

-- VENDA
ALTER TABLE venda
  ADD FOREIGN KEY (id_tipo_pagamento) REFERENCES tipo_pagamento(id_tipo),
  ADD FOREIGN KEY (cpf_funcionario) REFERENCES funcionario(cpf),
  ADD FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente);

-- DEVOLUÇÃO
ALTER TABLE devolucao
  ADD FOREIGN KEY (id_venda) REFERENCES venda(id_venda),
  ADD FOREIGN KEY (cpf_funcionario) REFERENCES funcionario(cpf);

-- ITENS DA DEVOLUÇÃO
ALTER TABLE devolucao_item
  ADD FOREIGN KEY (id_devolucao) REFERENCES devolucao(id_devolucao) ON DELETE CASCADE,
  ADD FOREIGN KEY (codigo_produto) REFERENCES produto(codigo_produto);

-- VALE CRÉDITO
ALTER TABLE devolucao_credito
  ADD FOREIGN KEY (id_devolucao) REFERENCES devolucao(id_devolucao),
  ADD FOREIGN KEY (cpf_cliente) REFERENCES cliente(cpf_cnpj);

-- FLUXO DE CAIXA
ALTER TABLE fluxo_caixa
  ADD FOREIGN KEY (cpf_funcionario_abertura) REFERENCES funcionario(cpf);

ALTER TABLE fluxo_caixa_movimento
  ADD FOREIGN KEY (id_fluxo) REFERENCES fluxo_caixa(id_fluxo),
  ADD FOREIGN KEY (id_venda) REFERENCES venda(id_venda);

-- TIPOS DE PAGAMENTO
INSERT INTO tipo_pagamento (descricao) VALUES 
('Dinheiro'), ('Cartão Débito'), ('Cartão Crédito'),
('PIX'), ('Vale Crédito'), ('Outros')
ON CONFLICT DO NOTHING;

-- TIPOS DE FUNCIONÁRIO
INSERT INTO tipo_funcionario (cargo) VALUES 
('Gerente'), ('Caixa')
ON CONFLICT DO NOTHING;

-- CONFIGURAÇÃO DO MERCADO
INSERT INTO configuracao_mercado (id_config, cnpj, razao_social, endereco, contato)
VALUES (1, '00000000000001', 'PDV Central Mercantil', 'Rua Principal, 100', '5511999999999')
ON CONFLICT DO NOTHING;

