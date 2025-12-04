# src/models/cupom_dao.py (CÓDIGO FINAL E FUNCIONAL)

import datetime
import logging
from src.db_connection import get_db_connection

logger = logging.getLogger(__name__)

class CupomDAO:

    # 🛑 CORREÇÃO AQUI: cpf_cliente removido da definição do argumento
    def create_cupom(self, cpf_caixa: str, numero_nf: str, itens_vendidos: list, 
                    condicao_pagamento: str, valor_pago: float,
                    id_cliente: int = None): # 🛑 cpf_cliente removido daqui
        """
        Cria o cupom de venda e todos os itens da transação em uma única transação atômica.
        :param cpf_caixa: CPF do funcionário (string).
        :returns: id_cupom (PK do cupom) se sucesso, None se falha.
        """
        conn = get_db_connection()
        if conn is None:
            logger.error("Falha ao obter conexão com o banco de dados.")
            return None
        
        try:
            # 1. Cálculos Essenciais
            valor_total = sum(item['quantidade'] * item['preco_unitario'] for item in itens_vendidos)
            troco = max(0, valor_pago - valor_total) if condicao_pagamento.upper() == 'DINHEIRO' else 0

            # 2. INSERE O CABEÇALHO DO CUPOM
            # 🛑 CORREÇÃO AQUI: cpf_cliente removido do INSERT
            sql_cupom = """
            INSERT INTO cupom (
                numero_nf, data_emissao, valor_total, cpf_caixa, id_cliente, 
                condicao_pagamento, valor_pago, troco, status, id_venda
            )
            VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s, 'EMITIDA', %s) 
            RETURNING id_cupom;
            """
            
            cur = conn.cursor()
            cur.execute(sql_cupom, (
                numero_nf, valor_total, cpf_caixa, id_cliente, 
                condicao_pagamento, valor_pago, troco, numero_nf
            ))
            id_cupom = cur.fetchone()[0]
            
            # 3. INSERE OS ITENS DO CUPOM (sem alterações)
            sql_itens = """
            INSERT INTO item_cupom (id_cupom, codigo_produto, quantidade, preco_unitario)
            VALUES (%s, %s, %s, %s);
            """
            
            itens_data = []
            for item in itens_vendidos:
                itens_data.append((
                    id_cupom,
                    item['codigo_produto'], 
                    item['quantidade'],
                    item['preco_unitario']
                ))

            cur.executemany(sql_itens, itens_data)

            conn.commit()
            return id_cupom
            
        except Exception as e:
            logger.error(f"Erro ao criar Cupom {numero_nf}: {e}")
            if conn: conn.rollback()
            raise # Propaga a exceção para o teste 'empty_items_fails'
        finally:
            if conn: conn.close()
            
    def get_cupom_details_by_id(self, id_cupom: int) -> dict:
        
        conn = get_db_connection()
        if conn is None:
            logger.error("Falha ao obter conexão com o banco de dados.")
            return None
        
        cupom_details = None
        
        try:
            with conn.cursor() as cur:
                
                # 1. CONSULTA PRINCIPAL: Busca o cabeçalho, Caixa, Cliente e Mercado (dados únicos)
                # 🛑 CORREÇÃO AQUI: Removendo 'c.cpf_cliente' do SELECT
                sql_header = """
                    SELECT 
                        c.numero_nf, c.data_emissao, c.valor_total, c.condicao_pagamento, c.valor_pago, c.troco,
                        f.nome AS nome_caixa, f.cpf AS cpf_caixa_fk,
                        cl.nome AS nome_cliente, NULL AS cpf_informado, -- 🛑 Retorna NULL para cpf_informado
                        cm.cnpj, cm.razao_social, cm.endereco, cm.contato
                    FROM cupom c
                    LEFT JOIN funcionario f ON c.cpf_caixa = f.cpf  
                    LEFT JOIN cliente cl ON c.id_cliente = cl.id_cliente
                    LEFT JOIN configuracao_mercado cm ON cm.id_config = 1 
                    WHERE c.id_cupom = %s;
                """
                cur.execute(sql_header, (id_cupom,))
                header_row = cur.fetchone()
                
                if not header_row:
                    return None
                
                header_cols = [desc[0] for desc in cur.description]
                cupom_details = dict(zip(header_cols, header_row))

                # 2. CONSULTA SECUNDÁRIA: Itens da Venda (sem alterações)
                sql_itens = """
                    SELECT
                        ic.quantidade, ic.preco_unitario,
                        p.nome AS nome_produto, p.codigo_produto
                    FROM item_cupom ic
                    JOIN produto p ON ic.codigo_produto = p.codigo_produto
                    WHERE ic.id_cupom = %s;
                """
                cur.execute(sql_itens, (id_cupom,))
                item_rows = cur.fetchall()
                
                item_cols = [desc[0] for desc in cur.description]
                cupom_details['itens'] = [dict(zip(item_cols, row)) for row in item_rows]
                
            return cupom_details
            
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes do cupom {id_cupom}: {e}")
            return None
        finally:
            if conn: conn.close()