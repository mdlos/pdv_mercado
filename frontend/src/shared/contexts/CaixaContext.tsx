import { createContext, useContext, useState } from "react";

interface ICaixaOptions {
  caixaAberto: boolean;
  operador: string | null;
  id: number | null;
  horaAbertura: Date | null;
  horaFechamento: Date | null;
  saldoInicial: number | null;
  saldoInformado: number | null;
}

interface ICaixaContextData {
  caixaOptions: ICaixaOptions;
  caixaAberto: boolean;
  abrirCaixa: (operador: string, saldoInicial: number) => void;
  fecharCaixa: (saldoInformado: number) => void;
}

const CaixaContext = createContext<ICaixaContextData>({} as ICaixaContextData);

export const useCaixaContext = () => useContext(CaixaContext);

export const CaixaProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [caixaOptions, setCaixa] = useState<ICaixaOptions>({
    caixaAberto: false,
    operador: null,
    id: null,
    horaAbertura: null,
    horaFechamento: null,
    saldoInicial: null,
    saldoInformado: null,
  });

  const abrirCaixa = (operador: string, saldoInicial: number) => {
    setCaixa({
      caixaAberto: true,
      operador,
      id: Date.now(),
      horaAbertura: new Date(),
      horaFechamento: null,
      saldoInicial,
      saldoInformado: null,
    });
  };

  const fecharCaixa = (saldoInformado: number) => {
    setCaixa(prev => ({
      ...prev,
      caixaAberto: false,
      horaFechamento: new Date(),
      saldoInformado
    }));
  };

  return (
    <CaixaContext.Provider value={{
      caixaOptions,
      caixaAberto: caixaOptions.caixaAberto,
      abrirCaixa,
      fecharCaixa,
    }}>
      {children}
    </CaixaContext.Provider>
  );
};
