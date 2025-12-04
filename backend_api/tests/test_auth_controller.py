import pytest
from app import create_app, bcrypt
from src.models.funcionario_dao import FuncionarioDAO
from src.db_connection import get_db_connection # Necessário para a fixture

@pytest.fixture
def client():
    app = create_app(testing=True) 
    app.testing = True
    return app.test_client()
@pytest.fixture
def criar_funcionario_teste():
    """
    Garante que o cargo 'Caixa' exista e cria o funcionário de teste.
    """
    dao = FuncionarioDAO()
    conn = get_db_connection()
    
    cpf_teste = "11111111111" 
    # 🛑 Usar "Caixa" para ser consistente com o assert final
    cargo_nome = "Caixa" 
    id_cargo_caixa = None 

    try:
        with conn.cursor() as cur:
            # 1. GARANTIR QUE O TIPO_FUNCIONARIO 'Caixa' EXISTA
            sql_busca_cargo = "SELECT id_tipo_funcionario FROM tipo_funcionario WHERE cargo = %s;"
            cur.execute(sql_busca_cargo, (cargo_nome,))
            result = cur.fetchone()
            
            if result is None:
                # Se não existe, insere o cargo e pega o ID gerado
                sql_insert_cargo = "INSERT INTO tipo_funcionario (cargo) VALUES (%s) RETURNING id_tipo_funcionario;"
                cur.execute(sql_insert_cargo, (cargo_nome,))
                id_cargo_caixa = cur.fetchone()[0]
                conn.commit()
            else:
                id_cargo_caixa = result[0]
                
        # 2. SETUP: Insere o funcionário
        senha_hash = bcrypt.generate_password_hash("1234").decode("utf-8")
        
        dao.insert(
            cpf=cpf_teste,
            nome="João",
            sobrenome="Teste",
            email="joao@teste.com",
            senha_hashed=senha_hash,
            # 🛑 Usa o ID que acabamos de garantir que exista
            id_tipo_funcionario=id_cargo_caixa, 
        )
        
        # 3. YIELD: Roda o teste
        yield 

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        # 4. TEARDOWN: Remove o funcionário e fecha a conexão
        dao.delete(cpf_teste) 
        if conn: conn.close()


def test_login_sucesso(client, criar_funcionario_teste):
    """
    Testa login correto
    """
    dados = {
        "email": "joao@teste.com",
        "senha": "1234"
    }

    response = client.post("/api/v1/auth/login", json=dados)
    
    assert response.status_code == 200
    json_data = response.get_json()

    assert "cpf" in json_data
    assert json_data["nome"] == "João"
    assert json_data["email"] == "joao@teste.com"
    # 🛑 Assert é 'Caixa' (com C maiúsculo)
    assert json_data["cargo"] == "Caixa"
def test_login_email_nao_existe(client):
    """
    Testa quando o email não está cadastrado
    """
    dados = {
        "email": "naoexiste@teste.com",
        "senha": "1234"
    }

    response = client.post("/api/v1/auth/login", json=dados)

    assert response.status_code == 404
    assert response.get_json()["error"] == "Funcionário não encontrado"


def test_login_senha_incorreta(client, criar_funcionario_teste):
    """
    Testa quando o email existe mas a senha está errada
    """
    dados = {
        "email": "joao@teste.com",
        "senha": "senhaerrada"
    }

    response = client.post("/api/v1/auth/login", json=dados)

    assert response.status_code == 401
    assert response.get_json()["error"] == "Senha incorreta"


def test_login_dados_incompletos(client):
    """
    Testa quando o JSON enviado está incompleto
    """
    dados = { "email": "joao@teste.com" }

    response = client.post("/api/v1/auth/login", json=dados)

    assert response.status_code == 400
    assert response.get_json()["error"] == "Email e senha são obrigatórios"