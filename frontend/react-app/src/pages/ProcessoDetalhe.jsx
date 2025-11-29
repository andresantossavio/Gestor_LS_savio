import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import Header from '../components/Header';
import ProcessoForm from '../components/ProcessoForm'; // Importa o formulário
import CalendarioProcesso from '../components/CalendarioProcesso';
import TarefaForm from '../components/TarefaForm';

const apiBase = '/api';

export default function ProcessoDetalhe() {
  const { processoId } = useParams(); // Pega o ID da URL
  const [processo, setProcesso] = useState(null);
  const [tarefas, setTarefas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [exibirForm, setExibirForm] = useState(false); // Estado para exibir o formulário
  const [exibirFormTarefa, setExibirFormTarefa] = useState(false); // Estado para exibir formulário de tarefa

  const fetchProcesso = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch(`${apiBase}/processos/${processoId}`);
      if (!res.ok) {
        throw new Error(`Erro na API: ${res.status}`);
      }
      const data = await res.json();
      setProcesso(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [processoId]);

  const fetchTarefas = useCallback(async () => {
    try {
      // Buscar tarefas do processo - usando filtros da API
      const res = await fetch(`${apiBase}/tarefas/filtros?processo_id=${processoId}`);
      if (!res.ok) {
        console.error('Erro ao buscar tarefas');
        return;
      }
      const data = await res.json();
      setTarefas(data);
    } catch (err) {
      console.error('Erro ao buscar tarefas:', err);
    }
  }, [processoId]);

  useEffect(() => {
    fetchProcesso();
    fetchTarefas();
  }, [fetchProcesso, fetchTarefas]);

  if (loading) return <div className="content">Carregando...</div>;
  if (error) return <div className="content">Erro: {error}</div>;
  if (!processo) return <div className="content">Processo não encontrado.</div>;

  // Se o formulário de edição deve ser exibido
  if (exibirForm) {
    return (
      <div className="content">
        <Header title={`Editando Processo: ${processo.numero}`} />
        <ProcessoForm
          processoParaEditar={processo}
          onFormSubmit={() => {
            setExibirForm(false); // Esconde o formulário
            fetchProcesso(); // Recarrega os dados do processo
          }}
          onCancel={() => setExibirForm(false)} // Esconde o formulário ao cancelar
        />
      </div>
    );
  }

  return (
    <div className="content">
      <Link to="/processos" className="btn btn-secondary" style={{ marginBottom: '20px' }}>
        &larr; Voltar para a lista
      </Link>
      
      {/* Cabeçalho com informações principais e ações */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <Header title={`Processo: ${processo.numero || 'Sem Número'}`} />
            <p><strong>Cliente:</strong> {processo.cliente?.nome || 'N/A'}</p>
            <p><strong>Autor:</strong> {processo.autor || 'N/A'}</p>
            <p><strong>Réu:</strong> {processo.reu || 'N/A'}</p>
          </div>
          <button 
            onClick={() => setExibirForm(true)}
            className="btn btn-primary"
          >
            Editar Processo
          </button>
        </div>
      </div>

      {/* Informações Detalhadas do Processo */}
      <div className="card">
        <h3>Informações do Processo</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
          <div><strong>Status:</strong> {processo.status || 'N/A'}</div>
          <div><strong>Fase:</strong> {processo.fase || 'N/A'}</div>
          <div><strong>Categoria:</strong> {processo.categoria || 'N/A'}</div>
          <div><strong>Tipo:</strong> {processo.tipo || 'N/A'}</div>
          {processo.rito && <div><strong>Rito:</strong> {processo.rito}</div>}
          {processo.classe && <div><strong>Classe:</strong> {processo.classe}</div>}
          {processo.sub_classe && <div><strong>Sub-classe:</strong> {processo.sub_classe}</div>}
          {processo.esfera_justica && <div><strong>Esfera de Justiça:</strong> {processo.esfera_justica}</div>}
          {processo.tribunal_originario && <div><strong>Tribunal Originário:</strong> {processo.tribunal_originario}</div>}
          {processo.municipio && <div><strong>Município:</strong> {processo.municipio.nome} - {processo.municipio.uf}</div>}
          {processo.vara && <div><strong>Vara:</strong> {processo.vara}</div>}
          {processo.data_abertura && <div><strong>Data de Abertura:</strong> {processo.data_abertura}</div>}
          {processo.data_fechamento && <div><strong>Data de Fechamento:</strong> {processo.data_fechamento}</div>}
        </div>
        {processo.observacoes && (
          <div style={{ marginTop: '15px' }}>
            <strong>Observações:</strong>
            <p style={{ marginTop: '5px', whiteSpace: 'pre-wrap' }}>{processo.observacoes}</p>
          </div>
        )}
      </div>

      {/* Seções para Andamentos, Tarefas, etc. */}
      <div className="card">
        <h3>Andamentos</h3>
        {/* Futuramente, listar os andamentos aqui */}
        <p>Nenhum andamento registrado.</p>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h3 style={{ margin: 0 }}>Tarefas</h3>
          <button 
            onClick={() => setExibirFormTarefa(true)}
            className="btn btn-primary"
          >
            + Nova Tarefa
          </button>
        </div>
        {tarefas.length === 0 ? (
          <p>Nenhuma tarefa registrada.</p>
        ) : (
          <ul>
            {tarefas.map(tarefa => (
              <li key={tarefa.id}>
                <strong>{tarefa.tipo_tarefa?.nome || 'Tarefa'}</strong> 
                {tarefa.prazo_fatal && ` - Prazo: ${new Date(tarefa.prazo_fatal + 'T00:00:00').toLocaleDateString('pt-BR')}`}
                {tarefa.status && ` - Status: ${tarefa.status}`}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Calendário do Processo */}
      {processo?.municipio_id && (
        <div>
          <h3 style={{ marginTop: 20, marginBottom: 15 }}>Calendário de Prazos</h3>
          <CalendarioProcesso 
            municipioId={processo.municipio_id} 
            tarefas={tarefas}
          />
        </div>
      )}
      
      <div className="card">
        <h3>Pagamentos</h3>
        {/* Futuramente, listar os pagamentos aqui */}
        <p>Nenhum pagamento registrado.</p>
      </div>

      {/* Modal de Criar Tarefa */}
      {exibirFormTarefa && (
        <TarefaForm
          processoId={processoId}
          onClose={() => setExibirFormTarefa(false)}
          onFormSubmit={() => {
            setExibirFormTarefa(false);
            fetchTarefas(); // Recarrega as tarefas
          }}
        />
      )}
    </div>
  );
}