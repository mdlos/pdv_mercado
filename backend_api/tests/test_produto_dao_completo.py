# tests/test_produto_dao_completo.py

import pytest
from decimal import Decimal
import secrets
import string
from psycopg import IntegrityError # Necessário para capturar a exceção de estoque negativo
from src.models.produto_dao import ProdutoDAO
from src.models.estoque_dao import EstoqueDAO
from src.db_connection import get_db_connection

# Instanciação dos DAOs
produto_dao = ProdutoDAO()
estoque_dao = EstoqueDAO() 

# =========================================================================
# DADOS DE REFERÊNCIA ESTÁTICOS PARA TESTES FUTUROS (ID Fixo Garantido)
# =========================================================================

# Variável global para armazenar os IDs dos produtos fixos
PRODUTOS_IDS_FIXOS = {} 

LISTA_PRODUTOS_ESTATICOS = [
    {
        "nome": "ARROZ Teste Fixo", 
        "descricao": "Arroz 1kg para Teste de Compra/Venda",
        "preco": "5.00", 
        "codigo_barras": "1000000000001", # Código de Barras ÚNICO e fixo
        "initial_quantity": 100
    },
    {
        "nome": "FEIJAO Teste Fixo", 
        "descricao": "Feijão 1kg para Teste de Baixa",
        "preco": "8.00", 
        "codigo_barras": "1000000000002",
        "initial_quantity": 200
    },
    {
        "nome": "OLEO Teste Fixo", 
        "descricao": "Óleo de Soja 900ml",
        "preco": "12.00", 
        "codigo_barras": "1000000000003",
        "initial_quantity": 50
    },
]

# --- FIXTURE DE SETUP ESTÁTICO ---

@pytest.fixture(scope="session", autouse=True)
def setup_produtos_estaticos():
    """ 
    Cria os 3 produtos fixos se não existirem no banco. 
    Usaremos o Código de Barras (UNIQUE) para verificar a existência.
    """
    global PRODUTOS_IDS_FIXOS
    
    print("\n--- Configurando Produtos Estáticos Finais ---")

    for index, dados in enumerate(LISTA_PRODUTOS_ESTATICOS):
        # Tenta buscar pelo Código de Barras para evitar duplicação
        produto_existente = produto_dao.find_by_codigo_barras(dados['codigo_barras']) # Assumindo que este método existe
        
        if produto_existente:
            id_existente = produto_existente['codigo_produto']
            PRODUTOS_IDS_FIXOS[index + 1] = id_existente
        else:
            try:
                id_inserido = produto_dao.insert(
                    dados['nome'], dados['descricao'], dados['preco'], 
                    dados['codigo_barras'], dados['initial_quantity']
                )
                PRODUTOS_IDS_FIXOS[index + 1] = id_inserido
            except Exception as e:
                print(f"ERRO CRÍTICO no setup de produto estático: {e}")
                
    yield # Executa os testes

    # --- CLEANUP APÓS OS TESTES (OPCIONAL: PODE SER REMOVIDO SE OS DADOS FOREM PERMANENTES) ---
    # Nota: Não limpamos aqui para manter os dados para outros módulos (Compra, Venda).
    # Se precisar de um banco limpo, rode o script de deleção antes de cada sessão de teste.


# --- Funções Auxiliares de CONFIGURAÇÃO e LIMPEZA (MANTIDAS) ---
# ... (manter as funções obter_dados_teste, configurar_teste_produto, limpar_produto_inserido, check_estoque_exists) ...

def gerar_codigo_aleatorio(length=13):
    """ Gera um código de produto/barras aleatório (13 dígitos). """
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def obter_dados_teste():
    """ Retorna um dicionário com dados válidos e únicos para a inserção (DINÂMICA). """
    return {
        "nome": f"Produto Teste {secrets.token_hex(4)}",
        "descricao": "Descrição para o teste de CRUD completo.",
        "preco": "15.50", 
        "codigo_barras": gerar_codigo_aleatorio(),
        "initial_quantity": 50 
    }

def configurar_teste_produto(dados):
    """ Insere um produto DINÂMICO e inicializa seu estoque, retorna o codigo_produto. """
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

def check_estoque_exists(codigo_produto: int) -> bool:
    """ Verifica se um registro de estoque existe. (Para o Veraliche) """
    conn = get_db_connection()
    if conn is None: return False
    try:
        with conn.cursor() as cur:
            sql = "SELECT codigo_produto FROM estoque WHERE codigo_produto = %s;"
            cur.execute(sql, (codigo_produto,))
            return cur.fetchone() is not None
    finally:
        if conn: conn.close()

# =========================================================================
# TESTES DE INTEGRAÇÃO CRUD (MODIFICADOS/RENUMERADOS)
# =========================================================================

def test_01_verificar_produtos_estaticos_foram_criados():
    """ Testa se os produtos fixos existem e são lidos corretamente. """
    assert len(PRODUTOS_IDS_FIXOS) == 3
    
    # Verifica o produto ARROZ (ID 1 do array)
    codigo_arroz = PRODUTOS_IDS_FIXOS[1]
    produto_db = produto_dao.find_by_id(codigo_arroz)
    assert produto_db is not None
    assert produto_db['nome'] == "ARROZ Teste Fixo"


def test_02_baixa_e_reposicao_de_estoque_com_sucesso_em_produto_fixo():
    """ 
    Testa a alteração de estoque usando o produto ARROZ (ID fixo 1).
    Garante que a quantidade volte ao estado inicial (100).
    """
    codigo_teste = PRODUTOS_IDS_FIXOS[1]
    ESTOQUE_INICIAL = 100 # Conforme o setup estático
    
    # 1. BAIXA DE ESTOQUE (Venda): Reduz 10 unidades (100 -> 90)
    rows_affected_baixa = estoque_dao.update_quantity(codigo_teste, ESTOQUE_INICIAL - 10)
    
    # 2. REPOSIÇÃO DE ESTOQUE (Compra): Aumenta 25 unidades (90 -> 115)
    rows_affected_reposicao = estoque_dao.update_quantity(codigo_teste, 90 + 25) 
    
    produto_pos_reposicao = produto_dao.find_by_id(codigo_teste)
    assert rows_affected_baixa == 1
    assert rows_affected_reposicao == 1
    assert produto_pos_reposicao['quantidade'] == 115
    
    # --- Limpeza Específica: REVERTER O ESTOQUE AO ESTADO INICIAL ---
    estoque_dao.update_quantity(codigo_teste, ESTOQUE_INICIAL)
    assert produto_dao.find_by_id(codigo_teste)['quantidade'] == ESTOQUE_INICIAL


def test_03_cadastro_de_produto_dinamico_com_estoque_inicial():
    """ Testa a transação atômica de CREATE (Produto + Estoque inicial) - DINÂMICO. """
    dados = obter_dados_teste()
    
    codigo_inserido = configurar_teste_produto(dados)
    
    assert codigo_inserido is not None
    
    produto_db = produto_dao.find_by_id(codigo_inserido) 
    assert produto_db['quantidade'] == dados['initial_quantity']
    
    # --- Limpeza ---
    limpar_produto_inserido(codigo_inserido)


def test_04_atualizacao_de_detalhes_do_produto_dinamico():
    """ Testa a funcionalidade de atualizar apenas dados não relacionados ao estoque (nome, preço) - DINÂMICO. """
    dados = obter_dados_teste()
    codigo_teste = configurar_teste_produto(dados)
    
    novo_nome = "Pão de Manteiga"
    
    rows_affected = produto_dao.update(codigo_teste, nome=novo_nome)
    
    produto_atualizado = produto_dao.find_by_id(codigo_teste) 
    
    assert rows_affected == 1
    assert produto_atualizado['nome'] == novo_nome
    assert produto_atualizado['quantidade'] == dados['initial_quantity']
    
    # --- Limpeza ---
    limpar_produto_inserido(codigo_teste)


def test_05_barreira_de_estoque_negativo_deve_falhar_em_produto_fixo():
    """ 
    Testa a principal regra de negócio: barrar estoque negativo usando o produto ÓLEO (ID fixo 3).
    """
    codigo_teste = PRODUTOS_IDS_FIXOS[3]
    ESTOQUE_INICIAL = 50 # Conforme o setup estático
    
    try:
        # 1. DIZ AO PYTEST PARA ESPERAR A EXCEÇÃO DE INTEGRIDADE DO BANCO DE DADOS
        with pytest.raises(IntegrityError): 
            # Tentativa de definir a quantidade final para um valor negativo
            estoque_dao.update_quantity(codigo_teste, -5) 
        
        # 2. VERIFICAÇÃO DE INTEGRIDADE: O estoque DEVE PERMANECER O MESMO
        produto_final = produto_dao.find_by_id(codigo_teste)
        assert produto_final['quantidade'] == ESTOQUE_INICIAL # Estoque deve permanecer 50
        
    finally:
        # 3. GARANTIA DE INTEGRIDADE: Reverte o estoque caso algo tenha o alterado (por segurança, mas deve ser 50)
        estoque_dao.update_quantity(codigo_teste, ESTOQUE_INICIAL)


def test_06_exclusao_de_produto_e_estoque_em_cascata_dinamico():
    """ Testa a exclusão em cascata (VERALICHE) para um produto DINÂMICO. """
    dados = obter_dados_teste()
    codigo_para_excluir = configurar_teste_produto(dados)
    
    try:
        assert check_estoque_exists(codigo_para_excluir) is True

        rows_affected = produto_dao.delete(codigo_para_excluir)
        
        assert rows_affected == 1
        assert produto_dao.find_by_id(codigo_para_excluir) is None
        
        assert check_estoque_exists(codigo_para_excluir) is False, "Falha no VERALICHE: Registro de estoque órfão encontrado após delete do produto."

    finally:
        # GARANTIA DE LIMPEZA
        limpar_produto_inserido(codigo_para_excluir)