import pytest
from decimal import Decimal
from src.models.venda_dao import VendaDAO
from src.models.funcionario_dao import FuncionarioDAO 
from src.models.fluxo_caixa_dao import FluxoCaixaDAO 
from src.db_connection import get_db_connection
from src.schemas.venda_schema import VendaSchema
from psycopg.errors import CheckViolation, UniqueViolation, UndefinedColumn 
import logging

logger = logging.getLogger(__name__)

# --- CONFIGURAÇÕES E CONSTANTES DE TESTE ---
CPF_FUNCIONARIO_TESTE = '77788899901'
EMAIL_FUNCIONARIO_TESTE = 'caixa.venda.test@pdv.com'
CPF_CLIENTE_TESTE = '12345678914'
ID_TIPO_PAGAMENTO_DINHEIRO = 1 # ID assumido para "Dinheiro"

# Instâncias dos DAOs
venda_dao = VendaDAO()
funcionario_dao = FuncionarioDAO()
fluxo_caixa_dao = FluxoCaixaDAO()
venda_schema = VendaSchema()

# --- UTILS PARA SETUP ---

def criar_produto_local(initial_quantity: int):
    """ Cria um produto simples e insere no estoque para o teste. """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        # 1. Inserir Produto (usando um ID alto para evitar conflito)
        codigo_produto = 400 + initial_quantity 
        cur.execute("""
            INSERT INTO produto (codigo_produto, nome, descricao, preco) 
            OVERRIDING SYSTEM VALUE
            VALUES (%s, 'Prod Teste Est', 'Descrição Est', 10.00) 
            ON CONFLICT (codigo_produto) DO UPDATE SET nome = EXCLUDED.nome 
            RETURNING codigo_produto;
        """, (codigo_produto,))
        
        # 2. Inserir/Atualizar Estoque
        cur.execute("""
            INSERT INTO estoque (codigo_produto, quantidade) 
            VALUES (%s, %s)
            ON CONFLICT (codigo_produto) DO UPDATE SET quantidade = %s;
        """, (codigo_produto, initial_quantity, initial_quantity))
        
        conn.commit()
        return codigo_produto, initial_quantity
    except Exception as e:
        logger.error(f"Erro ao criar produto local: {e}")
        conn.rollback()
        raise
    finally:
        if conn: conn.close()

def buscar_estoque_local(codigo_produto: int):
    """ Busca a quantidade atual de um produto no estoque. """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT quantidade FROM estoque WHERE codigo_produto = %s", (codigo_produto,))
        result = cur.fetchone()
        return result[0] if result else None
    finally:
        if conn: conn.close()

def garantir_caixa_aberto(cpf_funcionario):
    """ Abre o caixa se não estiver aberto para o funcionário. """
    id_aberto = fluxo_caixa_dao.buscar_caixa_aberto(cpf_funcionario)
    if id_aberto is None:
        return fluxo_caixa_dao.abrir_caixa(cpf_funcionario, Decimal('100.00'))
    return id_aberto

def realizar_venda_simulada_data(quantidade_venda: int, codigo_produto: int, preco_unitario: Decimal = Decimal('10.00')):
    """ 
    Retorna dados de venda formatados, prontos para o Schema. 
    O valor pago é configurado para cobrir o total da venda.
    """
    valor_total_venda = quantidade_venda * preco_unitario
    
    dados_venda = {
        "cpf_funcionario": CPF_FUNCIONARIO_TESTE,
        "cpf_cliente": CPF_CLIENTE_TESTE, 
        "itens": [
            {
                "codigo_produto": codigo_produto, 
                "quantidade_venda": quantidade_venda, 
                "preco_unitario": preco_unitario
            }
        ],
        "pagamentos": [
            {
                "id_tipo": ID_TIPO_PAGAMENTO_DINHEIRO, 
                "valor_pago": valor_total_venda 
            }
        ]
    }
    # O Schema faz o cálculo de total e troco na carga
    return venda_schema.load(dados_venda)

# --- FIXTURES GERAIS ---

@pytest.fixture(scope="module", autouse=True)
def setup_teardown_module():
    """ 
    SETUP: Garante que o funcionário e o tipo de pagamento existam.
    TEARDOWN: Limpa todos os dados de teste.
    """
    conn = get_db_connection()
    if conn is None:
        raise Exception("Não foi possível conectar ao DB para setup.")
    
    try:
        cur = conn.cursor()
        
        # INSERIR FUNCIONÁRIO 
        cur.execute("""
            INSERT INTO funcionario (cpf, nome, email, senha, id_tipo_funcionario) 
            VALUES (%s, 'Caixa Transacao', %s, 'hash_transacao', 1)
            ON CONFLICT (cpf) DO NOTHING;
        """, (CPF_FUNCIONARIO_TESTE, EMAIL_FUNCIONARIO_TESTE))

        # INSERIR TIPO PAGAMENTO (ID 1 = Dinheiro)
        cur.execute("""
            INSERT INTO tipo_pagamento (id_tipo, descricao) 
            OVERRIDING SYSTEM VALUE VALUES (%s, 'Dinheiro') 
            ON CONFLICT (id_tipo) DO NOTHING;
        """, (ID_TIPO_PAGAMENTO_DINHEIRO,))
        
        # GARANTE QUE O CLIENTE EXISTE (Para evitar ValueError no DAO)
        cur.execute("""
            INSERT INTO cliente (cpf_cnpj, nome, telefone) 
            VALUES (%s, 'Cliente Teste', '99999999999') 
            ON CONFLICT (cpf_cnpj) DO NOTHING;
        """, (CPF_CLIENTE_TESTE,))
        
        conn.commit()

        # Limpa o caixa de teste para garantir que o teste 01 falhe primeiro
        id_aberto = fluxo_caixa_dao.buscar_caixa_aberto(CPF_FUNCIONARIO_TESTE)
        if id_aberto:
             fluxo_caixa_dao.fechar_caixa(id_aberto, Decimal('0.00'))

    except Exception as e:
        logger.error(f"Erro no SETUP geral: {e}")
        conn.rollback()
        raise
    finally:
        if conn: conn.close()

    yield # Executa os testes

    # TEARDOWN: Limpeza
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM fluxo_caixa_movimento WHERE id_venda IN (SELECT id_venda FROM venda WHERE cpf_funcionario = %s)", (CPF_FUNCIONARIO_TESTE,))
            cur.execute("DELETE FROM venda_item WHERE id_venda IN (SELECT id_venda FROM venda WHERE cpf_funcionario = %s)", (CPF_FUNCIONARIO_TESTE,))
            cur.execute("DELETE FROM venda WHERE cpf_funcionario = %s", (CPF_FUNCIONARIO_TESTE,))
            cur.execute("DELETE FROM estoque WHERE codigo_produto > 400;")
            conn.commit()
        except Exception as e:
            logger.error(f"Erro no TEARDOWN: {e}")
            conn.rollback()
        finally:
            conn.close()

# --- TESTES DE TRANSAÇÃO (VendaDAO) ---

def test_01_venda_falha_se_caixa_nao_estiver_aberto():
    """
    Verifica se o DAO de Venda falha (com exceção) se o funcionário não tiver um caixa aberto.
    """
    # 1. SETUP: Garante que o caixa está FECHADO.
    
    # 2. CHAMA O DAO: Tenta registrar a venda
    codigo_produto_temp, _ = criar_produto_local(initial_quantity=1)
    validated_data = realizar_venda_simulada_data(quantidade_venda=1, codigo_produto=codigo_produto_temp)
    
    # Esperamos a exceção exata levantada pelo DAO
    with pytest.raises(Exception) as excinfo:
        venda_dao.registrar_venda(validated_data)

    # Verifica a mensagem de erro (confirma que o fluxo de caixa barrou a venda)
    assert "Caixa não está aberto" in str(excinfo.value)


def test_02_venda_sucesso_se_caixa_estiver_aberto():
    """
    Verifica a transação completa (Venda, Itens, Estoque, Fluxo) com sucesso.
    """
    # 1. SETUP: Abre o caixa.
    id_fluxo = garantir_caixa_aberto(CPF_FUNCIONARIO_TESTE)
    # Novo produto (Preço 10.00, Estoque 5)
    codigo_produto, estoque_inicial = criar_produto_local(initial_quantity=5) 
    
    # 2. REGISTRA A VENDA (2 unidades * R$ 10.00 = R$ 20.00)
    # A função utilitária agora garante que R$ 20.00 serão pagos.
    validated_data = realizar_venda_simulada_data(quantidade_venda=2, codigo_produto=codigo_produto) 
    id_venda = venda_dao.registrar_venda(validated_data)
    
    assert id_venda is not None
    
    # 3. VERIFICAÇÕES PÓS-TRANSAÇÃO
    
    # a. Estoque: Deve ter sido baixado (5 - 2 = 3)
    estoque_final = buscar_estoque_local(codigo_produto)
    assert estoque_final == 3
    
    # b. Fluxo de Caixa: Deve ter o movimento de ENTRADA (Valor Total: 20.00)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT valor FROM fluxo_caixa_movimento WHERE id_venda = %s AND id_fluxo = %s", (id_venda, id_fluxo))
    movimento = cur.fetchone()
    conn.close()
    
    assert movimento is not None
    assert movimento[0] == Decimal('20.00') # O valor total da venda simulada (2 * 10.00)


def test_03_venda_falha_por_estoque_insuficiente():
    """
    Verifica se a venda falha devido ao CheckViolation do DB e o ROLLBACK ocorre.
    """
    # 1. SETUP: CRIAÇÃO DO PRODUTO com estoque baixo e caixa aberto
    id_fluxo = garantir_caixa_aberto(CPF_FUNCIONARIO_TESTE)
    codigo_produto, estoque_inicial = criar_produto_local(initial_quantity=5)
    
    # 2. REGISTRA A VENDA (Tenta vender 10 de 5 -> Deve falhar no DB)
    QUANTIDADE_VENDIDA = 10
    # A função utilitária agora garante que R$ 100.00 serão pagos, passando pela validação do Schema.
    validated_data = realizar_venda_simulada_data(quantidade_venda=QUANTIDADE_VENDIDA, codigo_produto=codigo_produto) 
    
    # Espera o erro de CHECK VIOLATION do PostgreSQL (ocorre no DAO, após a validação do Schema)
    with pytest.raises(CheckViolation):
        venda_dao.registrar_venda(validated_data)
        
    # VERIFICAÇÃO: O estoque deve ter sido restaurado (Rollback)
    estoque_final = buscar_estoque_local(codigo_produto)
    assert estoque_final == estoque_inicial 


def test_03_registrar_venda_rapida_sem_cliente_sucesso():
    """
    Verifica a transação completa (Venda, Itens, Estoque, Fluxo) sem CPF/ID de cliente.
    """
    # SETUP: Abre o caixa.
    id_fluxo = garantir_caixa_aberto(CPF_FUNCIONARIO_TESTE)
    codigo_produto, estoque_inicial = criar_produto_local(initial_quantity=5)
    
    # PREPARA DADOS SEM CLIENTE (Valor total 1 * 5.00 = 5.00)
    dados_venda_base = {
        "cpf_funcionario": CPF_FUNCIONARIO_TESTE,
        "itens": [
            {"codigo_produto": codigo_produto, "quantidade_venda": 1, "preco_unitario": Decimal('5.00')}
        ],
        "pagamentos": [
            # Valor pago exatamente 5.00
            {"id_tipo": ID_TIPO_PAGAMENTO_DINHEIRO, "valor_pago": Decimal('5.00')}
        ]
    }
    # O Schema faz o cálculo de total e troco na carga
    validated_data = venda_schema.load(dados_venda_base)
    
    # REGISTRA A VENDA
    id_venda = venda_dao.registrar_venda(validated_data)
    
    assert id_venda is not None
    
    # VERIFICAÇÕES
    venda_record = venda_dao.buscar_por_id(id_venda)
    assert venda_record['id_cliente'] is None
    assert venda_record['cpf_cnpj_cliente'] is None 
    
    # Garante que o estoque foi baixado (5 - 1 = 4)
    estoque_final = buscar_estoque_local(codigo_produto)
    assert estoque_final == 4