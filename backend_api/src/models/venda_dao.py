# src/models/venda_dao.py

from src.db_connection import get_db_connection
import logging
from decimal import Decimal
from src.utils.formatters import clean_only_numbers 
from src.models.fluxo_caixa_dao import FluxoCaixaDAO 
from psycopg import rows 
import psycopg 

logger = logging.getLogger(__name__)

class VendaDAO:

    def __init__(self):
        self.fluxo_caixa_dao = FluxoCaixaDAO()


    def registrar_venda(self, dados_venda: dict):
        # ... (O código registrar_venda permanece OK, pois a limpeza do CPF_FUNCIONARIO é feita no Schema)
        
        conn = get_db_connection() 
        if conn is None:
            return None
            
        id_venda = None
        valor_total = dados_venda['valor_total']
        troco_calculado = dados_venda['troco'] 
        
        try:
            with conn.cursor() as cur:
                
                # --- 1. PREPARO (Cliente) ---
                cpf_cliente = dados_venda.get('cpf_cliente') 
                id_cliente = None
                cpf_cliente_limpo = None 

                if cpf_cliente:
                    cpf_cliente_limpo = clean_only_numbers(cpf_cliente) 
                    cur.execute("SELECT id_cliente FROM cliente WHERE cpf_cnpj = %s", (cpf_cliente_limpo,))
                    cliente_result = cur.fetchone()
                    id_cliente = cliente_result[0] if cliente_result else None

                    if id_cliente is None:
                        raise ValueError(f"O Cliente com CPF/CNPJ '{cpf_cliente}' não foi encontrado no sistema.")
                
                # --- 2. PREPARO (Pagamentos) ---
                pagamento = dados_venda['pagamentos'][0]
                
                # --- 3. INSERT na Tabela VENDA (Cabeçalho Completo) ---
                venda_sql = """
                    INSERT INTO venda (
                        valor_total, 
                        cpf_cnpj_cliente, 
                        id_cliente, 
                        cpf_funcionario,
                        id_tipo_pagamento, 
                        valor_pago,
                        troco,
                        desconto
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_venda;
                """
                
                cur.execute(venda_sql, (
                    valor_total, 
                    cpf_cliente_limpo, 
                    id_cliente, 
                    dados_venda['cpf_funcionario'],
                    pagamento['id_tipo'],
                    pagamento['valor_pago'],
                    troco_calculado,
                    dados_venda.get('desconto', 0)
                ))
                id_venda = cur.fetchone()[0]
                
                
                # --- 4. INSERT na Tabela VENDA_ITEM e UPDATE no ESTOQUE ---
                
                for item in dados_venda['itens']:
                    codigo_produto = item['codigo_produto']
                    quantidade_vendida = item['quantidade_venda']
                    
                    # a. BAIXA NO ESTOQUE (UPDATE)
                    estoque_update_sql = """
                        UPDATE estoque
                        SET quantidade = quantidade - %s
                        WHERE codigo_produto = %s
                        RETURNING quantidade; 
                    """
                    cur.execute(estoque_update_sql, (quantidade_vendida, codigo_produto))
                    
                    new_quantity_result = cur.fetchone()
                    
                    if new_quantity_result is None or new_quantity_result[0] < 0:
                        raise Exception(f"Estoque insuficiente para o produto {codigo_produto}. ROLLBACK!")
                        
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


                # --- 5. REGISTRO NO FLUXO DE CAIXA (LEDGER) ---
                
                id_fluxo_aberto = self.fluxo_caixa_dao.buscar_caixa_aberto(dados_venda['cpf_funcionario'])

                if id_fluxo_aberto is None:
                    raise Exception("Caixa não está aberto para o funcionário. ROLLBACK!")

                fluxo_movimento_sql = """
                    INSERT INTO fluxo_caixa_movimento (id_fluxo, id_venda, valor, tipo)
                    VALUES (%s, %s, %s, 'ENTRADA');
                """
                cur.execute(fluxo_movimento_sql, (id_fluxo_aberto, id_venda, valor_total))


                # --- 6. COMMIT FINAL ---
                conn.commit()
                return id_venda
                
        except ValueError as ve:
            logger.error(f"Erro de validação de venda: {ve}")
            if conn:
                conn.rollback()
            return None
        
        except Exception as e:
            logger.error(f"Erro CRÍTICO na transação de venda: {e}")
            if conn:
                conn.rollback()
            raise e
            
        finally:
            if conn:
                conn.close()

    def buscar_por_id(self, id_venda: int):
        # ... (código buscar_por_id inalterado) ...
        conn = get_db_connection() 
        if conn is None: return None
        
        venda_data = {}

        try:
            # Usando rows.dict_row para o DictCursor no psycopg v3
            with conn.cursor(row_factory=rows.dict_row) as cur: 

                sql_venda = """
                    SELECT 
                        v.*, 
                        tp.descricao AS tipo_pagamento_descricao,
                        f.nome AS nome_caixa,
                        c.nome AS nome_cliente,
                        cm.cnpj AS mercado_cnpj, 
                        cm.endereco AS mercado_endereco,
                        cm.razao_social AS mercado_razao_social,
                        cm.contato AS mercado_contato
                    FROM venda v
                    LEFT JOIN tipo_pagamento tp ON v.id_tipo_pagamento = tp.id_tipo
                    LEFT JOIN funcionario f ON v.cpf_funcionario = f.cpf
                    LEFT JOIN cliente c ON v.id_cliente = c.id_cliente 
                    LEFT JOIN configuracao_mercado cm ON cm.id_config = 1 
                    WHERE v.id_venda = %s;
                """
                cur.execute(sql_venda, (id_venda,))
                venda_record = cur.fetchone()
                
                if not venda_record:
                    return None
                
                venda_data = dict(venda_record) 

                # 2. Busca os ITENS da Venda
                sql_itens = """
                    SELECT 
                        vi.codigo_produto,
                        vi.quantidade_venda,
                        vi.preco_unitario,
                        vi.valor_total AS subtotal,
                        p.nome AS nome_produto
                    FROM venda_item vi
                    JOIN produto p ON vi.codigo_produto = p.codigo_produto
                    WHERE vi.id_venda = %s;
                """
                cur.execute(sql_itens, (id_venda,))
                item_records = cur.fetchall()
                
                venda_data['itens'] = [dict(r) for r in item_records] 

                # 3. Adaptação do Pagamento para o Schema (usando os dados já recuperados)
                venda_data['pagamentos'] = [{
                    'id_tipo': venda_data['id_tipo_pagamento'],
                    'valor_pago': venda_data['valor_pago'],
                    'troco': venda_data['troco'],
                    
                    'descricao': venda_data.get('tipo_pagamento_descricao') 
                }]
                
                return venda_data
            
        except Exception as e:
            logger.error(f"Erro ao buscar venda {id_venda}: {e}")
            return None
        finally:
            if conn: conn.close()

    # -------------------------------------------------------------
    # BUSCAR VENDAS FLEXÍVEL (MÉTODO PARA LISTAGEM)
    # -------------------------------------------------------------
    def buscar_vendas_flexivel(self, data_str=None, cpf_cliente=None):
        conn = get_db_connection()
        if conn is None: return []

        vendas_list = []
        
        try:
            # Usando rows.dict_row para o DictCursor no psycopg v3
            with conn.cursor(row_factory=rows.dict_row) as cur:
                
                sql = """
                    SELECT 
                        v.*, 
                        tp.descricao AS tipo_pagamento_descricao,
                        f.nome AS nome_caixa
                    FROM venda v 
                    LEFT JOIN tipo_pagamento tp ON v.id_tipo_pagamento = tp.id_tipo
                    LEFT JOIN funcionario f ON v.cpf_funcionario = f.cpf
                """
                params = []
                where_clauses = []
                
                # Filtro 1: Data
                if data_str:
                    where_clauses.append("DATE(v.data_venda) = %s")
                    params.append(data_str)
                    
                # Filtro 2: CPF do Cliente
                if cpf_cliente:
                    # 🛑 CORREÇÃO: Filtrar pelo CPF do CLIENTE, não do funcionário
                    where_clauses.append("REGEXP_REPLACE(v.cpf_cnpj_cliente, '[^0-9]', '', 'g') = %s") 
                    params.append(cpf_cliente) 
                    
                # Constrói a cláusula WHERE
                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses) 
                    
                sql += " ORDER BY v.data_venda DESC;"
                
                cur.execute(sql, tuple(params))
                rows_fetched = cur.fetchall() 
                
                vendas_list = [dict(r) for r in rows_fetched]

                # 🛑 CORREÇÃO: Buscar ITENS e formatar PAGAMENTOS para cada venda
                # Isso é necessário porque o VendaSchema exige esses campos aninhados.
                for venda in vendas_list:
                    # 1. Buscar Itens
                    sql_itens = """
                        SELECT 
                            vi.codigo_produto,
                            vi.quantidade_venda,
                            vi.preco_unitario,
                            vi.valor_total AS subtotal,
                            p.nome AS nome_produto
                        FROM venda_item vi
                        JOIN produto p ON vi.codigo_produto = p.codigo_produto
                        WHERE vi.id_venda = %s;
                    """
                    cur.execute(sql_itens, (venda['id_venda'],))
                    item_records = cur.fetchall()
                    venda['itens'] = [dict(r) for r in item_records]

                    # 2. Formatar Pagamentos (Lista)
                    venda['pagamentos'] = [{
                        'id_tipo': venda['id_tipo_pagamento'],
                        'valor_pago': venda['valor_pago'],
                        'troco': venda['troco'],
                        'descricao': venda.get('tipo_pagamento_descricao')
                    }]
            
            return vendas_list
            
        except Exception as e:
            print(f"Erro ao buscar vendas de forma flexível: {e}")
            return []
        finally:
            if conn: conn.close()