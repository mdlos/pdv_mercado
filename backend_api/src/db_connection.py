# src/db_connection.py

import psycopg
import os
from dotenv import load_dotenv 

load_dotenv() 

def get_db_connection():
    """
    Estabelece e retorna uma nova conexão com o PostgreSQL usando psycopg (v3).
    A função usa as variáveis de ambiente (DB_HOST, DB_NAME, etc.) do .env.
    """
    try:
        conn = psycopg.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),  
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5432") 
        )
        return conn
    except Exception as e:
        print(f"ERRO DE CONEXÃO COM O BANCO DE DADOS (psycopg v3): {e}")
        return None