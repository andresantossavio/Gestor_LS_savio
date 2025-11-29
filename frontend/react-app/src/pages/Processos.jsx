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
    <div className="content">
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <Header title="Processos" />
          {!exibirForm && (
            <button onClick={() => { setProcessoParaEditar(null); setExibirForm(true); }} className="btn btn-primary">
              + Novo Processo
            </button>
          )}
        </div>
      </div>

      {exibirForm && (
        <ProcessoForm
          processoParaEditar={processoParaEditar}
          onFormSubmit={() => { setExibirForm(false); load(); }}
          onCancel={() => setExibirForm(false)}
        />
      )}

      {!exibirForm && (
        <div className="card">
          {processos.length === 0 && <p style={{ textAlign: 'center', color: '#6b7280' }}>Nenhum processo cadastrado</p>}
          {processos.length > 0 && (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Nº do Processo</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Autor</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Réu</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Categoria</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Tipo</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Comarca/UF</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Cliente</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Status</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {processos.map((p) => (
                    <tr key={p.id} style={{ borderBottom: '1px solid #e5e7eb', transition: 'background-color 0.2s' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                      <td style={{ padding: '12px' }}>
                        <Link to={`/processos/${p.id}`} style={{ color: '#FFC107', fontWeight: '600', textDecoration: 'none' }}>
                          {p.numero || 'Ver Detalhes'}
                        </Link>
                      </td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>{p.autor || 'N/A'}</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>{p.reu || 'N/A'}</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>{p.categoria || 'N/A'}</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>{p.tipo || 'N/A'}</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>{p.comarca || 'N/A'} - {p.uf || 'N/A'}</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>{p.cliente?.nome || 'N/A'}</td>
                      <td style={{ padding: '12px' }}>
                        <span style={{ padding: '4px 12px', borderRadius: '12px', fontSize: '12px', fontWeight: '600', backgroundColor: p.status === 'Ativo' ? '#dcfce7' : '#fee2e2', color: p.status === 'Ativo' ? '#166534' : '#991b1b' }}>
                          {p.status || 'N/A'}
                        </span>
                      </td>
                      <td style={{ padding: '12px' }}>
                        <button onClick={() => handleEdit(p)} className="btn btn-primary" style={{ marginRight: '8px', padding: '6px 12px', fontSize: '13px' }}>Editar</button>
                        <button onClick={() => handleDelete(p.id)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '13px' }}>Excluir</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
