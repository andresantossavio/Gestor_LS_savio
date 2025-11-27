import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

// Importe seus componentes de página
import Dashboard from './pages/Dashboard';
import ProcessosLayout from './pages/ProcessosLayout'; // Importa o novo layout
import ProcessoDetalhe from './pages/ProcessoDetalhe'; // Importa a nova página
import Processos from './pages/Processos';
import Clientes from './pages/Clientes';
import Cadastros from './pages/Cadastros';
import Usuarios from './pages/Usuarios';
import Config from './pages/Config';
import Contabilidade from './pages/Contabilidade'; // 1. Importar o novo componente

import './App.css'; // Você pode criar este arquivo para estilização

function App() {
  return (
    <BrowserRouter basename="/frontend">
      <div className="app-container" style={{ display: 'flex' }}>
        <nav className="sidebar" style={{ width: '220px', background: '#f4f4f4', padding: '20px' }}>
          <h2>Gestor LS</h2>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li style={{ marginBottom: '10px' }}><Link to="/">Dashboard</Link></li>
            <li style={{ marginBottom: '10px' }}><Link to="/processos">Processos</Link></li>
            <li style={{ marginBottom: '10px' }}><Link to="/cadastros">Cadastros</Link></li>
            <li style={{ marginBottom: '10px' }}><Link to="/usuarios">Usuários</Link></li>
            <li style={{ marginBottom: '10px' }}><Link to="/configuracoes">Configurações</Link></li>
            <li style={{ marginBottom: '10px' }}><Link to="/contabilidade">Contabilidade</Link></li> {/* 2. Adicionar o link no menu */}
          </ul>
        </nav>
        <main className="content" style={{ flex: 1, padding: '20px' }}>
          <Routes>
            {/* Defina qual componente renderizar para cada rota */}
            <Route path="/" element={<Dashboard />} />
            <Route path="/processos" element={<ProcessosLayout />}>
              <Route index element={<Processos />} /> {/* Rota para a lista em /processos */}
              <Route path=":processoId" element={<ProcessoDetalhe />} /> {/* Rota para o detalhe em /processos/:id */}
            </Route>
            <Route path="/cadastros" element={<Cadastros />}>
              {/* Rotas aninhadas dentro de Cadastros */}
              <Route path="clientes" element={<Clientes />} />
            </Route>
            <Route path="/usuarios" element={<Usuarios />} /> {/* Mantemos a rota de usuários */}
            <Route path="/configuracoes" element={<Config />} />
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