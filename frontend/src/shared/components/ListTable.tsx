import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Typography,
    TablePagination,
    LinearProgress,
    Box,
    IconButton
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import type { ReactNode } from 'react';

export interface IColumn<T = any> {
    id: string;
    label: string;
    minWidth?: number;
    align?: 'right' | 'left' | 'center';
    // Function to format or render custom content for the cell
    render?: (value: any, row: T) => ReactNode;
}

interface IListTableProps<T = any> {
    columns: IColumn<T>[];
    rows: T[];
    isLoading?: boolean;
    totalCount: number;
    page: number;
    rowsPerPage: number;
    onPageChange: (newPage: number) => void;
    onRowsPerPageChange: (newRowsPerPage: number) => void;
    onDelete?: (row: T) => void;
    onEdit?: (row: T) => void;
}

export const ListTable = <T extends { id?: string | number } | any>({
    columns,
    rows,
    isLoading,
    totalCount,
    page,
    rowsPerPage,
    onPageChange,
    onRowsPerPageChange,
    onDelete,
    onEdit
}: IListTableProps<T>) => {
    return (
        <Paper elevation={1} sx={{ width: '100%', overflow: 'hidden' }}>
            <TableContainer sx={{
                maxHeight: '23rem',
                '&::-webkit-scrollbar': {
                    width: '8px',
                    height: '8px',
                },
                '&::-webkit-scrollbar-track': {
                    backgroundColor: 'var(--background-color-secondary)',
                    borderRadius: '4px',
                },
                '&::-webkit-scrollbar-thumb': {
                    backgroundColor: 'var(--principal-color)',
                    borderRadius: '4px',
                },
                '&::-webkit-scrollbar-thumb:hover': {
                    backgroundColor: 'var(--btn-principal-hover)',
                },
            }}>
                {isLoading && <LinearProgress />}
                <Table stickyHeader aria-label="custom table">
                    <TableHead>
                        <TableRow sx={{ backgroundColor: 'var(--principal-color)' }}>
                            {columns.map((column) => (
                                <TableCell
                                    key={column.id}
                                    align={column.align || 'left'}
                                    style={{ minWidth: column.minWidth }}
                                    sx={{ fontWeight: 'bold' }}
                                >
                                    {column.label}
                                </TableCell>
                            ))}
                            {(onDelete || onEdit) && (
                                <TableCell align="center" sx={{ fontWeight: 'bold', width: 100 }}>

                                </TableCell>
                            )}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {!isLoading && rows.length === 0 && (
                            <TableRow>
                                <TableCell colSpan={columns.length + ((onDelete || onEdit) ? 1 : 0)} align="center">
                                    <Typography variant="body2" color="textSecondary">
                                        Nenhum registro encontrado.
                                    </Typography>
                                </TableCell>
                            </TableRow>
                        )}

                        {rows.map((row, index) => {
                            // Try to use a unique id from the row, otherwise fallback to index
                            const rowKey = (row as any).id || index;
                            return (
                                <TableRow hover role="checkbox" tabIndex={-1} key={rowKey}>
                                    {columns.map((column) => {
                                        const value = (row as any)[column.id];
                                        return (
                                            <TableCell key={column.id} align={column.align || 'left'}>
                                                {column.render ? column.render(value, row) : value}
                                            </TableCell>
                                        );
                                    })}
                                    {(onDelete || onEdit) && (
                                        <TableCell align="center">
                                            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1 }}>
                                                {onEdit && (
                                                    <IconButton onClick={() => onEdit(row)} color="primary" size="small">
                                                        <EditIcon />
                                                    </IconButton>
                                                )}
                                                {onDelete && (
                                                    <IconButton onClick={() => onDelete(row)} color="error" size="small">
                                                        <DeleteIcon />
                                                    </IconButton>
                                                )}
                                            </Box>
                                        </TableCell>
                                    )}
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
            </TableContainer>
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                <TablePagination
                    rowsPerPageOptions={[5]}
                    component="div"
                    count={totalCount}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onPageChange={(_, newPage) => onPageChange(newPage)}
                    onRowsPerPageChange={(event) => onRowsPerPageChange(parseInt(event.target.value, 10))}
                    labelRowsPerPage="Linhas por página:"
                    labelDisplayedRows={({ from, to, count }) => `${from}-${to} de ${count !== -1 ? count : `mais de ${to}`}`}
                />
            </Box>
        </Paper>
    );
};
