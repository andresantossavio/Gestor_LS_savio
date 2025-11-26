import React, { useEffect, useState, useCallback } from 'react'
import Header from '../components/Header'

const apiBase = '/api'

// Componente do Formulário de Usuário
function UsuarioForm({ usuarioParaEditar, onFormSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    nome: '',
    login: '',
    email: '',
    senha: '',
    perfil: 'Usuario',
    ...usuarioParaEditar // Se usuarioParaEditar existir, ele sobrescreve os campos acima
  });

  const isEditing = !!usuarioParaEditar?.id;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const url = isEditing ? `${apiBase}/usuarios/${usuarioParaEditar.id}` : `${apiBase}/usuarios`;
    const method = isEditing ? 'PUT' : 'POST';

    // Não envia a senha se não for alterada na edição
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
      if (!response.ok) throw new Error('Falha ao salvar usuário');
      onFormSubmit(); // Avisa o componente pai para fechar o form e recarregar a lista
    } catch (err) {
      console.error(err);
      alert('Erro ao salvar usuário!');
    }
  };

  return (
    <div style={{ border: '1px solid #ccc', padding: '20px', marginTop: '20px', marginBottom: '20px' }}>
      <h3>{isEditing ? 'Editar Usuário' : 'Novo Usuário'}</h3>
      <form onSubmit={handleSubmit}>
        <input name="nome" value={formData.nome} onChange={handleChange} placeholder="Nome Completo" required style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
        <input name="login" value={formData.login} onChange={handleChange} placeholder="Login" required style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
        <input type="email" name="email" value={formData.email} onChange={handleChange} placeholder="Email" style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
        <input type="password" name="senha" value={formData.senha} onChange={handleChange} placeholder={isEditing ? 'Nova Senha (deixe em branco para não alterar)' : 'Senha'} required={!isEditing} style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
        <select name="perfil" value={formData.perfil} onChange={handleChange} style={{ display: 'block', marginBottom: '10px' }}>
          <option value="Usuario">Usuário</option>
          <option value="Administrador">Administrador</option>
        </select>
        <button type="submit">Salvar</button>
        <button type="button" onClick={onCancel} style={{ marginLeft: '10px' }}>Cancelar</button>
      </form>
    </div>
  );
}

export default function Cadastros() {
  const [usuarios, setUsuarios] = useState([])
  const [exibirForm, setExibirForm] = useState(false);
  const [usuarioParaEditar, setUsuarioParaEditar] = useState(null);

  const load = useCallback(async () => {
    try {
      const resp = await fetch(`${apiBase}/usuarios`);
      if (!resp.ok) throw new Error(`Erro na API: ${resp.status}`);
      const json = await resp.json();
      setUsuarios(json);
    } catch (err) { console.error(err); }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleEdit = (usuario) => {
    setUsuarioParaEditar(usuario);
    setExibirForm(true);
  };

  const handleDelete = async (usuarioId) => {
    if (window.confirm('Tem certeza que deseja excluir este usuário?')) {
      try {
        await fetch(`${apiBase}/usuarios/${usuarioId}`, { method: 'DELETE' });
        // Após deletar, recarrega a lista
        load();
      } catch (err) {
        console.error(err);
        alert('Falha ao excluir usuário.');
      }
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <Header title="Cadastros (Usuários)" />
      {!exibirForm && <button onClick={() => { setUsuarioParaEditar(null); setExibirForm(true); }}>Novo Usuário</button>}
      
      {exibirForm && <UsuarioForm 
        usuarioParaEditar={usuarioParaEditar} 
        onFormSubmit={() => { setExibirForm(false); load(); }} 
        onCancel={() => setExibirForm(false)} 
      />}

      <div style={{ marginTop: 20 }}>
        {usuarios.length === 0 && <div>Nenhum usuário</div>}
        {usuarios.map(u => (
          <div key={u.id} style={{ borderBottom: '1px solid #ddd', padding: 10 }}>
            <strong>{u.nome}</strong> — {u.login} — {u.email} — {u.perfil}
            <button onClick={() => handleEdit(u)} style={{ marginLeft: '20px' }}>Editar</button>
            <button onClick={() => handleDelete(u.id)} style={{ marginLeft: '10px' }}>Excluir</button>
          </div>
        ))}
      </div>
    </div>
  )
}
