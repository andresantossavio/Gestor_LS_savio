# Validações de Saldo em Caixa

## Visão Geral

O sistema agora valida automaticamente se há saldo suficiente nas contas de caixa **antes** de executar qualquer operação que movimente dinheiro. Se o saldo for insuficiente, a operação é bloqueada e uma mensagem detalhada é exibida ao usuário.

## Operações com Validação de Saldo

### 1. **APLICAR_RESERVA_CDB** (Aplicar Reserva em CDB)
- **Conta validada**: `1.1.1.1` (Caixa Corrente)
- **Mensagem de erro**:
  ```
  💰 Saldo insuficiente em Caixa Corrente para aplicar em CDB.
  Saldo disponível: R$ X,XX
  Valor solicitado: R$ Y,YY
  Faltam: R$ Z,ZZ
  
  💡 Dica: Separe os valores obrigatórios (INSS, Simples, Pró-labore) antes de aplicar em CDB.
  ```

### 2. **SEPARAR_INSS** (Separar Caixa para INSS)
- **Conta validada**: `1.1.1.1` (Caixa Corrente)
- **Mensagem de erro**:
  ```
  💰 Saldo insuficiente em Caixa Corrente para separar INSS.
  Saldo disponível: R$ X,XX
  Valor solicitado: R$ Y,YY
  Faltam: R$ Z,ZZ
  
  💡 Dica: Execute REC_HON (Receber Honorários) primeiro para ter saldo disponível.
  ```

### 3. **SEPARAR_SIMPLES** (Separar Caixa para Simples Nacional)
- **Conta validada**: `1.1.1.1` (Caixa Corrente)
- **Mensagem de erro**:
  ```
  💰 Saldo insuficiente em Caixa Corrente para separar Simples Nacional.
  Saldo disponível: R$ X,XX
  Valor solicitado: R$ Y,YY
  Faltam: R$ Z,ZZ
  
  💡 Dica: Execute REC_HON (Receber Honorários) primeiro para ter saldo disponível.
  ```

### 4. **SEPARAR_PRO_LABORE** (Separar Caixa para Pró-labore)
- **Conta validada**: `1.1.1.1` (Caixa Corrente)
- **Mensagem de erro**:
  ```
  💰 Saldo insuficiente em Caixa Corrente para separar Pró-labore.
  Saldo disponível: R$ X,XX
  Valor solicitado: R$ Y,YY
  Faltam: R$ Z,ZZ
  
  💡 Dica: Execute REC_HON (Receber Honorários) primeiro para ter saldo disponível.
  ```

### 5. **PAGAR_INSS** (Pagar INSS com Caixa Reservado)
- **Contas validadas**:
  1. `2.1.2.2` (INSS a Recolher) - Valida se há obrigação provisionada
  2. `1.1.1.2` (Caixa Reservado INSS) - Valida se há dinheiro separado
- **Mensagem de erro (obrigação)**:
  ```
  📋 Obrigação insuficiente em INSS a Recolher.
  Saldo da obrigação: R$ X,XX
  Valor solicitado: R$ Y,YY
  
  💡 Dica: Execute INSS_PESSOAL ou INSS_PATRONAL antes de pagar o INSS.
  ```
- **Mensagem de erro (caixa)**:
  ```
  💰 Saldo insuficiente em Caixa Reservado - INSS.
  Saldo disponível: R$ X,XX
  Valor solicitado: R$ Y,YY
  Faltam: R$ Z,ZZ
  
  💡 Dica: Execute SEPARAR_INSS antes de pagar o INSS.
  ```

### 6. **PAGAR_SIMPLES** (Pagar Simples Nacional com Caixa Reservado)
- **Contas validadas**:
  1. `2.1.2.1` (Simples a Recolher) - Valida se há obrigação provisionada
  2. `1.1.1.3` (Caixa Reservado Simples) - Valida se há dinheiro separado
- **Mensagem de erro (obrigação)**:
  ```
  📋 Obrigação insuficiente em Simples a Recolher.
  Saldo da obrigação: R$ X,XX
  Valor solicitado: R$ Y,YY
  
  💡 Dica: Execute PROVISIONAR_SIMPLES antes de pagar o Simples Nacional.
  ```
- **Mensagem de erro (caixa)**:
  ```
  💰 Saldo insuficiente em Caixa Reservado - Simples Nacional.
  Saldo disponível: R$ X,XX
  Valor solicitado: R$ Y,YY
  Faltam: R$ Z,ZZ
  
  💡 Dica: Execute SEPARAR_SIMPLES antes de pagar o Simples Nacional.
  ```

### 7. **PAGAR_PRO_LABORE** (Pagar Pró-labore com Caixa Reservado)
- **Contas validadas**:
  1. `2.1.3.1` (Pró-labore a Pagar) - Valida se há obrigação provisionada
  2. `1.1.1.4` (Caixa Reservado Pró-labore) - Valida se há dinheiro separado
- **Mensagem de erro (obrigação)**:
  ```
  📋 Obrigação insuficiente em Pró-labore a Pagar.
  Saldo da obrigação: R$ X,XX
  Valor solicitado: R$ Y,YY
  
  💡 Dica: Execute PRO_LABORE (provisão) antes de pagar o pró-labore.
  ```
- **Mensagem de erro (caixa)**:
  ```
  💰 Saldo insuficiente em Caixa Reservado - Pró-labore.
  Saldo disponível: R$ X,XX
  Valor solicitado: R$ Y,YY
  Faltam: R$ Z,ZZ
  
  💡 Dica: Execute SEPARAR_PRO_LABORE antes de pagar o pró-labore.
  ```

### 8. **DISTRIBUIR_LUCROS** (Distribuir Lucros aos Sócios)
- **Contas validadas**:
  1. `3.3` (Lucros Acumulados) - Valida se há lucro disponível
  2. `1.1.1.1` (Caixa Corrente) - Valida se há dinheiro para distribuir
- **Mensagem de erro (lucros)**:
  ```
  Saldo insuficiente em Lucros Acumulados.
  Saldo: R$ X,XX
  Valor: R$ Y,YY
  ```
- **Mensagem de erro (caixa)**:
  ```
  💰 Saldo insuficiente em Caixa Corrente para distribuir lucros.
  Saldo disponível: R$ X,XX
  Valor solicitado: R$ Y,YY
  Faltam: R$ Z,ZZ
  ```

### 9. **PAGAR_DESPESA_FUNDO** (Pagar Despesa Operacional)
- **Conta validada**: `1.1.1.1` (Caixa Corrente)
- **Mensagem de erro**:
  ```
  💰 Saldo insuficiente em Caixa Corrente para pagar despesa.
  Saldo disponível: R$ X,XX
  Valor solicitado: R$ Y,YY
  Faltam: R$ Z,ZZ
  ```

### 10. **RESGATAR_CDB_RESERVA** (Resgatar CDB da Reserva)
- **Contas validadas**:
  1. `1.1.1.5` (Aplicação CDB) - Valida se há investimento para resgatar
  2. `3.2.1.{socio_id}` (Reserva Legal do Sócio) - Valida se há reserva constituída
- **Mensagem de erro (CDB)**:
  ```
  💰 Saldo insuficiente em Aplicação CDB.
  Saldo disponível: R$ X,XX
  Valor solicitado: R$ Y,YY
  Faltam: R$ Z,ZZ
  
  💡 Dica: Execute APLICAR_RESERVA_CDB antes de resgatar.
  ```
- **Mensagem de erro (reserva)**:
  ```
  Saldo insuficiente na reserva de [Nome do Sócio].
  Saldo disponível: R$ X,XX
  Valor solicitado: R$ Y,YY
  ```

## Implementação Técnica

### Backend (`database/crud_contabilidade.py`)

Cada executor de operação que movimenta dinheiro contém:

```python
# 1. Buscar conta de caixa relevante
conta_caixa = _buscar_conta_por_codigo(db, "1.1.1.X")

# 2. Calcular saldo atual
saldo_caixa = crud_plano_contas.calcular_saldo_conta(db, conta_caixa.id)

# 3. Validar saldo
if saldo_caixa < valor:
    raise ValueError(
        f"💰 Saldo insuficiente em {conta_nome}.\n"
        f"Saldo disponível: R$ {saldo_caixa:.2f}\n"
        f"Valor solicitado: R$ {valor:.2f}\n"
        f"Faltam: R$ {valor - saldo_caixa:.2f}\n\n"
        f"💡 Dica: {dica_acao_corretiva}"
    )

# 4. Criar lançamento (só executa se validação passar)
lancamento = crud_plano_contas.criar_lancamento(...)
```

### Frontend (`frontend/react-app/src/pages/OperacoesContabeis.jsx`)

A mensagem de erro é exibida com formatação especial:

```jsx
{erro && (
    <div style={{
        padding: '16px 20px',
        backgroundColor: '#fee2e2',
        border: '1px solid #fecaca',
        borderRadius: '8px',
        color: '#991b1b',
        marginBottom: '16px',
        whiteSpace: 'pre-line',      // Preserva quebras de linha
        fontFamily: 'monospace',      // Fonte monoespaçada
        fontSize: '13px',
        lineHeight: '1.6'
    }}>
        {erro}
    </div>
)}
```

### API (`backend/main.py`)

O endpoint captura `ValueError` e retorna HTTP 400:

```python
@api_router.post("/contabilidade/operacoes/executar")
def executar_operacao_contabil(...):
    try:
        operacao_executada = crud_contabilidade.executar_operacao(...)
        return schemas.OperacaoContabilResponse(...)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Ordem Correta de Execução

Para evitar erros de saldo insuficiente, siga esta ordem:

### Mês Típico (Exemplo: Junho/2025)

1. **REC_HON** (Receber Honorários) → R$ 10.000,00
   - ✅ Credita `1.1.1.1` (Caixa Corrente)

2. **PROVISIONAR_SIMPLES** (Provisionar Simples) → R$ 600,00
   - ✅ Cria obrigação em `2.1.2.1`

3. **SEPARAR_SIMPLES** (Separar Caixa Simples) → R$ 600,00
   - ✅ Requer saldo em `1.1.1.1`

4. **SEPARAR_INSS** (Separar Caixa INSS) → R$ 900,00
   - ✅ Requer saldo em `1.1.1.1`

5. **SEPARAR_PRO_LABORE** (Separar Caixa Pró-labore) → R$ 2.000,00
   - ✅ Requer saldo em `1.1.1.1`

6. **APLICAR_RESERVA_CDB** (Aplicar em CDB) → R$ 5.000,00
   - ✅ Requer saldo em `1.1.1.1`

7. **INSS_PESSOAL** (Provisionar INSS Pessoal) → R$ 250,00
   - ✅ Cria obrigação em `2.1.2.2`

8. **INSS_PATRONAL** (Provisionar INSS Patronal) → R$ 650,00
   - ✅ Cria obrigação em `2.1.2.2`

9. **PRO_LABORE** (Provisionar Pró-labore) → R$ 2.000,00
   - ✅ Cria obrigação em `2.1.3.1`

### Pagamentos (Mês Seguinte)

10. **PAGAR_SIMPLES** → R$ 600,00
    - ✅ Requer obrigação em `2.1.2.1` + saldo em `1.1.1.3`

11. **PAGAR_INSS** → R$ 900,00
    - ✅ Requer obrigação em `2.1.2.2` + saldo em `1.1.1.2`

12. **PAGAR_PRO_LABORE** → R$ 2.000,00
    - ✅ Requer obrigação em `2.1.3.1` + saldo em `1.1.1.4`

## Benefícios

1. **Prevenção de Erros**: Impossível criar lançamentos com saldo negativo
2. **Clareza**: Usuário sabe exatamente por que a operação falhou
3. **Orientação**: Dicas sugerem qual operação executar primeiro
4. **Auditoria**: Sistema mantém integridade contábil sempre
5. **UX Melhorada**: Mensagens formatadas com emojis e valores precisos

## Regime de Competência

**Importante**: Estas validações aplicam-se ao **regime de caixa** (movimentação financeira real). As despesas e receitas seguem o **regime de competência**:

- ✅ **Provisionar despesa** (ex: `PROVISIONAR_SIMPLES`) → Não requer caixa
- ✅ **Pagar despesa** (ex: `PAGAR_SIMPLES`) → Requer caixa reservado
- ✅ **Despesa já registrada permanece** → Não diminui ao pagar (apenas muda passivo para caixa)

## Testando as Validações

### Cenário 1: Tentar separar INSS sem saldo
```
Caixa Corrente: R$ 500,00
SEPARAR_INSS: R$ 900,00

❌ Bloqueado:
💰 Saldo insuficiente em Caixa Corrente para separar INSS.
Saldo disponível: R$ 500,00
Valor solicitado: R$ 900,00
Faltam: R$ 400,00

💡 Dica: Execute REC_HON (Receber Honorários) primeiro.
```

### Cenário 2: Tentar pagar INSS sem provisão
```
INSS a Recolher: R$ 0,00
PAGAR_INSS: R$ 900,00

❌ Bloqueado:
📋 Obrigação insuficiente em INSS a Recolher.
Saldo da obrigação: R$ 0,00
Valor solicitado: R$ 900,00

💡 Dica: Execute INSS_PESSOAL ou INSS_PATRONAL antes.
```

### Cenário 3: Tentar pagar INSS sem caixa reservado
```
INSS a Recolher: R$ 900,00
Caixa Reservado INSS: R$ 0,00
PAGAR_INSS: R$ 900,00

❌ Bloqueado:
💰 Saldo insuficiente em Caixa Reservado - INSS.
Saldo disponível: R$ 0,00
Valor solicitado: R$ 900,00
Faltam: R$ 900,00

💡 Dica: Execute SEPARAR_INSS antes de pagar o INSS.
```

---

**Data da Implementação**: 04/12/2025  
**Versão**: 2.0  
**Status**: ✅ Implementado e Testado
