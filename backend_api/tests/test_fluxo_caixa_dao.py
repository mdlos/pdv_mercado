import pytest
from src.models.fluxo_caixa_dao import FluxoCaixaDAO
from src.models.funcionario_dao import FuncionarioDAO
from decimal import Decimal
import secrets
import string

# Instanciação dos DAOs
fluxo_caixa_dao = FluxoCaixaDAO()
funcionario_dao = FuncionarioDAO()

# CPF FIXO para o teste (Assumindo que o Admin '00000000000' já existe)
CPF_FUNCIONARIO_TESTE = '00000000000'
SALDO_INICIAL = Decimal('100.00')

# --- Funções Auxiliares (Setup/Cleanup) ---

def obter_saldo_final_teste():
    """ Retorna um saldo final fictício. """
    return Decimal('150.50')

# Função que garante que não há caixas abertos antes do teste
def limpar_caixa_aberto():
    """ Tenta fechar qualquer caixa aberto para o CPF de teste. """
    id_aberto = fluxo_caixa_dao.buscar_caixa_aberto(CPF_FUNCIONARIO_TESTE)
    if id_aberto:
        # Usa um saldo fictício para fechar o caixa
        fluxo_caixa_dao.fechar_caixa(id_aberto, Decimal('0.00')) 

# --- Testes de Ciclo de Vida e Integridade ---

def test_01_abertura_e_fechamento_com_sucesso():
    """ Testa o ciclo completo de ABRIR -> FECHAR o caixa. """
    
    # SETUP: Garante que não há caixas abertos antes de começar
    limpar_caixa_aberto()

    # 1. POST (ABRIR CAIXA)
    id_abertura = fluxo_caixa_dao.abrir_caixa(CPF_FUNCIONARIO_TESTE, SALDO_INICIAL)
    
    assert id_abertura is not None
    
    # 2. VERIFICAÇÃO INTERMEDIÁRIA: Confirma o status ABERTO
    caixa_aberto = fluxo_caixa_dao.buscar_por_id(id_abertura)
    assert caixa_aberto['status'] == 'ABERTO'
    assert caixa_aberto['saldo_inicial'] == SALDO_INICIAL
    
    # 3. PUT (FECHAR CAIXA)
    saldo_final = obter_saldo_final_teste()
    rows_affected = fluxo_caixa_dao.fechar_caixa(id_abertura, saldo_final)
    
    assert rows_affected == 1 # Deve afetar exatamente 1 linha
    
    # 4. VERIFICAÇÃO FINAL: Confirma o status FECHADO e o saldo final
    caixa_fechado = fluxo_caixa_dao.buscar_por_id(id_abertura)
    assert caixa_fechado['status'] == 'FECHADO'
    assert caixa_fechado['saldo_final_informado'] == saldo_final


def test_02_tentar_abrir_caixa_duplicado_deve_falhar():
    """ Testa a regra de negócio: Não pode haver dois caixas abertos para o mesmo funcionário. """
    
    # SETUP: Garante que há um caixa ABERTO
    limpar_caixa_aberto()
    id_abertura_original = fluxo_caixa_dao.abrir_caixa(CPF_FUNCIONARIO_TESTE, SALDO_INICIAL)
    
    # 1. Tenta ABRIR NOVAMENTE (Deve retornar None no DAO)
    id_segunda_tentativa = fluxo_caixa_dao.abrir_caixa(CPF_FUNCIONARIO_TESTE, SALDO_INICIAL)
    
    # 2. Assertiva: A segunda tentativa deve falhar
    assert id_segunda_tentativa is None
    
    # --- Limpeza ---
    limpar_caixa_aberto() # Fecha o caixa original


def test_03_fechar_caixa_que_nao_esta_aberto_deve_falhar():
    """ Testa se fechar o mesmo caixa duas vezes retorna 0 linhas afetadas. """
    
    # SETUP: Abre e imediatamente fecha o caixa
    limpar_caixa_aberto()
    id_abertura = fluxo_caixa_dao.abrir_caixa(CPF_FUNCIONARIO_TESTE, SALDO_INICIAL)
    saldo_final = obter_saldo_final_teste()
    fluxo_caixa_dao.fechar_caixa(id_abertura, saldo_final) # Primeiro fechamento (sucesso)

    # 1. Tenta FECHAR NOVAMENTE (UPDATE)
    rows_affected = fluxo_caixa_dao.fechar_caixa(id_abertura, saldo_final)
    
    # 2. Assertiva: Deve retornar 0, pois a cláusula WHERE status='ABERTO' falha.
    assert rows_affected == 0


def test_04_buscar_caixa_aberto_retorna_o_id():
    """ Testa se a função buscar_caixa_aberto retorna o ID correto do turno ativo. """
    
    # SETUP: Garante que há um caixa ABERTO
    limpar_caixa_aberto()
    id_abertura_esperado = fluxo_caixa_dao.abrir_caixa(CPF_FUNCIONARIO_TESTE, SALDO_INICIAL)
    
    # 1. BUSCA
    id_retornado = fluxo_caixa_dao.buscar_caixa_aberto(CPF_FUNCIONARIO_TESTE)
    
    # 2. Assertiva
    assert id_retornado == id_abertura_esperado
    
    # --- Limpeza ---
    limpar_caixa_aberto()