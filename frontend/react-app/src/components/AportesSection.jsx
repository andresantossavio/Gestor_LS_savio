import React, { useState, useEffect } from 'react';

const AportesSection = ({ socioId, socioNome, onAporteChange }) => {
    const [aportes, setAportes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingAporte, setEditingAporte] = useState(null);
    const [formData, setFormData] = useState({
        data: new Date().toISOString().split('T')[0],
        valor: '',
        tipo_aporte: 'dinheiro',
        descricao: ''
    });

    const fetchAportes = async () => {
        if (!socioId) return;
        
        setLoading(true);
        try {
            const res = await fetch(`/api/contabilidade/socios/${socioId}/aportes`);
            if (res.ok) {
                const data = await res.json();
                setAportes(data);
            }
        } catch (error) {
            console.error('Erro ao carregar aportes:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAportes();
    }, [socioId]);

    const handleOpenModal = (aporte = null) => {
        if (aporte) {
            setEditingAporte(aporte);
            setFormData({
                data: aporte.data,
                valor: aporte.valor.toString(),
                tipo_aporte: aporte.tipo_aporte,
                descricao: aporte.descricao || ''
            });
        } else {
            setEditingAporte(null);
            setFormData({
                data: new Date().toISOString().split('T')[0],
                valor: '',
                tipo_aporte: 'dinheiro',
                descricao: ''
            });
        }
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setEditingAporte(null);
        setFormData({
            data: new Date().toISOString().split('T')[0],
            valor: '',
            tipo_aporte: 'dinheiro',
            descricao: ''
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        const payload = {
            data: formData.data,
            valor: parseFloat(formData.valor),
            tipo_aporte: formData.tipo_aporte,
            descricao: formData.descricao || null
        };

        try {
            let res;
            if (editingAporte) {
                res = await fetch(`/api/contabilidade/aportes/${editingAporte.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            } else {
                res = await fetch(`/api/contabilidade/socios/${socioId}/aportes`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            }

            if (res.ok) {
                await fetchAportes();
                handleCloseModal();
                if (onAporteChange) onAporteChange();
            } else {
                const error = await res.json();
                alert(`Erro: ${error.detail || 'Falha ao salvar aporte'}`);
            }
        } catch (error) {
            console.error('Erro ao salvar aporte:', error);
            alert('Erro ao salvar aporte');
        }
    };

    const handleDelete = async (aporteId) => {
        if (!confirm('Tem certeza que deseja excluir este aporte? O capital social será recalculado automaticamente.')) {
            return;
        }

        try {
            const res = await fetch(`/api/contabilidade/aportes/${aporteId}`, {
                method: 'DELETE'
            });

            if (res.ok) {
                await fetchAportes();
                if (onAporteChange) onAporteChange();
            } else {
                alert('Erro ao excluir aporte');
            }
        } catch (error) {
            console.error('Erro ao excluir aporte:', error);
            alert('Erro ao excluir aporte');
        }
    };

    const getTipoBadge = (tipo) => {
        const badges = {
            'dinheiro': { label: '💵 Dinheiro', color: '#28a745' },
            'bens': { label: '🏢 Bens', color: '#007bff' },
            'servicos': { label: '⚙️ Serviços', color: '#9c27b0' },
            'retirada': { label: '📤 Retirada', color: '#dc3545' }
        };
        const badge = badges[tipo] || { label: tipo, color: '#6c757d' };
        return (
            <span style={{
                backgroundColor: badge.color,
                color: 'white',
                padding: '4px 12px',
                borderRadius: '12px',
                fontSize: '12px',
                fontWeight: '600'
            }}>
                {badge.label}
            </span>
        );
    };

    const formatDate = (dateStr) => {
        const date = new Date(dateStr + 'T00:00:00');
        return date.toLocaleDateString('pt-BR');
    };

    const formatCurrency = (value) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    };

    return (
        <div style={{ marginTop: '30px' }}>
            <div style={{ 
                backgroundColor: '#fff', 
                border: '1px solid #e5e5e5', 
                borderRadius: '8px',
                padding: '20px'
            }}>
                <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    marginBottom: '20px'
                }}>
                    <h3 style={{ margin: 0 }}>Aportes de Capital - {socioNome}</h3>
                    <button
                        onClick={() => handleOpenModal()}
                        style={{
                            padding: '10px 20px',
                            backgroundColor: '#007bff',
                            color: 'white',
                            border: 'none',
                            borderRadius: '5px',
                            cursor: 'pointer',
                            fontWeight: '600'
                        }}
                    >
                        ➕ Novo Aporte
                    </button>
                </div>

                {loading ? (
                    <p>Carregando aportes...</p>
                ) : aportes.length === 0 ? (
                    <p style={{ color: '#6c757d', textAlign: 'center', padding: '20px' }}>
                        Nenhum aporte registrado
                    </p>
                ) : (
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ backgroundColor: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                                <th style={{ padding: '12px', textAlign: 'left' }}>Data</th>
                                <th style={{ padding: '12px', textAlign: 'right' }}>Valor</th>
                                <th style={{ padding: '12px', textAlign: 'center' }}>Tipo</th>
                                <th style={{ padding: '12px', textAlign: 'left' }}>Descrição</th>
                                <th style={{ padding: '12px', textAlign: 'center' }}>Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {aportes.map((aporte) => (
                                <tr key={aporte.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                                    <td style={{ padding: '12px' }}>{formatDate(aporte.data)}</td>
                                    <td style={{ padding: '12px', textAlign: 'right', fontWeight: '600' }}>
                                        {formatCurrency(aporte.valor)}
                                    </td>
                                    <td style={{ padding: '12px', textAlign: 'center' }}>
                                        {getTipoBadge(aporte.tipo_aporte)}
                                    </td>
                                    <td style={{ padding: '12px' }}>
                                        {aporte.descricao || '-'}
                                    </td>
                                    <td style={{ padding: '12px', textAlign: 'center' }}>
                                        <button
                                            onClick={() => handleOpenModal(aporte)}
                                            style={{
                                                padding: '5px 10px',
                                                backgroundColor: '#28a745',
                                                color: 'white',
                                                border: 'none',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                                marginRight: '5px'
                                            }}
                                        >
                                            ✏️
                                        </button>
                                        <button
                                            onClick={() => handleDelete(aporte.id)}
                                            style={{
                                                padding: '5px 10px',
                                                backgroundColor: '#dc3545',
                                                color: 'white',
                                                border: 'none',
                                                borderRadius: '4px',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            🗑️
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Modal */}
            {showModal && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.5)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000
                }}>
                    <div style={{
                        backgroundColor: 'white',
                        borderRadius: '8px',
                        padding: '30px',
                        width: '500px',
                        maxWidth: '90%'
                    }}>
                        <h3 style={{ marginTop: 0 }}>
                            {editingAporte ? 'Editar Aporte' : 'Novo Aporte'}
                        </h3>
                        
                        <form onSubmit={handleSubmit}>
                            <div style={{ marginBottom: '15px' }}>
                                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>
                                    Data
                                </label>
                                <input
                                    type="date"
                                    value={formData.data}
                                    onChange={(e) => setFormData({ ...formData, data: e.target.value })}
                                    required
                                    style={{
                                        width: '100%',
                                        padding: '10px',
                                        border: '1px solid #ccc',
                                        borderRadius: '4px'
                                    }}
                                />
                            </div>

                            <div style={{ marginBottom: '15px' }}>
                                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>
                                    Valor (R$)
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={formData.valor}
                                    onChange={(e) => setFormData({ ...formData, valor: e.target.value })}
                                    required
                                    style={{
                                        width: '100%',
                                        padding: '10px',
                                        border: '1px solid #ccc',
                                        borderRadius: '4px'
                                    }}
                                />
                            </div>

                            <div style={{ marginBottom: '15px' }}>
                                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>
                                    Tipo de Aporte
                                </label>
                                <select
                                    value={formData.tipo_aporte}
                                    onChange={(e) => setFormData({ ...formData, tipo_aporte: e.target.value })}
                                    required
                                    style={{
                                        width: '100%',
                                        padding: '10px',
                                        border: '1px solid #ccc',
                                        borderRadius: '4px'
                                    }}
                                >
                                    <option value="dinheiro">💵 Dinheiro</option>
                                    <option value="bens">🏢 Bens</option>
                                    <option value="servicos">⚙️ Serviços</option>
                                    <option value="retirada">📤 Retirada (Saída de Sócio)</option>
                                </select>
                            </div>

                            <div style={{ marginBottom: '20px' }}>
                                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>
                                    Descrição (opcional)
                                </label>
                                <textarea
                                    value={formData.descricao}
                                    onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                                    rows={3}
                                    style={{
                                        width: '100%',
                                        padding: '10px',
                                        border: '1px solid #ccc',
                                        borderRadius: '4px',
                                        resize: 'vertical'
                                    }}
                                />
                            </div>

                            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                                <button
                                    type="button"
                                    onClick={handleCloseModal}
                                    style={{
                                        padding: '10px 20px',
                                        backgroundColor: '#6c757d',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '5px',
                                        cursor: 'pointer'
                                    }}
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    style={{
                                        padding: '10px 20px',
                                        backgroundColor: '#007bff',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '5px',
                                        cursor: 'pointer'
                                    }}
                                >
                                    {editingAporte ? 'Atualizar' : 'Criar Aporte'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AportesSection;
