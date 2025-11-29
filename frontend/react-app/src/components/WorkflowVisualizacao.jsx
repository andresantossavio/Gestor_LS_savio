import React from 'react';

export default function WorkflowVisualizacao({ tarefa }) {
  if (!tarefa) return null;

  const etapaAtual = tarefa.etapa_workflow_atual;
  const historico = tarefa.workflow_historico || [];

  // Definir etapas padrão baseadas no tipo de tarefa
  const getEtapasPadrao = () => {
    const tipoNome = tarefa.tipo_tarefa?.nome || '';
    
    if (tipoNome.includes('Intimação')) {
      return ['Análise', 'Classificação', 'Concluída'];
    }
    if (tipoNome === 'Petição' || tipoNome === 'Recurso') {
      return ['Elaboração', 'Revisão', 'Protocolização', 'Concluída'];
    }
    if (tipoNome === 'Preparar Audiência') {
      return ['Preparação', 'Realização', 'Concluída'];
    }
    
    return ['Iniciada', 'Em Andamento', 'Concluída'];
  };

  const etapas = getEtapasPadrao();
  const etapaAtualIndex = etapas.indexOf(etapaAtual);

  const getEtapaStyle = (index) => {
    const base = {
      flex: 1,
      padding: '12px',
      textAlign: 'center',
      borderRadius: '8px',
      fontSize: '13px',
      fontWeight: 500,
      position: 'relative',
      transition: 'all 0.3s',
    };

    if (index < etapaAtualIndex) {
      // Etapa concluída
      return {
        ...base,
        backgroundColor: '#dcfce7',
        color: '#166534',
        border: '2px solid #22c55e',
      };
    }

    if (index === etapaAtualIndex) {
      // Etapa atual
      return {
        ...base,
        backgroundColor: '#fef3c7',
        color: '#92400e',
        border: '2px solid #FFC107',
        fontWeight: 600,
        boxShadow: '0 0 0 3px rgba(255, 193, 7, 0.2)',
      };
    }

    // Etapa futura
    return {
      ...base,
      backgroundColor: '#f3f4f6',
      color: '#9ca3af',
      border: '2px solid #e5e7eb',
    };
  };

  const getIcone = (index) => {
    if (index < etapaAtualIndex) return '✓';
    if (index === etapaAtualIndex) return '⏳';
    return '○';
  };

  return (
    <div className="card" style={{ padding: 20 }}>
      <h4 style={{ margin: '0 0 20px 0', fontSize: 16, fontWeight: 600, color: '#374151' }}>
        Workflow da Tarefa
      </h4>

      {/* Barra de progresso */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: 20 }}>
        {etapas.map((etapa, index) => (
          <div key={index} style={getEtapaStyle(index)}>
            <div style={{ fontSize: 18, marginBottom: 4 }}>
              {getIcone(index)}
            </div>
            <div>{etapa}</div>
          </div>
        ))}
      </div>

      {/* Histórico de transições */}
      {historico.length > 0 && (
        <div style={{ marginTop: 20, borderTop: '1px solid #e5e7eb', paddingTop: 15 }}>
          <h5 style={{ margin: '0 0 10px 0', fontSize: 14, fontWeight: 600, color: '#374151' }}>
            Histórico de Mudanças
          </h5>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {historico.map((evento, index) => (
              <div
                key={index}
                style={{
                  padding: '10px',
                  backgroundColor: '#f9fafb',
                  borderLeft: '3px solid #FFC107',
                  borderRadius: '4px',
                  fontSize: 13,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <strong style={{ color: '#374151' }}>
                    {evento.etapa_anterior} → {evento.nova_etapa}
                  </strong>
                  <span style={{ color: '#6b7280', fontSize: 12 }}>
                    {new Date(evento.data).toLocaleString('pt-BR')}
                  </span>
                </div>
                {evento.usuario && (
                  <div style={{ color: '#6b7280', fontSize: 12 }}>
                    Por: {evento.usuario.nome || 'Sistema'}
                  </div>
                )}
                {evento.observacao && (
                  <div style={{ color: '#6b7280', fontSize: 12, marginTop: 4 }}>
                    {evento.observacao}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Informações adicionais */}
      <div style={{ marginTop: 20, padding: 15, backgroundColor: '#f9fafb', borderRadius: 8 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, fontSize: 13 }}>
          <div>
            <strong>Status:</strong> {tarefa.status || 'N/A'}
          </div>
          <div>
            <strong>Responsável:</strong> {tarefa.responsavel?.nome || 'Não atribuído'}
          </div>
          {tarefa.prazo_administrativo && (
            <div>
              <strong>Prazo Administrativo:</strong>{' '}
              {new Date(tarefa.prazo_administrativo + 'T00:00:00').toLocaleDateString('pt-BR')}
            </div>
          )}
          {tarefa.prazo_fatal && (
            <div>
              <strong>Prazo Fatal:</strong>{' '}
              {new Date(tarefa.prazo_fatal + 'T00:00:00').toLocaleDateString('pt-BR')}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
