import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';

const apiBase = '/api/contabilidade';

const EntradasDespesas = () => {
    const navigate = useNavigate();
    const [entradas, setEntradas] = useState([]);
    const [despesas, setDespesas] = useState([]);
    const [socios, setSocios] = useState([]);
    const [clientes, setClientes] = useState([]);
    const [filtroAno, setFiltroAno] = useState(new Date().getFullYear());
    const [filtroMes, setFiltroMes] = useState('');
    const [editandoEntrada, setEditandoEntrada] = useState(null);
    const [editandoDespesa, setEditandoDespesa] = useState(null);
    const [error, setError] = useState(null);
    const [sucesso, setSucesso] = useState(null);

    useEffect(() => {
        carregarDados();
    }, [filtroAno, filtroMes]);

    // Inicializar filtros a partir de parâmetros da URL (ex: ?mes=12&ano=2025)
    useEffect(() => {
        try {
            const params = new URLSearchParams(window.location.search);
            const mesParam = params.get('mes');
            const anoParam = params.get('ano');
            if (anoParam && !isNaN(parseInt(anoParam))) {
                setFiltroAno(parseInt(anoParam));
            }
            if (mesParam && !isNaN(parseInt(mesParam))) {
                setFiltroMes(String(parseInt(mesParam)));
            }
        } catch {}
    }, []);

    const carregarDados = async () => {
        try {
            const [entradasRes, despesasRes, sociosRes, clientesRes] = await Promise.all([
                fetch(`${apiBase}/entradas?skip=0&limit=1000`),
                fetch(`${apiBase}/despesas?skip=0&limit=1000`),
                fetch(`${apiBase}/socios`),
                fetch('/api/clientes')
            ]);

            if (!entradasRes.ok || !despesasRes.ok || !sociosRes.ok || !clientesRes.ok) {
                throw new Error('Falha ao carregar dados');
            }

            let todasEntradas = await entradasRes.json();
            let todasDespesas = await despesasRes.json();
            const todosSocios = await sociosRes.json();
            const todosClientes = await clientesRes.json();

            // Filtrar por ano e mês
            if (filtroAno) {
                todasEntradas = todasEntradas.filter(e => new Date(e.data).getFullYear() === parseInt(filtroAno));
                todasDespesas = todasDespesas.filter(d => new Date(d.data).getFullYear() === parseInt(filtroAno));
            }
            if (filtroMes) {
                todasEntradas = todasEntradas.filter(e => new Date(e.data).getMonth() + 1 === parseInt(filtroMes));
                todasDespesas = todasDespesas.filter(d => new Date(d.data).getMonth() + 1 === parseInt(filtroMes));
            }

            // Ordenar por data (mais recente primeiro)
            todasEntradas.sort((a, b) => new Date(b.data) - new Date(a.data));
            todasDespesas.sort((a, b) => new Date(b.data) - new Date(a.data));

            setEntradas(todasEntradas);
            setDespesas(todasDespesas);
            setSocios(todosSocios);
            setClientes(todosClientes);
        } catch (err) {
            setError(err.message);
        }
    };

    const formatarData = (data) => {
        return new Date(data).toLocaleDateString('pt-BR');
    };

    const formatarMoeda = (valor) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor);
    };

    const iniciarEdicaoEntrada = (entrada) => {
        // Criar cópia profunda para edição mantendo percentual inteiro já armazenado
        const copiaEntrada = {
            ...entrada,
            socios: entrada.socios ? entrada.socios.map(s => ({ ...s })) : []
        };
        setEditandoEntrada(copiaEntrada);
        setEditandoDespesa(null);
    };

    const iniciarEdicaoDespesa = (despesa) => {
        // Criar cópia profunda para edição
        const copiaDespesa = {
            ...despesa,
            responsaveis: despesa.responsaveis ? despesa.responsaveis.map(r => ({ ...r })) : []
        };
        setEditandoDespesa(copiaDespesa);
        setEditandoEntrada(null);
    };

    const atualizarPercentualSocio = (socioId, novoPercentual) => {
        const socios = [...editandoEntrada.socios];
        const index = socios.findIndex(s => s.socio_id === socioId);
        if (index !== -1) {
            socios[index] = { ...socios[index], percentual: parseFloat(novoPercentual) };
            setEditandoEntrada({ ...editandoEntrada, socios });
        }
    };

    const adicionarSocioEntrada = () => {
        const sociosDisponiveis = socios.filter(s => 
            !editandoEntrada.socios.some(es => es.socio_id === s.id)
        );
        if (sociosDisponiveis.length > 0) {
            const novoSocio = {
                socio_id: sociosDisponiveis[0].id,
                percentual: 0
            };
            setEditandoEntrada({
                ...editandoEntrada,
                socios: [...editandoEntrada.socios, novoSocio]
            });
        }
    };

    const removerSocioEntrada = (socioId) => {
        setEditandoEntrada({
            ...editandoEntrada,
            socios: editandoEntrada.socios.filter(s => s.socio_id !== socioId)
        });
    };

    const adicionarResponsavelDespesa = () => {
        const sociosDisponiveis = socios.filter(s => 
            !editandoDespesa.responsaveis.some(r => r.socio_id === s.id)
        );
        if (sociosDisponiveis.length > 0) {
            const novoResponsavel = {
                socio_id: sociosDisponiveis[0].id
            };
            setEditandoDespesa({
                ...editandoDespesa,
                responsaveis: [...editandoDespesa.responsaveis, novoResponsavel]
            });
        }
    };

    const removerResponsavelDespesa = (socioId) => {
        setEditandoDespesa({
            ...editandoDespesa,
            responsaveis: editandoDespesa.responsaveis.filter(r => r.socio_id !== socioId)
        });
    };

    const cancelarEdicao = () => {
        setEditandoEntrada(null);
        setEditandoDespesa(null);
        setError(null);
    };

    const salvarEntrada = async () => {
        try {
            setError(null);
            
            // Validar soma das porcentagens
            const totalPercentual = editandoEntrada.socios?.reduce((sum, s) => sum + parseFloat(s.percentual || 0), 0) || 0;
            if (Math.abs(totalPercentual - 100) > 0.01) {
                throw new Error(`A soma das porcentagens deve ser 100%. Total atual: ${totalPercentual.toFixed(2)}%`);
            }
            
            const response = await fetch(`${apiBase}/entradas/${editandoEntrada.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    cliente: editandoEntrada.cliente,
                    cliente_id: editandoEntrada.cliente_id,
                    data: editandoEntrada.data,
                    valor: parseFloat(editandoEntrada.valor),
                    socios: (editandoEntrada.socios || []).map(s => ({
                        socio_id: s.socio_id,
                        percentual: parseFloat(s.percentual)
                    }))
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Falha ao atualizar entrada');
            }

            setSucesso('Entrada atualizada com sucesso!');
            setTimeout(() => setSucesso(null), 3000);
            setEditandoEntrada(null);
            carregarDados();
        } catch (err) {
            setError(err.message);
        }
    };

    const salvarDespesa = async () => {
        try {
            setError(null);
            const response = await fetch(`${apiBase}/despesas/${editandoDespesa.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    data: editandoDespesa.data,
                    especie: editandoDespesa.especie,
                    tipo: editandoDespesa.tipo,
                    descricao: editandoDespesa.descricao,
                    valor: parseFloat(editandoDespesa.valor),
                    responsaveis: editandoDespesa.responsaveis || []
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Falha ao atualizar despesa');
            }

            setSucesso('Despesa atualizada com sucesso!');
            setTimeout(() => setSucesso(null), 3000);
            setEditandoDespesa(null);
            carregarDados();
        } catch (err) {
            setError(err.message);
        }
    };

    const excluirEntrada = async (id) => {
        if (!window.confirm('Tem certeza que deseja excluir esta entrada?')) return;

        try {
            const response = await fetch(`${apiBase}/entradas/${id}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Falha ao excluir entrada');
            
            setSucesso('Entrada excluída com sucesso!');
            setTimeout(() => setSucesso(null), 3000);
            carregarDados();
        } catch (err) {
            setError(err.message);
        }
    };

    const excluirDespesa = async (id) => {
        if (!window.confirm('Tem certeza que deseja excluir esta despesa?')) return;

        try {
            const response = await fetch(`${apiBase}/despesas/${id}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Falha ao excluir despesa');
            
            setSucesso('Despesa excluída com sucesso!');
            setTimeout(() => setSucesso(null), 3000);
            carregarDados();
        } catch (err) {
            setError(err.message);
        }
    };

    const anos = [2024, 2025, 2026, 2027];
    const meses = [
        { valor: '', nome: 'Todos os meses' },
        { valor: '1', nome: 'Janeiro' },
        { valor: '2', nome: 'Fevereiro' },
        { valor: '3', nome: 'Março' },
        { valor: '4', nome: 'Abril' },
        { valor: '5', nome: 'Maio' },
        { valor: '6', nome: 'Junho' },
        { valor: '7', nome: 'Julho' },
        { valor: '8', nome: 'Agosto' },
        { valor: '9', nome: 'Setembro' },
        { valor: '10', nome: 'Outubro' },
        { valor: '11', nome: 'Novembro' },
        { valor: '12', nome: 'Dezembro' }
    ];

    return (
        <div style={{ padding: 20 }}>
            <Header title="Gerenciar Entradas e Despesas" />

            {/* Filtros */}
            <div style={{ marginBottom: 20, padding: 15, backgroundColor: '#f5f5f5', borderRadius: 8 }}>
                <h3 style={{ marginTop: 0 }}>Filtros</h3>
                <div style={{ display: 'flex', gap: 15 }}>
                    <div>
                        <label style={{ display: 'block', marginBottom: 5, fontWeight: 'bold' }}>Ano:</label>
                        <select value={filtroAno} onChange={(e) => setFiltroAno(e.target.value)} style={inputStyle}>
                            {anos.map(ano => (
                                <option key={ano} value={ano}>{ano}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label style={{ display: 'block', marginBottom: 5, fontWeight: 'bold' }}>Mês:</label>
                        <select value={filtroMes} onChange={(e) => setFiltroMes(e.target.value)} style={inputStyle}>
                            {meses.map(mes => (
                                <option key={mes.valor} value={mes.valor}>{mes.nome}</option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            {/* Mensagens */}
            {error && <div style={{ padding: 10, backgroundColor: '#ffebee', color: '#c62828', borderRadius: 5, marginBottom: 15 }}>
                <strong>Erro:</strong> {error}
            </div>}
            {sucesso && <div style={{ padding: 10, backgroundColor: '#e8f5e9', color: '#2e7d32', borderRadius: 5, marginBottom: 15 }}>
                {sucesso}
            </div>}

            {/* Botões de Ação */}
            <div style={{ marginBottom: 20, display: 'flex', gap: 10 }}>
                <button onClick={() => navigate('/contabilidade/entradas/nova')} style={{ ...buttonStyle, backgroundColor: '#28a745' }}>
                    ➕ Nova Entrada
                </button>
                <button onClick={() => navigate('/contabilidade/despesas/nova')} style={{ ...buttonStyle, backgroundColor: '#dc3545' }}>
                    ➕ Nova Despesa
                </button>
            </div>

            {/* Tabela de Entradas */}
            <div style={{ marginBottom: 40 }}>
                <h2 style={{ color: '#28a745' }}>💰 Entradas ({entradas.length})</h2>
                {entradas.length === 0 ? (
                    <p style={{ fontStyle: 'italic', color: '#666' }}>Nenhuma entrada encontrada para o período selecionado.</p>
                ) : (
                    <div style={{ overflowX: 'auto' }}>
                        <table style={tableStyle}>
                            <thead>
                                <tr style={{ backgroundColor: '#28a745', color: 'white' }}>
                                    <th style={thStyle}>Data</th>
                                    <th style={thStyle}>Cliente</th>
                                    <th style={thStyle}>Valor</th>
                                    <th style={thStyle}>Sócios (%)</th>
                                    <th style={thStyle}>Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {entradas.map(entrada => (
                                    <React.Fragment key={entrada.id}>
                                        {editandoEntrada?.id === entrada.id ? (
                                            <tr style={{ backgroundColor: '#fff3cd' }}>
                                                <td style={tdStyle}>
                                                    <input
                                                        type="date"
                                                        value={editandoEntrada.data}
                                                        onChange={(e) => setEditandoEntrada({ ...editandoEntrada, data: e.target.value })}
                                                        style={{ ...inputStyle, width: '100%' }}
                                                    />
                                                </td>
                                                <td style={tdStyle}>
                                                    <input
                                                        type="text"
                                                        value={editandoEntrada.cliente}
                                                        onChange={(e) => setEditandoEntrada({ ...editandoEntrada, cliente: e.target.value })}
                                                        style={{ ...inputStyle, width: '100%' }}
                                                    />
                                                </td>
                                                <td style={tdStyle}>
                                                    <input
                                                        type="number"
                                                        step="0.01"
                                                        value={editandoEntrada.valor}
                                                        onChange={(e) => setEditandoEntrada({ ...editandoEntrada, valor: e.target.value })}
                                                        style={{ ...inputStyle, width: '100%' }}
                                                    />
                                                </td>
                                                <td style={tdStyle}>
                                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                                        {editandoEntrada.socios?.map(s => {
                                                            const socio = socios.find(soc => soc.id === s.socio_id);
                                                            return (
                                                                <div key={s.socio_id} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                                                                    <span style={{ fontSize: '12px', minWidth: '80px' }}>{socio?.nome || 'N/A'}:</span>
                                                                    <input
                                                                        type="number"
                                                                        step="0.01"
                                                                        value={s.percentual}
                                                                        onChange={(e) => atualizarPercentualSocio(s.socio_id, e.target.value)}
                                                                        style={{ ...inputStyle, width: '60px', padding: '4px' }}
                                                                    />
                                                                    <span style={{ fontSize: '12px' }}>%</span>
                                                                    <button 
                                                                        onClick={() => removerSocioEntrada(s.socio_id)}
                                                                        style={{ ...actionButtonStyle, backgroundColor: '#dc3545', padding: '2px 6px', fontSize: '10px' }}
                                                                    >
                                                                        ✗
                                                                    </button>
                                                                </div>
                                                            );
                                                        })}
                                                        <button 
                                                            onClick={adicionarSocioEntrada}
                                                            style={{ ...actionButtonStyle, backgroundColor: '#28a745', padding: '4px 8px', fontSize: '11px' }}
                                                        >
                                                            ➕ Adicionar Sócio
                                                        </button>
                                                        <div style={{ fontSize: '11px', fontWeight: 'bold', marginTop: '4px' }}>
                                                            Total: {editandoEntrada.socios?.reduce((sum, s) => sum + parseFloat(s.percentual || 0), 0).toFixed(2)}%
                                                        </div>
                                                    </div>
                                                </td>
                                                <td style={tdStyle}>
                                                    <button onClick={salvarEntrada} style={{ ...actionButtonStyle, backgroundColor: '#28a745', marginRight: 5 }}>
                                                        ✓ Salvar
                                                    </button>
                                                    <button onClick={cancelarEdicao} style={{ ...actionButtonStyle, backgroundColor: '#6c757d' }}>
                                                        ✗ Cancelar
                                                    </button>
                                                </td>
                                            </tr>
                                        ) : (
                                            <tr style={{ backgroundColor: entrada.id % 2 === 0 ? '#f9f9f9' : 'white' }}>
                                                <td style={tdStyle}>{formatarData(entrada.data)}</td>
                                                <td style={tdStyle}>{entrada.cliente}</td>
                                                <td style={tdStyle}>{formatarMoeda(entrada.valor)}</td>
                                                <td style={tdStyle}>
                                                    {entrada.socios?.map(s => {
                                                        return s.socio ? `${s.socio.nome} (${s.percentual.toFixed(2)}%)` : '';
                                                    }).filter(Boolean).join(', ') || 'N/A'}
                                                </td>
                                                <td style={tdStyle}>
                                                    <button 
                                                        onClick={() => iniciarEdicaoEntrada(entrada)} 
                                                        style={{ ...actionButtonStyle, backgroundColor: '#007bff', marginRight: 5 }}
                                                        title="Editar entrada"
                                                    >
                                                        ✏️ Editar
                                                    </button>
                                                    <button 
                                                        onClick={() => excluirEntrada(entrada.id)} 
                                                        style={{ ...actionButtonStyle, backgroundColor: '#dc3545' }}
                                                        title="Excluir entrada"
                                                    >
                                                        🗑️ Excluir
                                                    </button>
                                                </td>
                                            </tr>
                                        )}
                                    </React.Fragment>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Tabela de Despesas */}
            <div>
                <h2 style={{ color: '#dc3545' }}>💸 Despesas ({despesas.length})</h2>
                {despesas.length === 0 ? (
                    <p style={{ fontStyle: 'italic', color: '#666' }}>Nenhuma despesa encontrada para o período selecionado.</p>
                ) : (
                    <div style={{ overflowX: 'auto' }}>
                        <table style={tableStyle}>
                            <thead>
                                <tr style={{ backgroundColor: '#dc3545', color: 'white' }}>
                                    <th style={thStyle}>Data</th>
                                    <th style={thStyle}>Espécie</th>
                                    <th style={thStyle}>Tipo</th>
                                    <th style={thStyle}>Descrição</th>
                                    <th style={thStyle}>Valor</th>
                                    <th style={thStyle}>Responsáveis</th>
                                    <th style={thStyle}>Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {despesas.map(despesa => (
                                    <React.Fragment key={despesa.id}>
                                        {editandoDespesa?.id === despesa.id ? (
                                            <tr style={{ backgroundColor: '#fff3cd' }}>
                                                <td style={tdStyle}>
                                                    <input
                                                        type="date"
                                                        value={editandoDespesa.data}
                                                        onChange={(e) => setEditandoDespesa({ ...editandoDespesa, data: e.target.value })}
                                                        style={{ ...inputStyle, width: '100%' }}
                                                    />
                                                </td>
                                                <td style={tdStyle}>
                                                    <input
                                                        type="text"
                                                        value={editandoDespesa.especie}
                                                        onChange={(e) => setEditandoDespesa({ ...editandoDespesa, especie: e.target.value })}
                                                        style={{ ...inputStyle, width: '100%' }}
                                                    />
                                                </td>
                                                <td style={tdStyle}>
                                                    <input
                                                        type="text"
                                                        value={editandoDespesa.tipo}
                                                        onChange={(e) => setEditandoDespesa({ ...editandoDespesa, tipo: e.target.value })}
                                                        style={{ ...inputStyle, width: '100%' }}
                                                    />
                                                </td>
                                                <td style={tdStyle}>
                                                    <input
                                                        type="text"
                                                        value={editandoDespesa.descricao || ''}
                                                        onChange={(e) => setEditandoDespesa({ ...editandoDespesa, descricao: e.target.value })}
                                                        style={{ ...inputStyle, width: '100%' }}
                                                    />
                                                </td>
                                                <td style={tdStyle}>
                                                    <input
                                                        type="number"
                                                        step="0.01"
                                                        value={editandoDespesa.valor}
                                                        onChange={(e) => setEditandoDespesa({ ...editandoDespesa, valor: e.target.value })}
                                                        style={{ ...inputStyle, width: '100%' }}
                                                    />
                                                </td>
                                                <td style={tdStyle}>
                                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                                        {editandoDespesa.responsaveis?.map(r => {
                                                            const socio = socios.find(soc => soc.id === r.socio_id);
                                                            return (
                                                                <div key={r.socio_id} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                                                                    <span style={{ fontSize: '12px', minWidth: '100px' }}>{socio?.nome || 'N/A'}</span>
                                                                    <button 
                                                                        onClick={() => removerResponsavelDespesa(r.socio_id)}
                                                                        style={{ ...actionButtonStyle, backgroundColor: '#dc3545', padding: '2px 6px', fontSize: '10px' }}
                                                                    >
                                                                        ✗
                                                                    </button>
                                                                </div>
                                                            );
                                                        })}
                                                        <button 
                                                            onClick={adicionarResponsavelDespesa}
                                                            style={{ ...actionButtonStyle, backgroundColor: '#28a745', padding: '4px 8px', fontSize: '11px' }}
                                                        >
                                                            ➕ Adicionar Responsável
                                                        </button>
                                                        <div style={{ fontSize: '11px', fontStyle: 'italic', marginTop: '4px' }}>
                                                            Total: {editandoDespesa.responsaveis?.length || 0} responsável(is)
                                                        </div>
                                                    </div>
                                                </td>
                                                <td style={tdStyle}>
                                                    <button onClick={salvarDespesa} style={{ ...actionButtonStyle, backgroundColor: '#28a745', marginRight: 5 }}>
                                                        ✓ Salvar
                                                    </button>
                                                    <button onClick={cancelarEdicao} style={{ ...actionButtonStyle, backgroundColor: '#6c757d' }}>
                                                        ✗ Cancelar
                                                    </button>
                                                </td>
                                            </tr>
                                        ) : (
                                            <tr style={{ backgroundColor: despesa.id % 2 === 0 ? '#f9f9f9' : 'white' }}>
                                                <td style={tdStyle}>{formatarData(despesa.data)}</td>
                                                <td style={tdStyle}>{despesa.especie}</td>
                                                <td style={tdStyle}>{despesa.tipo}</td>
                                                <td style={tdStyle}>{despesa.descricao || '-'}</td>
                                                <td style={tdStyle}>{formatarMoeda(despesa.valor)}</td>
                                                <td style={tdStyle}>
                                                    {despesa.responsaveis?.map(r => {
                                                        const socio = socios.find(s => s.id === r.socio_id);
                                                        return socio ? socio.nome : '';
                                                    }).join(', ') || 'N/A'}
                                                </td>
                                                <td style={tdStyle}>
                                                    <button 
                                                        onClick={() => iniciarEdicaoDespesa(despesa)} 
                                                        style={{ ...actionButtonStyle, backgroundColor: '#007bff', marginRight: 5 }}
                                                        title="Editar despesa"
                                                    >
                                                        ✏️ Editar
                                                    </button>
                                                    <button 
                                                        onClick={() => excluirDespesa(despesa.id)} 
                                                        style={{ ...actionButtonStyle, backgroundColor: '#dc3545' }}
                                                        title="Excluir despesa"
                                                    >
                                                        🗑️ Excluir
                                                    </button>
                                                </td>
                                            </tr>
                                        )}
                                    </React.Fragment>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

// Estilos
const inputStyle = {
    padding: '8px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '14px'
};

const buttonStyle = {
    padding: '10px 20px',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 'bold'
};

const actionButtonStyle = {
    padding: '5px 10px',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px'
};

const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    marginTop: '10px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
};

const thStyle = {
    padding: '12px',
    textAlign: 'left',
    fontWeight: 'bold',
    borderBottom: '2px solid #ddd'
};

const tdStyle = {
    padding: '10px',
    borderBottom: '1px solid #eee'
};

export default EntradasDespesas;
