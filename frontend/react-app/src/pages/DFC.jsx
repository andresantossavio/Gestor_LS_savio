import React, { useState, useEffect } from 'react';

export default function DFC() {
  const [dfc, setDfc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mesAno, setMesAno] = useState(() => {
    const hoje = new Date();
    return `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}`;
  });

  useEffect(() => {
    carregarDFC();
  }, [mesAno]);

  const carregarDFC = async () => {
    setLoading(true);
    try {
      const [ano, mes] = mesAno.split('-');
      const response = await fetch(`/api/contabilidade/dfc?mes=${mes}&ano=${ano}`);
      const data = await response.json();
      setDfc(data);
    } catch (error) {
      console.error('Erro ao carregar DFC:', error);
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

  if (!dfc) {
    return (
      <div className="container mt-4">
        <div className="alert alert-warning">
          Erro ao carregar DFC
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Demonstração dos Fluxos de Caixa - DFC</h2>
        <div className="d-flex align-items-center">
          <label className="me-2">Período:</label>
          <input
            type="month"
            className="form-control"
            value={mesAno}
            onChange={(e) => setMesAno(e.target.value)}
            style={{ width: '180px' }}
          />
        </div>
      </div>

      <div className="card mb-4">
        <div className="card-body">
          <div className="alert alert-info">
            <strong>DFC - Método Direto:</strong> Demonstra as movimentações de caixa e equivalentes de caixa,
            classificadas em atividades operacionais, de investimento e de financiamento.
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-md-4">
          <div className="card mb-4">
            <div className="card-header bg-primary text-white">
              <h5 className="mb-0">Atividades Operacionais</h5>
            </div>
            <div className="card-body">
              <table className="table table-sm">
                <tbody>
                  <tr>
                    <td>Recebimentos de clientes</td>
                    <td className="text-end text-success fw-bold">
                      {formatarValor(dfc.operacionais?.recebimentos_clientes)}
                    </td>
                  </tr>
                  <tr>
                    <td>Pagamentos a fornecedores</td>
                    <td className="text-end text-danger">
                      {formatarValor(dfc.operacionais?.pagamentos_fornecedores)}
                    </td>
                  </tr>
                  <tr>
                    <td>Pagamentos de salários</td>
                    <td className="text-end text-danger">
                      {formatarValor(dfc.operacionais?.pagamentos_salarios)}
                    </td>
                  </tr>
                  <tr>
                    <td>Pagamentos de impostos</td>
                    <td className="text-end text-danger">
                      {formatarValor(dfc.operacionais?.pagamentos_impostos)}
                    </td>
                  </tr>
                  <tr>
                    <td>Outras receitas operacionais</td>
                    <td className="text-end text-success">
                      {formatarValor(dfc.operacionais?.outras_receitas)}
                    </td>
                  </tr>
                  <tr>
                    <td>Outras despesas operacionais</td>
                    <td className="text-end text-danger">
                      {formatarValor(dfc.operacionais?.outras_despesas)}
                    </td>
                  </tr>
                  <tr className="table-light">
                    <td><strong>Caixa Líquido das Operações</strong></td>
                    <td className={`text-end fw-bold ${dfc.operacionais?.total >= 0 ? 'text-success' : 'text-danger'}`}>
                      {formatarValor(dfc.operacionais?.total)}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card mb-4">
            <div className="card-header bg-warning text-dark">
              <h5 className="mb-0">Atividades de Investimento</h5>
            </div>
            <div className="card-body">
              <table className="table table-sm">
                <tbody>
                  <tr>
                    <td>Aquisição de imobilizado</td>
                    <td className="text-end text-danger">
                      {formatarValor(dfc.investimentos?.aquisicao_imobilizado)}
                    </td>
                  </tr>
                  <tr>
                    <td>Venda de imobilizado</td>
                    <td className="text-end text-success">
                      {formatarValor(dfc.investimentos?.venda_imobilizado)}
                    </td>
                  </tr>
                  <tr>
                    <td>Aplicações financeiras</td>
                    <td className="text-end text-danger">
                      {formatarValor(dfc.investimentos?.aplicacoes_financeiras)}
                    </td>
                  </tr>
                  <tr>
                    <td>Resgate de aplicações</td>
                    <td className="text-end text-success">
                      {formatarValor(dfc.investimentos?.resgate_aplicacoes)}
                    </td>
                  </tr>
                  <tr className="table-light">
                    <td><strong>Caixa Líquido de Investimentos</strong></td>
                    <td className={`text-end fw-bold ${dfc.investimentos?.total >= 0 ? 'text-success' : 'text-danger'}`}>
                      {formatarValor(dfc.investimentos?.total)}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card mb-4">
            <div className="card-header bg-danger text-white">
              <h5 className="mb-0">Atividades de Financiamento</h5>
            </div>
            <div className="card-body">
              <table className="table table-sm">
                <tbody>
                  <tr>
                    <td>Aumento de capital</td>
                    <td className="text-end text-success">
                      {formatarValor(dfc.financiamentos?.aumento_capital)}
                    </td>
                  </tr>
                  <tr>
                    <td>Empréstimos obtidos</td>
                    <td className="text-end text-success">
                      {formatarValor(dfc.financiamentos?.emprestimos_obtidos)}
                    </td>
                  </tr>
                  <tr>
                    <td>Pagamento de empréstimos</td>
                    <td className="text-end text-danger">
                      {formatarValor(dfc.financiamentos?.pagamento_emprestimos)}
                    </td>
                  </tr>
                  <tr>
                    <td>Distribuição de dividendos</td>
                    <td className="text-end text-danger">
                      {formatarValor(dfc.financiamentos?.distribuicao_dividendos)}
                    </td>
                  </tr>
                  <tr className="table-light">
                    <td><strong>Caixa Líquido de Financiamentos</strong></td>
                    <td className={`text-end fw-bold ${dfc.financiamentos?.total >= 0 ? 'text-success' : 'text-danger'}`}>
                      {formatarValor(dfc.financiamentos?.total)}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header bg-dark text-white">
          <h5 className="mb-0">Resumo do Período</h5>
        </div>
        <div className="card-body">
          <table className="table table-bordered">
            <tbody>
              <tr>
                <td className="fw-bold">Saldo Inicial de Caixa</td>
                <td className="text-end">{formatarValor(dfc.saldo_inicial)}</td>
              </tr>
              <tr className="table-light">
                <td>Caixa Líquido das Atividades Operacionais</td>
                <td className={`text-end ${dfc.operacionais?.total >= 0 ? 'text-success' : 'text-danger'}`}>
                  {formatarValor(dfc.operacionais?.total)}
                </td>
              </tr>
              <tr className="table-light">
                <td>Caixa Líquido das Atividades de Investimento</td>
                <td className={`text-end ${dfc.investimentos?.total >= 0 ? 'text-success' : 'text-danger'}`}>
                  {formatarValor(dfc.investimentos?.total)}
                </td>
              </tr>
              <tr className="table-light">
                <td>Caixa Líquido das Atividades de Financiamento</td>
                <td className={`text-end ${dfc.financiamentos?.total >= 0 ? 'text-success' : 'text-danger'}`}>
                  {formatarValor(dfc.financiamentos?.total)}
                </td>
              </tr>
              <tr className="table-warning">
                <td className="fw-bold">Variação Líquida de Caixa</td>
                <td className={`text-end fw-bold ${dfc.variacao_liquida >= 0 ? 'text-success' : 'text-danger'}`}>
                  {formatarValor(dfc.variacao_liquida)}
                </td>
              </tr>
              <tr className="table-success">
                <td className="fw-bold">Saldo Final de Caixa</td>
                <td className="text-end fw-bold">{formatarValor(dfc.saldo_final)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="row mt-4">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header bg-info text-white">
              <h5 className="mb-0">Análise de Liquidez</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <h6>Capacidade de Geração de Caixa</h6>
                <div className="progress" style={{ height: '30px' }}>
                  <div 
                    className={`progress-bar ${dfc.operacionais?.total >= 0 ? 'bg-success' : 'bg-danger'}`}
                    style={{ width: '100%' }}
                  >
                    {formatarValor(dfc.operacionais?.total)}
                  </div>
                </div>
                <small className="text-muted">
                  {dfc.operacionais?.total >= 0 ? 
                    'As operações estão gerando caixa positivo' : 
                    'As operações estão consumindo caixa'}
                </small>
              </div>

              <div>
                <h6>Cobertura de Investimentos</h6>
                <p className="fs-5">
                  {dfc.investimentos?.total < 0 && dfc.operacionais?.total > 0 ? (
                    <>
                      <span className="badge bg-success">✓</span>
                      {' '}Investimentos cobertos pelas operações
                    </>
                  ) : dfc.investimentos?.total < 0 ? (
                    <>
                      <span className="badge bg-warning">⚠</span>
                      {' '}Investimentos não cobertos pelas operações
                    </>
                  ) : (
                    <>
                      <span className="badge bg-info">ℹ</span>
                      {' '}Sem investimentos no período
                    </>
                  )}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-6">
          <div className="card">
            <div className="card-header bg-secondary text-white">
              <h5 className="mb-0">Indicadores</h5>
            </div>
            <div className="card-body">
              <table className="table table-sm">
                <tbody>
                  <tr>
                    <td><strong>Variação Percentual do Caixa:</strong></td>
                    <td className="text-end">
                      <span className={dfc.variacao_percentual >= 0 ? 'text-success' : 'text-danger'}>
                        {dfc.variacao_percentual?.toFixed(2)}%
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Caixa Operacional / Caixa Total:</strong></td>
                    <td className="text-end">
                      {dfc.variacao_liquida !== 0 ? 
                        ((dfc.operacionais?.total / dfc.variacao_liquida) * 100).toFixed(2) : 0}%
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Status Financeiro:</strong></td>
                    <td className="text-end">
                      {dfc.saldo_final > dfc.saldo_inicial ? (
                        <span className="badge bg-success">Crescimento</span>
                      ) : dfc.saldo_final < dfc.saldo_inicial ? (
                        <span className="badge bg-danger">Redução</span>
                      ) : (
                        <span className="badge bg-secondary">Estável</span>
                      )}
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
          <li><strong>Atividades Operacionais:</strong> Receitas e despesas relacionadas à atividade principal da empresa</li>
          <li><strong>Atividades de Investimento:</strong> Compra e venda de ativos de longo prazo e investimentos</li>
          <li><strong>Atividades de Financiamento:</strong> Captação e devolução de recursos de sócios e terceiros</li>
          <li><strong>Método Direto:</strong> Apresenta os recebimentos e pagamentos brutos de caixa</li>
        </ul>
      </div>
    </div>
  );
}
