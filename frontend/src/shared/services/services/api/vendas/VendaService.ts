import { Api } from '../axios_config';

export interface IItemVenda {
    id_produto: number;
    quantidade: number;
    valor_unitario: number;
}

export interface IPagamentoVenda {
    forma_pagamento: 'dinheiro' | 'debito' | 'credito' | 'pix' | 'promissoria';
    valor_recebido?: number;
    troco?: number;
    parcelas?: number;
}

export interface IVenda {
    id_venda?: number;
    id_cliente?: number | null;
    valor_total: number;
    data_venda: string;
    itens: IItemVenda[];
    pagamento: IPagamentoVenda;
}

const create = async (dados: Omit<IVenda, 'id_venda'>): Promise<number | Error> => {
    try {
        const { data } = await Api.post<IVenda>('/vendas', dados);

        if (data && data.id_venda) {
            return data.id_venda;
        }

        return new Error('Erro ao registrar a venda.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao registrar a venda.');
    }
};

const getAll = async (page = 1): Promise<{ data: IVenda[], totalCount: number } | Error> => {
    try {
        const { data, headers } = await Api.get(`/vendas?_page=${page}&_limit=10`);

        if (data) {
            return {
                data: data,
                totalCount: Number(headers['x-total-count'] || data.length),
            };
        }

        return new Error('Erro ao listar vendas.');
    } catch (error) {
        console.error(error);
        return new Error((error as { message: string }).message || 'Erro ao listar vendas.');
    }
};

export const VendaService = {
    create,
    getAll,
};
