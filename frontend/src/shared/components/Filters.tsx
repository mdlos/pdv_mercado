import { Box, Button, TextField, Paper, InputAdornment } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { useState } from 'react';

interface IFilterValues {
    nome: string;
    dataRegistro: string;
    id: string;
}

interface IFiltersProps {
    onSearch: (filters: IFilterValues) => void;
    onClear: () => void;
}

export const Filters = ({ onSearch, onClear }: IFiltersProps) => {
    const [filters, setFilters] = useState<IFilterValues>({
        nome: '',
        dataRegistro: '',
        id: ''
    });

    const handleChange = (key: keyof IFilterValues, value: string) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const handleSearch = () => {
        onSearch(filters);
    };

    const handleClear = () => {
        setFilters({ nome: '', dataRegistro: '', id: '' });
        onClear();
    };

    return (
        <Paper elevation={1} sx={{ padding: 2, marginBottom: 2, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            <TextField
                size="small"
                label="ID"
                value={filters.id}
                onChange={(e) => handleChange('id', e.target.value)}
                sx={{ width: '100px' }}
            />
            <TextField
                size="small"
                label="Nome"
                value={filters.nome}
                onChange={(e) => handleChange('nome', e.target.value)}
                sx={{ flex: 1, minWidth: '200px' }}
                InputProps={{
                    startAdornment: (
                        <InputAdornment position="start">
                            <SearchIcon />
                        </InputAdornment>
                    ),
                }}
            />
            <TextField
                size="small"
                label="Data de Registro"
                type="date"
                value={filters.dataRegistro}
                onChange={(e) => handleChange('dataRegistro', e.target.value)}
                InputLabelProps={{ shrink: true }}
                sx={{ width: '180px' }}
            />

            <Box sx={{ display: 'flex', gap: 1 }}>
                <Button variant="contained" color="primary" onClick={handleSearch}>
                    Pesquisar
                </Button>
                <Button variant="outlined" color="warning" onClick={handleClear}>
                    Limpar
                </Button>
            </Box>
        </Paper>
    );
};
