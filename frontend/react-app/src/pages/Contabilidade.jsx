import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import Header from '../components/Header';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

// --- Componentes de Widget ---

const Widget = ({ title, children }) => (
    <div style={{
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '20px',
        backgroundColor: '#f9f9f9',
        flex: 1,
        minWidth: '300px'
    }}>
        <h3 style={{ marginTop: 0, borderBottom: '2px solid #eee', paddingBottom: '10px' }}>{title}</h3>
        {children}
    </div>
);

const Dashboard = () => {
    const [canRenderCharts, setCanRenderCharts] = useState(true);
    const [loading, setLoading] = useState(true);
    const [balancoPatrimonialData, setBalancoPatrimonialData] = useState({ ativo: 0, passivo: 0, patrimonioLiquido: 0 });
    const [dreData, setDreData] = useState([]);
    const [lucrosData, setLucrosData] = useState({ disponiveis: 0, distribuidos: 0, fundoReserva: 0, proLabore: 0 });
    const [distribuicaoSociosData, setDistribuicaoSociosData] = useState([]);
    const [ano, setAno] = useState(new Date().getFullYear());

    useEffect(() => { 
        // Simple guard: disable charts if container width might be 0
        try {
            const el = document.querySelector('main');
            if (el && el.clientWidth < 300) {
                setCanRenderCharts(false);
            } else {
                setCanRenderCharts(true);
            }
        } catch (e) {
            setCanRenderCharts(false);
        }
    }, []);

    useEffect(() => {
        carregarDashboard();
    }, []);

    const carregarDashboard = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/contabilidade/dashboard-summary');
            if (response.ok) {
                const data = await response.json();
                setBalancoPatrimonialData(data.balancoPatrimonial);
                setDreData(data.dreData);
                setLucrosData(data.lucros);
                setDistribuicaoSociosData(data.distribuicaoSocios);
                setAno(data.ano);
            } else {
                console.error('Erro ao carregar dashboard:', response.statusText);
            }
        } catch (error) {
            console.error('Erro ao carregar dashboard:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div style={{ padding: 20 }}>
                <p>Carregando dados...</p>
            </div>
        );
    }

    return (
        <div style={{ padding: 20 }}>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
                <Widget title="Balanço Patrimonial">
                    <p><strong>Ativo:</strong> R$ {balancoPatrimonialData.ativo.toFixed(2)}</p>
                    <p><strong>Passivo:</strong> R$ {balancoPatrimonialData.passivo.toFixed(2)}</p>
                    <p><strong>Patrimônio Líquido:</strong> R$ {balancoPatrimonialData.patrimonioLiquido.toFixed(2)}</p>
                </Widget>

                <Widget title="Lucros e Fundos">
                    <p><strong>Lucro Disponível:</strong> R$ {lucrosData.disponiveis.toFixed(2)}</p>
                    <p><strong>Lucro Distribuído:</strong> R$ {lucrosData.distribuidos.toFixed(2)}</p>
                    <p><strong>Fundo de Reserva:</strong> R$ {lucrosData.fundoReserva.toFixed(2)}</p>
                    <p><strong>Pró-Labore:</strong> R$ {lucrosData.proLabore.toFixed(2)}</p>
                </Widget>

                <Widget title="Distribuição de Lucros">
                    {canRenderCharts ? (
                        <ResponsiveContainer width="100%" height={200}>
                            <PieChart>
                                <Pie
                                    data={distribuicaoSociosData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    dataKey="value"
                                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                >
                                    {distribuicaoSociosData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip formatter={(value) => `R$ ${value.toFixed(2)}`} />
                            </PieChart>
                        </ResponsiveContainer>
                    ) : (
                        <div style={{ color:'#6b7280', fontSize:13 }}>Gráficos desativados (layout estreito). Conteúdo funcional acima.</div>
                    )}
                </Widget>

                <Widget title="Demonstração de Resultado (DRE)">
                    {canRenderCharts ? (
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={dreData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip formatter={(value) => `R$ ${value.toFixed(2)}`} />
                                <Legend />
                                <Bar dataKey="valor" fill="#82ca9d" />
                            </BarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div style={{ color:'#6b7280', fontSize:13 }}>Gráficos desativados (layout estreito).</div>
                    )}
                </Widget>
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
    textDecoration: 'none',
    cursor: 'pointer',
    fontSize: '14px',
    display: 'inline-block',
    marginRight: '10px'
};

const Contabilidade = () => {
    const anoAtual = new Date().getFullYear();
    
    return (
        <div>
            <Header title={`Painel de Contabilidade - ${anoAtual}`} />
            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' }}>
                <Link to="/contabilidade/entradas/nova" style={buttonStyle}>+ Nova Entrada</Link>
                <Link to="/contabilidade/despesas/nova" style={buttonStyle}>+ Nova Despesa</Link>
                <Link to="/contabilidade/lancamentos" style={buttonStyle}>📋 Gerenciar Lançamentos</Link>
                <Link to="/contabilidade/socios" style={buttonStyle}>Gerenciar Sócios</Link>
                <Link to="/contabilidade/dre" style={buttonStyle}>📊 DRE Mensal</Link>
                <Link to="/contabilidade/pro-labore" style={buttonStyle}>💰 Pró-labore</Link>
                <Link to="/contabilidade/config-simples" style={buttonStyle}>⚙️ Config Simples</Link>
            </div>
            <Dashboard />
        </div>
    );
};

export default Contabilidade;