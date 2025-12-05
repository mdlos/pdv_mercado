import React, { useState } from "react";
import { Button, TextField, ThemeProvider } from "@mui/material";
import { Theme } from "../shared/themes/Theme";
import { motion } from "framer-motion";
import { useAuth } from "../shared/contexts/AuthContext";

import logo_mc from "../assets/logo_mc.svg";
import bg_login from "../assets/bg_login.png";

import { CircularProgress, Alert } from "@mui/material";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>(undefined);

  const { login } = useAuth();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setError(undefined);

    try {
      const result = await login({ email, senha: password });
      if (result) {
        setError(result);
      }
    } catch (err) {
      setError("Erro inesperado ao tentar fazer login.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <ThemeProvider theme={Theme}>
      {/* Background da página */}
      <img src={bg_login} className="z-0 w-full h-full" alt="Background de Login"
        style={{
          position: "fixed",
          filter: "brightness(0.5) blur(5px)",
          objectFit: "cover",
        }} />
      {/* Container principal do login */}
      <motion.div
        className="flex items-center justify-center h-screen w-screen z-10"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1.2 }}>
        <div className="flex flex-col items-center justify-center"
          style={{
            position: "relative",
            backgroundColor: "var(--background-color-secondary)",
            borderRadius: "10px",
            boxShadow: "0 0 10px rgba(0, 0, 0, 0.1)",
            padding: "10vh",
            gap: "1rem",
            minWidth: "70vh",
            minHeight: "80vh",

          }}>
          <img src={logo_mc} alt="Logo da Market Coffee" className="w-100 p-0 m-0" />

          <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-100">
            {error && <Alert severity="error">{error}</Alert>}

            <TextField
              type="email"
              label="Email"
              value={email}
              disabled={isLoading}
              onChange={(e) => setEmail(e.target.value)}
              fullWidth
            />
            <TextField
              type="password"
              label="Senha"
              value={password}
              disabled={isLoading}
              onChange={(e) => setPassword(e.target.value)}
              fullWidth
            />
            <Button
              type="submit"
              variant="contained"
              disabled={isLoading}
              size="large"
            >
              {isLoading ? <CircularProgress size={24} color="inherit" /> : 'Login'}
            </Button>
          </form>
        </div>
      </motion.div>
    </ThemeProvider>
  )
}

export default Login;
