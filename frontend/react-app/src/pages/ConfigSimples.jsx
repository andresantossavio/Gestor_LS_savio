import React, { useState, useEffect } from 'react';
import Header from '../components/Header';

const ConfigSimples = () => {
    const [faixas, setFaixas] = useState([]);
    const [loading, setLoading] = useState(false);
    const [editando, setEditando] = useState(null);
    const [nova, setNova] = useState({
        limite_superior: '',
        aliquota: '',
        deducao: '',
        vigencia_inicio: '',
        vigencia_fim: '',
        ordem: ''
    });

    const carregarFaixas = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/contabilidade/simples-faixas');
            if (!res.ok) throw new Error('Falha ao carregar faixas');
            const data = await res.json();
            setFaixas(data);
        } catch (e) {
            console.error(e);
            alert('Erro ao carregar faixas');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        carregarFaixas();
    }, []);

    const salvarNova = async () => {
        if (!nova.limite_superior || !nova.aliquota || !nova.vigencia_inicio || !nova.ordem) {
            alert('Preencha todos os campos obrigatórios (limite, alíquota, vigência início, ordem)');
            return;
        }

        try {
            const payload = {
                limite_superior: parseFloat(nova.limite_superior),
                aliquota: parseFloat(nova.aliquota) / 100, // Converter % para decimal
                deducao: parseFloat(nova.deducao) || 0.0,
                vigencia_inicio: nova.vigencia_inicio,
                vigencia_fim: nova.vigencia_fim || null,
                ordem: parseInt(nova.ordem)
            };

            const res = await fetch('/api/contabilidade/simples-faixas', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error('Falha ao criar faixa');
            await res.json();
            
            setNova({
                limite_superior: '',
                aliquota: '',
                deducao: '',
                vigencia_inicio: '',
                vigencia_fim: '',
                ordem: ''
            });
            
            carregarFaixas();
        } catch (e) {
            console.error(e);
            alert('Erro ao criar faixa');
        }
    };

    const atualizarFaixa = async (faixa_id) => {
        try {
            const faixa = faixas.find(f => f.id === faixa_id);
            const payload = {
                limite_superior: parseFloat(faixa.limite_superior),
                aliquota: parseFloat(faixa.aliquota),
                deducao: parseFloat(faixa.deducao),
                vigencia_inicio: faixa.vigencia_inicio,
                vigencia_fim: faixa.vigencia_fim || null,
                ordem: parseInt(faixa.ordem)
            };

            const res = await fetch(`/api/contabilidade/simples-faixas/${faixa_id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error('Falha ao atualizar faixa');
            await res.json();
            
            setEditando(null);
            carregarFaixas();
        } catch (e) {
            console.error(e);
            alert('Erro ao atualizar faixa');
        }
    };

    const deletarFaixa = async (faixa_id) => {
        if (!window.confirm('Tem certeza que deseja deletar esta faixa?')) return;

        try {
            const res = await fetch(`/api/contabilidade/simples-faixas/${faixa_id}`, {
                method: 'DELETE'
            });

            if (!res.ok) throw new Error('Falha ao deletar faixa');
            carregarFaixas();
        } catch (e) {
            console.error(e);
            alert('Erro ao deletar faixa');
        }
    };

    const formatarMoeda = (valor) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
    };

    const formatarPercentual = (valor) => {
        return `${(valor * 100).toFixed(2)}%`;
    };

    const handleEditChange = (faixa_id, campo, valor) => {
        setFaixas(faixas.map(f => {
            if (f.id === faixa_id) {
                return { ...f, [campo]: valor };
            }
            return f;
        }));
    };

    return (
        <div style={{ padding: 20 }}>
            <Header title="Configuração - Faixas do Simples Nacional" />

            <div style={{ marginBottom: 30, padding: 20, backgroundColor: '#f9fafb', borderRadius: 8 }}>
                <h3 style={{ marginTop: 0 }}>Adicionar Nova Faixa</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 15 }}>
                    <div>
                        <label style={labelStyle}>Limite Superior (R$)</label>
                        <input 
                            type="number" 
                            value={nova.limite_superior}
                            onChange={(e) => setNova({...nova, limite_superior: e.target.value})}
                            style={inputStyle}
                            placeholder="180000.00"
                        />
                    </div>
                    <div>
                        <label style={labelStyle}>Alíquota (%)</label>
                        <input 
                            type="number" 
                            step="0.01"
                            value={nova.aliquota}
                            onChange={(e) => setNova({...nova, aliquota: e.target.value})}
                            style={inputStyle}
                            placeholder="4.5"
                        />
                    </div>
                    <div>
                        <label style={labelStyle}>Dedução (R$)</label>
                        <input 
                            type="number" 
                            value={nova.deducao}
                            onChange={(e) => setNova({...nova, deducao: e.target.value})}
                            style={inputStyle}
                            placeholder="0.00"
                        />
                    </div>
                    <div>
                        <label style={labelStyle}>Vigência Início</label>
                        <input 
                            type="date" 
                            value={nova.vigencia_inicio}
                            onChange={(e) => setNova({...nova, vigencia_inicio: e.target.value})}
                            style={inputStyle}
                        />
                    </div>
                    <div>
                        <label style={labelStyle}>Vigência Fim (opcional)</label>
                        <input 
                            type="date" 
                            value={nova.vigencia_fim}
                            onChange={(e) => setNova({...nova, vigencia_fim: e.target.value})}
                            style={inputStyle}
                        />
                    </div>
                    <div>
                        <label style={labelStyle}>Ordem</label>
                        <input 
                            type="number" 
                            value={nova.ordem}
                            onChange={(e) => setNova({...nova, ordem: e.target.value})}
                            style={inputStyle}
                            placeholder="1"
                        />
                    </div>
                </div>
                <button onClick={salvarNova} style={{ ...buttonStyle, marginTop: 15 }}>
                    Adicionar Faixa
                </button>
            </div>

            <div style={{ overflowX: 'auto' }}>
                <table style={tableStyle}>
                    <thead>
                        <tr>
                            <th style={thStyle}>Ordem</th>
                            <th style={thStyle}>Limite Superior</th>
                            <th style={thStyle}>Alíquota</th>
                            <th style={thStyle}>Dedução</th>
                            <th style={thStyle}>Vigência Início</th>
                            <th style={thStyle}>Vigência Fim</th>
                            <th style={thStyle}>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading && (
                            <tr>
                                <td colSpan="7" style={{ textAlign: 'center', padding: 20 }}>Carregando...</td>
                            </tr>
                        )}
                        {!loading && faixas.length === 0 && (
                            <tr>
                                <td colSpan="7" style={{ textAlign: 'center', padding: 20, color: '#6b7280' }}>
                                    Nenhuma faixa configurada. Adicione a primeira faixa acima.
                                </td>
                            </tr>
                        )}
                        {!loading && faixas.map((faixa) => (
                            <tr key={faixa.id}>
                                <td style={tdStyle}>
                                    {editando === faixa.id ? (
                                        <input 
                                            type="number" 
                                            value={faixa.ordem}
                                            onChange={(e) => handleEditChange(faixa.id, 'ordem', e.target.value)}
                                            style={{ ...inputStyle, width: '60px' }}
                                        />
                                    ) : faixa.ordem}
                                </td>
                                <td style={tdStyle}>
                                    {editando === faixa.id ? (
                                        <input 
                                            type="number" 
                                            value={faixa.limite_superior}
                                            onChange={(e) => handleEditChange(faixa.id, 'limite_superior', e.target.value)}
                                            style={{ ...inputStyle, width: '120px' }}
                                        />
                                    ) : formatarMoeda(faixa.limite_superior)}
                                </td>
                                <td style={tdStyle}>
                                    {editando === faixa.id ? (
                                        <input 
                                            type="number" 
                                            step="0.0001"
                                            value={(faixa.aliquota * 100).toFixed(2)}
                                            onChange={(e) => handleEditChange(faixa.id, 'aliquota', parseFloat(e.target.value) / 100)}
                                            style={{ ...inputStyle, width: '80px' }}
                                        />
                                    ) : formatarPercentual(faixa.aliquota)}
                                </td>
                                <td style={tdStyle}>
                                    {editando === faixa.id ? (
                                        <input 
                                            type="number" 
                                            value={faixa.deducao}
                                            onChange={(e) => handleEditChange(faixa.id, 'deducao', e.target.value)}
                                            style={{ ...inputStyle, width: '120px' }}
                                        />
                                    ) : formatarMoeda(faixa.deducao)}
                                </td>
                                <td style={tdStyle}>
                                    {editando === faixa.id ? (
                                        <input 
                                            type="date" 
                                            value={faixa.vigencia_inicio}
                                            onChange={(e) => handleEditChange(faixa.id, 'vigencia_inicio', e.target.value)}
                                            style={inputStyle}
                                        />
                                    ) : faixa.vigencia_inicio}
                                </td>
                                <td style={tdStyle}>
                                    {editando === faixa.id ? (
                                        <input 
                                            type="date" 
                                            value={faixa.vigencia_fim || ''}
                                            onChange={(e) => handleEditChange(faixa.id, 'vigencia_fim', e.target.value)}
                                            style={inputStyle}
                                        />
                                    ) : (faixa.vigencia_fim || 'Vigente')}
                                </td>
                                <td style={tdStyle}>
                                    {editando === faixa.id ? (
                                        <>
                                            <button 
                                                onClick={() => atualizarFaixa(faixa.id)}
                                                style={{ ...buttonStyle, fontSize: '12px', padding: '5px 10px', marginRight: 5 }}
                                            >
                                                Salvar
                                            </button>
                                            <button 
                                                onClick={() => { setEditando(null); carregarFaixas(); }}
                                                style={{ ...buttonStyle, fontSize: '12px', padding: '5px 10px', backgroundColor: '#6b7280' }}
                                            >
                                                Cancelar
                                            </button>
                                        </>
                                    ) : (
                                        <>
                                            <button 
                                                onClick={() => setEditando(faixa.id)}
                                                style={{ ...buttonStyle, fontSize: '12px', padding: '5px 10px', marginRight: 5 }}
                                            >
                                                Editar
                                            </button>
                                            <button 
                                                onClick={() => deletarFaixa(faixa.id)}
                                                style={{ ...buttonStyle, fontSize: '12px', padding: '5px 10px', backgroundColor: '#ef4444' }}
                                            >
                                                Deletar
                                            </button>
                                        </>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div style={{ marginTop: 20, padding: 15, backgroundColor: '#fef3c7', borderRadius: 8 }}>
                <h4 style={{ marginTop: 0 }}>⚠️ Importante</h4>
                <p style={{ fontSize: 14 }}>
                    As faixas do Simples Nacional são aplicadas com base na <strong>receita acumulada dos últimos 12 meses</strong>.
                    Se a legislação mudar, adicione novas faixas com vigência futura e encerre as antigas definindo a "Vigência Fim".
                </p>
                <p style={{ fontSize: 14 }}>
                    Meses já consolidados não serão alterados automaticamente. Use o botão "Recalcular" na Previsão da Operação para atualizar meses específicos após mudar faixas.
                </p>
            </div>
        </div>
    );
};

const buttonStyle = {
    padding: '10px 15px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '14px',
};

const labelStyle = {
    display: 'block',
    fontSize: '13px',
    fontWeight: 600,
    marginBottom: '5px',
    color: '#374151'
};

const inputStyle = {
    width: '100%',
    padding: '8px',
    borderRadius: '4px',
    border: '1px solid #d1d5db',
    fontSize: '14px'
};

const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '14px'
};

const thStyle = {
    backgroundColor: '#1f2937',
    color: 'white',
    padding: '12px 8px',
    textAlign: 'left',
    fontWeight: 600,
    borderBottom: '2px solid #374151'
};

const tdStyle = {
    padding: '10px 8px',
    borderBottom: '1px solid #e5e7eb'
};

export default ConfigSimples;
