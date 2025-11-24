# tests/test_devolucao_dao.py

import pytest
import random
from decimal import Decimal
from src.models.devolucao_dao import DevolucaoDAO
from src.models.venda_dao import VendaDAO
from src.models.produto_dao import ProdutoDAO
from src.models.estoque_dao import EstoqueDAO
from src.models.funcionario_dao import FuncionarioDAO 
from src.schemas.venda_schema import VendaSchema 
from src.schemas.devolucao_schema import DevolucaoSchema 

# Instanciação dos DAOs necessários
devolucao_dao = DevolucaoDAO() # <-- CORREÇÃO: AGORA INSTANCIADO
venda_dao = VendaDAO()
produto_dao = ProdutoDAO()
estoque_dao = EstoqueDAO()
funcionario_dao = FuncionarioDAO()

# Instanciação dos Schemas (Variáveis globais)
venda_schema = VendaSchema() 
devolucao_schema = DevolucaoSchema() 


# --- Helpers de Setup ---

def criar_dados_basicos_para_venda():
    """ Cria um produto e dados base para simular uma venda. """
    dados_produto = {
        "nome": f"Produto Devolução {random.randint(1, 100)}", 
        "descricao": "Item de teste para devolução",
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
    
    return {
        "codigo_produto": codigo_produto,
        "preco_unitario": Decimal("10.00"),
        "cpf_funcionario": "00000000000",
        "id_tipo_pagamento": 1 # Dinheiro
    }

def realizar_venda_simulada(dados_base, quantidade_venda=10):
    """ Executa uma venda de sucesso e retorna o ID da venda e o código do produto. """
    
    # É NECESSÁRIO DECLARAR GLOBAL DEVIDO AO ESCOPO DA FUNÇÃO AUXILIAR
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
                "id_tipo": dados_base['id_tipo_pagamento'],
                "valor_pago": valor_pago
            }
        ]
    }
    
    validated_data = venda_schema.load(venda_json)
    id_venda = venda_dao.registrar_venda(validated_data)
    
    return id_venda, dados_base['codigo_produto']

def limpar_dados_venda(codigo_produto, id_venda=None):
    """ Deleta o produto de teste (que deleta o estoque). """
    if codigo_produto:
        produto_dao.delete(codigo_produto)
    
    if id_venda:
        # NOTA: Assumimos que o registro de venda não é deletado para fins de auditoria
        pass 

# --- Testes de Transação de Devolução (REVERSÃO) ---

def test_01_registrar_devolucao_e_restaurar_estoque():
    """ 
    Testa o ciclo completo: Vende 10, e devolve 5, verificando se o estoque aumenta.
    (Estoque deve ir de 50 -> 40 -> 45)
    """
    dados_base = criar_dados_basicos_para_venda()
    
    # SETUP: 1. Vende 10 unidades (Estoque: 50 -> 40)
    id_venda, codigo_produto = realizar_venda_simulada(dados_base, quantidade_venda=10)
    assert id_venda is not None
    
    # 2. VERIFICAÇÃO INTERMEDIÁRIA: Estoque deve ser 40
    estoque_atual = estoque_dao.find_by_product_id(codigo_produto)['quantidade']
    assert estoque_atual == 40
    
    # --- PROCESSO DE DEVOLUÇÃO ---
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
    
    # 3. REGISTRA A DEVOLUÇÃO
    validated_data = devolucao_schema.load(devolucao_json)
    id_devolucao = devolucao_dao.registrar_devolucao(validated_data) # <-- USANDO A VARIÁVEL CORRETAMENTE
    
    # Assertiva 1: Devolução deve ser registrada com sucesso
    assert id_devolucao is not None
    
    # Assertiva 2: Verifica a restauração do estoque (40 + 5 = 45)
    estoque_final = estoque_dao.find_by_product_id(codigo_produto)['quantidade']
    assert estoque_final == 45
    
    # --- Limpeza ---
    limpar_dados_venda(codigo_produto, id_venda)


def test_02_registrar_devolucao_com_venda_inexistente_deve_falhar():
    """ 
    Testa se a transação falha (retorna None) quando o id_venda não existe (FK).
    """
    dados_base = criar_dados_basicos_para_venda()
    codigo_produto = dados_base['codigo_produto']
    
    ID_VENDA_INVALIDA = 9999999 # ID que certamente não existe
    
    devolucao_json = {
        "id_venda": ID_VENDA_INVALIDA, # <-- CAUSA FALHA DE FK
        "motivo": "Venda Inexistente",
        "itens": [
            {
                "codigo_produto": codigo_produto,
                "quantidade_devolvida": 1,
                "valor_unitario": dados_base['preco_unitario'].to_eng_string()
            }
        ]
    }
    
    validated_data = devolucao_schema.load(devolucao_json)
    
    # REGISTRA A DEVOLUÇÃO (Espera-se que retorne None devido à falha de FK)
    id_devolucao = devolucao_dao.registrar_devolucao(validated_data) # <-- USANDO A VARIÁVEL CORRETAMENTE
    
    # Assertiva: A devolução deve falhar
    assert id_devolucao is None
    
    # Assertiva: O estoque DEVE PERMANECER INALTERADO (50)
    estoque_final = estoque_dao.find_by_product_id(codigo_produto)['quantidade']
    assert estoque_final == 50
    
    # --- Limpeza ---
    limpar_dados_venda(codigo_produto)