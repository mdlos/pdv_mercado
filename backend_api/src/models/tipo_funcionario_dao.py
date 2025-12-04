# src/models/tipo_funcionario_dao.py

from src.db_connection import get_db_connection
import logging

logger = logging.getLogger(__name__)

class TipoFuncionarioDAO:
    
    def __init__(self):
        self.table_name = "tipo_funcionario"
        
    def find_all(self):
        """ Retorna todos os tipos/cargos de funcionário. """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                # Retorna o ID e o nome do cargo para o Front-end
                cur.execute(f"SELECT id_tipo_funcionario, cargo FROM {self.table_name} ORDER BY id_tipo_funcionario")
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao buscar tipos de funcionário: {e}")
            return []
        finally:
            if conn:
                conn.close()