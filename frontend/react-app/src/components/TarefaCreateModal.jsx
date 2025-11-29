import React, { useEffect, useState } from 'react';

const apiBase = '/api';

export default function TarefaCreateModal({ processoId, onClose, onFormSubmit }) {
  const [formData, setFormData] = useState({
    tipo_tarefa_id: '',
    descricao_complementar: '',
    prazo_fatal: '',
    prazo_administrativo: '',
    responsavel_id: '',
    status: 'Pendente',
  });

  const [tiposTarefa, setTiposTarefa] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [tiposRes, usuariosRes] = await Promise.all([
          fetch(`${apiBase}/tipos-tarefa`),
          fetch(`${apiBase}/usuarios`)
        ]);
        
        if (tiposRes.ok) setTiposTarefa(await tiposRes.json());
        if (usuariosRes.ok) setUsuarios(await usuariosRes.json());
      } catch (err) {
        console.error('Erro ao carregar dados:', err);
      }
    };
    fetchData();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const cleanData = { ...formData };
      
      // Converter IDs para inteiro
      if (cleanData.tipo_tarefa_id) cleanData.tipo_tarefa_id = parseInt(cleanData.tipo_tarefa_id, 10);
      if (cleanData.responsavel_id) cleanData.responsavel_id = parseInt(cleanData.responsavel_id, 10);
      
      // Remover campos vazios
      Object.keys(cleanData).forEach(key => {
        if (cleanData[key] === '' || cleanData[key] === null) {
          delete cleanData[key];
        }
      });

      const response = await fetch(`${apiBase}/processos/${processoId}/tarefas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cleanData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Falha ao criar tarefa');
      }

      alert('Tarefa criada com sucesso!');
      onFormSubmit();
    } catch (err) {
      console.error(err);
      alert(`Erro ao criar tarefa: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    display: 'block',
    width: '100%',
    padding: '8px',
    marginBottom: '15px',
    borderRadius: '6px',
    border: '1px solid #d1d5db',
    fontSize: '14px',
  };

  const labelStyle = {
    display: 'block',
    marginBottom: '5px',
    fontSize: '14px',
    fontWeight: 500,
    color: '#374151',
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
          margin: '20px',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#374151' }}>
          Nova Tarefa
        </h3>

        <form onSubmit={handleSubmit}>
          {/* Tipo de Tarefa */}
          <div>
            <label style={labelStyle}>Tipo de Tarefa*</label>
            <select
              name="tipo_tarefa_id"
              value={formData.tipo_tarefa_id}
              onChange={handleChange}
              required
              style={inputStyle}
            >
              <option value="">Selecione o tipo</option>
              {tiposTarefa.map(tipo => (
                <option key={tipo.id} value={tipo.id}>
                  {tipo.nome}
                </option>
              ))}
            </select>
          </div>

          {/* Descrição Complementar */}
          <div>
            <label style={labelStyle}>Descrição Complementar</label>
            <textarea
              name="descricao_complementar"
              value={formData.descricao_complementar}
              onChange={handleChange}
              placeholder="Detalhes adicionais sobre a tarefa"
              rows="3"
              style={inputStyle}
            />
          </div>

          {/* Prazo Administrativo */}
          <div>
            <label style={labelStyle}>Prazo Administrativo</label>
            <input
              type="date"
              name="prazo_administrativo"
              value={formData.prazo_administrativo}
              onChange={handleChange}
              style={inputStyle}
            />
          </div>

          {/* Prazo Fatal */}
          <div>
            <label style={labelStyle}>Prazo Fatal*</label>
            <input
              type="date"
              name="prazo_fatal"
              value={formData.prazo_fatal}
              onChange={handleChange}
              required
              style={inputStyle}
            />
          </div>

          {/* Responsável */}
          <div>
            <label style={labelStyle}>Responsável</label>
            <select
              name="responsavel_id"
              value={formData.responsavel_id}
              onChange={handleChange}
              style={inputStyle}
            >
              <option value="">Nenhum responsável</option>
              {usuarios.map(usuario => (
                <option key={usuario.id} value={usuario.id}>
                  {usuario.nome}
                </option>
              ))}
            </select>
          </div>

          {/* Status */}
          <div>
            <label style={labelStyle}>Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
              style={inputStyle}
            >
              <option value="Pendente">Pendente</option>
              <option value="Em Andamento">Em Andamento</option>
              <option value="Concluída">Concluída</option>
              <option value="Cancelada">Cancelada</option>
            </select>
          </div>

          {/* Botões */}
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
            <button type="button" onClick={onClose} className="btn btn-secondary" disabled={loading}>
              Cancelar
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Salvando...' : 'Criar Tarefa'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
