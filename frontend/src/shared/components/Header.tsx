import { IconButton, Button, useMediaQuery, type Theme } from "@mui/material";
import { useDrawerContext } from "../contexts";


import MenuIcon from '@mui/icons-material/Menu';
import StorefrontIcon from '@mui/icons-material/Storefront';

import type_mc from "../../assets/type_mc.svg";

const Header = () => {
  const smUp = useMediaQuery((theme: Theme) => theme.breakpoints.up("sm"));
  const smUpMd = useMediaQuery((theme: Theme) => theme.breakpoints.up("md"));
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
        <IconButton  
          onClick={toggleDrawerOpen}
        >
          <MenuIcon />
        </IconButton>
        <img src={type_mc} alt="Tipografia Market Coffee" className="m-2" />
      </div>
      {smUp && (
        <div className="gap-2 m-2 px-4 flex flex-row">
          <Button 
            variant="outlined"
            sx={{
              whiteSpace: "nowrap",
              textOverflow: "ellipsis",
              overflow: "hidden",
            }} 
            startIcon={smUpMd &&(<StorefrontIcon />)}>Frente de caixa</Button>
          <Button variant="contained" color="error">Sair</Button>
        </div>
      )}
    </header>
  )
}

export default Header;