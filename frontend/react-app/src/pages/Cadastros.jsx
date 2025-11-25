import React, { useEffect, useState } from 'react'
import Header from '../components/Header'

export default function Cadastros(){
  const [usuarios, setUsuarios] = useState([])
  const apiBase = '/api'

  async function load(){
    try{
      const resp = await fetch(`${apiBase}/usuarios`)
      const json = await resp.json()
      setUsuarios(json)
    }catch(err){ console.error(err) }
  }

  useEffect(()=>{ load() }, [])

  return (
    <div style={{ padding: 20 }}>
      <Header title="Cadastros (Usuários)" />
      <button onClick={load}>Carregar</button>
      <div style={{ marginTop: 20 }}>
        {usuarios.length === 0 && <div>Nenhum usuário</div>}
        {usuarios.map(u => (
          <div key={u.id} style={{ borderBottom: '1px solid #ddd', padding: 10 }}>
            <strong>{u.nome}</strong> — {u.login} — {u.email} — {u.perfil}
          </div>
        ))}
      </div>
    </div>
  )
}
