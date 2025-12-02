import React, { useState, useEffect } from 'react';
import Header from '../components/Header';

const Lucros = () => {
    const [ano, setAno] = useState(new Date().getFullYear());
    const [dados, setDados] = useState(null);
    const [loading, setLoading] = useState(false);

    const carregarLucros = async () => {
        setLoading(true);
        try {
            const res = await fetch(`/api/contabilidade/lucros?year=${ano}&calcular_tempo_real=true`);
            if (!res.ok) throw new Error('Falha ao carregar distribuição de lucros');
            const data = await res.json();
            setDados(data);
        } catch (e) {
            console.error(e);
            alert('Erro ao carregar distribuição de lucros');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        carregarLucros();
    }, [ano]);

    const formatarMoeda = (valor) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
    };

    const formatarPercentual = (valor) => {
        return `${valor.toFixed(2)}%`;
    };

    if (!dados) {
        return (
            <div style={{ padding: 20 }}>
                <Header title="Distribuição de Lucros" />
                <p>{loading ? 'Carregando...' : 'Nenhum dado disponível'}</p>
            </div>
        );
    }

    return (
        <div style={{ padding: 20 }}>
            <Header title="Distribuição de Lucros" />
            
            <div style={{ marginBottom: 20 }}>
                <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 10 }}>
                    <label>Ano:</label>
                    <input 
                        type="number" 
                        value={ano} 
                        onChange={(e) => setAno(parseInt(e.target.value))}
                        min="2020"
                        max="2030"
                        style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc', width: '100px' }}
                    />
                    <button onClick={carregarLucros} style={buttonStyle}>
                        {loading ? 'Carregando...' : '🔄 Atualizar'}
                    </button>
                </div>
                <div style={{ padding: '10px', backgroundColor: '#e0f2fe', borderRadius: '4px', fontSize: '14px' }}>
                    ℹ️ <strong>Distribuição de Lucros:</strong> 5% Administrador | 10% Fundo | 85% distribuído entre sócios conforme participação nas entradas do mês.
                </div>
            </div>

            <div style={{ overflowX: 'auto' }}>
                <table style={tableStyle}>
                    <thead>
                        <tr>
                            <th style={thStyle}>Mês/Ano</th>
                            <th style={thStyle}>Admin 5%</th>
                            <th style={thStyle}>Fundo 10%</th>
                            {dados.socios_headers.map(socio => (
                                <th key={socio.id} style={thStyle}>{socio.nome}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {dados.meses.map((linha) => (
                            <tr key={linha.mes} style={{
                                backgroundColor: linha.consolidado ? '#f0fdf4' : '#fef9e7'
                            }}>
                                <td style={tdStyle}>
                                    {linha.mes}
                                    {!linha.consolidado && (
                                        <span style={{ marginLeft: '5px', fontSize: '11px', color: '#6b7280', fontStyle: 'italic' }}>
                                            (provisório)
                                        </span>
                                    )}
                                </td>
                                <td style={tdStyle}>{formatarMoeda(linha.admin_5p)}</td>
                                <td style={tdStyle}>{formatarMoeda(linha.fundo_10p)}</td>
                                {linha.socios.map(socio => (
                                    <td key={socio.socio_id} style={tdStyle}>
                                        <div>{formatarMoeda(socio.valor)}</div>
                                        <div style={{ fontSize: '11px', color: '#6b7280' }}>
                                            ({formatarPercentual(socio.percentual)})
                                        </div>
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div style={{ marginTop: 20, padding: 15, backgroundColor: '#f9fafb', borderRadius: 8 }}>
                <h3 style={{ marginTop: 0 }}>Legenda</h3>
                <p><span style={{ display: 'inline-block', width: 20, height: 20, backgroundColor: '#f0fdf4', border: '1px solid #ccc', marginRight: 8 }}></span>✅ Mês consolidado (valores baseados na DRE consolidada)</p>
                <p><span style={{ display: 'inline-block', width: 20, height: 20, backgroundColor: '#fef9e7', border: '1px solid #ccc', marginRight: 8 }}></span>Valores provisórios (calculados em tempo real)</p>
                <p style={{ fontSize: 14, color: '#6b7280', marginTop: 15 }}>
                    <strong>Como funciona:</strong>
                </p>
                <ul style={{ fontSize: 14, color: '#6b7280', marginTop: 5 }}>
                    <li><strong>Administrador (5%):</strong> 5% do lucro líquido reservado para o sócio administrador.</li>
                    <li><strong>Fundo (10%):</strong> 10% do lucro líquido destinado ao fundo de reserva.</li>
                    <li><strong>Distribuição aos Sócios (85%):</strong> Os 85% restantes são distribuídos proporcionalmente à participação de cada sócio nas entradas do mês.</li>
                    <li>Os percentuais entre parênteses mostram a participação de cada sócio nas receitas do mês.</li>
                    <li>Meses sem entradas terão distribuição zero para todos os sócios.</li>
                </ul>
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

const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '14px',
    minWidth: '1000px'
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

export default Lucros;
