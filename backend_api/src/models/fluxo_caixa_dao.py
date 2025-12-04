# src/models/fluxo_caixa_dao.py (VERSÃO FINAL E CORRIGIDA)

from src.db_connection import get_db_connection
import logging
from datetime import datetime
from decimal import Decimal
# 🛑 CORREÇÃO DE IMPORTAÇÃO: Remover a Nota e deixar os imports necessários
# from psycopg import rows 
# import psycopg 

logger = logging.getLogger(__name__)

class FluxoCaixaDAO:
    
    def __init__(self):
        self.table_name = "fluxo_caixa"

    def abrir_caixa(self, cpf_funcionario: str, saldo_inicial: Decimal):
        """ Registra a abertura de um novo turno de caixa. """
        conn = get_db_connection()
        if conn is None: return None
        
        try:
            with conn.cursor() as cur:
                # O status inicial é fixo como 'ABERTO'
                sql = f"""
                    INSERT INTO {self.table_name} 
                    (status, saldo_inicial, cpf_funcionario_abertura)
                    VALUES ('ABERTO', %s, %s)
                    RETURNING id_fluxo;
                """
                cur.execute(sql, (saldo_inicial, cpf_funcionario))
                id_fluxo = cur.fetchone()[0]
                conn.commit()
                return id_fluxo
        except Exception as e:
            logger.error(f"Erro ao abrir caixa para {cpf_funcionario}: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if conn: conn.close()

    def fechar_caixa(self, id_fluxo: int, saldo_contado: Decimal): # 🛑 Renomeado para saldo_contado
        """ 
        Registra o fechamento de um turno existente. 
        Atualiza o status e o saldo contado, e define a data/hora de fechamento.
        """
        conn = get_db_connection()
        if conn is None: return 0
        
        try:
            with conn.cursor() as cur:
                # O status final é 'FECHADO', e a data/hora de fechamento é definida agora
                sql = f"""
                    UPDATE {self.table_name}
                    SET status = 'FECHADO', 
                        saldo_contado = %s, -- 🛑 Usando saldo_contado (coluna corrigida)
                        data_hora_fechamento = CURRENT_TIMESTAMP
                    WHERE id_fluxo = %s AND status = 'ABERTO';
                """
                cur.execute(sql, (saldo_contado, id_fluxo))
                rows_affected = cur.rowcount
                conn.commit()
                return rows_affected
        except Exception as e:
            logger.error(f"Erro ao fechar caixa {id_fluxo}: {e}")
            if conn: conn.rollback()
            return 0
        finally:
            if conn: conn.close()
            
    def buscar_por_id(self, id_fluxo: int):
        """ Busca um registro de fluxo de caixa pelo ID. """
        conn = get_db_connection()
        if conn is None: return None
        
        try:
            with conn.cursor() as cur:
                sql = sql = """
                    SELECT 
                        fc.*, 
                        f.nome AS nome_operador -- 🛑 Adicionar o nome
                    FROM fluxo_caixa fc
                    LEFT JOIN funcionario f ON fc.cpf_funcionario_abertura = f.cpf
                    WHERE fc.id_fluxo = %s;
                    """
                cur.execute(sql, (id_fluxo,))
                row = cur.fetchone()
                if row is None: return None
                
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, row))
        except Exception as e:
            logger.error(f"Erro ao buscar fluxo {id_fluxo}: {e}")
            return None
        finally:
            if conn: conn.close()
            
    def buscar_caixa_aberto(self, cpf_funcionario: str):
        """ Retorna o ID do turno de caixa ABERTO para o funcionário. """
        conn = get_db_connection()
        if conn is None: return None
        
        try:
            with conn.cursor() as cur:
                sql = f"""
                    SELECT id_fluxo FROM {self.table_name} 
                    WHERE cpf_funcionario_abertura = %s AND status = 'ABERTO' 
                    ORDER BY data_hora_abertura DESC LIMIT 1;
                """
                cur.execute(sql, (cpf_funcionario,))
                row = cur.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Erro ao buscar caixa aberto para {cpf_funcionario}: {e}")
            return None
        finally:
            if conn: conn.close()
            
    def buscar_todos_fechados(self):
        """ Retorna todos os registros de caixa que estão FECHADO, com o nome do funcionário. """
        conn = get_db_connection()
        if conn is None: return []
        
        try:
            with conn.cursor() as cur:
                # Query com JOIN para buscar o nome do funcionário
                sql = """
                    SELECT fc.*, f.nome AS nome_funcionario
                    FROM fluxo_caixa fc
                    JOIN funcionario f ON fc.cpf_funcionario_abertura = f.cpf
                    WHERE fc.status = 'FECHADO'
                    ORDER BY fc.data_hora_fechamento DESC;
                """
                cur.execute(sql)
                rows = cur.fetchall()
                
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Erro ao buscar caixas fechados: {e}")
            return []
        finally:
            if conn: conn.close()
            
    def buscar_resumo_pagamentos_por_fluxo(self, id_fluxo: int) -> dict:
        """
        Calcula o resumo das vendas por tipo de pagamento para o turno (id_fluxo).
        O problema de retornar zero é corrigido pelo cast ::numeric.
        """
        conn = get_db_connection()
        if conn is None: return {'resumo_pagamentos': [], 'total_cancelado': Decimal('0.00')}

        try:
            with conn.cursor() as cur: 

                # 🛑 CORREÇÃO 1: Adicionar o CAST ::numeric para forçar a soma
                sql_resumo = """
                    SELECT
                        tp.id_tipo,
                        tp.descricao AS tipo_pagamento,
                        COALESCE(SUM(v.valor_total::numeric), 0) AS total_arrecadado 
                    FROM venda v
                    JOIN fluxo_caixa_movimento fcm ON v.id_venda = fcm.id_venda 
                    JOIN tipo_pagamento tp ON v.id_tipo_pagamento = tp.id_tipo
                    WHERE fcm.id_fluxo = %s AND v.status = 'Aprovada'
                    GROUP BY tp.id_tipo, tp.descricao;
                """
                cur.execute(sql_resumo, (id_fluxo,))
                
                # Mapeamento do resultado para dicionário
                resumo_pagamentos_raw = cur.fetchall()
                cols = [desc[0] for desc in cur.description]
                resumo_pagamentos = [dict(zip(cols, r)) for r in resumo_pagamentos_raw]

                # 🛑 CORREÇÃO 2: Adicionar o CAST ::numeric para forçar a soma de cancelados
                sql_cancelado = """
                    SELECT
                        COALESCE(SUM(v.valor_total::numeric), 0) AS total_cancelado
                    FROM venda v
                    JOIN fluxo_caixa_movimento fcm ON v.id_venda = fcm.id_venda
                    WHERE fcm.id_fluxo = %s AND v.status = 'Cancelada';
                """
                cur.execute(sql_cancelado, (id_fluxo,))
                
                # Tratar o retorno do single value (fetch all para evitar problemas com fetchone)
                total_cancelado_raw = cur.fetchone()
                total_cancelado = total_cancelado_raw[0] if total_cancelado_raw else Decimal('0.00')
                
                return {
                    'resumo_pagamentos': resumo_pagamentos,
                    'total_cancelado': total_cancelado
                }

        except Exception as e:
            # Captura exceções e loga
            logger.error(f"Erro ao buscar resumo de pagamentos para fluxo {id_fluxo}: {e}")
            return {'resumo_pagamentos': [], 'total_cancelado': Decimal('0.00')}
        finally:
            if conn: conn.close()