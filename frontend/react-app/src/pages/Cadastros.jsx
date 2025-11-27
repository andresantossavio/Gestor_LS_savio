import React, { useEffect, useState, useCallback } from 'react';
import Header from '../components/Header';

const apiBase = '/api';

// --- Componente do Formulário de Usuário ---
function UsuarioForm({ usuarioParaEditar, onFormSubmit, onCancel }) {
  const isEditing = !!usuarioParaEditar?.id;
  const initialState = isEditing
    ? { ...usuarioParaEditar, senha: '' } // Limpa a senha ao editar
    : { nome: '', email: '', login: '', senha: '', perfil: 'Padrão' };

  const [formData, setFormData] = useState(initialState);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const url = isEditing ? `${apiBase}/usuarios/${usuarioParaEditar.id}` : `${apiBase}/usuarios`;
    const method = isEditing ? 'PUT' : 'POST';

    // Remove a senha do corpo se não for fornecida durante a edição
    const body = { ...formData };
    if (isEditing && !body.senha) {
      delete body.senha;
    }

    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Falha ao salvar usuário');
      }
      onFormSubmit(); // Callback para recarregar a lista e fechar o form
    } catch (err) {
      console.error(err);
      alert(`Erro ao salvar usuário: ${err.message}`);
    }
  };

  return (
    <div style={{ border: '1px solid #ccc', padding: '20px', margin: '20px 0' }}>
      <h3>{isEditing ? 'Editar Usuário' : 'Novo Usuário'}</h3>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
        <input name="nome" value={formData.nome} onChange={handleChange} placeholder="Nome Completo" required />
        <input name="email" type="email" value={formData.email} onChange={handleChange} placeholder="E-mail" />
        <input name="login" value={formData.login} onChange={handleChange} placeholder="Login de Acesso" required />
        <input name="senha" type="password" value={formData.senha} onChange={handleChange} placeholder={isEditing ? "Nova Senha (deixe em branco para manter)" : "Senha"} required={!isEditing} />
        <select name="perfil" value={formData.perfil} onChange={handleChange}>
          <option value="Administrador">Administrador</option>
          <option value="Padrão">Padrão</option>
        </select>
        <div>
          <button type="submit">Salvar</button>
          <button type="button" onClick={onCancel} style={{ marginLeft: '10px' }}>Cancelar</button>
        </div>
      </form>
    </div>
  );
}


// --- Componente Principal de Cadastros de Usuários ---
export default function Cadastros() {
  const [usuarios, setUsuarios] = useState([]);
  const [exibirForm, setExibirForm] = useState(false);
  const [usuarioParaEditar, setUsuarioParaEditar] = useState(null);

  const loadUsuarios = useCallback(async () => {
    try {
      const res = await fetch(`${apiBase}/usuarios`);
      if (!res.ok) throw new Error(`Erro na API: ${res.status}`);
      const json = await res.json();
      setUsuarios(json);
    } catch (err) {
      console.error("Falha ao carregar usuários:", err);
    }
  }, []);

  useEffect(() => {
    loadUsuarios();
  }, [loadUsuarios]);

  const handleEdit = (usuario) => {
    setUsuarioParaEditar(usuario);
    setExibirForm(true);
  };

  const handleDelete = async (usuarioId) => {
    if (window.confirm('Tem certeza que deseja excluir este usuário?')) {
      try {
        await fetch(`${apiBase}/usuarios/${usuarioId}`, { method: 'DELETE' });
        loadUsuarios(); // Recarrega a lista após a exclusão
      } catch (err) {
        console.error(err);
        alert('Falha ao excluir usuário.');
      }
    }
  };

  const handleFormSubmit = () => {
    setExibirForm(false);
    setUsuarioParaEditar(null);
    loadUsuarios();
  };

  return (
    <div style={{ padding: 20 }}>
      <Header title="Gerenciamento de Usuários" />
      
      {!exibirForm && (
        <button onClick={() => { setUsuarioParaEditar(null); setExibirForm(true); }}>
          Novo Usuário
        </button>
      )}

      {exibirForm && (
        <UsuarioForm
          usuarioParaEditar={usuarioParaEditar}
          onFormSubmit={handleFormSubmit}
          onCancel={() => { setExibirForm(false); setUsuarioParaEditar(null); }}
        />
      )}

      <div style={{ marginTop: 20 }}>
        {usuarios.length === 0 && !exibirForm && <div>Nenhum usuário cadastrado.</div>}
        {usuarios.length > 0 && (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Nome</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Login</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Email</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Perfil</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Ações</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map((user) => (
                <tr key={user.id}>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{user.nome}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{user.login}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{user.email || 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{user.perfil}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                    <button onClick={() => handleEdit(user)}>Editar</button>
                    <button onClick={() => handleDelete(user.id)} style={{ marginLeft: '10px' }}>Excluir</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
