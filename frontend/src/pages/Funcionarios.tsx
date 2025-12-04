import { useState, useEffect, useMemo, type ChangeEvent } from 'react';
import { LayoutBase } from "../shared/layouts/LayoutBase";
import FormRegister from "../shared/components/FormRegister";
import { ListTable, type IColumn } from "../shared/components/ListTable";
import { Filters } from "../shared/components/Filters";
import { Confirmar } from "../shared/components/Confirmar";
import { Button, Fab, TextField, Box, LinearProgress } from "@mui/material";
import AddIcon from '@mui/icons-material/Add';
import { FuncionarioService, type IDetalheFuncionario } from '../shared/services/services/api';

const Funcionarios = () => {
    const [open, setOpen] = useState(false);
    const [openConfirm, setOpenConfirm] = useState(false);
    const [idToDelete, setIdToDelete] = useState<number | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    // Dados da tabela
    const [rows, setRows] = useState<IDetalheFuncionario[]>([]);
    const [totalCount, setTotalCount] = useState(0);

    const [formData, setFormData] = useState({
        id: '',
        cpf: '',
        sexo: '',
        email: '',
        senha: '',
        nome: '',
        sobrenome: '',
        nomeSocial: '',
        telefone: '',
        logradouro: '',
        numero: '',
        cidade: '',
        estado: '',
    });

    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [busca, setBusca] = useState({ cpf: '', nome: '', telefone: '' });

    const columns: IColumn[] = useMemo(() => [
        { id: 'cpf', label: 'CPF', minWidth: 100 },
        {
            id: 'nome',
            label: 'Nome Completo',
            minWidth: 150,
            render: (value, row) => `${row.nome} ${row.sobrenome}`
        },
        { id: 'sexo', label: 'Sexo', minWidth: 100 },
        { id: 'nome_social', label: 'Nome Social', minWidth: 100 },
        { id: 'telefone', label: 'Telefone', minWidth: 100 },
        // Campos aninhados não são exibidos diretamente na tabela simples, mas estão nos dados
    ], []);

    // Função para buscar dados
    const fetchData = () => {
        setIsLoading(true);
        FuncionarioService.getAll()
            .then((result) => {
                if (result instanceof Error) {
                    alert(result.message);
                } else {
                    let filteredData = result.data;

                    if (busca.nome) {
                        const termo = busca.nome.toLowerCase();
                        filteredData = filteredData.filter(item =>
                            item.nome.toLowerCase().includes(termo) ||
                            item.sobrenome.toLowerCase().includes(termo)
                        );
                    }
                    if (busca.cpf) {
                        filteredData = filteredData.filter(item => item.cpf.includes(busca.cpf));
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
            cpf: '',
            sexo: '',
            email: '',
            senha: '',
            nome: '',
            sobrenome: '',
            nomeSocial: '',
            telefone: '',
            logradouro: '',
            numero: '',
            cidade: '',
            estado: '',
        });
    };

    const handleSave = () => {
        setIsLoading(true);

        const dadosParaEnviar = {
            nome: formData.nome,
            sobrenome: formData.sobrenome,
            nome_social: formData.nomeSocial,
            cpf: formData.cpf,
            email: formData.email,
            telefone: formData.telefone,
            sexo: formData.sexo,
            senha: formData.senha, // Envia senha apenas se preenchida ou na criação
            localizacao: {
                logradouro: formData.logradouro,
                numero: formData.numero,
                cidade: formData.cidade,
                estado: formData.estado
            }
        };

        if (formData.id) {
            // Edição
            FuncionarioService.updateById(Number(formData.id), dadosParaEnviar)
                .then((result) => {
                    if (result instanceof Error) {
                        alert(result.message);
                    } else {
                        alert('Funcionário atualizado com sucesso!');
                        setOpen(false);
                        handleReset();
                        fetchData();
                    }
                })
                .finally(() => setIsLoading(false));
        } else {
            // Criação
            FuncionarioService.create(dadosParaEnviar)
                .then((result) => {
                    if (result instanceof Error) {
                        alert(result.message);
                    } else {
                        alert('Funcionário cadastrado com sucesso!');
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

    const handleEdit = (row: IDetalheFuncionario) => {
        setFormData({
            id: String(row.id_funcionario),
            cpf: row.cpf,
            sexo: row.sexo || '',
            email: row.email,
            senha: '', // Não preenche senha na edição por segurança
            nome: row.nome,
            sobrenome: row.sobrenome,
            nomeSocial: row.nome_social || '',
            telefone: row.telefone || '',
            logradouro: row.localizacao?.logradouro || '',
            numero: row.localizacao?.numero || '',
            cidade: row.localizacao?.cidade || '',
            estado: row.localizacao?.estado || '',
        });
        setOpen(true);
    };

    const handleDeleteClick = (row: IDetalheFuncionario) => {
        setIdToDelete(row.id_funcionario);
        setOpenConfirm(true);
    };

    const handleConfirmDelete = () => {
        if (idToDelete) {
            setIsLoading(true);
            FuncionarioService.deleteById(idToDelete)
                .then((result) => {
                    if (result instanceof Error) {
                        alert(result.message);
                    } else {
                        alert('Funcionário excluído com sucesso!');
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
        <LayoutBase titulo={"Funcionários"}>
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
                title={formData.id ? "Editar Funcionário" : "Cadastro de Funcionário"}
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
                        name="cpf"
                        value={formData.cpf}
                        onChange={handleChange}
                        id="outlined-basic-cpf"
                        label="CPF"
                        variant="outlined"
                        size='small'
                    />
                    <TextField
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        id="outlined-basic-email"
                        label="Email"
                        variant="outlined"
                        size='small'
                    />
                    <TextField
                        name="senha"
                        value={formData.senha}
                        onChange={handleChange}
                        id="outlined-basic-senha"
                        label="Senha"
                        type="password"
                        variant="outlined"
                        size='small'
                        helperText={formData.id ? "Deixe em branco para manter a senha atual" : ""}
                    />
                    <Box className="flex flex-row gap-4">
                        <TextField
                            name="nome"
                            value={formData.nome}
                            onChange={handleChange}
                            id="outlined-basic-nome"
                            className="w-full"
                            label="Nome"
                            variant="outlined"
                            size='small'
                        />
                        <TextField
                            name="sobrenome"
                            value={formData.sobrenome}
                            onChange={handleChange}
                            id="outlined-basic-sobrenome"
                            className="w-full"
                            label="Sobrenome"
                            variant="outlined"
                            size='small'
                        />
                    </Box>
                    <Box className="flex flex-row gap-4">
                        <TextField
                            name="nomeSocial"
                            value={formData.nomeSocial}
                            onChange={handleChange}
                            id="outlined-basic-nomeSocial"
                            className="w-full"
                            label="Nome Social"
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
                    <TextField
                        name="telefone"
                        value={formData.telefone}
                        onChange={handleChange}
                        id="outlined-basic-telefone"
                        label="Telefone"
                        variant="outlined"
                        size='small'
                    />
                    <Box className="flex flex-row gap-4">
                        <TextField
                            name="logradouro"
                            value={formData.logradouro}
                            onChange={handleChange}
                            id="outlined-basic-logradouro"
                            className='w-full'
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
                    <Box className="flex flex-row gap-4">
                        <TextField
                            name="cidade"
                            value={formData.cidade}
                            onChange={handleChange}
                            id="outlined-basic-cidade"
                            className="w-full"
                            label="Cidade"
                            variant="outlined"
                            size='small'
                        />
                        <TextField
                            name="estado"
                            value={formData.estado}
                            onChange={handleChange}
                            id="outlined-basic-estado"
                            className="w-40"
                            label="Estado"
                            variant="outlined"
                            size='small'
                        />
                    </Box>
                </Box>
            </FormRegister>

            <Confirmar
                open={openConfirm}
                title="Confirmar Exclusão"
                message="Deseja realmente excluir este funcionário?"
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

export default Funcionarios;