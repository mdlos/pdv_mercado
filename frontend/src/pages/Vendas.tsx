
import { useState, useEffect, useMemo } from 'react';
import { LayoutBase } from "../shared/layouts/LayoutBase";
import { ListTable, type IColumn } from "../shared/components/ListTable";
import { Filters } from "../shared/components/Filters";
import { Box, LinearProgress, TextField } from "@mui/material";
import { VendaService, type IVenda } from '../shared/services/services/api';

const Vendas = () => {
    const [isLoading, setIsLoading] = useState(false);

    // Dados da tabela
    const [rows, setRows] = useState<IVenda[]>([]);
    const [totalCount, setTotalCount] = useState(0);

    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [busca, setBusca] = useState({ data: '', cpf: '' });

    const columns: IColumn<IVenda>[] = useMemo(() => [
        { id: 'id_venda', label: 'ID', minWidth: 50 },
        {
            id: 'data_venda',
            label: 'Data',
            minWidth: 150,
            render: (value) => value ? new Date(value).toLocaleString() : '-'
        },
        {
            id: 'cpf_cliente',
            label: 'Cliente (CPF)',
            minWidth: 150,
            render: (value) => value || 'Não identificado'
        },
        { id: 'cpf_funcionario', label: 'Vendedor (CPF)', minWidth: 150 },
        {
            id: 'valor_total',
            label: 'Total',
            minWidth: 100,
            render: (value) => `R$ ${Number(value).toFixed(2)}`
        },
        {
            id: 'itens',
            label: 'Qtd. Itens',
            minWidth: 100,
            render: (value) => Array.isArray(value) ? value.length : 0
        }
    ], []);

    // Função para buscar dados
    const fetchData = () => {
        setIsLoading(true);
        // O serviço getAll espera (page, filterData, filterCpf)
        // Nota: O backend parece esperar data no formato YYYY-MM-DD para filtro exato, 
        // ou podemos ajustar conforme a necessidade.
        VendaService.getAll(page + 1, busca.data, busca.cpf)
            .then((result) => {
                if (result instanceof Error) {
                    alert(result.message);
                } else {
                    setTotalCount(result.totalCount);
                    const start = page * rowsPerPage;
                    const end = start + rowsPerPage;
                    setRows(result.data.slice(start, end));
                }
            })
            .finally(() => setIsLoading(false));
    };

    useEffect(() => {
        fetchData();
    }, [page, rowsPerPage, busca]); // Recarrega quando filtros mudam

    const handleChangePage = (newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (newRowsPerPage: number) => {
        setRowsPerPage(newRowsPerPage);
        setPage(0);
    };

    const handleSearch = () => {
        setPage(0);
        fetchData();
    };

    const handleClear = () => {
        setBusca({ data: '', cpf: '' });
        setPage(0);
    };

    return (
        <LayoutBase titulo={"Histórico de Vendas"}>
            <Filters onSearch={handleSearch} onClear={handleClear}>
                <Box sx={{ display: 'flex', gap: 2, width: '81%', flexWrap: 'wrap' }}>
                    <TextField
                        size="small"
                        label="Data"
                        type="date"
                        value={busca.data}
                        onChange={(e) => setBusca(prev => ({ ...prev, data: e.target.value }))}
                        InputLabelProps={{ shrink: true }}
                        sx={{ flex: 1, width: 100 }}
                    />
                    <TextField
                        size="small"
                        label="CPF Cliente"
                        value={busca.cpf}
                        onChange={(e) => setBusca(prev => ({ ...prev, cpf: e.target.value }))}
                        placeholder="000.000.000-00"
                        sx={{ flex: 1, width: 200 }}
                    />
                </Box>
            </Filters>

            <Box className="mb-4">
                {isLoading && <LinearProgress />}
                <ListTable
                    columns={columns}
                    rows={rows}
                    totalCount={totalCount}
                    page={page}
                    rowsPerPage={rowsPerPage}
                    onPageChange={handleChangePage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                // Sem onEdit e onDelete conforme solicitado
                />
            </Box>
        </LayoutBase>
    )
};

export default Vendas;
