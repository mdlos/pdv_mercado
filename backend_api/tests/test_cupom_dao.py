import pytest
from src.models.cupom_dao import CupomDAO
from src.db_connection import get_db_connection
import logging

logger = logging.getLogger(__name__)

# --- DADOS DE TESTE REUTILIZÁVEIS ---
CPF_FUNCIONARIO_TESTE = '99999999999' 
EMAIL_FUNCIONARIO_TESTE = 'caixa.dao.test@exclusivo.com'
ID_CLIENTE_TESTE = 888
CODIGO_PRODUTO_TESTE = 999 
NOME_PRODUTO_TESTE = "Produto Teste DAO"
NUMERO_NF_TESTE = "TEST-NF-001"

# Dados que simulam o que viria do frontend
ITENS_TESTE = [
    {"codigo_produto": CODIGO_PRODUTO_TESTE, "quantidade": 2, "preco_unitario": 10.50},
    {"codigo_produto": 888, "quantidade": 1, "preco_unitario": 5.00},
]

# -------------------------------------------------------------------------
# FIXTURES (SETUP E TEARDOWN) - VERSÃO FINAL CORRIGIDA
# -------------------------------------------------------------------------

@pytest.fixture(scope="module")
def setup_teardown_db():
    conn = get_db_connection()
    if conn is None:
        raise Exception("Não foi possível conectar ao banco de dados para o teste.")

    # Dados de SETUP
    try:
        cur = conn.cursor()

        # 1. INSERIR FUNCIONÁRIO (Usando CPF como PK)
        cur.execute("""
            INSERT INTO funcionario (cpf, nome, email, senha, id_tipo_funcionario) 
            VALUES (%s, 'Caixa Teste', %s, 'hash_fake', 1)
            ON CONFLICT (cpf) DO NOTHING;
        """, (CPF_FUNCIONARIO_TESTE, EMAIL_FUNCIONARIO_TESTE))

        # 2. INSERIR PRODUTOS (Usando OVERRIDING SYSTEM VALUE e INTEGER)
        cur.execute("""
            INSERT INTO produto (codigo_produto, nome, descricao, preco) 
            OVERRIDING SYSTEM VALUE
            VALUES (%s, %s, 'Descrição Teste', 10.50)
            ON CONFLICT (codigo_produto) DO NOTHING;
        """, (CODIGO_PRODUTO_TESTE, NOME_PRODUTO_TESTE))
        
        cur.execute("""
            INSERT INTO produto (codigo_produto, nome, descricao, preco) 
            OVERRIDING SYSTEM VALUE
            VALUES (888, 'Produto B', 'Descrição Produto B', 5.00)
            ON CONFLICT (codigo_produto) DO NOTHING;
        """)

        # 3. INSERIR CLIENTE (Com OVERRIDING SYSTEM VALUE e coluna 'cpf_cnpj')
        cur.execute("""
            INSERT INTO cliente (id_cliente, cpf_cnpj, nome) 
            OVERRIDING SYSTEM VALUE
            VALUES (%s, '88888888888', 'Cliente Teste')
            ON CONFLICT (id_cliente) DO NOTHING;
        """, (ID_CLIENTE_TESTE,))

        # 4. INSERIR CONFIGURAÇÃO DE MERCADO (ID 1)
        cur.execute("""
            INSERT INTO configuracao_mercado (id_config, cnpj, razao_social, endereco, contato) 
            VALUES (1, '00000000000001', 'Mercado Teste', 'Rua Teste', '9999-9999')
            ON CONFLICT (id_config) DO NOTHING;
        """)
        
        conn.commit()

    except Exception as e:
        conn.rollback()
        logger.error(f"Erro no SETUP do DB: {e}")
        try:
             cur.execute("DELETE FROM funcionario WHERE cpf = %s", (CPF_FUNCIONARIO_TESTE,))
             conn.commit()
        except:
             pass
        raise
    finally:
        if conn: conn.close()

    # 🛑 APENAS UM YIELD: INÍCIO DA EXECUÇÃO DOS TESTES
    yield

    # ------------------------------------
    # TEARDOWN: Limpar Dados Criados
    # ------------------------------------
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            
            # Deleta Itens e Cupom
            cur.execute("DELETE FROM item_cupom WHERE id_cupom IN (SELECT id_cupom FROM cupom WHERE numero_nf IN (%s, %s, %s, %s))", (NUMERO_NF_TESTE, "TEST-NF-002", "TEST-NF-003", "TEST-NF-004"))
            cur.execute("DELETE FROM cupom WHERE numero_nf IN (%s, %s, %s, %s)", (NUMERO_NF_TESTE, "TEST-NF-002", "TEST-NF-003", "TEST-NF-004"))
            
            # Deleta Dados de Referência
            cur.execute("DELETE FROM funcionario WHERE cpf = %s", (CPF_FUNCIONARIO_TESTE,))
            cur.execute("DELETE FROM produto WHERE codigo_produto IN (%s, %s)", (CODIGO_PRODUTO_TESTE, 888))
            cur.execute("DELETE FROM cliente WHERE id_cliente = %s", (ID_CLIENTE_TESTE,))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Erro no TEARDOWN do DB: {e}")
            conn.rollback()
        finally:
            conn.close()

# -------------------------------------------------------------------------
# TESTES DO CUPOMDAO (Chamadas corrigidas)
# -------------------------------------------------------------------------

@pytest.mark.usefixtures("setup_teardown_db")
def test_create_cupom_success_dinheiro():
    """Testa a criação bem-sucedida de um cupom com pagamento em dinheiro."""
    dao = CupomDAO()
    
    # Valores de Pagamento
    valor_pago = 30.00
    
    id_cupom = dao.create_cupom(
        cpf_caixa=CPF_FUNCIONARIO_TESTE,
        numero_nf=NUMERO_NF_TESTE,
        itens_vendidos=ITENS_TESTE,
        condicao_pagamento='DINHEIRO',
        valor_pago=valor_pago,
        id_cliente=ID_CLIENTE_TESTE 
    )
    
    assert id_cupom is not None
    
    # Verifica os dados inseridos
    details = dao.get_cupom_details_by_id(id_cupom)
    assert details is not None
    
    # Verifica cálculos e dados do cabeçalho
    assert details['numero_nf'] == NUMERO_NF_TESTE
    assert details['valor_total'] == 26.00
    assert details['troco'] == 4.00
    assert details['valor_pago'] == 30.00
    assert details['condicao_pagamento'] == 'DINHEIRO'
    assert details['nome_cliente'] == 'Cliente Teste'
    assert details['nome_caixa'] == 'Caixa Teste'
    
    # Verifica itens
    assert len(details['itens']) == 2
    
    item1 = [item for item in details['itens'] if item['codigo_produto'] == CODIGO_PRODUTO_TESTE][0]
    assert item1['quantidade'] == 2
    assert item1['preco_unitario'] == 10.50
    assert item1['nome_produto'] == NOME_PRODUTO_TESTE


@pytest.mark.usefixtures("setup_teardown_db")
def test_create_cupom_success_cartao_sem_troco():
    """Testa a criação bem-sucedida de um cupom com pagamento em cartão."""
    dao = CupomDAO()
    
    # Valor Total: 26.00. Valor Pago: 26.00
    valor_pago = 26.00 
    
    id_cupom = dao.create_cupom(
        cpf_caixa=CPF_FUNCIONARIO_TESTE,
        numero_nf="TEST-NF-002",
        itens_vendidos=ITENS_TESTE,
        condicao_pagamento='CRÉDITO',
        valor_pago=valor_pago,
        # 🛑 CORREÇÃO AQUI: Removemos cpf_cliente da chamada
        # cpf_cliente="123.456.789-00" 
    )
    
    assert id_cupom is not None
    
    # Verifica os dados inseridos
    details = dao.get_cupom_details_by_id(id_cupom)
    assert details is not None
    
    # 🛑 CORREÇÃO AQUI: Asserção deve checar que cpf_informado é None, pois o DAO retorna NULL
    assert details['cpf_informado'] is None 
    
    # Verifica cálculos (Troco deve ser 0 em Cartão)
    assert details['valor_total'] == 26.00
    assert details['troco'] == 0.00
    assert details['condicao_pagamento'] == 'CRÉDITO'
    assert details['nome_cliente'] is None

@pytest.mark.usefixtures("setup_teardown_db")
def test_create_cupom_empty_items_fails():
    """Testa se a criação falha com a lista de itens vazia."""
    dao = CupomDAO()
    
    # O DAO deve falhar na validação do cálculo ou na inserção de itens vazios
    with pytest.raises(Exception): 
        dao.create_cupom(
            cpf_caixa=CPF_FUNCIONARIO_TESTE,
            numero_nf="TEST-NF-003",
            itens_vendidos=[],
            condicao_pagamento='DINHEIRO',
            valor_pago=10.00
        )

@pytest.mark.usefixtures("setup_teardown_db")
def test_get_cupom_details_not_found():
    """Testa a busca por um cupom que não existe."""
    dao = CupomDAO()
    details = dao.get_cupom_details_by_id(999999)
    assert details is None

@pytest.mark.usefixtures("setup_teardown_db")
def test_get_cupom_details_full_data():
    """
    Testa a recuperação completa dos dados do cupom, incluindo todos os JOINs.
    """
    dao = CupomDAO()
    
    # 1. Cria o cupom (SETUP dentro do teste)
    id_cupom = dao.create_cupom(
        cpf_caixa=CPF_FUNCIONARIO_TESTE,
        numero_nf="TEST-NF-004",
        itens_vendidos=ITENS_TESTE,
        condicao_pagamento='PIX',
        valor_pago=26.00,
        id_cliente=ID_CLIENTE_TESTE
    )
    assert id_cupom is not None
    
    # 2. Busca e validação
    details = dao.get_cupom_details_by_id(id_cupom)
    
    assert details is not None
    
    # Validação do Cabeçalho e JOINs (mercado, caixa, cliente)
    assert details['numero_nf'] == "TEST-NF-004"
    assert details['nome_caixa'] == 'Caixa Teste'
    assert details['nome_cliente'] == 'Cliente Teste'
    assert details['cnpj'] == '00000000000001'
    assert details['razao_social'] == 'Mercado Teste'
    assert details['valor_total'] == 26.00
    assert details['condicao_pagamento'] == 'PIX'
    
    # Validação dos Itens
    assert isinstance(details['itens'], list)
    assert len(details['itens']) == 2
    
    # Validação de item específico com nome do produto e preço
    item_teste = [item for item in details['itens'] if item['codigo_produto'] == CODIGO_PRODUTO_TESTE][0]
    assert item_teste['nome_produto'] == NOME_PRODUTO_TESTE
    assert item_teste['quantidade'] == 2