# tests/test_transacoes_dao.py

import pytest
import random
from decimal import Decimal
from src.models.venda_dao import VendaDAO
from src.models.compra_dao import CompraDAO
from src.models.devolucao_dao import DevolucaoDAO
from src.models.produto_dao import ProdutoDAO
from src.models.estoque_dao import EstoqueDAO
from src.models.funcionario_dao import FuncionarioDAO 
from src.schemas.venda_schema import VendaSchema 
from src.schemas.devolucao_schema import DevolucaoSchema 
from src.schemas.compra_schema import CompraSchema
import secrets
from datetime import date

# Instanciação dos DAOs necessários
venda_dao = VendaDAO()
compra_dao = CompraDAO()
devolucao_dao = DevolucaoDAO()
produto_dao = ProdutoDAO()
estoque_dao = EstoqueDAO()
funcionario_dao = FuncionarioDAO()

# Instanciação dos Schemas (Variáveis globais)
venda_schema = VendaSchema() 
devolucao_schema = DevolucaoSchema() 
compra_schema = CompraSchema()


# --- Helpers de Setup ---

def criar_dados_basicos_para_produto(initial_quantity=50, preco="10.00"):
    """ Cria um produto e dados base para simular transações. """
    dados_produto = {
        "nome": f"Produto Transacao {random.randint(1, 1000)}", 
        "descricao": "Item de teste para transacoes",
        "preco": preco, 
        "codigo_barras": f"{random.randint(10**12, 10**13 - 1)}",
        "initial_quantity": initial_quantity
    }
    codigo_produto = produto_dao.insert(
        dados_produto['nome'], 
        dados_produto['descricao'], 
        dados_produto['preco'],
        dados_produto['codigo_barras'],
        dados_produto['initial_quantity']
    )
    
    return {
        "codigo_produto": codigo_produto,
        "preco_unitario": Decimal(preco),
        "cpf_funcionario": "00000000000",
        "id_tipo_pagamento_dinheiro": 1, # Dinheiro
        "id_fornecedor": 1 # Fornecedor de teste
    }

def realizar_venda_simulada(dados_base, quantidade_venda=10):
    """ Executa uma venda de sucesso e retorna o ID da venda e o código do produto. """
    
    # CORREÇÃO: Acessa a variável global instanciada no topo do arquivo
    global venda_schema 
    
    PRECO = dados_base['preco_unitario']
    valor_pago = (quantidade_venda * PRECO).to_eng_string()
    
    venda_json = {
        "cpf_funcionario": dados_base['cpf_funcionario'],
        "itens": [
            {
                "codigo_produto": dados_base['codigo_produto'],
                "quantidade_venda": quantidade_venda,
                "preco_unitario": PRECO.to_eng_string()
            }
        ],
        "pagamentos": [
            {
                "id_tipo": dados_base['id_tipo_pagamento_dinheiro'],
                "valor_pago": valor_pago
            }
        ]
    }
    
    validated_data = venda_schema.load(venda_json)
    id_venda = venda_dao.registrar_venda(validated_data)
    
    return id_venda, dados_base['codigo_produto']

def limpar_dados_transacao(codigo_produto):
    """ Deleta o produto de teste (que deleta o estoque). """
    if codigo_produto:
        produto_dao.delete(codigo_produto)
    

# --- Testes de Transação: VENDA, DEVOLUÇÃO e COMPRA ---

def test_01_venda_baixa_estoque_com_sucesso():
    """ 
    Testa se a transação de VENDA subtrai o estoque atomicamente. (50 -> 40)
    """
    dados_base = criar_dados_basicos_para_produto(initial_quantity=50)
    codigo_produto = dados_base['codigo_produto']
    
    # 1. REGISTRA A VENDA
    id_venda, _ = realizar_venda_simulada(dados_base, quantidade_venda=10)
    assert id_venda is not None
    
    # 2. VERIFICAÇÃO: Estoque deve ser 40
    registro_estoque = estoque_dao.find_by_product_id(codigo_produto)['quantidade']
    assert registro_estoque == 40
    
    # --- Limpeza ---
    limpar_dados_transacao(codigo_produto)


def test_02_venda_falha_por_estoque_insuficiente():
    """ 
    Testa se a transação de VENDA falha e faz ROLLBACK. (Vende 60 do estoque de 50)
    """
    dados_base = criar_dados_basicos_para_produto(initial_quantity=50)
    codigo_produto = dados_base['codigo_produto']
    
    QUANTIDADE_VENDIDA = 60 # Vai falhar no UPDATE: 50 - 60 = -10
    PRECO_UNITARIO = dados_base['preco_unitario']
    
    venda_json = {
        "cpf_funcionario": dados_base['cpf_funcionario'],
        "itens": [
            {"codigo_produto": codigo_produto, "quantidade_venda": QUANTIDADE_VENDIDA, "preco_unitario": PRECO_UNITARIO.to_eng_string()}
        ],
        "pagamentos": [
            {"id_tipo": dados_base['id_tipo_pagamento_dinheiro'], "valor_pago": (QUANTIDADE_VENDIDA * PRECO_UNITARIO).to_eng_string()}
        ]
    }
    
    validated_data = venda_schema.load(venda_json)
    id_venda = venda_dao.registrar_venda(validated_data)
    
    assert id_venda is None
    
    # Assertiva: O estoque DEVE PERMANECER INALTERADO (50)
    registro_estoque = estoque_dao.find_by_product_id(codigo_produto)
    assert registro_estoque['quantidade'] == 50
    
    # --- Limpeza ---
    limpar_dados_transacao(codigo_produto)


def test_03_devolucao_restaura_estoque_com_sucesso():
    """ 
    CORREÇÃO DE ESCOPO: Testa a transação de DEVOLUÇÃO: restaura o estoque. (50 -> 40 -> 45)
    """
    # É NECESSÁRIO DECLARAR GLOBAL DEVIDO AO ESCOPO DA FUNÇÃO
    global devolucao_schema
    
    dados_base = criar_dados_basicos_para_produto(initial_quantity=50)
    codigo_produto = dados_base['codigo_produto']
    
    # SETUP: 1. Vende 10 unidades (Estoque: 50 -> 40)
    id_venda, _ = realizar_venda_simulada(dados_base, quantidade_venda=10)
    
    # 2. REGISTRA A DEVOLUÇÃO de 5 unidades
    QUANTIDADE_DEVOLVIDA = 5 
    PRECO_UNITARIO = dados_base['preco_unitario']
    
    devolucao_json = {
        "id_venda": id_venda,
        "motivo": "Cliente desistiu da compra",
        "itens": [
            {
                "codigo_produto": codigo_produto,
                "quantidade_devolvida": QUANTIDADE_DEVOLVIDA,
                "valor_unitario": PRECO_UNITARIO.to_eng_string()
            }
        ]
    }
    
    validated_data = devolucao_schema.load(devolucao_json)
    id_devolucao = devolucao_dao.registrar_devolucao(validated_data)
    
    # Assertiva 1: Devolução deve ser registrada com sucesso
    assert id_devolucao is not None
    
    # Assertiva 2: Verifica a restauração do estoque (40 + 5 = 45)
    estoque_final = estoque_dao.find_by_product_id(codigo_produto)['quantidade']
    assert estoque_final == 45
    
    # --- Limpeza ---
    limpar_dados_transacao(codigo_produto)


def test_04_compra_aumento_estoque_com_sucesso():
    """ 
    Testa a transação de COMPRA: registra a compra e aumenta o estoque. (50 -> 150)
    """
    # É NECESSÁRIO DECLARAR GLOBAL DEVIDO AO ESCOPO DA FUNÇÃO
    global compra_schema 
    
    dados_base = criar_dados_basicos_para_produto(initial_quantity=50, preco="1.00")
    codigo_produto = dados_base['codigo_produto']
    
    QUANTIDADE_COMPRADA = 100
    PRECO_UNITARIO = Decimal("0.80") # Preço de custo
    
    compra_json = {
        "id_fornecedor": dados_base['id_fornecedor'],
        "data_compra": date.today().isoformat(),
        "itens": [
            {
                "codigo_produto": codigo_produto,
                "quantidade_compra": QUANTIDADE_COMPRADA,
                "preco_unitario": PRECO_UNITARIO.to_eng_string()
            }
        ]
    }
    
    validated_data = compra_schema.load(compra_json)
    id_compra = compra_dao.registrar_compra(validated_data)
    
    # 1. Assertiva: A compra deve ser registrada com sucesso
    assert id_compra is not None
    
    # 2. Assertiva: Verifica o aumento no estoque (50 + 100 = 150)
    registro_estoque = estoque_dao.find_by_product_id(codigo_produto)
    assert registro_estoque['quantidade'] == 150
    
    # --- Limpeza ---
    limpar_dados_transacao(codigo_produto)