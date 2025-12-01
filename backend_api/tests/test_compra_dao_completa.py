# tests/test_compra_dao_completa.py (VERSÃO FINAL COM APENAS TESTE DE SUCESSO)

import pytest
from decimal import Decimal
from datetime import date
import random
import secrets
import string

# Importação dos DAOs necessários
from src.models.compra_dao import CompraDAO
from src.models.produto_dao import ProdutoDAO
from src.models.estoque_dao import EstoqueDAO
from src.models.fornecedor_dao import FornecedorDAO 
from src.schemas.compra_schema import CompraSchema
from src.db_connection import get_db_connection

# Instanciação dos DAOs e Schemas
compra_dao = CompraDAO()
produto_dao = ProdutoDAO()
estoque_dao = EstoqueDAO()
fornecedor_dao = FornecedorDAO()
compra_schema = CompraSchema()

# --- Constantes e Variáveis Globais de Teste ---

PRECO_CUSTO = Decimal("0.80")
GLOBAL_IDS = {} 

def gerar_codigo_aleatorio(length=13):
    """ Gera um código de produto/barras aleatório (13 dígitos). """
    return ''.join(secrets.choice(string.digits) for _ in range(length))

# --- Fixture de Setup de Pré-requisitos (EXECUTA ANTES DE TUDO) ---

@pytest.fixture(scope="session", autouse=True)
def setup_prerequisitos_compra():
    """ 
    Garante que as entidades Fornecedor e Produto existam no banco, 
    buscando ou criando-as se necessário.
    """
    global GLOBAL_IDS
    conn = get_db_connection()
    if conn is None: 
        pytest.skip("Conexão com o banco falhou. Pulando testes de Compra.")
        return

    # print("\n--- Configurando Pré-requisitos de Compra (Buscando/Criando) ---")

    # --- 1. FORNECEDOR ---
    fornecedores = fornecedor_dao.find_all() 
    if fornecedores:
        GLOBAL_IDS['id_fornecedor'] = fornecedores[0]['id_fornecedor']
    else:
        # Cria um mínimo se não houver
        cnpj_aleatorio = gerar_codigo_aleatorio(14)
        id_f = fornecedor_dao.insert(
            cnpj=cnpj_aleatorio,
            razao_social="Fornecedor Teste Mínimo",
            email=f"minimo_{cnpj_aleatorio}@teste.com",
            celular="999999999",
            localizacao_data={"cep": "11111000", "cidade": "SP", "uf": "SP"}
        )
        GLOBAL_IDS['id_fornecedor'] = id_f

    # --- 2. PRODUTO ---
    produtos = produto_dao.find_all() 
    
    if produtos:
        GLOBAL_IDS['codigo_produto'] = produtos[0]['codigo_produto']
        GLOBAL_IDS['estoque_inicial'] = produtos[0]['quantidade']
    else:
        # Cria um produto mínimo
        codigo_p = produto_dao.insert(
            "Produto Minimo Compra", "Desc", "1.00", gerar_codigo_aleatorio(), 50
        )
        GLOBAL_IDS['codigo_produto'] = codigo_p
        GLOBAL_IDS['estoque_inicial'] = 50
    
    yield # Executa os testes

def limpar_produto_inserido(codigo_produto):
    """ Deleta o produto de teste (que deleta o estoque). """
    if codigo_produto:
        produto_dao.delete(codigo_produto)

# --- Teste Principal de Transação de Compra ---

def test_01_registrar_compra_e_aumento_de_estoque_com_sucesso():
    """ 
    Testa se a transação de COMPRA registra a compra e AUMENTA o estoque atomicamente, 
    usando entidades existentes.
    """
    codigo_produto = GLOBAL_IDS.get('codigo_produto')
    id_fornecedor = GLOBAL_IDS.get('id_fornecedor')
    
    if not codigo_produto or not id_fornecedor:
        pytest.skip("Pré-requisitos (Produto e Fornecedor) não configurados.")
        
    # 1. Recupera o estoque inicial ATUAL
    estoque_inicial = estoque_dao.find_by_product_id(codigo_produto)['quantidade']
    
    QUANTIDADE_COMPRADA = 100
    PRECO_UNITARIO = PRECO_CUSTO # 0.80
    
    # 2. Monta o JSON de Compra
    compra_json = {
        "id_fornecedor": id_fornecedor, # ID dinâmico
        "data_compra": date.today().isoformat(),
        "itens": [
            {
                "codigo_produto": codigo_produto, # ID dinâmico
                "quantidade_compra": QUANTIDADE_COMPRADA,
                "preco_unitario": PRECO_UNITARIO.to_eng_string()
            }
        ]
    }
    
    # 3. Valida e Calcula o Total
    validated_data = compra_schema.load(compra_json)
    
    # 4. REGISTRA A COMPRA
    id_compra = compra_dao.registrar_compra(validated_data)
    
    # Assertiva 1: A compra deve ser registrada com sucesso
    assert id_compra is not None
    
    # Assertiva 2: Verifica o aumento no estoque
    estoque_final = estoque_dao.find_by_product_id(codigo_produto)['quantidade']
    assert estoque_final == estoque_inicial + QUANTIDADE_COMPRADA
    
    # --- Limpeza Pós-Teste (Restaura o estoque para o estado inicial para não corromper outros testes) ---
    estoque_dao.update_quantity(codigo_produto, estoque_inicial)
    produto_pos_limpeza = produto_dao.find_by_id(codigo_produto)
    assert produto_pos_limpeza['quantidade'] == estoque_inicial, "Falha na limpeza: Estoque não restaurado."