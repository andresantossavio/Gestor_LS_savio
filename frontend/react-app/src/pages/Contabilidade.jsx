import React, { useEffect, useState } from 'react'
import Header from '../components/Header'

export default function Contabilidade(){
  const [pagamentos, setPagamentos] = useState([])
  const apiBase = '/api'

  async function load(){
    try{
      const resp = await fetch(`${apiBase}/pagamentos`)
      const json = await resp.json()
      setPagamentos(json)
    }catch(err){ console.error(err) }
  }

  useEffect(()=>{ load() }, [])

  return (
    <div style={{ padding: 20 }}>
      <Header title="Contabilidade" />
      <button onClick={load}>Carregar Pagamentos</button>
      <div style={{ marginTop: 20 }}>
        {pagamentos.length === 0 && <div>Nenhum pagamento encontrado</div>}
        {pagamentos.map(p => (
          <div key={p.id} style={{ borderBottom: '1px solid #ddd', padding: 10 }}>
            <strong>{p.descricao}</strong> — Valor: {p.valor} — Tipo: {p.tipo} — Data: {p.data_pagamento}
          </div>
        ))}
      </div>
    </div>
  )
}
