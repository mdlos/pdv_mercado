import { Api } from '../axios_config';

export interface IItemVenda {
    codigo_produto: number;
    quantidade_venda: number;
    preco_unitario: number;
    subtotal?: number;
    nome_produto?: string; // Opcional, para exibição
}

export interface IPagamentoVenda {
    id_tipo: number; // 1: Dinheiro, 2: Cartão, etc. (Precisa mapear no frontend)
    valor_pago: number;
    troco?: number;
    descricao?: string; // Retornado pelo backend
}

export interface IVenda {
    id_venda?: number;
    cpf_cliente?: string | null;
    cpf_funcionario: string;
    valor_total?: number;
    desconto?: number;
    troco?: number;
    data_venda?: string;
    itens: IItemVenda[];
    pagamentos: IPagamentoVenda[]; // Backend espera lista, mas o DAO processa o primeiro item por enquanto
}

const create = async (dados: Omit<IVenda, 'id_venda'>): Promise<number | Error> => {
    try {
        const { data } = await Api.post<IVenda>('/vendas', dados);

        if (data && data.id_venda) {
            return data.id_venda;
        }

        return new Error('Erro ao registrar a venda.');
    } catch (error) {
        const err = error as any;
        if (err.response && err.response.data) {
            const errorData = err.response.data;
            const errorMessage = errorData.message || 'Erro ao registrar a venda.';
            const detailedErrors = errorData.errors ? JSON.stringify(errorData.errors) : '';
            return new Error(`${errorMessage} ${detailedErrors}`);
        }
        return new Error('Erro ao registrar a venda.');
    }
};

const getAll = async (page = 1, filterData = '', filterCpf = ''): Promise<{ data: IVenda[], totalCount: number } | Error> => {
    try {
        let url = '/vendas';
        const params = new URLSearchParams();

        if (filterData) params.append('data', filterData);
        if (filterCpf) params.append('cpf', filterCpf);

        if (params.toString()) {
            url += `?${params.toString()}`;
        }

        const { data } = await Api.get(url);

        if (data) {
            return {
                data: data,
                totalCount: data.length,
            };
        }

        return new Error('Erro ao listar vendas.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao listar vendas.');
    }
};

const getById = async (id: number): Promise<IVenda | Error> => {
    try {
        const { data } = await Api.get(`/vendas/${id}`);

        if (data) {
            return data;
        }

        return new Error('Erro ao consultar venda.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao consultar venda.');
    }
};

export const VendaService = {
    create,
    getAll,
    getById,
};
