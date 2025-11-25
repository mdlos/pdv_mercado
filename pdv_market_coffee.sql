/*
Iremos adotar o snake_case como padrão no nosso banco pois é um padrão usado 
no postgresql e no python, onde nomes de atributos e variáveis são todas em 
maiúsculas e separadas _ . Ex: produto ou tipo_pagamento. 
*/

-- =====================================================================================
-- Criação do Banco de Dados
-- CREATE DATABASE pdv_market_coffee; -- Cria usando o pgAdmin4 ou via terminal com psql
-- =====================================================================================

-- =====================================================================================
-- TABELA CLIENTE
-- Clientes cadastrados no sistema
-- =====================================================================================
CREATE TABLE IF NOT EXISTS cliente (
    id_cliente INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cpf_cnpj VARCHAR(18) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    sexo CHAR(1),
    telefone VARCHAR(15),
    email VARCHAR(100) UNIQUE
);

-- =====================================================================================
-- TABELA LOCALIZACAO
-- Endereços usados por Cliente, Fornecedor e Funcionário
-- =====================================================================================
CREATE TABLE IF NOT EXISTS localizacao (
    id_localizacao INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cep VARCHAR(10) NOT NULL,
    logradouro VARCHAR(150),
    numero VARCHAR(10),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    uf CHAR(2)
);

-- =====================================================================================
-- TIPO DE PAGAMENTO
-- Ex: Dinheiro, Cartão Débito, PIX, etc.
-- =====================================================================================
CREATE TABLE IF NOT EXISTS tipo_pagamento (
    id_tipo INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    descricao VARCHAR(50) UNIQUE NOT NULL
);

-- =====================================================================================
-- TIPO DE FUNCIONÁRIO
-- Ex: Vendedor, Gerente, Caixa, Estoquista
-- =====================================================================================
CREATE TABLE IF NOT EXISTS tipo_funcionario (
    id_tipo_funcionario INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cargo VARCHAR(100) UNIQUE NOT NULL
);

-- =====================================================================================
-- FORNECEDOR
-- =====================================================================================
CREATE TABLE IF NOT EXISTS fornecedor (
    id_fornecedor INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cnpj VARCHAR(18) UNIQUE NOT NULL,
    razao_social VARCHAR(150) NOT NULL,
    situacao_cadastral VARCHAR(50),
    data_abertura DATE,
    celular VARCHAR(15),
    email VARCHAR(100) UNIQUE
);

-- =====================================================================================
-- PRODUTO
-- =====================================================================================
CREATE TABLE IF NOT EXISTS produto (
    codigo_produto INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT NOT NULL,
    preco DECIMAL(10, 2)  NOT NULL CHECK (preco > 0),
	codigo_barras VARCHAR(50)  UNIQUE
);

-- =====================================================================================
-- FUNCIONÁRIO
-- =====================================================================================
CREATE TABLE IF NOT EXISTS funcionario (
    cpf VARCHAR(11) PRIMARY KEY,
    sexo CHAR(1),
    email VARCHAR(100)  NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    sobrenome VARCHAR(100), 
    nome_social VARCHAR(100),
    telefone VARCHAR(15),
    id_tipo_funcionario INT NOT NULL
);

-- =====================================================================================
-- FLUXO DE CAIXA
-- =====================================================================================
CREATE TABLE IF NOT EXISTS fluxo_caixa (
    id_fluxo INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    saldo_inicial DECIMAL(10, 2) NOT NULL,
    saldo_final_informado DECIMAL(10, 2),
    data_hora_abertura TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cpf_funcionario_abertura VARCHAR(11) NOT NULL,
   data_hora_fechamento TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================================================
-- VENDA
-- =====================================================================================
CREATE TABLE IF NOT EXISTS venda (
    id_venda INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valor_total DECIMAL(10, 2) NOT NULL,
    cpf_cliente VARCHAR(11), -- CPF opcional para venda rápida
    id_cliente INT
);

-- =====================================================================================
-- DEVOLUÇÃO
-- =====================================================================================
CREATE TABLE IF NOT EXISTS devolucao (
    id_devolucao INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    motivo TEXT,
    data_devolucao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_venda INT NOT NULL
);

-- =====================================================================================
-- COMPRA
-- =====================================================================================
CREATE TABLE IF NOT EXISTS compra (
    id_compra INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_compra DATE NOT NULL DEFAULT CURRENT_DATE,
    data_entrega DATE,
    valor_total_compra DECIMAL(10, 2) NOT NULL,
    id_fornecedor INT NOT NULL
);

-- =====================================================================================
-- PAGAMENTO
-- =====================================================================================
CREATE TABLE IF NOT EXISTS pagamento (
    id_pagamento INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    valor_pago DECIMAL(10, 2) NOT NULL,
    id_tipo INT NOT NULL,
    id_venda INT NOT NULL
);

-- =====================================================================================
-- ITENS DA VENDA
-- =====================================================================================
CREATE TABLE IF NOT EXISTS venda_item (
    id_venda INT,
    codigo_produto INT,
    preco_unitario DECIMAL(10, 2) NOT NULL,
    quantidade_venda INT NOT NULL,
    valor_total DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (id_venda, codigo_produto)
);

-- =====================================================================================
-- ITENS DA DEVOLUÇÃO
-- =====================================================================================
CREATE TABLE IF NOT EXISTS devolucao_item (
    id_devolucao INT,
    codigo_produto INT,
    quantidade_devolvida INT NOT NULL,
    valor_unitario DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (id_devolucao, codigo_produto)
);

-- =====================================================================================
-- CRÉDITO DE DEVOLUÇÃO
-- =====================================================================================
CREATE TABLE IF NOT EXISTS devolucao_credito (
    id_devolucao INT PRIMARY KEY,
    codigo_vale_credito VARCHAR(50) UNIQUE NOT NULL,
    data_validade DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(50) NOT NULL
);

-- =====================================================================================
-- ITENS DA COMPRA
-- =====================================================================================
CREATE TABLE IF NOT EXISTS compra_item (
    id_compra INT,
    codigo_produto INT,
    quantidade_compra INT NOT NULL,
    preco_unitario DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (id_compra, codigo_produto)
);

-- =====================================================================================
-- ESTOQUE
-- PK = FK de produto
-- =====================================================================================
CREATE TABLE IF NOT EXISTS estoque (
    codigo_produto INT PRIMARY KEY,
    quantidade INT NOT NULL DEFAULT 0
);

-- =====================================================================================
-- NOTA FISCAL
-- =====================================================================================
CREATE TABLE IF NOT EXISTS nota_fiscal (
    id_nf INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    numero_nf VARCHAR(50) UNIQUE NOT NULL,
    data_emissao DATE NOT NULL DEFAULT CURRENT_DATE,
    valor_total DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    id_venda INT UNIQUE NOT NULL
);

/* ============================================================
   As chaves estrangeiras foram declaradas como CONSTRAINTS
   nomeadas, visando melhor organização e manutenção do schema.
   ============================================================ */

-- =====================================================================================
-- CLIENTE → LOCALIZAÇÃO
-- =====================================================================================
ALTER TABLE cliente
ADD COLUMN IF NOT EXISTS id_localizacao INT;

ALTER TABLE cliente
ADD CONSTRAINT fk_cliente_localizacao
FOREIGN KEY (id_localizacao) REFERENCES localizacao(id_localizacao);


-- =====================================================================================
-- FUNCIONARIO → LOCALIZAÇÃO
-- =====================================================================================
ALTER TABLE funcionario
ADD COLUMN IF NOT EXISTS id_localizacao INT;

ALTER TABLE funcionario
ADD CONSTRAINT fk_funcionario_localizacao
FOREIGN KEY (id_localizacao) REFERENCES localizacao(id_localizacao);


-- =====================================================================================
-- FORNECEDOR → LOCALIZAÇÃO
-- =====================================================================================
ALTER TABLE fornecedor
ADD COLUMN IF NOT EXISTS id_localizacao INT;

ALTER TABLE fornecedor
ADD CONSTRAINT fk_fornecedor_localizacao
FOREIGN KEY (id_localizacao) REFERENCES localizacao(id_localizacao);


-- =====================================================================================
-- FUNCIONARIO → TIPO DE FUNCIONÁRIO
-- =====================================================================================
ALTER TABLE funcionario
ADD CONSTRAINT fk_funcionario_tipo
FOREIGN KEY (id_tipo_funcionario)
REFERENCES tipo_funcionario(id_tipo_funcionario);


-- =====================================================================================
-- FLUXO DE CAIXA → FUNCIONÁRIO
-- =====================================================================================
ALTER TABLE fluxo_caixa
ADD CONSTRAINT fk_fluxo_caixa_funcionario_cpf
FOREIGN KEY (cpf_funcionario_abertura)
REFERENCES funcionario(cpf);


-- =====================================================================================
-- VENDA → CLIENTE
-- =====================================================================================
ALTER TABLE venda
ADD CONSTRAINT fk_venda_cliente
FOREIGN KEY (id_cliente)
REFERENCES cliente(id_cliente);


-- =====================================================================================
-- DEVOLUÇÃO → VENDA
-- =====================================================================================
ALTER TABLE devolucao
ADD CONSTRAINT fk_devolucao_venda
FOREIGN KEY (id_venda)
REFERENCES venda(id_venda);


-- =====================================================================================
-- COMPRA → FORNECEDOR
-- =====================================================================================
ALTER TABLE compra
ADD CONSTRAINT fk_compra_fornecedor
FOREIGN KEY (id_fornecedor)
REFERENCES fornecedor(id_fornecedor);


-- =====================================================================================
-- PAGAMENTO → TIPO PAGAMENTO
-- =====================================================================================
ALTER TABLE pagamento
ADD CONSTRAINT fk_pagamento_tipo
FOREIGN KEY (id_tipo)
REFERENCES tipo_pagamento(id_tipo);


-- =====================================================================================
-- PAGAMENTO → VENDA
-- =====================================================================================
ALTER TABLE pagamento
ADD CONSTRAINT fk_pagamento_venda
FOREIGN KEY (id_venda)
REFERENCES venda(id_venda);


-- =====================================================================================
-- VENDA ITEM → VENDA / PRODUTO
-- =====================================================================================
ALTER TABLE venda_item
ADD CONSTRAINT fk_venda_item_venda
FOREIGN KEY (id_venda)
REFERENCES venda(id_venda);

ALTER TABLE venda_item
ADD CONSTRAINT fk_venda_item_produto
FOREIGN KEY (codigo_produto)
REFERENCES produto(codigo_produto);


-- =====================================================================================
-- DEVOLUCAO ITEM → DEVOLUCAO / PRODUTO
-- =====================================================================================
ALTER TABLE devolucao_item
ADD CONSTRAINT fk_devolucao_item_devolucao
FOREIGN KEY (id_devolucao)
REFERENCES devolucao(id_devolucao);

ALTER TABLE devolucao_item
ADD CONSTRAINT fk_devolucao_item_produto
FOREIGN KEY (codigo_produto)
REFERENCES produto(codigo_produto);


-- =====================================================================================
-- DEVOLUCAO CRÉDITO → DEVOLUCAO
-- =====================================================================================
ALTER TABLE devolucao_credito
ADD CONSTRAINT fk_devolucao_credito_devolucao
FOREIGN KEY (id_devolucao)
REFERENCES devolucao(id_devolucao);


-- =====================================================================================
-- COMPRA ITEM → COMPRA / PRODUTO
-- =====================================================================================
ALTER TABLE compra_item
ADD CONSTRAINT fk_compra_item_compra
FOREIGN KEY (id_compra)
REFERENCES compra(id_compra);

ALTER TABLE compra_item
ADD CONSTRAINT fk_compra_item_produto
FOREIGN KEY (codigo_produto)
REFERENCES produto(codigo_produto);


-- =====================================================================================
-- ESTOQUE → PRODUTO
-- =====================================================================================
ALTER TABLE estoque
ADD CONSTRAINT fk_estoque_produto
FOREIGN KEY (codigo_produto)
REFERENCES produto(codigo_produto)
ON DELETE CASCADE;


-- =====================================================================================
-- NOTA FISCAL → VENDA
-- =====================================================================================
ALTER TABLE nota_fiscal
ADD CONSTRAINT fk_nota_fiscal_venda
FOREIGN KEY (id_venda)
REFERENCES venda(id_venda);

-- =====================================================================================
INSERT INTO tipo_funcionario (cargo) VALUES ('Gerente') ON CONFLICT (cargo) DO NOTHING;
INSERT INTO tipo_funcionario (cargo) VALUES ('Caixa') ON CONFLICT (cargo) DO NOTHING;
-- ===================================================================================== 

--  =====================================================================================
--Cadastrar formas de pagamentos)
INSERT INTO tipo_pagamento (descricao) VALUES ('Dinheiro') ON CONFLICT (descricao) DO NOTHING;
INSERT INTO tipo_pagamento (descricao) VALUES ('Cartão Débito') ON CONFLICT (descricao) DO NOTHING;
INSERT INTO tipo_pagamento (descricao) VALUES ('Cartão Crédito') ON CONFLICT (descricao) DO NOTHING;
INSERT INTO tipo_pagamento (descricao) VALUES ('PIX') ON CONFLICT (descricao) DO NOTHING;
INSERT INTO tipo_pagamento (descricao) VALUES ('Vale Credito') ON CONFLICT (descricao) DO NOTHING;
INSERT INTO tipo_pagamento (descricao) VALUES ('Outros') ON CONFLICT (descricao) DO NOTHING;
-- =====================================================================================
