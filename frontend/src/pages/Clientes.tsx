import { useState } from 'react';
import { LayoutBase } from "../shared/layouts/LayoutBase";
import FormRegister from "../shared/components/FormRegister";
import { Button, Fab, TextField, Box } from "@mui/material";
import AddIcon from '@mui/icons-material/Add';

const Clientes = () => {
    const [open, setOpen] = useState(false);

    return (
        <LayoutBase titulo={"Clientes"}>
            <FormRegister
                title="Cadastro de Usuário"
                buttons={[
                    <Button variant="outlined" color="error">Resetar</Button>,
                    <Button variant="contained" color="primary">Salvar</Button>,
                ]}
                open={open}
                onClose={() => setOpen(false)}
            >
                <Box className="flex flex-col gap-4">
                    <TextField id="outlined-basic" label="Nome Completo" variant="outlined" size='small' />
                    <Box className="flex flex-row justify-between gap-2 w-full">
                        <TextField id="outlined-basic" className="w-100" label="CPF" variant="outlined" size='small' />
                        <TextField id="outlined-basic" className="w-40" label="Sexo" variant="outlined" size='small' />
                    </Box>
                    <Box className="flex flex-row justify-between gap-2 w-full">
                        <TextField id="outlined-basic" className="w-100" label="Celular" variant="outlined" size='small' />
                        <TextField id="outlined-basic" className="w-100" label="Email" variant="outlined" size='small' />
                    </Box>
                    <Box className="flex flex-row justify-between gap-2 w-full">
                        <TextField id="outlined-basic" className="w-100" label="Logradouro" variant="outlined" size='small' />
                        <TextField id="outlined-basic" className="w-40" label="Número" variant="outlined" size='small' />
                    </Box>
                    <Box className="flex flex-row justify-between gap-2 w-full">
                        <TextField id="outlined-basic" className="w-100" label="Cidade" variant="outlined" size='small' />
                        <TextField id="outlined-basic" className="w-100" label="Estado" variant="outlined" size='small' />
                    </Box>
                </Box>

            </FormRegister>

            <Fab
                color="primary"
                aria-label="add"
                sx={{ position: "fixed", bottom: "20px", right: "20px" }}
                onClick={() => setOpen(true)}
            >
                <AddIcon />
            </Fab>
        </LayoutBase>
    )
};

export default Clientes;