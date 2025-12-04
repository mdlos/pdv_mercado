import { Api } from '../axios_config';

export interface IProduto {
    id_produto?: number;
    nome: string;
    codigo_barras: string;
    preco_venda: number;
    quantidade_estoque?: number;
}

export interface IDetalheProduto extends IProduto {
    id_produto: number;
}

type TProdutoComTotalCount = {
    data: IDetalheProduto[];
    totalCount: number;
}

const getAll = async (page = 1, filter = ''): Promise<TProdutoComTotalCount | Error> => {
    try {
        const urlRelativa = `/produtos?_page=${page}&_limit=10&nome_like=${filter}`;
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

const getByCodigo = async (codigo: string): Promise<IDetalheProduto | Error> => {
    try {
        // Assume que a API suporta filtro por código de barras
        const { data } = await Api.get(`/produtos?codigo_barras=${codigo}`);

        if (data && data.length > 0) {
            return data[0];
        }

        return new Error('Produto não encontrado.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao consultar o registro.');
    }
};

const getById = async (id: number): Promise<IDetalheProduto | Error> => {
    try {
        const { data } = await Api.get(`/produtos/${id}`);

        if (data) {
            return data;
        }

        return new Error('Erro ao consultar o registro.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao consultar o registro.');
    }
};

const create = async (dados: Omit<IProduto, 'id_produto'>): Promise<number | Error> => {
    try {
        const { data } = await Api.post<IDetalheProduto>('/produtos', dados);

        if (data) {
            return data.id_produto;
        }

        return new Error('Erro ao criar o registro.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao criar o registro.');
    }
};

const updateById = async (id: number, dados: Partial<Omit<IProduto, 'id_produto'>>): Promise<void | Error> => {
    try {
        await Api.put(`/produtos/${id}`, dados);
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao atualizar o registro.');
    }
};

const deleteById = async (id: number): Promise<void | Error> => {
    try {
        await Api.delete(`/produtos/${id}`);
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao apagar o registro.');
    }
};

export const ProdutoService = {
    getAll,
    getByCodigo,
    getById,
    create,
    updateById,
    deleteById,
};
