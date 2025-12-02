import React, { useState, useEffect } from 'react';

export default function DMPL() {
  const [dmpl, setDmpl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [anoInicio, setAnoInicio] = useState(new Date().getFullYear());
  const [anoFim, setAnoFim] = useState(new Date().getFullYear());

  useEffect(() => {
    carregarDMPL();
  }, [anoInicio, anoFim]);

  const carregarDMPL = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/contabilidade/dmpl?ano_inicio=${anoInicio}&ano_fim=${anoFim}`);
      const data = await response.json();
      setDmpl(data);
    } catch (error) {
      console.error('Erro ao carregar DMPL:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatarValor = (valor) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor || 0);
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

  if (!dmpl) {
    return (
      <div className="container mt-4">
        <div className="alert alert-warning">
          Erro ao carregar DMPL
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Demonstração das Mutações do Patrimônio Líquido - DMPL</h2>
        <div className="d-flex align-items-center gap-2">
          <label className="me-2">Período:</label>
          <input
            type="number"
            className="form-control"
            value={anoInicio}
            onChange={(e) => setAnoInicio(parseInt(e.target.value))}
            style={{ width: '100px' }}
            min="2020"
            max="2099"
          />
          <span>até</span>
          <input
            type="number"
            className="form-control"
            value={anoFim}
            onChange={(e) => setAnoFim(parseInt(e.target.value))}
            style={{ width: '100px' }}
            min="2020"
            max="2099"
          />
        </div>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="alert alert-info">
            <strong>DMPL</strong> - Demonstra as movimentações ocorridas nas contas do Patrimônio Líquido durante o período.
            Inclui capital social, reservas, lucros/prejuízos acumulados e outras mutações.
          </div>

          <div className="table-responsive">
            <table className="table table-bordered table-hover">
              <thead className="table-dark">
                <tr>
                  <th>Descrição</th>
                  <th className="text-end">Capital Social</th>
                  <th className="text-end">Reservas de Lucros</th>
                  <th className="text-end">Lucros/Prejuízos Acumulados</th>
                  <th className="text-end">Total do PL</th>
                </tr>
              </thead>
              <tbody>
                <tr className="table-light">
                  <td><strong>Saldo Inicial em {dmpl.ano_inicio}</strong></td>
                  <td className="text-end">{formatarValor(dmpl.saldo_inicial?.capital_social)}</td>
                  <td className="text-end">{formatarValor(dmpl.saldo_inicial?.reservas)}</td>
                  <td className="text-end">{formatarValor(dmpl.saldo_inicial?.lucros_acumulados)}</td>
                  <td className="text-end fw-bold">{formatarValor(dmpl.saldo_inicial?.total)}</td>
                </tr>

                {dmpl.movimentacoes && dmpl.movimentacoes.map((mov, idx) => (
                  <tr key={idx}>
                    <td>{mov.descricao}</td>
                    <td className="text-end">{formatarValor(mov.capital_social)}</td>
                    <td className="text-end">{formatarValor(mov.reservas)}</td>
                    <td className="text-end">{formatarValor(mov.lucros_acumulados)}</td>
                    <td className="text-end">{formatarValor(mov.total)}</td>
                  </tr>
                ))}

                <tr className="table-success fw-bold">
                  <td>Saldo Final em {dmpl.ano_fim}</td>
                  <td className="text-end">{formatarValor(dmpl.saldo_final?.capital_social)}</td>
                  <td className="text-end">{formatarValor(dmpl.saldo_final?.reservas)}</td>
                  <td className="text-end">{formatarValor(dmpl.saldo_final?.lucros_acumulados)}</td>
                  <td className="text-end">{formatarValor(dmpl.saldo_final?.total)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="row mt-4">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h5 className="mb-0">Principais Movimentações</h5>
            </div>
            <div className="card-body">
              {dmpl.movimentacoes && dmpl.movimentacoes.length > 0 ? (
                <ul className="list-group list-group-flush">
                  {dmpl.movimentacoes.map((mov, idx) => (
                    <li key={idx} className="list-group-item d-flex justify-content-between align-items-center">
                      {mov.descricao}
                      <span className={`badge ${mov.total >= 0 ? 'bg-success' : 'bg-danger'}`}>
                        {formatarValor(mov.total)}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-muted">Nenhuma movimentação no período</p>
              )}
            </div>
          </div>
        </div>

        <div className="col-md-6">
          <div className="card">
            <div className="card-header bg-success text-white">
              <h5 className="mb-0">Resumo</h5>
            </div>
            <div className="card-body">
              <table className="table table-sm">
                <tbody>
                  <tr>
                    <td><strong>Patrimônio Líquido Inicial:</strong></td>
                    <td className="text-end">{formatarValor(dmpl.saldo_inicial?.total)}</td>
                  </tr>
                  <tr>
                    <td><strong>Total de Mutações:</strong></td>
                    <td className="text-end">
                      <span className={dmpl.total_mutacoes >= 0 ? 'text-success' : 'text-danger'}>
                        {formatarValor(dmpl.total_mutacoes)}
                      </span>
                    </td>
                  </tr>
                  <tr className="table-light">
                    <td><strong>Patrimônio Líquido Final:</strong></td>
                    <td className="text-end fw-bold">{formatarValor(dmpl.saldo_final?.total)}</td>
                  </tr>
                  <tr>
                    <td><strong>Variação Percentual:</strong></td>
                    <td className="text-end">
                      <span className={dmpl.variacao_percentual >= 0 ? 'text-success' : 'text-danger'}>
                        {dmpl.variacao_percentual?.toFixed(2)}%
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div className="alert alert-secondary mt-4">
        <h6>Notas Explicativas:</h6>
        <ul>
          <li><strong>Capital Social:</strong> Recursos investidos pelos sócios na empresa</li>
          <li><strong>Reservas de Lucros:</strong> Lucros retidos para fins específicos (legal, estatutária, contingências)</li>
          <li><strong>Lucros/Prejuízos Acumulados:</strong> Resultado acumulado não destinado</li>
          <li><strong>Movimentações típicas:</strong> Aumentos de capital, distribuição de dividendos, constituição de reservas, lucro/prejuízo do exercício</li>
        </ul>
      </div>
    </div>
  );
}
