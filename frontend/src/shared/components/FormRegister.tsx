import * as React from 'react';
import { Box, Typography, Modal, useMediaQuery, type Theme, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const style = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '40vw',
    minWidth: '400px',
    bgcolor: 'background.paper',
    borderRadius: '10px',
    boxShadow: 24,
    p: 4,
};

interface IFormRegisterProps {
    title: string;
    children: React.ReactNode;
    buttons: React.ReactNode[];
    open: boolean;
    onClose: () => void;
}

const FormRegister: React.FC<IFormRegisterProps> = ({ title, children, buttons, open, onClose }) => {
    const smUpMd = useMediaQuery((theme: Theme) => theme.breakpoints.up("md"));

    return (
        <Modal
            open={open}
            onClose={onClose}
            aria-labelledby="modal-modal-title"
            aria-describedby="modal-modal-description"
        >
            <Box sx={style} className="flex flex-col gap-12">
                {smUpMd ? (
                    <Box className="flex flex-row justify-between">
                        <Typography id="modal-modal-title" color="textPrimary" variant="h5" component="h2">
                            {title}
                        </Typography>
                        <IconButton color="error" onClick={onClose}>
                            <CloseIcon />
                        </IconButton>
                    </Box>
                ) : (
                    <Box className="flex flex-row justify-between">
                        <Typography id="modal-modal-title" color="textPrimary" variant="h6" component="h2">
                            {title}
                        </Typography>
                        <IconButton color="error" onClick={onClose}>
                            <CloseIcon />
                        </IconButton>
                    </Box>
                )}
                <Box className="flex flex-col">
                    {children}
                </Box>
                <Box className="flex flex-row justify-end gap-2">
                    {buttons}
                </Box>
            </Box>
        </Modal>
    );
}

export default FormRegister;