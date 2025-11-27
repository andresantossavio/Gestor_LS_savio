import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import Header from '../components/Header';

// --- Dados de Exemplo (Mocks) ---
// No futuro, esses dados virão da sua API.

const balancoPatrimonialData = {
    ativo: 15000,
    passivo: 5000,
    patrimonioLiquido: 10000,
};

const dreData = [
    { name: 'Receita Bruta', valor: 20000 },
    { name: 'Despesas', valor: -5000 },
    { name: 'Lucro Bruto', valor: 15000 },
    { name: 'Impostos', valor: -2000 },
    { name: 'Lucro Líquido', valor: 13000 },
];

const lucrosData = {
    disponiveis: 13000,
    distribuidos: 10000,
    fundoReserva: 2000,
    proLabore: 1000,
};

const distribuicaoSociosData = [
    { name: 'Sócio André', value: 6000 },
    { name: 'Sócio Bruna', value: 4000 },
];

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
    // Hooks para carregar dados da API (exemplo)
    // const [balanco, setBalanco] = useState(null);
    // useEffect(() => {
    //   fetch('/api/contabilidade/balanco').then(res => res.json()).then(setBalanco);
    // }, []);

    return (
        <div style={{ padding: 20 }}>
            <Header title="Painel de Contabilidade" />

            <div style={{ marginBottom: '20px', display: 'flex', gap: '10px' }}>
                <Link to="/contabilidade/entradas/nova" style={buttonStyle}>+ Nova Entrada</Link>
                <Link to="/contabilidade/despesas/nova" style={buttonStyle}>+ Nova Despesa</Link>
                <Link to="/contabilidade/socios" style={buttonStyle}>Gerenciar Sócios</Link>
            </div>

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
                </Widget>

                <Widget title="Demonstração de Resultado (DRE)">
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
};


export default Dashboard;