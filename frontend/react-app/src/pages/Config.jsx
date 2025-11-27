import React, { useEffect, useState, useCallback } from 'react';
import Header from '../components/Header';

export default function Config() {
  const [usuarios, setUsuarios] = useState([]);

  const loadUsuarios = useCallback(async () => {
    try {
      const res = await fetch('/api/usuarios');
      if (!res.ok) throw new Error('Falha ao buscar usuários');
      const data = await res.json();
      setUsuarios(data);
    } catch (err) {
      console.error(err);
      alert('Erro ao carregar usuários.');
    }
  }, []);

  useEffect(() => {
    loadUsuarios();
  }, [loadUsuarios]);

  const handlePerfilChange = async (usuarioId, novoPerfil) => {
    try {
      const response = await fetch(`/api/usuarios/${usuarioId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ perfil: novoPerfil }),
      });

      if (!response.ok) {
        throw new Error('Falha ao atualizar perfil do usuário.');
      }

      // Atualiza a lista localmente para refletir a mudança imediatamente
      setUsuarios(prevUsuarios =>
        prevUsuarios.map(u =>
          u.id === usuarioId ? { ...u, perfil: novoPerfil } : u
        )
      );

    } catch (err) {
      console.error(err);
      alert('Erro ao atualizar o perfil.');
      loadUsuarios(); // Recarrega a lista para reverter a mudança visual em caso de erro
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <Header title="Configurações" />
      <h2>Gerenciamento de Perfis de Usuário</h2>
      <div style={{ marginTop: 20 }}>
        {usuarios.map(usuario => (
          <div key={usuario.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #ddd', padding: '10px 0' }}>
            <span><strong>{usuario.nome}</strong> ({usuario.login})</span>
            <select value={usuario.perfil} onChange={(e) => handlePerfilChange(usuario.id, e.target.value)}>
              <option value="Usuario">Usuário</option>
              <option value="Administrador">Administrador</option>
            </select>
          </div>
        ))}
      </div>
    </div>
  )
}
