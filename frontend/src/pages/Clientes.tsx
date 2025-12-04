import { useState, useEffect, useMemo, type ChangeEvent } from 'react';
import { LayoutBase } from "../shared/layouts/LayoutBase";
import FormRegister from "../shared/components/FormRegister";
import { ListTable, type IColumn } from "../shared/components/ListTable";
import { Filters } from "../shared/components/Filters";
import { Confirmar } from "../shared/components/Confirmar";
import { Button, Fab, TextField, Box, LinearProgress } from "@mui/material";
import AddIcon from '@mui/icons-material/Add';
import { ClienteService, type IDetalheCliente } from '../shared/services/services/api';

const Clientes = () => {
    const [open, setOpen] = useState(false);
    const [openConfirm, setOpenConfirm] = useState(false);
    const [idToDelete, setIdToDelete] = useState<number | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    // Dados da tabela
    const [rows, setRows] = useState<IDetalheCliente[]>([]);
    const [totalCount, setTotalCount] = useState(0);

    const [formData, setFormData] = useState({
        id: '',
        nome: '',
        cpf: '',
        sexo: '',
        celular: '',
        email: '',
        cep: '', // NOVO CAMPO
        logradouro: '',
        numero: '',
        cidade: '',
        estado: ''
    });

    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [busca, setBusca] = useState({ cpf: '', nome: '', telefone: '' });

    const columns: IColumn[] = useMemo(() => [
        { id: 'cpf_cnpj', label: 'CPF', minWidth: 100 },
        { id: 'nome', label: 'Nome Completo', minWidth: 170 },
        { id: 'email', label: 'Email', minWidth: 170 },
        { id: 'telefone', label: 'Telefone', minWidth: 100 },
        { id: 'sexo', label: 'Sexo', minWidth: 100 },
    ], []);

    // Função para buscar dados
    const fetchData = () => {
        setIsLoading(true);
        ClienteService.getAll()
            .then((result) => {
                if (result instanceof Error) {
                    alert(result.message);
                } else {
                    let filteredData = result.data;

                    if (busca.nome) {
                        filteredData = filteredData.filter(item => item.nome.toLowerCase().includes(busca.nome.toLowerCase()));
                    }
                    if (busca.cpf) {
                        filteredData = filteredData.filter(item => item.cpf_cnpj.includes(busca.cpf));
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
            cpf: '',
            sexo: '',
            celular: '',
            email: '',
            cep: '',
            logradouro: '',
            numero: '',
            cidade: '',
            estado: ''
        });
    };

    const handleSave = () => {
        setIsLoading(true);

        const dadosParaEnviar = {
            nome: formData.nome,
            cpf_cnpj: formData.cpf,
            email: formData.email || undefined,
            telefone: formData.celular || undefined,
            sexo: formData.sexo || undefined,
            localizacao: {
                cep: formData.cep, // NOVO CAMPO
                logradouro: formData.logradouro,
                numero: formData.numero,
                cidade: formData.cidade,
                uf: formData.estado // Backend espera 'uf'
            }
        };

        if (formData.id) {
            // Edição
            ClienteService.updateById(Number(formData.id), dadosParaEnviar)
                .then((result) => {
                    if (result instanceof Error) {
                        alert(result.message);
                    } else {
                        alert('Cliente atualizado com sucesso!');
                        setOpen(false);
                        handleReset();
                        fetchData();
                    }
                })
                .finally(() => setIsLoading(false));
        } else {
            // Criação
            ClienteService.create(dadosParaEnviar)
                .then((result) => {
                    if (result instanceof Error) {
                        alert(result.message);
                    } else {
                        alert('Cliente cadastrado com sucesso!');
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
        setBusca({ cpf: '', nome: '', telefone: '' });
        setPage(0);
    };

    const handleEdit = (row: IDetalheCliente) => {
        setFormData({
            id: String(row.id_cliente),
            nome: row.nome,
            cpf: row.cpf_cnpj,
            sexo: row.sexo || '',
            celular: row.telefone || '',
            email: row.email || '',
            cep: row.localizacao?.cep || '',
            logradouro: row.localizacao?.logradouro || '',
            numero: row.localizacao?.numero || '',
            cidade: row.localizacao?.cidade || '',
            estado: row.localizacao?.uf || '' // Backend retorna 'uf'
        });
        setOpen(true);
    };

    const handleDeleteClick = (row: IDetalheCliente) => {
        setIdToDelete(row.id_cliente);
        setOpenConfirm(true);
    };

    const handleConfirmDelete = () => {
        if (idToDelete) {
            setIsLoading(true);
            ClienteService.deleteById(idToDelete)
                .then((result) => {
                    if (result instanceof Error) {
                        alert(result.message);
                    } else {
                        alert('Cliente excluído com sucesso!');
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
        <LayoutBase titulo={"Clientes"}>
            <Filters onSearch={handleSearch} onClear={handleClear}>
                <Box sx={{ display: 'flex', gap: 2, width: '81%', flexWrap: 'wrap' }}>
                    <TextField
                        size="small"
                        label="CPF"
                        value={busca.cpf}
                        onChange={(e) => setBusca(prev => ({ ...prev, cpf: e.target.value }))}
                        sx={{ width: '100' }}
                    />
                    <TextField
                        size="small"
                        label="Nome"
                        value={busca.nome}
                        onChange={(e) => setBusca(prev => ({ ...prev, nome: e.target.value }))}
                        sx={{ flex: 1, minWidth: '100' }}
                    />
                    <TextField
                        size="small"
                        label="Telefone"
                        value={busca.telefone}
                        onChange={(e) => setBusca(prev => ({ ...prev, telefone: e.target.value }))}
                        sx={{ width: '100' }}
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
                title={formData.id ? "Editar Cliente" : "Cadastro de Cliente"}
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
                        label="Nome Completo"
                        variant="outlined"
                        size='small'
                        fullWidth
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
                            name="cep"
                            value={formData.cep}
                            onChange={handleChange}
                            id="outlined-basic-cep"
                            className="w-40"
                            label="CEP"
                            variant="outlined"
                            size='small'
                        />
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
                            label="Estado (UF)"
                            variant="outlined"
                            size='small'
                        />
                    </Box>
                </Box>
            </FormRegister>

            <Confirmar
                open={openConfirm}
                title="Confirmar Exclusão"
                message="Deseja realmente excluir este cliente?"
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

export default Clientes;