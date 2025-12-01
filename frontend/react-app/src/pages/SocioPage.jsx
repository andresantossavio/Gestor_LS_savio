import React, { useState, useEffect } from 'react';
import Header from '../components/Header';

const apiBase = '/api/contabilidade';

const SocioPage = () => {
    const [socios, setSocios] = useState([]);
    const [usuarios, setUsuarios] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [editingId, setEditingId] = useState(null);
    const [newSocio, setNewSocio] = useState({
        nome: '',
        usuario_id: null,
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
                    capital_social: parseFloat(newSocio.capital_social) || null,
                    percentual: percentualDecimal || null,
                }),
            });
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || `Falha ao ${editingId ? 'atualizar' : 'criar'} sócio`);
            }
            // Reset form and reload list
            setNewSocio({ nome: '', usuario_id: null, funcao: '', capital_social: '', percentual: '' });
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
                    
                    <input name="capital_social" type="number" value={newSocio.capital_social} onChange={handleInputChange} placeholder="Capital Social (R$)" style={inputStyle}/>
                    <input name="percentual" type="number" step="0.01" value={newSocio.percentual} onChange={handleInputChange} placeholder="Percentual na Sociedade (ex: 50 para 50%)" style={inputStyle}/>
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <button type="submit" style={buttonStyle}>{editingId ? 'Atualizar Sócio' : 'Adicionar Sócio'}</button>
                        {editingId && (
                            <button type="button" onClick={handleCancelEdit} style={cancelButtonStyle}>Cancelar</button>
                        )}
                    </div>
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
                                        {socio.funcao || 'N/A'} - Capital: R$ {socio.capital_social?.toFixed(2) || '0.00'} - Percentual: {socio.percentual ? (socio.percentual * 100).toFixed(2) : '0'}%
                                    </span>
                                </div>
                                <div style={{ display: 'flex', gap: '10px' }}>
                                    <button onClick={() => handleEdit(socio)} style={editButtonStyle}>✏️ Editar</button>
                                    <button onClick={() => handleDelete(socio.id)} style={deleteButtonStyle}>🗑️ Excluir</button>
                                </div>
                            </div>
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
