# tests/test_fornecedor_dao.py

import pytest
from src.models.fornecedor_dao import FornecedorDAO
from src.db_connection import get_db_connection
from src.utils.formatters import clean_only_numbers
import random
import string
import secrets
from datetime import date, timedelta

# Cria a instância do DAO
fornecedor_dao = FornecedorDAO()

# --- Funções Auxiliares de CONFIGURAÇÃO e LIMPEZA ---

def gerar_cnpj_aleatorio():
    """ Gera um CNPJ de 14 dígitos totalmente único. """
    return ''.join(secrets.choice(string.digits) for _ in range(14))

def obter_dados_teste():
    """ Retorna um dicionário com dados válidos e únicos para a inserção. """
    cnpj_unico = gerar_cnpj_aleatorio()
    return {
        "cnpj": cnpj_unico,
        "razao_social": f"Fornecedor Teste {secrets.token_hex(4)}",
        "email": f"teste_{cnpj_unico}@fornecedor.com", 
        "celular": "9988877766",
        "data_abertura": date.today().isoformat(),
        "localizacao_data": {
            "cep": "54321000",
            "logradouro": "Av. Teste Integrado",
            "numero": "10",
            "cidade": "Salvador",
            "uf": "BA"
        }
    }

def configurar_teste_fornecedor(dados):
    """ Insere um fornecedor com localização, retorna o ID. """
    id_inserido = fornecedor_dao.insert(
        cnpj=dados['cnpj'],
        razao_social=dados['razao_social'],
        email=dados['email'],
        celular=dados.get('celular'),
        situacao_cadastral=None,
        data_abertura=dados.get('data_abertura'),
        localizacao_data=dados['localizacao_data']
    )
    return id_inserido

def configurar_teste_fornecedor_sem_localizacao(dados):
    """ Insere um fornecedor COM id_localizacao = NULL, retorna o ID. """
    id_inserido = fornecedor_dao.insert(
        cnpj=dados['cnpj'],
        razao_social=dados['razao_social'],
        email=dados['email'],
        celular=dados.get('celular'),
        situacao_cadastral=None,
        data_abertura=dados.get('data_abertura'),
        localizacao_data=None # Força o NULL na FK
    )
    return id_inserido

def limpar_fornecedor_inserido(id_fornecedor):
    """ Tenta deletar o fornecedor e sua localização. """
    fornecedor_dao.delete(id_fornecedor) 

# --- Testes de Integração CRUD e Transação (01-04) ---

def test_01_dao_inserir_e_verificar_transacao_atomica():
    """ Testa a criação atômica do fornecedor e localização. """
    dados = obter_dados_teste()
    id_inserido = configurar_teste_fornecedor(dados)
    
    assert id_inserido is not None
    
    # 2. READ ONE: Busca o fornecedor para verificar dados e localização
    inserted_fornecedor = fornecedor_dao.find_by_id(id_inserido)
    
    # Verifica localização
    assert inserted_fornecedor['cep'] == dados['localizacao_data']['cep']
    
    # --- Limpeza ---
    limpar_fornecedor_inserido(id_inserido)


def test_02_dao_atualizar_dados_e_localizacao():
    """ Testa a atualização atômica de dados pessoais e endereço. """
    dados = obter_dados_teste()
    id_inserido = configurar_teste_fornecedor(dados)
    
    novo_nome = "Nova Razao Social Editada"
    novo_email = f"novo_{dados['email']}"
    novo_cep = "10101000"
    
    # 1. UPDATE: Altera Nome, Email (Fornecedor) e CEP (Localização)
    rows_affected = fornecedor_dao.update(
        id_fornecedor=id_inserido,
        razao_social=novo_nome,
        email=novo_email,
        localizacao_data={'cep': novo_cep, 'numero': '199'}
    )
    
    assert rows_affected == 1, "O update falhou. Deve retornar 1 (linha afetada)."
    
    # 2. VERIFICAÇÃO: Busca e confirma a alteração
    updated_fornecedor = fornecedor_dao.find_by_id(id_inserido)
    
    assert updated_fornecedor['razao_social'] == novo_nome
    assert updated_fornecedor['email'] == novo_email
    assert updated_fornecedor['cep'] == novo_cep
    
    # --- Limpeza ---
    limpar_fornecedor_inserido(id_inserido)


def test_03_dao_delete_exclusao_atomica():
    """ Testa a remoção atômica do fornecedor e sua localização. """
    dados = obter_dados_teste()
    id_inserido = configurar_teste_fornecedor(dados)
    
    # 1. DELETE: Chama a função de exclusão
    rows_affected = fornecedor_dao.delete(id_inserido)
    
    assert rows_affected == 1
    
    # 2. VERIFICAÇÃO: Tenta buscar o fornecedor deletado
    deleted_fornecedor = fornecedor_dao.find_by_id(id_inserido)
    
    assert deleted_fornecedor is None


def test_04_dao_insert_cnpj_duplicado_deve_falhar():
    """ Testa se a inserção falha ao tentar usar um CNPJ duplicado. """
    dados = obter_dados_teste()
    
    # SETUP: Insere o primeiro fornecedor
    id_original = configurar_teste_fornecedor(dados)
    
    # Tenta inserir um SEGUNDO fornecedor com o MESMO CNPJ (deve falhar por UNIQUE)
    id_inserido_fail = fornecedor_dao.insert(
        cnpj=dados['cnpj'], # CNPJ DUPLICADO
        razao_social="Duplicado",
        email="outro@email.com", 
    )
    
    assert id_inserido_fail is None
    
    # --- Limpeza ---
    limpar_fornecedor_inserido(id_original)

# --- Testes de Casos de Borda e Atualização (05-07) ---

def test_05_dao_update_somente_razao_social():
    """ Testa a atualização APENAS da Razão Social (teste de atualização parcial). """
    dados = obter_dados_teste()
    id_inserido = configurar_teste_fornecedor(dados)
    
    novo_nome = "Razao Social Mínima Atualizada"
    
    # 1. UPDATE: Altera SÓ a Razão Social
    rows_affected = fornecedor_dao.update(
        id_fornecedor=id_inserido,
        razao_social=novo_nome
    )
    
    assert rows_affected == 1
    
    # 2. VERIFICAÇÃO: Confirma se o nome mudou, mas o e-mail permaneceu
    updated_fornecedor = fornecedor_dao.find_by_id(id_inserido)
    assert updated_fornecedor['razao_social'] == novo_nome
    assert updated_fornecedor['email'] == dados['email']

    # --- Limpeza ---
    limpar_fornecedor_inserido(id_inserido)


def test_06_dao_update_add_localizacao_where_null():
    """ Testa a adição de localização a um fornecedor que NÃO possuía endereço (transição de NULL para valor). """
    dados = obter_dados_teste()
    # SETUP: Insere sem localização (usando helper sem localização)
    id_inserido = configurar_teste_fornecedor_sem_localizacao(dados)
    
    novo_endereco = {'cep': '44444444', 'cidade': 'Nova Cidade Teste'}
    
    # 1. UPDATE: Chama o update para adicionar a localização (DAO deve fazer um INSERT na tabela 'localizacao')
    rows_affected = fornecedor_dao.update(
        id_fornecedor=id_inserido,
        localizacao_data=novo_endereco
    )
    
    # 2. VERIFICAÇÃO: Deve retornar 1 (a linha 'fornecedor' foi atualizada com a nova FK)
    assert rows_affected == 1
    
    # 3. VERIFICAÇÃO FINAL: Confirma se o endereço foi salvo
    updated_fornecedor = fornecedor_dao.find_by_id(id_inserido)
    assert updated_fornecedor['cep'] == novo_endereco['cep']
    assert updated_fornecedor['id_localizacao'] is not None

    # --- Limpeza ---
    limpar_fornecedor_inserido(id_inserido)


def test_07_dao_deletar_fornecedor_sem_localizacao():
    """ Testa se a exclusão funciona quando o id_localizacao é NULL (teste de borda). """
    dados = obter_dados_teste()
    # SETUP: Insere sem localização
    id_inserido = configurar_teste_fornecedor_sem_localizacao(dados)
    
    # 1. DELETE: Chama a função de exclusão
    rows_affected = fornecedor_dao.delete(id_inserido)
    
    # 2. VERIFICAÇÃO: Deve ser 1, e a função deve passar sem erro de ROLLBACK
    assert rows_affected == 1
    
    # --- Limpeza ---
    # A exclusão já foi feita pelo teste
    pass