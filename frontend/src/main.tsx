import { StrictMode } from 'react';
import { Theme } from './shared/themes/Theme';
import { createRoot } from 'react-dom/client';
import { ThemeProvider } from '@emotion/react';

import './index.css';

import Login from './pages/login';
import Header from './shared/components/Header';
import SideBar from './shared/components/SideBar';
import { DrawerProvider } from './shared/contexts';
import { BrowserRouter } from 'react-router-dom';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider theme={Theme}>
      <BrowserRouter>
        <DrawerProvider>
          {/* <Login /> */}
          <Header />
          <SideBar />
        </DrawerProvider>
      </BrowserRouter>
    </ThemeProvider>
  </StrictMode>,
)
