import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';

const apiBase = '/api/contabilidade';

const EntradaForm = () => {
    const navigate = useNavigate();
    const [socios, setSocios] = useState([]);
    const [clientes, setClientes] = useState([]);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({
        cliente: '',
        cliente_id: null,
        data: new Date().toISOString().split('T')[0], // Default to today
        valor: '',
        socios: [] // Will hold { socio_id, percentual }
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
        
        // Carregar clientes para associá-los
        const fetchClientes = async () => {
            try {
                const response = await fetch('/api/clientes');
                if (!response.ok) throw new Error('Falha ao carregar clientes.');
                setClientes(await response.json());
            } catch (err) {
                setError(err.message);
            }
        };
        
        fetchSocios();
        fetchClientes();
    }, []);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleClienteChange = (e) => {
        const clienteId = e.target.value;
        if (clienteId) {
            const clienteSelecionado = clientes.find(c => c.id === parseInt(clienteId));
            setFormData(prev => ({
                ...prev,
                cliente_id: parseInt(clienteId),
                cliente: clienteSelecionado ? clienteSelecionado.nome : ''
            }));
        } else {
            setFormData(prev => ({ ...prev, cliente_id: null, cliente: '' }));
        }
    };

    const handleSocioPercentualChange = (socio_id, percentualStr) => {
        const percentualInt = parseFloat(percentualStr); // agora mantemos inteiro (ex: 50)
        const otherSocios = formData.socios.filter(s => s.socio_id !== socio_id);

        let newSocios;
        if (!isNaN(percentualInt) && percentualInt > 0) {
            newSocios = [...otherSocios, { socio_id, percentual: percentualInt }];
        } else {
            newSocios = otherSocios;
        }
        setFormData(prev => ({ ...prev, socios: newSocios }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        
        const totalPercentual = formData.socios.reduce((sum, s) => sum + s.percentual, 0);
        if (Math.abs(totalPercentual - 100) > 0.001) {
            setError(`A soma dos percentuais dos sócios deve ser 100%. Soma atual: ${totalPercentual.toFixed(0)}%`);
            return;
        }

        try {
            const response = await fetch(`${apiBase}/entradas`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...formData,
                    valor: parseFloat(formData.valor),
                    socios: formData.socios.map(s => ({ socio_id: s.socio_id, percentual: s.percentual }))
                }),
            });
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Falha ao criar entrada.');
            }
            navigate('/contabilidade'); // Redireciona para o dashboard após sucesso
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div style={{ padding: 20 }}>
            <Header title="Registrar Nova Entrada" />
            
            <form onSubmit={handleSubmit} style={formContainerStyle}>
                <div style={{ marginBottom: '10px' }}>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Cliente Cadastrado:</label>
                    <select 
                        value={formData.cliente_id || ''} 
                        onChange={handleClienteChange} 
                        style={inputStyle}
                    >
                        <option value="">Selecione um cliente (opcional)</option>
                        {clientes.map(cliente => (
                            <option key={cliente.id} value={cliente.id}>
                                {cliente.nome} {cliente.cpf_cnpj ? `(${cliente.cpf_cnpj})` : ''}
                            </option>
                        ))}
                    </select>
                </div>
                
                <div style={{ marginBottom: '10px' }}>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Nome do Cliente (texto livre):</label>
                    <input 
                        name="cliente" 
                        value={formData.cliente} 
                        onChange={handleInputChange} 
                        placeholder="Nome do Cliente" 
                        required 
                        style={inputStyle}
                        readOnly={!!formData.cliente_id}
                    />
                    <small style={{ color: '#666' }}>
                        {formData.cliente_id ? 'Preenchido automaticamente do cliente selecionado' : 'Ou digite um nome manualmente'}
                    </small>
                </div>
                
                <input name="valor" type="number" step="0.01" value={formData.valor} onChange={handleInputChange} placeholder="Valor da Entrada (R$)" required style={inputStyle}/>
                <input name="data" type="date" value={formData.data} onChange={handleInputChange} required style={inputStyle}/>
                
                <h4>Distribuição entre Sócios (a soma deve ser 100%)</h4>
                {socios.map(socio => (
                    <div key={socio.id} style={{ marginBottom: '10px' }}>
                        <label style={{ marginRight: '10px', width: '150px', display: 'inline-block' }}>{socio.nome}</label>
                        <input
                            type="number"
                            step="1"
                            min="0"
                            max="100"
                            placeholder="Percentual (%)"
                            onChange={(e) => handleSocioPercentualChange(socio.id, e.target.value)}
                            style={{ ...inputStyle, width: '100px', display: 'inline-block' }}
                        />
                    </div>
                ))}

                <button type="submit" style={buttonStyle}>Salvar Entrada</button>
            </form>

            {error && <p style={{ color: 'red' }}><strong>Erro:</strong> {error}</p>}
        </div>
    );
};

// Reusing styles from SocioPage for consistency
const formContainerStyle = { marginBottom: '30px', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', backgroundColor: '#f9f9f9' };
const inputStyle = { padding: '10px', marginBottom: '10px', borderRadius: '4px', border: '1px solid #ccc' };
const buttonStyle = { padding: '10px 20px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' };

export default EntradaForm;
