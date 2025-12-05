import React from "react";
import Header from "../components/Header";
import SideBar from "../components/SideBar";
import { useDrawerContext } from "../contexts";

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isDrawerOpen } = useDrawerContext();

  return (
    <>
      <Header />
      <SideBar />
      <main
        style={{
          display: "flex",
          width: isDrawerOpen ? "calc(100% - 256px)" : "100%",
          minHeight: "calc(100vh - 100px)", // Garante que o layout ocupe pelo menos a altura da tela menos o header
          marginTop: "100px", // Espaço para a Header
          marginLeft: isDrawerOpen ? "256px" : "0px", // Ajusta dinamicamente com base na sidebar
          transition: "margin-left 0.3s",
          padding: "16px",
        }}
      >
        {children}
      </main>
    </>
  );
};

export default Layout;