# tests/test_venda_dao.py

import pytest
import random
from decimal import Decimal
from src.models.venda_dao import VendaDAO
from src.models.produto_dao import ProdutoDAO
from src.models.estoque_dao import EstoqueDAO
from src.models.funcionario_dao import FuncionarioDAO
from src.schemas.venda_schema import VendaSchema

# Instanciação dos DAOs necessários
venda_dao = VendaDAO()
produto_dao = ProdutoDAO()
estoque_dao = EstoqueDAO()
funcionario_dao = FuncionarioDAO()

# Instanciação do Schema (para obter a lógica de validação/cálculo)
venda_schema = VendaSchema()

# --- Helpers de Setup ---

def criar_dados_basicos_para_venda():
    """ Cria um produto e um funcionário com um estoque inicial (50) para o teste. """
    # 1. Cria um Produto com Estoque
    dados_produto = {
        "nome": f"Produto Venda {random.randint(1, 100)}", 
        "descricao": "Item de teste para venda",
        "preco": "10.00", 
        "codigo_barras": f"{random.randint(10**12, 10**13 - 1)}",
        "initial_quantity": 50 # Estoque inicial
    }
    codigo_produto = produto_dao.insert(
        dados_produto['nome'], 
        dados_produto['descricao'], 
        dados_produto['preco'],
        dados_produto['codigo_barras'],
        dados_produto['initial_quantity']
    )
    
    # 2. Assume que o Admin (00000000000) e o Tipo de Pagamento (ID 1 - Dinheiro) existem
    
    return {
        "codigo_produto": codigo_produto,
        "preco_unitario": Decimal("10.00"),
        "cpf_funcionario": "00000000000",
        "id_tipo_pagamento": 1
    }

def limpar_dados_venda(codigo_produto, id_venda=None):
    """ Deleta o produto de teste (que deleta o estoque) e a venda, se criada. """
    if codigo_produto:
        # Usa o DAO para deletar o produto (que executa a exclusão atômica)
        produto_dao.delete(codigo_produto)
    
    # ATENÇÃO: Para testes, precisamos deletar o registro de venda,
    # mas o VendaDAO não tem um delete público. Assumimos que o teste não
    # falhou na criação do produto, ou o teste de exclusão da venda será manual.
    # Se você precisar de um DELETE de venda, ele precisará ser implementado no VendaDAO.
    pass 

# --- Testes de Transação e Integridade ---

def test_01_registrar_venda_com_baixa_estoque():
    """ 
    Testa se a transação registra a venda e subtrai o estoque atomicamente. (50 -> 40)
    """
    dados_base = criar_dados_basicos_para_venda()
    codigo_produto = dados_base['codigo_produto']
    
    QUANTIDADE_VENDIDA = 10
    PRECO_UNITARIO = dados_base['preco_unitario']
    
    # 1. Monta o JSON de Venda
    venda_json = {
        "cpf_funcionario": dados_base['cpf_funcionario'],
        "itens": [
            {
                "codigo_produto": codigo_produto,
                "quantidade_venda": QUANTIDADE_VENDIDA,
                "preco_unitario": PRECO_UNITARIO.to_eng_string()
            }
        ],
        "pagamentos": [
            {
                "id_tipo": dados_base['id_tipo_pagamento'],
                "valor_pago": (QUANTIDADE_VENDIDA * PRECO_UNITARIO).to_eng_string()
            }
        ]
    }
    
    # 2. Valida e Calcula o Total
    validated_data = venda_schema.load(venda_json)
    
    # 3. REGISTRA A VENDA
    id_venda = venda_dao.registrar_venda(validated_data)
    
    # Assertiva 1: A venda deve ser registrada com sucesso
    assert id_venda is not None
    
    # Assertiva 2: Verifica a baixa no estoque (50 - 10 = 40)
    registro_estoque = estoque_dao.find_by_product_id(codigo_produto)
    assert registro_estoque['quantidade'] == 40
    
    # --- Limpeza ---
    limpar_dados_venda(codigo_produto, id_venda)


def test_02_registrar_venda_com_estoque_insuficiente_deve_falhar():
    """ 
    Testa se a transação falha (retorna None) quando o estoque fica negativo. 
    (Vende 60 unidades do estoque de 50).
    """
    dados_base = criar_dados_basicos_para_venda()
    codigo_produto = dados_base['codigo_produto']
    
    QUANTIDADE_VENDIDA = 60 # Vai falhar no UPDATE: 50 - 60 = -10
    PRECO_UNITARIO = dados_base['preco_unitario']
    
    # 1. Monta o JSON de Venda
    venda_json = {
        "cpf_funcionario": dados_base['cpf_funcionario'],
        "itens": [
            {
                "codigo_produto": codigo_produto,
                "quantidade_venda": QUANTIDADE_VENDIDA,
                "preco_unitario": PRECO_UNITARIO.to_eng_string()
            }
        ],
        "pagamentos": [
            {
                "id_tipo": dados_base['id_tipo_pagamento'],
                "valor_pago": (QUANTIDADE_VENDIDA * PRECO_UNITARIO).to_eng_string()
            }
        ]
    }
    
    # 2. Valida e Calcula o Total
    validated_data = venda_schema.load(venda_json)
    
    # 3. REGISTRA A VENDA (Espera-se que retorne None)
    id_venda = venda_dao.registrar_venda(validated_data)
    
    # Assertiva: A venda deve falhar
    assert id_venda is None
    
    # Assertiva: O estoque DEVE PERMANECER INALTERADO (50), devido ao ROLLBACK
    registro_estoque = estoque_dao.find_by_product_id(codigo_produto)
    assert registro_estoque['quantidade'] == 50
    
    # --- Limpeza ---
    limpar_dados_venda(codigo_produto)


def test_03_registrar_venda_com_tipo_pagamento_inexistente_deve_falhar():
    """
    Testa se a transação falha e faz ROLLBACK quando o ID do tipo de pagamento (FK) não existe.
    """
    dados_base = criar_dados_basicos_para_venda()
    codigo_produto = dados_base['codigo_produto']
    
    # ID de tipo de pagamento que NÃO EXISTE no banco (ex: ID 999)
    ID_TIPO_INVALIDO = 999 
    QUANTIDADE_VENDIDA = 1 
    PRECO_UNITARIO = dados_base['preco_unitario']
    
    venda_json = {
        "cpf_funcionario": dados_base['cpf_funcionario'],
        "itens": [
            {
                "codigo_produto": codigo_produto,
                "quantidade_venda": QUANTIDADE_VENDIDA,
                "preco_unitario": PRECO_UNITARIO.to_eng_string()
            }
        ],
        "pagamentos": [
            {
                "id_tipo": ID_TIPO_INVALIDO, # <-- CAUSA A FALHA DE FK
                "valor_pago": PRECO_UNITARIO.to_eng_string()
            }
        ]
    }
    
    validated_data = venda_schema.load(venda_json)
    
    id_venda = venda_dao.registrar_venda(validated_data)
    
    assert id_venda is None
    
    # Assertiva: O estoque DEVE PERMANECER INALTERADO (50) devido ao ROLLBACK
    registro_estoque = estoque_dao.find_by_product_id(codigo_produto)
    assert registro_estoque['quantidade'] == 50
    
    # --- Limpeza ---
    limpar_dados_venda(codigo_produto)


def test_04_registrar_venda_com_produto_inexistente_deve_falhar():
    """
    Testa se a transação falha e faz ROLLBACK quando um item (produto) não é encontrado.
    """
    dados_base = criar_dados_basicos_para_venda()
    codigo_produto_valido = dados_base['codigo_produto']
    
    CODIGO_PRODUTO_INVALIDO = 99999 # Um ID que certamente não existe
    
    PRECO_UNITARIO = dados_base['preco_unitario']
    ID_TIPO_PAGAMENTO = dados_base['id_tipo_pagamento']
    
    venda_json = {
        "cpf_funcionario": dados_base['cpf_funcionario'],
        "itens": [
            {
                "codigo_produto": CODIGO_PRODUTO_INVALIDO, # <-- CAUSA FALHA NO UPDATE DE ESTOQUE
                "quantidade_venda": 1,
                "preco_unitario": PRECO_UNITARIO.to_eng_string()
            }
        ],
        "pagamentos": [
            {
                "id_tipo": ID_TIPO_PAGAMENTO,
                "valor_pago": PRECO_UNITARIO.to_eng_string()
            }
        ]
    }
    
    validated_data = venda_schema.load(venda_json)
    
    id_venda = venda_dao.registrar_venda(validated_data)
    
    assert id_venda is None
    
    # Assertiva: O estoque do produto VÁLIDO (codigo_produto_valido) DEVE PERMANECER INALTERADO
    registro_estoque = estoque_dao.find_by_product_id(codigo_produto_valido)
    assert registro_estoque['quantidade'] == 50
    
    # --- Limpeza ---
    limpar_dados_venda(codigo_produto_valido)