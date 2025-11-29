import React from 'react'
import Header from '../components/Header'

export default function Dashboard(){
  return (
    <div className="content">
      <div className="card">
        <Header title="Dashboard" />
      </div>
      <div className="card">
        <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#374151' }}>Resumo do Sistema</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
          <div style={{ padding: '20px', backgroundColor: '#fef3c7', borderRadius: '12px', textAlign: 'center' }}>
            <h4 style={{ margin: 0, color: '#92400e', fontSize: '2rem' }}>-</h4>
            <p style={{ margin: '8px 0 0 0', color: '#78350f', fontWeight: '600' }}>Processos Ativos</p>
          </div>
          <div style={{ padding: '20px', backgroundColor: '#dbeafe', borderRadius: '12px', textAlign: 'center' }}>
            <h4 style={{ margin: 0, color: '#1e3a8a', fontSize: '2rem' }}>-</h4>
            <p style={{ margin: '8px 0 0 0', color: '#1e40af', fontWeight: '600' }}>Tarefas Pendentes</p>
          </div>
          <div style={{ padding: '20px', backgroundColor: '#dcfce7', borderRadius: '12px', textAlign: 'center' }}>
            <h4 style={{ margin: 0, color: '#14532d', fontSize: '2rem' }}>-</h4>
            <p style={{ margin: '8px 0 0 0', color: '#166534', fontWeight: '600' }}>Clientes</p>
          </div>
        </div>
        <p style={{ marginTop: '30px', color: '#6b7280', textAlign: 'center' }}>KPIs, gráficos e widgets em desenvolvimento</p>
      </div>
    </div>
  )
}
