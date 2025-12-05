
import { createContext, useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Environment } from "../environment";
import { AuthService, type IAuthResponse } from "../services/services/api/auth/AuthService";

interface ILoginData {
  email: string;
  senha: string;
}

interface IAuthContextData {
  isAuthenticated: boolean;
  user?: Omit<IAuthResponse, 'token'>;
  login: (dados: ILoginData) => Promise<string | void>;
  logout: () => void;
}

const AuthContext = createContext<IAuthContextData>({} as IAuthContextData);

export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext deve ser usado dentro de um AuthProvider");
  }
  return context;
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    const token = localStorage.getItem('ACCESS_TOKEN');
    return !!token;
  });

  const [user, setUser] = useState<Omit<IAuthResponse, 'token'> | undefined>(() => {
    const storedUser = localStorage.getItem('USER_DATA');
    if (storedUser) {
      try {
        return JSON.parse(storedUser);
      } catch (error) {
        console.error("Falha ao analisar os dados do usuário.", error);
        return undefined;
      }
    }
    return undefined;
  });

  const navigate = useNavigate();

  const login = async (dados: ILoginData): Promise<string | void> => {
    const result = await AuthService.login(dados);

    if (result instanceof Error) {
      return result.message;
    } else {
      localStorage.setItem('ACCESS_TOKEN', result.token);
      localStorage.setItem('USER_DATA', JSON.stringify({
        cpf: result.cpf,
        nome: result.nome,
        cargo: result.cargo
      }));

      setUser({
        cpf: result.cpf,
        nome: result.nome,
        cargo: result.cargo
      });
      setIsAuthenticated(true);
      navigate(Environment.ROTA_INICIAL);
    }
  }

  const logout = () => {
    localStorage.removeItem('ACCESS_TOKEN');
    localStorage.removeItem('USER_DATA');
    setIsAuthenticated(false);
    setUser(undefined);
    navigate(Environment.ROTA_LOGIN);
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  return useContext(AuthContext);
}