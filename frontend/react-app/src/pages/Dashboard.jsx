import React from 'react'
import Header from '../components/Header'

export default function Dashboard(){
  return (
    <div style={{ padding: 20 }}>
      <Header title="Dashboard" />
      <p>Resumo do sistema (KPIs, gráficos e widgets).</p>
    </div>
  )
}
