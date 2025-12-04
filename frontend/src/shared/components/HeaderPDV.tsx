import { useState } from 'react';
import { Button } from "@mui/material";
import { Confirmar } from "./Confirmar";
import type_mc from "../../assets/type_mc.svg";

const HeaderPDV = () => {
    const [openConfirm, setOpenConfirm] = useState(false);

    const handleCloseBox = () => {
        window.close();
    };

    return (
        <>
            <header className="justify-between items-center w-full shadow-md flex flex-row p-2"
                style={{
                    position: "fixed",
                    zIndex: 1000,
                    backgroundColor: "var(--background-color-secondary)",
                    height: "100px",
                    top: 0,
                    left: 0
                }}>
                <div className="flex flex-row items-center pl-4">
                    <img src={type_mc} alt="Tipografia Market Coffee" className="m-2" />
                </div>

                <div className="gap-2 m-2 px-4 flex flex-row">
                    <Button
                        variant="contained"
                        color="error"
                        onClick={() => setOpenConfirm(true)}
                    >
                        Fechar Caixa
                    </Button>
                </div>
            </header>

            <Confirmar
                open={openConfirm}
                title="Fechar Caixa"
                message="Deseja realmente fechar o caixa e sair?"
                onClose={() => setOpenConfirm(false)}
                onConfirm={handleCloseBox}
            />
        </>
    )
}

export default HeaderPDV;
