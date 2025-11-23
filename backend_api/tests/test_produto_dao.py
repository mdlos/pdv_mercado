# tests/test_produto_dao.py (CONFIRMAÇÃO)

import pytest
from src.models.produto_dao import ProdutoDAO
from src.db_connection import get_db_connection
import random
import string
import secrets

# Cria a instância do DAO
produto_dao = ProdutoDAO()

# --- Funções Auxiliares de CONFIGURAÇÃO e LIMPEZA ---

def gerar_codigo_barras_unico():
    """ Gera um código de barras de 13 dígitos totalmente único. """
    return ''.join(secrets.choice(string.digits) for _ in range(13))

def obter_dados_teste():
    """ Retorna um dicionário com dados válidos e únicos para a inserção. """
    return {
        "nome": f"Produto Teste {secrets.token_hex(4)}", # NOME ÚNICO
        "descricao": "Descrição para o teste de CRUD completo.",
        "preco": "15.50", 
        "codigo_barras": gerar_codigo_barras_unico(), # CÓDIGO DE BARRAS ÚNICO
        "initial_quantity": 5
    }

def configurar_teste_produto(dados):
    """ Insere um produto e inicializa seu estoque, retorna o codigo_produto. """
    codigo_produto = produto_dao.insert(
        dados['nome'], 
        dados['descricao'], 
        dados['preco'],
        dados['codigo_barras'],
        dados['initial_quantity']
    )
    return codigo_produto

def limpar_produto_inserido(codigo_produto):
    """ Tenta deletar o produto e seu registro de estoque. """
    produto_dao.delete(codigo_produto) 

def setup_test_produto():
    dados = obter_dados_teste()
    codigo_produto = produto_dao.insert(
        dados['nome'], 
        dados['descricao'], 
        dados['preco'],
        dados['codigo_barras']
    )
    return codigo_produto, dados['nome']

# --- Testes de Integração CRUD e Transação Atômica (FINAL) ---

def test_01_dao_find_all_read_all():
    """ Testa se a conexão funciona e se find_all retorna uma lista. """
    produtos = produto_dao.find_all() 
    assert isinstance(produtos, list), "find_all deve retornar uma lista."


def test_02_dao_inserir_e_verificar_transacao_atomica():
    """ Testa a inserção do produto e verifica se o estoque inicial foi criado. """
    dados = obter_dados_teste()
    
    codigo_produto = configurar_teste_produto(dados)
    
    # VERIFICAÇÃO: Produto existe (Chamando find_by_id)
    inserted_produto = produto_dao.find_by_id(codigo_produto)
    assert inserted_produto['nome'] == dados['nome']
    
    # VERIFICAÇÃO: Estoque foi inicializado 
    from src.models.estoque_dao import EstoqueDAO
    estoque_dao = EstoqueDAO()
    registro_estoque = estoque_dao.find_by_product_id(codigo_produto)
    
    assert registro_estoque is not None
    assert registro_estoque['quantidade'] == dados['initial_quantity']
    
    limpar_produto_inserido(codigo_produto)


def test_03_dao_update_update_e_codigo_barras():
    """ Testa a atualização do nome, preço e código de barras. """
    codigo_produto, _ = setup_test_produto() 
    
    # Geramos NOVO NOME e NOVO CÓDIGO DE BARRAS ÚNICOS para o UPDATE
    novo_nome = f"Produto Editado XYZ {secrets.token_hex(4)}" 
    novo_preco = "77.77"
    novo_codigo_barras = gerar_codigo_barras_unico() 
    
    # UPDATE: Chama a função de atualização
    rows_affected = produto_dao.update(
        codigo_produto, 
        nome=novo_nome, 
        preco=novo_preco,
        codigo_barras=novo_codigo_barras
    )
    
    # 1. Verifica se UMA linha foi afetada
    assert rows_affected == 1, "O update falhou. Deve retornar 1 (linha afetada)."
    
    # 2. VERIFICAÇÃO: Busca e confirma a alteração
    updated_produto = produto_dao.find_by_id(codigo_produto)
    assert updated_produto['nome'] == novo_nome
    assert updated_produto['codigo_barras'] == novo_codigo_barras

    limpar_produto_inserido(codigo_produto)


def test_04_dao_delete_deletion():
    """ Testa a remoção atômica do produto e do registro de estoque. """
    codigo_produto, _ = setup_test_produto()
    
    rows_affected = produto_dao.delete(codigo_produto)
    
    assert rows_affected == 1
    
    # 2. VERIFICAÇÃO: Garante que o produto não existe mais
    deleted_produto = produto_dao.find_by_id(codigo_produto)
    assert deleted_produto is None
    
    # 3. VERIFICAÇÃO: Garante que o registro de estoque também sumiu
    from src.models.estoque_dao import EstoqueDAO
    estoque_dao = EstoqueDAO()
    registro_estoque = estoque_dao.find_by_product_id(codigo_produto)
    
    assert registro_estoque is None, "O registro de estoque deveria ter sido deletado."


def test_05_dao_update_sem_alteracoes():
    """ Testa a atualização sem passar novos dados. """
    codigo_produto, _ = setup_test_produto()
    
    rows_affected = produto_dao.update(codigo_produto) 
    
    assert rows_affected == 0
    
    limpar_produto_inserido(codigo_produto)


def test_06_dao_insert_price_zero_should_fail():
    """ Testa a regra de negócio do DB: Inserção falha se o preço for zero ou negativo. """
    dados = obter_dados_teste()
    
    codigo_produto_fail = produto_dao.insert(dados['nome'], dados['descricao'], "0.00", dados['codigo_barras'])
    
    assert codigo_produto_fail is None