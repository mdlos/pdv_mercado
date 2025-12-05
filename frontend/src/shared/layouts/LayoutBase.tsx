import { Box, Typography, useMediaQuery, useTheme, type Theme } from "@mui/material"
import React from "react"

interface ILayoutBaseProps {
  titulo: string;
  children: React.ReactNode
}

export const LayoutBase: React.FC<ILayoutBaseProps> = ({ children, titulo }) => {
  const smDown = useMediaQuery((theme: Theme) => theme.breakpoints.down('sm'));
  const mdDown = useMediaQuery((theme: Theme) => theme.breakpoints.down('md'));
  const theme = useTheme();

  return (
    <>
      <Box className="h-full w-full flex flex-col" gap={1}>
        <Box className="flex items-center" height={theme.spacing(6)}>
          <Typography
            fontWeight="bold"
            whiteSpace="nowrap"
            textOverflow="ellipsis"
            color="var(--font-color)"
            variant={smDown ? 'h5' : mdDown ? 'h4' : 'h4'}
          >
            {titulo}
          </Typography>
        </Box>

        <Box flex={1} overflow="auto">
          {children}
        </Box>
      </Box>
    </>
  )
}