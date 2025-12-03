import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Typography,
    LinearProgress
} from '@mui/material';
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
}

export const ListTable = <T extends { id?: string | number } | any>({ columns, rows, isLoading }: IListTableProps<T>) => {
    return (
        <TableContainer component={Paper} elevation={1} sx={{ width: '100%', overflow: 'hidden' }}>
            {isLoading && <LinearProgress />}
            <Table stickyHeader aria-label="custom table">
                <TableHead>
                    <TableRow>
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
                    </TableRow>
                </TableHead>
                <TableBody>
                    {!isLoading && rows.length === 0 && (
                        <TableRow>
                            <TableCell colSpan={columns.length} align="center">
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
                            </TableRow>
                        );
                    })}
                </TableBody>
            </Table>
        </TableContainer>
    );
};
