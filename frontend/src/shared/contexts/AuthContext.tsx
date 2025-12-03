import { createContext, useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Environment } from "../environment";

interface IAuthOptions {
  email: string;
  password: string;
}

interface IAuthContextData {
  isAuthenticated: boolean;
  authOptions?: IAuthOptions;
  login: (options: IAuthOptions, callback?: () => void) => void;
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
    const storedAuth = localStorage.getItem('auth_data');
    return !!storedAuth;
  });

  const [authOptions, setAuthOptions] = useState<IAuthOptions | undefined>(() => {
    const storedAuth = localStorage.getItem('auth_data');
    if (storedAuth) {
      try {
        return JSON.parse(storedAuth);
      } catch (error) {
        console.error("Falha ao analisar os dados de autenticação.", error);
        return undefined;
      }
    }
    return undefined;
  });

  const navigate = useNavigate();

  const login = (options: IAuthOptions, callback?: () => void) => {
    localStorage.setItem('auth_data', JSON.stringify(options));
    setAuthOptions(options);
    setIsAuthenticated(true);

    if (callback) {
      callback();
    } else {
      navigate(Environment.ROTA_INICIAL);
    }
  }

  const logout = () => {
    localStorage.removeItem('auth_data');
    setIsAuthenticated(false);
    setAuthOptions(undefined);
    navigate(Environment.ROTA_LOGIN);
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, authOptions, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  return useContext(AuthContext);
}