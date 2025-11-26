import React, { useEffect, useState, useCallback } from 'react'
import Header from '../components/Header'

export default function Clientes() {
  const [clientes, setClientes] = useState([])
  const apiBase = '/api'

  const load = useCallback(async () => {
    try {
      const res = await fetch(`${apiBase}/clientes`);
      if (!res.ok) throw new Error(`Erro na API: ${res.status}`);
      const json = await res.json();
      setClientes(json);
    } catch (err) {
      console.error(err);
    }
  }, []); // useCallback com array de dependências vazio

  useEffect(() => { load() }, [load])

  return (
    <div style={{ padding: 20 }}>
      <Header title="Clientes" />
      <button onClick={load}>Carregar</button>
      <div style={{ marginTop: 20 }}>
        {clientes.length === 0 && <div>Nenhum cliente</div>}
        {clientes.map(c => (
          <div key={c.id} style={{ borderBottom: '1px solid #ddd', padding: 10 }}>
            <strong>{c.nome}</strong> — {c.cpf_cnpj} — {c.telefone} — {c.email}
          </div>
        ))}
      </div>
    </div>
  )
}
