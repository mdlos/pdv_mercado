import * as React from 'react';
import { Box, Button, Typography, Modal, useMediaQuery, type Theme } from '@mui/material';

const style = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '40vw',
    minWidth: '500px',
    bgcolor: 'background.paper',
    border: '2px solid #000',
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
    const smUp = useMediaQuery((theme: Theme) => theme.breakpoints.up("sm"));
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
                        <Button onClick={onClose}>X</Button>
                    </Box>
                ) : (
                    <Box className="flex flex-row justify-between">
                        <Typography id="modal-modal-title" color="textPrimary" variant="h6" component="h2">
                            {title}
                        </Typography>
                        <Button onClick={onClose}>X</Button>
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