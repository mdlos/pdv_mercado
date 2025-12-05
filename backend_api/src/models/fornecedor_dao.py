# src/models/fornecedor_dao.py

from src.db_connection import get_db_connection
from src.utils.formatters import clean_only_numbers
import logging

logger = logging.getLogger(__name__)

class FornecedorDAO:
    
    def __init__(self):
        self.table_name = "fornecedor"
    
    def insert(self, cnpj: str, razao_social: str, email: str, celular: str = None, 
            situacao_cadastral: str = None, data_abertura: str = None, localizacao_data: dict = None):
        """ Insere a localização e, em seguida, o fornecedor na mesma transação. """
        conn = None
        id_fornecedor = None
        id_localizacao = None
        
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                
                if localizacao_data:
                    localizacao_sql = """
                        INSERT INTO localizacao (cep, logradouro, numero, bairro, cidade, uf)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id_localizacao;
                    """
                    loc_values = (
                        localizacao_data.get('cep'), localizacao_data.get('logradouro'), 
                        localizacao_data.get('numero'), localizacao_data.get('bairro'), 
                        localizacao_data.get('cidade'), localizacao_data.get('uf')
                    )
                    cur.execute(localizacao_sql, loc_values)
                    id_localizacao = cur.fetchone()[0]

                fornecedor_sql = f"""
                    INSERT INTO {self.table_name} 
                    (cnpj, razao_social, email, celular, situacao_cadastral, data_abertura, id_localizacao)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_fornecedor;
                """
                
                values = (
                    cnpj, razao_social, email, celular, situacao_cadastral, data_abertura, id_localizacao
                )
                cur.execute(fornecedor_sql, values)
                id_fornecedor = cur.fetchone()[0]
                
                conn.commit()
                return id_fornecedor
        except Exception as e:
            logger.error(f"Erro ao inserir fornecedor: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if conn: conn.close()

    def find_by_id(self, id_fornecedor: int):
        """ Busca um fornecedor pelo ID, fazendo JOIN com localizacao. """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                sql = """
                    SELECT 
                        f.id_fornecedor, f.cnpj, f.razao_social, f.email, f.celular, f.situacao_cadastral, f.data_abertura, f.id_localizacao,
                        l.cep, l.logradouro, l.numero, l.bairro, l.cidade, l.uf, l.id_localizacao AS loc_id
                    FROM fornecedor f
                    LEFT JOIN localizacao l ON f.id_localizacao = l.id_localizacao
                    WHERE f.id_fornecedor = %s;
                """
                cur.execute(sql, (id_fornecedor,))
                row = cur.fetchone()
                if row is None: return None
                
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, row))
        except Exception as e:
            logger.error(f"Erro ao buscar fornecedor {id_fornecedor}: {e}")
            return None
        finally:
            if conn: conn.close()

    def find_all(self, limit=None): # 🔑 AGORA ACEITA O PARÂMETRO LIMIT
        """ Retorna todos os fornecedores (ou limitado). """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                # Query com LEFT JOIN para buscar dados
                sql = """
                    SELECT f.id_fornecedor, f.cnpj, f.razao_social, f.email, f.celular, f.data_abertura,
                        l.cep, l.cidade, l.uf, COALESCE(l.id_localizacao, 0) AS id_localizacao
                    FROM fornecedor f
                    LEFT JOIN localizacao l ON f.id_localizacao = l.id_localizacao
                    ORDER BY f.id_fornecedor
                """
                if limit is not None:
                    sql += f" LIMIT {limit}" # Adiciona a cláusula LIMIT se for solicitada
                    
                cur.execute(sql)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao buscar todos os fornecedores: {e}")
            return []
        finally:
            if conn: conn.close()
            
    def find_by_cnpj(self, cnpj: str): 
        """ Busca um fornecedor pelo CNPJ, fazendo JOIN com localizacao. """
        conn = get_db_connection()
        if conn is None: return None

        try:
            with conn.cursor() as cur:
                # Query com JOIN para buscar todos os dados relacionados (CNPJ, Razão Social, Endereço)
                sql = """
                    SELECT 
                        f.id_fornecedor, f.cnpj, f.razao_social, f.email, f.celular, f.situacao_cadastral, f.data_abertura, f.id_localizacao,
                        l.cep, l.logradouro, l.numero, l.bairro, l.cidade, l.uf, l.id_localizacao AS loc_id
                    FROM fornecedor f
                    LEFT JOIN localizacao l ON f.id_localizacao = l.id_localizacao
                    WHERE f.cnpj = %s;
                    """
                cur.execute(sql, (cnpj,))
                row = cur.fetchone()
                if row is None: return None
                
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, row))
        except Exception as e:
            logger.error(f"Erro ao buscar fornecedor por CNPJ {cnpj}: {e}")
            return None
        finally:
            if conn: conn.close()
            
    def update(self, id_fornecedor: int, localizacao_data: dict = None, **kwargs):
        """ Atualiza dados do fornecedor e sua localização. """
        conn = None
        rows_affected_total = 0
        new_id_localizacao = None

        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                
                # Obter o id_localizacao atual e verificar se o fornecedor existe
                cur.execute("SELECT id_localizacao FROM fornecedor WHERE id_fornecedor = %s;", (id_fornecedor,))
                result = cur.fetchone()
                if not result:
                    return 0 # Fornecedor não encontrado
                current_id_localizacao = result[0]
                
                # Lógica de Atualização/Inserção de LOCALIZAÇÃO
                if localizacao_data:
                    fields_localizacao = [f"{k} = %s" for k in localizacao_data.keys()]
                    values_localizacao = list(localizacao_data.values())
                    
                    if current_id_localizacao:
                        # Caso o fornecedor já tenha endereço: UPDATE
                        values_localizacao.append(current_id_localizacao)
                        sql_localizacao = f"UPDATE localizacao SET {', '.join(fields_localizacao)} WHERE id_localizacao = %s;"
                        cur.execute(sql_localizacao, tuple(values_localizacao))
                        rows_affected_total += cur.rowcount
                        
                    else:
                        # Caso o fornecedor NÃO TENHA endereço: INSERT (e gera novo FK)
                        fields = ', '.join(localizacao_data.keys())
                        placeholders = ', '.join(['%s'] * len(values_localizacao))
                        
                        sql_insert_localizacao = f"""
                            INSERT INTO localizacao ({fields}) VALUES ({placeholders})
                            RETURNING id_localizacao;
                        """
                        cur.execute(sql_insert_localizacao, tuple(values_localizacao))
                        new_id_localizacao = cur.fetchone()[0]
                        rows_affected_total += 1


                # UPDATE na tabela FORNECEDOR
                # Inclui a nova FK se uma localização foi inserida
                if new_id_localizacao:
                    kwargs['id_localizacao'] = new_id_localizacao
                    
                fields_fornecedor = []
                values_fornecedor = []
                
                for key, value in kwargs.items():
                    fields_fornecedor.append(f"{key} = %s")
                    values_fornecedor.append(value)
                
                if fields_fornecedor:
                    values_fornecedor.append(id_fornecedor)
                    sql_fornecedor = f"UPDATE fornecedor SET {', '.join(fields_fornecedor)} WHERE id_fornecedor = %s;"
                    cur.execute(sql_fornecedor, tuple(values_fornecedor))
                    rows_affected_total += cur.rowcount

                if rows_affected_total > 0:
                    conn.commit()
                    return 1 
                else:
                    return 0 

        except Exception as e:
            logger.error(f"Erro ao atualizar fornecedor {id_fornecedor}: {e}")
            if conn: conn.rollback()
            return -1
        finally:
            if conn: conn.close()


    def delete(self, id_fornecedor: int):
        """ Deleta o fornecedor e sua localização, se existir. """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                # Obter o id_localizacao antes de deletar o fornecedor
                cur.execute("SELECT id_localizacao FROM fornecedor WHERE id_fornecedor = %s;", (id_fornecedor,))
                result = cur.fetchone()
                id_localizacao = result[0] if result else None

                # DELETE o fornecedor
                cur.execute("DELETE FROM fornecedor WHERE id_fornecedor = %s;", (id_fornecedor,))
                rows_deleted = cur.rowcount
                
                # DELETE a localização (se existia)
                if id_localizacao:
                    cur.execute("DELETE FROM localizacao WHERE id_localizacao = %s;", (id_localizacao,))
                
                conn.commit()
                return rows_deleted
        except Exception as e:
            logger.error(f"Erro ao deletar fornecedor {id_fornecedor}: {e}")
            if conn: conn.rollback()
            return 0
        finally:
            if conn: conn.close()