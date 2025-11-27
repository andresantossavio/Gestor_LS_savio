import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FaEdit } from 'react-icons/fa'; // Ícone de edição
import Header from '../components/Header';

const apiBase = '/api';

export default function ProcessoDetalhe() {
  const { processoId } = useParams(); // Pega o ID da URL
  const [processo, setProcesso] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProcesso = async () => {
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
    };

    fetchProcesso();
  }, [processoId]);

  if (loading) return <div>Carregando...</div>;
  if (error) return <div>Erro: {error}</div>;
  if (!processo) return <div>Processo não encontrado.</div>;

  return (
    <div style={{ padding: 20 }}>
      <Link to="/processos">{"< Voltar para a lista de processos"}</Link>
      
      {/* Cabeçalho com informações principais e ações */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        borderBottom: '2px solid #ccc', 
        paddingBottom: '10px', 
        marginBottom: '20px' 
      }}>
        <div>
          <Header title={`Processo: ${processo.numero || 'Sem Número'}`} />
          <p style={{ margin: 0 }}><strong>Cliente:</strong> {processo.cliente?.nome || 'N/A'}</p>
          <p style={{ margin: 0 }}><strong>Autor:</strong> {processo.autor || 'N/A'}</p>
          <p style={{ margin: 0 }}><strong>Réu:</strong> {processo.reu || 'N/A'}</p>
        </div>
        <div>
          {/* Botões de Ação Fixos */}
          <button style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <FaEdit /> Editar Processo
          </button>
          {/* Outros botões podem ser adicionados aqui */}
        </div>
      </div>

      {/* Seções para Andamentos, Tarefas, etc. */}
      <div style={{ marginTop: '30px', display: 'grid', gap: '20px' }}>
        <section style={{ border: '1px solid #eee', padding: '15px', borderRadius: '5px' }}>
          <h3>Andamentos</h3>
        </section>
        <section style={{ border: '1px solid #eee', padding: '15px', borderRadius: '5px' }}>
          <h3>Tarefas</h3>
        </section>
        <section style={{ border: '1px solid #eee', padding: '15px', borderRadius: '5px' }}>
          <h3>Pagamentos</h3>
        </section>
      </div>
    </div>
  );
}