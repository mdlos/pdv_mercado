import { useState, type ChangeEvent, useMemo } from 'react';
import { LayoutBase } from "../shared/layouts/LayoutBase";
import FormRegister from "../shared/components/FormRegister";
import { ListTable, type IColumn } from "../shared/components/ListTable";
import { Filters } from "../shared/components/Filters";
import { Confirmar } from "../shared/components/Confirmar";
import { Button, Fab, TextField, Box } from "@mui/material";
import AddIcon from '@mui/icons-material/Add';

const Produtos = () => {
    const [open, setOpen] = useState(false);
    const [openConfirm, setOpenConfirm] = useState(false);
    const [idToDelete, setIdToDelete] = useState<number | string | null>(null);
    const [formData, setFormData] = useState({
        id: '',
        nome: '',
        descricao: '',
        preco: '',
        codigoBarras: '',
        estoque: ''
    });

    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);

    const columns: IColumn[] = useMemo(() => [
        { id: 'id', label: 'ID', minWidth: 100 },
        { id: 'nome', label: 'Nome', minWidth: 100 },
        { id: 'descricao', label: 'Descrição', minWidth: 100 },
        { id: 'preco', label: 'Preço', minWidth: 100 },
        { id: 'codigoBarras', label: 'Código de Barras', minWidth: 100 },
        { id: 'estoque', label: 'Estoque', minWidth: 100 },
    ], []);

    // Mock data for now, replace with API call later
    const rows = [
        { id: '1', nome: 'Produto 1', descricao: 'Descrição 1', preco: '10.00', codigoBarras: '123456789', estoque: '10' },
        { id: '2', nome: 'Produto 2', descricao: 'Descrição 2', preco: '20.00', codigoBarras: '987654321', estoque: '20' },
        { id: '3', nome: 'Produto 3', descricao: 'Descrição 3', preco: '30.00', codigoBarras: '111111111', estoque: '30' },
        { id: '4', nome: 'Produto 4', descricao: 'Descrição 4', preco: '40.00', codigoBarras: '222222222', estoque: '40' },
        { id: '5', nome: 'Produto 5', descricao: 'Descrição 5', preco: '50.00', codigoBarras: '333333333', estoque: '50' },
        { id: '6', nome: 'Produto 6', descricao: 'Descrição 6', preco: '60.00', codigoBarras: '444444444', estoque: '60' },
        { id: '7', nome: 'Produto 7', descricao: 'Descrição 7', preco: '70.00', codigoBarras: '555555555', estoque: '70' },
        { id: '8', nome: 'Produto 8', descricao: 'Descrição 8', preco: '80.00', codigoBarras: '666666666', estoque: '80' },
        { id: '9', nome: 'Produto 9', descricao: 'Descrição 9', preco: '90.00', codigoBarras: '777777777', estoque: '90' },
        { id: '10', nome: 'Produto 10', descricao: 'Descrição 10', preco: '100.00', codigoBarras: '888888888', estoque: '100' },
    ];

    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleReset = () => {
        setFormData({
            id: '',
            nome: '',
            descricao: '',
            preco: '',
            codigoBarras: '',
            estoque: ''
        });
    };

    const handleSave = () => {
        console.log("Dados salvos:", formData);
        setOpen(false);
        handleReset();
    };

    const handleChangePage = (newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (newRowsPerPage: number) => {
        setRowsPerPage(newRowsPerPage);
        setPage(0);
    };

    const handleSearch = (filters: any) => {
        console.log("Filtrando por:", filters);
        // Implementar lógica de filtro aqui
    };

    const handleClear = () => {
        console.log("Filtros limpos");
        // Implementar lógica de limpar filtros aqui
    };

    const handleEdit = (row: any) => {
        console.log("Editando produto:", row);
        setFormData({ ...row }); // Preenche o formulário com os dados da linha
        setOpen(true);
    };

    const handleDeleteClick = (row: any) => {
        setIdToDelete(row.id);
        setOpenConfirm(true);
    };

    const handleConfirmDelete = () => {
        console.log("Deletando produto ID:", idToDelete);
        // Implementar lógica de deletar aqui
        setOpenConfirm(false);
        setIdToDelete(null);
    };

    return (
        <LayoutBase titulo={"Produtos"}>
            <Filters onSearch={handleSearch} onClear={handleClear} />

            <Box className="mb-4">
                <ListTable
                    columns={columns}
                    rows={rows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)}
                    totalCount={rows.length}
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
                    <Button key="save" variant="contained" color="primary" onClick={handleSave}>Salvar</Button>,
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
                    />
                    <TextField
                        name="descricao"
                        value={formData.descricao}
                        onChange={handleChange}
                        id="outlined-basic-descricao"
                        label="Descrição"
                        variant="outlined"
                        size='small'
                    />
                    <TextField
                        name="preco"
                        value={formData.preco}
                        onChange={handleChange}
                        id="outlined-basic-preco"
                        label="Preço"
                        variant="outlined"
                        size='small'
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
                        label="Estoque"
                        variant="outlined"
                        size='small'
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