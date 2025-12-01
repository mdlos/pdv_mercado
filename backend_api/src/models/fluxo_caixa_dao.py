# src/models/fluxo_caixa_dao.py

from src.db_connection import get_db_connection
import logging
from datetime import datetime
from decimal import Decimal

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
                # ESTA É A LINHA CRÍTICA: O saldo_inicial precisa ser um valor Decimal aqui.
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

    def fechar_caixa(self, id_fluxo: int, saldo_final_informado: Decimal):
        """ 
        Registra o fechamento de um turno existente. 
        Atualiza o status e o saldo final, e define a data/hora de fechamento.
        """
        conn = get_db_connection()
        if conn is None: return 0
        
        try:
            with conn.cursor() as cur:
                # O status final é 'FECHADO', e a data/hora de fechamento é definida agora
                sql = f"""
                    UPDATE {self.table_name}
                    SET status = 'FECHADO', 
                        saldo_final_informado = %s,
                        data_hora_fechamento = CURRENT_TIMESTAMP
                    WHERE id_fluxo = %s AND status = 'ABERTO';
                """
                cur.execute(sql, (saldo_final_informado, id_fluxo))
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
                sql = f"SELECT * FROM {self.table_name} WHERE id_fluxo = %s"
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