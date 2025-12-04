import { useState, useEffect, useMemo, type ChangeEvent } from 'react';
import { LayoutBase } from "../shared/layouts/LayoutBase";
import FormRegister from "../shared/components/FormRegister";
import { ListTable, type IColumn } from "../shared/components/ListTable";
import { Filters } from "../shared/components/Filters";
import { Confirmar } from "../shared/components/Confirmar";
import { Button, Fab, TextField, Box, LinearProgress } from "@mui/material";
import AddIcon from '@mui/icons-material/Add';
import { ProdutoService, type IDetalheProduto } from '../shared/services/services/api';

const Produtos = () => {
    const [open, setOpen] = useState(false);
    const [openConfirm, setOpenConfirm] = useState(false);
    const [idToDelete, setIdToDelete] = useState<number | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    // Dados da tabela
    const [rows, setRows] = useState<IDetalheProduto[]>([]);
    const [totalCount, setTotalCount] = useState(0);

    const [formData, setFormData] = useState({
        id: '',
        nome: '',
        preco: '',
        codigoBarras: '',
        estoque: ''
    });

    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [busca, setBusca] = useState({ id: '', nome: '', codigoBarras: '' });

    const columns: IColumn[] = useMemo(() => [
        { id: 'id_produto', label: 'ID', minWidth: 50 },
        { id: 'nome', label: 'Nome', minWidth: 150 },
        {
            id: 'preco_venda',
            label: 'Preço',
            minWidth: 100,
            render: (value) => `R$ ${Number(value).toFixed(2)}`
        },
        { id: 'codigo_barras', label: 'Código de Barras', minWidth: 120 },
        { id: 'quantidade_estoque', label: 'Estoque', minWidth: 80 },
    ], []);

    // Função para buscar dados
    const fetchData = () => {
        setIsLoading(true);
        ProdutoService.getAll()
            .then((result) => {
                if (result instanceof Error) {
                    alert(result.message);
                } else {
                    let filteredData = result.data;

                    if (busca.nome) {
                        filteredData = filteredData.filter(item => item.nome.toLowerCase().includes(busca.nome.toLowerCase()));
                    }
                    if (busca.codigoBarras) {
                        filteredData = filteredData.filter(item => item.codigo_barras.includes(busca.codigoBarras));
                    }
                    if (busca.id) {
                        filteredData = filteredData.filter(item => String(item.id_produto) === busca.id);
                    }

                    setTotalCount(filteredData.length);

                    const start = page * rowsPerPage;
                    const end = start + rowsPerPage;
                    setRows(filteredData.slice(start, end));
                }
            })
            .finally(() => setIsLoading(false));
    };

    useEffect(() => {
        fetchData();
    }, [page, rowsPerPage, busca]);

    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleReset = () => {
        setFormData({
            id: '',
            nome: '',
            preco: '',
            codigoBarras: '',
            estoque: ''
        });
    };

    const handleSave = () => {
        setIsLoading(true);

        const dadosParaEnviar = {
            nome: formData.nome,
            preco_venda: Number(formData.preco.replace(',', '.')),
            codigo_barras: formData.codigoBarras,
            quantidade_estoque: Number(formData.estoque)
        };

        if (formData.id) {
            // Edição
            ProdutoService.updateById(Number(formData.id), dadosParaEnviar)
                .then((result) => {
                    if (result instanceof Error) {
                        alert(result.message);
                    } else {
                        alert('Produto atualizado com sucesso!');
                        setOpen(false);
                        handleReset();
                        fetchData();
                    }
                })
                .finally(() => setIsLoading(false));
        } else {
            // Criação
            ProdutoService.create(dadosParaEnviar)
                .then((result) => {
                    if (result instanceof Error) {
                        alert(result.message);
                    } else {
                        alert('Produto cadastrado com sucesso!');
                        setOpen(false);
                        handleReset();
                        fetchData();
                    }
                })
                .finally(() => setIsLoading(false));
        }
    };

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
        setBusca({ id: '', nome: '', codigoBarras: '' });
        setPage(0);
    };

    const handleEdit = (row: IDetalheProduto) => {
        setFormData({
            id: String(row.id_produto),
            nome: row.nome,
            preco: String(row.preco_venda),
            codigoBarras: row.codigo_barras,
            estoque: String(row.quantidade_estoque || 0)
        });
        setOpen(true);
    };

    const handleDeleteClick = (row: IDetalheProduto) => {
        setIdToDelete(row.id_produto);
        setOpenConfirm(true);
    };

    const handleConfirmDelete = () => {
        if (idToDelete) {
            setIsLoading(true);
            ProdutoService.deleteById(idToDelete)
                .then((result) => {
                    if (result instanceof Error) {
                        alert(result.message);
                    } else {
                        alert('Produto excluído com sucesso!');
                        fetchData();
                    }
                })
                .finally(() => {
                    setIsLoading(false);
                    setOpenConfirm(false);
                    setIdToDelete(null);
                });
        }
    };

    return (
        <LayoutBase titulo={"Produtos"}>
            <Filters onSearch={handleSearch} onClear={handleClear}>
                <Box sx={{ display: 'flex', gap: 2, width: '81%', flexWrap: 'wrap' }}>
                    <TextField
                        size="small"
                        label="ID"
                        value={busca.id}
                        onChange={(e) => setBusca(prev => ({ ...prev, id: e.target.value }))}
                        sx={{ width: '100px' }}
                    />
                    <TextField
                        size="small"
                        label="Nome"
                        value={busca.nome}
                        onChange={(e) => setBusca(prev => ({ ...prev, nome: e.target.value }))}
                        sx={{ flex: 1, minWidth: '200px' }}
                    />
                    <TextField
                        size="small"
                        label="Cód. Barras"
                        value={busca.codigoBarras}
                        onChange={(e) => setBusca(prev => ({ ...prev, codigoBarras: e.target.value }))}
                        sx={{ width: '200px' }}
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
                    onEdit={handleEdit}
                    onDelete={handleDeleteClick}
                />
            </Box>

            <FormRegister
                title={formData.id ? "Editar Produto" : "Cadastro de Produto"}
                buttons={[
                    <Button key="reset" variant="outlined" color="warning" onClick={handleReset}>Resetar</Button>,
                    <Button key="save" variant="contained" color="primary" onClick={handleSave} disabled={isLoading}>
                        {isLoading ? 'Salvando...' : 'Salvar'}
                    </Button>,
                ]}
                open={open}
                onClose={() => {
                    setOpen(false);
                    handleReset();
                }}
            >
                <Box className="flex flex-col gap-4">
                    <TextField
                        name="nome"
                        value={formData.nome}
                        onChange={handleChange}
                        id="outlined-basic-nome"
                        label="Nome"
                        variant="outlined"
                        size='small'
                        fullWidth
                    />
                    <TextField
                        name="preco"
                        value={formData.preco}
                        onChange={handleChange}
                        id="outlined-basic-preco"
                        label="Preço (R$)"
                        variant="outlined"
                        size='small'
                        type="number"
                        inputProps={{ step: "0.01" }}
                    />
                    <TextField
                        name="codigoBarras"
                        value={formData.codigoBarras}
                        onChange={handleChange}
                        id="outlined-basic-codigoBarras"
                        label="Código de Barras"
                        variant="outlined"
                        size='small'
                    />
                    <TextField
                        name="estoque"
                        value={formData.estoque}
                        onChange={handleChange}
                        id="outlined-basic-estoque"
                        label="Estoque Inicial"
                        variant="outlined"
                        size='small'
                        type="number"
                    />
                </Box>
            </FormRegister>

            <Confirmar
                open={openConfirm}
                title="Confirmar Exclusão"
                message="Deseja realmente excluir este produto?"
                onClose={() => setOpenConfirm(false)}
                onConfirm={handleConfirmDelete}
            />

            <Fab
                color="primary"
                aria-label="add"
                sx={{ position: "fixed", bottom: "20px", right: "20px" }}
                onClick={() => {
                    handleReset();
                    setOpen(true);
                }}
            >
                <AddIcon />
            </Fab>
        </LayoutBase>
    )
};

export default Produtos;