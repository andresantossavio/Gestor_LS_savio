import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

// Importe seus componentes de página  
import Dashboard from './pages/Dashboard.jsx'
import ProcessosLayout from './pages/ProcessosLayout.jsx'
import ProcessoDetalhe from './pages/ProcessoDetalhe.jsx'
import Processos from './pages/Processos.jsx'
import Clientes from './pages/Clientes.jsx'
import Cadastros from './pages/Cadastros.jsx'
import Usuarios from './pages/Usuarios.jsx'
import Config from './pages/Config.jsx'
import ConfigFeriados from './pages/ConfigFeriados.jsx'
import Contabilidade from './pages/Contabilidade.jsx'
import EntradaForm from './pages/EntradaForm.jsx'
import DespesaForm from './pages/DespesaForm.jsx'
import SocioPage from './pages/SocioPage.jsx'
import DRE from './pages/DRE.jsx'
import ConfigSimples from './pages/ConfigSimples.jsx'
import DashboardTarefas from './pages/DashboardTarefas.jsx'
import Tarefas from './pages/Tarefas.jsx'

import './styles.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app-container" style={{ display: 'flex' }}>
        <nav className="sidebar">
          <h2 className="logo">Gestor LS</h2>
          <ul>
            <li><Link to="/" className="menu-item">Dashboard</Link></li>
            <li><Link to="/processos" className="menu-item">Processos</Link></li>
            <li><Link to="/tarefas" className="menu-item">Tarefas</Link></li>
            <li><Link to="/tarefas/dashboard" className="menu-item submenu-item">📊 Dashboard Tarefas</Link></li>
            <li><Link to="/cadastros" className="menu-item">Cadastros</Link></li>
            <li><Link to="/usuarios" className="menu-item">Usuários</Link></li>
            <li><Link to="/configuracoes" className="menu-item">Configurações</Link></li>
            <li><Link to="/contabilidade" className="menu-item">Contabilidade</Link></li>
          </ul>
        </nav>
        <main className="content" style={{ flex: 1, padding: '20px' }}>
          <Routes>
            {/* Defina qual componente renderizar para cada rota */}
            <Route path="/" element={<Dashboard />} />
            <Route path="/processos" element={<ProcessosLayout />}>
              <Route index element={<Processos />} />
              <Route path=":processoId" element={<ProcessoDetalhe />} />
            </Route>
            <Route path="/cadastros" element={<Cadastros />}>
              {/* Rotas aninhadas dentro de Cadastros */}
              <Route path="clientes" element={<Clientes />} />
            </Route>
            <Route path="/usuarios" element={<Usuarios />} />
            
            {/* Rotas mais específicas devem vir ANTES das rotas genéricas */}
            <Route path="/configuracoes/feriados" element={<ConfigFeriados />} />
            <Route path="/configuracoes" element={<Config />} />
            
            <Route path="/tarefas/dashboard" element={<DashboardTarefas />} />
            <Route path="/tarefas" element={<Tarefas />} />
            
            <Route path="/contabilidade/entradas/nova" element={<EntradaForm />} />
            <Route path="/contabilidade/despesas/nova" element={<DespesaForm />} />
            <Route path="/contabilidade/socios" element={<SocioPage />} />
            <Route path="/contabilidade/dre" element={<DRE />} />
            <Route path="/contabilidade/config-simples" element={<ConfigSimples />} />
            <Route path="/contabilidade" element={<Contabilidade />} />
            
            {/* Rota para página não encontrada */}
            <Route path="*" element={<h1>404: Página Não Encontrada</h1>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;