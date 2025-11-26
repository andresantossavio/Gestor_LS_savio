import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

// Importe seus componentes de página
import Dashboard from './pages/Dashboard';
import Processos from './pages/Processos';
import Cadastros from './pages/Cadastros';
import Usuarios from './pages/Usuarios';
import Contabilidade from './pages/Contabilidade'; // 1. Importar o novo componente

import './App.css'; // Você pode criar este arquivo para estilização

function App() {
  return (
    <BrowserRouter>
      <div className="app-container" style={{ display: 'flex' }}>
        <nav className="sidebar" style={{ width: '220px', background: '#f4f4f4', padding: '20px' }}>
          <h2>Gestor LS</h2>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li style={{ marginBottom: '10px' }}><Link to="/">Dashboard</Link></li>
            <li style={{ marginBottom: '10px' }}><Link to="/processos">Processos</Link></li>
            <li style={{ marginBottom: '10px' }}><Link to="/cadastros">Cadastros</Link></li>
            <li style={{ marginBottom: '10px' }}><Link to="/usuarios">Usuários</Link></li>
            <li style={{ marginBottom: '10px' }}><Link to="/contabilidade">Contabilidade</Link></li> {/* 2. Adicionar o link no menu */}
          </ul>
        </nav>
        <main className="content" style={{ flex: 1, padding: '20px' }}>
          <Routes>
            {/* Defina qual componente renderizar para cada rota */}
            <Route path="/" element={<Dashboard />} />
            <Route path="/processos" element={<Processos />} />
            <Route path="/cadastros" element={<Cadastros />} />
            <Route path="/usuarios" element={<Usuarios />} />
            <Route path="/contabilidade" element={<Contabilidade />} /> {/* 3. Adicionar a rota */}
            
            {/* Rota para página não encontrada */}
            <Route path="*" element={<h1>404: Página Não Encontrada</h1>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;