import { useState, type ChangeEvent, useMemo } from 'react';
import { LayoutBase } from "../shared/layouts/LayoutBase";
import FormRegister from "../shared/components/FormRegister";
import { ListTable, type IColumn } from "../shared/components/ListTable";
import { Button, Fab, TextField, Box } from "@mui/material";
import AddIcon from '@mui/icons-material/Add';

const Clientes = () => {
    const [open, setOpen] = useState(false);
    const [formData, setFormData] = useState({
        nome: '',
        cpf: '',
        sexo: '',
        celular: '',
        email: '',
        logradouro: '',
        numero: '',
        cidade: '',
        estado: ''
    });

    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);

    const columns: IColumn[] = useMemo(() => [
        { id: 'cpf', label: 'CPF', minWidth: 100 },
        { id: 'nome', label: 'Nome Completo', minWidth: 170 },
        { id: 'email', label: 'Email', minWidth: 170 },
        { id: 'celular', label: 'Telefone', minWidth: 100 },
        { id: 'sexo', label: 'Sexo', minWidth: 100 },
        { id: 'logradouro', label: 'Logradouro', minWidth: 100 },
        { id: 'numero', label: 'Número', minWidth: 100 },
        { id: 'cidade', label: 'Cidade', minWidth: 100 },
        { id: 'estado', label: 'Estado', minWidth: 100 },
    ], []);

    // Mock data for now, replace with API call later
    const rows = [
        { id: 1, cpf: '123.456.789-00', nome: 'João da Silva', email: 'joao@email.com', celular: '(11) 99999-9999' },
        { id: 2, cpf: '987.654.321-11', nome: 'Maria Oliveira', email: 'maria@email.com', celular: '(21) 88888-8888' },
        { id: 3, cpf: '987.654.321-11', nome: 'Maria Oliveira', email: 'maria@email.com', celular: '(21) 88888-8888' },
        { id: 4, cpf: '987.654.321-11', nome: 'Maria Oliveira', email: 'maria@email.com', celular: '(21) 88888-8888' },
        { id: 5, cpf: '987.654.321-11', nome: 'Maria Oliveira', email: 'maria@email.com', celular: '(21) 88888-8888' },
        { id: 6, cpf: '987.654.321-11', nome: 'Maria Oliveira', email: 'maria@email.com', celular: '(21) 88888-8888' },
        { id: 7, cpf: '987.654.321-11', nome: 'Maria Oliveira', email: 'maria@email.com', celular: '(21) 88888-8888' },
        { id: 8, cpf: '987.654.321-11', nome: 'Maria Oliveira', email: 'maria@email.com', celular: '(21) 88888-8888' },
        { id: 9, cpf: '987.654.321-11', nome: 'Maria Oliveira', email: 'maria@email.com', celular: '(21) 88888-8888' },
        { id: 10, cpf: '987.654.321-11', nome: 'Maria Oliveira', email: 'maria@email.com', celular: '(21) 88888-8888' },
    ];

    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleReset = () => {
        setFormData({
            nome: '',
            cpf: '',
            sexo: '',
            celular: '',
            email: '',
            logradouro: '',
            numero: '',
            cidade: '',
            estado: ''
        });
    };

    const handleSave = () => {
        console.log("Dados salvos:", formData);
        setOpen(false);
    };

    const handleChangePage = (newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (newRowsPerPage: number) => {
        setRowsPerPage(newRowsPerPage);
        setPage(0);
    };

    return (
        <LayoutBase titulo={"Clientes"}>
            <Box className="mb-4">
                <ListTable
                    columns={columns}
                    rows={rows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)}
                    totalCount={rows.length}
                    page={page}
                    rowsPerPage={rowsPerPage}
                    onPageChange={handleChangePage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                />
            </Box>

            <FormRegister
                title="Cadastro de Usuário"
                buttons={[
                    <Button key="reset" variant="outlined" color="warning" onClick={handleReset}>Resetar</Button>,
                    <Button key="save" variant="contained" color="primary" onClick={handleSave}>Salvar</Button>,
                ]}
                open={open}
                onClose={() => setOpen(false)}
            >
                <Box className="flex flex-col gap-4">
                    <TextField
                        name="nome"
                        value={formData.nome}
                        onChange={handleChange}
                        id="outlined-basic-nome"
                        label="Nome Completo"
                        variant="outlined"
                        size='small'
                    />
                    <Box className="flex flex-row justify-between gap-2 w-full">
                        <TextField
                            name="cpf"
                            value={formData.cpf}
                            onChange={handleChange}
                            id="outlined-basic-cpf"
                            className="w-100"
                            label="CPF"
                            variant="outlined"
                            size='small'
                        />
                        <TextField
                            name="sexo"
                            value={formData.sexo}
                            onChange={handleChange}
                            id="outlined-basic-sexo"
                            className="w-40"
                            label="Sexo"
                            variant="outlined"
                            size='small'
                        />
                    </Box>
                    <Box className="flex flex-row justify-between gap-2 w-full">
                        <TextField
                            name="celular"
                            value={formData.celular}
                            onChange={handleChange}
                            id="outlined-basic-celular"
                            className="w-100"
                            label="Celular"
                            variant="outlined"
                            size='small'
                        />
                        <TextField
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            id="outlined-basic-email"
                            className="w-100"
                            label="Email"
                            variant="outlined"
                            size='small'
                        />
                    </Box>
                    <Box className="flex flex-row justify-between gap-2 w-full">
                        <TextField
                            name="logradouro"
                            value={formData.logradouro}
                            onChange={handleChange}
                            id="outlined-basic-logradouro"
                            className="w-100"
                            label="Logradouro"
                            variant="outlined"
                            size='small'
                        />
                        <TextField
                            name="numero"
                            value={formData.numero}
                            onChange={handleChange}
                            id="outlined-basic-numero"
                            className="w-40"
                            label="Número"
                            variant="outlined"
                            size='small'
                        />
                    </Box>
                    <Box className="flex flex-row justify-between gap-2 w-full">
                        <TextField
                            name="cidade"
                            value={formData.cidade}
                            onChange={handleChange}
                            id="outlined-basic-cidade"
                            className="w-100"
                            label="Cidade"
                            variant="outlined"
                            size='small'
                        />
                        <TextField
                            name="estado"
                            value={formData.estado}
                            onChange={handleChange}
                            id="outlined-basic-estado"
                            className="w-100"
                            label="Estado"
                            variant="outlined"
                            size='small'
                        />
                    </Box>
                </Box>

            </FormRegister>

            <Fab
                color="primary"
                aria-label="add"
                sx={{ position: "fixed", bottom: "20px", right: "20px" }}
                onClick={() => setOpen(true)}
            >
                <AddIcon />
            </Fab>
        </LayoutBase>
    )
};

export default Clientes;