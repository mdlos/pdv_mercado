import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import Login from './pages/login';
import './index.css';
import { Theme } from './themes/Theme';
import { ThemeProvider } from '@emotion/react';
import Header from './components/Header';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider theme={Theme}>
      <Login />
      {/* <Header /> */}
    </ThemeProvider>
  </StrictMode>,
)
