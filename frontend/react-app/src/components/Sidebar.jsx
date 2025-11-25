import React from 'react'
import { Link } from 'react-router-dom'

export default function Sidebar(){
  const items = [
    { name: 'Dashboard', to: '/' },
    { name: 'Cadastros', to: '/cadastros' },
    { name: 'Processos', to: '/processos' },
    { name: 'Contabilidade', to: '/contabilidade' },
    { name: 'Tarefas', to: '/tarefas' },
    { name: 'Clientes', to: '/clientes' },
    { name: 'Configurações', to: '/config' }
  ]

  return (
    <aside className="sidebar">
      <div className="logo">Gestão Leão e Savio</div>
      <nav>
        {items.map(i => (
          <Link key={i.to} to={i.to} className="menu-item">{i.name}</Link>
        ))}
      </nav>
    </aside>
  )
}
