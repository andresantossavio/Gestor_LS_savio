import React, { useEffect, useState } from 'react'
import Header from '../components/Header'

export default function Tarefas() {
  const [tarefas, setTarefas] = useState([])
  const apiBase = '/api'

  async function load() {
    try {
      const res = await fetch(`${apiBase}/tarefas`)
      const json = await res.json()
      setTarefas(json)
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <div style={{ padding: 20 }}>
      <Header title="Tarefas" />
      <button onClick={load}>Carregar</button>
      <div style={{ marginTop: 20 }}>
        {tarefas.length === 0 && <div>Nenhuma tarefa</div>}
        {tarefas.map(t => (
          <div key={t.id} style={{ borderBottom: '1px solid #ddd', padding: 10 }}>
            <strong>{t.titulo}</strong> — {t.responsavel_id || ''} — {t.prazo || ''}
          </div>
        ))}
      </div>
    </div>
  )
}
