import React, { useEffect, useState, useCallback } from 'react';
import Header from '../components/Header';

export default function Processos() {
  const [processos, setProcessos] = useState([]);
  const apiBase = '/api';

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

  return (
    <div style={{ padding: 20 }}>
      <Header title="Processos" />
      <button onClick={load}>Carregar Processos</button>
      <div style={{ marginTop: 20 }}>
        {processos.length === 0 && <div>Nenhum processo</div>}
        {processos.length > 0 && (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Número</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Autor</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Réu</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Cliente</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Status</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Observações</th>
              </tr>
            </thead>
            <tbody>
              {processos.map((p) => (
                <tr key={p.id}>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.numero || 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.autor || 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.reu || 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.cliente ? p.cliente.nome : 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.status || 'N/A'}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{p.observacoes || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
