import React, { useEffect, useState } from 'react';

const apiBase = '/api';

export default function AndamentoForm({ processoId, onClose, onFormSubmit }) {
  const [formData, setFormData] = useState({
    tipo_andamento_id: '',
    descricao_complementar: '',
    data: new Date().toISOString().split('T')[0],
  });

  const [tiposAndamento, setTiposAndamento] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Carregar tipos de andamento
    const fetchTipos = async () => {
      try {
        const res = await fetch(`${apiBase}/tipos-andamento`);
        if (res.ok) {
          const tipos = await res.json();
          setTiposAndamento(tipos);
        }
      } catch (err) {
        console.error('Erro ao carregar tipos de andamento:', err);
      }
    };

    fetchTipos();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        processo_id: parseInt(processoId),
        tipo_andamento_id: parseInt(formData.tipo_andamento_id),
        descricao_complementar: formData.descricao_complementar || null,
        data: formData.data,
      };

      const res = await fetch(`${apiBase}/andamentos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Erro ao criar andamento');
      }

      alert('Andamento criado com sucesso!');
      onFormSubmit();
    } catch (err) {
      console.error(err);
      alert('Erro ao criar andamento: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{
          width: '90%',
          maxWidth: '600px',
          maxHeight: '90vh',
          overflowY: 'auto',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{ marginTop: 0 }}>Novo Andamento Processual</h2>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 500 }}>
              Tipo de Andamento *
            </label>
            <select
              name="tipo_andamento_id"
              value={formData.tipo_andamento_id}
              onChange={handleChange}
              required
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db' }}
            >
              <option value="">Selecione...</option>
              {tiposAndamento.map(tipo => (
                <option key={tipo.id} value={tipo.id}>{tipo.nome}</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 500 }}>
              Data do Andamento *
            </label>
            <input
              type="date"
              name="data"
              value={formData.data}
              onChange={handleChange}
              required
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db' }}
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 500 }}>
              Descrição Complementar
            </label>
            <textarea
              name="descricao_complementar"
              value={formData.descricao_complementar}
              onChange={handleChange}
              rows={4}
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db' }}
              placeholder="Detalhes do andamento processual..."
            />
          </div>

          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
