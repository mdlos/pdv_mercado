import { Api } from '../axios_config';
import type { ILocalizacao } from '../clientes/ClienteService';

export interface IFuncionario {
    id_funcionario?: number;
    nome: string;
    sobrenome: string;
    nome_social?: string;
    cpf: string;
    email: string;
    telefone?: string;
    sexo?: string;
    senha?: string;
    localizacao: ILocalizacao;
}

export interface IDetalheFuncionario extends IFuncionario {
    id_funcionario: number;
}

type TFuncionarioComTotalCount = {
    data: IDetalheFuncionario[];
    totalCount: number;
}

const getAll = async (page = 1, filter = ''): Promise<TFuncionarioComTotalCount | Error> => {
    try {
        const urlRelativa = `/funcionarios?_page=${page}&_limit=10&nome_like=${filter}`;
        const { data, headers } = await Api.get(urlRelativa);

        if (data) {
            return {
                data: data,
                totalCount: Number(headers['x-total-count'] || data.length),
            };
        }

        return new Error('Erro ao listar os registros.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao listar os registros.');
    }
};

const getById = async (id: number): Promise<IDetalheFuncionario | Error> => {
    try {
        const { data } = await Api.get(`/funcionarios/${id}`);

        if (data) {
            return data;
        }

        return new Error('Erro ao consultar o registro.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao consultar o registro.');
    }
};

const create = async (dados: Omit<IFuncionario, 'id_funcionario'>): Promise<number | Error> => {
    try {
        const { data } = await Api.post<IDetalheFuncionario>('/funcionarios', dados);

        if (data) {
            return data.id_funcionario;
        }

        return new Error('Erro ao criar o registro.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao criar o registro.');
    }
};

const updateById = async (id: number, dados: Partial<Omit<IFuncionario, 'id_funcionario'>>): Promise<void | Error> => {
    try {
        await Api.put(`/funcionarios/${id}`, dados);
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao atualizar o registro.');
    }
};

const deleteById = async (id: number): Promise<void | Error> => {
    try {
        await Api.delete(`/funcionarios/${id}`);
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao apagar o registro.');
    }
};

export const FuncionarioService = {
    getAll,
    create,
    getById,
    updateById,
    deleteById,
};
