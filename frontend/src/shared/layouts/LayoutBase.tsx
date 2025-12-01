import { Box, Typography, useMediaQuery, useTheme, type Theme } from "@mui/material"
import React from "react"

interface ILayoutBaseProps {
  titulo: string;
  children: React.ReactNode
}

export const LayoutBase: React.FC<ILayoutBaseProps> = ({ children, titulo }) => {
  const smDown = useMediaQuery((theme: Theme) => theme.breakpoints.down('md'));
  const mdDown = useMediaQuery((theme: Theme) => theme.breakpoints.down('md'));
  const theme = useTheme();

  return (
    <>
      <Box className="h-100 flex flex-col gap-1">
        <Box className="p-4 flex items-center" height={theme.spacing(12)}>
          <Typography 
            fontWeight="bold" 
            whiteSpace="nowrap"
            textOverflow="ellipsis"
            variant={smDown ? 'h5' : mdDown ? 'h4' : 'h3'} 
          >
            {titulo}
          </Typography>
        </Box>
  
        <Box>
          Barra de Ferramentas
        </Box>  
  
        <Box flex={1} overflow="auto">
          {children}
        </Box>  
      </Box>
    </>
  )
}