import React, { useEffect, useState } from 'react';

const apiBase = '/api';

export default function FeriadoFormModal({ feriadoParaEditar, onClose, onFormSubmit }) {
  const [formData, setFormData] = useState({
    data: '',
    nome: '',
    tipo: 'nacional',
    uf: '',
    municipio_id: '',
    recorrente: false,
  });

  const [ufs, setUfs] = useState([]);
  const [municipios, setMunicipios] = useState([]);
  const [loadingMunicipios, setLoadingMunicipios] = useState(false);

  const isEditing = !!feriadoParaEditar?.id;

  useEffect(() => {
    if (feriadoParaEditar) {
      setFormData({
        data: feriadoParaEditar.data || '',
        nome: feriadoParaEditar.nome || '',
        tipo: feriadoParaEditar.tipo || 'nacional',
        uf: feriadoParaEditar.uf || '',
        municipio_id: feriadoParaEditar.municipio_id || '',
        recorrente: feriadoParaEditar.recorrente || false,
      });
    }
  }, [feriadoParaEditar]);

  // Carregar UFs
  useEffect(() => {
    const fetchUfs = async () => {
      try {
        const res = await fetch(`${apiBase}/config/ufs`);
        if (!res.ok) throw new Error('Falha ao buscar UFs');
        setUfs(await res.json());
      } catch (err) {
        console.error("Erro ao buscar UFs:", err);
      }
    };
    fetchUfs();
  }, []);

  // Carregar municípios quando UF for selecionada
  useEffect(() => {
    if (formData.uf && formData.tipo === 'municipal') {
      const fetchMunicipios = async () => {
        setLoadingMunicipios(true);
        try {
          const res = await fetch(`${apiBase}/municipios/uf/${formData.uf}`);
          if (!res.ok) throw new Error('Falha ao buscar municípios');
          const data = await res.json();
          setMunicipios(data);
        } catch (err) {
          console.error("Erro ao buscar municípios:", err);
          setMunicipios([]);
        } finally {
          setLoadingMunicipios(false);
        }
      };
      fetchMunicipios();
    } else {
      setMunicipios([]);
    }
  }, [formData.uf, formData.tipo]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newFormData = { ...formData, [name]: type === 'checkbox' ? checked : value };

    // Limpar campos dependentes quando tipo mudar
    if (name === 'tipo') {
      newFormData.uf = '';
      newFormData.municipio_id = '';
    }

    // Limpar município quando UF mudar
    if (name === 'uf') {
      newFormData.municipio_id = '';
    }

    setFormData(newFormData);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validações
    if (formData.tipo === 'estadual' && !formData.uf) {
      alert('UF é obrigatória para feriados estaduais.');
      return;
    }

    if (formData.tipo === 'municipal' && (!formData.uf || !formData.municipio_id)) {
      alert('UF e Município são obrigatórios para feriados municipais.');
      return;
    }

    // Preparar dados para envio
    const cleanData = (obj) => {
      const newObj = { ...obj };
      
      // Converter municipio_id para inteiro se for string
      if (newObj.municipio_id && typeof newObj.municipio_id === 'string') {
        newObj.municipio_id = parseInt(newObj.municipio_id, 10);
      }

      // Remover campos não necessários conforme o tipo
      if (obj.tipo === 'nacional') {
        delete newObj.uf;
        delete newObj.municipio_id;
      } else if (obj.tipo === 'estadual') {
        delete newObj.municipio_id;
      }

      return newObj;
    };

    const url = isEditing ? `${apiBase}/feriados/${feriadoParaEditar.id}` : `${apiBase}/feriados`;
    const method = isEditing ? 'PUT' : 'POST';

    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cleanData(formData)),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Falha ao salvar feriado');
      }

      alert(`Feriado ${isEditing ? 'atualizado' : 'criado'} com sucesso!`);
      onFormSubmit();
    } catch (err) {
      console.error(err);
      alert(`Erro ao salvar feriado: ${err.message}`);
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
          maxWidth: '500px',
          maxHeight: '90vh',
          overflowY: 'auto',
          margin: '20px',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#374151' }}>
          {isEditing ? 'Editar Feriado' : 'Novo Feriado'}
        </h3>

        <form onSubmit={handleSubmit}>
          {/* Data */}
          <div>
            <label style={labelStyle}>Data*</label>
            <input
              type="date"
              name="data"
              value={formData.data}
              onChange={handleChange}
              required
              style={inputStyle}
            />
          </div>

          {/* Nome */}
          <div>
            <label style={labelStyle}>Nome*</label>
            <input
              type="text"
              name="nome"
              value={formData.nome}
              onChange={handleChange}
              placeholder="Ex: Natal"
              required
              style={inputStyle}
            />
          </div>

          {/* Tipo */}
          <div>
            <label style={labelStyle}>Tipo*</label>
            <select
              name="tipo"
              value={formData.tipo}
              onChange={handleChange}
              required
              style={inputStyle}
            >
              <option value="nacional">Nacional</option>
              <option value="estadual">Estadual</option>
              <option value="municipal">Municipal</option>
            </select>
          </div>

          {/* UF - aparece para estadual e municipal */}
          {(formData.tipo === 'estadual' || formData.tipo === 'municipal') && (
            <div>
              <label style={labelStyle}>UF*</label>
              <select
                name="uf"
                value={formData.uf}
                onChange={handleChange}
                required
                style={inputStyle}
              >
                <option value="">Selecione a UF</option>
                {ufs.map(uf => <option key={uf} value={uf}>{uf}</option>)}
              </select>
            </div>
          )}

          {/* Município - aparece apenas para municipal */}
          {formData.tipo === 'municipal' && formData.uf && (
            <div>
              <label style={labelStyle}>Município*</label>
              {loadingMunicipios ? (
                <p style={{ fontSize: 14, color: '#6b7280' }}>Carregando municípios...</p>
              ) : (
                <select
                  name="municipio_id"
                  value={formData.municipio_id}
                  onChange={handleChange}
                  required
                  style={inputStyle}
                >
                  <option value="">Selecione o Município</option>
                  {municipios.map(m => (
                    <option key={m.id} value={m.id}>
                      {m.nome}
                    </option>
                  ))}
                </select>
              )}
            </div>
          )}

          {/* Recorrente */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'flex', alignItems: 'center', fontSize: '14px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                name="recorrente"
                checked={formData.recorrente}
                onChange={handleChange}
                style={{ marginRight: '8px' }}
              />
              Feriado recorrente (repete anualmente)
            </label>
          </div>

          {/* Botões */}
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
            <button type="button" onClick={onClose} className="btn btn-secondary">
              Cancelar
            </button>
            <button type="submit" className="btn btn-primary">
              Salvar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
