
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

## 🗒️ Sobre o Projeto

Este projeto faz parte da disciplina **Banco de Dados** do curso de **Ciências da Computação da UESB**, sob orientação dos professores **Hélio Lopes dos Santos** e **Maísa Soares dos Santos Lopes**.

O objetivo é desenvolver um **sistema de PDV (Ponto de Venda) para mercado**, aplicando conceitos de modelagem e gerenciamento de banco de dados. O projeto visa consolidar o aprendizado sobre estruturação de dados, integração entre sistemas e práticas colaborativas em equipe utilizando **Git e GitHub** para controle de versão.

O repositório inclui uma pasta chamada **atividade**, onde estão os arquivos relacionados ao desenvolvimento e às entregas do projeto.


## 🛠 Tecnologias

1. **Git e GitHub** – para versionamento e colaboração;
2. **VS Code** – ambiente de desenvolvimento;
3. **Banco de Dados** – PostgreSQL, MariaDB ou MySQL;
4. **Linguagens** – HTML, CSS, Python e PHP;
5. **Framework** – React, para a interface web do sistema.
6. **Docker** – para conteinerização e facilitação do deploy do sistema.


## 👨‍💻 Instalação

| Systema  | Local padrão da pasta                       |
| ------- | -------------------------------------------- |
| Linux   | `~/opt/marketcoffee`                              |
| macOS   | `~/`                              |
| Windows | `~\Documents\`                               |

- Escolha uma das maneiras de instalar
  - **GitHub**
    - Clone o git `/home/` folder.
  - **ZIP**
    - Desacompactar o arquivo Zip em sua pasta padrão.
- No Windows.
- No Linux.
# Market Coffee PDV – Guia de Instalação com Docker (Linux)
Passo a passo como instalar e executar o projeto Market Coffee PDV no Linux utilizando Docker e Docker Compose.
## 1. Pré-requisitos
Certifique-se de que seu sistema está atualizado:
```
sudo apt update
sudo apt upgrade -y
```
## 2. Instalar Docker e Docker Compose
```
sudo apt install -y docker.io docker-compose
```
Adicionar seu usuário ao grupo docker:
```
sudo usermod -aG docker SEU_USUARIO
groups SEU_USUARIO   # para confirmar
```
Iniciar o serviço do Docker e ativá-lo na inicialização:
```
sudo service docker start
sudo update-rc.d docker defaults
docker info
```
## 3. Criar diretório do projeto
```
mkdir -p /opt/market_coffee_pdv
cd /opt/market_coffee_pdv
```
## 4. Criar arquivos do projeto
### docker-compose.yml
Crie o arquivo:
```
nano docker-compose.yml
```
Adicione algo como:
```
version: "3.9"

services:
  backend:
    build: ./backend
    container_name: pdv_backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    container_name: pdv_frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app

  postgres:
    image: postgres:15
    container_name: pdv_postgres
    environment:
      POSTGRES_USER: usuario_banco_dados
      POSTGRES_PASSWORD: senha_banco_dados
      POSTGRES_DB: pdv_market_coffee
    volumes:
      - ./postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
```
### Dockerfiles iniciais
Criar estrutura:
```
mkdir backend frontend
```
Backend:
```
cd backend
nano Dockerfile
```
Exemplo:
```
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```
Frontend:
```
cd ../frontend
nano Dockerfile
```
Exemplo:
```
FROM node:20
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "run", "dev"]
```
Volte ao diretório principal:
```
cd /opt/market_coffee_pdv
```
## 5. Subir o ambiente pela primeira vez
```
docker-compose up -d
```
## 6. Configurar o backend
Crie o requirements.txt:
```
nano backend/requirements.txt
```
Adicione:
```
fastapi
uvicorn
psycopg2-binary
SQLAlchemy
python-dotenv
```
Rebuild do backend:
```
docker-compose build backend
docker-compose up -d
```
## 7. Baixar o código oficial do projeto
Entre no backend:
```
cd backend
git clone https://github.com/mdlos/pdv_mercado.git
```
O GitHub baixa como pasta:
```
pdv_mercado-main
```
Copie os arquivos para dentro do backend:
```
cd pdv_mercado-main/backend_api
mv * /opt/market_coffee_pdv/backend/
```
Volte ao diretório principal:
```
cd /opt/market_coffee_pdv/backend
```
Rebuild do backend:
```
docker-compose up -d --build
```
## 8. Importar o banco de dados
Volte onde está o dump SQL:
```
cd /opt/market_coffee_pdv
```
Se o arquivo veio do repositório:
```
cd pdv_mercado-main
mv pdv_market_coffee.sql /opt/market_coffee_pdv/
cd /opt/market_coffee_pdv
```
Importar para o Postgres:
```
docker exec -i pdv_postgres psql -U usuario_banco_dados -d pdv_market_coffee < /opt/market_coffee_pdv/pdv_market_coffee.sql
```
## 9. Acessar o sistema
Backend (FastAPI):\
[http://localhost:8000]()
Frontend (React ou equivalente):\
[http://localhost:3000]()
Banco de dados:\
PostgreSQL rodando em localhost:5432

OBS: O sistema pode ser usando com o Docker via conteiners conforme descrito ou s/ o Docker rodando os scripts Python!

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


