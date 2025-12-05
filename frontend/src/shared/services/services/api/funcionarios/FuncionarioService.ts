import { Api } from '../axios_config';
import type { ILocalizacao } from '../clientes/ClienteService';

export interface IFuncionario {
    cpf: string; // CPF é a chave primária
    nome: string;
    sobrenome: string;
    nome_social?: string;
    email?: string;
    telefone?: string;
    sexo?: string;
    senha?: string; // Usado apenas no create/update
    id_tipo_funcionario: number; // Obrigatório
    localizacao?: ILocalizacao;
    tipo_cargo?: string;
}

export interface IDetalheFuncionario extends IFuncionario { }

export type TFuncionarioComTotalCount = {
    data: IDetalheFuncionario[];
    totalCount: number;
}

const getAll = async (filter = ''): Promise<TFuncionarioComTotalCount | Error> => {
    try {
        const { data } = await Api.get('/funcionarios');

        if (data) {
            let filteredData = data;
            if (filter) {
                filteredData = data.filter((item: IDetalheFuncionario) =>
                    item.nome.toLowerCase().includes(filter.toLowerCase()) ||
                    item.cpf.includes(filter)
                );
            }

            return {
                data: filteredData,
                totalCount: filteredData.length,
            };
        }

        return new Error('Erro ao listar os registros.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao listar os registros.');
    }
};

const getByCpf = async (cpf: string): Promise<IDetalheFuncionario | Error> => {
    try {
        const { data } = await Api.get(`/funcionarios/${cpf}`);

        if (data) {
            return data;
        }

        return new Error('Erro ao consultar o registro.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao consultar o registro.');
    }
};

const create = async (dados: IFuncionario): Promise<string | Error> => {
    try {
        const { data } = await Api.post<IDetalheFuncionario>('/funcionarios', dados);

        if (data) {
            return data.cpf;
        }

        return new Error('Erro ao criar o registro.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao criar o registro.');
    }
};

const updateByCpf = async (cpf: string, dados: Partial<IFuncionario>): Promise<void | Error> => {
    try {
        await Api.put(`/funcionarios/${cpf}`, dados);
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao atualizar o registro.');
    }
};

const deleteByCpf = async (cpf: string): Promise<void | Error> => {
    try {
        await Api.delete(`/funcionarios/${cpf}`);
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao apagar o registro.');
    }
};

export const FuncionarioService = {
    getAll,
    create,
    getByCpf,
    updateByCpf,
    deleteByCpf,
};
