import { StrictMode } from 'react';
import { Theme } from './shared/themes/Theme';
import { createRoot } from 'react-dom/client';
import { ThemeProvider } from '@emotion/react';

import './index.css';

import { DrawerProvider, AuthProvider, CaixaProvider } from './shared/contexts';
import { BrowserRouter } from 'react-router-dom';
import { AppRoutes } from './routes';


createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider theme={Theme}>
      <BrowserRouter>
        <AuthProvider>
          <CaixaProvider>
            <DrawerProvider>
              <AppRoutes />
            </DrawerProvider>
          </CaixaProvider>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  </StrictMode>,
)
