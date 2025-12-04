import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import Header from '../components/Header'

const API_BASE_URL = '/api'

export default function Contabilidade() {
  const navigate = useNavigate()
  const [kpis, setKpis] = useState({
    saldoCaixa: null,
    patrimonioLiquido: null,
    lucroMes: null,
    loading: true,
    error: null
  })

  useEffect(() => {
    carregarKPIs()
  }, [])

  async function carregarKPIs() {
    try {
      const hoje = new Date()
      const mes = hoje.getMonth() + 1
      const ano = hoje.getFullYear()

      // Buscar saldo caixa e PL do balanço patrimonial
      const balanco = await axios.get(`${API_BASE_URL}/contabilidade/balanco-patrimonial`, {
        params: { mes, ano }
      })

      // Conta 1.1.1 = Caixa e Bancos
      const contaCaixa = balanco.data.ativo.circulante.find(c => c.codigo === '1.1.1')
      const saldoCaixa = contaCaixa ? contaCaixa.saldo : 0

      const patrimonioLiquido = balanco.data.patrimonio_liquido.total

      // Buscar lucro do mês
      const lucros = await axios.get(`${API_BASE_URL}/contabilidade/lucros`, {
        params: { mes, ano }
      })
      const lucroMes = lucros.data.lucro_liquido || 0

      setKpis({
        saldoCaixa,
        patrimonioLiquido,
        lucroMes,
        loading: false,
        error: null
      })
    } catch (error) {
      console.error('Erro ao carregar KPIs:', error)
      setKpis(prev => ({
        ...prev,
        loading: false,
        error: 'Erro ao carregar indicadores. Verifique se o plano de contas foi inicializado.'
      }))
    }
  }

  function formatarMoeda(valor) {
    if (valor === null || valor === undefined) return 'R$ -'
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor)
  }

  const cardStyle = {
    padding: '20px',
    borderRadius: '12px',
    textAlign: 'center',
    cursor: 'pointer',
    transition: 'transform 0.2s, box-shadow 0.2s',
    border: '2px solid transparent'
  }

  const cardHoverStyle = {
    transform: 'translateY(-4px)',
    boxShadow: '0 8px 16px rgba(0,0,0,0.1)'
  }

  const navCards = [
    { title: 'Operações Contábeis', path: '/contabilidade/operacoes', color: '#dbeafe', textColor: '#1e3a8a', icon: '⚙️', description: 'Executar lançamentos padronizados (pró-labore, INSS, etc.) e visualizar o histórico de operações.' },
    { title: 'Balanço Patrimonial', path: '/contabilidade/balanco', color: '#fef3c7', textColor: '#92400e', icon: '📊', description: 'Visualizar a posição financeira da empresa (Ativo, Passivo e Patrimônio Líquido).' },
    { title: 'DMPL', path: '/contabilidade/dmpl', color: '#e0e7ff', textColor: '#3730a3', icon: '📈', description: 'Demonstração das Mutações do Patrimônio Líquido. Mostra a variação do PL ao longo do tempo.' },
    { title: 'DFC', path: '/contabilidade/dfc', color: '#ddd6fe', textColor: '#5b21b6', icon: '💹', description: 'Demonstração dos Fluxos de Caixa. Mostra as entradas e saídas de caixa por atividade.' },
    { title: 'Lucros & Dividendos', path: '/contabilidade/lucros', color: '#d1fae5', textColor: '#065f46', icon: '💰', description: 'Analisar o resultado do exercício e a distribuição de lucros.' },
    { title: 'Pró-labore', path: '/contabilidade/pro-labore', color: '#fce7f3', textColor: '#831843', icon: '👤', description: 'Visualizar e gerenciar as retiradas dos sócios.' },
    { title: 'Entradas & Despesas', path: '/contabilidade/entradas-despesas', color: '#e5e7eb', textColor: '#1f2937', icon: '💵', description: 'Gerenciar a previsão de receitas e despesas futuras para projeção de caixa.' },
    { title: 'Plano de Contas', path: '/contabilidade/plano-contas', color: '#fed7aa', textColor: '#7c2d12', icon: '📋', description: 'Estrutura de contas usada para registrar todas as movimentações financeiras.' },
    { title: 'Sócios', path: '/contabilidade/socios', color: '#bfdbfe', textColor: '#1e40af', icon: '👥', description: 'Gerenciar os sócios da empresa e seus dados.' },
    { title: 'Config Simples', path: '/contabilidade/config-simples', color: '#c7d2fe', textColor: '#3730a3', icon: '⚙️', description: 'Configurar as faixas e alíquotas do Simples Nacional.' }
  ]

  return (
    <div className="content">
      <div className="card">
        <Header title="Contabilidade" />
      </div>

      {/* KPIs */}
      <div className="card">
        <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#374151' }}>Indicadores Principais</h3>
        {kpis.loading ? (
          <p style={{ textAlign: 'center', color: '#6b7280' }}>Carregando...</p>
        ) : kpis.error ? (
          <div style={{ padding: '20px', backgroundColor: '#fee2e2', borderRadius: '8px', color: '#991b1b', textAlign: 'center' }}>
            {kpis.error}
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
            <div style={{ padding: '20px', backgroundColor: '#dcfce7', borderRadius: '12px', textAlign: 'center' }}>
              <h4 style={{ margin: 0, color: '#14532d', fontSize: '1.8rem', fontWeight: '700' }}>
                {formatarMoeda(kpis.saldoCaixa)}
              </h4>
              <p style={{ margin: '8px 0 0 0', color: '#166534', fontWeight: '600' }}>Saldo em Caixa</p>
            </div>
            <div style={{ padding: '20px', backgroundColor: '#dbeafe', borderRadius: '12px', textAlign: 'center' }}>
              <h4 style={{ margin: 0, color: '#1e3a8a', fontSize: '1.8rem', fontWeight: '700' }}>
                {formatarMoeda(kpis.patrimonioLiquido)}
              </h4>
              <p style={{ margin: '8px 0 0 0', color: '#1e40af', fontWeight: '600' }}>Patrimônio Líquido</p>
            </div>
            <div style={{ padding: '20px', backgroundColor: '#fef3c7', borderRadius: '12px', textAlign: 'center' }}>
              <h4 style={{ margin: 0, color: '#92400e', fontSize: '1.8rem', fontWeight: '700' }}>
                {formatarMoeda(kpis.lucroMes)}
              </h4>
              <p style={{ margin: '8px 0 0 0', color: '#78350f', fontWeight: '600' }}>Lucro do Mês</p>
            </div>
          </div>
        )}
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <button
            onClick={carregarKPIs}
            style={{
              padding: '10px 20px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            🔄 Atualizar
          </button>
        </div>
      </div>

      {/* Navigation Cards */}
      <div className="card">
        <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#374151' }}>Módulos</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px' }}>
          {navCards.map((card, idx) => (
            <div
              key={idx}
              style={{ ...cardStyle, backgroundColor: card.color }}
              onClick={() => navigate(card.path)}
              title={card.description}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = cardHoverStyle.transform
                e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = 'none'
              }}
            >
              <div style={{ fontSize: '2.5rem', marginBottom: '8px' }}>{card.icon}</div>
              <p style={{ margin: 0, color: card.textColor, fontWeight: '700', fontSize: '0.95rem' }}>
                {card.title}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
