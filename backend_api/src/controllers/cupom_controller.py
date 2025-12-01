# backend_api/src/controllers/cupom_controller.py

from flask import Blueprint, request, jsonify
from src.models.cupom_dao import CupomDAO
# from src.decorators.auth import auth_required # Importar quando o decorator de autorização for criado

cupom_bp = Blueprint('cupom', __name__)
dao = CupomDAO()

@cupom_bp.route('/', methods=['POST'])
# @auth_required(roles=['Admin', 'Caixa']) # Exemplo de como proteger a rota
def criar_cupom():
    data = request.get_json()
    
    # -------------------------------------------------------------------------
    # 1. VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS (Mínimo para registrar uma venda)
    # -------------------------------------------------------------------------
    required_fields = ['numero_nf', 'id_funcionario', 'itens_vendidos', 'condicao_pagamento', 'valor_pago']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"O campo '{field}' é obrigatório para registrar a venda."}), 400

    # Validação da lista de itens
    itens_vendidos = data['itens_vendidos']
    if not isinstance(itens_vendidos, list) or not itens_vendidos:
        return jsonify({"error": "A lista de itens vendidos está inválida ou vazia."}), 400

    # -------------------------------------------------------------------------
    # 2. EXTRAÇÃO E PREPARAÇÃO DOS DADOS
    # -------------------------------------------------------------------------
    try:
        id_funcionario = int(data['id_funcionario'])
        valor_pago = float(data['valor_pago'])
        
        # Campos opcionais para identificação do cliente
        id_cliente = data.get('id_cliente')
        cpf_cliente = data.get('cpf_cliente')

        # Certificar-se de que os valores opcionais são None se vazios
        if id_cliente is not None:
            id_cliente = int(id_cliente)
        
    except (ValueError, TypeError):
        return jsonify({"error": "Tipos de dados inválidos para id_funcionario, id_cliente ou valor_pago."}), 400

    # -------------------------------------------------------------------------
    # 3. CHAMADA AO DAO
    # -------------------------------------------------------------------------
    try:
        id_cupom = dao.create_cupom(
            numero_nf=data['numero_nf'],
            id_funcionario=id_funcionario,
            itens_vendidos=itens_vendidos,
            condicao_pagamento=data['condicao_pagamento'],
            valor_pago=valor_pago,
            id_cliente=id_cliente,
            cpf_cliente=cpf_cliente
        )
        
        if id_cupom is None:
            # Isso cobre falhas no DB não tratadas (que deveriam ser 500)
            return jsonify({"error": "Falha interna ao criar o cupom de venda."}), 500

        return jsonify({
            "message": "Venda registrada com sucesso.",
            "id_cupom": id_cupom,
            "numero_nf": data['numero_nf']
        }), 201

    except Exception as e:
        # Tratamento genérico de erro, idealmente deve ser mais específico
        # Ex: tratar erro de chave estrangeira com 400
        return jsonify({"error": "Erro no servidor ao processar a venda.", "details": str(e)}), 500