import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const OperacoesContabeis = () => {
    const [operacoes, setOperacoes] = useState([]);
    const [historico, setHistorico] = useState([]);
    const [socios, setSocios] = useState([]);
    const [loading, setLoading] = useState(false);
    const [erro, setErro] = useState('');
    const [sucesso, setSucesso] = useState('');
    
    // Filtros
    const [mesReferencia, setMesReferencia] = useState('');
    
    // Formulário
    const [formData, setFormData] = useState({
        operacao_codigo: '',
        valor: '',
        data: new Date().toISOString().split('T')[0],
        descricao: '',
        socio_id: ''
    });
    
    // Operação expandida no histórico
    const [expandido, setExpandido] = useState(null);

    useEffect(() => {
        carregarOperacoes();
        carregarSocios();
        carregarHistorico();
        
        // Definir mês atual como padrão
        const hoje = new Date();
        const mesAtual = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}`;
        setMesReferencia(mesAtual);
    }, []);

    useEffect(() => {
        if (mesReferencia) {
            carregarHistorico();
        }
    }, [mesReferencia]);

    const carregarOperacoes = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/contabilidade/operacoes`);
            setOperacoes(response.data);
        } catch (error) {
            console.error('Erro ao carregar operações:', error);
            setErro('Erro ao carregar operações disponíveis');
        }
    };

    const carregarSocios = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/contabilidade/socios`);
            setSocios(response.data);
        } catch (error) {
            console.error('Erro ao carregar sócios:', error);
        }
    };

    const carregarHistorico = async () => {
        try {
            const params = {};
            if (mesReferencia) {
                params.mes_referencia = mesReferencia;
            }
            
            const response = await axios.get(`${API_BASE_URL}/contabilidade/operacoes/historico`, { params });
            setHistorico(response.data);
        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setErro('');
        setSucesso('');

        try {
            // Validações
            if (!formData.operacao_codigo) {
                throw new Error('Selecione uma operação');
            }
            if (!formData.valor || parseFloat(formData.valor) <= 0) {
                throw new Error('Informe um valor válido');
            }
            if (!formData.data) {
                throw new Error('Informe a data');
            }

            const payload = {
                operacao_codigo: formData.operacao_codigo,
                valor: parseFloat(formData.valor),
                data: formData.data,
                descricao: formData.descricao || null,
                socio_id: formData.socio_id ? parseInt(formData.socio_id) : null
            };

            await axios.post(`${API_BASE_URL}/contabilidade/operacoes/executar`, payload);
            
            setSucesso('Operação executada com sucesso!');
            
            // Limpar formulário
            setFormData({
                operacao_codigo: '',
                valor: '',
                data: new Date().toISOString().split('T')[0],
                descricao: '',
                socio_id: ''
            });
            
            // Recarregar histórico
            await carregarHistorico();
            
            // Limpar mensagem de sucesso após 3 segundos
            setTimeout(() => setSucesso(''), 3000);
        } catch (error) {
            console.error('Erro ao executar operação:', error);
            setErro(error.response?.data?.detail || error.message || 'Erro ao executar operação');
        } finally {
            setLoading(false);
        }
    };

    const handleCancelar = async (operacaoId) => {
        if (!window.confirm('Tem certeza que deseja cancelar esta operação? Os lançamentos contábeis serão removidos.')) {
            return;
        }

        try {
            await axios.delete(`${API_BASE_URL}/contabilidade/operacoes/${operacaoId}`);
            setSucesso('Operação cancelada com sucesso!');
            await carregarHistorico();
            setTimeout(() => setSucesso(''), 3000);
        } catch (error) {
            console.error('Erro ao cancelar operação:', error);
            setErro(error.response?.data?.detail || 'Erro ao cancelar operação');
        }
    };

    const toggleExpandir = (operacaoId) => {
        setExpandido(expandido === operacaoId ? null : operacaoId);
    };

    const operacaoSelecionada = operacoes.find(op => op.codigo === formData.operacao_codigo);
    const necessitaSocio = ['PRO_LABORE', 'DISTRIBUIR_LUCROS'].includes(formData.operacao_codigo);

    return (
        <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
            <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px', color: '#1f2937' }}>
                Operações Contábeis
            </h1>
            <p style={{ color: '#6b7280', marginBottom: '24px' }}>
                Execute operações contábeis padronizadas e visualize o histórico
            </p>

            {/* Mensagens */}
            {erro && (
                <div style={{
                    padding: '12px 16px',
                    backgroundColor: '#fee2e2',
                    border: '1px solid #fecaca',
                    borderRadius: '8px',
                    color: '#991b1b',
                    marginBottom: '16px'
                }}>
                    {erro}
                </div>
            )}

            {sucesso && (
                <div style={{
                    padding: '12px 16px',
                    backgroundColor: '#d1fae5',
                    border: '1px solid #a7f3d0',
                    borderRadius: '8px',
                    color: '#065f46',
                    marginBottom: '16px'
                }}>
                    {sucesso}
                </div>
            )}

            {/* Formulário */}
            <div style={{
                backgroundColor: 'white',
                borderRadius: '12px',
                padding: '24px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                marginBottom: '32px'
            }}>
                <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '20px', color: '#1f2937' }}>
                    Nova Operação
                </h2>

                <form onSubmit={handleSubmit}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                        {/* Operação */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500', color: '#374151' }}>
                                Operação *
                            </label>
                            <select
                                value={formData.operacao_codigo}
                                onChange={(e) => setFormData({ ...formData, operacao_codigo: e.target.value })}
                                style={{
                                    width: '100%',
                                    padding: '10px',
                                    border: '1px solid #d1d5db',
                                    borderRadius: '6px',
                                    fontSize: '14px'
                                }}
                                required
                            >
                                <option value="">Selecione uma operação</option>
                                {operacoes.map(op => (
                                    <option key={op.id} value={op.codigo}>
                                        {op.nome}
                                    </option>
                                ))}
                            </select>
                            {operacaoSelecionada && (
                                <div style={{
                                    background: '#f3f4f6',
                                    borderRadius: '8px',
                                    padding: '10px 14px',
                                    marginTop: '8px',
                                    marginBottom: '8px',
                                    fontSize: '13px',
                                    color: '#374151',
                                    borderLeft: '4px solid #FFC107',
                                    boxShadow: '0 1px 2px rgba(0,0,0,0.04)'
                                }}>
                                    <strong>O que esta operação faz?</strong><br />
                                    {operacaoSelecionada.descricao}
                                </div>
                            )}
                        </div>

                        {/* Valor */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500', color: '#374151' }}>
                                Valor (R$) *
                            </label>
                            <input
                                type="number"
                                step="0.01"
                                min="0.01"
                                value={formData.valor}
                                onChange={(e) => setFormData({ ...formData, valor: e.target.value })}
                                style={{
                                    width: '100%',
                                    padding: '10px',
                                    border: '1px solid #d1d5db',
                                    borderRadius: '6px',
                                    fontSize: '14px'
                                }}
                                required
                            />
                        </div>

                        {/* Data */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500', color: '#374151' }}>
                                Data *
                            </label>
                            <input
                                type="date"
                                value={formData.data}
                                onChange={(e) => setFormData({ ...formData, data: e.target.value })}
                                style={{
                                    width: '100%',
                                    padding: '10px',
                                    border: '1px solid #d1d5db',
                                    borderRadius: '6px',
                                    fontSize: '14px'
                                }}
                                required
                            />
                        </div>

                        {/* Sócio (condicional) */}
                        {necessitaSocio && (
                            <div>
                                <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500', color: '#374151' }}>
                                    Sócio
                                </label>
                                <select
                                    value={formData.socio_id}
                                    onChange={(e) => setFormData({ ...formData, socio_id: e.target.value })}
                                    style={{
                                        width: '100%',
                                        padding: '10px',
                                        border: '1px solid #d1d5db',
                                        borderRadius: '6px',
                                        fontSize: '14px'
                                    }}
                                >
                                    <option value="">Selecione um sócio (opcional)</option>
                                    {socios.map(socio => (
                                        <option key={socio.id} value={socio.id}>
                                            {socio.nome}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        )}
                    </div>

                    {/* Descrição */}
                    <div style={{ marginBottom: '20px' }}>
                        <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500', color: '#374151' }}>
                            Descrição
                        </label>
                        <textarea
                            value={formData.descricao}
                            onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                            rows="3"
                            style={{
                                width: '100%',
                                padding: '10px',
                                border: '1px solid #d1d5db',
                                borderRadius: '6px',
                                fontSize: '14px',
                                resize: 'vertical'
                            }}
                            placeholder="Descrição ou histórico da operação (opcional)"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        style={{
                            backgroundColor: '#FFC107',
                            color: '#000',
                            padding: '12px 24px',
                            borderRadius: '8px',
                            border: 'none',
                            fontSize: '16px',
                            fontWeight: '600',
                            cursor: loading ? 'not-allowed' : 'pointer',
                            opacity: loading ? 0.6 : 1
                        }}
                    >
                        {loading ? 'Executando...' : 'Executar Operação'}
                    </button>
                </form>
            </div>

            {/* Histórico */}
            <div style={{
                backgroundColor: 'white',
                borderRadius: '12px',
                padding: '24px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#1f2937' }}>
                        Histórico de Operações
                    </h2>
                    
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                        <label style={{ fontWeight: '500', color: '#374151' }}>Mês:</label>
                        <input
                            type="month"
                            value={mesReferencia}
                            onChange={(e) => setMesReferencia(e.target.value)}
                            style={{
                                padding: '8px 12px',
                                border: '1px solid #d1d5db',
                                borderRadius: '6px',
                                fontSize: '14px'
                            }}
                        />
                    </div>
                </div>

                {historico.length === 0 ? (
                    <p style={{ textAlign: 'center', color: '#6b7280', padding: '40px' }}>
                        Nenhuma operação encontrada para este período
                    </p>
                ) : (
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Data</th>
                                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Operação</th>
                                    <th style={{ padding: '12px', textAlign: 'right', fontWeight: '600', color: '#374151' }}>Valor</th>
                                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Descrição</th>
                                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Sócio</th>
                                    <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600', color: '#374151' }}>Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {historico.map((op) => (
                                    <React.Fragment key={op.id}>
                                        <tr 
                                            style={{ 
                                                borderBottom: '1px solid #f3f4f6',
                                                backgroundColor: op.cancelado ? '#fee2e2' : 'transparent',
                                                opacity: op.cancelado ? 0.6 : 1
                                            }}
                                        >
                                            <td style={{ padding: '12px' }}>
                                                {new Date(op.data).toLocaleDateString('pt-BR')}
                                            </td>
                                            <td style={{ padding: '12px' }}>
                                                <div style={{ fontWeight: '500' }}>{op.operacao_nome}</div>
                                                {op.cancelado && (
                                                    <span style={{ fontSize: '12px', color: '#dc2626' }}>
                                                        (Cancelada)
                                                    </span>
                                                )}
                                            </td>
                                            <td style={{ padding: '12px', textAlign: 'right', fontWeight: '500' }}>
                                                R$ {op.valor.toFixed(2)}
                                            </td>
                                            <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280' }}>
                                                {op.descricao || '-'}
                                            </td>
                                            <td style={{ padding: '12px', fontSize: '14px' }}>
                                                {op.socio_nome || '-'}
                                            </td>
                                            <td style={{ padding: '12px', textAlign: 'center' }}>
                                                <button
                                                    onClick={() => toggleExpandir(op.id)}
                                                    style={{
                                                        padding: '6px 12px',
                                                        backgroundColor: '#f3f4f6',
                                                        border: '1px solid #d1d5db',
                                                        borderRadius: '6px',
                                                        fontSize: '13px',
                                                        cursor: 'pointer',
                                                        marginRight: '8px'
                                                    }}
                                                >
                                                    {expandido === op.id ? '▼' : '▶'} Lançamentos
                                                </button>
                                                {!op.cancelado && (
                                                    <button
                                                        onClick={() => handleCancelar(op.id)}
                                                        style={{
                                                            padding: '6px 12px',
                                                            backgroundColor: '#fee2e2',
                                                            border: '1px solid #fecaca',
                                                            borderRadius: '6px',
                                                            fontSize: '13px',
                                                            color: '#991b1b',
                                                            cursor: 'pointer'
                                                        }}
                                                    >
                                                        Cancelar
                                                    </button>
                                                )}
                                            </td>
                                        </tr>
                                        {expandido === op.id && (
                                            <tr>
                                                <td colSpan="6" style={{ padding: '16px', backgroundColor: '#f9fafb' }}>
                                                    <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', color: '#374151' }}>
                                                        Lançamentos Contábeis:
                                                    </h4>
                                                    <table style={{ width: '100%', fontSize: '13px' }}>
                                                        <thead>
                                                            <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                                                                <th style={{ padding: '8px', textAlign: 'left', color: '#6b7280' }}>Conta Débito</th>
                                                                <th style={{ padding: '8px', textAlign: 'left', color: '#6b7280' }}>Conta Crédito</th>
                                                                <th style={{ padding: '8px', textAlign: 'right', color: '#6b7280' }}>Valor</th>
                                                                <th style={{ padding: '8px', textAlign: 'left', color: '#6b7280' }}>Histórico</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            {op.lancamentos.map((lanc) => (
                                                                <tr key={lanc.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                                                                    <td style={{ padding: '8px' }}>
                                                                        <div>{lanc.conta_debito_codigo} - {lanc.conta_debito_descricao}</div>
                                                                    </td>
                                                                    <td style={{ padding: '8px' }}>
                                                                        <div>{lanc.conta_credito_codigo} - {lanc.conta_credito_descricao}</div>
                                                                    </td>
                                                                    <td style={{ padding: '8px', textAlign: 'right', fontWeight: '500' }}>
                                                                        R$ {lanc.valor.toFixed(2)}
                                                                    </td>
                                                                    <td style={{ padding: '8px', color: '#6b7280' }}>
                                                                        {lanc.historico}
                                                                    </td>
                                                                </tr>
                                                            ))}
                                                        </tbody>
                                                    </table>
                                                </td>
                                            </tr>
                                        )}
                                    </React.Fragment>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default OperacoesContabeis;
