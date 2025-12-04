# src/models/compra_dao.py (FINAL E CORRIGIDO)

from src.db_connection import get_db_connection
import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional 

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
            conn.autocommit = False 

            with conn.cursor() as cur:
                
                # 1. INSERT na Tabela COMPRA 
                sql_compra = "INSERT INTO compra (id_fornecedor, data_compra, valor_total_compra) VALUES (%s, %s, %s) RETURNING id_compra;"
                
                # Cálculo valor_total (usando custo_unitario, pois o schema deve validar essa chave)
                valor_total = sum(
                    Decimal(str(item['quantidade_comprada'])) * Decimal(str(item['custo_unitario'])) 
                    for item in dados_compra['itens']
                )

                params_compra = (
                    dados_compra['id_fornecedor'],
                    datetime.now(),
                    valor_total.to_eng_string()
                )

                cur.execute(sql_compra, params_compra)
                id_compra = cur.fetchone()[0]
                
                
                # --- 2. LOOP para Itens e AUMENTO DE ESTOQUE ---
                
                for item in dados_compra['itens']:
                    codigo_produto = item['codigo_produto']
                    quantidade_comprada = item['quantidade_comprada']
                    custo_unitario = item['custo_unitario']
                    
                    # A. INSERT na COMPRA_ITEM
                    # 🛑 NOTA: Assumindo que a coluna na compra_item se chama 'custo_unitario', não 'preco_unitario'
                    sql_item = "INSERT INTO compra_item (id_compra, codigo_produto, quantidade_comprada, custo_unitario) VALUES (%s, %s, %s, %s);"
                    params_item = (id_compra, codigo_produto, quantidade_comprada, custo_unitario)
                    cur.execute(sql_item, params_item)
                    
                    # B. SQL para atualizar o estoque (AUMENTO)
                    sql_estoque_update = "UPDATE estoque SET quantidade = quantidade + %s WHERE codigo_produto = %s;"
                    params_estoque_update = (quantidade_comprada, codigo_produto)
                    cur.execute(sql_estoque_update, params_estoque_update)


            # 3. COMMIT FINAL
            conn.commit() 
            return id_compra
        except Exception as e:
                logger.error(f"Erro CRÍTICO na transação de compra: {e}")
                if conn:
                    conn.rollback() 
                raise e 
        
        finally:
            # 🛑 CORREÇÃO 1: Remover manipulação de autocommit no finally
            if conn:
                conn.close()

    # -----------------------------------------------------------------
    # R - READ (Buscar Compras por Data/Período) - CORRIGIDO
    # -----------------------------------------------------------------
    def find_by_date(self, data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> list[dict]:
        conn = get_db_connection()
        if conn is None: return []

        try:
            with conn.cursor() as cur:
                sql = """
                    SELECT 
                        c.id_compra, c.data_compra, c.valor_total_compra, 
                        f.razao_social AS nome_fornecedor -- 🛑 CORREÇÃO 2: Usar razao_social
                    FROM compra c
                    LEFT JOIN fornecedor f ON c.id_fornecedor = f.id_fornecedor 
                """
                params = []
                where_clauses = []
                
                if data_inicio:
                    where_clauses.append("c.data_compra >= %s")
                    params.append(data_inicio)
                    
                if data_fim:
                    where_clauses.append("c.data_compra < %s::date + INTERVAL '1 day'")
                    params.append(data_fim)
                
                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)
                
                sql += " ORDER BY c.data_compra DESC;"
                
                cur.execute(sql, params)
                rows = cur.fetchall()
                
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Erro ao buscar compras por data: {e}")
            # 🛑 CORREÇÃO 3: Propagar o erro para o Controller, que lida com o 500.
            raise 
        finally:
            if conn:
                conn.close()