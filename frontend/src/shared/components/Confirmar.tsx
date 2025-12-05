import React from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography } from '@mui/material';

interface IConfirmarProps {
    open: boolean;
    title: string;
    message: string;
    onClose: () => void;
    onConfirm: () => void;
}

export const Confirmar: React.FC<IConfirmarProps> = ({ open, title, message, onClose, onConfirm }) => {
    return (
        <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
            <DialogTitle>{title}</DialogTitle>
            <DialogContent>
                <Typography>{message}</Typography>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">
                    Cancelar
                </Button>
                <Button onClick={onConfirm} color="error" variant="contained" autoFocus>
                    Confirmar
                </Button>
            </DialogActions>
        </Dialog>
    );
};
