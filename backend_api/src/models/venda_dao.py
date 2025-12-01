# src/models/venda_dao.py (VERSÃO FINAL E FUNCIONAL PARA TESTES)

from src.db_connection import get_db_connection
import logging
from decimal import Decimal
from src.utils.formatters import clean_only_numbers 
# Importa o FluxoCaixaDAO para buscar o ID da sessão aberta
from src.models.fluxo_caixa_dao import FluxoCaixaDAO 
# Importar exceções específicas do Psycopg (opcional, mas bom para clareza)
# from psycopg.errors import CheckViolation, UniqueViolation 

logger = logging.getLogger(__name__)

class VendaDAO:

    def __init__(self):
        self.fluxo_caixa_dao = FluxoCaixaDAO()


    def registrar_venda(self, dados_venda: dict):
        """
        Executa a transação atômica completa da venda (INSERT VENDA, ITENS, BAIXA ESTOQUE)
        e registra a ENTRADA na tabela FLUXO_CAIXA_MOVIMENTO.
        """
        conn = get_db_connection() 
        if conn is None:
            return None
            
        id_venda = None
        valor_total = dados_venda['valor_total']
        # Troco já vem calculado e validado do Schema
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
                # Usaremos os dados do primeiro pagamento para popular as colunas da tabela 'venda'
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
                        troco
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_venda;
                """
                
                cur.execute(venda_sql, (
                    valor_total, 
                    cpf_cliente_limpo, 
                    id_cliente, 
                    dados_venda['cpf_funcionario'],
                    pagamento['id_tipo'],
                    pagamento['valor_pago'],
                    troco_calculado
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
                    # NOTA: O erro CheckViolation do DB será capturado pelo bloco 'except Exception' abaixo
                    cur.execute(estoque_update_sql, (quantidade_vendida, codigo_produto))
                    
                    new_quantity_result = cur.fetchone()
                    
                    # Embora o DB já previna o valor negativo (CheckViolation), esta é a lógica segura
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
                
                # 5a. Busca o ID da sessão de caixa aberta
                id_fluxo_aberto = self.fluxo_caixa_dao.buscar_caixa_aberto(dados_venda['cpf_funcionario'])

                if id_fluxo_aberto is None:
                    # 🛑 EXCEÇÃO PARA O TESTE 01
                    raise Exception("Caixa não está aberto para o funcionário. ROLLBACK!")

                # 5b. Insere na tabela de MOVIMENTO, usando o ID do fluxo.
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
            # 🛑 CORREÇÃO CRÍTICA AQUI: Propaga a exceção para que o Pytest a capture
            logger.error(f"Erro CRÍTICO na transação de venda: {e}")
            if conn:
                conn.rollback()
            raise e # 🛑 ESSENCIAL para os testes 01 e 03
            
        finally:
            if conn:
                conn.close()

    # -------------------------------------------------------------
    # BUSCAR POR ID (Nota / ID da Venda)
    # -------------------------------------------------------------
    def buscar_por_id(self, id_venda: int):
        """ Busca uma venda, seus itens e pagamentos. """
        conn = get_db_connection()
        if conn is None: return None

        try:
            with conn.cursor() as cur:
                # 1. Busca os dados da VENDA principal (inclui os novos campos)
                cur.execute("""
                    SELECT 
                        v.*, 
                        tp.descricao AS tipo_pagamento_descricao
                    FROM venda v 
                    LEFT JOIN tipo_pagamento tp ON v.id_tipo_pagamento = tp.id_tipo
                    WHERE v.id_venda = %s
                """, (id_venda,))
                venda_record = cur.fetchone()
                if not venda_record:
                    return None
                
                venda_columns = [desc[0] for desc in cur.description]
                venda_data = dict(zip(venda_columns, venda_record))

                # 2. Busca os ITENS da Venda
                cur.execute("SELECT * FROM venda_item WHERE id_venda = %s", (id_venda,))
                item_records = cur.fetchall()
                item_columns = [desc[0] for desc in cur.description]
                venda_data['itens'] = [dict(zip(item_columns, r)) for r in item_records]

                # 3. Adaptação do Pagamento para o Schema
                venda_data['pagamentos'] = [{
                    'id_tipo': venda_data['id_tipo_pagamento'],
                    'valor_pago': venda_data['valor_pago'],
                    'troco': venda_data['troco'],
                    'descricao': venda_data['tipo_pagamento_descricao'] 
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
        """ 
        Retorna vendas filtrando por data (YYYY-MM-DD) OU CPF do cliente.
        """
        conn = get_db_connection()
        if conn is None: return []

        try:
            with conn.cursor() as cur:
                sql = "SELECT v.*, tp.descricao AS tipo_pagamento_descricao FROM venda v LEFT JOIN tipo_pagamento tp ON v.id_tipo_pagamento = tp.id_tipo "
                params = []
                where_clauses = []
                
                # Filtro 1: Data
                if data_str:
                    where_clauses.append("DATE(v.data_venda) = %s")
                    params.append(data_str)
                    
                # Filtro 2: CPF do Cliente
                if cpf_cliente:
                    # Usando a coluna real: cpf_cnpj_cliente
                    where_clauses.append("v.cpf_cnpj_cliente = %s") 
                    params.append(clean_only_numbers(cpf_cliente))
                    
                # Constrói a cláusula WHERE
                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses) 
                    
                sql += " ORDER BY v.data_venda DESC;"
                
                cur.execute(sql, tuple(params))
                rows = cur.fetchall()
                
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"Erro ao buscar vendas de forma flexível: {e}")
            return []
        finally:
            if conn: conn.close()