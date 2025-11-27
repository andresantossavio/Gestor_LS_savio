import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Clientes from './pages/Clientes'
import Processos from './pages/Processos'
import Tarefas from './pages/Tarefas'
import Dashboard from './pages/Dashboard'
import Cadastros from './pages/Cadastros'
import Contabilidade from './pages/Contabilidade'
import Config from './pages/Config'
import ProcessosLayout from './pages/ProcessosLayout'
import ProcessoDetalhe from './pages/ProcessoDetalhe'
import SocioPage from './pages/SocioPage'
import EntradaForm from './pages/EntradaForm'
import DespesaForm from './pages/DespesaForm'
import './styles.css'

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Sidebar />
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/cadastros" element={<Cadastros />} />
            <Route path="/processos" element={<ProcessosLayout />}>
              <Route index element={<Processos />} />
              <Route path=":processoId" element={<ProcessoDetalhe />} />
            </Route>
            <Route path="/contabilidade" element={<Contabilidade />} />
            <Route path="/contabilidade/socios" element={<SocioPage />} />
            <Route path="/contabilidade/entradas/nova" element={<EntradaForm />} />
            <Route path="/contabilidade/despesas/nova" element={<DespesaForm />} />
            <Route path="/tarefas" element={<Tarefas />} />
            <Route path="/clientes" element={<Clientes />} />
            <Route path="/config" element={<Config />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

createRoot(document.getElementById('root')).render(<App />)
