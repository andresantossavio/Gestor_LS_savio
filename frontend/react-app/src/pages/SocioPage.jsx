import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import AportesSection from '../components/AportesSection';

const apiBase = '/api/contabilidade';

const SocioPage = () => {
    const [socios, setSocios] = useState([]);
    const [usuarios, setUsuarios] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [editingId, setEditingId] = useState(null);
    const [selectedSocioForAportes, setSelectedSocioForAportes] = useState(null);
    const [newSocio, setNewSocio] = useState({
        nome: '',
        usuario_id: null,
        funcao: '',
        capital_social: '',
        percentual: ''
    });
    const hojeISO = new Date().toISOString().slice(0, 10);
    const [aporteInicial, setAporteInicial] = useState({ valor: '', data: hojeISO, forma: 'dinheiro' });
    const [aporteEdicao, setAporteEdicao] = useState({ valor: '', data: hojeISO, forma: 'dinheiro' });

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

    const fetchUsuarios = async () => {
        try {
            const response = await fetch('/api/usuarios');
            if (!response.ok) {
                throw new Error('Falha ao carregar usuários');
            }
            const data = await response.json();
            setUsuarios(data);
        } catch (err) {
            setError(err.message);
        }
    };

    useEffect(() => {
        fetchSocios();
        fetchUsuarios();
    }, []);

    // Atualiza o formulário de edição quando o sócio é modificado (ex: após editar aporte)
    useEffect(() => {
        if (editingId) {
            const socioAtualizado = socios.find(s => s.id === editingId);
            if (socioAtualizado) {
                setNewSocio({
                    nome: socioAtualizado.nome || '',
                    usuario_id: socioAtualizado.usuario_id || null,
                    funcao: socioAtualizado.funcao || '',
                    capital_social: socioAtualizado.capital_social || '',
                    percentual: (socioAtualizado.percentual || 0) * 100
                });
            }
        }
    }, [socios, editingId]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setNewSocio(prev => ({ ...prev, [name]: value }));
    };

    const handleUsuarioChange = (e) => {
        const usuarioId = e.target.value;
        if (usuarioId) {
            const usuarioSelecionado = usuarios.find(u => u.id === parseInt(usuarioId));
            setNewSocio(prev => ({
                ...prev,
                usuario_id: parseInt(usuarioId),
                nome: usuarioSelecionado ? usuarioSelecionado.nome : prev.nome
            }));
        } else {
            setNewSocio(prev => ({ ...prev, usuario_id: null }));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        try {
            const percentualValue = parseFloat(newSocio.percentual);
            // Convert percentage to decimal if needed (if user enters 50, convert to 0.5)
            const percentualDecimal = percentualValue > 1 ? percentualValue / 100 : percentualValue;
            
            const url = editingId ? `${apiBase}/socios/${editingId}` : `${apiBase}/socios`;
            const method = editingId ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...newSocio,
                    usuario_id: newSocio.usuario_id || null,
                    // No create: capital_social será 0; aporte lançado em seguida
                    capital_social: editingId ? (parseFloat(newSocio.capital_social) || null) : 0,
                    percentual: percentualDecimal || null,
                }),
            });
            if (!response.ok) {
                let message = `Falha ao ${editingId ? 'atualizar' : 'criar'} sócio`;
                try { const errData = await response.json(); message = errData.detail || message; } catch { message = await response.text(); }
                throw new Error(message);
            }
            const socioCriadoOuEditado = await response.json();

            // Se criação com aporte inicial informado, registrar aporte e atualizar capital
            if (!editingId) {
                const valorAporte = parseFloat(aporteInicial.valor);
                if (valorAporte && aporteInicial.data) {
                    const respAporte = await fetch(`${apiBase}/socios/${socioCriadoOuEditado.id}/aportes`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            valor: valorAporte,
                            data: aporteInicial.data,
                            forma: aporteInicial.forma || 'dinheiro'
                        })
                    });
                    if (!respAporte.ok) {
                        let message2 = 'Falha ao registrar aporte inicial';
                        try { const errData2 = await respAporte.json(); message2 = errData2.detail || message2; } catch { message2 = await respAporte.text(); }
                        throw new Error(message2);
                    }
                }
            }

            // Reset form e recarregar lista
            setNewSocio({ nome: '', usuario_id: null, funcao: '', capital_social: '', percentual: '' });
            setAporteInicial({ valor: '', data: '', forma: 'dinheiro' });
            setEditingId(null);
            fetchSocios();
        } catch (err) {
            setError(err.message);
        }
    };

    const handleEdit = (socio) => {
        setNewSocio({
            nome: socio.nome,
            usuario_id: socio.usuario_id || null,
            funcao: socio.funcao || '',
            capital_social: socio.capital_social || '',
            percentual: socio.percentual ? (socio.percentual * 100).toString() : ''
        });
        setEditingId(socio.id);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleRegistrarAporte = async () => {
        if (!editingId) return;
        try {
            const valor = parseFloat(aporteEdicao.valor);
            if (!valor || !aporteEdicao.data) {
                setError('Informe valor e data do aporte.');
                return;
            }
            const resp = await fetch(`${apiBase}/socios/${editingId}/aportes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    valor,
                    data: aporteEdicao.data,
                    forma: aporteEdicao.forma || 'dinheiro',
                })
            });
            if (!resp.ok) {
                let message = 'Falha ao registrar aporte';
                try { const errData = await resp.json(); message = errData.detail || message; } catch { message = await resp.text(); }
                throw new Error(message);
            }
            setAporteEdicao({ valor: '', data: '', forma: 'dinheiro' });
            fetchSocios();
        } catch (err) {
            setError(err.message);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm('Tem certeza que deseja excluir este sócio?')) return;
        
        try {
            const response = await fetch(`${apiBase}/socios/${id}`, {
                method: 'DELETE',
            });
            if (!response.ok) {
                throw new Error('Falha ao excluir sócio');
            }
            fetchSocios();
        } catch (err) {
            setError(err.message);
        }
    };

    const handleCancelEdit = () => {
        setNewSocio({ nome: '', usuario_id: null, funcao: '', capital_social: '', percentual: '' });
        setEditingId(null);
    };

    return (
        <div style={{ padding: 20 }}>
            <Header title="Gerenciar Sócios" />
            {/* Resumo do capital social total */}
            <CapitalResumo socios={socios} />
            
            <div style={formContainerStyle}>
                <h3>{editingId ? 'Editar Sócio' : 'Adicionar Novo Sócio'}</h3>
                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '10px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Vincular a um Usuário (opcional):</label>
                        <select 
                            value={newSocio.usuario_id || ''} 
                            onChange={handleUsuarioChange} 
                            style={inputStyle}
                        >
                            <option value="">Selecione um usuário (opcional)</option>
                            {usuarios.map(usuario => (
                                <option key={usuario.id} value={usuario.id}>
                                    {usuario.nome} ({usuario.login})
                                </option>
                            ))}
                        </select>
                    </div>
                    
                    <input 
                        name="nome" 
                        value={newSocio.nome} 
                        onChange={handleInputChange} 
                        placeholder="Nome do Sócio" 
                        required 
                        style={inputStyle}
                        readOnly={!!newSocio.usuario_id}
                    />
                    {newSocio.usuario_id && (
                        <small style={{ display: 'block', marginBottom: '10px', color: '#666' }}>
                            Nome preenchido automaticamente do usuário selecionado
                        </small>
                    )}
                    
                    <div style={{ marginBottom: '10px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Função:</label>
                        <select 
                            name="funcao" 
                            value={newSocio.funcao} 
                            onChange={handleInputChange} 
                            required
                            style={inputStyle}
                        >
                            <option value="">Selecione a função</option>
                            <option value="Administrador">Administrador</option>
                            <option value="Capitalista">Capitalista</option>
                            <option value="Serviço">Serviço</option>
                        </select>
                        <small style={{ display: 'block', marginTop: '5px', color: '#666' }}>
                            Administrador: recebe 5% de remuneração de Sócio-Administrador
                        </small>
                    </div>
                    
                    {/* Para criação: valor do capital inicial entra como Aporte (valor + data + forma). */}
                    {!editingId ? (
                        <>
                            <input
                                name="capital_inicial"
                                type="number"
                                value={aporteInicial.valor}
                                onChange={(e) => setAporteInicial(prev => ({ ...prev, valor: e.target.value }))}
                                placeholder="Capital Inicial (R$)"
                                style={inputStyle}
                            />
                            <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                                <input type="date" value={aporteInicial.data} onChange={(e) => setAporteInicial(prev => ({ ...prev, data: e.target.value || hojeISO }))} placeholder="Data do aporte" style={inputStyle} />
                                <select value={aporteInicial.forma} onChange={(e) => setAporteInicial(prev => ({ ...prev, forma: e.target.value }))} style={inputStyle}>
                                    <option value="dinheiro">Dinheiro</option>
                                    <option value="bens">Bens</option>
                                </select>
                            </div>
                        </>
                    ) : (
                        <input
                            name="capital_social"
                            type="number"
                            value={newSocio.capital_social}
                            onChange={handleInputChange}
                            placeholder="Capital Social Atual (R$)"
                            style={inputStyle}
                            readOnly
                        />
                    )}
                    <input name="percentual" type="number" step="0.01" value={newSocio.percentual} onChange={handleInputChange} placeholder="Percentual na Sociedade (ex: 50 para 50%)" style={inputStyle}/>
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <button type="submit" style={buttonStyle}>{editingId ? 'Atualizar Sócio' : 'Adicionar Sócio'}</button>
                        {editingId && (
                            <button type="button" onClick={handleCancelEdit} style={cancelButtonStyle}>Cancelar</button>
                        )}
                    </div>
                </form>
                {editingId && (
                    <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #ddd' }}>
                        <h4 style={{ marginBottom: '8px' }}>Adicionar Aporte de Capital</h4>
                        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                            <input type="number" placeholder="Valor do aporte (R$)" value={aporteEdicao.valor} onChange={(e) => setAporteEdicao(prev => ({ ...prev, valor: e.target.value }))} style={inputStyle} />
                            <input type="date" value={aporteEdicao.data} onChange={(e) => setAporteEdicao(prev => ({ ...prev, data: e.target.value || hojeISO }))} style={inputStyle} />
                            <select value={aporteEdicao.forma} onChange={(e) => setAporteEdicao(prev => ({ ...prev, forma: e.target.value }))} style={inputStyle}>
                                <option value="dinheiro">Dinheiro</option>
                                <option value="bens">Bens</option>
                            </select>
                        </div>
                        <button type="button" onClick={handleRegistrarAporte} style={{ ...buttonStyle, marginTop: '8px' }}>Adicionar Aporte</button>
                    </div>
                )}
            </div>

            {error && <p style={{ color: 'red' }}><strong>Erro:</strong> {error}</p>}

            <h2>Sócios Atuais</h2>
            {isLoading ? (
                <p>Carregando sócios...</p>
            ) : (
                <ul style={listStyle}>
                    {socios.length === 0 && <p>Nenhum sócio cadastrado.</p>}
                    {(() => {
                        const totalCapital = (socios || []).reduce((acc, s) => acc + (s.capital_social || 0), 0);
                        const calcPerc = (s) => {
                            if (!totalCapital) return 0;
                            const cap = s.capital_social || 0;
                            return (cap / totalCapital) * 100;
                        };
                        return socios.map(socio => (
                        <li key={socio.id} style={listItemStyle}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div>
                                    <strong>{socio.nome}</strong>
                                    {socio.usuario && (
                                        <span style={{ color: '#007bff', marginLeft: '8px' }}>
                                            👤 Usuário: {socio.usuario.login}
                                        </span>
                                    )}
                                    <br />
                                    <span style={{ color: '#666' }}>
                                        {socio.funcao || 'N/A'} - Capital: R$ {socio.capital_social?.toFixed(2) || '0.00'} - Percentual: {calcPerc(socio).toFixed(2)}%
                                    </span>
                                </div>
                                <div style={{ display: 'flex', gap: '10px' }}>
                                    <button 
                                        onClick={() => setSelectedSocioForAportes(selectedSocioForAportes?.id === socio.id ? null : socio)} 
                                        style={{
                                            padding: '5px 10px',
                                            backgroundColor: selectedSocioForAportes?.id === socio.id ? '#ffc107' : '#17a2b8',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '4px',
                                            cursor: 'pointer',
                                            fontSize: '14px'
                                        }}
                                    >
                                        💰 Aportes
                                    </button>
                                    <button onClick={() => handleEdit(socio)} style={editButtonStyle}>✏️ Editar</button>
                                    <button onClick={() => handleDelete(socio.id)} style={deleteButtonStyle}>🗑️ Excluir</button>
                                </div>
                            </div>
                            {selectedSocioForAportes?.id === socio.id && (
                                <AportesSection 
                                    socioId={socio.id} 
                                    socioNome={socio.nome}
                                    onAporteChange={fetchSocios}
                                />
                            )}
                        </li>
                        ));
                    })()}
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

const cancelButtonStyle = {
    padding: '10px 20px',
    backgroundColor: '#6c757d',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
};

const editButtonStyle = {
    padding: '5px 10px',
    backgroundColor: '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
};

const deleteButtonStyle = {
    padding: '5px 10px',
    backgroundColor: '#dc3545',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
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

// Componente auxiliar para exibir o total de capital social
const CapitalResumo = ({ socios }) => {
    const total = (socios || []).reduce((acc, s) => acc + (s.capital_social || 0), 0);
    return (
        <div style={{ margin: '12px 0 20px', padding: '12px', background: '#fff', border: '1px solid #e5e5e5', borderRadius: 6 }}>
            <strong>Capital Social Total:</strong> R$ {total.toFixed(2)}
        </div>
    );
};
