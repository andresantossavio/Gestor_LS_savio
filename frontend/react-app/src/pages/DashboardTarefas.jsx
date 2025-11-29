import React, { useEffect, useState, useCallback } from 'react';
import Header from '../components/Header';

const apiBase = '/api';

export default function DashboardTarefas() {
  const [estatisticas, setEstatisticas] = useState(null);
  const [metricasResponsavel, setMetricasResponsavel] = useState([]);
  const [tempoMedio, setTempoMedio] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    try {
      const [estatRes, metricasRes, tempoRes] = await Promise.all([
        fetch(`${apiBase}/tarefas/estatisticas`),
        fetch(`${apiBase}/tarefas/metricas-responsavel`),
        fetch(`${apiBase}/tarefas/tempo-medio-tipo`)
      ]);

      if (estatRes.ok) setEstatisticas(await estatRes.json());
      if (metricasRes.ok) setMetricasResponsavel(await metricasRes.json());
      if (tempoRes.ok) setTempoMedio(await tempoRes.json());
    } catch (err) {
      console.error('Erro ao carregar dashboard:', err);
      alert('Erro ao carregar dados do dashboard.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const handleExportarExcel = () => {
    alert('Funcionalidade de exportação será implementada');
  };

  const getStatusColor = (status) => {
    const cores = {
      'Pendente': '#ef4444',
      'Em Andamento': '#FFC107',
      'Concluída': '#22c55e',
      'Cancelada': '#6b7280',
    };
    return cores[status] || '#9ca3af';
  };

  const CardKPI = ({ titulo, valor, cor, icone }) => (
    <div
      className="card"
      style={{
        flex: 1,
        minWidth: '200px',
        padding: '20px',
        textAlign: 'center',
        borderLeft: `4px solid ${cor}`,
      }}
    >
      <div style={{ fontSize: '32px', marginBottom: '10px' }}>{icone}</div>
      <div style={{ fontSize: '36px', fontWeight: 700, color: cor, marginBottom: '8px' }}>
        {valor}
      </div>
      <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: 500 }}>
        {titulo}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div style={{ padding: 20 }}>
        <Header title="Dashboard de Tarefas" />
        <p>Carregando...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <Header title="Dashboard de Tarefas" />
        <div style={{ display: 'flex', gap: 10 }}>
          <button onClick={loadDashboard} className="btn btn-secondary">
            🔄 Atualizar
          </button>
          <button onClick={handleExportarExcel} className="btn btn-primary">
            📊 Exportar Dashboard
          </button>
        </div>
      </div>

      {/* Cards KPI */}
      {estatisticas && (
        <>
          <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', marginBottom: '20px' }}>
            <CardKPI
              titulo="Total de Tarefas"
              valor={estatisticas.total}
              cor="#3b82f6"
              icone="📋"
            />
            <CardKPI
              titulo="Pendentes"
              valor={estatisticas.por_status['Pendente'] || 0}
              cor="#ef4444"
              icone="⏰"
            />
            <CardKPI
              titulo="Em Andamento"
              valor={estatisticas.por_status['Em Andamento'] || 0}
              cor="#FFC107"
              icone="🔄"
            />
            <CardKPI
              titulo="Concluídas"
              valor={estatisticas.por_status['Concluída'] || 0}
              cor="#22c55e"
              icone="✅"
            />
          </div>

          <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', marginBottom: '20px' }}>
            <CardKPI
              titulo="Tarefas Vencidas"
              valor={estatisticas.vencidas}
              cor="#dc2626"
              icone="⚠️"
            />
            <CardKPI
              titulo="Próximas a Vencer (7 dias)"
              valor={estatisticas.proximas_vencer}
              cor="#f59e0b"
              icone="🔔"
            />
          </div>

          {/* Gráfico de Tarefas por Status */}
          <div className="card" style={{ marginBottom: 20 }}>
            <h3 style={{ marginTop: 0, marginBottom: 15 }}>Distribuição por Status</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {Object.entries(estatisticas.por_status).map(([status, quantidade]) => {
                const total = estatisticas.total || 1;
                const percentual = (quantidade / total * 100).toFixed(1);
                
                return (
                  <div key={status}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '14px' }}>
                      <span style={{ fontWeight: 500 }}>{status}</span>
                      <span style={{ color: '#6b7280' }}>{quantidade} ({percentual}%)</span>
                    </div>
                    <div
                      style={{
                        width: '100%',
                        height: '24px',
                        backgroundColor: '#f3f4f6',
                        borderRadius: '12px',
                        overflow: 'hidden',
                      }}
                    >
                      <div
                        style={{
                          width: `${percentual}%`,
                          height: '100%',
                          backgroundColor: getStatusColor(status),
                          transition: 'width 0.3s',
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Gráfico de Tarefas por Tipo */}
          <div className="card" style={{ marginBottom: 20 }}>
            <h3 style={{ marginTop: 0, marginBottom: 15 }}>Tarefas por Tipo</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {estatisticas.por_tipo.map(item => {
                const total = estatisticas.total || 1;
                const percentual = (item.quantidade / total * 100).toFixed(1);
                
                return (
                  <div key={item.tipo}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '14px' }}>
                      <span style={{ fontWeight: 500 }}>{item.tipo}</span>
                      <span style={{ color: '#6b7280' }}>{item.quantidade} ({percentual}%)</span>
                    </div>
                    <div
                      style={{
                        width: '100%',
                        height: '24px',
                        backgroundColor: '#f3f4f6',
                        borderRadius: '12px',
                        overflow: 'hidden',
                      }}
                    >
                      <div
                        style={{
                          width: `${percentual}%`,
                          height: '100%',
                          backgroundColor: '#3b82f6',
                          transition: 'width 0.3s',
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}

      {/* Métricas por Responsável */}
      {metricasResponsavel.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ marginTop: 0, marginBottom: 15 }}>Produtividade por Responsável</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f3f4f6', borderBottom: '2px solid #e5e7eb' }}>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: 600 }}>Responsável</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600 }}>Total</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600 }}>Pendentes</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600 }}>Em Andamento</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600 }}>Concluídas</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600 }}>Taxa de Conclusão</th>
                </tr>
              </thead>
              <tbody>
                {metricasResponsavel.map(metrica => (
                  <tr key={metrica.responsavel_id} style={{ borderBottom: '1px solid #e5e7eb' }}>
                    <td style={{ padding: '12px' }}>
                      <strong>{metrica.responsavel}</strong>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      {metrica.total}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <span style={{ color: '#ef4444', fontWeight: 600 }}>
                        {metrica.pendentes}
                      </span>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <span style={{ color: '#FFC107', fontWeight: 600 }}>
                        {metrica.em_andamento}
                      </span>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <span style={{ color: '#22c55e', fontWeight: 600 }}>
                        {metrica.concluidas}
                      </span>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                        <div
                          style={{
                            width: '60px',
                            height: '8px',
                            backgroundColor: '#f3f4f6',
                            borderRadius: '4px',
                            overflow: 'hidden',
                          }}
                        >
                          <div
                            style={{
                              width: `${metrica.taxa_conclusao}%`,
                              height: '100%',
                              backgroundColor: '#22c55e',
                            }}
                          />
                        </div>
                        <span style={{ fontSize: '13px', fontWeight: 600 }}>
                          {metrica.taxa_conclusao}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tempo Médio por Tipo */}
      {tempoMedio.length > 0 && (
        <div className="card">
          <h3 style={{ marginTop: 0, marginBottom: 15 }}>Tempo Médio de Conclusão por Tipo</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
            {tempoMedio.map(item => (
              <div
                key={item.tipo}
                style={{
                  padding: '15px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '8px',
                  borderLeft: '4px solid #3b82f6',
                }}
              >
                <div style={{ fontWeight: 600, marginBottom: '8px', color: '#374151' }}>
                  {item.tipo}
                </div>
                <div style={{ fontSize: '28px', fontWeight: 700, color: '#3b82f6', marginBottom: '4px' }}>
                  {item.tempo_medio_dias} <span style={{ fontSize: '16px' }}>dias</span>
                </div>
                <div style={{ fontSize: '13px', color: '#6b7280' }}>
                  {item.quantidade_concluidas} tarefas concluídas
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
