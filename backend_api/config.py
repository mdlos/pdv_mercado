# config.py

import os

class Config:
    # A chave secreta é essencial para segurança em sessões e proteção CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-padrao-caso-nao-encontre'
    
    # Configurações gerais do ambiente
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    
    # As variáveis do banco de dados serão lidas aqui
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')