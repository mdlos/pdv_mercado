import { List, Drawer, Box, ListItemButton, ListItemIcon, ListItemText, useTheme, useMediaQuery } from "@mui/material";
import { useMatch, useNavigate, useResolvedPath } from "react-router-dom";
import { useDrawerContext } from "../contexts/DrawerContext";

import React from "react";

interface IListItemLinkProps {
  to: string;
  label: string;
  icon: React.ReactNode;
  onClick?: () => void | undefined;
}

const ListItemLink: React.FC<IListItemLinkProps> = ({ to, label, icon, onClick }) => {
  const navigate = useNavigate();

  const resolvedPath = useResolvedPath(to);
  const match = useMatch({ path: resolvedPath.pathname, end: false });

  const handleClick = () => {
    navigate(to as string);
    onClick?.(); // Verifica se onClick existe antes de chamar
  };
    
  return (
    <ListItemButton selected={!!match} onClick={handleClick} className="flex flex-rows items-center gap-2">
      <ListItemIcon className="ml-4">
        {icon}
      </ListItemIcon>
      <ListItemText primary={label} />
    </ListItemButton>
  );
};

const SideBar: React.FC = ({  }) => {
  const theme = useTheme();
  const smDown = useMediaQuery(theme.breakpoints.down("sm"));
  
  const { isDrawerOpen, toggleDrawerOpen, drawerOptions } = useDrawerContext();

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
          overflow: "hidden",
        },
      }}>
        <Box 
          width={theme.spacing(32)} 
          className="relative flex flex-col h-full justify-start items-center">
          <List component="nav" className="w-full">
            {drawerOptions.map(drawerOption => (
              <ListItemLink 
                to={drawerOption.path}
                key={drawerOption.path}
                icon={drawerOption.icon}
                label={drawerOption.label}
                onClick={smDown ? toggleDrawerOpen : undefined}
              /> 
            ))}
          </List>
        </Box>
      </Drawer>

      <Box width={smDown ? 0 : theme.spacing(32)}>
        
      </Box>
    </>
  );
};

export default SideBar;