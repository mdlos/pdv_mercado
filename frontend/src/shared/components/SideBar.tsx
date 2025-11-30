import { List, Drawer, Box, Icon, ListItemButton, ListItemIcon, ListItemText, useTheme, useMediaQuery, Button } from "@mui/material";
import HomeIcon from '@mui/icons-material/Home';
import { useNavigate } from "react-router-dom";
import { useDrawerContext } from "../contexts/DrawerContext";

import React from "react";

interface IListItemLinkProps {
  to: String;
  label: string;
  icon: String;
  onClick?: () => void | undefined;
}

const ListItemLink: React.FC<IListItemLinkProps> = ({ to, label, icon, onClick }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(to as string);
    onClick?.(); // Verifica se onClick existe antes de chamar
  };
    
  return (
    <ListItemButton onClick={handleClick}>
      <ListItemIcon>
          <Icon>{icon}</Icon>
      </ListItemIcon>
      <ListItemText primary={label} />
    </ListItemButton>
  );
};

const SideBar: React.FC = ({  }) => {
  const theme = useTheme();
  const smDown = useMediaQuery(theme.breakpoints.down("sm"));
  
  const { isDrawerOpen, toggleDrawerOpen } = useDrawerContext();

  return (
    <>
      <Drawer 
        open={isDrawerOpen} 
        onClose={toggleDrawerOpen}
        variant={smDown ? "temporary" : "persistent"}
        anchor="left"
        sx={{
        "& .MuiDrawer-paper": {
          marginTop: "100px",               // altura da AppBar
          height: "calc(100% - 100px)",     // evita sobrepor o rodapé
          width: theme.spacing(32),
        },
      }}>
        <Box 
          width={theme.spacing(32)} 
          className="relative flex flex-col h-full justify-start items-center">
          <List component="nav" className="w-full">
            <ListItemButton>
              <ListItemIcon>
                <HomeIcon />
              </ListItemIcon>
              <ListItemText primary="Página Inicial" />
            </ListItemButton>  
          </List>
        </Box>
      </Drawer>

      <Box width={smDown ? 0 : theme.spacing(32)}>
        
      </Box>
    </>
  );
};

export default SideBar;