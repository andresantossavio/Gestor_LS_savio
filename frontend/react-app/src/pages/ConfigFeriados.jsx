import React, { useEffect, useState, useCallback } from 'react';
import Header from '../components/Header';
import FeriadoFormModal from '../components/FeriadoFormModal';

const apiBase = '/api';

export default function ConfigFeriados() {
  const [feriados, setFeriados] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [feriadoParaEditar, setFeriadoParaEditar] = useState(null);
  
  // Filtros
  const [filtros, setFiltros] = useState({
    tipo: '',
    uf: '',
    municipio_id: '',
    ano: new Date().getFullYear(),
  });

  const [ufs, setUfs] = useState([]);
  const [municipios, setMunicipios] = useState([]);

  // Paginação
  const [paginaAtual, setPaginaAtual] = useState(1);
  const itensPorPagina = 20;

  // Carregar UFs
  useEffect(() => {
    const fetchUfs = async () => {
      try {
        const res = await fetch(`${apiBase}/config/ufs`);
        if (!res.ok) throw new Error('Falha ao buscar UFs');
        setUfs(await res.json());
      } catch (err) {
        console.error("Erro ao buscar UFs:", err);
      }
    };
    fetchUfs();
  }, []);

  // Carregar municípios quando UF for selecionada
  useEffect(() => {
    if (filtros.uf) {
      const fetchMunicipios = async () => {
        try {
          const res = await fetch(`${apiBase}/municipios/uf/${filtros.uf}`);
          if (!res.ok) throw new Error('Falha ao buscar municípios');
          const data = await res.json();
          setMunicipios(data);
        } catch (err) {
          console.error("Erro ao buscar municípios:", err);
          setMunicipios([]);
        }
      };
      fetchMunicipios();
    } else {
      setMunicipios([]);
      setFiltros(prev => ({ ...prev, municipio_id: '' }));
    }
  }, [filtros.uf]);

  const loadFeriados = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filtros.tipo) params.append('tipo', filtros.tipo);
      if (filtros.uf) params.append('uf', filtros.uf);
      if (filtros.municipio_id) params.append('municipio_id', filtros.municipio_id);
      if (filtros.ano) params.append('ano', filtros.ano);

      const res = await fetch(`${apiBase}/feriados?${params.toString()}`);
      if (!res.ok) throw new Error('Falha ao buscar feriados');
      const data = await res.json();
      setFeriados(data);
      setPaginaAtual(1);
    } catch (err) {
      console.error(err);
      alert('Erro ao carregar feriados.');
    } finally {
      setLoading(false);
    }
  }, [filtros]);

  useEffect(() => {
    loadFeriados();
  }, [loadFeriados]);

  const handleFiltroChange = (e) => {
    const { name, value } = e.target;
    setFiltros(prev => ({ ...prev, [name]: value }));
  };

  const handleNovoFeriado = () => {
    setFeriadoParaEditar(null);
    setShowModal(true);
  };

  const handleEditarFeriado = (feriado) => {
    setFeriadoParaEditar(feriado);
    setShowModal(true);
  };

  const handleExcluirFeriado = async (feriadoId) => {
    if (!confirm('Tem certeza que deseja excluir este feriado?')) return;

    try {
      const res = await fetch(`${apiBase}/feriados/${feriadoId}`, {
        method: 'DELETE',
      });
      if (!res.ok) throw new Error('Falha ao excluir feriado');
      alert('Feriado excluído com sucesso!');
      loadFeriados();
    } catch (err) {
      console.error(err);
      alert(`Erro ao excluir feriado: ${err.message}`);
    }
  };

  const handleFormSubmit = () => {
    setShowModal(false);
    loadFeriados();
  };

  // Paginação
  const indexUltimo = paginaAtual * itensPorPagina;
  const indexPrimeiro = indexUltimo - itensPorPagina;
  const feriadosPaginados = feriados.slice(indexPrimeiro, indexUltimo);
  const totalPaginas = Math.ceil(feriados.length / itensPorPagina);

  const formatarData = (dataStr) => {
    const date = new Date(dataStr + 'T00:00:00');
    return date.toLocaleDateString('pt-BR');
  };

  const renderTipo = (feriado) => {
    if (feriado.tipo === 'nacional') return 'Nacional';
    if (feriado.tipo === 'estadual') return `Estadual (${feriado.uf})`;
    if (feriado.tipo === 'municipal') return `Municipal (${feriado.municipio?.nome || 'N/A'})`;
    return feriado.tipo;
  };

  return (
    <div style={{ padding: 20 }}>
      <Header title="Gestão de Feriados" />

      {/* Filtros */}
      <div className="card" style={{ marginBottom: 20 }}>
        <h3 style={{ marginTop: 0, marginBottom: 15 }}>Filtros</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: 5, fontSize: 14, fontWeight: 500 }}>Tipo</label>
            <select
              name="tipo"
              value={filtros.tipo}
              onChange={handleFiltroChange}
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db' }}
            >
              <option value="">Todos</option>
              <option value="nacional">Nacional</option>
              <option value="estadual">Estadual</option>
              <option value="municipal">Municipal</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: 5, fontSize: 14, fontWeight: 500 }}>UF</label>
            <select
              name="uf"
              value={filtros.uf}
              onChange={handleFiltroChange}
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db' }}
            >
              <option value="">Todas</option>
              {ufs.map(uf => <option key={uf} value={uf}>{uf}</option>)}
            </select>
          </div>

          {filtros.uf && (
            <div>
              <label style={{ display: 'block', marginBottom: 5, fontSize: 14, fontWeight: 500 }}>Município</label>
              <select
                name="municipio_id"
                value={filtros.municipio_id}
                onChange={handleFiltroChange}
                style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db' }}
              >
                <option value="">Todos</option>
                {municipios.map(m => <option key={m.id} value={m.id}>{m.nome}</option>)}
              </select>
            </div>
          )}

          <div>
            <label style={{ display: 'block', marginBottom: 5, fontSize: 14, fontWeight: 500 }}>Ano</label>
            <input
              type="number"
              name="ano"
              value={filtros.ano}
              onChange={handleFiltroChange}
              min="2020"
              max="2100"
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db' }}
            />
          </div>
        </div>

        <div style={{ marginTop: 15 }}>
          <button onClick={loadFeriados} className="btn btn-primary">
            Buscar
          </button>
        </div>
      </div>

      {/* Botão Novo Feriado */}
      <div style={{ marginBottom: 20 }}>
        <button onClick={handleNovoFeriado} className="btn btn-primary">
          + Novo Feriado
        </button>
      </div>

      {/* Tabela de Feriados */}
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <>
          <div className="card" style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f3f4f6', borderBottom: '2px solid #e5e7eb' }}>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: 600 }}>Data</th>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: 600 }}>Nome</th>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: 600 }}>Tipo</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600 }}>Recorrente</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600 }}>Ações</th>
                </tr>
              </thead>
              <tbody>
                {feriadosPaginados.length === 0 ? (
                  <tr>
                    <td colSpan="5" style={{ padding: '20px', textAlign: 'center', color: '#6b7280' }}>
                      Nenhum feriado encontrado
                    </td>
                  </tr>
                ) : (
                  feriadosPaginados.map(feriado => (
                    <tr key={feriado.id} style={{ borderBottom: '1px solid #e5e7eb' }}>
                      <td style={{ padding: '12px' }}>{formatarData(feriado.data)}</td>
                      <td style={{ padding: '12px' }}>{feriado.nome}</td>
                      <td style={{ padding: '12px' }}>{renderTipo(feriado)}</td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        {feriado.recorrente ? '✓' : '—'}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <button
                          onClick={() => handleEditarFeriado(feriado)}
                          className="btn btn-secondary"
                          style={{ marginRight: 8, fontSize: 12, padding: '6px 12px' }}
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleExcluirFeriado(feriado.id)}
                          className="btn btn-danger"
                          style={{ fontSize: 12, padding: '6px 12px' }}
                        >
                          Excluir
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Paginação */}
          {totalPaginas > 1 && (
            <div style={{ marginTop: 20, display: 'flex', justifyContent: 'center', gap: 10 }}>
              <button
                onClick={() => setPaginaAtual(prev => Math.max(1, prev - 1))}
                disabled={paginaAtual === 1}
                className="btn btn-secondary"
                style={{ fontSize: 12 }}
              >
                Anterior
              </button>
              <span style={{ padding: '8px 12px', fontSize: 14 }}>
                Página {paginaAtual} de {totalPaginas}
              </span>
              <button
                onClick={() => setPaginaAtual(prev => Math.min(totalPaginas, prev + 1))}
                disabled={paginaAtual === totalPaginas}
                className="btn btn-secondary"
                style={{ fontSize: 12 }}
              >
                Próxima
              </button>
            </div>
          )}
        </>
      )}

      {/* Modal de Formulário */}
      {showModal && (
        <FeriadoFormModal
          feriadoParaEditar={feriadoParaEditar}
          onClose={() => setShowModal(false)}
          onFormSubmit={handleFormSubmit}
        />
      )}
    </div>
  );
}
