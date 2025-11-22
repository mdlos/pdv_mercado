'''===============================================================================
Comando para tertar todos os testes deste arquivo com saída resumida:
pytest -v --tb=short tests/test_cliente_dao.py
tests/test_cliente_dao.py
==============================================================================='''

import pytest
from src.models.cliente_dao import ClienteDAO
from src.db_connection import get_db_connection
import secrets
import string
import random

# Cria a instância do DAO que será testada
cliente_dao = ClienteDAO()

# --- Funções Auxiliares de SETUP e TEARDOWN ---

def generate_random_cpf_cnpj():
    """ Gera um CPF/CNPJ aleatório (14 dígitos) para garantir unicidade. """
    return ''.join(secrets.choice(string.digits) for _ in range(14))

def get_test_data():
    """ Retorna um dicionário com todos os dados necessários para a inserção. """
    # Garantimos que o email também seja único para evitar conflito
    unique_number = random.randint(1000, 9999) 
    return {
        "cpf_cnpj": generate_random_cpf_cnpj(),
        "nome": "Cliente Teste Pytest",
        "email": f"teste_{unique_number}@cleanup.com",
        "telefone": "77981177487",
        "sexo": 'M',
        "localizacao_data": {
            "cep": "99999-999",
            "logradouro": "Rua Teste",
            "numero": "1",
            "bairro": "Bairro Teste",
            "cidade": "Cidade Teste",
            "uf": "SP"
        }
    }

def setup_test_client():
    """ Insere um cliente completo para ser usado em testes e retorna o ID. """
    data = get_test_data()
    
    # Chama o INSERT do DAO com todos os 6 argumentos
    new_id = cliente_dao.insert(
        data['cpf_cnpj'], 
        data['nome'], 
        data['email'],
        data['telefone'],  
        data['sexo'],      
        data['localizacao_data'] 
    )
    
    return new_id, data['cpf_cnpj']

def cleanup_inserted_cliente(cliente_id):
    """ Tenta deletar o cliente e sua localização para limpar o banco real. """
    cliente_dao.delete(cliente_id) # Usa a função de delete do DAO (que remove as duas tabelas)

# --- Testes de Integração CRUD ---

def test_01_dao_find_all_read_all():
    """ Testa se a conexão funciona e se find_all retorna uma lista. """
    clientes = cliente_dao.find_all()
    assert isinstance(clientes, list), "find_all deve retornar uma lista."


def test_02_dao_insert_create_and_read_one():
    """ Testa a inserção de um cliente e o método find_by_id, verificando os novos campos. """
    data = get_test_data()
    
    # 1. CREATE: Insere o cliente (COM TODOS OS ARGUMENTOS)
    new_id = cliente_dao.insert(
        data['cpf_cnpj'], 
        data['nome'], 
        data['email'],
        data['telefone'],  
        data['sexo'],      
        data['localizacao_data']
    )
    
    assert new_id is not None
    
    # 2. READ ONE: Busca pelo ID inserido
    inserted_cliente = cliente_dao.find_by_id(new_id)
    
    # Verifica se os novos campos foram salvos
    assert inserted_cliente is not None
    assert inserted_cliente['nome'] == data['nome']
    assert inserted_cliente['telefone'] == data['telefone'] # Verifica telefone
    
    # --- Limpeza (Teardown) ---
    cleanup_inserted_cliente(new_id)

def test_03_dao_update_update():
    """ Testa a atualização de um cliente existente. """
    # SETUP: Insere um cliente para manipular
    cliente_id, _ = setup_test_client()
    novo_nome = "Nome Atualizado Pytest"
    novo_email = "novo.email.update@teste.com"
    
    # UPDATE: Chama a função de atualização, passando o nome e o novo email
    rows_affected = cliente_dao.update(cliente_id, nome=novo_nome, email=novo_email)
    
    # 1. Verifica se UMA linha foi afetada (Sucesso!)
    assert rows_affected == 1, "O update falhou. Deve retornar 1 (linha afetada)."
    
    # 2. READ ONE: Busca o cliente para confirmar a alteração
    updated_cliente = cliente_dao.find_by_id(cliente_id)
    
    # Verifica se o nome e o email foram alterados
    assert updated_cliente is not None
    assert updated_cliente['nome'] == novo_nome
    assert updated_cliente['email'] == novo_email 

    # --- Limpeza (Teardown) ---
    cleanup_inserted_cliente(cliente_id)

def test_04_dao_delete_delete():
    """ Testa a remoção de um cliente e sua localização. """
    # SETUP: Insere um cliente para deletar
    cliente_id, _ = setup_test_client()
    
    # 1. DELETE: Chama a função de exclusão
    rows_affected = cliente_dao.delete(cliente_id)
    
    # Verifica se uma linha foi afetada (sucesso)
    assert rows_affected == 1
    
    # 2. READ ONE: Tenta buscar o cliente deletado
    deleted_cliente = cliente_dao.find_by_id(cliente_id)
    
    # Verifica se o cliente não existe mais
    assert deleted_cliente is None

def test_05_dao_update_no_changes():
    """ Testa a atualização sem passar novos dados. """
    cliente_id, _ = setup_test_client()
    
    # UPDATE: Chama a função sem passar 'nome', 'email', etc.
    rows_affected = cliente_dao.update(cliente_id) 
    
    # Verifica se 0 linhas foram afetadas (correto, pois nada mudou)
    assert rows_affected == 0
    
    # --- Limpeza (Teardown) ---
    cleanup_inserted_cliente(cliente_id)
    
# --- Testes de Regras de Negócio e Conflitos ---

def test_06_dao_update_with_location():
    """ Testa a atualização de dados do cliente e da localização ao mesmo tempo. """
    cliente_id, _ = setup_test_client()
    
    novo_telefone = "99988877766"
    novo_cep = "1111111111" # Apenas números para o DB
    
    # 1. UPDATE: Chama a função de atualização, alterando campos de Cliente e Localização
    rows_affected = cliente_dao.update(
        cliente_id, 
        telefone=novo_telefone,
        localizacao_data={'cep': novo_cep, 'cidade': 'Nova Cidade Testada'}
    )
    
    # Verifica se a atualização ocorreu
    assert rows_affected == 1, "O update falhou ao atualizar dados de Cliente e Localização."
    
    # 2. READ ONE: Busca o cliente para confirmar as alterações
    updated_cliente = cliente_dao.find_by_id(cliente_id)
    
    # Verifica se os campos foram alterados
    assert updated_cliente is not None
    assert updated_cliente['telefone'] == novo_telefone 
    assert updated_cliente['cep'] == novo_cep           

    # --- Limpeza (Teardown) ---
    cleanup_inserted_cliente(cliente_id)


def test_07_dao_insert_duplicate_cpf_cnpj():
    """ Testa se a inserção falha e retorna None ao tentar usar um CPF/CNPJ duplicado. """
    
    # SETUP: Insere o primeiro cliente (que será o duplicado)
    data1 = get_test_data()
    cliente_id, duplicate_cpf = setup_test_client()
    
    # 1. Tenta inserir um SEGUNDO cliente com o mesmo CPF/CNPJ
    data2 = get_test_data()
    data2['cpf_cnpj'] = duplicate_cpf # Define o valor duplicado
    
    # Tenta executar o INSERT (Espera-se que o banco lance um erro UNIQUE)
    new_id = cliente_dao.insert(
        data2['cpf_cnpj'], 
        data2['nome'], 
        data2['email'],
        data2['telefone'],  
        data2['sexo'],      
        data2['localizacao_data']
    )
    
    # 2. Verifica se o DAO tratou o erro e retornou None
    assert new_id is None, "O DAO não tratou corretamente a exceção de CPF/CNPJ duplicado (UNIQUE constraint)."

    # --- Limpeza (Teardown) ---
    cleanup_inserted_cliente(cliente_id)
    