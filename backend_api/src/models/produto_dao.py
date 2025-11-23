# src/models/produto_dao.py (VERSÃO FINAL E COMPLETA)

from src.db_connection import get_db_connection
import logging

logger = logging.getLogger(__name__)

DEFAULT_INITIAL_QUANTITY = 0 

class ProdutoDAO:
    
    def __init__(self):
        self.table_name = "produto"
    
    # -----------------------------------------------------------------
    # R - READ (Busca) - CORRIGIDO (Adicionando find_by_id)
    # -----------------------------------------------------------------
    
    def find_all(self):
        """ Retorna todos os produtos do banco, incluindo a quantidade do estoque. """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                # SQL: Adiciona LEFT JOIN com a tabela 'estoque'
                sql = f"""
                    SELECT 
                        p.codigo_produto, p.nome, p.descricao, p.preco, p.codigo_barras, 
                        COALESCE(e.quantidade, 0) AS quantidade
                    FROM {self.table_name} p
                    LEFT JOIN estoque e ON p.codigo_produto = e.codigo_produto
                    ORDER BY p.codigo_produto;
                """
                cur.execute(sql)
                
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao buscar todos os produtos: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def find_by_id(self, codigo_produto: int): # <--- MÉTODO QUE FALTAVA!
        """ Retorna um produto pelo seu código. """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute(f'SELECT "codigo_produto", "nome", "descricao", "preco", "codigo_barras" FROM {self.table_name} WHERE "codigo_produto" = %s', (codigo_produto,))
                row = cur.fetchone()
                if row is None:
                    return None
                
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, row))
        except Exception as e:
            logger.error(f"Erro ao buscar produto {codigo_produto}: {e}")
            return None
        finally:
            if conn:
                conn.close()

    # -----------------------------------------------------------------
    # C - CREATE (Inserção) - NOMENCLATURA EM INGLÊS MANTIDA
    # -----------------------------------------------------------------

    def insert(self, nome: str, descricao: str, preco: str, codigo_barras: str = None, initial_quantity: int = DEFAULT_INITIAL_QUANTITY):
        """ Insere um novo produto e inicializa seu estoque na mesma transação. """
        conn = None
        last_id = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                # 1. INSERE O PRODUTO E RETORNA O ID
                cur.execute(
                    f"""
                    INSERT INTO {self.table_name} ("nome", "descricao", "preco", "codigo_barras")
                    VALUES (%s, %s, %s, %s)
                    RETURNING codigo_produto;
                    """,
                    (nome, descricao, preco, codigo_barras)
                )
                last_id = cur.fetchone()[0]
                
                # 2. INSERE O REGISTRO DE ESTOQUE
                cur.execute(
                    """
                    INSERT INTO estoque (codigo_produto, quantidade)
                    VALUES (%s, %s);
                    """,
                    (last_id, initial_quantity)
                )

                # 3. COMMIT (Transação atômica)
                conn.commit()
                return last_id
        except Exception as e:
            logger.error(f"Erro ao inserir produto e inicializar estoque: {e}")
            if conn:
                conn.rollback() 
            return None
        finally:
            if conn:
                conn.close()

    # -----------------------------------------------------------------
    # U - UPDATE (Atualização) - NOMENCLATURA EM INGLÊS MANTIDA
    # -----------------------------------------------------------------

    def update(self, codigo_produto: int, **kwargs):
        """ 
        Atualiza campos de um produto. 
        **kwargs recebe nome, descricao, preco, codigo_barras (opcionais).
        """
        if not kwargs:
            return 0  

        conn = None
        try:
            conn = get_db_connection()
            
            set_clauses = []
            values = []
            
            for key, value in kwargs.items():
                set_clauses.append(f'"{key}" = %s') 
                values.append(value)
            
            values.append(codigo_produto)
            
            # SQL: Cláusula WHERE
            sql = f'UPDATE {self.table_name} SET {", ".join(set_clauses)} WHERE "codigo_produto" = %s'
            
            with conn.cursor() as cur:
                cur.execute(sql, tuple(values))
                rows_affected = cur.rowcount
                conn.commit()
                return rows_affected

        except Exception as e:
            logger.error(f"Erro ao atualizar produto {codigo_produto}: {e}")
            if conn:
                conn.rollback()
            return 0
        finally:
            if conn:
                conn.close()
                
    # -----------------------------------------------------------------
    # D - DELETE (Exclusão) - NOMENCLATURA EM INGLÊS MANTIDA
    # -----------------------------------------------------------------

    def delete(self, codigo_produto: int):
        """ Deleta um produto e seu registro de estoque. """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                # 1. DELETA O REGISTRO DE ESTOQUE
                cur.execute(f'DELETE FROM estoque WHERE "codigo_produto" = %s', (codigo_produto,))
                
                # 2. DELETA O PRODUTO
                cur.execute(f'DELETE FROM {self.table_name} WHERE "codigo_produto" = %s', (codigo_produto,))
                rows_affected = cur.rowcount
                
                conn.commit()
                return rows_affected
        except Exception as e:
            logger.error(f"Erro ao deletar produto {codigo_produto}: {e}")
            if conn:
                conn.rollback()
            return 0
        finally:
            if conn:
                conn.close()