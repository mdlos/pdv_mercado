# tests/test_cliente_dao_completo.py (CORRIGIDO)

import pytest
from src.models.cliente_dao import ClienteDAO
from src.db_connection import get_db_connection
import random
import string
import secrets

# Instanciação dos DAOs
cliente_dao = ClienteDAO()

# --- Funções Auxiliares de CONFIGURAÇÃO e LIMPEZA ---

def gerar_cpf_aleatorio():
    """ Gera um CPF aleatório (11 dígitos). """
    return ''.join(secrets.choice(string.digits) for _ in range(11))

def obter_dados_teste():
    """ Retorna um dicionário com dados válidos e únicos para a inserção de cliente. """
    cpf_aleatorio = gerar_cpf_aleatorio()
    return {
        "cpf_cnpj": cpf_aleatorio,
        "nome": "Cliente Teste",
        "email": f"cliente{cpf_aleatorio}@teste.com", # Email único
        "telefone": "77999887766",
        "sexo": 'F',
        "localizacao_data": {
            "cep": "11111111",
            "logradouro": "Rua Teste Cliente",
            "numero": "1",
            "cidade": "Cidade Cliente",
            "uf": "BA"
        }
    }

def setup_test_cliente(data):
    """ Insere um cliente completo para teste e retorna o ID. """
    # O ClienteDAO.insert já faz a transação Location + Client
    id_inserido = cliente_dao.insert(
        cpf_cnpj=data['cpf_cnpj'],
        nome=data['nome'],
        email=data['email'],
        telefone=data['telefone'],
        sexo=data['sexo'],
        localizacao_data=data['localizacao_data']
    )
    return id_inserido

def limpar_cliente_inserido(id_cliente):
    """ Tenta deletar o cliente e sua localização. """
    # O DAO deve deletar a localização atomicamente
    cliente_dao.delete(id_cliente) 

# --- Fixture para verificar exclusão de localização (VERALICHE helper) ---

def check_localizacao_exists(localizacao_id: int) -> bool:
    """ Verifica se a localização (endereço) existe diretamente no banco. """
    conn = get_db_connection()
    if conn is None: return False
    try:
        with conn.cursor() as cur:
            sql = "SELECT id_localizacao FROM localizacao WHERE id_localizacao = %s;"
            cur.execute(sql, (localizacao_id,))
            return cur.fetchone() is not None
    finally:
        if conn: conn.close()


# =========================================================================
# TESTES DE INTEGRAÇÃO CRUD
# =========================================================================

def test_01_inserir_e_ler_com_sucesso():
    """ Testa a transação atômica de CREATE (Cliente + Localização) e READ ONE. """
    dados = obter_dados_teste()
    
    # 1. CREATE: Insere o cliente
    id_inserido = setup_test_cliente(dados)
    
    assert id_inserido is not None
    
    # 2. READ ONE: Busca o cliente pelo ID (PK)
    cliente_db = cliente_dao.find_by_id(id_inserido)
    
    # 3. VERIFICAÇÕES
    assert cliente_db is not None
    assert cliente_db['nome'] == dados['nome']
    assert cliente_db['cep'] == dados['localizacao_data']['cep'] # Localização lida via JOIN

    # --- Limpeza ---
    limpar_cliente_inserido(id_inserido)


def test_02_busca_por_cpf_cnpj_funciona():
    """ Testa a busca pela chave de negócio (CPF/CNPJ). """
    dados = obter_dados_teste()
    id_inserido = setup_test_cliente(dados)
    
    # 1. CHAMA O DAO: Busca o cliente pelo CPF
    cliente_buscado = cliente_dao.find_by_cpf_cnpj(dados['cpf_cnpj'])
    
    # 2. ASSERÇÕES: Verifica se encontrou e se o ID é o mesmo
    assert cliente_buscado is not None
    assert cliente_buscado['id_cliente'] == id_inserido
    
    # --- Limpeza ---
    limpar_cliente_inserido(id_inserido)


def test_03_atualizacao_de_dados_e_localizacao():
    """ Testa a atualização parcial de dados pessoais e endereço. """
    dados = obter_dados_teste()
    id_inserido = setup_test_cliente(dados)
    
    novo_nome = "Cliente Atualizado Teste"
    novo_cep = "88888888"
    
    # 1. UPDATE: Altera Nome (Cliente) e CEP (Localização)
    # CORREÇÃO AQUI: Passando id_inserido como argumento posicional
    rows_affected = cliente_dao.update(
        id_inserido,  # <-- CORRIGIDO!
        nome=novo_nome,
        localizacao_data={'cep': novo_cep}
    )
    
    # 2. VERIFICAÇÃO: Deve afetar 1 linha
    assert rows_affected == 1
    
    # 3. VERIFICAÇÃO FINAL: Confirma as alterações
    cliente_atualizado = cliente_dao.find_by_id(id_inserido)
    assert cliente_atualizado['nome'] == novo_nome
    assert cliente_atualizado['cep'] == novo_cep # CEP deve ter sido alterado

    # --- Limpeza ---
    limpar_cliente_inserido(id_inserido)


def test_04_inserir_cpf_duplicado_deve_falhar():
    """ Testa a regra de negócio: Não pode haver CNPJ/CPF duplicado. """
    dados = obter_dados_teste()
    id_original = setup_test_cliente(dados) # Cliente 1 criado
    
    # Tenta inserir um SEGUNDO cliente com o MESMO CNPJ (deve falhar por UNIQUE)
    id_inserido_fail = cliente_dao.insert(
        cpf_cnpj=dados['cpf_cnpj'], # CNPJ DUPLICADO
        nome="Cliente Duplicado",
        email="duplicado@teste.com",
        telefone='11111111111',
        sexo='M',
        localizacao_data={'cep': '00000000', 'cidade': 'Falha'}
    )
    
    # 1. ASSERÇÃO: A segunda inserção deve falhar e retornar None
    assert id_inserido_fail is None
    
    # --- Limpeza ---
    limpar_cliente_inserido(id_original)


def test_05_exclusao_atomica_e_limpeza_de_localizacao():
    """ Testa a deleção atômica do Cliente e da Localização (evita dados órfãos). """
    dados = obter_dados_teste()
    id_inserido = setup_test_cliente(dados)
    
    # 1. RECUPERA ID DA LOCALIZAÇÃO: Busca o cliente para obter o ID da localização
    cliente_db = cliente_dao.find_by_id(id_inserido)
    id_loc_inserida = cliente_db['id_localizacao']
    
    # 2. VERIFICA PRÉ-EXCLUSÃO: A localização DEVE existir antes
    assert check_localizacao_exists(id_loc_inserida) is True

    # 3. CHAMA O DAO PARA EXCLUIR O CLIENTE
    rows_affected = cliente_dao.delete(id_inserido)
    
    # 4. ASSERÇÃO 1: Garante que o cliente foi excluído
    assert rows_affected == 1
    
    # 5. ASSERÇÃO 2 (VERALICHE): Verifica se a localização TAMBÉM foi excluída
    assert check_localizacao_exists(id_loc_inserida) is False, "Falha no VERALICHE: Localização órfã encontrada após delete do cliente."