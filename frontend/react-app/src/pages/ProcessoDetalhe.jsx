import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import Header from '../components/Header';
import ProcessoForm from '../components/ProcessoForm'; // Importa o formulário

const apiBase = '/api';

export default function ProcessoDetalhe() {
  const { processoId } = useParams(); // Pega o ID da URL
  const [processo, setProcesso] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [exibirForm, setExibirForm] = useState(false); // Estado para exibir o formulário

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

  useEffect(() => {
    fetchProcesso();
  }, [fetchProcesso]);

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
          {processo.uf && <div><strong>UF:</strong> {processo.uf}</div>}
          {processo.comarca && <div><strong>Comarca:</strong> {processo.comarca}</div>}
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
        <h3>Tarefas</h3>
        {/* Futuramente, listar as tarefas aqui */}
        <p>Nenhuma tarefa registrada.</p>
      </div>
      
      <div className="card">
        <h3>Pagamentos</h3>
        {/* Futuramente, listar os pagamentos aqui */}
        <p>Nenhum pagamento registrado.</p>
      </div>
    </div>
  );
}