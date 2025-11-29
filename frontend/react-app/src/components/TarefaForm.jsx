import React, { useEffect, useState } from 'react';

const apiBase = '/api';

export default function TarefaForm({ processoId, tarefaParaEditar, onClose, onFormSubmit }) {
  const [formData, setFormData] = useState({
    tipo_tarefa_id: '',
    descricao_complementar: '',
    prazo_fatal: '',
    responsavel_id: '',
    status: 'Pendente',
  });

  const [tiposTarefa, setTiposTarefa] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Carregar tipos de tarefa e usuários
    const fetchData = async () => {
      try {
        const [tiposRes, usuariosRes] = await Promise.all([
          fetch(`${apiBase}/tipos-tarefa`),
          fetch(`${apiBase}/usuarios`)
        ]);
        
        if (tiposRes.ok) {
          const tipos = await tiposRes.json();
          setTiposTarefa(tipos);
        }
        
        if (usuariosRes.ok) {
          const users = await usuariosRes.json();
          setUsuarios(users);
        }
      } catch (err) {
        console.error('Erro ao carregar dados:', err);
      }
    };

    fetchData();

    // Se está editando, preencher o formulário
    if (tarefaParaEditar) {
      setFormData({
        tipo_tarefa_id: tarefaParaEditar.tipo_tarefa_id || '',
        descricao_complementar: tarefaParaEditar.descricao_complementar || '',
        prazo_fatal: tarefaParaEditar.prazo_fatal || '',
        responsavel_id: tarefaParaEditar.responsavel_id || '',
        status: tarefaParaEditar.status || 'Pendente',
      });
    }
  }, [tarefaParaEditar]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        ...formData,
        processo_id: parseInt(processoId),
        tipo_tarefa_id: parseInt(formData.tipo_tarefa_id),
        responsavel_id: formData.responsavel_id ? parseInt(formData.responsavel_id) : null,
      };

      let res;
      if (tarefaParaEditar) {
        // Atualizar tarefa existente
        res = await fetch(`${apiBase}/tarefas/${tarefaParaEditar.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } else {
        // Criar nova tarefa
        res = await fetch(`${apiBase}/tarefas`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      }

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Erro ao salvar tarefa');
      }

      alert(tarefaParaEditar ? 'Tarefa atualizada com sucesso!' : 'Tarefa criada com sucesso!');
      onFormSubmit();
    } catch (err) {
      console.error(err);
      alert('Erro ao salvar tarefa: ' + err.message);
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
        <h2 style={{ marginTop: 0 }}>
          {tarefaParaEditar ? 'Editar Tarefa' : 'Nova Tarefa'}
        </h2>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 500 }}>
              Tipo de Tarefa *
            </label>
            <select
              name="tipo_tarefa_id"
              value={formData.tipo_tarefa_id}
              onChange={handleChange}
              required
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db' }}
            >
              <option value="">Selecione...</option>
              {tiposTarefa.map(tipo => (
                <option key={tipo.id} value={tipo.id}>{tipo.nome}</option>
              ))}
            </select>
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
              placeholder="Detalhes da tarefa..."
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 500 }}>
              Prazo Fatal
            </label>
            <input
              type="date"
              name="prazo_fatal"
              value={formData.prazo_fatal}
              onChange={handleChange}
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db' }}
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 500 }}>
              Responsável
            </label>
            <select
              name="responsavel_id"
              value={formData.responsavel_id}
              onChange={handleChange}
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db' }}
            >
              <option value="">Nenhum</option>
              {usuarios.map(usuario => (
                <option key={usuario.id} value={usuario.id}>{usuario.nome}</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 500 }}>
              Status *
            </label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
              required
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db' }}
            >
              <option value="Pendente">Pendente</option>
              <option value="Em Andamento">Em Andamento</option>
              <option value="Concluída">Concluída</option>
              <option value="Cancelada">Cancelada</option>
            </select>
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
