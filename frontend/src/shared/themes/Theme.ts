import { createTheme } from "@mui/material/styles";

export const Theme = createTheme({
    palette: {
        mode: 'dark',
        primary: {
            main: '#4487f4',
            light: '#5594fd',
        },
        secondary: {
            main: '#f50057',
        },
        background: {
            default: '#071827',
        },
        text: {
            primary: '#f4f4f4',
            secondary: '#f4f4f4',
            disabled: '#f4f4f4',
        },
    },
})
