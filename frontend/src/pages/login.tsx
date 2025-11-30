import React, { useState } from "react";
import { Button, TextField, ThemeProvider } from "@mui/material";
import { Theme } from "../shared/themes/Theme";
import { motion } from "framer-motion";

import logo_mc from "../assets/logo_mc.svg";
import bg_login from "../assets/bg_login.png";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");  
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    console.log(username, password);
  }  

  return (
    <ThemeProvider theme={Theme}>
      <img src={bg_login} className="z-0 w-full h-full" alt="Background de Login"
        style={{
          position: "absolute",
          filter: "brightness(0.5) blur(5px)",
          objectFit: "cover",
        }}/>
        <motion.div
          className="flex flex-col items-center justify-center h-screen"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.2 }}>
          <div className="z-10 flex flex-col items-center justify-center"
            style={{
              position: "relative",
              backgroundColor: "var(--background-color)",
              borderRadius: "10px",
              boxShadow: "0 0 10px rgba(0, 0, 0, 0.1)",
              padding: "10vh",
              gap: "1rem",
              minWidth: "70vh",
              minHeight: "80vh",
            
            }}>
            <img src={logo_mc} alt="Logo da Market Coffee" className="w-100 p-0 m-0" />
            <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-100">
              <TextField
                type="email"
                label="Email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}/>
              <TextField
                type="password"
                label="Senha"
                value={password}
                onChange={(e) => setPassword(e.target.value)}/>
              <Button type="submit" variant="contained">Login</Button>
            </form>
          </div>
        </motion.div>
    </ThemeProvider>
  )
}

export default Login;
