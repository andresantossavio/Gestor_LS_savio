# Sistema de Operações Contábeis Padronizadas

## Visão Geral

Este sistema foi implementado para simplificar o registro de operações contábeis através de 8 operações padronizadas que geram automaticamente os lançamentos contábeis correspondentes.

## Operações Disponíveis

### 1. Receber honorários (REC_HON)
**Lançamento:** D-Caixa / C-Receita  
**Uso:** Registrar recebimento de honorários de clientes.

### 2. Reservar fundo (RESERVAR_FUNDO)
**Lançamento:** D-Lucros Acum. / C-Reserva  
**Uso:** Transferir parte dos lucros para fundo de reserva (geralmente 10%).

### 3. Pró-labore (bruto) (PRO_LABORE)
**Lançamentos:**
- D-Despesa Pró-labore / C-Caixa (89% líquido)
- D-Despesa Pró-labore / C-INSS a Recolher (11%)

**Uso:** Registrar pagamento de pró-labore com desconto de INSS de 11%.

### 4. INSS patronal (INSS_PATRONAL)
**Lançamento:** D-Despesa INSS patronal / C-INSS a Recolher  
**Uso:** Provisionar INSS patronal (20% sobre pró-labore).

### 5. Pagar INSS (PAGAR_INSS)
**Lançamento:** D-INSS a Recolher / C-Caixa  
**Uso:** Efetuar pagamento do INSS acumulado.  
**Validação:** Verifica se há saldo suficiente em "INSS a Recolher".

### 6. Distribuir lucros (DISTRIBUIR_LUCROS)
**Lançamento:** D-Lucros Acum. / C-Caixa  
**Uso:** Distribuir lucros aos sócios.  
**Validação:** Verifica se há saldo suficiente em "Lucros Acumulados".

### 7. Pagar despesa via fundo (PAGAR_DESPESA_FUNDO)
**Lançamento:** D-Outras Despesas / C-Caixa  
**Uso:** Registrar pagamento de despesas diversas.

### 8. Baixa do fundo (BAIXAR_FUNDO)
**Lançamento:** D-Reserva / C-Lucros Acum.  
**Uso:** Transferir recursos do fundo de reserva de volta para lucros.  
**Validação:** Verifica se há saldo suficiente em "Reserva".

## Como Usar

### Interface Web

1. Acesse **Contabilidade > Operações** no menu
2. Selecione a operação desejada no formulário
3. Preencha:
   - **Valor:** Montante da operação (em R$)
   - **Data:** Data da operação
   - **Descrição:** Histórico opcional
   - **Sócio:** Apenas para operações PRO_LABORE e DISTRIBUIR_LUCROS (opcional)
4. Clique em **Executar Operação**

### Histórico

- Filtrar operações por mês de referência
- Expandir cada operação para ver os lançamentos contábeis gerados
- Cancelar operações (remove os lançamentos contábeis)

### Via API

#### Listar operações disponíveis
```bash
GET /api/contabilidade/operacoes
```

#### Executar operação
```bash
POST /api/contabilidade/operacoes/executar
Content-Type: application/json

{
  "operacao_codigo": "REC_HON",
  "valor": 5000.00,
  "data": "2025-12-03",
  "descricao": "Honorários caso XYZ",
  "socio_id": null
}
```

#### Listar histórico
```bash
GET /api/contabilidade/operacoes/historico?mes_referencia=2025-12
```

#### Cancelar operação
```bash
DELETE /api/contabilidade/operacoes/{operacao_id}
```

## Estrutura do Banco de Dados

### Tabela `operacoes`
- **id:** Identificador único
- **codigo:** Código da operação (REC_HON, PRO_LABORE, etc.)
- **nome:** Nome descritivo
- **descricao:** Descrição detalhada dos lançamentos
- **ativo:** Se a operação está disponível
- **ordem:** Ordem de exibição

### Tabela `operacoes_contabeis`
- **id:** Identificador único
- **operacao_id:** FK para operação executada
- **data:** Data da operação
- **valor:** Valor da operação
- **descricao:** Histórico/descrição
- **mes_referencia:** Mês de competência (YYYY-MM)
- **socio_id:** FK para sócio (quando aplicável)
- **criado_por_id:** FK para usuário que executou
- **cancelado:** Se a operação foi cancelada

### Atualização em `lancamentos_contabeis`
- **operacao_contabil_id:** FK para a operação que gerou o lançamento

## Validações

As seguintes operações possuem validações de saldo:

- **PAGAR_INSS:** Verifica saldo em "INSS a Recolher"
- **DISTRIBUIR_LUCROS:** Verifica saldo em "Lucros Acumulados"
- **BAIXAR_FUNDO:** Verifica saldo em "Reserva"

Se não houver saldo suficiente, a operação retorna erro e não é executada.

## Plano de Contas Simplificado

Para usar este sistema, certifique-se que o plano de contas possui estas contas:

- **1.1** - Caixa
- **2.1** - INSS a Recolher
- **3.1** - Reserva (Fundo/Reserva)
- **3.2** - Lucros Acumulados
- **3.3** - Capital Social
- **4.1** - Receita
- **5.1** - Despesa Pró-labore
- **5.2** - Despesa INSS patronal
- **5.3** - Outras Despesas

## Exemplo de Fluxo Completo

```
1. Receber honorários (REC_HON)
   Valor: R$ 10.000,00
   → D-Caixa R$ 10.000 / C-Receita R$ 10.000

2. Reservar fundo (RESERVAR_FUNDO)
   Valor: R$ 1.000,00 (10% dos lucros)
   → D-Lucros Acum. R$ 1.000 / C-Reserva R$ 1.000

3. Pró-labore bruto (PRO_LABORE)
   Valor: R$ 3.000,00
   → D-Despesa PL R$ 2.670 / C-Caixa R$ 2.670 (89%)
   → D-Despesa PL R$ 330 / C-INSS Recolher R$ 330 (11%)

4. INSS patronal (INSS_PATRONAL)
   Valor: R$ 600,00 (20% sobre R$ 3.000)
   → D-Despesa INSS R$ 600 / C-INSS Recolher R$ 600

5. Pagar INSS (PAGAR_INSS)
   Valor: R$ 930,00 (R$ 330 + R$ 600)
   → D-INSS Recolher R$ 930 / C-Caixa R$ 930

6. Distribuir lucros (DISTRIBUIR_LUCROS)
   Valor: R$ 5.000,00
   → D-Lucros Acum. R$ 5.000 / C-Caixa R$ 5.000
```

## Troubleshooting

### Erro: "Contas contábeis não encontradas"
- Execute o script de inicialização do plano de contas
- Verifique se as contas 1.1, 2.1, 3.1, 3.2, 4.1, 5.1, 5.2, 5.3 existem

### Erro: "Saldo insuficiente"
- Verifique o balanço patrimonial
- Certifique-se que há saldo positivo na conta de origem

### Operação cancelada por engano
- Não é possível reverter o cancelamento
- Execute novamente a operação com os mesmos dados

## Migração

Para criar as tabelas e inicializar as operações:

```bash
python database/migrar_operacoes.py
```

Este script:
1. Cria as tabelas `operacoes` e `operacoes_contabeis`
2. Adiciona campo `operacao_contabil_id` em `lancamentos_contabeis`
3. Inicializa as 8 operações padronizadas
4. Verifica a estrutura criada

## Próximos Passos

1. Simplificar o plano de contas para usar apenas as 12 contas necessárias
2. Excluir lançamentos antigos que não sejam de integralização de capital
3. Migrar operações do sistema antigo para o novo formato
