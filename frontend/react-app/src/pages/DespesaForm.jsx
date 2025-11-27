import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';

const apiBase = '/api/contabilidade';

const DespesaForm = () => {
    const navigate = useNavigate();
    const [socios, setSocios] = useState([]);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({
        data: new Date().toISOString().split('T')[0],
        especie: '',
        tipo: '',
        descricao: '',
        valor: '',
        responsaveis: [] // Will hold { socio_id }
    });

    useEffect(() => {
        // Carregar sócios para poder associá-los
        const fetchSocios = async () => {
            try {
                const response = await fetch(`${apiBase}/socios`);
                if (!response.ok) throw new Error('Falha ao carregar sócios.');
                setSocios(await response.json());
            } catch (err) {
                setError(err.message);
            }
        };
        fetchSocios();
    }, []);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSocioCheckboxChange = (socio_id, isChecked) => {
        let newResponsaveis;
        if (isChecked) {
            newResponsaveis = [...formData.responsaveis, { socio_id }];
        } else {
            newResponsaveis = formData.responsaveis.filter(r => r.socio_id !== socio_id);
        }
        setFormData(prev => ({ ...prev, responsaveis: newResponsaveis }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        if (formData.responsaveis.length === 0) {
            setError('Selecione pelo menos um sócio responsável.');
            return;
        }

        try {
            const response = await fetch(`${apiBase}/despesas`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...formData,
                    valor: parseFloat(formData.valor)
                }),
            });
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Falha ao criar despesa.');
            }
            navigate('/contabilidade'); // Redireciona para o dashboard
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div style={{ padding: 20 }}>
            <Header title="Registrar Nova Despesa" />
            
            <form onSubmit={handleSubmit} style={formContainerStyle}>
                <input name="especie" value={formData.especie} onChange={handleInputChange} placeholder="Espécie (ex: Estrutura, Individual)" required style={inputStyle}/>
                <input name="tipo" value={formData.tipo} onChange={handleInputChange} placeholder="Tipo (ex: Internet, Salário)" required style={inputStyle}/>
                <input name="descricao" value={formData.descricao} onChange={handleInputChange} placeholder="Descrição detalhada" style={inputStyle}/>
                <input name="valor" type="number" step="0.01" value={formData.valor} onChange={handleInputChange} placeholder="Valor da Despesa (R$)" required style={inputStyle}/>
                <input name="data" type="date" value={formData.data} onChange={handleInputChange} required style={inputStyle}/>
                
                <h4>Sócios Responsáveis (divisão igualitária)</h4>
                {socios.map(socio => (
                    <div key={socio.id} style={{ marginBottom: '10px' }}>
                        <label>
                            <input
                                type="checkbox"
                                onChange={(e) => handleSocioCheckboxChange(socio.id, e.target.checked)}
                                style={{ marginRight: '10px' }}
                            />
                            {socio.nome}
                        </label>
                    </div>
                ))}

                <button type="submit" style={buttonStyle}>Salvar Despesa</button>
            </form>

            {error && <p style={{ color: 'red' }}><strong>Erro:</strong> {error}</p>}
        </div>
    );
};

// Reusing styles for consistency
const formContainerStyle = { marginBottom: '30px', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', backgroundColor: '#f9f9f9' };
const inputStyle = { display: 'block', width: 'calc(100% - 22px)', padding: '10px', marginBottom: '10px', borderRadius: '4px', border: '1px solid #ccc' };
const buttonStyle = { padding: '10px 20px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' };

export default DespesaForm;
