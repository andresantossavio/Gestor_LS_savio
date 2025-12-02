import React, { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth, addMonths, subMonths } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export default function PagamentosPendentes() {
    const [mesAtual, setMesAtual] = useState(new Date());
    const [pagamentos, setPagamentos] = useState([]);
    const [resumo, setResumo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [filtroTipo, setFiltroTipo] = useState('TODOS');
    const [apenasPendentes, setApenasPendentes] = useState(false);
    const [editandoData, setEditandoData] = useState(null);
    const [dataConfirmacao, setDataConfirmacao] = useState('');

    const mes = mesAtual.getMonth() + 1;
    const ano = mesAtual.getFullYear();

    const tipos = [
        { value: 'TODOS', label: 'Todos', color: 'secondary' },
        { value: 'SIMPLES', label: 'Simples Nacional', color: 'warning' },
        { value: 'INSS', label: 'INSS', color: 'info' },
        { value: 'LUCRO_SOCIO', label: 'Lucro Sócio', color: 'success' },
        { value: 'FUNDO_RESERVA', label: 'Fundo Reserva', color: 'primary' },
        { value: 'DESPESA', label: 'Despesa', color: 'danger' }
    ];

    useEffect(() => {
        carregarDados();
    }, [mes, ano, filtroTipo, apenasPendentes]);

    const carregarDados = async () => {
        setLoading(true);
        try {
            // Carregar pagamentos
            let url = `/api/pagamentos-pendentes?mes=${mes}&ano=${ano}`;
            if (filtroTipo !== 'TODOS') {
                url += `&tipo=${filtroTipo}`;
            }
            if (apenasPendentes) {
                url += '&apenas_pendentes=true';
            }

            const resPagamentos = await fetch(url);
            const dataPagamentos = await resPagamentos.json();
            setPagamentos(dataPagamentos);

            // Carregar resumo
            const resResumo = await fetch(`/api/pagamentos-pendentes/resumo/${mes}/${ano}`);
            const dataResumo = await resResumo.json();
            setResumo(dataResumo);
        } catch (error) {
            console.error('Erro ao carregar dados:', error);
        } finally {
            setLoading(false);
        }
    };

    const confirmarPagamento = async (pagamentoId, data) => {
        try {
            const res = await fetch(`/api/pagamentos-pendentes/${pagamentoId}/confirmar`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ data_confirmacao: data })
            });

            if (res.ok) {
                carregarDados();
                setEditandoData(null);
            } else {
                alert('Erro ao confirmar pagamento');
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao confirmar pagamento');
        }
    };

    const desconfirmarPagamento = async (pagamentoId) => {
        if (!confirm('Deseja remover a confirmação deste pagamento?')) return;

        try {
            const res = await fetch(`/api/pagamentos-pendentes/${pagamentoId}/desconfirmar`, {
                method: 'POST'
            });

            if (res.ok) {
                carregarDados();
            } else {
                alert('Erro ao desconfirmar pagamento');
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao desconfirmar pagamento');
        }
    };

    const excluirPagamento = async (pagamentoId) => {
        if (!confirm('Deseja realmente excluir este pagamento pendente?')) return;

        try {
            const res = await fetch(`/api/pagamentos-pendentes/${pagamentoId}`, {
                method: 'DELETE'
            });

            if (res.ok) {
                carregarDados();
            } else {
                alert('Erro ao excluir pagamento');
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao excluir pagamento');
        }
    };

    const handleConfirmarComDataHoje = (pagamentoId) => {
        const hoje = format(new Date(), 'yyyy-MM-dd');
        confirmarPagamento(pagamentoId, hoje);
    };

    const handleAbrirModalData = (pagamento) => {
        setEditandoData(pagamento);
        setDataConfirmacao(
            pagamento.data_confirmacao || format(new Date(), 'yyyy-MM-dd')
        );
    };

    const handleSalvarData = () => {
        if (!dataConfirmacao) {
            alert('Selecione uma data');
            return;
        }
        confirmarPagamento(editandoData.id, dataConfirmacao);
    };

    const getTipoColor = (tipo) => {
        const t = tipos.find(t => t.value === tipo);
        return t ? t.color : 'secondary';
    };

    const getTipoLabel = (tipo) => {
        const t = tipos.find(t => t.value === tipo);
        return t ? t.label : tipo;
    };

    const mesAnterior = () => {
        setMesAtual(subMonths(mesAtual, 1));
    };

    const proximoMes = () => {
        setMesAtual(addMonths(mesAtual, 1));
    };

    const mesTexto = format(mesAtual, 'MMMM yyyy', { locale: ptBR });

    if (loading) {
        return (
            <div className="container mt-4">
                <div className="text-center">
                    <div className="spinner-border" role="status">
                        <span className="visually-hidden">Carregando...</span>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="container-fluid mt-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h2>💰 Pagamentos Pendentes</h2>
            </div>

            {/* Navegação de Mês */}
            <div className="card mb-4">
                <div className="card-body">
                    <div className="d-flex justify-content-between align-items-center">
                        <button className="btn btn-outline-primary" onClick={mesAnterior}>
                            ← Mês Anterior
                        </button>
                        <h4 className="mb-0 text-capitalize">{mesTexto}</h4>
                        <button className="btn btn-outline-primary" onClick={proximoMes}>
                            Próximo Mês →
                        </button>
                    </div>
                </div>
            </div>

            {/* Resumo Financeiro */}
            {resumo && (
                <div className="row mb-4">
                    <div className="col-md-3">
                        <div className="card bg-success text-white">
                            <div className="card-body">
                                <h6>Total Entradas</h6>
                                <h3>R$ {resumo.total_entradas.toFixed(2)}</h3>
                                <small>{resumo.qtd_entradas} entradas</small>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-3">
                        <div className="card bg-primary text-white">
                            <div className="card-body">
                                <h6>Confirmadas</h6>
                                <h3>R$ {resumo.total_saidas_confirmadas.toFixed(2)}</h3>
                                <small>{resumo.qtd_confirmados} pagamentos</small>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-3">
                        <div className="card bg-warning text-dark">
                            <div className="card-body">
                                <h6>Pendentes</h6>
                                <h3>R$ {resumo.total_pendente.toFixed(2)}</h3>
                                <small>{resumo.qtd_pendentes} pagamentos</small>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-3">
                        <div className={`card ${resumo.saldo_disponivel >= 0 ? 'bg-info' : 'bg-danger'} text-white`}>
                            <div className="card-body">
                                <h6>Saldo Disponível</h6>
                                <h3>R$ {resumo.saldo_disponivel.toFixed(2)}</h3>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Breakdown por Tipo */}
            {resumo && resumo.breakdown && Object.keys(resumo.breakdown).length > 0 && (
                <div className="card mb-4">
                    <div className="card-header">
                        <h5 className="mb-0">Breakdown por Tipo</h5>
                    </div>
                    <div className="card-body">
                        <div className="row">
                            {Object.entries(resumo.breakdown).map(([tipo, valores]) => (
                                <div key={tipo} className="col-md-4 mb-3">
                                    <div className={`card border-${getTipoColor(tipo)}`}>
                                        <div className="card-body">
                                            <h6 className={`text-${getTipoColor(tipo)}`}>
                                                {getTipoLabel(tipo)}
                                            </h6>
                                            <div>
                                                <small>Confirmado: R$ {valores.confirmado.toFixed(2)}</small>
                                            </div>
                                            <div>
                                                <strong>Pendente: R$ {valores.pendente.toFixed(2)}</strong>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Filtros */}
            <div className="card mb-4">
                <div className="card-body">
                    <div className="row">
                        <div className="col-md-6">
                            <label>Tipo:</label>
                            <select
                                className="form-select"
                                value={filtroTipo}
                                onChange={(e) => setFiltroTipo(e.target.value)}
                            >
                                {tipos.map(t => (
                                    <option key={t.value} value={t.value}>{t.label}</option>
                                ))}
                            </select>
                        </div>
                        <div className="col-md-6">
                            <label>&nbsp;</label>
                            <div className="form-check">
                                <input
                                    type="checkbox"
                                    className="form-check-input"
                                    id="apenasPendentes"
                                    checked={apenasPendentes}
                                    onChange={(e) => setApenasPendentes(e.target.checked)}
                                />
                                <label className="form-check-label" htmlFor="apenasPendentes">
                                    Apenas Pendentes
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Lista de Pagamentos */}
            <div className="card">
                <div className="card-header">
                    <h5 className="mb-0">Lista de Pagamentos ({pagamentos.length})</h5>
                </div>
                <div className="card-body">
                    {pagamentos.length === 0 ? (
                        <div className="alert alert-info">
                            <strong>Nenhum pagamento encontrado para {mesTexto}.</strong>
                            <br />
                            <small>💡 Use os botões "← Mês Anterior" ou "Próximo Mês →" acima para navegar pelos meses com pagamentos registrados (agosto e novembro de 2025).</small>
                        </div>
                    ) : (
                        <div className="table-responsive">
                            <table className="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Status</th>
                                        <th>Tipo</th>
                                        <th>Descrição</th>
                                        <th className="text-end">Valor</th>
                                        <th>Data Confirmação</th>
                                        <th>Ações</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {pagamentos.map(pag => (
                                        <tr key={pag.id} className={pag.confirmado ? 'table-success' : ''}>
                                            <td>
                                                {pag.confirmado ? (
                                                    <span className="badge bg-success">✓ Pago</span>
                                                ) : (
                                                    <span className="badge bg-warning">Pendente</span>
                                                )}
                                            </td>
                                            <td>
                                                <span className={`badge bg-${getTipoColor(pag.tipo)}`}>
                                                    {getTipoLabel(pag.tipo)}
                                                </span>
                                            </td>
                                            <td>{pag.descricao}</td>
                                            <td className="text-end">
                                                <strong>R$ {pag.valor.toFixed(2)}</strong>
                                            </td>
                                            <td>
                                                {pag.data_confirmacao ? (
                                                    format(new Date(pag.data_confirmacao), 'dd/MM/yyyy')
                                                ) : (
                                                    <span className="text-muted">-</span>
                                                )}
                                            </td>
                                            <td>
                                                <div className="btn-group btn-group-sm">
                                                    {!pag.confirmado ? (
                                                        <>
                                                            <button
                                                                className="btn btn-success"
                                                                onClick={() => handleConfirmarComDataHoje(pag.id)}
                                                                title="Confirmar com data de hoje"
                                                            >
                                                                ✓
                                                            </button>
                                                            <button
                                                                className="btn btn-primary"
                                                                onClick={() => handleAbrirModalData(pag)}
                                                                title="Definir data"
                                                            >
                                                                📅
                                                            </button>
                                                        </>
                                                    ) : (
                                                        <>
                                                            <button
                                                                className="btn btn-warning"
                                                                onClick={() => desconfirmarPagamento(pag.id)}
                                                                title="Desfazer confirmação"
                                                            >
                                                                ↺
                                                            </button>
                                                            <button
                                                                className="btn btn-info"
                                                                onClick={() => handleAbrirModalData(pag)}
                                                                title="Editar data"
                                                            >
                                                                📅
                                                            </button>
                                                        </>
                                                    )}
                                                    <button
                                                        className="btn btn-danger"
                                                        onClick={() => excluirPagamento(pag.id)}
                                                        title="Excluir"
                                                    >
                                                        🗑️
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>

            {/* Modal de Editar Data */}
            {editandoData && (
                <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
                    <div className="modal-dialog">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">
                                    {editandoData.confirmado ? 'Editar' : 'Definir'} Data de Confirmação
                                </h5>
                                <button
                                    type="button"
                                    className="btn-close"
                                    onClick={() => setEditandoData(null)}
                                ></button>
                            </div>
                            <div className="modal-body">
                                <div className="mb-3">
                                    <label className="form-label">Pagamento:</label>
                                    <p>{editandoData.descricao}</p>
                                </div>
                                <div className="mb-3">
                                    <label className="form-label">Data de Confirmação:</label>
                                    <input
                                        type="date"
                                        className="form-control"
                                        value={dataConfirmacao}
                                        onChange={(e) => setDataConfirmacao(e.target.value)}
                                    />
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={() => setEditandoData(null)}
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="button"
                                    className="btn btn-primary"
                                    onClick={handleSalvarData}
                                >
                                    Salvar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
