import React, { useState, useEffect, useRef } from 'react';

export default function LancamentosContabeis() {
  const [lancamentos, setLancamentos] = useState([]);
  const [contas, setContas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingLancamento, setEditingLancamento] = useState(null);
  const formRef = useRef(null);
  const [filtroDataInicio, setFiltroDataInicio] = useState('');
  const [filtroDataFim, setFiltroDataFim] = useState('');
  const [filtroConta, setFiltroConta] = useState('');
  const [filtroTipo, setFiltroTipo] = useState('');
  const [filtroApenasPendentes, setFiltroApenasPendentes] = useState(false);
  const [showPagamentoModal, setShowPagamentoModal] = useState(false);
  const [lancamentoPagamento, setLancamentoPagamento] = useState(null);
  const [pagamentoData, setPagamentoData] = useState({
    data_pagamento: new Date().toISOString().split('T')[0],
    valor_pago: '',
    observacao: ''
  });
  const [formData, setFormData] = useState({
    data: new Date().toISOString().split('T')[0],
    historico: '',
    debito_conta_id: '',
    credito_conta_id: '',
    valor: ''
  });

  useEffect(() => {
    carregarDados();
  }, []);

  useEffect(() => {
    carregarDados();
  }, [filtroDataInicio, filtroDataFim, filtroConta, filtroTipo, filtroApenasPendentes]);

  useEffect(() => {
    if (showForm && formRef.current) {
      formRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [showForm]);

  const carregarDados = async () => {
    try {
      let url = '/api/contabilidade/lancamentos?';
      const params = new URLSearchParams();
      if (filtroDataInicio) params.append('data_inicio', filtroDataInicio);
      if (filtroDataFim) params.append('data_fim', filtroDataFim);
      if (filtroConta) params.append('conta_id', filtroConta);
      if (filtroTipo) params.append('tipo_lancamento', filtroTipo);
      if (filtroApenasPendentes) params.append('apenas_pendentes', 'true');
      
      url += params.toString();
      
      const [lancamentosRes, contasRes] = await Promise.all([
        fetch(url),
        fetch('/api/contabilidade/plano-contas')
      ]);
      
      const lancamentosData = await lancamentosRes.json();
      const contasData = await contasRes.json();
      
      setLancamentos(lancamentosData);
      setContas(extrairContasAnaliticas(contasData));
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const extrairContasAnaliticas = (contas) => {
    let resultado = [];
    contas.forEach(conta => {
      if (conta.aceita_lancamento) {
        resultado.push(conta);
      }
      if (conta.filhas && conta.filhas.length > 0) {
        resultado = resultado.concat(extrairContasAnaliticas(conta.filhas));
      }
    });
    return resultado;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.debito_conta_id === formData.credito_conta_id) {
      alert('As contas de débito e crédito devem ser diferentes!');
      return;
    }

    try {
      const url = editingLancamento 
        ? `/api/contabilidade/lancamentos/${editingLancamento.id}`
        : '/api/contabilidade/lancamentos';
      const method = editingLancamento ? 'PUT' : 'POST';
      
      const payload = {
        ...formData,
        debito_conta_id: parseInt(formData.debito_conta_id),
        credito_conta_id: parseInt(formData.credito_conta_id),
        valor: parseFloat(formData.valor)
      };
      
      console.log('Enviando lançamento:', payload);
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      console.log('Status da resposta:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Erro do servidor:', errorText);
        let errorMessage = 'Erro ao salvar lançamento';
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          errorMessage = errorText || errorMessage;
        }
        throw new Error(errorMessage);
      }

      alert('Lançamento salvo com sucesso!');
      setShowForm(false);
      setEditingLancamento(null);
      setFormData({
        data: new Date().toISOString().split('T')[0],
        historico: '',
        debito_conta_id: '',
        credito_conta_id: '',
        valor: ''
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao salvar lançamento:', error);
      alert(`Erro ao salvar lançamento: ${error.message}`);
    }
  };

  const handleEdit = (lancamento) => {
    if (!lancamento.editavel) {
      alert('Este lançamento foi gerado automaticamente e não pode ser editado.');
      return;
    }
    setEditingLancamento(lancamento);
    setFormData({
      data: lancamento.data,
      historico: lancamento.historico,
      debito_conta_id: lancamento.debito_conta_id,
      credito_conta_id: lancamento.credito_conta_id,
      valor: lancamento.valor
    });
    setShowForm(true);
  };

  const handleDelete = async (id, editavel) => {
    if (!editavel) {
      alert('Este lançamento foi gerado automaticamente e não pode ser excluído.');
      return;
    }
    
    if (!confirm('Tem certeza que deseja excluir este lançamento?')) {
      return;
    }

    try {
      await fetch(`/api/contabilidade/lancamentos/${id}`, {
        method: 'DELETE'
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao excluir lançamento:', error);
      alert('Erro ao excluir lançamento');
    }
  };

  const formatarData = (dataStr) => {
    const data = new Date(dataStr + 'T00:00:00');
    return data.toLocaleDateString('pt-BR');
  };

  const formatarValor = (valor) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  };

  const getTipoLabel = (tipo) => {
    const tipos = {
      'efetivo': 'Efetivo',
      'provisao': 'Provisão',
      'pagamento_pro_labore': 'Pag. Pró-labore',
      'pagamento_lucro': 'Pag. Lucro',
      'pagamento_imposto': 'Pag. Imposto'
    };
    return tipos[tipo] || tipo;
  };

  const getTipoBadge = (tipo) => {
    const badges = {
      'efetivo': 'success',
      'provisao': 'warning',
      'pagamento_pro_labore': 'info',
      'pagamento_lucro': 'primary',
      'pagamento_imposto': 'danger'
    };
    return badges[tipo] || 'secondary';
  };

  const getStatusBadge = (lancamento) => {
    if (lancamento.tipo_lancamento === 'efetivo') {
      return <span className="badge bg-success">Efetivado</span>;
    }
    if (lancamento.pago) {
      if (lancamento.valor_pago < lancamento.valor) {
        return <span className="badge bg-warning">Pago Parcial</span>;
      }
      return <span className="badge bg-success">Pago</span>;
    }
    if (lancamento.tipo_lancamento === 'provisao') {
      return <span className="badge bg-warning">Pendente</span>;
    }
    return <span className="badge bg-secondary">-</span>;
  };

  const handleMarcarPagamento = (lancamento) => {
    setLancamentoPagamento(lancamento);
    setPagamentoData({
      data_pagamento: new Date().toISOString().split('T')[0],
      valor_pago: lancamento.saldo_pendente || lancamento.valor,
      observacao: ''
    });
    setShowPagamentoModal(true);
  };

  const handleSubmitPagamento = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`/api/contabilidade/lancamentos/${lancamentoPagamento.id}/marcar-pagamento`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          data_pagamento: pagamentoData.data_pagamento,
          valor_pago: parseFloat(pagamentoData.valor_pago) || null,
          observacao: pagamentoData.observacao || null
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao registrar pagamento');
      }

      const result = await response.json();
      alert(result.message);
      setShowPagamentoModal(false);
      setLancamentoPagamento(null);
      carregarDados();
    } catch (error) {
      console.error('Erro ao marcar pagamento:', error);
      alert(`Erro: ${error.message}`);
    }
  };

  const totalDebito = lancamentos.reduce((sum, l) => sum + l.valor, 0);
  const totalCredito = lancamentos.reduce((sum, l) => sum + l.valor, 0);

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
        <h2>Diário - Lançamentos Contábeis</h2>
        <button 
          className="btn btn-primary"
          onClick={() => {
            setShowForm(true);
            setEditingLancamento(null);
          }}
        >
          + Novo Lançamento
        </button>
      </div>

      {showForm && (
        <div className="card mb-4" ref={formRef}>
          <div className="card-body">
            <h5 className="card-title">
              {editingLancamento ? 'Editar Lançamento' : 'Novo Lançamento'}
            </h5>
            <form onSubmit={handleSubmit}>
              <div className="row">
                <div className="col-md-2">
                  <label className="form-label">Data *</label>
                  <input
                    type="date"
                    className="form-control"
                    value={formData.data}
                    onChange={(e) => setFormData({...formData, data: e.target.value})}
                    required
                  />
                </div>
                <div className="col-md-10">
                  <label className="form-label">Histórico *</label>
                  <input
                    type="text"
                    className="form-control"
                    value={formData.historico}
                    onChange={(e) => setFormData({...formData, historico: e.target.value})}
                    required
                    placeholder="Descrição do lançamento"
                  />
                </div>
              </div>
              <div className="row mt-3">
                <div className="col-md-5">
                  <label className="form-label">Conta de Débito *</label>
                  <select
                    className="form-select"
                    value={formData.debito_conta_id}
                    onChange={(e) => setFormData({...formData, debito_conta_id: e.target.value})}
                    required
                  >
                    <option value="">Selecione...</option>
                    {contas.map(c => (
                      <option key={c.id} value={c.id}>
                        {c.codigo} - {c.descricao}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-md-5">
                  <label className="form-label">Conta de Crédito *</label>
                  <select
                    className="form-select"
                    value={formData.credito_conta_id}
                    onChange={(e) => setFormData({...formData, credito_conta_id: e.target.value})}
                    required
                  >
                    <option value="">Selecione...</option>
                    {contas.map(c => (
                      <option key={c.id} value={c.id}>
                        {c.codigo} - {c.descricao}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-md-2">
                  <label className="form-label">Valor *</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    className="form-control"
                    value={formData.valor}
                    onChange={(e) => setFormData({...formData, valor: e.target.value})}
                    required
                  />
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
                    setEditingLancamento(null);
                    setFormData({
                      data: new Date().toISOString().split('T')[0],
                      historico: '',
                      debito_conta_id: '',
                      credito_conta_id: '',
                      valor: ''
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

      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title">Filtros</h5>
          <div className="row">
            <div className="col-md-2">
              <label className="form-label">Data Início</label>
              <input
                type="date"
                className="form-control"
                value={filtroDataInicio}
                onChange={(e) => setFiltroDataInicio(e.target.value)}
              />
            </div>
            <div className="col-md-2">
              <label className="form-label">Data Fim</label>
              <input
                type="date"
                className="form-control"
                value={filtroDataFim}
                onChange={(e) => setFiltroDataFim(e.target.value)}
              />
            </div>
            <div className="col-md-3">
              <label className="form-label">Conta</label>
              <select
                className="form-select"
                value={filtroConta}
                onChange={(e) => setFiltroConta(e.target.value)}
              >
                <option value="">Todas</option>
                {contas.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.codigo} - {c.descricao}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Tipo de Lançamento</label>
              <select
                className="form-select"
                value={filtroTipo}
                onChange={(e) => setFiltroTipo(e.target.value)}
              >
                <option value="">Todos</option>
                <option value="efetivo">Efetivo</option>
                <option value="provisao">Provisão</option>
                <option value="pagamento_pro_labore">Pag. Pró-labore</option>
                <option value="pagamento_lucro">Pag. Lucro</option>
                <option value="pagamento_imposto">Pag. Imposto</option>
              </select>
            </div>
            <div className="col-md-2 d-flex align-items-end">
              <button
                className="btn btn-secondary w-100"
                onClick={() => {
                  setFiltroDataInicio('');
                  setFiltroDataFim('');
                  setFiltroConta('');
                  setFiltroTipo('');
                  setFiltroApenasPendentes(false);
                }}
              >
                Limpar
              </button>
            </div>
          </div>
          <div className="row mt-3">
            <div className="col-md-12">
              <div className="form-check">
                <input
                  type="checkbox"
                  className="form-check-input"
                  id="filtroApenasPendentes"
                  checked={filtroApenasPendentes}
                  onChange={(e) => setFiltroApenasPendentes(e.target.checked)}
                />
                <label className="form-check-label" htmlFor="filtroApenasPendentes">
                  Mostrar apenas provisões pendentes de pagamento
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="alert alert-info">
            <strong>Método das Partidas Dobradas:</strong> Cada lançamento possui um débito e um crédito de mesmo valor.
            Lançamentos automáticos (gerados pelo sistema) não podem ser editados ou excluídos.
          </div>
          <div className="table-responsive">
            <table className="table table-sm table-hover">
              <thead className="table-dark">
                <tr>
                  <th style={{width: '80px'}}>Data</th>
                  <th>Histórico</th>
                  <th style={{width: '200px'}}>Débito</th>
                  <th style={{width: '200px'}}>Crédito</th>
                  <th className="text-end" style={{width: '100px'}}>Valor</th>
                  <th className="text-center" style={{width: '100px'}}>Tipo</th>
                  <th className="text-center" style={{width: '80px'}}>Ref.Mês</th>
                  <th className="text-center" style={{width: '120px'}}>Status</th>
                  <th className="text-center" style={{width: '100px'}}>Ações</th>
                </tr>
              </thead>
              <tbody>
                {lancamentos.length === 0 ? (
                  <tr>
                    <td colSpan="9" className="text-center text-muted">
                      Nenhum lançamento encontrado
                    </td>
                  </tr>
                ) : (
                  lancamentos.map(lancamento => (
                    <tr key={lancamento.id}>
                      <td>{formatarData(lancamento.data)}</td>
                      <td>
                        {lancamento.historico}
                        {lancamento.lancamento_origem_id && (
                          <div>
                            <small className="text-muted">
                              {lancamento.tipo_lancamento?.startsWith('pagamento_') && (
                                `Pagamento de #${lancamento.lancamento_origem_id}`
                              )}
                            </small>
                          </div>
                        )}
                      </td>
                      <td>
                        <small className="text-muted">{lancamento.debito_conta_codigo}</small><br/>
                        {lancamento.debito_conta_nome}
                      </td>
                      <td>
                        <small className="text-muted">{lancamento.credito_conta_codigo}</small><br/>
                        {lancamento.credito_conta_nome}
                      </td>
                      <td className="text-end fw-bold">{formatarValor(lancamento.valor)}</td>
                      <td className="text-center">
                        {lancamento.tipo_lancamento ? (
                          <span className={`badge bg-${getTipoBadge(lancamento.tipo_lancamento)}`}>
                            {getTipoLabel(lancamento.tipo_lancamento)}
                          </span>
                        ) : (
                          <span className="badge bg-secondary">-</span>
                        )}
                      </td>
                      <td className="text-center">
                        {lancamento.referencia_mes || '-'}
                      </td>
                      <td className="text-center">
                        {getStatusBadge(lancamento)}
                        {lancamento.pago && lancamento.data_pagamento && (
                          <div>
                            <small className="text-muted">
                              {formatarData(lancamento.data_pagamento)}
                            </small>
                          </div>
                        )}
                        {lancamento.saldo_pendente > 0 && (
                          <div>
                            <small className="text-warning">
                              Saldo: {formatarValor(lancamento.saldo_pendente)}
                            </small>
                          </div>
                        )}
                      </td>
                      <td className="text-center">
                        {lancamento.tipo_lancamento === 'provisao' && !lancamento.pago && (
                          <button
                            className="btn btn-sm btn-success mb-1"
                            onClick={() => handleMarcarPagamento(lancamento)}
                            title="Marcar Pagamento"
                          >
                            💰
                          </button>
                        )}
                        {lancamento.editavel && (
                          <>
                            <button
                              className="btn btn-sm btn-warning me-1"
                              onClick={() => handleEdit(lancamento)}
                              title="Editar"
                            >
                              ✏️
                            </button>
                            <button
                              className="btn btn-sm btn-danger"
                              onClick={() => handleDelete(lancamento.id, lancamento.editavel)}
                              title="Excluir"
                            >
                              🗑️
                            </button>
                          </>
                        )}
                        {!lancamento.editavel && lancamento.tipo_lancamento !== 'provisao' && (
                          <span className="text-muted" title="Lançamento automático não pode ser editado">🔒</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
              <tfoot className="table-light">
                <tr>
                  <td colSpan="4" className="text-end fw-bold">TOTAIS:</td>
                  <td className="text-end fw-bold">{formatarValor(totalDebito)}</td>
                  <td colSpan="4"></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>

      {/* Modal de Pagamento */}
      {showPagamentoModal && lancamentoPagamento && (
        <div className="modal show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Marcar Pagamento</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => {
                    setShowPagamentoModal(false);
                    setLancamentoPagamento(null);
                  }}
                ></button>
              </div>
              <form onSubmit={handleSubmitPagamento}>
                <div className="modal-body">
                  <div className="alert alert-info">
                    <strong>Lançamento #{lancamentoPagamento.id}</strong><br/>
                    {lancamentoPagamento.historico}<br/>
                    <strong>Valor Total:</strong> {formatarValor(lancamentoPagamento.valor)}<br/>
                    {lancamentoPagamento.saldo_pendente && (
                      <>
                        <strong>Saldo Pendente:</strong> {formatarValor(lancamentoPagamento.saldo_pendente)}
                      </>
                    )}
                  </div>

                  <div className="mb-3">
                    <label className="form-label">Data do Pagamento *</label>
                    <input
                      type="date"
                      className="form-control"
                      value={pagamentoData.data_pagamento}
                      onChange={(e) => setPagamentoData({...pagamentoData, data_pagamento: e.target.value})}
                      required
                    />
                  </div>

                  <div className="mb-3">
                    <label className="form-label">Valor Pago</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0.01"
                      className="form-control"
                      value={pagamentoData.valor_pago}
                      onChange={(e) => setPagamentoData({...pagamentoData, valor_pago: e.target.value})}
                      placeholder={`Deixe em branco para pagar tudo (${formatarValor(lancamentoPagamento.saldo_pendente || lancamentoPagamento.valor)})`}
                    />
                    <small className="text-muted d-block mb-1">
                      Se deixar em branco ou informar valor igual ao saldo, será pagamento total. 
                      Caso contrário, será pagamento parcial.
                    </small>
                    <small className="text-info">
                      💡 O sistema aceita diferenças de até R$ 0,05 para compensar arredondamentos de DARF/Boletos.
                    </small>
                  </div>

                  <div className="mb-3">
                    <label className="form-label">Observação</label>
                    <textarea
                      className="form-control"
                      rows="3"
                      value={pagamentoData.observacao}
                      onChange={(e) => setPagamentoData({...pagamentoData, observacao: e.target.value})}
                      placeholder="Informações adicionais sobre o pagamento (opcional)"
                    ></textarea>
                  </div>

                  {lancamentoPagamento.tipo_lancamento === 'provisao' && 
                   lancamentoPagamento.historico.toLowerCase().includes('pró-labore') && (
                    <div className="alert alert-warning">
                      <strong>⚠️ Atenção:</strong> Pagamento de pró-labore será dividido automaticamente:<br/>
                      • 89% para o beneficiário<br/>
                      • 11% para retenção de INSS
                    </div>
                  )}
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => {
                      setShowPagamentoModal(false);
                      setLancamentoPagamento(null);
                    }}
                  >
                    Cancelar
                  </button>
                  <button type="submit" className="btn btn-success">
                    Confirmar Pagamento
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
