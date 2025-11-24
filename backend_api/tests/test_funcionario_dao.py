# tests/test_funcionario_dao.py

import pytest
from src.models.funcionario_dao import FuncionarioDAO
from src.db_connection import get_db_connection
from src.utils.formatters import clean_only_numbers
import random
import string
import secrets

# Necessário para verificar se o hash de senha funciona
from flask_bcrypt import Bcrypt 
from app import create_app # Importamos para obter a instância bcrypt inicializada

# Cria a instância do DAO e do Bcrypt
funcionario_dao = FuncionarioDAO()
# Inicializa o Bcrypt para uso no teste de hash
bcrypt = Bcrypt(create_app()) 


# --- Funções Auxiliares de CONFIGURAÇÃO e LIMPEZA ---

def gerar_cpf_aleatorio():
    """ Gera um CPF aleatório (11 dígitos). """
    # Garantimos 11 dígitos, como esperado pelo Schema
    return ''.join(secrets.choice(string.digits) for _ in range(11))

def obter_dados_teste():
    """ Retorna um dicionário com dados válidos e únicos para a inserção de funcionário. """
    return {
        "cpf": gerar_cpf_aleatorio(),
        "nome": "Funcionario Teste",
        "sobrenome": f"Sobrenome {random.randint(100, 999)}",
        "email": f"teste{random.randint(100, 999)}@funcionario.com",
        "senha_pura": "senhateste123", # Senha pura para hashing
        "id_tipo_funcionario": 1, # Assume que o ID 1 (Admin/Gerente) existe
        "localizacao_data": {
            "cep": "12345678",
            "logradouro": "Rua Teste DAO",
            "numero": "100",
            "cidade": "Cidade Teste",
            "uf": "SP"
        }
    }

def configurar_teste_funcionario(dados):
    """ Insere um funcionário completo para teste e retorna o CPF. """
    # 1. Gera o hash da senha pura ANTES de chamar o DAO
    senha_hashed = bcrypt.generate_password_hash(dados['senha_pura']).decode('utf-8')
    
    # 2. Chama o INSERT do DAO
    cpf_inserido = funcionario_dao.insert(
        cpf=dados['cpf'],
        nome=dados['nome'],
        sobrenome=dados['sobrenome'],
        senha_hashed=senha_hashed,
        id_tipo_funcionario=dados['id_tipo_funcionario'],
        email=dados['email'],
        sexo='M',
        telefone="77999887766",
        nome_social="Funcionario Teste",
        localizacao_data=dados['localizacao_data']
    )
    return cpf_inserido

def limpar_funcionario_inserido(cpf):
    """ Tenta deletar o funcionário e sua localização. """
    funcionario_dao.delete(cpf) 

# --- Testes de Integração CRUD e Segurança ---

def test_01_dao_inserir_criar_e_ler():
    """ Testa a inserção, leitura e verifica o hash da senha e localização. (CREATE/READ) """
    dados = obter_dados_teste()
    senha_pura = dados['senha_pura']
    
    # 1. CREATE: Insere o funcionário
    cpf_inserido = configurar_teste_funcionario(dados)
    
    assert cpf_inserido is not None
    
    # 2. READ ONE: Busca o funcionário
    inserted_funcionario = funcionario_dao.find_by_cpf(cpf_inserido)
    
    # Verifica dados básicos
    assert inserted_funcionario['nome'] == dados['nome']
    
    # 3. VERIFICA SEGURANÇA (Hash)
    hash_salvo = inserted_funcionario['senha']
    assert bcrypt.check_password_hash(hash_salvo, senha_pura) is True, "O hash da senha não corresponde à senha pura."
    
    # 4. VERIFICA LOCALIZAÇÃO
    assert inserted_funcionario['cep'] == dados['localizacao_data']['cep']
    
    # --- Limpeza ---
    limpar_funcionario_inserido(cpf_inserido)


def test_02_dao_deletar_exclusao():
    """ Testa a remoção do funcionário e da localização. (DELETE) """
    dados = obter_dados_teste()
    cpf_inserido = configurar_teste_funcionario(dados)
    
    # 1. DELETE: Chama a função de exclusão
    rows_affected = funcionario_dao.delete(cpf_inserido)
    
    # Verifica se uma linha foi afetada
    assert rows_affected == 1
    
    # 2. VERIFICAÇÃO: Tenta buscar o funcionário deletado
    deleted_funcionario = funcionario_dao.find_by_cpf(cpf_inserido)
    
    # Verifica se o funcionário não existe mais
    assert deleted_funcionario is None


def test_03_dao_atualizar_senha_e_nome():
    """ Testa a atualização do nome e a alteração da senha. (UPDATE) """
    dados = obter_dados_teste()
    cpf_inserido = configurar_teste_funcionario(dados)
    
    novo_nome = "Nome Editado"
    nova_senha_pura = "novasenha456"
    
    # 1. Gera o NOVO hash da senha
    nova_senha_hashed = bcrypt.generate_password_hash(nova_senha_pura).decode('utf-8')
    
    # 2. UPDATE: Chama a função de atualização
    rows_affected = funcionario_dao.update(
        cpf=cpf_inserido,
        nome=novo_nome,
        senha_hashed=nova_senha_hashed # Passa o novo hash
    )
    
    # Verifica se uma linha foi afetada
    assert rows_affected == 1
    
    # 3. VERIFICAÇÃO: Busca e checa o novo nome e a nova senha
    updated_funcionario = funcionario_dao.find_by_cpf(cpf_inserido)
    
    # Verifica o nome
    assert updated_funcionario['nome'] == novo_nome
    
    # Verifica o novo hash da senha
    hash_salvo_novo = updated_funcionario['senha']
    assert bcrypt.check_password_hash(hash_salvo_novo, nova_senha_pura) is True, "O novo hash de senha não corresponde à nova senha pura."

    # --- Limpeza ---
    limpar_funcionario_inserido(cpf_inserido)


def test_04_dao_atualizar_somente_localizacao():
    """ Testa a atualização APENAS da localização, sem alterar outros campos. """
    dados = obter_dados_teste()
    cpf_inserido = configurar_teste_funcionario(dados)
    
    novo_cep = "87654321"
    
    # 1. UPDATE: Altera SÓ a localização
    rows_affected = funcionario_dao.update(
        cpf=cpf_inserido,
        localizacao_data={'cep': novo_cep, 'numero': '999'} # Altera só CEP e Número
    )
    
    # 2. VERIFICAÇÃO: Busca o funcionário
    updated_funcionario = funcionario_dao.find_by_cpf(cpf_inserido)
    
    # Verifica se houve alteração (o DAO deve retornar 1 ou 0)
    assert rows_affected in [0, 1] 

    # Verifica se o CEP foi alterado, mas o nome original permanece
    assert updated_funcionario['cep'] == novo_cep
    assert updated_funcionario['nome'] == dados['nome'] # Verifica que o nome NÃO mudou

    # --- Limpeza ---
    limpar_funcionario_inserido(cpf_inserido)


def test_05_dao_atualizar_somente_cargo():
    """ Testa a atualização APENAS do cargo (id_tipo_funcionario). """
    dados = obter_dados_teste()
    cpf_inserido = configurar_teste_funcionario(dados)
    
    # Assumimos que o ID 2 (Caixa) existe no DB.
    ID_CAIXA = 2 
    
    # 1. UPDATE: Altera SÓ o cargo
    rows_affected = funcionario_dao.update(
        cpf=cpf_inserido,
        id_tipo_funcionario=ID_CAIXA
    )
    
    # 2. VERIFICAÇÃO: Busca o funcionário
    updated_funcionario = funcionario_dao.find_by_cpf(cpf_inserido)
    
    # Verifica se o ID do cargo foi alterado
    assert rows_affected == 1
    assert updated_funcionario['id_tipo_funcionario'] == ID_CAIXA
    
    # --- Limpeza ---
    limpar_funcionario_inserido(cpf_inserido)


def test_06_dao_inserir_cpf_duplicado_deve_falhar():
    """ Testa se a inserção falha ao tentar usar um CPF duplicado. """
    dados = obter_dados_teste()
    
    # SETUP: Insere o primeiro funcionário
    cpf_original = configurar_teste_funcionario(dados)
    
    # Tenta inserir um SEGUNDO funcionário com o MESMO CPF
    senha_hashed_dummy = bcrypt.generate_password_hash(b'dummy').decode('utf-8')
    
    cpf_inserido_fail = funcionario_dao.insert(
        cpf=dados['cpf'], # CPF DUPLICADO
        nome="Duplicado",
        sobrenome="Duplicado",
        senha_hashed=senha_hashed_dummy,
        id_tipo_funcionario=dados['id_tipo_funcionario'] 
    )
    
    # Verifica se o DAO tratou o erro e retornou None
    assert cpf_inserido_fail is None
    
    # --- Limpeza ---
    limpar_funcionario_inserido(cpf_original)