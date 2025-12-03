# Implementação do Backend de Contabilidade - Resumo Completo

## 📋 Visão Geral

Sistema completo de contabilidade implementado com FastAPI + React, incluindo:
- CRUD completo para sócios, aportes, entradas e despesas
- Motor de operações contábeis padronizadas
- Geração automática de lançamentos contábeis
- DMPL (Demonstração das Mutações do Patrimônio Líquido)
- DFC (Demonstração do Fluxo de Caixa - método direto)
- Previsões operacionais mensais
- Dashboard com KPIs em tempo real

## 🗂️ Arquivos Criados/Modificados

### Backend

#### 1. `database/crud_contabilidade.py` (NOVO - ~1200 linhas)
**Responsabilidades:**
- CRUD de Sócio (create, read, update, delete)
- CRUD de Aporte de Capital (com atualização automática de capital_social)
- CRUD de Entrada e Despesa (previsões)
- Configuração e Simples Nacional
- **Motor de Operações Contábeis:**
  - `executar_operacao`: Dispatcher para 8 operações padronizadas
  - `_executar_rec_hon`, `_executar_reservar_fundo`, `_executar_pro_labore`, etc.
  - Cada operação gera lançamentos via `crud_plano_contas.criar_lancamento`
- **Validações:** `validar_equacao_contabil` (Ativo = Passivo + PL)
- **Previsões:** consolidar/desconsolidar `PrevisaoOperacaoMensal`
- **DMPL:** `calcular_dmpl` - agrega movimentações de contas PL (código 3.*)
- **DFC:** `calcular_dfc` - método direto, classifica movimentações de caixa (1.1.1)

**Códigos de Conta Utilizados:**
```python
# Ativo
1.1.1 - Caixa e Bancos
1.1.3 - Adiantamentos a Sócios

# Passivo
2.1.5 - INSS a Pagar
2.1.6 - Lucros a Pagar

# Patrimônio Líquido
3.1 - Capital Social
3.2 - Reservas de Lucros
3.3 - Lucros Acumulados

# Receitas
4.1.1 - Receita de Honorários

# Despesas
5.1.1 - Pró-labore
5.1.3 - Encargos Sociais (INSS Patronal)
5.2 - Despesas Operacionais (subconta 5.2.x criada dinamicamente)
```

#### 2. `backend/schemas.py` (MODIFICADO)
**Adições:**
- `DMPLResponse`: Estrutura para DMPL
  - `SaldoPLResponse` (capital_social, reservas, lucros_acumulados)
  - `MovimentacaoPLResponse` (nome_operacao, capital_social, reservas, lucros_acumulados)
- `DFCResponse`: Estrutura para DFC
  - `FluxoOperacionalResponse` (receitas, despesas_pessoal, despesas_operacionais, impostos_pagos)
  - `FluxoInvestimentoResponse` (aquisicoes_imobilizado, alienacoes_imobilizado)
  - `FluxoFinanciamentoResponse` (aportes_capital, distribuicao_lucros, adiantamentos_socios)

#### 3. `backend/main.py` (MODIFICADO)
**Alterações:**
- Importado `Header` de fastapi
- **POST `/contabilidade/operacoes/executar`:**
  - Aceita header `X-User-Id` para rastrear criador
  - Passa `criado_por_id` para `crud_contabilidade.executar_operacao`
- **GET `/contabilidade/dmpl`:**
  - Params: `ano_inicio`, `ano_fim`
  - Response: `schemas.DMPLResponse`
- **GET `/contabilidade/dfc`:**
  - Params: `mes`, `ano`
  - Response: `schemas.DFCResponse`

#### 4. `database/init_operacoes.py` (NOVO)
**Responsabilidade:** Seed script para popular tabela `Operacao` com 8 operações padronizadas.

**Operações:**
1. `REC_HON` - Receber Honorários
2. `RESERVAR_FUNDO` - Reservar Fundo
3. `PRO_LABORE` - Pró-labore (bruto)
4. `INSS_PATRONAL` - INSS Patronal
5. `PAGAR_INSS` - Pagar INSS
6. `DISTRIBUIR_LUCROS` - Distribuir Lucros
7. `PAGAR_DESPESA_FUNDO` - Pagar Despesa via Fundo
8. `BAIXAR_FUNDO` - Baixa do Fundo

### Frontend

#### 1. `frontend/react-app/src/pages/Contabilidade.jsx` (NOVO)
**Responsabilidade:** Dashboard principal do módulo de contabilidade.

**Recursos:**
- **KPIs:** Saldo Caixa, Patrimônio Líquido, Lucro do Mês
- **Navegação:** Cards para 10 submódulos:
  - Operações Contábeis
  - Balanço Patrimonial
  - DMPL
  - DFC
  - Lucros & Dividendos
  - Pró-labore
  - Lançamentos
  - Plano de Contas
  - Sócios
  - Config Simples

#### 2. `frontend/react-app/src/pages/OperacoesContabeis.jsx` (MODIFICADO)
**Alteração:** `API_BASE_URL` mudado de `'http://localhost:8000/api'` para `'/api'` (usa proxy Vite)

## 🔧 Arquitetura do Sistema

### Fluxo de Operações Contábeis

```
Frontend (OperacoesContabeis.jsx)
    ↓ POST /contabilidade/operacoes/executar
Backend (main.py) → crud_contabilidade.executar_operacao
    ↓
Dispatcher → _executar_[operacao] (REC_HON, PRO_LABORE, etc.)
    ↓
crud_plano_contas.criar_lancamento (gera LancamentoContabil)
    ↓
Database: tabelas OperacaoContabil + LancamentoContabil
```

### Separação de Conceitos

**Entradas/Despesas:**
- Apenas previsões
- NÃO geram lançamentos contábeis
- Alimentam `PrevisaoOperacaoMensal`
- Exibem projeção de fechamento do mês

**Operações Contábeis:**
- Eventos contábeis reais
- Geram `LancamentoContabil` via partidas dobradas
- Base para DMPL, DFC, Balanço
- 8 operações padronizadas com validações

### DMPL - Demonstração das Mutações do Patrimônio Líquido

**Fonte de dados:** `LancamentoContabil` WHERE (conta_debito.tipo='PL' OR conta_credito.tipo='PL')

**Lógica:**
1. Calcula saldo inicial das contas PL (3.1, 3.2, 3.3)
2. Agrupa movimentações por operação
3. Calcula impacto líquido em cada subconta PL
4. Retorna: saldo_inicial, movimentacoes[], saldo_final, variacao_%

**Subcontas PL:**
- `capital_social` (3.1)
- `reservas` (3.2)
- `lucros_acumulados` (3.3)

### DFC - Demonstração do Fluxo de Caixa (Método Direto)

**Fonte de dados:** `LancamentoContabil` WHERE (conta_debito_id=caixa_id OR conta_credito_id=caixa_id)

**Classificação por contraparte:**

**Fluxos Operacionais:**
- Receitas (tipo='Receita')
- Despesas de Pessoal (5.1.*)
- Despesas Operacionais (5.2.*)
- Impostos/INSS (2.1.4, 2.1.5)

**Fluxos de Investimento:**
- Imobilizado/Intangível (1.2.*)

**Fluxos de Financiamento:**
- Aportes de Capital (3.1)
- Distribuição de Lucros (3.3, 3.4)
- Adiantamentos a Sócios (1.1.3)

## 🚀 Instruções de Teste

### 1. Inicializar Plano de Contas

```bash
cd c:\PythonProjects\GESTOR_LS
python database\init_plano_contas.py
```

**Saída esperada:** Plano de contas completo (contas 1.* a 5.*) criado.

### 2. Seed de Operações

```bash
python database\init_operacoes.py
```

**Saída esperada:** 8 operações cadastradas (REC_HON a BAIXAR_FUNDO).

### 3. Iniciar Backend

```bash
cd c:\PythonProjects\GESTOR_LS
python backend\main.py
```

**Verificar:** Backend rodando em `http://127.0.0.1:8000`

### 4. Iniciar Frontend

```bash
cd c:\PythonProjects\GESTOR_LS\frontend\react-app
npm run dev
```

**Verificar:** Frontend rodando em `http://localhost:5173`

### 5. Testar Dashboard

1. Acesse: `http://localhost:5173/contabilidade`
2. **Verificar:** Dashboard carrega com KPIs (podem estar zerados se não houver lançamentos)
3. **Clicar:** Em cada card de navegação para confirmar roteamento

### 6. Testar Operações Contábeis

1. Acesse: `http://localhost:5173/contabilidade/operacoes`
2. **Criar Sócio:**
   - POST `/contabilidade/socios`
   - Dados: nome, cpf, percentual_participacao
3. **Executar REC_HON (Receber Honorários):**
   - Operação: "Receber Honorários"
   - Valor: 10000
   - Data: hoje
   - Descrição: "Honorários cliente X"
   - Sócio: (opcional)
4. **Verificar:** Histórico exibe operação com 1 lançamento (D-1.1.1/C-4.1.1)
5. **Executar RESERVAR_FUNDO:**
   - Valor: 1000
   - Verificar: lançamento D-3.3/C-3.2
6. **Executar PRO_LABORE:**
   - Valor: 5000 (bruto)
   - Verificar: 2 lançamentos (89% líquido para caixa + 11% INSS a pagar)

### 7. Testar DMPL

1. Acesse: `http://localhost:5173/contabilidade/dmpl`
2. **Filtrar:** Ano início = 2025, Ano fim = 2025
3. **Verificar:**
   - Saldo Inicial PL
   - Movimentações por operação (REC_HON, RESERVAR_FUNDO, etc.)
   - Saldo Final PL
   - Variação %

### 8. Testar DFC

1. Acesse: `http://localhost:5173/contabilidade/dfc`
2. **Filtrar:** Mês/Ano atual
3. **Verificar:**
   - Fluxo Operacional (receitas, despesas)
   - Fluxo de Investimento (se houver)
   - Fluxo de Financiamento (aportes, distribuições)
   - Saldo inicial/final de caixa

### 9. Testar Balanço

1. Acesse: `http://localhost:5173/contabilidade/balanco`
2. **Verificar:**
   - Ativo: Caixa (1.1.1) com saldo correto
   - Passivo: INSS a Pagar (2.1.5) se houver pró-labore
   - PL: Capital Social, Reservas, Lucros Acumulados
   - Equação: Ativo = Passivo + PL

### 10. Testar Validações

**PAGAR_INSS sem saldo:**
1. Tentar executar PAGAR_INSS com valor > saldo INSS a Pagar
2. **Esperado:** Erro 400 "Saldo insuficiente em INSS a Recolher"

**DISTRIBUIR_LUCROS sem saldo:**
1. Tentar distribuir lucros com valor > saldo Lucros Acumulados
2. **Esperado:** Erro 400 "Saldo insuficiente em Lucros Acumulados"

**BAIXAR_FUNDO sem saldo:**
1. Tentar baixar fundo com valor > saldo Reservas
2. **Esperado:** Erro 400 "Saldo insuficiente em Reservas"

## 🔍 Verificações de Integridade

### 1. Equação Contábil
**Query SQL:**
```sql
SELECT 
  SUM(CASE WHEN tipo='Ativo' THEN saldo ELSE 0 END) as total_ativo,
  SUM(CASE WHEN tipo='Passivo' THEN saldo ELSE 0 END) as total_passivo,
  SUM(CASE WHEN tipo='PL' THEN saldo ELSE 0 END) as total_pl
FROM plano_de_contas
JOIN lancamentos_contabeis ...
```
**Esperado:** `total_ativo = total_passivo + total_pl`

### 2. Partidas Dobradas
**Query SQL:**
```sql
SELECT 
  data,
  SUM(CASE WHEN conta_debito_id IS NOT NULL THEN valor ELSE 0 END) as total_debitos,
  SUM(CASE WHEN conta_credito_id IS NOT NULL THEN valor ELSE 0 END) as total_creditos
FROM lancamentos_contabeis
GROUP BY data
```
**Esperado:** `total_debitos = total_creditos` para cada data

### 3. Saldo Caixa = Soma Lançamentos
**Verificar:** Saldo calculado em `/balanco-patrimonial` conta 1.1.1 deve bater com soma de todos os lançamentos de caixa considerando débitos/créditos e natureza devedora.

## 📝 Próximos Passos (Opcionais)

### 1. Autenticação
- Implementar sistema de login/JWT
- Popular `X-User-Id` header automaticamente via interceptor axios
- Restringir rotas por permissão

### 2. Classificação de Contas
- Adicionar campo `classificacao` em PlanoDeContas
- Permitir usuário categorizar contas customizadas

### 3. Códigos-Chave para Operações
- Criar tabela `CodigoChaveOperacao` vinculando operação → conta específica
- Permitir usuário customizar contas usadas em cada operação

### 4. Auditoria
- Tabela de audit log para rastrear alterações
- Impedir exclusão de lançamentos (apenas cancelamento)

### 5. Relatórios Adicionais
- DRE (Demonstração do Resultado do Exercício)
- Análise Vertical/Horizontal
- Gráficos de evolução patrimonial

### 6. Exportação
- PDF para DMPL, DFC, Balanço
- Excel para análises

## 🐛 Troubleshooting

### Erro: "Conta não encontrada"
**Causa:** Plano de contas não inicializado.
**Solução:** `python database\init_plano_contas.py`

### Erro: "Operação não encontrada"
**Causa:** Tabela Operacao vazia.
**Solução:** `python database\init_operacoes.py`

### KPIs não carregam no dashboard
**Causa:** Sem lançamentos contábeis.
**Solução:** Executar pelo menos 1 operação (REC_HON) para popular caixa.

### DMPL/DFC vazios
**Causa:** Nenhuma operação executada no período filtrado.
**Solução:** Verificar filtros de data e executar operações.

### Frontend não conecta ao backend
**Causa:** Backend não está rodando ou proxy Vite mal configurado.
**Solução:** 
1. Verificar backend em `http://127.0.0.1:8000/docs`
2. Verificar `vite.config.mjs` proxy `/api` → `http://127.0.0.1:8000`

## 📚 Referências

- **OPERACOES_CONTABEIS.md**: Especificação detalhada das 8 operações
- **database/models.py**: Schemas SQLAlchemy
- **database/init_plano_contas.py**: Estrutura do plano de contas padrão
- **FastAPI Docs**: `http://127.0.0.1:8000/docs` (Swagger UI)

---

**Status:** ✅ Implementação completa
**Data:** 2025
**Desenvolvedor:** GitHub Copilot + User
