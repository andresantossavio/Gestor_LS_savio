import React, { useState, useEffect } from 'react';
import Header from '../components/Header';

const apiBase = '/api/contabilidade';

const SocioPage = () => {
    const [socios, setSocios] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [newSocio, setNewSocio] = useState({
        nome: '',
        funcao: '',
        capital_social: '',
        percentual: ''
    });

    const fetchSocios = async () => {
        setIsLoading(true);
        try {
            const response = await fetch(`${apiBase}/socios`);
            if (!response.ok) {
                throw new Error('Falha ao carregar sócios');
            }
            const data = await response.json();
            setSocios(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchSocios();
    }, []);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setNewSocio(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null); // Limpa erros anteriores
        try {
            const response = await fetch(`${apiBase}/socios`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...newSocio,
                    capital_social: parseFloat(newSocio.capital_social) || null,
                    percentual: parseFloat(newSocio.percentual) || null,
                }),
            });
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Falha ao criar sócio');
            }
            // Reset form and reload list
            setNewSocio({ nome: '', funcao: '', capital_social: '', percentual: '' });
            fetchSocios();
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div style={{ padding: 20 }}>
            <Header title="Gerenciar Sócios" />
            
            <div style={formContainerStyle}>
                <h3>Adicionar Novo Sócio</h3>
                <form onSubmit={handleSubmit}>
                    <input name="nome" value={newSocio.nome} onChange={handleInputChange} placeholder="Nome do Sócio" required style={inputStyle}/>
                    <input name="funcao" value={newSocio.funcao} onChange={handleInputChange} placeholder="Função (ex: Administrador)" style={inputStyle}/>
                    <input name="capital_social" type="number" value={newSocio.capital_social} onChange={handleInputChange} placeholder="Capital Social (R$)" style={inputStyle}/>
                    <input name="percentual" type="number" step="0.01" value={newSocio.percentual} onChange={handleInputChange} placeholder="Percentual na Sociedade (ex: 0.5 para 50%)" style={inputStyle}/>
                    <button type="submit" style={buttonStyle}>Adicionar Sócio</button>
                </form>
            </div>

            {error && <p style={{ color: 'red' }}><strong>Erro:</strong> {error}</p>}

            <h2>Sócios Atuais</h2>
            {isLoading ? (
                <p>Carregando sócios...</p>
            ) : (
                <ul style={listStyle}>
                    {socios.length === 0 && <p>Nenhum sócio cadastrado.</p>}
                    {socios.map(socio => (
                        <li key={socio.id} style={listItemStyle}>
                            <strong>{socio.nome}</strong> ({socio.funcao || 'N/A'}) - Capital: R$ {socio.capital_social?.toFixed(2) || '0.00'} - Percentual: {socio.percentual ? (socio.percentual * 100).toFixed(2) : '0'}%
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};


// Simple styles for demonstration
const formContainerStyle = {
    marginBottom: '30px',
    padding: '20px',
    border: '1px solid #ccc',
    borderRadius: '8px',
    backgroundColor: '#f9f9f9',
};

const inputStyle = {
    display: 'block',
    width: 'calc(100% - 20px)',
    padding: '10px',
    marginBottom: '10px',
    borderRadius: '4px',
    border: '1px solid #ccc',
};

const buttonStyle = {
    padding: '10px 20px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
};

const listStyle = {
    listStyleType: 'none',
    padding: 0,
};

const listItemStyle = {
    padding: '10px',
    borderBottom: '1px solid #eee',
};

export default SocioPage;
