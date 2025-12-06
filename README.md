
<img width=100% src="https://capsule-render.vercel.app/api?type=waving&color=02A6F4&height=120&section=header"/>
<h1 align="center">UESB | PDV Mercado</h1>

<div align="center">  
  <img width=40% src="http://img.shields.io/static/v1?label=STATUS&message=EM%20DESENVOLVIMENTO&color=02A6F4&style=for-the-badge"/>
</div>

<div align="center">
 <a href="#-sobre-o-projeto"> Sobre</a> • 
 <a href="#-tecnologias"> Tecnologias</a> • 
 <a href="#-instalacao"> Instalação</a> • 
 <a href="#-desenvolvedores"> Desenvolvedores</a>
</div>


<img width=100% src="https://github.com/mdlos/pdv_mercado/blob/main/entrega_de_atividade/MarketCoffee.png"/>


## 🗒️ Sobre o Projeto

Este projeto faz parte da disciplina **Banco de Dados** do curso de **Ciências da Computação da UESB**, sob orientação dos professores **Hélio Lopes dos Santos** e **Maísa Soares dos Santos Lopes**.

O objetivo é desenvolver um **sistema de PDV (Ponto de Venda) para mercado**, aplicando conceitos de modelagem e gerenciamento de banco de dados. O projeto visa consolidar o aprendizado sobre estruturação de dados, integração entre sistemas e práticas colaborativas em equipe utilizando **Git e GitHub** para controle de versão.



## 🛠 Tecnologias

1. **Git e GitHub** – para versionamento e colaboração;
2. **VS Code** – ambiente de desenvolvimento;
3. **Banco de Dados** – PostgreSQL, pgAdmin;
4. **Linguagens** – HTML, CSS, Python e Typescript;
5. **Framework/Bibliotecas** – Flask, Psycopg, React, MaterialUI, Tailwind, FramerMotion;


# Documentação da API - PDV Mercado

Esta documentação detalha os endpoints principais da API, com exemplos de dados para envio (Input) e o formato das respostas (Output).

**Base URL:** `http://127.0.0.1:8080/api/v1`

---

## 1. Clientes
**Endpoint Base:** `/clientes`

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
*Nota: `email`, `telefone` e `sexo` são opcionais. Se vazios, envie `null` ou não envie o campo.*

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
    // ...
  },
  // ...
]
```

### 1.3. Buscar Cliente (GET)
**URL:** `/api/v1/clientes/{identifier}`
*Aceita busca por **ID** (inteiro) ou **CPF/CNPJ** (string) no mesmo endpoint.*

**Exemplos:**
*   `/api/v1/clientes/1` (Busca pelo ID 1)
*   `/api/v1/clientes/12345678901` (Busca pelo CPF)

**Resposta de Sucesso (200 OK):**
Retorna o objeto completo do cliente (mesmo formato do POST).

### 1.4. Atualizar Cliente (PUT)
**URL:** `/api/v1/clientes/{id_cliente}`

**Corpo da Requisição (JSON - Parcial):**
Envie apenas os campos que deseja alterar.
```json
{
  "email": "novo@email.com",
  "localizacao": {
      "logradouro": "Nova Rua",
      "numero": "999"
  }
}
```

### 1.5. Deletar Cliente (DELETE)
**URL:** `/api/v1/clientes/{id_cliente}`

**Resposta de Sucesso (204 No Content):**
Sem conteúdo.

---

## 2. Funcionários
**Endpoint Base:** `/funcionarios`

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
*Nota: `id_tipo_funcionario`: 1 = Admin/Gerente, 2 = Vendedor/Operador.*

**Resposta de Sucesso (201 Created):**
```json
{
  "cpf": "111.222.333-44",
  "nome": "Ana",
  "sobrenome": "Pereira",
  "email": "ana@mercado.com",
  "telefone": "(11) 98888-7777",
  "cargo": {
    "id": 2,
    "nome": "Vendedor"
  },
  "localizacao_detalhes": {
    "id_localizacao": 11,
    // ...
  }
}
```

### 2.2. Listar Funcionários (GET)
**URL:** `/api/v1/funcionarios/`

### 2.3. Buscar Funcionário (GET)
**URL:** `/api/v1/funcionarios/{cpf}`
*Busca através do CPF (apenas números ou formatado).*

### 2.4. Atualizar Funcionário (PUT)
**URL:** `/api/v1/funcionarios/{cpf}`
*Permite atualizar dados cadastrais e senha.*

### 2.5. Deletar Funcionário (DELETE)
**URL:** `/api/v1/funcionarios/{cpf}`

---

## 3. Produtos
**Endpoint Base:** `/produtos`

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
*Retorna lista de produtos com suas quantidades em estoque.*

### 3.3. Buscar Produto por ID (GET)
**URL:** `/api/v1/produtos/{id}`

### 3.4. Atualizar Produto (PUT)
**URL:** `/api/v1/produtos/{id}`
*Atualiza dados do produto (preço, nome, descrição, código de barras).*

### 3.5. Deletar Produto (DELETE)
**URL:** `/api/v1/produtos/{id}`

---

## 4. Vendas
**Endpoint Base:** `/vendas`

### 4.1. Registrar Venda (POST)
**URL:** `/api/v1/vendas/`

**Corpo da Requisição (JSON):**
```json
{
  "cpf_funcionario": "11122233344",
  "cpf_cliente": "12345678901", 
  "desconto": 0.0,
  "itens": [
    {
      "codigo_produto": 15,
      "quantidade_venda": 2,
      "preco_unitario": 25.90
    }
  ],
  "pagamentos": [
    {
      "id_tipo": 1, 
      "valor_pago": 60.00
    }
  ]
}
```
*   `cpf_cliente` é opcional.
*   `preco_unitario` deve ser enviado para garantir consistência histórica.
*   `id_tipo` (Pagamento): 1=Dinheiro (exige `valor_pago` explícito). Outros (Cartão/Pix) podem ter `valor_pago` omitido para auto-preenchimento do total restante.

**Resposta de Sucesso (201 Created):**
Retorna o objeto completo da venda, incluindo `troco` e totais calculados.

### 4.2. Listar Vendas (GET)
**URL:** `/api/v1/vendas/`

**Filtros Opcionais (Query Params):**
*   `?data=YYYY-MM-DD`: Filtra por data específica.
*   `?cpf=...`: Filtra por CPF do cliente.
*   Rota útil: `/api/v1/vendas/hoje` (Vendas do dia atual).

### 4.3. Buscar Venda por ID (GET)
**URL:** `/api/v1/vendas/{id_venda}`

---

## 5. Tutorial de Execução (Primeira Vez)

Este guia orienta como configurar e executar o projeto (Backend e Frontend) em ambiente de desenvolvimento local.

### 5.1. Pré-requisitos
*   **Python 3.8+** instalado.
*   **Node.js 18+** e **npm** instalados.

### 5.2. Executando o Backend (API)

1.  **Navegue até a pasta do backend:**
    ```bash
    cd backend_api
    ```

2.  **Crie e ative um ambiente virtual (Recomendado):**
    *   *Windows:*
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   *Linux/Mac:*
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure o ambiente (.env):**
    *   Crie um arquivo `.env` na raiz de `backend_api` se não existir.
    *   Defina as variáveis básicas (ex: `PORT=8080`, configurações de banco).

5.  **Inicie o servidor:**
    ```bash
    python app.py
    ```
    *   O servidor iniciará (padrão em `http://127.0.0.1:5000` ou na porta definida no `.env` e.g., `8080`).

### 5.3. Executando o Frontend (Web App)

1.  **Navegue até a pasta do frontend:**
    ```bash
    cd frontend
    ```

2.  **Instale as dependências:**
    ```bash
    npm install
    ```

3.  **Inicie o servidor de desenvolvimento:**
    ```bash
    npm run dev
    ```
    *   O terminal exibirá a URL local (geralmente `http://localhost:5173`).



## 💻 Desenvolvedores
 
<table>
  <tr>
    <td align="center"><img style="" src="https://avatars.githubusercontent.com/u/72825281?v=4" width="100px;" alt=""/><br /><sub><b> Marcio Fonseca </b></sub></a><br />👨‍💻</a></td>
    <td align="center"><img style="" src="https://avatars.githubusercontent.com/u/132524236?v=4" width="100px;" alt=""/><br /><sub><b> Gustavo Públio </b></sub></a><br />👨‍💻</a></td>
    <td align="center"><img style="" src="https://avatars.githubusercontent.com/u/145059388?v=4" width="100px;" alt=""/><br /><sub><b> Patrick Tigre</b></sub></a><br />👨‍💻</a></td>
    <td align="center"><img style="" src="https://avatars.githubusercontent.com/u/175572993?v=4" width="100px;" alt=""/><br /><sub><b> Brener  </b></sub></a><br />👨‍💻</a></td>
    <td align="center"><img style="" src="https://avatars.githubusercontent.com/u/204011390?v=4" width="100px;" alt=""/><br /><sub><b> Alessandro Brito </b></sub></a><br />👨‍💻</a></td>
    <td align="center"><img style="" src="https://avatars.githubusercontent.com/u/119082207?v=4" width="100px;" alt=""/><br /><sub><b> Ronilson Rocha  </b></sub></a><br />👨‍💻</a></td>
  </tr>
</table>


