# src/models/devolucao_dao.py

from src.db_connection import get_db_connection
import logging
from decimal import Decimal
from datetime import date, timedelta # Import para data

logger = logging.getLogger(__name__)

class DevolucaoDAO:
    
    def registrar_devolucao(self, dados_devolucao: dict):
        """
        Executa a transação atômica completa de devolução:
        1. INSERT na devolução.
        2. INSERT em devolucao_item e UPDATE no estoque.
        3. INSERT na devolucao_credito (com data de validade de 1 ano).
        """
        conn = get_db_connection()
        if conn is None:
            return None
            
        id_devolucao = None

        try:
            with conn.cursor() as cur:
                
                # --- 1. INSERT na Tabela DEVOLUÇÃO ---
                devolucao_sql = """
                    INSERT INTO devolucao (id_venda, motivo)
                    VALUES (%s, %s)
                    RETURNING id_devolucao;
                """
                cur.execute(devolucao_sql, (dados_devolucao['id_venda'], dados_devolucao.get('motivo')))
                id_devolucao = cur.fetchone()[0]
                
                
                # --- 2. LOOP para Itens e RESTAURAÇÃO DE ESTOQUE ---
                
                for item in dados_devolucao['itens']:
                    codigo_produto = item['codigo_produto']
                    quantidade_devolvida = item['quantidade_devolvida']
                    
                    # a. RESTAURAÇÃO DE ESTOQUE (UPDATE: Aumenta a quantidade)
                    estoque_update_sql = """
                        UPDATE estoque 
                        SET quantidade = quantidade + %s 
                        WHERE codigo_produto = %s;
                    """
                    cur.execute(estoque_update_sql, (quantidade_devolvida, codigo_produto))
                    
                    # b. INSERT na DEVOLUÇÃO_ITEM
                    item_sql = """
                        INSERT INTO devolucao_item (id_devolucao, codigo_produto, quantidade_devolvida, valor_unitario)
                        VALUES (%s, %s, %s, %s);
                    """
                    cur.execute(item_sql, (
                        id_devolucao, 
                        codigo_produto, 
                        quantidade_devolvida, 
                        item['valor_unitario']
                    ))


                # --- 3. INSERT na Tabela DEVOLUÇÃO_CRÉDITO (Nova Lógica) ---
                
                # GERAÇÃO DA DATA DE VALIDADE: 1 ANO (365 dias)
                codigo_vale = f"CREDITO-{id_devolucao}-{date.today().year}"
                data_validade = date.today() + timedelta(days=365) # <-- CORREÇÃO APLICADA AQUI
                
                credito_sql = """
                    INSERT INTO devolucao_credito (id_devolucao, codigo_vale_credito, data_validade, status)
                    VALUES (%s, %s, %s, 'ATIVO');
                """
                cur.execute(credito_sql, (id_devolucao, codigo_vale, data_validade))


                # --- 4. COMMIT FINAL (Se todas as etapas acima funcionarem) ---
                conn.commit()
                return id_devolucao
                
        except Exception as e:
            logger.error(f"Erro CRÍTICO na transação de devolução: {e}")
            if conn:
                conn.rollback() 
            return None
        finally:
            if conn:
                conn.close()