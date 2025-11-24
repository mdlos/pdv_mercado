# src/models/venda_dao.py

from src.db_connection import get_db_connection
from src.utils.formatters import clean_only_numbers
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class VendaDAO:
    
    def registrar_venda(self, dados_venda: dict):
        """
        Executa a transação atômica completa da venda:
        1. INSERT na venda.
        2. INSERT nos itens.
        3. UPDATE no estoque (baixa).
        4. INSERT nos pagamentos.
        """
        conn = get_db_connection()
        if conn is None:
            return None
            
        id_venda = None

        try:
            with conn.cursor() as cur:
                
                # --- 1. INSERT na Tabela VENDA ---
                
                # Para simplificar, assumimos que o id_cliente do DB já está limpo
                cpf_cliente_limpo = dados_venda.get('cpf_cliente') 
                
                # NOTA: Assumimos que a tabela 'cliente' tem o id_cliente e o cpf_cliente
                # O Front-end deve fornecer o CPF e o Back-end faz a busca para obter o id_cliente
                # Para este DAO, vamos buscar o id_cliente (se o cpf_cliente existir)
                
                id_cliente = None
                if cpf_cliente_limpo:
                    cur.execute("SELECT id_cliente FROM cliente WHERE cpf_cnpj = %s", (cpf_cliente_limpo,))
                    cliente_result = cur.fetchone()
                    id_cliente = cliente_result[0] if cliente_result else None
                
                
                venda_sql = """
                    INSERT INTO venda (valor_total, cpf_cliente, id_cliente)
                    VALUES (%s, %s, %s)
                    RETURNING id_venda;
                """
                # O valor_total já foi calculado e validado no VendaSchema
                cur.execute(venda_sql, (dados_venda['valor_total'], cpf_cliente_limpo, id_cliente))
                id_venda = cur.fetchone()[0]
                
                
                # --- 2. INSERT na Tabela VENDA_ITEM e UPDATE no ESTOQUE ---
                
                for item in dados_venda['itens']:
                    codigo_produto = item['codigo_produto']
                    quantidade_vendida = item['quantidade_venda']
                    
                    # a. BAIXA NO ESTOQUE (UPDATE)
                    # O estoque atual é a quantidade atual - quantidade vendida
                    # Para garantir a integridade, o ideal seria checar se o estoque é suficiente
                    
                    estoque_update_sql = """
                        UPDATE estoque 
                        SET quantidade = quantidade - %s 
                        WHERE codigo_produto = %s
                        RETURNING quantidade; -- Retorna a nova quantidade para checagem
                    """
                    cur.execute(estoque_update_sql, (quantidade_vendida, codigo_produto))
                    
                    # Verificação de Estoque (Se o estoque ficou negativo, a venda deve falhar)
                    new_quantity_result = cur.fetchone()
                    if new_quantity_result is None or new_quantity_result[0] < 0:
                        raise Exception(f"Estoque insuficiente para o produto {codigo_produto}.")
                        
                    # b. INSERT na VENDA_ITEM
                    item_sql = """
                        INSERT INTO venda_item (id_venda, codigo_produto, preco_unitario, quantidade_venda, valor_total)
                        VALUES (%s, %s, %s, %s, %s);
                    """
                    cur.execute(item_sql, (
                        id_venda, 
                        codigo_produto, 
                        item['preco_unitario'], 
                        quantidade_vendida, 
                        item['subtotal']
                    ))


                # --- 3. INSERT na Tabela PAGAMENTO ---
                
                for pagamento in dados_venda['pagamentos']:
                    pagamento_sql = """
                        INSERT INTO pagamento (id_tipo, valor_pago, id_venda)
                        VALUES (%s, %s, %s);
                    """
                    cur.execute(pagamento_sql, (
                        pagamento['id_tipo'],
                        pagamento['valor_pago'],
                        id_venda
                    ))


                # --- 4. COMMIT FINAL (Se todas as etapas acima funcionarem) ---
                conn.commit()
                return id_venda
                
        except Exception as e:
            logger.error(f"Erro CRÍTICO na transação de venda: {e}")
            if conn:
                conn.rollback() # Reverte todas as alterações (venda, itens, pagamentos, estoque)
            return None
        finally:
            if conn:
                conn.close()