import type_mc from "../assets/type_mc.svg";
import { Button } from "@mui/material";

const Header = () => {
    return (
        <header className="justify-between items-center w-full shadow-md flex flex-row p-2"
            style={{
                position: "fixed",
                zIndex: 1000,
                backgroundColor: "var(--background-color)",
            }}
        >
            <img src={type_mc} alt="Tipografia Market Coffee" className="m-2" />
            <div className="gap-2 m-2">
                <Button variant="contained">Logout</Button>
            </div>
        </header>
    )
}

export default Header;