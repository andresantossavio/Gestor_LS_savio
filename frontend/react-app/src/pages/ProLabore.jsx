import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function ProLabore() {
  const [ano, setAno] = useState(new Date().getFullYear());
  const [dados, setDados] = useState([]);
  const [socios, setSocios] = useState([]);
  const [socioSelecionado, setSocioSelecionado] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    carregarSocios();
  }, []);

  useEffect(() => {
    if (socioSelecionado) {
      carregarDados();
    }
  }, [ano, socioSelecionado]);

  const carregarSocios = async () => {
    try {
      const response = await fetch('/api/contabilidade/socios');
      if (!response.ok) throw new Error('Erro ao carregar sócios');
      const data = await response.json();
      
      // Filtrar apenas sócios administradores
      const administradores = data.filter(s => s.funcao === 'Administrador');
      setSocios(administradores);
      
      // Selecionar primeiro administrador por padrão
      if (administradores.length > 0) {
        setSocioSelecionado(administradores[0]);
      }
    } catch (err) {
      setError(err.message);
      console.error('Erro ao carregar sócios:', err);
    }
  };

  const carregarDados = async () => {
    if (!socioSelecionado) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/contabilidade/pro-labore/${socioSelecionado.id}?year=${ano}`);
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Erro ao carregar dados: ${errorText}`);
      }
      const data = await response.json();
      
      // Validar se a resposta tem o formato esperado
      if (!data || !data.meses || !Array.isArray(data.meses)) {
        console.error('Resposta inválida do servidor:', data);
        setDados([]);
        return;
      }
      
      // Transformar os dados para o formato esperado pela UI
      const dadosFormatados = data.meses.map(mes => {
        // Backend já retorna INSS pessoal e patronal calculados corretamente
        const inssPessoal = mes.inss_pessoal || 0;
        const inssPatronal = mes.inss_patronal || 0;
        const inssTotal = inssPessoal + inssPatronal;
        
        return {
          mes: `${mes.ano}-${String(mes.mes).padStart(2, '0')}`,
          lucro_liquido: mes.lucro_liquido || 0,
          proLaboreBruto: mes.pro_labore_bruto || 0,
          inssPessoal: inssPessoal,
          inssPatronal: inssPatronal,
          inssTotal: inssTotal,
          proLaboreLiquido: mes.pro_labore_liquido || 0,
          lucroFinal: mes.lucro_final_socio || 0,
          percentualContribuicao: mes.percentual_contribuicao || 0,
          faturamentoTotal: mes.faturamento_total || 0,
          contribuicaoSocio: mes.contribuicao_socio || 0
        };
      });
      
      // Mostrar todos os meses que retornaram do backend
      setDados(dadosFormatados);
    } catch (err) {
      setError(err.message);
      console.error('Erro ao carregar pró-labore:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatarMoeda = (valor) => {
    if (valor === null || valor === undefined) return 'R$ 0,00';
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  };

  const formatarMes = (mes) => {
    const [ano, mesNum] = mes.split('-');
    const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    return `${meses[parseInt(mesNum) - 1]}/${ano}`;
  };

  const calcularTotais = () => {
    return dados.reduce((acc, mes) => ({
      proLaboreBruto: acc.proLaboreBruto + (mes.proLaboreBruto || 0),
      inssPessoal: acc.inssPessoal + (mes.inssPessoal || 0),
      inssPatronal: acc.inssPatronal + (mes.inssPatronal || 0),
      inssTotal: acc.inssTotal + (mes.inssTotal || 0),
      proLaboreLiquido: acc.proLaboreLiquido + (mes.proLaboreLiquido || 0),
      lucroFinal: acc.lucroFinal + (mes.lucroFinal || 0)
    }), {
      proLaboreBruto: 0,
      inssPessoal: 0,
      inssPatronal: 0,
      inssTotal: 0,
      proLaboreLiquido: 0,
      lucroFinal: 0
    });
  };

  const totais = calcularTotais();

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <h1>Erro</h1>
        <p style={{ color: 'red' }}>{error}</p>
        <button onClick={() => navigate('/contabilidade')}>← Voltar</button>
      </div>
    );
  }

  if (socios.length === 0) {
    return (
      <div style={{ padding: '20px' }}>
        <h1>Pró-labore</h1>
        <p>Nenhum sócio administrador encontrado. Por favor, configure um sócio com função "Administrador".</p>
        <button onClick={() => navigate('/contabilidade')}>← Voltar</button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Pró-labore {ano} - {socioSelecionado?.nome}</h1>
        <button 
          onClick={() => navigate('/contabilidade')}
          style={{
            padding: '10px 20px',
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          ← Voltar
        </button>
      </div>

      <div style={{ marginBottom: '20px', display: 'flex', gap: '15px', alignItems: 'center' }}>
        <div>
          <label style={{ marginRight: '10px' }}>Sócio Administrador:</label>
          <select 
            value={socioSelecionado?.id || ''} 
            onChange={(e) => {
              const socio = socios.find(s => s.id === Number(e.target.value));
              setSocioSelecionado(socio);
            }}
            style={{ padding: '5px 10px' }}
          >
            {socios.map(s => (
              <option key={s.id} value={s.id}>
                {s.nome} ({(s.percentual * 100).toFixed(2)}%)
              </option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ marginRight: '10px' }}>Ano:</label>
          <select 
            value={ano} 
            onChange={(e) => setAno(Number(e.target.value))}
            style={{ padding: '5px 10px' }}
          >
            {[2024, 2025, 2026].map(y => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>

        <button 
          onClick={carregarDados}
          style={{
            padding: '5px 15px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          🔄 Atualizar
        </button>
      </div>

      {/* Cards com resumo anual */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginBottom: '30px' }}>
        <div style={{ padding: '15px', backgroundColor: '#fff3e0', borderRadius: '8px', border: '1px solid #ffb74d' }}>
          <div style={{ fontSize: '14px', color: '#f57c00', marginBottom: '5px' }}>Pró-labore Bruto</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#e65100' }}>{formatarMoeda(totais.proLaboreBruto)}</div>
        </div>

        <div style={{ padding: '15px', backgroundColor: '#ffebee', borderRadius: '8px', border: '1px solid #ef5350' }}>
          <div style={{ fontSize: '14px', color: '#c62828', marginBottom: '5px' }}>INSS Total</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#b71c1c' }}>{formatarMoeda(totais.inssTotal)}</div>
          <div style={{ fontSize: '11px', color: '#666', marginTop: '5px' }}>
            Pessoal: {formatarMoeda(totais.inssPessoal)} | Patronal: {formatarMoeda(totais.inssPatronal)}
          </div>
        </div>

        <div style={{ padding: '15px', backgroundColor: '#e3f2fd', borderRadius: '8px', border: '1px solid #90caf9' }}>
          <div style={{ fontSize: '14px', color: '#1976d2', marginBottom: '5px' }}>Pró-labore Líquido</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#0d47a1' }}>{formatarMoeda(totais.proLaboreLiquido)}</div>
        </div>
        <div style={{ padding: '15px', backgroundColor: '#e8f5e9', borderRadius: '8px', border: '1px solid #66bb6a' }}>
          <div style={{ fontSize: '14px', color: '#2e7d32', marginBottom: '5px' }}>Lucro {socioSelecionado?.nome.split(' ')[0]} (líquido)</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#1b5e20' }}>{formatarMoeda(totais.lucroFinal)}</div>
          <div style={{ fontSize: '11px', color: '#4b5563', marginTop: '5px' }}>Excedente líquido acima de pró‑labore (salário mínimo × 0,89)</div>
        </div>
      </div>

      {loading ? (
        <p>Carregando dados...</p>
      ) : dados.length === 0 ? (
        <p>Nenhum mês com pró-labore encontrado para o ano de {ano}.</p>
      ) : (
        <>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
              <thead>
                <tr style={{ backgroundColor: '#1f2937', color: 'white' }}>
                  <th style={{ padding: '12px 8px', textAlign: 'left', borderBottom: '2px solid #374151' }}>Mês</th>
                  <th style={{ padding: '12px 8px', textAlign: 'right', borderBottom: '2px solid #374151' }}>% Contrib.</th>
                  <th style={{ padding: '12px 8px', textAlign: 'right', borderBottom: '2px solid #374151' }}>Valor Bruto</th>
                  <th style={{ padding: '12px 8px', textAlign: 'right', borderBottom: '2px solid #374151' }}>INSS (Pessoa)</th>
                  <th style={{ padding: '12px 8px', textAlign: 'right', borderBottom: '2px solid #374151' }}>INSS (Patronal)</th>
                  <th style={{ padding: '12px 8px', textAlign: 'right', borderBottom: '2px solid #374151' }}>Pró-Labore Líquido</th>
                  <th style={{ padding: '12px 8px', textAlign: 'right', borderBottom: '2px solid #374151' }}>Lucro {socioSelecionado?.nome.split(' ')[0]} (líquido)</th>
                </tr>
              </thead>
              <tbody>
                {dados.map((mes, index) => (
                  <tr key={mes.mes} style={{ backgroundColor: index % 2 === 0 ? '#f9fafb' : 'white' }}>
                    <td style={{ padding: '10px 8px', borderBottom: '1px solid #e5e7eb' }}>{formatarMes(mes.mes)}</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right', borderBottom: '1px solid #e5e7eb', color: '#6366f1' }}>{mes.percentualContribuicao?.toFixed(2)}%</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }}>{formatarMoeda(mes.proLaboreBruto)}</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }}>{formatarMoeda(mes.inssPessoal)}</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }}>{formatarMoeda(mes.inssPatronal)}</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right', borderBottom: '1px solid #e5e7eb', fontWeight: 'bold', color: '#0d47a1' }}>{formatarMoeda(mes.proLaboreLiquido)}</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right', borderBottom: '1px solid #e5e7eb', fontWeight: 'bold', color: '#059669' }}>{formatarMoeda(mes.lucroFinal)}</td>
                  </tr>
                ))}
                <tr style={{ backgroundColor: '#f3f4f6', fontWeight: 'bold' }}>
                  <td style={{ padding: '12px 8px', borderTop: '2px solid #9ca3af' }}>TOTAL</td>
                  <td style={{ padding: '12px 8px', textAlign: 'right', borderTop: '2px solid #9ca3af' }}>-</td>
                  <td style={{ padding: '12px 8px', textAlign: 'right', borderTop: '2px solid #9ca3af' }}>{formatarMoeda(totais.proLaboreBruto)}</td>
                  <td style={{ padding: '12px 8px', textAlign: 'right', borderTop: '2px solid #9ca3af' }}>{formatarMoeda(totais.inssPessoal)}</td>
                  <td style={{ padding: '12px 8px', textAlign: 'right', borderTop: '2px solid #9ca3af' }}>{formatarMoeda(totais.inssPatronal)}</td>
                  <td style={{ padding: '12px 8px', textAlign: 'right', borderTop: '2px solid #9ca3af', color: '#0d47a1' }}>{formatarMoeda(totais.proLaboreLiquido)}</td>
                  <td style={{ padding: '12px 8px', textAlign: 'right', borderTop: '2px solid #9ca3af', color: '#059669' }}>{formatarMoeda(totais.lucroFinal)}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#fef3c7', borderRadius: '8px', fontSize: '13px' }}>
            <p style={{ margin: '0 0 10px 0' }}><strong>📝 Como funciona o cálculo:</strong></p>
            <ul style={{ margin: 0, paddingLeft: '20px' }}>
              <li><strong>Lucro Bruto:</strong> Entradas - Despesas (exceto INSS)</li>
              <li><strong>Percentual de Contribuição:</strong> Calculado com base nas entradas reais do mês</li>
              <li><strong>Pró-labore do Administrador:</strong> 5% do lucro + 85% do lucro × % contrib. (máximo: salário mínimo)</li>
              <li><strong>INSS Total:</strong> 31% do pró-labore (11% pessoal + 20% patronal)</li>
              <li><strong>Lucro Líquido (Previsão da Operação):</strong> Lucro Bruto - INSS Total (o pró-labore NÃO é despesa)</li>
              <li><strong>Lucro Final do Sócio:</strong> Pró-labore Líquido + Lucro Disponível (para não-admin) ou apenas Pró-labore Líquido (para admin)</li>
              <li style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #facc15' }}>
                <strong>⚠️ Importante:</strong> O pró-labore não é contabilizado como despesa na Previsão da Operação, mas sim como distribuição de lucro. 
                Apenas os encargos (INSS) são despesas.
              </li>
            </ul>
          </div>
        </>
      )}
    </div>
  );
}

export default ProLabore;
