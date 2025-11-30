import type_mc from "../../assets/type_mc.svg";
import { IconButton, Button } from "@mui/material";
import MenuIcon from '@mui/icons-material/Menu';
import { useDrawerContext } from "../contexts";

const Header = () => {
  const { isDrawerOpen, toggleDrawerOpen } = useDrawerContext();

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
      <div className="gap-2 m-2">
        <Button variant="contained" color="error">Sair</Button>
      </div>
    </header>
  )
}

export default Header;