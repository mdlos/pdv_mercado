import { Button } from "@mui/material";
import { Routes, Route, Navigate } from "react-router-dom";

import { useDrawerContext } from "../shared/contexts";
import { useEffect } from "react";

import HomeIcon from '@mui/icons-material/Home';
import PeopleAltIcon from '@mui/icons-material/PeopleAlt';
import LoyaltyIcon from '@mui/icons-material/Loyalty';;
import LocalGroceryStoreIcon from '@mui/icons-material/LocalGroceryStore';
import AssignmentIndIcon from '@mui/icons-material/AssignmentInd';

export const AppRoutes = () => {
  const { toggleDrawerOpen, setDrawerOptions } = useDrawerContext();

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
      <Route path="/pagina-inicial" element=""/>
      <Route path="/clientes" element=""/>
      <Route path="/produtos" element=""/>
      <Route path="/vendas" element=""/>
      <Route path="/funcionarios" />
      <Route path="*" element={<Navigate to="/home" />} />
    </Routes>
  );
}