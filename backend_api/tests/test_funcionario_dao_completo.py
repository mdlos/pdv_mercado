# tests/test_funcionario_dao_completo.py

import pytest
from decimal import Decimal
import secrets
import string
from src.models.cliente_dao import ClienteDAO
from src.models.funcionario_dao import FuncionarioDAO
from src.models.produto_dao import ProdutoDAO
from src.db_connection import get_db_connection # Necessário para check_localizacao
from src.schemas.funcionario_schema import FuncionarioSchema
from app import create_app, bcrypt # Necessário para hashing
from src.models.estoque_dao import EstoqueDAO # Necessário para o VendaDAO

# Instanciação dos DAOs e Schemas (Disponível para uso nos helpers)
cliente_dao = ClienteDAO()
funcionario_dao = FuncionarioDAO()
funcionario_schema = FuncionarioSchema()

# --- Constantes e Helpers de Setup ---

CPF_FUNCIONARIO_BASE = "22222222222" # CPF Fixo para o setup do teste
ID_CARGO_ADMIN = 1 
ID_CARGO_CAIXA = 2 # Assumimos que o ID 2 é 'Caixa'

def gerar_cpf_aleatorio():
    """ Gera um CPF aleatório (11 dígitos). """
    return ''.join(secrets.choice(string.digits) for _ in range(11))

def check_localizacao_exists(localizacao_id: int) -> bool:
    """ 
    Verifica se uma localização (endereço) existe diretamente no banco.
    Usado no VERALICHE.
    """
    if localizacao_id is None:
        return False
        
    conn = get_db_connection()
    if conn is None: 
        return False 

    try:
        with conn.cursor() as cur:
            sql = "SELECT id_localizacao FROM localizacao WHERE id_localizacao = %s;"
            cur.execute(sql, (localizacao_id,))
            result = cur.fetchone()
            return result is not None
    finally:
        if conn: conn.close()


@pytest.fixture(scope="session", autouse=True)
def configurar_setup_inicial():
    """ Fixture que garante que o Operador Base e o Cargo Admin existam na sessão de teste. """
    try:
        # 1. FUNCIONÁRIO BASE (Cria um funcionário para ser a FK em Venda)
        senha_hashed = bcrypt.generate_password_hash(b'12345678').decode('utf-8')
        funcionario_dao.insert(
            cpf=CPF_FUNCIONARIO_BASE, nome="Operador Base", sobrenome="Teste", 
            senha_hashed=senha_hashed, id_tipo_funcionario=ID_CARGO_ADMIN, 
            email="operador_base@teste.com", sexo='M', telefone=None, nome_social=None, localizacao_data=None
        )
    except Exception as e:
        pass
    yield


# ----------------------------------------------------------------------------------
# TESTES DE CRUD BÁSICO E INTEGRIDADE
# ----------------------------------------------------------------------------------

def test_01_cadastro_de_funcionario_com_sucesso():
    """ Testa se o DAO consegue cadastrar um novo funcionário e se a senha está hashed. """
    cpf_novo = gerar_cpf_aleatorio()
    senha_pura = "senhateste123"
    
    try:
        senha_hashed = bcrypt.generate_password_hash(senha_pura).decode('utf-8')
        
        cpf_inserido = funcionario_dao.insert(
            cpf=cpf_novo,
            nome="Novo Funcionario",
            sobrenome="Da Silva",
            senha_hashed=senha_hashed,
            id_tipo_funcionario=ID_CARGO_ADMIN,
            email=f"novo_{cpf_novo}@teste.com",
            sexo='F',
            telefone=None,
            nome_social=None,
            localizacao_data=None
        )
        
        assert cpf_inserido == cpf_novo
        funcionario_db = funcionario_dao.find_by_cpf(cpf_inserido)
        assert bcrypt.check_password_hash(funcionario_db['senha'], senha_pura) is True

    finally:
        funcionario_dao.delete(cpf_novo)


def test_02_atualizacao_de_funcionario_com_sucesso():
    """ Testa a funcionalidade de atualizar os dados de um funcionário. """
    cpf_para_atualizar = gerar_cpf_aleatorio()
    senha_inicial = bcrypt.generate_password_hash(b'senha_antiga').decode('utf-8')
    try:
        funcionario_dao.insert(
            cpf=cpf_para_atualizar,
            nome="Nome Antigo",
            sobrenome="Sobrenome Antigo",
            senha_hashed=senha_inicial,
            id_tipo_funcionario=ID_CARGO_ADMIN,
            email=f"antigo_{cpf_para_atualizar}@teste.com",
            sexo='M',
            telefone='11999999999',
            localizacao_data={'cep': '00000000', 'cidade': 'Cidade Antiga'}
        )
        
        novos_dados = {
            "nome": "Nome Novo",
            "sobrenome": "Sobrenome Novo",
            "email": f"novo_{cpf_para_atualizar}@teste.com",
        }
        
        rows_affected = funcionario_dao.update(cpf_para_atualizar, **novos_dados)
        
        funcionario_atualizado = funcionario_dao.find_by_cpf(cpf_para_atualizar)
        assert rows_affected == 1
        assert funcionario_atualizado['nome'] == "Nome Novo"
        assert funcionario_atualizado['sobrenome'] == "Sobrenome Novo"
        assert bcrypt.check_password_hash(funcionario_atualizado['senha'], 'senha_antiga') is True

    finally:
        funcionario_dao.delete(cpf_para_atualizar)       
        
def test_03_busca_e_listagem_de_funcionarios():
    """ Testa a funcionalidade de buscar um funcionário por CPF e listar todos. """
    cpf_teste_busca = gerar_cpf_aleatorio()
    senha_hash = bcrypt.generate_password_hash(b'get_test').decode('utf-8')
    
    try:
        funcionario_dao.insert(
            cpf=cpf_teste_busca,
            nome="Funcionario Busca",
            sobrenome="Teste",
            senha_hashed=senha_hash,
            id_tipo_funcionario=ID_CARGO_ADMIN,
            email=f"busca_{cpf_teste_busca}@teste.com",
            sexo='O',
            telefone=None,
            localizacao_data=None
        )
        
        # 1. BUSCA POR CPF
        funcionario_buscado = funcionario_dao.find_by_cpf(cpf_teste_busca)
        assert funcionario_buscado is not None
        
        # 2. LISTAGEM
        todos_funcionarios = funcionario_dao.find_all()
        assert len(todos_funcionarios) >= 2 
        
    finally:
        funcionario_dao.delete(cpf_teste_busca) 
        
        
def test_04_exclusao_de_funcionario_com_sucesso():
    """ Testa a exclusão de um funcionário e a garantia de que ele não está mais no DB. """
    cpf_para_excluir = gerar_cpf_aleatorio()
    senha_hash = bcrypt.generate_password_hash(b'delete_test').decode('utf-8')
    
    try:
        cpf_inserido = funcionario_dao.insert(
            cpf=cpf_para_excluir,
            nome="Funcionario Exclusao",
            sobrenome="Teste",
            senha_hashed=senha_hash,
            id_tipo_funcionario=ID_CARGO_ADMIN,
            email=f"exclusao_{cpf_para_excluir}@teste.com",
            sexo='M',
            telefone=None,
            localizacao_data=None
        )
        
        rows_affected = funcionario_dao.delete(cpf_para_excluir)
        
        # VERIFICAÇÃO: O resultado deve ser None (não encontrado)
        funcionario_excluido = funcionario_dao.find_by_cpf(cpf_para_excluir)
        assert rows_affected == 1
        assert funcionario_excluido is None
        
    finally:
        try:
            funcionario_dao.delete(cpf_para_excluir)
        except:
            pass
        
    
def test_05_exclusao_de_funcionario_e_localizacao():
    """ Testa a exclusão em cascata: ao deletar o funcionário, a sua localização 
    associada deve ser automaticamente deletada para evitar dados órfãos. (VERALICHE)
    """
    cpf_para_excluir = gerar_cpf_aleatorio()
    senha_hash = bcrypt.generate_password_hash(b'delete_loc_test').decode('utf-8')
    
    localizacao_data = {
        'cep': '99999999',
        'cidade': 'Cidade Exclusao Teste',
        'uf': 'XX',
        'logradouro': 'Rua de Teste'
    }
    
    id_loc_inserida = None
    try:
        # 1. SETUP: Insere o funcionário COM localização
        funcionario_dao.insert(
            cpf=cpf_para_excluir,
            nome="Funcionario com Loc",
            sobrenome="Delete Test",
            senha_hashed=senha_hash,
            id_tipo_funcionario=ID_CARGO_ADMIN,
            email=f"loc_delete_{cpf_para_excluir}@teste.com",
            sexo='F',
            telefone=None,
            localizacao_data=localizacao_data
        )
        
        # 2. RECUPERA ID DA LOCALIZAÇÃO
        funcionario_inserido = funcionario_dao.find_by_cpf(cpf_para_excluir)
        id_loc_inserida = funcionario_inserido['id_localizacao']
        
        # 3. VERIFICA PRÉ-EXCLUSÃO
        assert check_localizacao_exists(id_loc_inserida) is True, "A localização não existe antes do delete."

        # 4. CHAMA O DAO PARA EXCLUIR O FUNCIONÁRIO
        funcionario_dao.delete(cpf_para_excluir)
        
        # 5. ASSERÇÃO 2 (VERALICHE): Verifica se a localização TAMBÉM foi excluída
        assert check_localizacao_exists(id_loc_inserida) is False, "Falha no VERALICHE: Localização órfã encontrada após delete do funcionário."

    finally:
        try:
            funcionario_dao.delete(cpf_para_excluir)
        except:
            pass


def test_06_promocao_e_rebaixamento_de_cargo():
    """ 
    Testa a atualização do campo id_tipo_funcionario (troca de cargo),
    simulando uma promoção de Admin/Gerente para Caixa e vice-versa.
    """
    cpf_para_troca = gerar_cpf_aleatorio()
    senha_hash = bcrypt.generate_password_hash(b'troca_cargo').decode('utf-8')
    
    # Assumindo que ID 1 é Admin e ID 2 é Caixa
    ID_GERENTE = 1 
    ID_CAIXA = 2   

    try:
        # 1. SETUP: Insere o funcionário como Gerente/Admin (ID_GERENTE)
        funcionario_dao.insert(
            cpf=cpf_para_troca,
            nome="Troca Cargo",
            sobrenome="Teste",
            senha_hashed=senha_hash,
            id_tipo_funcionario=ID_GERENTE, # Começa como GERENTE
            email=f"troca_{cpf_para_troca}@teste.com",
            sexo='M',
            telefone=None,
            localizacao_data=None
        )
        
        # --- 2. REBAIXAMENTO: Gerente (1) -> Caixa (2) ---
        
        rows_affected_rebaixamento = funcionario_dao.update(
            cpf_para_troca,
            id_tipo_funcionario=ID_CAIXA # Altera para Caixa
        )

        assert rows_affected_rebaixamento == 1
        funcionario_db_rebaixado = funcionario_dao.find_by_cpf(cpf_para_troca)
        assert funcionario_db_rebaixado['id_tipo_funcionario'] == ID_CAIXA
        
        # --- 3. PROMOÇÃO: Caixa (2) -> Gerente (1) ---
        
        rows_affected_promocao = funcionario_dao.update(
            cpf_para_troca,
            id_tipo_funcionario=ID_GERENTE # Altera de volta para Gerente
        )
        
        assert rows_affected_promocao == 1
        funcionario_db_promovido = funcionario_dao.find_by_cpf(cpf_para_troca)
        assert funcionario_db_promovido['id_tipo_funcionario'] == ID_GERENTE

    finally:
        # 4. LIMPEZA
        try:
            funcionario_dao.delete(cpf_para_troca)
        except:
            pass