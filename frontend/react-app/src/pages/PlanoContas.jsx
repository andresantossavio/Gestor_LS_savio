import React, { useState, useEffect } from 'react';

export default function PlanoContas() {
  const [contas, setContas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingConta, setEditingConta] = useState(null);
  const [formData, setFormData] = useState({
    codigo: '',
    nome: '',
    natureza: 'D',
    pai_id: null,
    aceita_lancamento: true,
    ativo: true
  });

  useEffect(() => {
    carregarContas();
  }, []);

  const carregarContas = async () => {
    try {
      const response = await fetch('/api/contabilidade/plano-contas');
      const data = await response.json();
      setContas(data);
    } catch (error) {
      console.error('Erro ao carregar plano de contas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = '/api/contabilidade/plano-contas';
      const method = 'POST';
      
      await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      setShowForm(false);
      setEditingConta(null);
      setFormData({
        codigo: '',
        nome: '',
        natureza: 'D',
        pai_id: null,
        aceita_lancamento: true,
        ativo: true
      });
      carregarContas();
    } catch (error) {
      console.error('Erro ao salvar conta:', error);
      alert('Erro ao salvar conta');
    }
  };

  const formatarSaldo = (valor) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  };

  const renderContas = (contas, nivel = 0) => {
    return contas.map(conta => (
      <React.Fragment key={conta.id}>
        <tr style={{ backgroundColor: conta.aceita_lancamento ? 'white' : '#f8f9fa' }}>
          <td style={{ paddingLeft: `${nivel * 20 + 10}px`, fontWeight: nivel === 0 ? 'bold' : 'normal' }}>
            {conta.codigo}
          </td>
          <td style={{ fontWeight: nivel === 0 ? 'bold' : 'normal' }}>
            {conta.descricao}
          </td>
          <td className="text-center">
            <span className={`badge ${conta.natureza === 'D' ? 'bg-primary' : 'bg-success'}`}>
              {conta.natureza === 'D' ? 'Devedora' : 'Credora'}
            </span>
          </td>
          <td className="text-center">{conta.nivel}</td>
          <td className="text-center">
            {conta.aceita_lancamento ? 
              <span className="badge bg-success">Sim</span> : 
              <span className="badge bg-secondary">Não</span>
            }
          </td>
          <td className="text-end">{formatarSaldo(conta.saldo || 0)}</td>
          <td className="text-center">
            {conta.ativo ? 
              <span className="badge bg-success">Ativo</span> : 
              <span className="badge bg-danger">Inativo</span>
            }
          </td>
        </tr>
        {conta.filhas && conta.filhas.length > 0 && renderContas(conta.filhas, nivel + 1)}
      </React.Fragment>
    ));
  };

  if (loading) {
    return (
      <div className="container mt-4">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Carregando...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Plano de Contas</h2>
        <button 
          className="btn btn-primary"
          onClick={() => setShowForm(true)}
        >
          + Nova Conta
        </button>
      </div>

      {showForm && (
        <div className="card mb-4">
          <div className="card-body">
            <h5 className="card-title">
              {editingConta ? 'Editar Conta' : 'Nova Conta'}
            </h5>
            <form onSubmit={handleSubmit}>
              <div className="row">
                <div className="col-md-3">
                  <label className="form-label">Código *</label>
                  <input
                    type="text"
                    className="form-control"
                    value={formData.codigo}
                    onChange={(e) => setFormData({...formData, codigo: e.target.value})}
                    required
                    placeholder="Ex: 1.1.1"
                  />
                </div>
                <div className="col-md-5">
                  <label className="form-label">Nome *</label>
                  <input
                    type="text"
                    className="form-control"
                    value={formData.nome}
                    onChange={(e) => setFormData({...formData, nome: e.target.value})}
                    required
                  />
                </div>
                <div className="col-md-2">
                  <label className="form-label">Natureza *</label>
                  <select
                    className="form-select"
                    value={formData.natureza}
                    onChange={(e) => setFormData({...formData, natureza: e.target.value})}
                  >
                    <option value="D">Devedora</option>
                    <option value="C">Credora</option>
                  </select>
                </div>
                <div className="col-md-2">
                  <label className="form-label">Conta Superior</label>
                  <select
                    className="form-select"
                    value={formData.pai_id || ''}
                    onChange={(e) => setFormData({...formData, pai_id: e.target.value ? parseInt(e.target.value) : null})}
                  >
                    <option value="">Nenhuma</option>
                    {contas.map(c => (
                      <option key={c.id} value={c.id}>{c.codigo} - {c.descricao}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="row mt-3">
                <div className="col-md-6">
                  <div className="form-check">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      checked={formData.aceita_lancamento}
                      onChange={(e) => setFormData({...formData, aceita_lancamento: e.target.checked})}
                    />
                    <label className="form-check-label">
                      Aceita lançamentos (conta analítica)
                    </label>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="form-check">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      checked={formData.ativo}
                      onChange={(e) => setFormData({...formData, ativo: e.target.checked})}
                    />
                    <label className="form-check-label">
                      Conta ativa
                    </label>
                  </div>
                </div>
              </div>
              <div className="mt-3">
                <button type="submit" className="btn btn-primary me-2">
                  Salvar
                </button>
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowForm(false);
                    setEditingConta(null);
                    setFormData({
                      codigo: '',
                      nome: '',
                      natureza: 'D',
                      pai_id: null,
                      aceita_lancamento: true,
                      ativo: true
                    });
                  }}
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-body">
          <div className="alert alert-info">
            <strong>Legenda:</strong> Contas com fundo cinza são sintéticas (não aceitam lançamentos diretos).
            Contas com fundo branco são analíticas (aceitam lançamentos).
          </div>
          <div className="table-responsive">
            <table className="table table-sm table-hover">
              <thead className="table-dark">
                <tr>
                  <th>Código</th>
                  <th>Nome</th>
                  <th className="text-center">Natureza</th>
                  <th className="text-center">Nível</th>
                  <th className="text-center">Aceita Lançamento</th>
                  <th className="text-end">Saldo</th>
                  <th className="text-center">Status</th>
                </tr>
              </thead>
              <tbody>
                {renderContas(contas)}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
