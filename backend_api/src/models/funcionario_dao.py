# src/models/funcionario_dao.py

from src.db_connection import get_db_connection
import logging
from flask_bcrypt import Bcrypt # Importamos Bcrypt, mas ele precisa ser inicializado no app.py

logger = logging.getLogger(__name__)

# NOTA: O objeto Bcrypt será injetado ou inicializado no app.py, por enquanto o DAO foca no SQL.

class FuncionarioDAO:
    
    def __init__(self):
        self.table_name = "funcionario"
    
    # -----------------------------------------------------------------
    # C - CREATE (Inserção)
    # -----------------------------------------------------------------
    
    def insert(self, cpf: str, nome: str, sobrenome: str, senha_hashed: str, id_tipo_funcionario: int, 
            email: str = None, sexo: str = None, telefone: str = None, nome_social: str = None, 
            localizacao_data: dict = None):
        """ Insere a localização (se houver) e o funcionário na mesma transação. """
        conn = None
        id_localizacao = None
        
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                
                # 1. INSERIR LOCALIZAÇÃO (SE HOUVER)
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

                # 2. INSERIR FUNCIONÁRIO (Com senha hashed e FKs)
                funcionario_sql = f"""
                    INSERT INTO {self.table_name} 
                    (cpf, nome, sobrenome, senha, email, sexo, telefone, nome_social, id_tipo_funcionario, id_localizacao)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                
                # Valores do funcionário
                values = (
                    cpf, nome, sobrenome, senha_hashed, email, sexo, telefone, nome_social, id_tipo_funcionario, id_localizacao
                )
                cur.execute(funcionario_sql, values)
                
                conn.commit()
                return cpf
        except Exception as e:
            logger.error(f"Erro ao inserir funcionário: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if conn: conn.close()

    # -----------------------------------------------------------------
    # R - READ (Busca por CPF)
    # -----------------------------------------------------------------

    def find_by_cpf(self, cpf: str):
        """ Busca um funcionário pelo CPF, fazendo JOIN com localizacao e tipo_funcionario. """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                # Query com JOINs para buscar todos os dados relacionados
                sql = """
                    SELECT 
                        f.cpf, f.nome, f.sobrenome, f.email, f.telefone, f.sexo, f.nome_social, f.id_tipo_funcionario, f.id_localizacao, f.senha,
                        tf.cargo AS tipo_cargo, -- ALTERADO: de 'tf.nome_social' para 'tf.cargo'
                        l.cep, l.logradouro, l.numero, l.bairro, l.cidade, l.uf, l.id_localizacao AS loc_id
                    FROM funcionario f
                    LEFT JOIN localizacao l ON f.id_localizacao = l.id_localizacao
                    LEFT JOIN tipo_funcionario tf ON f.id_tipo_funcionario = tf.id_tipo_funcionario
                    WHERE f.cpf = %s;
                """
                cur.execute(sql, (cpf,))
                row = cur.fetchone()
                if row is None: return None
                
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, row))
        except Exception as e:
            logger.error(f"Erro ao buscar funcionário {cpf}: {e}")
            return None
        finally:
            if conn: conn.close()
            
    # -----------------------------------------------------------------
    # D - DELETE (Exclusão)
    # -----------------------------------------------------------------

    def delete(self, cpf: str):
        """ Deleta o funcionário e sua localização, se existir. """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                # 1. Obter o id_localizacao antes de deletar o funcionário
                cur.execute("SELECT id_localizacao FROM funcionario WHERE cpf = %s;", (cpf,))
                result = cur.fetchone()
                id_localizacao = result[0] if result else None

                # 2. DELETE o funcionário
                cur.execute("DELETE FROM funcionario WHERE cpf = %s;", (cpf,))
                rows_deleted = cur.rowcount
                
                # 3. DELETE a localização (se existia)
                if id_localizacao:
                    cur.execute("DELETE FROM localizacao WHERE id_localizacao = %s;", (id_localizacao,))
                
                conn.commit()
                return rows_deleted
        except Exception as e:
            logger.error(f"Erro ao deletar funcionário {cpf}: {e}")
            if conn: conn.rollback()
            return 0
        finally:
            if conn: conn.close()
    # -----------------------------------------------------------------
    # U - UPDATE (Atualização)
    # -----------------------------------------------------------------
    def update(self, cpf: str, senha_hashed: str = None, nome: str = None, sobrenome: str = None, 
            email: str = None, sexo: str = None, telefone: str = None, nome_social: str = None, 
            id_tipo_funcionario: int = None, localizacao_data: dict = None):
        """ Atualiza dados do funcionário e sua localização (opcionalmente). """
        conn = None
        rows_affected_total = 0
        
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                
                # 1. Obter o id_localizacao (Necessário para a transação)
                cur.execute("SELECT id_localizacao FROM funcionario WHERE cpf = %s;", (cpf,))
                result = cur.fetchone()
                if not result:
                    return 0 # Funcionário não encontrado
                id_localizacao = result[0]
                
                
                # 2. UPDATE na tabela FUNCIONARIO
                fields_funcionario = []
                values_funcionario = []

                # Verifica quais campos do funcionário foram fornecidos para atualização
                if nome is not None: fields_funcionario.append("nome = %s"); values_funcionario.append(nome)
                if sobrenome is not None: fields_funcionario.append("sobrenome = %s"); values_funcionario.append(sobrenome)
                if email is not None: fields_funcionario.append("email = %s"); values_funcionario.append(email)
                if sexo is not None: fields_funcionario.append("sexo = %s"); values_funcionario.append(sexo)
                if telefone is not None: fields_funcionario.append("telefone = %s"); values_funcionario.append(telefone)
                if nome_social is not None: fields_funcionario.append("nome_social = %s"); values_funcionario.append(nome_social)
                if id_tipo_funcionario is not None: fields_funcionario.append("id_tipo_funcionario = %s"); values_funcionario.append(id_tipo_funcionario)
                
                # A senha só é atualizada se for fornecido o hash
                if senha_hashed:
                    fields_funcionario.append("senha = %s"); 
                    values_funcionario.append(senha_hashed)

                if fields_funcionario:
                    values_funcionario.append(cpf)
                    sql_funcionario = f"UPDATE funcionario SET {', '.join(fields_funcionario)} WHERE cpf = %s;"
                    cur.execute(sql_funcionario, tuple(values_funcionario))
                    rows_affected_total += cur.rowcount

                
                # 3. UPDATE na tabela LOCALIZACAO (se houver dados para ela)
                if localizacao_data and id_localizacao:
                    fields_localizacao = []
                    values_localizacao = []
                    
                    # Verifica campos de localização para atualização
                    if localizacao_data.get('cep') is not None: fields_localizacao.append("cep = %s"); values_localizacao.append(localizacao_data['cep'])
                    if localizacao_data.get('logradouro') is not None: fields_localizacao.append("logradouro = %s"); values_localizacao.append(localizacao_data['logradouro'])
                    if localizacao_data.get('numero') is not None: fields_localizacao.append("numero = %s"); values_localizacao.append(localizacao_data['numero'])
                    if localizacao_data.get('cidade') is not None: fields_localizacao.append("cidade = %s"); values_localizacao.append(localizacao_data['cidade'])
                    if localizacao_data.get('uf') is not None: fields_localizacao.append("uf = %s"); values_localizacao.append(localizacao_data['uf'])
                    
                    if fields_localizacao:
                        values_localizacao.append(id_localizacao)
                        sql_localizacao = f"UPDATE localizacao SET {', '.join(fields_localizacao)} WHERE id_localizacao = %s;"
                        cur.execute(sql_localizacao, tuple(values_localizacao))
                        rows_affected_total += cur.rowcount
                        
                # 4. COMMIT
                if rows_affected_total > 0:
                    conn.commit()
                    return 1 
                else:
                    return 0 

        except Exception as e:
            logger.error(f"Erro ao atualizar funcionário {cpf}: {e}")
            if conn: conn.rollback()
            return -1 
        finally:
            if conn: conn.close()