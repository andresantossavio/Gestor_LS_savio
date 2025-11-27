import React, { useEffect, useState, useCallback } from 'react';
import Header from '../components/Header';
import { Link } from 'react-router-dom';
import ProcessoForm from '../components/ProcessoForm'; // Importa o formulário

const apiBase = '/api';

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
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Categoria</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Tipo</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Comarca/UF</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Cliente</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Status</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Ações</th>
              </tr>
            </thead>
            <tbody>
              {processos.map((p) => (
                <tr key={p.id}>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                    <Link to={`/processos/${p.id}`}>{p.numero || 'Ver Detalhes'}</Link>
                  </td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.autor || 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.reu || 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.categoria || 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.tipo || 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.comarca || 'N/A'} - {p.uf || 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.cliente?.nome || 'N/A'}</td>
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
