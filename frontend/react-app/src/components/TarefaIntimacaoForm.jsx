import React, { useEffect, useState } from 'react';

const apiBase = '/api';

const CLASSIFICACOES = [
  'Nada a fazer',
  'Intimação ao autor',
  'Decisão Interlocutória',
  'Outras',
  'Sentença'
];

export default function TarefaIntimacaoForm({ processoId, tarefaParaClassificar, onClose, onFormSubmit }) {
  const isClassificacao = !!tarefaParaClassificar;
  
  const [formData, setFormData] = useState({
    conteudo_intimacao: '',
    classificacao_intimacao: '',
    conteudo_decisao: '',
    criar_tarefa_derivada: false,
    tipo_tarefa_derivada_id: '',
    prazo_fatal_derivada: '',
  });

  const [tiposTarefa, setTiposTarefa] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchTipos = async () => {
      try {
        const res = await fetch(`${apiBase}/tipos-tarefa`);
        if (res.ok) {
          const tipos = await res.json();
          // Filtrar apenas tipos que podem ser derivados (Petição, Recurso)
          setTiposTarefa(tipos.filter(t => ['Petição', 'Recurso'].includes(t.nome)));
        }
      } catch (err) {
        console.error('Erro ao carregar tipos de tarefa:', err);
      }
    };
    fetchTipos();
  }, []);

  useEffect(() => {
    if (tarefaParaClassificar) {
      setFormData({
        conteudo_intimacao: tarefaParaClassificar.conteudo_intimacao || '',
        classificacao_intimacao: tarefaParaClassificar.classificacao_intimacao || '',
        conteudo_decisao: tarefaParaClassificar.conteudo_decisao || '',
        criar_tarefa_derivada: false,
        tipo_tarefa_derivada_id: '',
        prazo_fatal_derivada: '',
      });
    }
  }, [tarefaParaClassificar]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newFormData = { ...formData, [name]: type === 'checkbox' ? checked : value };

    // Limpar campos dependentes
    if (name === 'classificacao_intimacao') {
      // Limpar conteúdo de decisão se não for Decisão Interlocutória ou Sentença
      if (!['Decisão Interlocutória', 'Sentença'].includes(value)) {
        newFormData.conteudo_decisao = '';
      }
    }

    if (name === 'criar_tarefa_derivada' && !checked) {
      newFormData.tipo_tarefa_derivada_id = '';
      newFormData.prazo_fatal_derivada = '';
    }

    setFormData(newFormData);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      let url, method, body;

      if (isClassificacao) {
        // Classificar intimação existente
        url = `${apiBase}/tarefas/${tarefaParaClassificar.id}/classificar`;
        method = 'PATCH';
        
        body = {
          classificacao_intimacao: formData.classificacao_intimacao,
        };

        // Adicionar conteúdo de decisão se necessário
        if (['Decisão Interlocutória', 'Sentença'].includes(formData.classificacao_intimacao)) {
          body.conteudo_decisao = formData.conteudo_decisao;
        }

        // Adicionar informações de tarefa derivada se solicitado
        if (formData.criar_tarefa_derivada) {
          body.criar_tarefa_derivada = true;
          body.tipo_tarefa_derivada_id = parseInt(formData.tipo_tarefa_derivada_id, 10);
          body.prazo_fatal_derivada = formData.prazo_fatal_derivada;
        }
      } else {
        // Criar nova intimação
        url = `${apiBase}/processos/${processoId}/tarefas/intimacao`;
        method = 'POST';
        
        body = {
          conteudo_intimacao: formData.conteudo_intimacao,
        };
      }

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Falha ao processar intimação');
      }

      alert(isClassificacao ? 'Intimação classificada com sucesso!' : 'Intimação criada com sucesso!');
      onFormSubmit();
    } catch (err) {
      console.error(err);
      alert(`Erro: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    display: 'block',
    width: '100%',
    padding: '8px',
    marginBottom: '15px',
    borderRadius: '6px',
    border: '1px solid #d1d5db',
    fontSize: '14px',
  };

  const labelStyle = {
    display: 'block',
    marginBottom: '5px',
    fontSize: '14px',
    fontWeight: 500,
    color: '#374151',
  };

  const requerConteudoDecisao = ['Decisão Interlocutória', 'Sentença'].includes(formData.classificacao_intimacao);

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{
          width: '90%',
          maxWidth: '700px',
          maxHeight: '90vh',
          overflowY: 'auto',
          margin: '20px',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#374151' }}>
          {isClassificacao ? 'Classificar Intimação' : 'Nova Análise de Intimação'}
        </h3>

        <form onSubmit={handleSubmit}>
          {/* Conteúdo da Intimação - apenas ao criar */}
          {!isClassificacao && (
            <div>
              <label style={labelStyle}>Conteúdo da Intimação*</label>
              <textarea
                name="conteudo_intimacao"
                value={formData.conteudo_intimacao}
                onChange={handleChange}
                placeholder="Descreva o conteúdo da intimação recebida"
                rows="4"
                required
                style={inputStyle}
              />
              <p style={{ fontSize: 12, color: '#6b7280', marginTop: -10, marginBottom: 15 }}>
                Os prazos serão calculados automaticamente: administrativo em 2 dias úteis, fatal em 3 dias úteis.
              </p>
            </div>
          )}

          {/* Classificação - apenas ao classificar */}
          {isClassificacao && (
            <>
              <div>
                <label style={labelStyle}>Classificação*</label>
                <select
                  name="classificacao_intimacao"
                  value={formData.classificacao_intimacao}
                  onChange={handleChange}
                  required
                  style={inputStyle}
                >
                  <option value="">Selecione a classificação</option>
                  {CLASSIFICACOES.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              {/* Conteúdo da Decisão - apenas para Decisão Interlocutória e Sentença */}
              {requerConteudoDecisao && (
                <div>
                  <label style={labelStyle}>Conteúdo da Decisão*</label>
                  <textarea
                    name="conteudo_decisao"
                    value={formData.conteudo_decisao}
                    onChange={handleChange}
                    placeholder="Descreva o conteúdo da decisão"
                    rows="4"
                    required
                    style={inputStyle}
                  />
                </div>
              )}

              {/* Opção de criar tarefa derivada */}
              <div style={{ marginBottom: 20, padding: 15, backgroundColor: '#f9fafb', borderRadius: 8 }}>
                <label style={{ display: 'flex', alignItems: 'center', fontSize: '14px', cursor: 'pointer', marginBottom: 10 }}>
                  <input
                    type="checkbox"
                    name="criar_tarefa_derivada"
                    checked={formData.criar_tarefa_derivada}
                    onChange={handleChange}
                    style={{ marginRight: '8px' }}
                  />
                  <strong>Criar tarefa derivada (Petição ou Recurso)</strong>
                </label>

                {formData.criar_tarefa_derivada && (
                  <>
                    <div>
                      <label style={labelStyle}>Tipo da Tarefa Derivada*</label>
                      <select
                        name="tipo_tarefa_derivada_id"
                        value={formData.tipo_tarefa_derivada_id}
                        onChange={handleChange}
                        required
                        style={inputStyle}
                      >
                        <option value="">Selecione o tipo</option>
                        {tiposTarefa.map(tipo => (
                          <option key={tipo.id} value={tipo.id}>
                            {tipo.nome}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label style={labelStyle}>Prazo Fatal da Tarefa Derivada*</label>
                      <input
                        type="date"
                        name="prazo_fatal_derivada"
                        value={formData.prazo_fatal_derivada}
                        onChange={handleChange}
                        required
                        style={inputStyle}
                      />
                      <p style={{ fontSize: 12, color: '#6b7280', marginTop: -10 }}>
                        O prazo administrativo será calculado automaticamente (2 dias úteis antes do fatal).
                      </p>
                    </div>
                  </>
                )}
              </div>
            </>
          )}

          {/* Botões */}
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
            <button type="button" onClick={onClose} className="btn btn-secondary" disabled={loading}>
              Cancelar
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Processando...' : (isClassificacao ? 'Classificar' : 'Criar Análise')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
