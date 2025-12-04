
import { Api } from '../axios_config';

export interface ILoginData {
    email: string;
    senha: string;
}

export interface IAuthResponse {
    cpf: string;
    nome: string;
    cargo: string;
    token: string;
}

const login = async (dados: ILoginData): Promise<IAuthResponse | Error> => {
    try {
        const { data } = await Api.post<IAuthResponse>('/auth/login', dados);

        if (data) {
            return data;
        }

        return new Error('Erro ao realizar login.');
    } catch (error) {
        const err = error as any;
        if (err.response && err.response.data) {
            return new Error(err.response.data.error || 'Erro ao realizar login.');
        }
        return new Error('Erro ao realizar login.');
    }
};

export const AuthService = {
    login,
};
