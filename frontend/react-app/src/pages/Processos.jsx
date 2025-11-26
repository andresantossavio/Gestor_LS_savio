import React, { useEffect, useState, useCallback } from 'react';
import Header from '../components/Header';

const apiBase = '/api';

// Componente do Formulário de Processo
function ProcessoForm({ processoParaEditar, onFormSubmit, onCancel }) {
  const isEditing = !!processoParaEditar?.id;

  const initialState = isEditing ? { ...processoParaEditar } : {
    numero: '',
    autor: '',
    reu: '',
    uf: '',
    comarca: '',
    vara: '',
    fase: '',
    status: '',
    data_abertura: '',
    observacoes: '',
    cliente_id: ''
  };
  const [formData, setFormData] = useState(initialState);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const url = isEditing ? `${apiBase}/processos/${processoParaEditar.id}` : `${apiBase}/processos`;
    const method = isEditing ? 'PUT' : 'POST';

    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Falha ao salvar processo');
      }
      onFormSubmit();
    } catch (err) {
      console.error(err);
      alert(`Erro ao salvar processo: ${err.message}`);
    }
  };

  return (
    <div style={{ border: '1px solid #ccc', padding: '20px', margin: '20px 0' }}>
      <h3>{isEditing ? 'Editar Processo' : 'Novo Processo'}</h3>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
        <input name="numero" value={formData.numero} onChange={handleChange} placeholder="Número do Processo" />
        <input name="autor" value={formData.autor} onChange={handleChange} placeholder="Autor" />
        <input name="reu" value={formData.reu} onChange={handleChange} placeholder="Réu" />
        <input name="uf" value={formData.uf} onChange={handleChange} placeholder="UF" />
        <input name="comarca" value={formData.comarca} onChange={handleChange} placeholder="Comarca" />
        <input name="vara" value={formData.vara} onChange={handleChange} placeholder="Vara/Juízo" />
        <select name="fase" value={formData.fase} onChange={handleChange}>
          <option value="">Selecione a Fase</option>
          <option value="Conhecimento">Conhecimento</option>
          <option value="Cumprimento de Sentença">Cumprimento de Sentença</option>
        </select>
        <input name="status" value={formData.status} onChange={handleChange} placeholder="Status" />
        <input name="data_abertura" value={formData.data_abertura} onChange={handleChange} placeholder="Data de Abertura" type="date" />
        <input name="cliente_id" value={formData.cliente_id} onChange={handleChange} placeholder="ID do Cliente" type="number" style={{ gridColumn: '1 / -1' }}/>
        <textarea name="observacoes" value={formData.observacoes} onChange={handleChange} placeholder="Observações" style={{ gridColumn: '1 / -1', minHeight: '80px' }} />
        <div>
          <button type="submit">Salvar</button>
          <button type="button" onClick={onCancel} style={{ marginLeft: '10px' }}>Cancelar</button>
        </div>
      </form>
    </div>
  );
}

export default function Processos() {
  const [processos, setProcessos] = useState([]);
  const [exibirForm, setExibirForm] = useState(false);
  const [processoParaEditar, setProcessoParaEditar] = useState(null);

  const load = useCallback(async () => {
    try {
      const res = await fetch(`${apiBase}/processos`);
      if (!res.ok) throw new Error(`Erro na API: ${res.status}`);
      const json = await res.json();
      setProcessos(json);
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleEdit = (processo) => {
    setProcessoParaEditar(processo);
    setExibirForm(true);
  };

  const handleDelete = async (processoId) => {
    if (window.confirm('Tem certeza que deseja excluir este processo?')) {
      try {
        await fetch(`${apiBase}/processos/${processoId}`, { method: 'DELETE' });
        load();
      } catch (err) {
        console.error(err);
        alert('Falha ao excluir processo.');
      }
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <Header title="Processos" />
      {!exibirForm && <button onClick={() => { setProcessoParaEditar(null); setExibirForm(true); }}>Novo Processo</button>}
      {exibirForm && <ProcessoForm
        processoParaEditar={processoParaEditar}
        onFormSubmit={() => { setExibirForm(false); load(); }}
        onCancel={() => setExibirForm(false)}
      />}
      <div style={{ marginTop: 20 }}>
        {processos.length === 0 && <div>Nenhum processo</div>}
        {processos.length > 0 && (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Nº do Processo</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Autor</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Réu</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Comarca/UF</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Cliente</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Status</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Ações</th>
              </tr>
            </thead>
            <tbody>
              {processos.map((p) => (
                <tr key={p.id}>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.numero || 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.autor || 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.reu || 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.comarca || 'N/A'} - {p.uf || 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.cliente ? p.cliente.nome : 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.status || 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                    <button onClick={() => handleEdit(p)}>Editar</button>
                    <button onClick={() => handleDelete(p.id)} style={{ marginLeft: '10px' }}>Excluir</button>
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
