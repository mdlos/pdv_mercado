import { Box, Button, Paper } from '@mui/material';
import { type ReactNode } from 'react';

interface IFiltersProps {
    onSearch: () => void;
    onClear: () => void;
    children: ReactNode;
}

export const Filters = ({ onSearch, onClear, children }: IFiltersProps) => {
    return (
        <Paper elevation={1} sx={{ padding: 2, marginBottom: 2, display: 'flex', width: '100', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            {children}

            <Box sx={{ display: 'flex', gap: 1, marginLeft: 'auto' }}>
                <Button variant="contained" color="primary" onClick={onSearch}>
                    Pesquisar
                </Button>
                <Button variant="outlined" color="warning" onClick={onClear}>
                    Limpar
                </Button>
            </Box>
        </Paper>
    );
};
