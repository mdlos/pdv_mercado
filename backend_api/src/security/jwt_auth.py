# src/security/jwt_auth.py

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from http import HTTPStatus
from typing import List

# 🛑 NOTA: Defina uma chave secreta forte no seu arquivo config.py ou .env
# Chave secreta de teste para o JWT
SECRET_KEY = 'SUA_CHAVE_SECRETA_JWT_AQUI' 
ALGORITHM = 'HS256'

def encode_auth_token(cpf: str, cargo: str) -> str:
    """ Gera o JWT (Token) para o usuário. """
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1), # Expira em 1 dia
            'iat': datetime.utcnow(),
            'cpf': cpf,
            'cargo': cargo # O cargo é crucial para a autorização (RBAC)
        }
        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM
        )
    except Exception as e:
        return str(e)

def decode_auth_token(auth_token: str) -> dict | None:
    """ Decodifica o JWT para obter o CPF e Cargo. """
    try:
        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expirado. Por favor, faça login novamente.'}
    except jwt.InvalidTokenError:
        return {'error': 'Token inválido.'}

def auth_required(roles: List[str] = None):
    """
    Decorator para proteger rotas. Verifica o JWT e as permissões de cargo.
    Ex: @auth_required(roles=['Gerente', 'Admin'])
    """
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({"message": "Token JWT ausente ou mal formatado."}), HTTPStatus.UNAUTHORIZED # 401

            auth_token = auth_header.split(' ')[1]
            payload = decode_auth_token(auth_token)

            if 'error' in payload:
                return jsonify({"message": payload['error']}), HTTPStatus.UNAUTHORIZED # 401
            
            # --- 🛑 LÓGICA DE AUTORIZAÇÃO (RBAC) ---
            user_cargo = payload.get('cargo')
            
            if roles and user_cargo not in roles:
                return jsonify({"message": f"Acesso negado. Cargo '{user_cargo}' não tem permissão para esta rota."}), HTTPStatus.FORBIDDEN # 403

            # Injete o CPF e Cargo no request para ser usado pelo Controller/DAO, se necessário
            request.user_cpf = payload['cpf']
            request.user_cargo = user_cargo

            return f(*args, **kwargs)
        return decorated
    return wrapper