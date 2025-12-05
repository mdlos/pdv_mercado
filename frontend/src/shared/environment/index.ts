export const Environment = {
  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:3000/api',

  LIMITE_LINHAS: import.meta.env.VITE_LIMITE_LINHAS ? Number(import.meta.env.VITE_LIMITE_LINHAS) : 5,

  TIMEOUT_API: import.meta.env.VITE_TIMEOUT_API ? Number(import.meta.env.VITE_TIMEOUT_API) : 60000, 

  INPUT_DEBOUNCE: import.meta.env.VITE_INPUT_DEBOUNCE ? Number(import.meta.env.VITE_INPUT_DEBOUNCE) : 300,

 // Rotas das páginas
  ROTA_LOGIN: import.meta.env.VITE_ROTA_LOGIN || '/',
  ROTA_INICIAL: import.meta.env.VITE_ROTA_INICIAL || '/pagina-inicial',
  ROTA_CLIENTES: import.meta.env.VITE_ROTA_CLIENTES || '/clientes',
  ROTA_PRODUTOS: import.meta.env.VITE_ROTA_PRODUTOS || '/produtos',
  ROTA_VENDAS: import.meta.env.VITE_ROTA_VENDAS || '/vendas',
  ROTA_FUNCIONARIOS: import.meta.env.VITE_ROTA_FUNCIONARIOS || '/funcionarios',
  ROTA_CAIXAS: import.meta.env.VITE_ROTA_CAIXAS || '/caixas',
  ROTA_FRENTE_DE_CAIXA: import.meta.env.VITE_ROTA_FRENTE_DE_CAIXA || '/frente-de-caixa',

};