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
    <div className="content">
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <Header title="Tarefas" />
          <button onClick={load} className="btn btn-primary">Atualizar</button>
        </div>
      </div>
      
      <div className="card">
        {tarefas.length === 0 && <p style={{ textAlign: 'center', color: '#6b7280' }}>Nenhuma tarefa cadastrada</p>}
        {tarefas.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {tarefas.map(t => (
              <div key={t.id} style={{ padding: '16px', backgroundColor: '#f9fafb', borderRadius: '8px', borderLeft: '4px solid #FFC107' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div>
                    <div style={{ fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                      Tipo ID: {t.tipo_tarefa_id}
                    </div>
                    <div style={{ color: '#6b7280', fontSize: '14px' }}>
                      {t.descricao_complementar || 'Sem descrição'}
                    </div>
                  </div>
                  <div style={{ padding: '4px 12px', borderRadius: '12px', fontSize: '12px', fontWeight: '600', backgroundColor: '#dbeafe', color: '#1e40af', whiteSpace: 'nowrap' }}>
                    Prazo: {t.prazo || 'N/A'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
