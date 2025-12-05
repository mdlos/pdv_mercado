
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.db_connection import get_db_connection

def create_tables():
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to DB")
        return

    with conn.cursor() as cur:
        print("Creating tables...")
        
        # Create venda table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS venda (
                id_venda SERIAL PRIMARY KEY,
                valor_total DECIMAL(10, 2),
                cpf_cnpj_cliente VARCHAR(20),
                id_cliente INTEGER,
                cpf_funcionario VARCHAR(11),
                id_tipo_pagamento INTEGER,
                valor_pago DECIMAL(10, 2),
                troco DECIMAL(10, 2),
                desconto DECIMAL(10, 2),
                data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'Aprovada'
            );
        """)
        
        # Create venda_item table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS venda_item (
                id_venda_item SERIAL PRIMARY KEY,
                id_venda INTEGER REFERENCES venda(id_venda),
                codigo_produto INTEGER,
                preco_unitario DECIMAL(10, 2),
                quantidade_venda INTEGER,
                valor_total DECIMAL(10, 2)
            );
        """)

        # Create fluxo_caixa table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fluxo_caixa (
                id_fluxo SERIAL PRIMARY KEY,
                status VARCHAR(20),
                saldo_inicial DECIMAL(10, 2),
                cpf_funcionario_abertura VARCHAR(11),
                saldo_contado DECIMAL(10, 2),
                data_hora_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_hora_fechamento TIMESTAMP
            );
        """)

        # Create fluxo_caixa_movimento table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fluxo_caixa_movimento (
                id_movimento SERIAL PRIMARY KEY,
                id_fluxo INTEGER REFERENCES fluxo_caixa(id_fluxo),
                id_venda INTEGER REFERENCES venda(id_venda),
                valor DECIMAL(10, 2),
                tipo VARCHAR(20)
            );
        """)
        
        conn.commit()
        print("Tables created successfully")
    
    conn.close()

if __name__ == "__main__":
    create_tables()
