# src/models/cliente_dao.py

from src.db_connection import get_db_connection

class ClienteDAO:
    """ 
    Data Access Object (DAO) para a entidade 'Cliente'.
    Implementa o CRUD completo usando SQL puro (psycopg v3).
    """
    
    # ------------------------------------------------
    # READ ALL
    # ------------------------------------------------
    def find_all(self):
        """ Executa SELECT de todos os clientes. """
        conn = get_db_connection()
        if conn is None: return []
        
        try:
            with conn.cursor() as cur:
                # O JOIN para listar os dados de localização junto
                sql = """
                    SELECT c.id_cliente, c.nome, c.cpf_cnpj, c.email, c.telefone, c.sexo, 
                        l.cep, l.logradouro, l.numero, l.bairro, l.cidade, l.uf
                    FROM cliente c
                    JOIN localizacao l ON c.id_localizacao = l.id_localizacao
                    ORDER BY c.id_cliente;
                """
                cur.execute(sql)
                
                column_names = [desc.name for desc in cur.description]
                clientes_data = cur.fetchall()
                clientes_list = [dict(zip(column_names, row)) for row in clientes_data]
                
                return clientes_list
                
        except Exception as e:
            print(f"Erro no ClienteDAO.find_all: {e}")
            return []
        finally:
            if conn: conn.close() 

    # ------------------------------------------------
    # CREATE (CORRIGIDO)
    # ------------------------------------------------
    def insert(self, cpf_cnpj, nome, email, telefone, sexo, localizacao_data):
        """ Insere a localização e, em seguida, o cliente na mesma transação. """
        conn = get_db_connection()
        if conn is None: return None

        try:
            with conn.cursor() as cur:
                # ------------------------------------------------
                # 1. INSERIR LOCALIZAÇÃO
                # ------------------------------------------------
                localizacao_sql = """
                    INSERT INTO localizacao 
                    (cep, logradouro, numero, bairro, cidade, uf)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_localizacao;
                """
                loc_values = (
                    localizacao_data['cep'],
                    localizacao_data.get('logradouro'),
                    localizacao_data.get('numero'),
                    localizacao_data.get('bairro'),
                    localizacao_data.get('cidade'),
                    localizacao_data.get('uf')
                )
                cur.execute(localizacao_sql, loc_values)
                id_localizacao = cur.fetchone()[0]

                # ------------------------------------------------
                # 2. INSERIR CLIENTE (Com todos os campos)
                # ------------------------------------------------
                cliente_sql = """
                    INSERT INTO cliente 
                    (cpf_cnpj, nome, email, telefone, sexo, id_localizacao) 
                    VALUES (%s, %s, %s, %s, %s, %s) 
                    RETURNING id_cliente;
                """
                # Ordem dos valores: (cpf_cnpj, nome, email, telefone, sexo, id_localizacao)
                cur.execute(cliente_sql, (cpf_cnpj, nome, email, telefone, sexo, id_localizacao))
                
                new_id = cur.fetchone()[0]
                
                conn.commit() 
                
                return new_id
                
        except Exception as e:
            if conn: conn.rollback() 
            print(f"Erro no ClienteDAO.insert (Transação): {e}")
            return None
        finally:
            if conn: conn.close()

    # ------------------------------------------------
    # READ ONE (find_by_id)
    # ------------------------------------------------
    def find_by_id(self, cliente_id):
        """ Busca um único cliente pelo id_cliente, incluindo dados de localização. """
        conn = get_db_connection()
        if conn is None: return None
        
        try:
            with conn.cursor() as cur:
                # SQL: JOIN para retornar todos os dados
                sql = """
                    SELECT c.id_cliente, c.nome, c.cpf_cnpj, c.email, c.telefone, c.sexo, 
                        l.cep, l.logradouro, l.numero, l.bairro, l.cidade, l.uf, l.id_localizacao
                    FROM cliente c
                    JOIN localizacao l ON c.id_localizacao = l.id_localizacao
                    WHERE c.id_cliente = %s;
                """
                cur.execute(sql, (cliente_id,))
                
                cliente_data = cur.fetchone() 
                
                if cliente_data:
                    column_names = [desc.name for desc in cur.description]
                    return dict(zip(column_names, cliente_data))
                else:
                    return None 
                    
        except Exception as e:
            print(f"Erro no ClienteDAO.find_by_id: {e}")
            return None
        finally:
            if conn: conn.close()

    # ------------------------------------------------
    # UPDATE (IMPLEMENTADO)
    # ------------------------------------------------
    def update(self, cliente_id, nome=None, email=None, cpf_cnpj=None, telefone=None, sexo=None, localizacao_data=None):
        """ 
        Atualiza o cliente e sua localização. 
        Retorna o número de linhas afetadas (1 se sucesso, 0 se não encontrado, -1 se erro).
        """
        conn = get_db_connection()
        if conn is None: return -1

        try:
            with conn.cursor() as cur:
                # 1. PEGAR O ID DA LOCALIZAÇÃO
                cur.execute("SELECT id_localizacao FROM cliente WHERE id_cliente = %s;", (cliente_id,))
                result = cur.fetchone()
                if not result:
                    return 0 # Cliente não encontrado
                id_localizacao = result[0]

                rows_affected_cliente = 0
                rows_affected_localizacao = 0

                # 2. UPDATE na tabela CLIENTE
                fields_cliente = []
                values_cliente = []
                
                if nome is not None:
                    fields_cliente.append("nome = %s")
                    values_cliente.append(nome)
                if email is not None:
                    fields_cliente.append("email = %s")
                    values_cliente.append(email)
                # ... (adicione aqui outros campos do cliente, como cpf_cnpj, telefone, sexo)
                if cpf_cnpj is not None:
                    fields_cliente.append("cpf_cnpj = %s")
                    values_cliente.append(cpf_cnpj)
                if telefone is not None:
                    fields_cliente.append("telefone = %s")
                    values_cliente.append(telefone)
                if sexo is not None:
                    fields_cliente.append("sexo = %s")
                    values_cliente.append(sexo)
                
                if fields_cliente:
                    values_cliente.append(cliente_id) # Adiciona o ID para a cláusula WHERE
                    sql_cliente = f"UPDATE cliente SET {', '.join(fields_cliente)} WHERE id_cliente = %s;"
                    cur.execute(sql_cliente, tuple(values_cliente))
                    rows_affected_cliente = cur.rowcount

                # 3. UPDATE na tabela LOCALIZACAO
                if localizacao_data:
                    fields_localizacao = []
                    values_localizacao = []
                    
                    # Usa get() para checar se a chave existe antes de tentar atualizar
                    if localizacao_data.get('cep') is not None:
                        fields_localizacao.append("cep = %s")
                        values_localizacao.append(localizacao_data['cep'])
                    if localizacao_data.get('logradouro') is not None:
                        fields_localizacao.append("logradouro = %s")
                        values_localizacao.append(localizacao_data['logradouro'])
                    # ... (adicione aqui outros campos de localização)
                    if localizacao_data.get('numero') is not None:
                        fields_localizacao.append("numero = %s")
                        values_localizacao.append(localizacao_data['numero'])
                    if localizacao_data.get('bairro') is not None:
                        fields_localizacao.append("bairro = %s")
                        values_localizacao.append(localizacao_data['bairro'])
                    if localizacao_data.get('cidade') is not None:
                        fields_localizacao.append("cidade = %s")
                        values_localizacao.append(localizacao_data['cidade'])
                    if localizacao_data.get('uf') is not None:
                        fields_localizacao.append("uf = %s")
                        values_localizacao.append(localizacao_data['uf'])
                    
                    if fields_localizacao:
                        values_localizacao.append(id_localizacao)
                        sql_localizacao = f"UPDATE localizacao SET {', '.join(fields_localizacao)} WHERE id_localizacao = %s;"
                        cur.execute(sql_localizacao, tuple(values_localizacao))
                        rows_affected_localizacao = cur.rowcount
                        
                # 4. COMMIT DA TRANSAÇÃO
                if rows_affected_cliente > 0 or rows_affected_localizacao > 0:
                    conn.commit()
                    return 1 # Retorna 1 se qualquer alteração ocorreu
                else:
                    return 0 # Retorna 0 se o cliente foi encontrado, mas não houve alterações.

        except Exception as e:
            if conn: conn.rollback()
            print(f"Erro no ClienteDAO.update (Transação): {e}")
            return -1
        finally:
            if conn: conn.close()
    # ------------------------------------------------
    # DELETE
    # ------------------------------------------------
    def delete(self, cliente_id):
        """ Deleta o cliente e sua localização na mesma transação. """
        conn = get_db_connection()
        if conn is None: return 0

        try:
            with conn.cursor() as cur:
                # 1. Obter o id_localizacao antes de deletar o cliente
                cur.execute("SELECT id_localizacao FROM cliente WHERE id_cliente = %s;", (cliente_id,))
                result = cur.fetchone()
                if not result:
                    return 0
                id_localizacao = result[0]

                # 2. DELETE o cliente
                cur.execute("DELETE FROM cliente WHERE id_cliente = %s;", (cliente_id,))
                rows_deleted_cliente = cur.rowcount
                
                # 3. DELETE a localização
                cur.execute("DELETE FROM localizacao WHERE id_localizacao = %s;", (id_localizacao,))
                
                conn.commit()
                
                return rows_deleted_cliente # Retorna 1 se deletou, 0 se não encontrou
                
        except Exception as e:
            if conn: conn.rollback()
            print(f"Erro no ClienteDAO.delete: {e}")
            return -1
        finally:
            if conn: conn.close()