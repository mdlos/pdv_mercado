import { IconButton, Button, useMediaQuery, type Theme } from "@mui/material";
import { Environment } from "../environment";
import { useDrawerContext } from "../contexts";
import { useAuth } from "../contexts/AuthContext"


import MenuIcon from '@mui/icons-material/Menu';
import StorefrontIcon from '@mui/icons-material/Storefront';

import type_mc from "../../assets/type_mc.svg";

const Header = () => {
  const smUp = useMediaQuery((theme: Theme) => theme.breakpoints.up("sm"));
  const smUpMd = useMediaQuery((theme: Theme) => theme.breakpoints.up("md"));

  const { logout } = useAuth();
  const { toggleDrawerOpen } = useDrawerContext();

  return (
    <header className="justify-between items-center w-full shadow-md flex flex-row p-2"
      style={{
        position: "fixed",
        zIndex: 1000,
        backgroundColor: "var(--background-color)",
        height: "100px",
      }}>
      <div className="flex flex-row items-center">
        {/* Botão menu para a sidebar */}
        <IconButton
          onClick={toggleDrawerOpen}
        >
          <MenuIcon />
        </IconButton>
        <img src={type_mc} alt="Tipografia Market Coffee" className="m-2" />
      </div>
      {smUp && (
        <div className="gap-2 m-2 px-4 flex flex-row">
          {/* Botão Frente de Caixa */}
          <Button
            variant="outlined"
            sx={{
              whiteSpace: "nowrap",
              textOverflow: "ellipsis",
              overflow: "hidden",
            }}
            startIcon={smUpMd && (<StorefrontIcon />)}
            onClick={() => window.open(Environment.ROTA_FRENTE_DE_CAIXA, "_blank")}>Frente de caixa</Button>
          {/* Botão Sair - volta para a tela de login */}
          <Button
            variant="contained"
            color="error"
            onClick={logout}>Sair</Button>
        </div>
      )}
    </header>
  )
}

export default Header;