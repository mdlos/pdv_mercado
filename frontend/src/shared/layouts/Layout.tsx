import React from "react";
import Header from "../components/Header";
import SideBar from "../components/SideBar";
import { useDrawerContext } from "../contexts";

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isDrawerOpen } = useDrawerContext(); // Estado da sidebar

  return (
    <>
      <Header /> {/* Header fixa no topo */}
      <SideBar /> {/* Sidebar fixa na lateral */}
      <main
        style={{
          marginTop: "100px", // Espaço para a Header
          marginLeft: isDrawerOpen ? "256px" : "0px", // Ajusta dinamicamente com base na sidebar
          transition: "margin-left 0.3s", // Animação suave
          padding: "16px",
        }}
      >
        {children} {/* Conteúdo das páginas */}
      </main>
    </>
  );
};

export default Layout;