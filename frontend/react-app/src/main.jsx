import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

// Importe seus componentes de página
import Dashboard from './pages/Dashboard'
import ProcessosLayout from './pages/ProcessosLayout'
import ProcessoDetalhe from './pages/ProcessoDetalhe'
import Processos from './pages/Processos'
import Clientes from './pages/Clientes'
import ClienteDetalhe from './pages/ClienteDetalhe'
import Cadastros from './pages/Cadastros'
import Usuarios from './pages/Usuarios'
import Config from './pages/Config'
import ConfigFeriados from './pages/ConfigFeriados'
import Tarefas from './pages/Tarefas'
import DashboardTarefas from './pages/DashboardTarefas'
import Contabilidade from './pages/Contabilidade'
import EntradaForm from './pages/EntradaForm'
import DespesaForm from './pages/DespesaForm'
import SocioPage from './pages/SocioPage'
import DRE from './pages/DRE'
import ProLabore from './pages/ProLabore'
import ConfigSimples from './pages/ConfigSimples'
import Lancamentos from './pages/Lancamentos'
import PlanoContas from './pages/PlanoContas'
import LancamentosContabeis from './pages/LancamentosContabeis'
import Balanco from './pages/Balanco'
import DMPL from './pages/DMPL'
import DFC from './pages/DFC'
import Sidebar from './components/Sidebar'

import './styles.css';

// Updated 2025-11-28 21:03 - Removed balance icon
function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', height: '100vh', background: '#f8f9fa', position: 'relative' }}>
        <Sidebar />
        <main style={{ flex: 1, padding: '32px', overflow: 'auto', background: 'linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%)', position: 'relative', zIndex: 0 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/processos" element={<ProcessosLayout />}>
              <Route index element={<Processos />} />
              <Route path=":processoId" element={<ProcessoDetalhe />} />
            </Route>
            <Route path="/cadastros" element={<Cadastros />} />
            <Route path="/clientes" element={<Clientes />} />
            <Route path="/clientes/:clienteId" element={<ClienteDetalhe />} />
            <Route path="/usuarios" element={<Usuarios />} />
            
            {/* Rotas de Tarefas */}
            <Route path="/tarefas/dashboard" element={<DashboardTarefas />} />
            <Route path="/tarefas" element={<Tarefas />} />
            
            {/* Rotas de Configuração */}
            <Route path="/configuracoes/feriados" element={<ConfigFeriados />} />
            <Route path="/configuracoes" element={<Config />} />
            <Route path="/config" element={<Config />} />
            
            {/* Rotas de Contabilidade */}
            <Route path="/contabilidade/entradas/nova" element={<EntradaForm />} />
            <Route path="/contabilidade/despesas/nova" element={<DespesaForm />} />
            {/* Gerenciar Entradas/Despesas */}
            <Route path="/contabilidade/lancamentos" element={<Lancamentos />} />
            {/* Lançamentos Contábeis */}
            <Route path="/contabilidade/lancamentos-contabeis" element={<LancamentosContabeis />} />
            <Route path="/contabilidade/plano-contas" element={<PlanoContas />} />
            <Route path="/contabilidade/balanco" element={<Balanco />} />
            <Route path="/contabilidade/dmpl" element={<DMPL />} />
            <Route path="/contabilidade/dfc" element={<DFC />} />
            <Route path="/contabilidade/socios" element={<SocioPage />} />
            <Route path="/contabilidade/dre" element={<DRE />} />
            <Route path="/contabilidade/pro-labore" element={<ProLabore />} />
            <Route path="/contabilidade/config-simples" element={<ConfigSimples />} />
            <Route path="/contabilidade" element={<Contabilidade />} />
            
            <Route path="*" element={<h1>404: Página Não Encontrada</h1>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

createRoot(document.getElementById('root')).render(<App />)
