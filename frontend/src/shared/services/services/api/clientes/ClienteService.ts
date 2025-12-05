import { Api } from '../axios_config';

export interface ILocalizacao {
    [key: string]: any;
}

export interface ICliente {
    id_cliente?: number;
    nome: string;
    cpf_cnpj: string;
    email?: string;
    telefone?: string;
    sexo?: string;
    localizacao: ILocalizacao;
}

export interface IDetalheCliente extends ICliente {
    id_cliente: number;
}

type TClienteComTotalCount = {
    data: IDetalheCliente[];
    totalCount: number;
}

const getAll = async (): Promise<TClienteComTotalCount | Error> => {
    try {
        const { data } = await Api.get('/clientes');

        if (data) {
            return {
                data: data,
                totalCount: data.length,
            };
        }

        return new Error('Erro ao listar os registros.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao listar os registros.');
    }
};

const getById = async (id: number): Promise<IDetalheCliente | Error> => {
    try {
        const { data } = await Api.get(`/clientes/${id}`);

        if (data) {
            return data;
        }

        return new Error('Erro ao consultar o registro.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao consultar o registro.');
    }
};

const create = async (dados: Omit<ICliente, 'id_cliente'>): Promise<number | Error> => {
    try {
        const { data } = await Api.post<IDetalheCliente>('/clientes', dados);

        if (data) {
            return data.id_cliente;
        }

        return new Error('Erro ao criar o registro.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao criar o registro.');
    }
};

const updateById = async (id: number, dados: Partial<Omit<ICliente, 'id_cliente'>>): Promise<void | Error> => {
    try {
        await Api.put(`/clientes/${id}`, dados);
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao atualizar o registro.');
    }
};

const deleteById = async (id: number): Promise<void | Error> => {
    try {
        await Api.delete(`/clientes/${id}`);
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao apagar o registro.');
    }
};

export const ClienteService = {
    getAll,
    create,
    getById,
    updateById,
    deleteById,
};
