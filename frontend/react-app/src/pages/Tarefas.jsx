import React, { useEffect, useState, useCallback } from 'react'
import Header from '../components/Header'

export default function Tarefas() {
  const [tarefas, setTarefas] = useState([])
  const apiBase = '/api'

  const load = useCallback(async () => {
    try {
      const res = await fetch(`${apiBase}/tarefas`);
      if (!res.ok) throw new Error(`Erro na API: ${res.status}`);
      const json = await res.json();
      setTarefas(json);
    } catch (err) {
      console.error(err);
    }
  }, []); // useCallback com array de dependências vazio

  useEffect(() => { load() }, [load])

  return (
    <div style={{ padding: 20 }}>
      <Header title="Tarefas" />
      <button onClick={load}>Carregar</button>
      <div style={{ marginTop: 20 }}>
        {tarefas.length === 0 && <div>Nenhuma tarefa</div>}
        {tarefas.map(t => (
          <div key={t.id} style={{ borderBottom: '1px solid #ddd', padding: 10 }}>
            <strong>Tipo ID: {t.tipo_tarefa_id}</strong> — {t.descricao_complementar || 'Sem descrição'} — Prazo: {t.prazo || 'N/A'}
          </div>
        ))}
      </div>
    </div>
  )
}
