import React from 'react';
import { Link, Outlet } from 'react-router-dom';
import Header from '../components/Header';

export default function Cadastros() {
  return (
    <div style={{ padding: 20 }}>
      <Header title="Cadastros" />
      <div style={{ display: 'flex' }}>
        <nav style={{ borderRight: '1px solid #ccc', paddingRight: '20px', marginRight: '20px' }}>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li style={{ marginBottom: '10px' }}><Link to="clientes">Clientes</Link></li>
            {/* Adicione outros links de cadastro aqui no futuro */}
          </ul>
        </nav>
        <div style={{ flex: 1 }}>
          {/* O Outlet renderiza a rota filha correspondente (ex: Clientes) */}
          <Outlet />
        </div>
      </div>
    </div>
  );
}
