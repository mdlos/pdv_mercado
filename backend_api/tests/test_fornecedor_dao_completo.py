# tests/test_fornecedor_dao_completo.py (VERSÃO COM SETUP ESTÁTICO)

import pytest
from src.models.fornecedor_dao import FornecedorDAO
from src.db_connection import get_db_connection
import random
import string
import secrets
from datetime import date

# Instanciação dos DAOs
fornecedor_dao = FornecedorDAO()

# =========================================================================
# DADOS DE REFERÊNCIA ESTÁTICOS PARA TESTES FUTUROS (ID FIXO GARANTIDO)
# =========================================================================

# NOTA: Estes IDs (1, 2, 3) serão criados e persistirão no banco para outros testes.
LISTA_FORNECEDORES_ESTATICOS = [
    {
        "cnpj": "11111111000101",
        "razao_social": "GIGA Atacado de Alimentos",
        "email": "giga@atacado.com.br",
        "celular": "987654321",
        "localizacao_data": {"cep": "11111000", "cidade": "SP", "uf": "SP"}
    },
    {
        "cnpj": "22222222000202",
        "razao_social": "TEC Distribuidora de Eletrônicos",
        "email": "tec@distrib.com",
        "celular": "912345678",
        "localizacao_data": {"cep": "22222000", "cidade": "RJ", "uf": "RJ"}
    },
    {
        "cnpj": "33333333000303",
        "razao_social": "FARMA Produtos de Limpeza",
        "email": "farma@limpeza.com",
        "celular": "900001111",
        "localizacao_data": {"cep": "33333000", "cidade": "BH", "uf": "MG"}
    },
]

# Variável global para armazenar os IDs fixos
FORNECEDORES_IDS = {}

# --- Fixture de Setup e Cleanup ---

@pytest.fixture(scope="session", autouse=True)
def setup_fornecedores_estaticos():
    """ 
    Garante que os fornecedores de teste estejam no banco de dados.
    Esta função é executada apenas uma vez por sessão de teste.
    """
    print("\n--- Configurando Fornecedores Estáticos ---")
    global FORNECEDORES_IDS
    
    for i, dados in enumerate(LISTA_FORNECEDORES_ESTATICOS):
        # Tenta buscar pelo CNPJ para evitar duplicação em sessões diferentes
        fornecedor_existente = fornecedor_dao.find_by_cnpj(dados['cnpj'])
        
        if fornecedor_existente:
            FORNECEDORES_IDS[i + 1] = fornecedor_existente['id_fornecedor']
            print(f"Fornecedor {dados['razao_social']} já existe (ID: {fornecedor_existente['id_fornecedor']}).")
        else:
            # Caso não exista, insere um novo fornecedor
            try:
                id_inserido = fornecedor_dao.insert(
                    cnpj=dados['cnpj'],
                    razao_social=dados['razao_social'],
                    email=dados['email'],
                    celular=dados['celular'],
                    localizacao_data=dados['localizacao_data']
                )
                FORNECEDORES_IDS[i + 1] = id_inserido
                print(f"Fornecedor {dados['razao_social']} inserido com ID: {id_inserido}")
            except Exception as e:
                print(f"Erro ao inserir fornecedor estático {dados['razao_social']}: {e}")
                
    # Não fazemos limpeza (yield) aqui, pois os dados são necessários para testes futuros.
    # O desenvolvedor deve limpar o banco manualmente ou via setup inicial se necessário.
    print("--- Setup de Fornecedores Concluído ---")
    

# --- Funções Auxiliares (mantidas e ajustadas) ---

def gerar_cnpj_aleatorio():
    # ... (mantido o código de geração de CNPJ) ...
    return ''.join(secrets.choice(string.digits) for _ in range(14))

def obter_dados_teste():
    """ Retorna dados válidos e únicos para testes DINÂMICOS. """
    # ... (mantido o código de dados dinâmicos) ...
    cnpj_aleatorio = gerar_cnpj_aleatorio()
    return {
        "cnpj": cnpj_aleatorio,
        "razao_social": f"Fornecedor Teste DINÂMICO {secrets.token_hex(4)}",
        "email": f"teste_{cnpj_aleatorio}@dinamico.com",
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

def setup_test_fornecedor(data):
    """ Insere um fornecedor DINÂMICO e retorna o ID. """
    id_inserido = fornecedor_dao.insert(
        cnpj=data['cnpj'],
        razao_social=data['razao_social'],
        email=data['email'],
        celular=data.get('celular'),
        data_abertura=data.get('data_abertura'),
        localizacao_data=data['localizacao_data']
    )
    return id_inserido

def limpar_fornecedor_inserido(id_fornecedor):
    """ Tenta deletar o fornecedor DINÂMICO. """
    fornecedor_dao.delete(id_fornecedor) 

def check_localizacao_exists(localizacao_id: int) -> bool:
    """ Verifica se uma localização existe. """
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
# TESTES DE INTEGRAÇÃO (USANDO DADOS DINÂMICOS E ESTÁTICOS)
# =========================================================================

def test_01_verificar_fornecedores_estaticos():
    """ Verifica se os IDs estáticos foram criados e podem ser lidos. """
    assert len(FORNECEDORES_IDS) == 3
    
    # Exemplo de leitura de um fornecedor estático
    id_giga = FORNECEDORES_IDS[1]
    fornecedor_db = fornecedor_dao.find_by_id(id_giga)
    
    assert fornecedor_db is not None
    assert fornecedor_db['razao_social'] == "GIGA Atacado de Alimentos"
    assert fornecedor_db['cnpj'] == "11111111000101"

# --- Testes CRUD originais (usando dados DINÂMICOS) ---

def test_02_inserir_e_ler_fornecedor_dinamico_com_sucesso():
    # ... (mantido o corpo do teste original 01, agora 02) ...
    dados = obter_dados_teste()
    id_inserido = setup_test_fornecedor(dados)
    
    assert id_inserido is not None
    
    fornecedor_db = fornecedor_dao.find_by_id(id_inserido)
    
    assert fornecedor_db is not None
    assert fornecedor_db['razao_social'] == dados['razao_social']

    limpar_fornecedor_inserido(id_inserido)


def test_03_atualizacao_de_dados_e_localizacao_dinamica():
    # ... (mantido o corpo do teste original 02, agora 03) ...
    dados = obter_dados_teste()
    id_inserido = setup_test_fornecedor(dados)
    
    novo_nome = "Nova Razao Atualizada"
    novo_cep = "99999999"
    
    rows_affected = fornecedor_dao.update(
        id_fornecedor=id_inserido,
        razao_social=novo_nome,
        localizacao_data={'cep': novo_cep}
    )
    
    assert rows_affected == 1
    
    fornecedor_atualizado = fornecedor_dao.find_by_id(id_inserido)
    assert fornecedor_atualizado['razao_social'] == novo_nome
    assert fornecedor_atualizado['cep'] == novo_cep

    limpar_fornecedor_inserido(id_inserido)


def test_04_inserir_cnpj_duplicado_deve_falhar():
    # ... (mantido o corpo do teste original 03, agora 04) ...
    dados = obter_dados_teste()
    id_original = setup_test_fornecedor(dados)
    
    id_inserido_fail = fornecedor_dao.insert(
        cnpj=dados['cnpj'],
        razao_social="Duplicado",
        email="duplicado@teste.com",
    )
    
    assert id_inserido_fail is None
    
    limpar_fornecedor_inserido(id_original)


def test_05_exclusao_atomica_e_limpeza_de_localizacao_dinamica():
    # ... (mantido o corpo do teste original 04, agora 05) ...
    dados = obter_dados_teste()
    id_inserido = setup_test_fornecedor(dados)
    
    fornecedor_db = fornecedor_dao.find_by_id(id_inserido)
    id_loc_inserida = fornecedor_db['id_localizacao']
    
    assert check_localizacao_exists(id_loc_inserida) is True

    rows_affected = fornecedor_dao.delete(id_inserido)
    
    assert rows_affected == 1
    
    assert check_localizacao_exists(id_loc_inserida) is False, "Falha no VERALICHE: Localização órfã encontrada após delete do fornecedor."