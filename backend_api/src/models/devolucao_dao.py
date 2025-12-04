# src/models/devolucao_dao.py (CÓDIGO FINAL COM CORREÇÃO DE ID E DATA)

from src.db_connection import get_db_connection
import logging
from decimal import Decimal
from datetime import date, timedelta 
from typing import Optional

logger = logging.getLogger(__name__)

class DevolucaoDAO:
    
    def registrar_devolucao(self, dados_devolucao: dict):
        """
        Executa a transação atômica completa de devolução,
        incluindo o registro do funcionário que a processou.
        """
        conn = None
        id_devolucao = None
        
        # EXTRAÇÃO CRÍTICA: Valor total, CPF Cliente, e CPF Funcionário (Vindo do Schema)
        valor_total_devolucao = dados_devolucao['valor_total_devolucao']
        cpf_cliente = dados_devolucao['cpf_cliente']
        cpf_funcionario = dados_devolucao['cpf_funcionario'] 
        
        try:
            conn = get_db_connection()
            conn.autocommit = False 

            with conn.cursor() as cur:
                
                # --- 1. INSERT na Tabela DEVOLUÇÃO ---
                devolucao_sql = """
                    INSERT INTO devolucao (id_venda, motivo, cpf_funcionario) 
                    VALUES (%s, %s, %s)
                    RETURNING id_devolucao;
                """
                cur.execute(devolucao_sql, (
                    dados_devolucao['id_venda'], 
                    dados_devolucao.get('motivo'),
                    cpf_funcionario 
                ))
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


                # --- 3. INSERT na Tabela DEVOLUÇÃO_CRÉDITO (Adicionar Valor e Cliente) ---
                
                codigo_vale = f"CREDITO-{id_devolucao}-{date.today().year}"
                data_validade = date.today() + timedelta(days=365)
                
                credito_sql = """
                    INSERT INTO devolucao_credito (id_devolucao, codigo_vale_credito, cpf_cliente, valor_credito, data_validade, status)
                    VALUES (%s, %s, %s, %s, %s, 'ATIVO');
                """
                cur.execute(credito_sql, (
                    id_devolucao, 
                    codigo_vale, 
                    cpf_cliente, 
                    valor_total_devolucao.to_eng_string(), 
                    data_validade
                ))


                # --- 4. COMMIT FINAL (Transação atômica) ---
                conn.commit()
                return id_devolucao
                
        except Exception as e:
            logger.error(f"Erro CRÍTICO na transação de devolução: {e}")
            if conn:
                conn.rollback() 
            raise 
        finally:
            if conn:
                conn.autocommit = True
                conn.close()

    def find_active_credit_by_cpf(self, cpf_cliente: str) -> list[dict]:
        """ Busca todos os vales de crédito ATIVOS para um CPF específico. """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                sql = """
                    SELECT 
                        id_devolucao, codigo_vale_credito, valor_credito, data_validade -- 🛑 CORREÇÃO FINAL APLICADA AQUI
                    FROM devolucao_credito 
                    WHERE cpf_cliente = %s AND status = 'ATIVO';
                """
                cur.execute(sql, (cpf_cliente,))
                rows = cur.fetchall()
                
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Erro ao buscar créditos ativos para o CPF {cpf_cliente}: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def buscar_devolucao_completa(self, id_devolucao: int) -> dict | None:
        """ Busca todos os detalhes da devolução, itens devolvidos, e o vale-crédito gerado. """
        conn = None
        try:
            conn = get_db_connection()
            
            with conn.cursor() as cur:
                
                # 1. BUSCA O CABEÇALHO DA DEVOLUÇÃO E OS DADOS DO VALE/CLIENTE
                sql_devolucao = """
                    SELECT
                        d.id_devolucao, d.id_venda, d.motivo, 
                        d.data_devolucao AS data_hora_devolucao, -- CORREÇÃO DE DATA CONFIRMADA
                        dc.codigo_vale_credito, dc.valor_credito, dc.data_validade, dc.status AS status_credito,
                        dc.cpf_cliente, d.cpf_funcionario,
                        c.nome AS nome_cliente, c.cpf_cnpj AS cpf_cnpj_cliente,
                        cm.cnpj AS mercado_cnpj, cm.endereco AS mercado_endereco
                    FROM devolucao d
                    JOIN devolucao_credito dc ON d.id_devolucao = dc.id_devolucao
                    LEFT JOIN cliente c ON dc.cpf_cliente = c.cpf_cnpj 
                    LEFT JOIN configuracao_mercado cm ON cm.id_config = 1 
                    WHERE d.id_devolucao = %s;
                """
                cur.execute(sql_devolucao, (id_devolucao,))
                devolucao_record = cur.fetchone()

                if not devolucao_record:
                    return None
                
                header_cols = [desc[0] for desc in cur.description]
                devolucao_data = dict(zip(header_cols, devolucao_record))

                # 2. BUSCA OS ITENS DEVOLVIDOS
                sql_itens = """
                    SELECT
                        di.codigo_produto, di.quantidade_devolvida, di.valor_unitario,
                        p.nome AS nome_produto
                    FROM devolucao_item di
                    JOIN produto p ON di.codigo_produto = p.codigo_produto
                    WHERE di.id_devolucao = %s;
                """
                cur.execute(sql_itens, (id_devolucao,))
                item_records = cur.fetchall()
                item_cols = [desc[0] for desc in cur.description]
                
                devolucao_data['itens_devolvidos'] = [dict(zip(item_cols, row)) for row in item_records]
                
                return devolucao_data
        except Exception as e:
            logger.error(f"Erro ao buscar devolução completa {id_devolucao}: {e}")
            return None
        finally:
            if conn:
                conn.close()


    def find_devolucao_ids_by_cpf(self, cpf_cliente: str) -> list[dict]:
        """ Busca todos os IDs de devolução vinculados a um CPF de cliente. """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                sql = """
                    SELECT d.id_devolucao 
                    FROM devolucao d
                    JOIN devolucao_credito dc ON d.id_devolucao = dc.id_devolucao
                    WHERE dc.cpf_cliente = %s
                    ORDER BY d.data_devolucao DESC; -- CORREÇÃO DE DATA CONFIRMADA
                """
                cur.execute(sql, (cpf_cliente,))
                rows = cur.fetchall()
                
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Erro ao buscar IDs de devolução para o CPF {cpf_cliente}: {e}")
            return []
        finally:
            if conn:
                conn.close()