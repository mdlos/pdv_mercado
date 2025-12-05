# src/services/fluxo_caixa_service.py (CÓDIGO FINAL E CORRIGIDO)

from src.models.fluxo_caixa_dao import FluxoCaixaDAO
from src.models.venda_dao import VendaDAO 
from decimal import Decimal
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FluxoCaixaService:
    
    def __init__(self):
        self.fluxo_dao = FluxoCaixaDAO()
        self.venda_dao = VendaDAO() 

    def obter_relatorio_caixas_fechados(self):
        # ... (Mantido inalterado)
        pass 
    
    def gerar_resumo_fechamento(self, id_fluxo: int) -> dict | None:
        """
        Gera o relatório analítico e o cálculo do saldo teórico do caixa.
        """
        dados_caixa = self.fluxo_dao.buscar_por_id(id_fluxo)
        if not dados_caixa:
            return None

        saldo_inicial = dados_caixa.get('saldo_inicial', Decimal('0.00')) 
        
        resumo_financeiro = self.fluxo_dao.buscar_resumo_pagamentos_por_fluxo(id_fluxo)
        
        resumo_pagamentos = resumo_financeiro['resumo_pagamentos']
        total_cancelado = resumo_financeiro['total_cancelado']

        # Cálculo do Total Arrecadado
        total_arrecadado_aprovado = Decimal('0.00')
        total_dinheiro_arrecadado = Decimal('0.00')
        
        for item in resumo_pagamentos:
            valor = item['total_arrecadado']
            total_arrecadado_aprovado += valor
            if item['id_tipo'] == 1: 
                total_dinheiro_arrecadado = valor
        
        # Cálculo do Saldo Teórico e Movimentação Líquida
        movimento_liquido = total_arrecadado_aprovado - total_cancelado
        saldo_teorico = saldo_inicial + movimento_liquido

        # Compilação do Relatório Final
        relatorio = {
            "id_fluxo": id_fluxo,
            "nome_operador": dados_caixa.get('nome_operador', 'Operador Não Encontrado'), 
            "data_abertura": dados_caixa.get('data_hora_abertura'),
            "data_fechamento": dados_caixa.get('data_hora_fechamento'), 
            "saldo_inicial": saldo_inicial, 
            
            "saldo_teorico": movimento_liquido, 
            
            "valor_total_movimentacao": movimento_liquido + total_cancelado, 
            "total_vendas_canceladas": total_cancelado,
            "resumo_analitico": resumo_pagamentos
            
        }
        
        return relatorio