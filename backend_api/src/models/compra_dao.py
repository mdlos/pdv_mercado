# src/models/compra_dao.py (VERSÃO FINAL E CORRIGIDA)

from src.db_connection import get_db_connection
import logging
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)

class CompraDAO:
    
    def __init__(self):
        self.table_name = "compra"
        
    def registrar_compra(self, dados_compra: dict):
        """
        Registra uma nova compra, seus itens e atualiza o estoque de forma ATÔMICA (transacional).
        """
        conn = None
        id_compra = None
        try:
            conn = get_db_connection()
            conn.autocommit = False # Garante controle manual

            with conn.cursor() as cur:
                
                # 1. INSERT na Tabela COMPRA 
                sql_compra = "INSERT INTO compra (id_fornecedor, data_compra, valor_total_compra) VALUES (%s, %s, %s) RETURNING id_compra;"
                
                # Cálculo valor_total
                valor_total = sum(
                    Decimal(str(item['quantidade_compra'])) * Decimal(str(item['preco_unitario'])) 
                    for item in dados_compra['itens']
                )

                params_compra = (
                    dados_compra['id_fornecedor'],
                    dados_compra['data_compra'],
                    valor_total.to_eng_string()
                )

                cur.execute(sql_compra, params_compra)
                id_compra = cur.fetchone()[0]
                
                
                # --- 2. LOOP para Itens e AUMENTO DE ESTOQUE ---
                
                for item in dados_compra['itens']:
                    codigo_produto = item['codigo_produto']
                    quantidade_compra = item['quantidade_compra']
                    preco_unitario = item['preco_unitario']

                    # A. INSERT na COMPRA_ITEM (ESTA LINHA VAI FALHAR COM FK INEXISTENTE)
                    sql_item = "INSERT INTO compra_item (id_compra, codigo_produto, quantidade_compra, preco_unitario) VALUES (%s, %s, %s, %s);"
                    params_item = (id_compra, codigo_produto, quantidade_compra, preco_unitario)
                    cur.execute(sql_item, params_item)
                    
                    # B. SQL para atualizar o estoque (AUMENTO)
                    sql_estoque_update = "UPDATE estoque SET quantidade = quantidade + %s WHERE codigo_produto = %s;"
                    params_estoque_update = (quantidade_compra, codigo_produto)
                    cur.execute(sql_estoque_update, params_estoque_update)


            # 3. COMMIT FINAL: SOMENTE SE O LOOP INTEIRO PASSAR
            conn.commit() 
            return id_compra
        except Exception as e:
                # 4. Rollback: Se o erro (FK) ocorrer no loop, tudo é desfeito
                logger.error(f"Erro CRÍTICO na transação de compra: {e}")
                if conn:
                    conn.rollback() 
                
                # 🔑 CORREÇÃO FINAL: Relança a exceção (IntegrityError) para o Pytest capturar
                raise e 
        
        finally:
            # 5. Fechamento da Conexão
            if conn:
                conn.autocommit = True
                conn.close()