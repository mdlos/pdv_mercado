import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

export const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();

  return isAuthenticated ? <>{children}</> : <Navigate to="/" />;
}