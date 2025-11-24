# src/services/fluxo_caixa_service.py

from src.models.fluxo_caixa_dao import FluxoCaixaDAO
from src.models.venda_dao import VendaDAO # Futuramente usado para buscar vendas no período
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class FluxoCaixaService:
    def __init__(self):
        self.fluxo_dao = FluxoCaixaDAO()
        self.venda_dao = VendaDAO() # Instancia o DAO de venda
        # Nota: O VendaDAO precisaria de um método para calcular o total de vendas em um período.

    def obter_relatorio_caixas_fechados(self):
        """
        Gera um relatório de caixas fechados com cálculo de movimentação e diferença.
        """
        caixas = self.fluxo_dao.buscar_todos_fechados()
        relatorio = []
        
        for caixa in caixas:
            try:
                saldo_inicial = Decimal(str(caixa['saldo_inicial']))
                saldo_final_informado = Decimal(str(caixa['saldo_final_informado']))
                
                # ATENÇÃO: Esta é a parte que simula a movimentação de caixa.
                # Em um projeto real, você chamaria: self.venda_dao.calcular_movimentacao_do_periodo(...)
                
                # Simulação para demonstrar a lógica:
                # Movimentação Líquida = (Total de Vendas no período - Total de Saídas)
                # Vamos assumir que a movimentação líquida calculada foi 250.00
                movimento_liquido = Decimal(250.00) 
                
                # Cálculo da Auditoria
                saldo_esperado = saldo_inicial + movimento_liquido
                diferenca = saldo_final_informado - saldo_esperado
                
                # Adiciona os resultados ao dicionário
                caixa['movimentacao_liquida'] = movimento_liquido.to_eng_string()
                caixa['saldo_esperado'] = saldo_esperado.to_eng_string()
                caixa['diferenca_caixa'] = diferenca.to_eng_string()
                
                relatorio.append(caixa)
                
            except Exception as e:
                logger.error(f"Erro ao calcular movimentação para o caixa {caixa.get('id_fluxo')}: {e}")
                continue # Pula para o próximo registro
                
        return relatorio