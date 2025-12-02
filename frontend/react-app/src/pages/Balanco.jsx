import React, { useState, useEffect } from 'react';

export default function Balanco() {
  const [balanco, setBalanco] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mesAno, setMesAno] = useState(() => {
    const hoje = new Date();
    return `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}`;
  });

  useEffect(() => {
    carregarBalanco();
  }, [mesAno]);

  const carregarBalanco = async () => {
    setLoading(true);
    try {
      const [ano, mes] = mesAno.split('-');
      const response = await fetch(`/api/contabilidade/balanco-patrimonial?mes=${mes}&ano=${ano}`);
      const data = await response.json();
      setBalanco(data);
    } catch (error) {
      console.error('Erro ao carregar balanço:', error);
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

  const renderGrupo = (grupo, nivel = 0) => {
    if (!grupo) return null;

    return (
      <React.Fragment key={grupo.codigo}>
        <tr style={{ 
          backgroundColor: nivel === 0 ? '#e9ecef' : nivel === 1 ? '#f8f9fa' : 'white',
          fontWeight: nivel <= 1 ? 'bold' : 'normal'
        }}>
          <td style={{ paddingLeft: `${nivel * 20 + 10}px` }}>
            {grupo.codigo} - {grupo.nome}
          </td>
          <td className="text-end">{formatarValor(grupo.saldo)}</td>
        </tr>
        {grupo.subgrupos && grupo.subgrupos.map(sub => renderGrupo(sub, nivel + 1))}
      </React.Fragment>
    );
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

  if (!balanco) {
    return (
      <div className="container mt-4">
        <div className="alert alert-warning">
          Erro ao carregar balanço patrimonial
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Balanço Patrimonial</h2>
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

      <div className="row">
        {/* ATIVO */}
        <div className="col-md-6">
          <div className="card mb-4">
            <div className="card-header bg-primary text-white">
              <h5 className="mb-0">ATIVO</h5>
            </div>
            <div className="card-body p-0">
              <table className="table table-sm mb-0">
                <tbody>
                  {balanco.ativo && balanco.ativo.map(grupo => renderGrupo(grupo))}
                  <tr className="table-primary fw-bold">
                    <td>TOTAL DO ATIVO</td>
                    <td className="text-end">{formatarValor(balanco.totais?.ativo)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* PASSIVO + PL */}
        <div className="col-md-6">
          <div className="card mb-4">
            <div className="card-header bg-danger text-white">
              <h5 className="mb-0">PASSIVO</h5>
            </div>
            <div className="card-body p-0">
              <table className="table table-sm mb-0">
                <tbody>
                  {balanco.passivo && balanco.passivo.map(grupo => renderGrupo(grupo))}
                  <tr className="table-danger fw-bold">
                    <td>TOTAL DO PASSIVO</td>
                    <td className="text-end">{formatarValor(balanco.totais?.passivo)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div className="card mb-4">
            <div className="card-header bg-success text-white">
              <h5 className="mb-0">PATRIMÔNIO LÍQUIDO</h5>
            </div>
            <div className="card-body p-0">
              <table className="table table-sm mb-0">
                <tbody>
                  {balanco.patrimonioLiquido && balanco.patrimonioLiquido.map(grupo => renderGrupo(grupo))}
                  <tr className="table-success fw-bold">
                    <td>TOTAL DO PATRIMÔNIO LÍQUIDO</td>
                    <td className="text-end">{formatarValor(balanco.totais?.patrimonioLiquido)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div className="card">
            <div className="card-header bg-dark text-white">
              <h5 className="mb-0">TOTAL PASSIVO + PL</h5>
            </div>
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center">
                <h4 className="mb-0">TOTAL</h4>
                <h4 className="mb-0">{formatarValor(balanco.totais?.passivoMaisPl)}</h4>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="alert alert-info mt-4">
        <strong>Equação Fundamental da Contabilidade:</strong> Ativo = Passivo + Patrimônio Líquido
        <br/>
        <strong>Verificação:</strong> {' '}
        {Math.abs((balanco.totais?.ativo || 0) - (balanco.totais?.passivoMaisPl || 0)) < 0.01 ? (
          <span className="text-success">✓ Balanço fechado corretamente</span>
        ) : (
          <span className="text-danger">✗ Há diferença no balanço - verificar lançamentos</span>
        )}
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <h5 className="mb-0">Análise Vertical</h5>
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col-md-6">
              <h6>Composição do Ativo</h6>
              <table className="table table-sm">
                <tbody>
                  <tr>
                    <td>Ativo Circulante</td>
                    <td className="text-end">
                      {balanco.ativo?.saldo ? 
                        ((balanco.ativo.subgrupos?.find(s => s.codigo === '1.1')?.saldo || 0) / balanco.ativo.saldo * 100).toFixed(2) : 0}%
                    </td>
                  </tr>
                  <tr>
                    <td>Ativo Não Circulante</td>
                    <td className="text-end">
                      {balanco.ativo?.saldo ? 
                        ((balanco.ativo.subgrupos?.find(s => s.codigo === '1.2')?.saldo || 0) / balanco.ativo.saldo * 100).toFixed(2) : 0}%
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div className="col-md-6">
              <h6>Composição do Passivo + PL</h6>
              <table className="table table-sm">
                <tbody>
                  <tr>
                    <td>Passivo Circulante</td>
                    <td className="text-end">
                      {balanco.ativo?.saldo ? 
                        ((balanco.passivo?.subgrupos?.find(s => s.codigo === '2.1')?.saldo || 0) / balanco.ativo.saldo * 100).toFixed(2) : 0}%
                    </td>
                  </tr>
                  <tr>
                    <td>Passivo Não Circulante</td>
                    <td className="text-end">
                      {balanco.ativo?.saldo ? 
                        ((balanco.passivo?.subgrupos?.find(s => s.codigo === '2.2')?.saldo || 0) / balanco.ativo.saldo * 100).toFixed(2) : 0}%
                    </td>
                  </tr>
                  <tr>
                    <td>Patrimônio Líquido</td>
                    <td className="text-end">
                      {balanco.ativo?.saldo ? 
                        ((balanco.patrimonio_liquido?.saldo || 0) / balanco.ativo.saldo * 100).toFixed(2) : 0}%
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <h5 className="mb-0">Indicadores Financeiros</h5>
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col-md-4">
              <h6>Liquidez Corrente</h6>
              <p className="fs-4 fw-bold text-primary">
                {balanco.passivo?.subgrupos?.find(s => s.codigo === '2.1')?.saldo ? 
                  ((balanco.ativo?.subgrupos?.find(s => s.codigo === '1.1')?.saldo || 0) / 
                   (balanco.passivo?.subgrupos?.find(s => s.codigo === '2.1')?.saldo || 1)).toFixed(2) : 
                  '∞'}
              </p>
              <small className="text-muted">Ativo Circulante / Passivo Circulante</small>
            </div>
            <div className="col-md-4">
              <h6>Endividamento Geral</h6>
              <p className="fs-4 fw-bold text-warning">
                {balanco.ativo?.saldo ? 
                  (((balanco.passivo?.saldo || 0) / balanco.ativo.saldo) * 100).toFixed(2) : 0}%
              </p>
              <small className="text-muted">Passivo Total / Ativo Total</small>
            </div>
            <div className="col-md-4">
              <h6>Patrimônio Líquido</h6>
              <p className="fs-4 fw-bold text-success">
                {formatarValor(balanco.patrimonio_liquido?.saldo)}
              </p>
              <small className="text-muted">Capital próprio da empresa</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
