import { AxiosError, type AxiosResponse } from 'axios';
import { Environment } from '../../../environment';

export const errorInterceptor = (error: AxiosError) => {
    if (error.message === 'Network Error') {
        return Promise.reject(new Error('Erro de conexão.'));
    }

    if (error.response?.status === 401) {
        localStorage.removeItem('auth_data');

        if (window.location.pathname !== Environment.ROTA_LOGIN) {
            window.location.href = Environment.ROTA_LOGIN;
        }
    }

    return Promise.reject(error);
};

export const responseInterceptor = (response: AxiosResponse) => {
    return response;
};
