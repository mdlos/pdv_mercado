# src/controllers/funcionario_controller.py 

from flask import Blueprint, request, jsonify
from src.schemas.funcionario_schema import FuncionarioSchema
from src.models.funcionario_dao import FuncionarioDAO
from src.utils.formatters import clean_only_numbers
from http import HTTPStatus
import logging
from app import bcrypt 


logger = logging.getLogger(__name__)

# Inicializa o Blueprint
funcionario_bp = Blueprint('funcionario', __name__, url_prefix='/api/v1/funcionarios')
# Instancia o DAO e os Schemas
funcionario_dao = FuncionarioDAO()
funcionario_schema = FuncionarioSchema() 
funcionarios_schema = FuncionarioSchema(many=True)

# -----------------------------------------------------------
# C - CREATE (Criação de Novo Funcionário) - RESOLVE A SENHA
# -----------------------------------------------------------
@funcionario_bp.route('/', methods=['POST'], strict_slashes=False)
def create_funcionario():
    """ Rota para criar um novo funcionário. """
    data = request.get_json()
    
    # 1. Validação dos dados
    try:
        funcionario_data = funcionario_schema.load(data)
    except Exception as e:
        error_details = getattr(e, 'messages', str(e))
        logger.error(f"Erro de validação ao criar funcionário: {error_details}")
        return jsonify({"message": "Erro de validação", "errors": error_details}), HTTPStatus.BAD_REQUEST

    # 2. Segurança: Hash da Senha
    # 🛑 CORREÇÃO CRÍTICA: Pegamos a senha do campo 'senha' (que o usuário enviou)
    senha_pura = funcionario_data.pop('senha') 
    senha_hashed = bcrypt.generate_password_hash(senha_pura).decode('utf-8')

    # 3. Processa a Localização (se presente)
    localizacao_data = funcionario_data.pop('localizacao', None)
    
    # 4. Inserção no Banco de Dados
    try:
        cpf_limpo = clean_only_numbers(funcionario_data['cpf'])
        
        # O DAO recebe o nome 'senha_hashed'
        cpf_inserido = funcionario_dao.insert(
            cpf=cpf_limpo,
            nome=funcionario_data['nome'],
            sobrenome=funcionario_data['sobrenome'],
            senha_hashed=senha_hashed, 
            id_tipo_funcionario=funcionario_data['id_tipo_funcionario'],
            email=funcionario_data.get('email'),
            sexo=funcionario_data.get('sexo'),
            telefone=funcionario_data.get('telefone'),
            nome_social=funcionario_data.get('nome_social'),
            localizacao_data=localizacao_data
        )
        
        if cpf_inserido:
            novo_funcionario_data = funcionario_dao.find_by_cpf(cpf_inserido)
            return funcionario_schema.dump(novo_funcionario_data), HTTPStatus.CREATED
        else:
            return jsonify({"message": "Não foi possível inserir o funcionário (pode ser CPF duplicado ou erro de FK)."}), HTTPStatus.INTERNAL_SERVER_ERROR

    except ValueError as ve:
        return jsonify({"message": str(ve)}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        logger.error(f"Erro inesperado ao criar funcionário: {e}")
        return jsonify({"message": f"Erro interno no servidor: {e}"}), HTTPStatus.INTERNAL_SERVER_ERROR

# -----------------------------------------------------------
# R - READ ALL (Busca Todos)
# -----------------------------------------------------------
@funcionario_bp.route('/', methods=['GET'], strict_slashes=False)
def listar_todos_funcionarios():
    """ Rota para buscar e retornar todos os funcionários cadastrados. """
    
    funcionarios_data = funcionario_dao.find_all() 
    
    if funcionarios_data:
        return funcionarios_schema.dump(funcionarios_data), HTTPStatus.OK
    else:
        return jsonify([]), HTTPStatus.OK

# -----------------------------------------------------------
# R - READ (Busca por CPF)
# -----------------------------------------------------------
@funcionario_bp.route('/<string:cpf>', methods=['GET']) 
def get_funcionario(cpf):
    """ Rota para buscar um funcionário pelo CPF. """
    
    cpf_limpo = clean_only_numbers(cpf) 
    
    funcionario_data = funcionario_dao.find_by_cpf(cpf_limpo) 
    
    if funcionario_data:
        return funcionario_schema.dump(funcionario_data), HTTPStatus.OK
    else:
        return jsonify({"message": f"Funcionário com CPF {cpf} não encontrado."}), HTTPStatus.NOT_FOUND

# -----------------------------------------------------------
# D - DELETE (Exclusão por CPF)
# -----------------------------------------------------------
@funcionario_bp.route('/<string:cpf>', methods=['DELETE'])
def delete_funcionario(cpf):
    """ Rota para deletar um funcionário e sua localização associada. """
    cpf_limpo = clean_only_numbers(cpf)
    
    rows_affected = funcionario_dao.delete(cpf_limpo)
    
    if rows_affected > 0:
        return '', HTTPStatus.NO_CONTENT 
    else:
        return jsonify({"message": f"Funcionário com CPF {cpf} não encontrado ou erro na exclusão."}), HTTPStatus.NOT_FOUND

## -----------------------------------------------------------
# U - UPDATE (Atualização de Funcionário)
# -----------------------------------------------------------
@funcionario_bp.route('/<string:cpf>', methods=['PUT'])
def update_funcionario(cpf):
    """ Rota para atualizar dados do funcionário. """
    data = request.get_json()
    cpf_limpo = clean_only_numbers(cpf)
    
    # 1. Validação dos dados (partial=True permite enviar apenas alguns campos)
    try:
        # Nota: O Schema deve ser corrigido para aceitar 'senha' para LOAD
        funcionario_data = funcionario_schema.load(data, partial=True)
    except Exception as e:
        error_details = getattr(e, 'messages', str(e))
        return jsonify({"message": "Erro de validação", "errors": error_details}), HTTPStatus.BAD_REQUEST

    senha_hashed = None
    
    # 2. Trata a Senha (Se for enviada, gera o HASH)
    if 'senha' in funcionario_data:
        senha_pura = funcionario_data.pop('senha') 
        senha_hashed = bcrypt.generate_password_hash(senha_pura).decode('utf-8')

    # 3. Processa a Localização (se presente)
    localizacao_data = funcionario_data.pop('localizacao', None) 
    
    # 4. Chamada ao DAO para o UPDATE
    rows_affected = funcionario_dao.update(
        cpf=cpf_limpo,
        senha_hashed=senha_hashed,
        localizacao_data=localizacao_data,
        **funcionario_data
    )
    
    # 5. Resposta
    if rows_affected == 1:
        funcionario_atualizado = funcionario_dao.find_by_cpf(cpf_limpo)
        return funcionario_schema.dump(funcionario_atualizado), HTTPStatus.OK
    elif rows_affected == 0:
        return jsonify({"message": f"Funcionário {cpf} encontrado, mas nenhum dado foi alterado."}), HTTPStatus.OK
    else:
        return jsonify({"message": "Erro interno ao atualizar funcionário.", "status": "Error"}), HTTPStatus.INTERNAL_SERVER_ERROR