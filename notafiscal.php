<?php
require_once BASE_PATH . '/src/config/Autoload.php';

if (!Usuario::autenticado()) {
    header('Location: ' . BASE_URL . '/login');
    exit;
}

Permissoes::exigir('vendas');

$numero_nf = $_GET['nf'] ?? '';

if (!$numero_nf) {
    header('Location: ' . BASE_URL . '/dashboard');
    exit;
}

// Buscar nota fiscal real do banco
$nf_service = new NotaFiscal();
$venda_service = new Venda();
$nf_info = $nf_service->getByNumero($numero_nf);

if (!$nf_info) {
    header('Location: ' . BASE_URL . '/dashboard');
    exit;
}

// Buscar itens da venda
$itens = $venda_service->getItens($nf_info['id_venda']);

// Formatar dados da nota fiscal
$notaFiscal = [
    'numero' => $nf_info['numero_nf'],
    'data' => date('d/m/Y H:i', strtotime($nf_info['data_emissao'])),
    'cliente' => $nf_info['cliente_nome'] ?? 'Consumidor',
    'cpf_cnpj' => $nf_info['cpf_cnpj'] ?? '-',
    'endereco' => '-',
    'itens' => array_map(function($item) {
        return [
            'descricao' => $item['produto_nome'] ?? 'Produto',
            'quantidade' => $item['quantidade_venda'],
            'valor_unit' => floatval($item['preco_unitario']),
            'total' => floatval($item['valor_total'])
        ];
    }, $itens),
    'subtotal' => floatval($nf_info['valor_total']),
    'desconto' => 0.00,
    'total' => floatval($nf_info['valor_total']),
    'pagamento' => '-',
    'troco' => 0.00,
    'vendedor' => Usuario::getUsuario()['nome'] ?? 'Sistema',
    'caixa' => 'Caixa PDV'
];

// Calcular itens totais
$totalItens = count($notaFiscal['itens']);
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Nota Fiscal - Market Coffee PDV">
    <title>Nota Fiscal <?php echo htmlspecialchars($numero_nf); ?> - Market Coffee PDV</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #f5f5f5;
            padding: 1rem;
            line-height: 1.5;
        }
        .container { max-width: 600px; margin: 0 auto; }
        .header-buttons {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            padding: 0 0 1rem 0;
            border-bottom: 2px solid #ddd;
        }
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 4px;
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        .btn-print { background: #030213; color: white; }
        .btn-print:hover { background: #1a0f2e; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
        .btn-back { background: transparent; border: 1px solid #ccc; color: #030213; }
        .btn-back:hover { background: #f5f5f5; }
        .nota-fiscal {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            max-width: 80mm;
            margin: 0 auto;
            font-size: 12px;
        }
        .header-nf {
            text-align: center;
            border-bottom: 2px solid #000;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }
        .header-nf h1 { font-size: 14px; font-weight: bold; }
        .header-nf p { font-size: 10px; margin-top: 0.25rem; }
        .nf-numero {
            text-align: center;
            font-size: 14px;
            font-weight: bold;
            margin: 1rem 0;
            border: 1px solid #000;
            padding: 0.5rem;
        }
        .info-row { display: flex; justify-content: space-between; margin-bottom: 0.25rem; }
        .label { font-weight: bold; }
        .info-section { margin-bottom: 1rem; }
        .section-title { font-weight: bold; font-size: 11px; border-bottom: 1px dashed #000; margin-bottom: 0.5rem; padding-bottom: 0.25rem; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; font-size: 11px; }
        table th { text-align: left; border-bottom: 1px solid #000; padding: 0.25rem 0; font-weight: bold; font-size: 10px; }
        table td { padding: 0.25rem 0; border-bottom: 1px dashed #999; }
        .item-desc { width: 50%; }
        .item-qty { width: 15%; text-align: center; }
        .item-valor { width: 17%; text-align: right; }
        .item-total { width: 18%; text-align: right; }
        .totais { margin: 1rem 0; }
        .total-row { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
        .total-row.grande { font-weight: bold; font-size: 13px; border-top: 2px solid #000; border-bottom: 2px solid #000; padding: 0.5rem 0; }
        .footer-info { text-align: center; font-size: 10px; margin-top: 1rem; border-top: 1px dashed #000; padding-top: 0.5rem; }
        .footer-info p { margin: 0.25rem 0; }
        .thankyou { text-align: center; font-weight: bold; margin-top: 0.75rem; font-size: 12px; }
        @media print {
            body { background: white; padding: 0; }
            .header-buttons { display: none; }
            .nota-fiscal { box-shadow: none; border: none; }
            .btn { display: none; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-buttons">
            <a href="javascript:window.print()" class="btn btn-print">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24" style="stroke: currentColor; stroke-width: 1.5; fill: none;">
                    <path d="M17 17H7m10-12H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2z"/>
                    <path d="M9 11h6"/>
                </svg>
                Imprimir / Gerar PDF
            </a>
            <a href="<?php echo BASE_URL . '/pdv'; ?>" class="btn btn-back">← Voltar</a>
        </div>

        <div class="nota-fiscal">
            <!-- Cabeçalho -->
            <div class="header-nf">
                <h1>MARKET COFFEE</h1>
                <p>CNPJ: 12.345.678/0001-99</p>
                <p>Rua Principal, 500 -Vitoria da Conquista/BA</p>
                <p>Tel: (77) 98765-4321</p>
            </div>

            <!-- Número da NF -->
            <div class="nf-numero">
                <?php echo htmlspecialchars($notaFiscal['numero']); ?>
            </div>

            <!-- Informações da Venda -->
            <div class="info-section">
                <div class="section-title">INFORMAÇÕES DA VENDA</div>
                <div class="info-row">
                    <span class="label">Data/Hora:</span>
                    <span><?php echo htmlspecialchars($notaFiscal['data']); ?></span>
                </div>
                <div class="info-row">
                    <span class="label">Vendedor:</span>
                    <span><?php echo htmlspecialchars($notaFiscal['vendedor']); ?></span>
                </div>
                <div class="info-row">
                    <span class="label">Caixa:</span>
                    <span><?php echo htmlspecialchars($notaFiscal['caixa']); ?></span>
                </div>
            </div>

            <!-- Dados do Cliente -->
            <div class="info-section">
                <div class="section-title">CLIENTE</div>
                <div class="info-row">
                    <span class="label">Nome:</span>
                    <span><?php echo htmlspecialchars($notaFiscal['cliente']); ?></span>
                </div>
                <div class="info-row">
                    <span class="label">CPF/CNPJ:</span>
                    <span><?php echo htmlspecialchars($notaFiscal['cpf_cnpj']); ?></span>
                </div>
                <div class="info-row" style="flex-direction: column;">
                    <span class="label">Endereço:</span>
                    <span><?php echo htmlspecialchars($notaFiscal['endereco']); ?></span>
                </div>
            </div>

            <!-- Itens da Nota -->
            <div class="info-section">
                <div class="section-title">ITENS</div>
                <table>
                    <thead>
                        <tr>
                            <th class="item-desc">Descrição</th>
                            <th class="item-qty">Qtd</th>
                            <th class="item-valor">Valor</th>
                            <th class="item-total">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($notaFiscal['itens'] as $item): ?>
                        <tr>
                            <td class="item-desc"><?php echo htmlspecialchars($item['descricao']); ?></td>
                            <td class="item-qty"><?php echo $item['quantidade']; ?></td>
                            <td class="item-valor">R$ <?php echo number_format($item['valor_unit'], 2, ',', '.'); ?></td>
                            <td class="item-total">R$ <?php echo number_format($item['total'], 2, ',', '.'); ?></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>

            <!-- Totais -->
            <div class="totais">
                <div class="total-row">
                    <span>Subtotal:</span>
                    <span>R$ <?php echo number_format($notaFiscal['subtotal'], 2, ',', '.'); ?></span>
                </div>
                <?php if ($notaFiscal['desconto'] > 0): ?>
                <div class="total-row">
                    <span>Desconto:</span>
                    <span>-R$ <?php echo number_format($notaFiscal['desconto'], 2, ',', '.'); ?></span>
                </div>
                <?php endif; ?>
                <div class="total-row grande">
                    <span>TOTAL:</span>
                    <span>R$ <?php echo number_format($notaFiscal['total'], 2, ',', '.'); ?></span>
                </div>
            </div>

            <!-- Formas de Pagamento -->
            <div class="info-section">
                <div class="section-title">PAGAMENTO</div>
                <div class="info-row">
                    <span class="label">Forma:</span>
                    <span><?php echo htmlspecialchars($notaFiscal['pagamento']); ?></span>
                </div>
                <?php if ($notaFiscal['troco'] > 0): ?>
                <div class="info-row">
                    <span class="label">Troco:</span>
                    <span>R$ <?php echo number_format($notaFiscal['troco'], 2, ',', '.'); ?></span>
                </div>
                <?php endif; ?>
            </div>

            <!-- Rodapé -->
            <div class="footer-info">
                <p>Obrigado pela compra!</p>
                <p>Volte sempre a Market Coffee</p>
                <p style="margin-top: 0.5rem; font-size: 9px;">Consumidor, exija sua nota fiscal</p>
            </div>

            <div class="thankyou">
                ♦ ♦ ♦ FIM DO CUPOM ♦ ♦ ♦
            </div>
        </div>
    </div>

    <script>
        // Auto-print quando carrega em modo especial
        if (window.location.hash === '#autoprint') {
            window.addEventListener('load', function() {
                setTimeout(window.print, 500);
            });
        }
    </script>
</body>
</html>
