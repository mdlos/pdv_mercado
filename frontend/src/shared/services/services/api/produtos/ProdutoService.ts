import { Api } from '../axios_config';

export interface IProduto {
    codigo_produto?: number;
    nome: string;
    descricao: string;
    preco: number;
    codigo_barras: string;
    initial_quantity?: number; // Usado apenas no create
    quantidade?: number; // Retornado pelo backend
}

export interface IDetalheProduto extends IProduto {
    codigo_produto: number;
}

type TProdutoComTotalCount = {
    data: IDetalheProduto[];
    totalCount: number;
}

const getAll = async (page = 1, filter = ''): Promise<TProdutoComTotalCount | Error> => {
    try {
        // Backend atualmente retorna todos os produtos sem paginação
        const { data } = await Api.get('/produtos');

        if (data) {
            let filteredData = data;
            if (filter) {
                filteredData = data.filter((item: IDetalheProduto) =>
                    item.nome.toLowerCase().includes(filter.toLowerCase()) ||
                    item.codigo_barras.includes(filter)
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

const getByCodigo = async (codigo: string): Promise<IDetalheProduto | Error> => {
    try {
        // Backend não tem rota de busca por código de barras ainda, simulando com getAll
        const { data } = await Api.get('/produtos');

        if (data) {
            const produto = data.find((item: IDetalheProduto) => item.codigo_barras === codigo);
            if (produto) return produto;
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

const create = async (dados: Omit<IProduto, 'codigo_produto'>): Promise<number | Error> => {
    try {
        const { data } = await Api.post<{ codigo_produto: number }>('/produtos', dados);

        if (data) {
            return data.codigo_produto;
        }

        return new Error('Erro ao criar o registro.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao criar o registro.');
    }
};

const updateById = async (id: number, dados: Partial<Omit<IProduto, 'codigo_produto'>>): Promise<void | Error> => {
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
