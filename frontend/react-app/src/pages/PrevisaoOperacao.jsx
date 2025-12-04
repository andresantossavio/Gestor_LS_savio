import React, { useState, useEffect } from 'react';
import Header from '../components/Header';

const PrevisaoOperacao = () => {
    const [ano, setAno] = useState(new Date().getFullYear());
    const [dados, setDados] = useState([]);
    const [loading, setLoading] = useState(false);

    const carregarPrevisao = async () => {
        setLoading(true);
        try {
            // Sempre carregar com cálculo em tempo real
            const res = await fetch(`/api/contabilidade/previsao-operacao?year=${ano}&calcular_tempo_real=true`);
            if (!res.ok) throw new Error('Falha ao carregar Previsão da Operação');
            const data = await res.json();
            setDados(data);
        } catch (e) {
            console.error(e);
            alert('Erro ao carregar Previsão da Operação');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        carregarPrevisao();
    }, [ano]);

    const consolidarMes = async (mes) => {
        try {
            const res = await fetch(`/api/contabilidade/previsao-operacao/consolidar?mes=${mes}&forcar=false`, {
                method: 'POST'
            });
            if (!res.ok) throw new Error('Falha ao consolidar');
            await res.json();
            carregarPrevisao();
        } catch (e) {
            console.error(e);
            alert('Erro ao consolidar mês');
        }
    };

    const recalcularMes = async (mes) => {
        if (!window.confirm(`Recalcular e sobrescrever a consolidação de ${mes}?`)) return;
        try {
            const res = await fetch(`/api/contabilidade/previsao-operacao/consolidar?mes=${mes}&forcar=true`, {
                method: 'POST'
            });
            if (!res.ok) throw new Error('Falha ao recalcular');
            await res.json();
            carregarPrevisao();
        } catch (e) {
            console.error(e);
            alert('Erro ao recalcular mês');
        }
    };

    const desconsolidarMes = async (mes) => {
        if (!window.confirm(`Desconsolidar o mês ${mes}? Isso permitirá recalcular posteriormente.`)) {
            return;
        }
        try {
            const res = await fetch(`/api/contabilidade/previsao-operacao/consolidar?mes=${mes}`, {
                method: 'DELETE'
            });
            if (!res.ok) {
                throw new Error('Falha ao desconsolidar');
            }
            const data = await res.json();
            alert(`Mês ${mes} desconsolidado com sucesso!`);
            carregarPrevisao();
        } catch (e) {
            console.error(e);
            alert('Erro ao desconsolidar mês');
        }
    };

    const formatarMoeda = (valor) => {
        if (valor === null || valor === undefined || isNaN(valor)) {
            return 'R$ 0,00';
        }
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
    };

    const formatarPercentual = (valor) => {
        if (valor === null || valor === undefined || isNaN(valor)) {
            return '0.00%';
        }
        return `${(valor * 100).toFixed(2)}%`;
    };

    return (
        <div style={{ padding: 20 }}>
            <Header title="Previsão da Operação" />
            
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
                    <button onClick={carregarPrevisao} style={buttonStyle}>
                        {loading ? 'Carregando...' : '🔄 Recalcular Valores'}
                    </button>
                </div>
                <div style={{ padding: '10px', backgroundColor: '#e0f2fe', borderRadius: '4px', fontSize: '14px' }}>
                    ℹ️ <strong>Os valores são calculados em tempo real</strong> com base nas entradas e despesas cadastradas. 
                    Clique em "Consolidar" para salvar os valores definitivos do mês.
                </div>
            </div>

            <div style={{ overflowX: 'auto' }}>
                <table style={tableStyle}>
                    <thead>
                        <tr>
                            <th style={thStyle}>Mês</th>
                            <th style={thStyle}>Receita Bruta</th>
                            <th style={thStyle}>Receita 12m</th>
                            <th style={thStyle}>Alíquota</th>
                            <th style={thStyle}>Alíq. Efetiva</th>
                            <th style={thStyle}>Dedução</th>
                            <th style={thStyle}>Imposto Mês</th>
                            <th style={thStyle}>Pró-labore Bruto</th>
                            <th style={thStyle}>INSS Pessoal (11%)</th>
                            <th style={thStyle}>Pró-labore Líquido</th>
                            <th style={thStyle}>INSS Patronal (20%)</th>
                            <th style={thStyle}>Despesas Gerais</th>
                            <th style={thStyle}>Lucro Líquido</th>
                            <th style={thStyle}>Reserva Legal (10%)</th>
                            <th style={thStyle}>Lucro Distribuível</th>
                            <th style={thStyle}>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        {dados.map((linha) => (
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
                                <td style={tdStyle}>{formatarMoeda(linha.receita_bruta)}</td>
                                <td style={tdStyle}>{formatarMoeda(linha.receita_12m)}</td>
                                <td style={tdStyle}>{formatarPercentual(linha.aliquota)}</td>
                                <td style={tdStyle}>{formatarPercentual(linha.aliquota_efetiva)}</td>
                                <td style={tdStyle}>{formatarMoeda(linha.deducao)}</td>
                                <td style={tdStyle}>{formatarMoeda(linha.imposto)}</td>
                                <td style={tdStyle}>{formatarMoeda(linha.pro_labore_bruto || 0)}</td>
                                <td style={tdStyle}>{formatarMoeda(linha.inss_pessoal || 0)}</td>
                                <td style={tdStyle}>{formatarMoeda(linha.pro_labore_liquido || 0)}</td>
                                <td style={tdStyle}>{formatarMoeda(linha.inss_patronal || 0)}</td>
                                <td style={tdStyle}>{formatarMoeda(linha.despesas_gerais)}</td>
                                <td style={tdStyle}>{formatarMoeda(linha.lucro_liquido)}</td>
                                <td style={tdStyle}>{formatarMoeda(linha.reserva_legal || 0)}</td>
                                <td style={tdStyle}>{formatarMoeda(linha.lucro_distribuivel || 0)}</td>
                                <td style={tdStyle}>
                                    {!linha.consolidado && (
                                        <button 
                                            onClick={() => consolidarMes(linha.mes)}
                                            style={{ ...buttonStyle, fontSize: '12px', padding: '5px 10px' }}
                                        >
                                            Consolidar
                                        </button>
                                    )}
                                    {linha.consolidado && (
                                        <>
                                            <button 
                                                onClick={() => recalcularMes(linha.mes)}
                                                style={{ ...buttonStyle, fontSize: '12px', padding: '5px 10px', backgroundColor: '#f59e0b', marginRight: '5px' }}
                                            >
                                                Recalcular
                                            </button>
                                            <button 
                                                onClick={() => desconsolidarMes(linha.mes)}
                                                style={{ ...buttonStyle, fontSize: '12px', padding: '5px 10px', backgroundColor: '#ef4444' }}
                                            >
                                                Desconsolidar
                                            </button>
                                        </>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div style={{ marginTop: 20, padding: 15, backgroundColor: '#f9fafb', borderRadius: 8 }}>
                <h3 style={{ marginTop: 0 }}>Legenda</h3>
                <p><span style={{ display: 'inline-block', width: 20, height: 20, backgroundColor: '#f0fdf4', border: '1px solid #ccc', marginRight: 8 }}></span>✅ Mês consolidado (valores salvos no banco)</p>
                <p><span style={{ display: 'inline-block', width: 20, height: 20, backgroundColor: '#fef9e7', border: '1px solid #ccc', marginRight: 8 }}></span>Valores provisórios (não consolidados)</p>
                <p style={{ fontSize: 14, color: '#6b7280', marginTop: 15 }}>
                    <strong>Como funciona:</strong>
                </p>
                <ul style={{ fontSize: 14, color: '#6b7280', marginTop: 5 }}>
                    <li>Toda vez que você adiciona uma <strong>entrada</strong> ou <strong>despesa</strong>, os valores da Previsão da Operação são recalculados automaticamente.</li>
                    <li>Os meses com valores <strong>provisórios</strong> são atualizados sempre que você clica em "🔄 Recalcular Valores".</li>
                    <li>Clique em <strong>"Consolidar"</strong> para salvar os valores definitivos do mês no banco de dados.</li>
                    <li>Meses consolidados podem ser <strong>recalculados</strong> se houver necessidade de correção.</li>
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
    minWidth: '1200px'
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

export default PrevisaoOperacao;
