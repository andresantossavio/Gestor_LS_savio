import React, { useEffect, useState } from 'react';

const apiBase = '/api';

const MESES = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];

const DIAS_SEMANA = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

export default function CalendarioProcesso({ municipioId, tarefas = [] }) {
  const [ano, setAno] = useState(new Date().getFullYear());
  const [mes, setMes] = useState(new Date().getMonth() + 1); // getMonth() retorna 0-11
  const [calendario, setCalendario] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!municipioId) return;

    const loadCalendario = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${apiBase}/feriados/calendario/${ano}/${mes}/${municipioId}`);
        if (!res.ok) throw new Error('Falha ao buscar calendário');
        const data = await res.json();
        setCalendario(data);
      } catch (err) {
        console.error(err);
        alert('Erro ao carregar calendário.');
      } finally {
        setLoading(false);
      }
    };

    loadCalendario();
  }, [ano, mes, municipioId]);

  // Cria mapa de tarefas por data
  const tarefasPorData = {};
  tarefas.forEach(tarefa => {
    if (tarefa.prazo_fatal) {
      const data = new Date(tarefa.prazo_fatal + 'T00:00:00').toISOString().split('T')[0];
      if (!tarefasPorData[data]) tarefasPorData[data] = [];
      tarefasPorData[data].push(tarefa);
    }
  });

  const handleMesAnterior = () => {
    if (mes === 1) {
      setMes(12);
      setAno(ano - 1);
    } else {
      setMes(mes - 1);
    }
  };

  const handleMesProximo = () => {
    if (mes === 12) {
      setMes(1);
      setAno(ano + 1);
    } else {
      setMes(mes + 1);
    }
  };

  const handleHoje = () => {
    const hoje = new Date();
    setAno(hoje.getFullYear());
    setMes(hoje.getMonth() + 1);
  };

  // Obter o dia da semana do primeiro dia do mês (0 = Domingo)
  // Adiciona 'T12:00:00' para evitar problemas de timezone
  const primeiroDiaSemana = calendario.length > 0 
    ? new Date(calendario[0].data + 'T12:00:00').getDay() 
    : 0;

  // Criar array para renderização com espaços vazios
  const diasRender = [];
  for (let i = 0; i < primeiroDiaSemana; i++) {
    diasRender.push(null);
  }
  calendario.forEach(dia => diasRender.push(dia));

  const getDiaStyle = (dia) => {
    if (!dia) return {};

    const base = {
      position: 'relative',
      padding: '8px',
      minHeight: '60px',
      border: '1px solid #e5e7eb',
      cursor: 'pointer',
      transition: 'all 0.2s',
    };

    if (dia.feriado) {
      return {
        ...base,
        backgroundColor: '#fca5a5',
        color: '#7f1d1d',
        fontWeight: 600,
      };
    }

    if (dia.fim_semana) {
      return {
        ...base,
        backgroundColor: '#fee2e2',
        color: '#991b1b',
      };
    }

    if (dia.dia_util) {
      return {
        ...base,
        backgroundColor: '#ffffff',
        color: '#374151',
      };
    }

    return {
      ...base,
      backgroundColor: '#f9fafb',
      color: '#6b7280',
    };
  };

  const renderDia = (dia) => {
    if (!dia) {
      return <div style={{ padding: '8px', minHeight: '60px' }}></div>;
    }

    const temTarefas = tarefasPorData[dia.data] && tarefasPorData[dia.data].length > 0;
    const hoje = new Date().toISOString().split('T')[0];
    const ehHoje = dia.data === hoje;

    return (
      <div
        style={{
          ...getDiaStyle(dia),
          ...(ehHoje && { boxShadow: '0 0 0 2px #FFC107', fontWeight: 700 }),
        }}
        title={dia.feriado ? dia.nome_feriado : ''}
      >
        <div style={{ fontSize: '14px', marginBottom: '4px' }}>{dia.dia}</div>
        {dia.feriado && (
          <div style={{ fontSize: '10px', marginTop: '2px' }}>🎉 {dia.nome_feriado}</div>
        )}
        {temTarefas && (
          <div
            style={{
              position: 'absolute',
              bottom: '4px',
              right: '4px',
              backgroundColor: '#FFC107',
              color: '#000',
              borderRadius: '50%',
              width: '20px',
              height: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '11px',
              fontWeight: 700,
            }}
          >
            {tarefasPorData[dia.data].length}
          </div>
        )}
      </div>
    );
  };

  if (!municipioId) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
        Selecione um município para visualizar o calendário
      </div>
    );
  }

  return (
    <div className="card">
      <div style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <button onClick={handleMesAnterior} className="btn btn-secondary" style={{ padding: '8px 16px' }}>
            ← Anterior
          </button>
          <h3 style={{ margin: 0 }}>
            {MESES[mes - 1]} de {ano}
          </h3>
          <button onClick={handleMesProximo} className="btn btn-secondary" style={{ padding: '8px 16px' }}>
            Próximo →
          </button>
        </div>
        <div style={{ textAlign: 'center' }}>
          <button onClick={handleHoje} className="btn btn-primary" style={{ padding: '6px 12px', fontSize: '12px' }}>
            📅 Hoje
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
          Carregando calendário...
        </div>
      ) : (
        <>
          {/* Grid do Calendário */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(7, 1fr)',
              gap: '2px',
              marginBottom: '20px',
            }}
          >
            {/* Cabeçalho dos dias da semana */}
            {DIAS_SEMANA.map(dia => (
              <div
                key={dia}
                style={{
                  padding: '8px',
                  textAlign: 'center',
                  fontWeight: 600,
                  fontSize: '14px',
                  backgroundColor: '#f3f4f6',
                  color: '#374151',
                }}
              >
                {dia}
              </div>
            ))}

            {/* Dias do mês */}
            {diasRender.map((dia, index) => (
              <div key={index}>{renderDia(dia)}</div>
            ))}
          </div>

          {/* Legenda */}
          <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '15px' }}>
            <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', fontWeight: 600 }}>Legenda:</h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '15px', fontSize: '13px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div style={{ width: '20px', height: '20px', backgroundColor: '#ffffff', border: '1px solid #e5e7eb' }}></div>
                <span>Dia útil</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div style={{ width: '20px', height: '20px', backgroundColor: '#fee2e2', border: '1px solid #e5e7eb' }}></div>
                <span>Fim de semana</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div style={{ width: '20px', height: '20px', backgroundColor: '#fca5a5', border: '1px solid #e5e7eb' }}></div>
                <span>Feriado</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div
                  style={{
                    width: '20px',
                    height: '20px',
                    backgroundColor: '#FFC107',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '11px',
                    fontWeight: 700,
                  }}
                >
                  3
                </div>
                <span>Tarefas no dia</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div style={{ width: '20px', height: '20px', backgroundColor: '#ffffff', border: '2px solid #FFC107' }}></div>
                <span>Dia atual</span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
