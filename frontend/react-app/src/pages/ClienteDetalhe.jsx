import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import Header from '../components/Header';

const apiBase = '/api';

export default function ClienteDetalhe() {
  const { clienteId } = useParams();
  const navigate = useNavigate();
  const [cliente, setCliente] = useState(null);
  const [processos, setProcessos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCliente = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch(`${apiBase}/clientes/${clienteId}`);
      if (!res.ok) {
        throw new Error(`Erro na API: ${res.status}`);
      }
      const data = await res.json();
      setCliente(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [clienteId]);

  const fetchProcessos = useCallback(async () => {
    try {
      const res = await fetch(`${apiBase}/processos`);
      if (!res.ok) throw new Error(`Erro na API: ${res.status}`);
      const allProcessos = await res.json();
      // Filtra processos deste cliente
      const processosDoCliente = allProcessos.filter(p => p.cliente_id === parseInt(clienteId));
      setProcessos(processosDoCliente);
    } catch (err) {
      console.error(err);
    }
  }, [clienteId]);

  useEffect(() => {
    fetchCliente();
    fetchProcessos();
  }, [fetchCliente, fetchProcessos]);

  if (loading) return <div className="content">Carregando...</div>;
  if (error) return <div className="content">Erro: {error}</div>;
  if (!cliente) return <div className="content">Cliente não encontrado.</div>;

  return (
    <div className="content">
      <Link to="/clientes" className="btn btn-secondary" style={{ marginBottom: '20px' }}>
        &larr; Voltar para a lista
      </Link>
      
      {/* Cabeçalho com informações principais */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <Header title={cliente.nome} />
            {cliente.nome_fantasia && (
              <p style={{ fontSize: '16px', color: '#6b7280', marginTop: '5px' }}>
                Nome Fantasia: {cliente.nome_fantasia}
              </p>
            )}
            <p style={{ marginTop: '10px' }}>
              <strong>{cliente.tipo_pessoa === 'Pessoa Física' ? 'CPF' : cliente.tipo_pessoa === 'Pessoa Jurídica' ? 'CNPJ' : 'CPF/CNPJ'}:</strong> {cliente.cpf_cnpj || 'N/A'}
            </p>
          </div>
          <button 
            onClick={() => navigate('/clientes')}
            className="btn btn-primary"
          >
            Editar Cliente
          </button>
        </div>
      </div>

      {/* Informações Pessoais/Jurídicas */}
      <div className="card">
        <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#374151' }}>
          {cliente.tipo_pessoa === 'Pessoa Física' ? 'Informações Pessoais' : 'Informações da Empresa'}
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
          <div><strong>Tipo:</strong> {cliente.tipo_pessoa || 'N/A'}</div>
          
          {cliente.tipo_pessoa === 'Pessoa Jurídica' && (
            <>
              {cliente.tipo_pj && <div><strong>Tipo de PJ:</strong> {cliente.tipo_pj}</div>}
              {cliente.subtipo_pj && <div><strong>Subtipo:</strong> {cliente.subtipo_pj}</div>}
            </>
          )}
          
          {cliente.tipo_pessoa === 'Pessoa Física' && cliente.capacidade && (
            <div><strong>Capacidade:</strong> {cliente.capacidade}</div>
          )}
          
          {cliente.telefone && <div><strong>Telefone:</strong> {cliente.telefone}</div>}
          {cliente.email && <div><strong>Email:</strong> {cliente.email}</div>}
        </div>

        {/* Responsável Legal (se houver) */}
        {(cliente.responsavel_nome || cliente.responsavel_cpf) && (
          <>
            <h4 style={{ marginTop: '20px', marginBottom: '10px', color: '#374151' }}>Responsável Legal</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
              {cliente.responsavel_nome && <div><strong>Nome:</strong> {cliente.responsavel_nome}</div>}
              {cliente.responsavel_cpf && <div><strong>CPF:</strong> {cliente.responsavel_cpf}</div>}
            </div>
          </>
        )}
      </div>

      {/* Endereço */}
      {(cliente.cep || cliente.logradouro || cliente.cidade) && (
        <div className="card">
          <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#374151' }}>Endereço</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
            {cliente.cep && <div><strong>CEP:</strong> {cliente.cep}</div>}
            {cliente.logradouro && <div><strong>Logradouro:</strong> {cliente.logradouro}</div>}
            {cliente.numero && <div><strong>Número:</strong> {cliente.numero}</div>}
            {cliente.complemento && <div><strong>Complemento:</strong> {cliente.complemento}</div>}
            {cliente.bairro && <div><strong>Bairro:</strong> {cliente.bairro}</div>}
            {cliente.cidade && <div><strong>Cidade:</strong> {cliente.cidade}</div>}
            {cliente.uf && <div><strong>UF:</strong> {cliente.uf}</div>}
          </div>
        </div>
      )}

      {/* Processos do Cliente */}
      <div className="card">
        <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#374151' }}>
          Processos ({processos.length})
        </h3>
        {processos.length === 0 && (
          <p style={{ textAlign: 'center', color: '#6b7280' }}>Nenhum processo cadastrado para este cliente</p>
        )}
        {processos.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {processos.map(p => (
              <div 
                key={p.id} 
                onClick={() => navigate(`/processos/${p.id}`)}
                style={{ 
                  padding: '16px', 
                  backgroundColor: '#f9fafb', 
                  borderRadius: '8px', 
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  border: '1px solid #e5e7eb'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#ffffff';
                  e.currentTarget.style.borderColor = '#FFC107';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 4px 8px rgba(255, 193, 7, 0.2)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#f9fafb';
                  e.currentTarget.style.borderColor = '#e5e7eb';
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={{ fontWeight: '600', color: '#374151', marginBottom: '4px' }}>
                  {p.numero || 'Sem número'}
                </div>
                <div style={{ color: '#6b7280', fontSize: '14px' }}>
                  {p.autor && <span>Autor: {p.autor}</span>}
                  {p.autor && p.reu && <span> • </span>}
                  {p.reu && <span>Réu: {p.reu}</span>}
                  {(p.autor || p.reu) && p.status && <span> • </span>}
                  {p.status && <span>Status: {p.status}</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
