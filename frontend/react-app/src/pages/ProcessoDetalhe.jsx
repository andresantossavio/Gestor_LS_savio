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