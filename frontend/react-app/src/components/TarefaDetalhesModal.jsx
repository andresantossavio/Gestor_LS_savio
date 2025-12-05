import React, { useState, useEffect } from 'react';
import TarefaIntimacaoForm from './TarefaIntimacaoForm';

const apiBase = 'http://localhost:8080/api';

export default function TarefaDetalhesModal({ tarefa, processoId, onClose, onAtualizar }) {
  const [usuarios, setUsuarios] = useState([]);
  const [tarefasDerivadas, setTarefasDerivadas] = useState([]);
  const [exibirFormClassificar, setExibirFormClassificar] = useState(false);

  // Verificação mais flexível para intimações
  const tipoNome = tarefa.tipo_tarefa?.nome || '';
  const isIntimacao = tipoNome === 'Análise de Intimação' || tipoNome.toLowerCase().includes('intimação') || tipoNome.toLowerCase().includes('intimacao');
  const jaConcluida = tarefa.status === 'Concluída' || tarefa.etapa_workflow_atual === 'concluido';
  
  // Debug - remover depois
  useEffect(() => {
    console.log('=== DEBUG TarefaDetalhesModal ===');
    console.log('Tarefa completa:', tarefa);
    console.log('tipo_tarefa:', tarefa.tipo_tarefa);
    console.log('tipo_tarefa.nome:', tipoNome);
    console.log('isIntimacao:', isIntimacao);
    console.log('================================');
  }, [tarefa]);

  useEffect(() => {
    const fetchDados = async () => {
      try {
        const usuariosRes = await fetch(`${apiBase}/usuarios`);
        if (usuariosRes.ok) {
          setUsuarios(await usuariosRes.json());
        }

        const derivadasRes = await fetch(`${apiBase}/tarefas/${tarefa.id}/derivadas`);
        if (derivadasRes.ok) {
          setTarefasDerivadas(await derivadasRes.json());
        }
      } catch (err) {
        console.error('Erro ao carregar dados:', err);
      }
    };

    fetchDados();
  }, [tarefa.id]);

  const avancarWorkflow = async (novaEtapa) => {
    try {
      const res = await fetch(`${apiBase}/tarefas/${tarefa.id}/workflow/avancar`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nova_etapa: novaEtapa,
          acao: `Avançou para ${novaEtapa}`
        })
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Erro ao avançar workflow');
      }

      alert('Workflow avançado com sucesso!');
      onAtualizar();
      onClose();
    } catch (err) {
      console.error(err);
      alert('Erro: ' + err.message);
    }
  };

  const concluirTarefa = async () => {
    if (!confirm('Deseja realmente concluir esta tarefa?')) return;

    try {
      const res = await fetch(`${apiBase}/tarefas/${tarefa.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...tarefa,
          status: 'Concluída',
          etapa_workflow_atual: 'concluido'
        })
      });

      if (!res.ok) {
        throw new Error('Erro ao concluir tarefa');
      }

      alert('Tarefa concluída com sucesso!');
      onAtualizar();
      onClose();
    } catch (err) {
      alert('Erro ao concluir tarefa: ' + err.message);
    }
  };

  const atribuirResponsavel = async (responsavelId) => {
    try {
      const res = await fetch(`${apiBase}/tarefas/${tarefa.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...tarefa,
          responsavel_id: responsavelId ? parseInt(responsavelId) : null
        })
      });

      if (!res.ok) {
        throw new Error('Erro ao atribuir responsável');
      }

      alert('Responsável atribuído com sucesso!');
      onAtualizar();
    } catch (err) {
      alert('Erro: ' + err.message);
    }
  };

  return (
    <>
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
            maxWidth: '800px',
            maxHeight: '90vh',
            overflowY: 'auto',
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
            <div>
              <h2 style={{ margin: 0, marginBottom: '5px' }}>{tipoNome || 'Tarefa'}</h2>
              <span style={{
                display: 'inline-block',
                padding: '4px 12px',
                borderRadius: '12px',
                fontSize: '12px',
                fontWeight: 600,
                backgroundColor: jaConcluida ? '#10b981' : tarefa.status === 'Em Andamento' ? '#f59e0b' : '#6b7280',
                color: 'white'
              }}>
                {tarefa.status || 'Pendente'}
              </span>
            </div>
            <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer' }}>
              ×
            </button>
          </div>

          <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
            <div style={{ marginBottom: '10px' }}>
              <strong>Etapa do Workflow:</strong> {tarefa.etapa_workflow_atual || 'N/A'}
            </div>
            
            {tarefa.prazo_fatal && (
              <div style={{ marginBottom: '10px' }}>
                <strong>Prazo Fatal:</strong> {new Date(tarefa.prazo_fatal + 'T00:00:00').toLocaleDateString('pt-BR')}
              </div>
            )}

            {tarefa.prazo_administrativo && (
              <div style={{ marginBottom: '10px' }}>
                <strong>Prazo Administrativo:</strong> {new Date(tarefa.prazo_administrativo + 'T00:00:00').toLocaleDateString('pt-BR')}
              </div>
            )}

            <div style={{ marginBottom: '10px' }}>
              <strong>Responsável:</strong>{' '}
              <select
                value={tarefa.responsavel_id || ''}
                onChange={(e) => atribuirResponsavel(e.target.value)}
                disabled={jaConcluida}
                style={{ marginLeft: '10px', padding: '4px 8px', borderRadius: '4px', border: '1px solid #d1d5db' }}
              >
                <option value="">Nenhum</option>
                {usuarios.map(u => (
                  <option key={u.id} value={u.id}>{u.nome}</option>
                ))}
              </select>
            </div>

            {tarefa.descricao_complementar && (
              <div style={{ marginTop: '15px' }}>
                <strong>Descrição:</strong>
                <p style={{ marginTop: '5px', whiteSpace: 'pre-wrap' }}>{tarefa.descricao_complementar}</p>
              </div>
            )}
          </div>

          {isIntimacao && (
            <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#fef3c7', borderRadius: '8px' }}>
              <h4 style={{ marginTop: 0 }}>Conteúdo da Intimação</h4>
              <p style={{ fontSize: '11px', color: '#999', marginTop: '-5px', marginBottom: '10px' }}>Tipo: {tipoNome}</p>
              {tarefa.conteudo_intimacao ? (
                <p style={{ whiteSpace: 'pre-wrap' }}>{tarefa.conteudo_intimacao}</p>
              ) : (
                <p style={{ color: '#6b7280', fontStyle: 'italic' }}>Conteúdo da intimação não informado</p>
              )}
              
              {tarefa.classificacao_intimacao ? (
                <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#fff', borderRadius: '6px' }}>
                  <strong>Classificação:</strong> <span style={{ color: '#059669', fontWeight: 600 }}>{tarefa.classificacao_intimacao}</span>
                </div>
              ) : (
                <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#fff3cd', borderRadius: '6px', border: '1px solid #ffc107' }}>
                  <strong>⚠️ Intimação pendente de classificação</strong>
                </div>
              )}

              {tarefa.conteudo_decisao && (
                <div style={{ marginTop: '10px' }}>
                  <strong>Conteúdo da Decisão:</strong>
                  <p style={{ whiteSpace: 'pre-wrap', marginTop: '5px' }}>{tarefa.conteudo_decisao}</p>
                </div>
              )}
            </div>
          )}

          {tarefa.workflow_historico && tarefa.workflow_historico.length > 0 && (
            <div style={{ marginBottom: '20px' }}>
              <h4>Histórico do Workflow</h4>
              <div style={{ borderLeft: '3px solid #3b82f6', paddingLeft: '15px' }}>
                {tarefa.workflow_historico.map((item, idx) => (
                  <div key={idx} style={{ marginBottom: '15px', paddingBottom: '15px', borderBottom: '1px solid #e5e7eb' }}>
                    <div style={{ fontSize: '14px', color: '#6b7280' }}>
                      {new Date(item.timestamp).toLocaleString('pt-BR')}
                    </div>
                    <div style={{ fontWeight: 500, marginTop: '5px' }}>
                      {item.etapa_anterior} → {item.etapa_nova}
                    </div>
                    <div style={{ fontSize: '14px', marginTop: '3px' }}>{item.acao}</div>
                    <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '3px' }}>
                      Por: {item.usuario_nome}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {tarefasDerivadas.length > 0 && (
            <div style={{ marginBottom: '20px' }}>
              <h4>Tarefas Derivadas</h4>
              <ul>
                {tarefasDerivadas.map(td => (
                  <li key={td.id}>
                    {td.tipo_tarefa?.nome} - {td.status}
                    {td.prazo_fatal && ` (Prazo: ${new Date(td.prazo_fatal + 'T00:00:00').toLocaleDateString('pt-BR')})`}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {!jaConcluida && (
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #e5e7eb' }}>
              {isIntimacao && !tarefa.classificacao_intimacao && (
                <button
                  onClick={() => setExibirFormClassificar(true)}
                  className="btn btn-primary"
                  style={{ fontSize: '16px', fontWeight: 600 }}
                >
                  📋 Classificar Intimação
                </button>
              )}

              {isIntimacao && tarefa.classificacao_intimacao && (
                <button
                  onClick={() => setExibirFormClassificar(true)}
                  className="btn btn-secondary"
                >
                  Reclassificar
                </button>
              )}

              {!isIntimacao && tarefa.etapa_workflow_atual === 'em_andamento' && (
                <button
                  onClick={() => avancarWorkflow('concluido')}
                  className="btn btn-success"
                >
                  Marcar como Concluída
                </button>
              )}

              {!isIntimacao && (
                <button
                  onClick={concluirTarefa}
                  className="btn"
                  style={{ backgroundColor: '#10b981', color: 'white' }}
                >
                  Concluir Tarefa
                </button>
              )}

              <button onClick={onClose} className="btn btn-secondary">
                Fechar
              </button>
            </div>
          )}
        </div>
      </div>

      {exibirFormClassificar && (
        <TarefaIntimacaoForm
          processoId={processoId}
          tarefaParaClassificar={tarefa}
          onClose={() => setExibirFormClassificar(false)}
          onFormSubmit={() => {
            setExibirFormClassificar(false);
            onAtualizar();
            onClose();
          }}
        />
      )}
    </>
  );
}
