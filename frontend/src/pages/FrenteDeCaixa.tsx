import { useState, useEffect } from 'react';
import HeaderPDV from "../shared/components/HeaderPDV";
import {
  Box, Paper, TextField, Button, Typography, Autocomplete, Table,
  TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton,
  InputAdornment, Chip, Dialog, DialogTitle, DialogContent, DialogActions,
  FormControl, FormLabel, RadioGroup, FormControlLabel, Radio, Divider,
  CircularProgress
} from "@mui/material";
import AddShoppingCartIcon from '@mui/icons-material/AddShoppingCart';
import DeleteIcon from '@mui/icons-material/Delete';
import LocalOfferIcon from '@mui/icons-material/LocalOffer';
import PersonIcon from '@mui/icons-material/Person';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import CreditCardIcon from '@mui/icons-material/CreditCard';
import QrCodeIcon from '@mui/icons-material/QrCode';
import ReceiptIcon from '@mui/icons-material/Receipt';

// Serviços API
import {
  ProdutoService, type IDetalheProduto,
  ClienteService, type IDetalheCliente,
  VendaService, type IVenda
} from '../shared/services/services/api';

interface IItemCarrinho {
  id: number;
  produto: IDetalheProduto;
  quantidade: number;
}

type FormaPagamento = 'dinheiro' | 'debito' | 'credito' | 'pix' | 'promissoria';

const FrenteDeCaixa = () => {
  // Estados do Carrinho e Venda
  const [produtosLista, setProdutosLista] = useState<IDetalheProduto[]>([]);
  const [produtoSelecionado, setProdutoSelecionado] = useState<IDetalheProduto | null>(null);
  const [quantidade, setQuantidade] = useState<number>(1);
  const [carrinho, setCarrinho] = useState<IItemCarrinho[]>([]);
  const [desconto, setDesconto] = useState<string>('');
  const [isLoadingProdutos, setIsLoadingProdutos] = useState(false);

  // Estados do Cliente
  const [cpfBusca, setCpfBusca] = useState('');
  const [clienteIdentificado, setClienteIdentificado] = useState<IDetalheCliente | null>(null);
  const [isLoadingCliente, setIsLoadingCliente] = useState(false);

  // Estados do Pagamento
  const [openPagamento, setOpenPagamento] = useState(false);
  const [formaPagamento, setFormaPagamento] = useState<FormaPagamento>('dinheiro');
  const [valorRecebido, setValorRecebido] = useState<string>('');
  const [parcelas, setParcelas] = useState<number>(1);
  const [isSavingVenda, setIsSavingVenda] = useState(false);

  // Carregar produtos iniciais
  useEffect(() => {
    setIsLoadingProdutos(true);
    ProdutoService.getAll(1, '')
      .then((result) => {
        if (result instanceof Error) {
          alert(result.message);
        } else {
          setProdutosLista(result.data);
        }
      })
      .finally(() => setIsLoadingProdutos(false));
  }, []);

  // Funções de Carrinho
  const handleAdicionarAoCarrinho = () => {
    if (produtoSelecionado && quantidade > 0) {
      const novoItem: IItemCarrinho = {
        id: Date.now(),
        produto: produtoSelecionado,
        quantidade: quantidade
      };
      setCarrinho(prev => [...prev, novoItem]);
      setProdutoSelecionado(null);
      setQuantidade(1);
    }
  };

  const handleRemoverItem = (idItem: number) => {
    setCarrinho(prev => prev.filter(item => item.id !== idItem));
  };

  // Cálculos
  const calcularSubtotal = () => carrinho.reduce((acc, item) => acc + (item.produto.preco_venda * item.quantidade), 0);

  const calcularTotalFinal = () => {
    const subtotal = calcularSubtotal();
    const valorDesconto = parseFloat(desconto) || 0;
    return Math.max(0, subtotal - valorDesconto);
  };

  const calcularTroco = () => {
    const total = calcularTotalFinal();
    const valorLimpo = valorRecebido.replace(',', '.');
    const recebido = parseFloat(valorLimpo) || 0;
    return Math.max(0, recebido - total);
  };

  // Funções de Cliente
  const handleBuscarCliente = () => {
    setIsLoadingCliente(true);
    // Tenta buscar na lista geral primeiro (ideal seria endpoint específico de busca por CPF)
    ClienteService.getAll()
      .then((result) => {
        if (result instanceof Error) {
          alert(result.message);
        } else {
          const cpfLimpoBusca = cpfBusca.replace(/\D/g, '');
          const clienteEncontrado = result.data.find(c => c.cpf_cnpj.replace(/\D/g, '') === cpfLimpoBusca);

          if (clienteEncontrado) {
            setClienteIdentificado(clienteEncontrado);
            setCpfBusca('');
          } else {
            alert('Cliente não encontrado!');
            setClienteIdentificado(null);
          }
        }
      })
      .finally(() => setIsLoadingCliente(false));
  };

  const handleRemoverCliente = () => setClienteIdentificado(null);

  // Funções de Pagamento
  const handleAbrirPagamento = () => {
    if (carrinho.length === 0) {
      alert("Adicione itens ao carrinho antes de finalizar.");
      return;
    }
    setValorRecebido(calcularTotalFinal().toFixed(2));
    setOpenPagamento(true);
  };

  const handleFinalizarVenda = () => {
    if (formaPagamento === 'promissoria' && !clienteIdentificado) {
      alert("Para pagamento em Promissória, é necessário identificar o cliente.");
      return;
    }

    let valorRecebidoFloat = 0;
    if (formaPagamento === 'dinheiro') {
      const valorLimpo = valorRecebido.replace(',', '.');
      valorRecebidoFloat = parseFloat(valorLimpo);

      const total = calcularTotalFinal();

      if (isNaN(valorRecebidoFloat) || valorRecebidoFloat < total) {
        alert(`Valor recebido insuficiente. Total: R$ ${total.toFixed(2)}`);
        return;
      }
    }

    setIsSavingVenda(true);

    const dadosVenda: Omit<IVenda, 'id_venda'> = {
      data_venda: new Date().toISOString(),
      id_cliente: clienteIdentificado?.id_cliente || null,
      valor_total: calcularTotalFinal(),
      itens: carrinho.map(item => ({
        id_produto: item.produto.id_produto,
        quantidade: item.quantidade,
        valor_unitario: item.produto.preco_venda
      })),
      pagamento: {
        forma_pagamento: formaPagamento,
        parcelas: formaPagamento === 'credito' ? parcelas : 1,
        valor_recebido: formaPagamento === 'dinheiro' ? valorRecebidoFloat : undefined,
        troco: formaPagamento === 'dinheiro' ? (valorRecebidoFloat - calcularTotalFinal()) : undefined
      }
    };

    VendaService.create(dadosVenda)
      .then((result) => {
        if (result instanceof Error) {
          alert(result.message);
        } else {
          alert(`Venda ${result} realizada com sucesso!`);
          // Resetar tudo
          setCarrinho([]);
          setDesconto('');
          setClienteIdentificado(null);
          setOpenPagamento(false);
          setFormaPagamento('dinheiro');
          setValorRecebido('');
          setParcelas(1);
        }
      })
      .finally(() => setIsSavingVenda(false));
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden', backgroundColor: '#f5f5f5' }}>
      <HeaderPDV />

      <Box sx={{ backgroundColor: 'var(--background-color)', marginTop: '100px', padding: 2, flex: 1, overflow: 'hidden', display: 'flex', gap: 2 }}>

        {/* Painel Esquerdo (Busca e Cliente) */}
        <Paper elevation={3} sx={{ p: 3, width: '35%', display: 'flex', flexDirection: 'column', gap: 3, overflowY: 'auto' }}>

          {/* Cliente */}
          <Box sx={{ pb: 2, borderBottom: '1px solid #eee' }}>
            <Typography variant="h6" fontWeight="bold" color="primary" gutterBottom>
              Identificação do Cliente
            </Typography>
            {clienteIdentificado ? (
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', bgcolor: '#e8f5e9', p: 2, borderRadius: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircleIcon color="success" />
                  <Box>
                    <Typography variant="subtitle2" fontWeight="bold">{clienteIdentificado.nome}</Typography>
                    <Typography variant="caption">{clienteIdentificado.cpf_cnpj}</Typography>
                  </Box>
                </Box>
                <IconButton size="small" onClick={handleRemoverCliente} color="error">
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Box>
            ) : (
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  label="CPF do Cliente"
                  size="small"
                  fullWidth
                  value={cpfBusca}
                  onChange={(e) => setCpfBusca(e.target.value)}
                  placeholder="000.000.000-00"
                  InputProps={{ startAdornment: (<InputAdornment position="start"><PersonIcon /></InputAdornment>) }}
                />
                <Button variant="outlined" onClick={handleBuscarCliente} disabled={isLoadingCliente}>
                  {isLoadingCliente ? <CircularProgress size={24} /> : 'Buscar'}
                </Button>
              </Box>
            )}
          </Box>

          {/* Produto */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Typography variant="h6" fontWeight="bold" color="primary">
              Adicionar Produto
            </Typography>

            <Autocomplete
              options={produtosLista}
              loading={isLoadingProdutos}
              getOptionLabel={(option) => `${option.codigo_barras} - ${option.nome}`}
              value={produtoSelecionado}
              onChange={(_, newValue) => setProdutoSelecionado(newValue)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Pesquisar Produto"
                  placeholder="Nome ou Código"
                  fullWidth
                  InputProps={{
                    ...params.InputProps,
                    endAdornment: (
                      <>
                        {isLoadingProdutos ? <CircularProgress color="inherit" size={20} /> : null}
                        {params.InputProps.endAdornment}
                      </>
                    ),
                  }}
                />
              )}
              noOptionsText="Nenhum produto encontrado"
            />

            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Quantidade"
                type="number"
                value={quantidade}
                onChange={(e) => setQuantidade(Number(e.target.value))}
                fullWidth
                InputProps={{ inputProps: { min: 1 } }}
              />
              <TextField
                label="Preço Unitário"
                value={produtoSelecionado ? `R$ ${produtoSelecionado.preco_venda.toFixed(2)}` : ''}
                disabled
                fullWidth
              />
            </Box>

            <Button
              variant="contained"
              color="primary"
              fullWidth
              size="large"
              startIcon={<AddShoppingCartIcon />}
              onClick={handleAdicionarAoCarrinho}
              disabled={!produtoSelecionado}
              sx={{ height: '50px' }}
            >
              ADICIONAR ITEM
            </Button>
          </Box>

          {/* Desconto */}
          <Box sx={{ mt: 'auto', pt: 2, borderTop: '1px solid #eee' }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              Opções da Venda
            </Typography>
            <TextField
              label="Desconto Total (R$)"
              type="number"
              value={desconto}
              onChange={(e) => setDesconto(e.target.value)}
              fullWidth
              InputProps={{ startAdornment: (<InputAdornment position="start"><LocalOfferIcon color="action" /></InputAdornment>) }}
            />
          </Box>
        </Paper>

        {/* Painel Direito (Lista e Totais) */}
        <Paper elevation={3} sx={{ p: 0, flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <Box sx={{ p: 2, bgcolor: 'var(--principal-color)', color: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6" fontWeight="bold">Lista de Itens</Typography>
            {clienteIdentificado && (
              <Chip icon={<PersonIcon sx={{ color: '#fff !important' }} />} label={`Cliente: ${clienteIdentificado.nome}`} sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: '#fff' }} />
            )}
          </Box>

          <TableContainer sx={{ flex: 1, overflowY: 'auto' }}>
            <Table stickyHeader size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Item</TableCell>
                  <TableCell>Código</TableCell>
                  <TableCell>Produto</TableCell>
                  <TableCell align="right">Qtd</TableCell>
                  <TableCell align="right">Unitário</TableCell>
                  <TableCell align="right">Total</TableCell>
                  <TableCell align="center">Ação</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {carrinho.map((item, index) => (
                  <TableRow key={item.id} hover>
                    <TableCell>{index + 1}</TableCell>
                    <TableCell>{item.produto.codigo_barras}</TableCell>
                    <TableCell>{item.produto.nome}</TableCell>
                    <TableCell align="right">{item.quantidade}</TableCell>
                    <TableCell align="right">R$ {item.produto.preco_venda.toFixed(2)}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>R$ {(item.produto.preco_venda * item.quantidade).toFixed(2)}</TableCell>
                    <TableCell align="center">
                      <IconButton size="small" color="error" onClick={() => handleRemoverItem(item.id)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
                {carrinho.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                      <Typography variant="body1" color="textSecondary">Nenhum item adicionado ao carrinho.</Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Rodapé Totais e Botão Finalizar */}
          <Box sx={{ p: 2, bgcolor: 'var(--background-color-secondary)', borderTop: '1px solid #ddd' }}>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <Box sx={{ flex: 1 }}>
                <Button
                  variant="contained"
                  color="success"
                  size="large"
                  fullWidth
                  sx={{ height: '60px', fontSize: '1.2rem' }}
                  onClick={handleAbrirPagamento}
                  disabled={carrinho.length === 0}
                >
                  FINALIZAR VENDA
                </Button>
              </Box>
              <Box sx={{ flex: 1, textAlign: 'right' }}>
                <Typography variant="body2">Subtotal: <strong>R$ {calcularSubtotal().toFixed(2)}</strong></Typography>
                <Typography variant="body2" color="error">Desconto: <strong>- R$ {parseFloat(desconto || '0').toFixed(2)}</strong></Typography>
                <Typography variant="h4" color="primary" fontWeight="bold">R$ {calcularTotalFinal().toFixed(2)}</Typography>
              </Box>
            </Box>
          </Box>
        </Paper>
      </Box>

      {/* Modal de Pagamento */}
      <Dialog
        open={openPagamento}
        onClose={() => setOpenPagamento(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { minHeight: '50vh', maxHeight: '90vh' }
        }}
      >
        <DialogTitle sx={{ bgcolor: 'primary.main', color: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          Finalizar Pagamento
        </DialogTitle>

        <DialogContent dividers sx={{ mt: 0, p: 3 }}>
          <Box sx={{ mb: 3, textAlign: 'center' }}>
            <Typography variant="h6" color="textSecondary">Total a Pagar</Typography>
            <Typography variant="h3" color="primary" fontWeight="bold">
              R$ {calcularTotalFinal().toFixed(2)}
            </Typography>
          </Box>

          <Divider sx={{ mb: 3 }} />

          <FormControl component="fieldset" fullWidth>
            <FormLabel component="legend" sx={{ mb: 1, fontWeight: 'bold' }}>Selecione a Forma de Pagamento:</FormLabel>
            <RadioGroup
              row
              value={formaPagamento}
              onChange={(e) => setFormaPagamento(e.target.value as FormaPagamento)}
              sx={{ justifyContent: 'center', gap: 2, mb: 2 }}
            >
              <FormControlLabel value="dinheiro" control={<Radio />} label="Dinheiro" />
              <FormControlLabel value="debito" control={<Radio />} label="Débito" />
              <FormControlLabel value="credito" control={<Radio />} label="Crédito" />
              <FormControlLabel value="pix" control={<Radio />} label="Pix" />
              <FormControlLabel value="promissoria" control={<Radio />} label="Promissória" />
            </RadioGroup>
          </FormControl>

          <Box sx={{ mt: 2, p: 3, bgcolor: '#f5f5f5', borderRadius: 2, minHeight: '150px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            {formaPagamento === 'dinheiro' && (
              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  label="Valor Recebido (R$)"
                  fullWidth
                  type="text"
                  value={valorRecebido}
                  onChange={(e) => setValorRecebido(e.target.value)}
                  InputProps={{ startAdornment: <InputAdornment position="start"><AttachMoneyIcon /></InputAdornment> }}
                  autoFocus
                />
                <TextField
                  label="Troco"
                  fullWidth
                  value={`R$ ${calcularTroco().toFixed(2)}`}
                  disabled
                  sx={{ input: { color: 'green', fontWeight: 'bold', fontSize: '1.2rem' } }}
                />
              </Box>
            )}

            {formaPagamento === 'credito' && (
              <TextField
                label="Número de Parcelas"
                type="number"
                fullWidth
                value={parcelas}
                onChange={(e) => setParcelas(Number(e.target.value))}
                InputProps={{ inputProps: { min: 1, max: 12 } }}
                helperText="Juros podem ser aplicados dependendo da bandeira."
              />
            )}

            {formaPagamento === 'pix' && (
              <Box sx={{ textAlign: 'center', py: 1 }}>
                <QrCodeIcon sx={{ fontSize: 60, color: 'primary.main', mb: 1 }} />
                <Typography variant="body1" fontWeight="bold">Aguardando leitura do QR Code...</Typography>
              </Box>
            )}

            {formaPagamento === 'promissoria' && (
              <Box sx={{ textAlign: 'center', py: 1 }}>
                <ReceiptIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                <Typography variant="body1">
                  Venda na conta de: <strong>{clienteIdentificado?.nome || '...'}</strong>
                </Typography>
                {!clienteIdentificado ? (
                  <Typography variant="caption" color="error" display="block" sx={{ mt: 1 }}>
                    ERRO: Selecione um cliente antes de finalizar.
                  </Typography>
                ) : (
                  <Typography variant="caption" color="success.main" display="block" sx={{ mt: 1 }}>
                    Cliente identificado. Pronto para finalizar.
                  </Typography>
                )}
              </Box>
            )}

            {formaPagamento === 'debito' && (
              <Box sx={{ textAlign: 'center', py: 1 }}>
                <CreditCardIcon sx={{ fontSize: 50, color: 'primary.main', mb: 1 }} />
                <Typography variant="body1">Aguardando processamento na maquininha...</Typography>
              </Box>
            )}
          </Box>
        </DialogContent>

        <DialogActions sx={{ p: 3, justifyContent: 'space-between' }}>
          <Button
            onClick={() => setOpenPagamento(false)}
            color="inherit"
            variant="outlined"
            size="large"
            disabled={isSavingVenda}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleFinalizarVenda}
            color="success"
            variant="contained"
            size="large"
            disabled={(formaPagamento === 'promissoria' && !clienteIdentificado) || isSavingVenda}
            sx={{ px: 4 }}
          >
            {isSavingVenda ? <CircularProgress size={24} color="inherit" /> : 'CONFIRMAR PAGAMENTO'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default FrenteDeCaixa;