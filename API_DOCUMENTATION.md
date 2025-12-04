# Documentação da API - PDV Mercado

Esta documentação detalha os endpoints principais da API, com exemplos de dados para envio (Input) e o formato das respostas (Output).

**Base URL:** `http://127.0.0.1:8080/api/v1`

---

## 1. Clientes
**Endpoint:** `/clientes`

### 1.1. Criar Cliente (POST)
**URL:** `/api/v1/clientes/`

**Corpo da Requisição (JSON):**
```json
{
  "nome": "João Silva",
  "cpf_cnpj": "12345678901",
  "email": "joao@email.com",
  "telefone": "11999998888",
  "sexo": "M", 
  "localizacao": {
    "logradouro": "Rua das Flores",
    "numero": "123",
    "bairro": "Centro",
    "cidade": "São Paulo",
    "uf": "SP",
    "cep": "01001000"
  }
}
```
*Nota: `email`, `telefone` e `sexo` são opcionais. Se vazios, não envie ou envie `null`.*

**Resposta de Sucesso (201 Created):**
```json
{
  "id_cliente": 1,
  "nome": "João Silva",
  "cpf_cnpj": "123.456.789-01",
  "email": "joao@email.com",
  "telefone": "(11) 99999-8888",
  "sexo": "M",
  "tipo_doc": "cpf",
  "localizacao_saida": {
    "id_localizacao": 10,
    "logradouro": "Rua das Flores",
    "numero": "123",
    "bairro": "Centro",
    "cidade": "São Paulo",
    "uf": "SP",
    "cep": "01001-000"
  }
}
```

### 1.2. Listar Clientes (GET)
**URL:** `/api/v1/clientes/`

**Resposta de Sucesso (200 OK):**
```json
[
  {
    "id_cliente": 1,
    "nome": "João Silva",
    "cpf_cnpj": "123.456.789-01",
    "email": "joao@email.com",
    "localizacao_saida": { ... }
    // ... outros campos
  },
  {
    "id_cliente": 2,
    "nome": "Maria Souza",
    "cpf_cnpj": "987.654.321-00",
    // ...
  }
]
```

---

## 2. Funcionários
**Endpoint:** `/funcionarios`

### 2.1. Criar Funcionário (POST)
**URL:** `/api/v1/funcionarios/`

**Corpo da Requisição (JSON):**
```json
{
  "nome": "Ana",
  "sobrenome": "Pereira",
  "cpf": "11122233344",
  "senha": "senhaSegura123",
  "id_tipo_funcionario": 2, 
  "email": "ana@mercado.com",
  "telefone": "11988887777",
  "sexo": "F",
  "nome_social": null,
  "localizacao": {
    "logradouro": "Av. Paulista",
    "numero": "1000",
    "bairro": "Bela Vista",
    "cidade": "São Paulo",
    "uf": "SP",
    "cep": "01310100"
  }
}
```
*Nota: `id_tipo_funcionario`: 1 = Admin, 2 = Vendedor (exemplo).*

**Resposta de Sucesso (201 Created):**
```json
{
  "cpf": "111.222.333-44",
  "nome": "Ana",
  "sobrenome": "Pereira",
  "email": "ana@mercado.com",
  "telefone": "(11) 98888-7777",
  "sexo": "F",
  "cargo": {
    "id": 2,
    "nome": "Vendedor"
  },
  "localizacao_detalhes": {
    "id_localizacao": 11,
    "logradouro": "Av. Paulista",
    "cidade": "São Paulo",
    "uf": "SP",
    // ...
  }
}
```

### 2.2. Listar Funcionários (GET)
**URL:** `/api/v1/funcionarios/`

**Resposta de Sucesso (200 OK):**
```json
[
  {
    "cpf": "111.222.333-44",
    "nome": "Ana",
    "cargo": { "id": 2, "nome": "Vendedor" },
    // ...
  },
  // ...
]
```

---

## 3. Produtos
**Endpoint:** `/produtos`

### 3.1. Criar Produto (POST)
**URL:** `/api/v1/produtos/`

**Corpo da Requisição (JSON):**
```json
{
  "nome": "Arroz 5kg",
  "descricao": "Arroz Branco Tipo 1",
  "preco": 25.90,
  "codigo_barras": "7891234567890",
  "initial_quantity": 100 
}
```
*Nota: `initial_quantity` é opcional. Se enviado, cria um registro inicial de estoque.*

**Resposta de Sucesso (201 Created):**
```json
{
  "message": "Produto criado com sucesso!",
  "codigo_produto": 15,
  "nome": "Arroz 5kg"
}
```

### 3.2. Listar Produtos (GET)
**URL:** `/api/v1/produtos/`

**Resposta de Sucesso (200 OK):**
```json
[
  {
    "codigo_produto": 15,
    "nome": "Arroz 5kg",
    "descricao": "Arroz Branco Tipo 1",
    "preco": 25.90,
    "codigo_barras": "7891234567890",
    "quantidade": 100 
  },
  // ...
]
```
*Nota: O campo `quantidade` reflete o estoque atual.*

---

## 4. Vendas
**Endpoint:** `/vendas`

### 4.1. Registrar Venda (POST)
**URL:** `/api/v1/vendas/`

**Corpo da Requisição (JSON):**
```json
{
  "cpf_funcionario": "11122233344",
  "cpf_cliente": "12345678901", 
  "itens": [
    {
      "codigo_produto": 15,
      "quantidade_venda": 2
    },
    {
      "codigo_produto": 8,
      "quantidade_venda": 1
    }
  ],
  "pagamentos": [
    {
      "id_tipo_pagamento": 1, 
      "valor_pago": 50.00
    },
    {
      "id_tipo_pagamento": 2, 
      "valor_pago": 10.00
    }
  ]
}
```
*Nota: `cpf_cliente` é opcional. `id_tipo_pagamento`: 1=Dinheiro, 2=Crédito, 3=Débito, 4=Pix (exemplo).*

**Resposta de Sucesso (201 Created):**
```json
{
  "id_venda": 50,
  "data_venda": "2025-12-04T14:30:00",
  "total_venda": 60.00,
  "funcionario": {
    "cpf": "111.222.333-44",
    "nome": "Ana"
  },
  "cliente": {
    "id_cliente": 1,
    "nome": "João Silva"
  },
  "itens": [
    {
      "codigo_produto": 15,
      "nome_produto": "Arroz 5kg",
      "quantidade": 2,
      "preco_unitario": 25.90,
      "subtotal": 51.80
    },
    // ...
  ],
  "pagamentos": [
    {
      "tipo_pagamento": "Dinheiro",
      "valor": 50.00
    },
    // ...
  ]
}
```

### 4.2. Listar Vendas (GET)
**URL:** `/api/v1/vendas/`

**Filtros Opcionais (Query Params):**
*   `?data=YYYY-MM-DD`: Filtra por data específica.
*   `?cpf=...`: Filtra por CPF do cliente.
*   `/hoje`: Atalho para vendas de hoje.

**Resposta de Sucesso (200 OK):**
```json
[
  {
    "id_venda": 50,
    "data_venda": "2025-12-04T14:30:00",
    "total_venda": 60.00,
    "funcionario": { ... },
    "cliente": { ... },
    // ...
  }
]
```
