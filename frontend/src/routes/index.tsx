import { Routes, Route, Navigate } from "react-router-dom";
import { useDrawerContext } from "../shared/contexts";
import { useEffect } from "react";

import HomeIcon from '@mui/icons-material/Home';
import PeopleAltIcon from '@mui/icons-material/PeopleAlt';
import LoyaltyIcon from '@mui/icons-material/Loyalty';
import LocalGroceryStoreIcon from '@mui/icons-material/LocalGroceryStore';
import AssignmentIndIcon from '@mui/icons-material/AssignmentInd';

import Home from '../pages/home';
import Layout from "../shared/layouts/Layout";

export const AppRoutes = () => {
  const { setDrawerOptions } = useDrawerContext();

  useEffect(() => {
    setDrawerOptions([
      {
        icon: <HomeIcon />,
        path: "/pagina-inicial",
        label: "Página Inicial",
      },
      {
        icon: <PeopleAltIcon />,
        path: "/clientes",
        label: "Clientes",
      },
      {
        icon: <LoyaltyIcon />,
        path: "/produtos",
        label: "Produtos",
      },
      {
        icon: <LocalGroceryStoreIcon />,
        path: "/vendas",
        label: "Vendas",
      },
      {
        icon: <AssignmentIndIcon />,
        path: "/funcionarios",
        label: "Funcionários",
      },
    ]);
  }, []);

  return (
    <Routes>
      <Route path="/pagina-inicial" element={<Layout><Home /></Layout>} />
      <Route path="/clientes" element={<Layout><div>Clientes</div></Layout>} />
      <Route path="/produtos" element={<Layout><div>Produtos</div></Layout>} />
      <Route path="/vendas" element={<Layout><div>Vendas</div></Layout>} />
      <Route path="/funcionarios" element={<Layout><div>Funcionários</div></Layout>} />
      <Route path="*" element={<Navigate to="/pagina-inicial" />} />
    </Routes>
  );
};