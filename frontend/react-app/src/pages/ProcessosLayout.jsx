import React from 'react';
import { Outlet } from 'react-router-dom';

// Este componente serve como um "layout" para as rotas aninhadas de processos.
// O <Outlet> renderizará o componente da rota filha correspondente.
export default function ProcessosLayout() {
  return <Outlet />;
}