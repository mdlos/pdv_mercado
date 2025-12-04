import { Routes, Route, Navigate } from "react-router-dom";
import { useDrawerContext } from "../shared/contexts";
import { useAuthContext } from "../shared/contexts";
import { PrivateRoute } from "../shared/contexts/PrivateRoute";
import { useEffect } from "react";
import { Environment } from "../shared/environment";

import HomeIcon from '@mui/icons-material/Home';
import PeopleAltIcon from '@mui/icons-material/PeopleAlt';
import LoyaltyIcon from '@mui/icons-material/Loyalty';
import LocalGroceryStoreIcon from '@mui/icons-material/LocalGroceryStore';
import AssignmentIndIcon from '@mui/icons-material/AssignmentInd';
import StorefrontIcon from '@mui/icons-material/Storefront';

import Home from '../pages/Home';
import Login from "../pages/Login";
import FrenteDeCaixa from "../pages/FrenteDeCaixa";
import Clientes from "../pages/Clientes";
import Layout from "../shared/layouts/Layout";
import Produtos from "../pages/Produtos";

export const AppRoutes = () => {
  const { setDrawerOptions } = useDrawerContext();

  useEffect(() => {
    setDrawerOptions([
      {
        icon: <HomeIcon />,
        path: Environment.ROTA_INICIAL,
        label: "Página Inicial",
      },
      {
        icon: <PeopleAltIcon />,
        path: Environment.ROTA_CLIENTES,
        label: "Clientes",
      },
      {
        icon: <LoyaltyIcon />,
        path: Environment.ROTA_PRODUTOS,
        label: "Produtos",
      },
      {
        icon: <LocalGroceryStoreIcon />,
        path: Environment.ROTA_VENDAS,
        label: "Vendas",
      },
      {
        icon: <AssignmentIndIcon />,
        path: Environment.ROTA_FUNCIONARIOS,
        label: "Funcionários",
      },
      {
        icon: <StorefrontIcon />,
        path: Environment.ROTA_CAIXAS,
        label: "Caixas",
      },
    ]);
  }, []);

  return (
    <Routes>
      <Route path={Environment.ROTA_LOGIN} element={<Login />} />

      <Route path={Environment.ROTA_FRENTE_DE_CAIXA} element={
        // <PrivateRoute>
        <FrenteDeCaixa />
        // </PrivateRoute>  
      } />

      {/* Rota dos elementos da drawer */}
      <Route path={Environment.ROTA_INICIAL} element={
        // <PrivateRoute>
        <Layout><Home /></Layout>
        // </PrivateRoute>
      } />

      <Route path={Environment.ROTA_CLIENTES} element={<Layout><Clientes /></Layout>} />
      <Route path={Environment.ROTA_PRODUTOS} element={<Layout><Produtos /></Layout>} />
      <Route path={Environment.ROTA_VENDAS} element={<Layout><div>Vendas</div></Layout>} />
      <Route path={Environment.ROTA_FUNCIONARIOS} element={<Layout><div>Funcionários</div></Layout>} />
      <Route path={Environment.ROTA_CAIXAS} element={<Layout><div>Caixas</div></Layout>} />
      <Route path={Environment.ROTA_FRENTE_DE_CAIXA} element={<FrenteDeCaixa />} />

      {/* Qualquer rota n'ao e contrada volta para a pagina inicial */}
      <Route path="*" element={<Navigate to={Environment.ROTA_INICIAL} />} />
    </Routes>
  );
};