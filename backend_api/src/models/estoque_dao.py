# src/models/estoque_dao.py

from src.db_connection import get_db_connection
import logging

logger = logging.getLogger(__name__)

class EstoqueDAO:
    
    def __init__(self):
        self.table_name = "estoque"
    
    # -----------------------------------------------------------------
    # C - CREATE (Inicializa estoque)
    # -----------------------------------------------------------------
    
    def insert(self, codigo_produto: int, quantidade: int):
        """ Inicializa o registro de estoque para um novo produto. """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                # O comando não retorna ID, mas sim o código_produto inserido
                cur.execute(
                    f"""
                    INSERT INTO {self.table_name} (codigo_produto, quantidade)
                    VALUES (%s, %s)
                    RETURNING codigo_produto;
                    """,
                    (codigo_produto, quantidade)
                )
                conn.commit()
                return codigo_produto
        except Exception as e:
            logger.error(f"Erro ao inicializar estoque para produto {codigo_produto}: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if conn: conn.close()
            
    # -----------------------------------------------------------------
    # R - READ (Busca Estoque)
    # -----------------------------------------------------------------
    
    def find_by_product_id(self, codigo_produto: int):
        """ Retorna o registro de estoque pelo código do produto. """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute(f"SELECT codigo_produto, quantidade FROM {self.table_name} WHERE codigo_produto = %s", (codigo_produto,))
                row = cur.fetchone()
                if row is None: return None
                
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, row))
        except Exception as e:
            logger.error(f"Erro ao buscar estoque de produto {codigo_produto}: {e}")
            return None
        finally:
            if conn: conn.close()

    # -----------------------------------------------------------------
    # U - UPDATE (Atualiza a quantidade)
    # -----------------------------------------------------------------

    def update_quantity(self, codigo_produto: int, nova_quantidade: int):
        """ Atualiza a quantidade do produto no estoque. """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE {self.table_name} SET quantidade = %s WHERE codigo_produto = %s",
                    (nova_quantidade, codigo_produto)
                )
                rows_affected = cur.rowcount
                conn.commit()
                return rows_affected
        except Exception as e:
            logger.error(f"Erro ao atualizar estoque de produto {codigo_produto}: {e}")
            if conn: conn.rollback()
            return 0
        finally:
            if conn: conn.close()