# src/models/compra_dao.py

from src.db_connection import get_db_connection
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class CompraDAO:
    
    def registrar_compra(self, dados_compra: dict):
        """
        Executa a transação atômica completa da compra:
        1. INSERT na compra.
        2. INSERT nos itens da compra.
        3. UPDATE no estoque (aumento da quantidade).
        """
        conn = get_db_connection()
        if conn is None:
            return None
            
        id_compra = None

        try:
            with conn.cursor() as cur:
                
                # --- 1. INSERT na Tabela COMPRA ---
                compra_sql = """
                    INSERT INTO compra (id_fornecedor, data_compra, data_entrega, valor_total_compra)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id_compra;
                """
                cur.execute(compra_sql, (
                    dados_compra['id_fornecedor'], 
                    dados_compra['data_compra'], 
                    dados_compra.get('data_entrega'), 
                    dados_compra['valor_total_compra']
                ))
                id_compra = cur.fetchone()[0]
                
                
                # --- 2. LOOP para Itens e AUMENTO DE ESTOQUE ---
                
                for item in dados_compra['itens']:
                    codigo_produto = item['codigo_produto']
                    quantidade_compra = item['quantidade_compra']
                    
                    # a. AUMENTO NO ESTOQUE (UPDATE)
                    # Adiciona a quantidade comprada ao estoque
                    estoque_update_sql = """
                        UPDATE estoque 
                        SET quantidade = quantidade + %s 
                        WHERE codigo_produto = %s;
                    """
                    cur.execute(estoque_update_sql, (quantidade_compra, codigo_produto))
                    
                    # b. INSERT na COMPRA_ITEM
                    item_sql = """
                        INSERT INTO compra_item (id_compra, codigo_produto, quantidade_compra, preco_unitario)
                        VALUES (%s, %s, %s, %s);
                    """
                    cur.execute(item_sql, (
                        id_compra, 
                        codigo_produto, 
                        quantidade_compra, 
                        item['preco_unitario']
                    ))


                # --- 3. COMMIT FINAL (Se todas as etapas acima funcionarem) ---
                conn.commit()
                return id_compra
                
        except Exception as e:
            logger.error(f"Erro CRÍTICO na transação de compra: {e}")
            if conn:
                conn.rollback() # Reverte todas as alterações (compra, itens, estoque)
            return None
        finally:
            if conn:
                conn.close()