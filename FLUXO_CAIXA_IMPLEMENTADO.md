# Sistema de Gestão de Fluxo de Caixa - Implementação Completa

## 📊 Visão Geral

Este documento detalha o sistema de gestão de fluxo de caixa implementado no Gestor_LS, alinhado com o fluxo operacional real de um escritório de advocacia.

## 🏦 Estrutura de Contas de Caixa

A conta **1.1.1 Caixa e Bancos** foi transformada em conta **sintética** (não aceita lançamentos diretos), com as seguintes subcontas analíticas:

- **1.1.1.1 - Caixa Corrente**: Caixa operacional diário
- **1.1.1.2 - Caixa Reservado - INSS**: Valores separados para pagamento de INSS
- **1.1.1.3 - Caixa Reservado - Simples Nacional**: Valores separados para pagamento do Simples
- **1.1.1.4 - Caixa Reservado - Pró-labore**: Valores separados para pagamento de pró-labore
- **1.1.1.5 - Aplicação CDB - Reserva Legal**: Investimento da reserva legal de 10%

## 🔄 Fluxo Operacional Completo

### Fase 1: Recebimento e Provisão
1. **REC_HON** - Receber Honorários
   - D: 1.1.1.1 (Caixa Corrente)
   - C: 4.1.1 (Receita de Honorários)

2. **PROVISIONAR_SIMPLES** - Provisionar Simples Nacional
   - D: 5.3.1 (Despesa - Simples)
   - C: 2.1.2.1 (Simples a Recolher)

3. **PRO_LABORE** - Provisionar Pró-labore
   - D: 5.1.1 (Despesa - Pró-labore)
   - C: 2.1.3.1 (Pró-labore a Pagar)
   - **IMPORTANTE**: Esta operação apenas provisiona, não paga!

4. **INSS_PESSOAL** - Provisionar INSS Pessoal
   - D: 5.1.1 (Despesa - Pró-labore)
   - C: 2.1.2.2 (INSS a Recolher)

5. **INSS_PATRONAL** - Provisionar INSS Patronal
   - D: 5.1.3 (Encargos - INSS Patronal)
   - C: 2.1.2.2 (INSS a Recolher)

### Fase 2: Separação de Caixa (Movimentações Internas)
Estas operações **NÃO afetam a DRE**, apenas reorganizam o caixa:

6. **SEPARAR_SIMPLES** - Separar Dinheiro para Simples
   - D: 1.1.1.3 (Caixa Reservado - Simples)
   - C: 1.1.1.1 (Caixa Corrente)

7. **SEPARAR_INSS** - Separar Dinheiro para INSS
   - D: 1.1.1.2 (Caixa Reservado - INSS)
   - C: 1.1.1.1 (Caixa Corrente)

8. **SEPARAR_PRO_LABORE** - Separar Dinheiro para Pró-labore
   - D: 1.1.1.4 (Caixa Reservado - Pró-labore)
   - C: 1.1.1.1 (Caixa Corrente)

### Fase 3: Apuração e Reserva Legal
9. **APURAR_RESULTADO** - Apurar Resultado do Período
   - Se lucro: D: 4.9.9 (Conta Técnica) / C: 3.3 (Lucros Acumulados)
   - Se prejuízo: D: 3.3 (Lucros Acumulados) / C: 4.9.9 (Conta Técnica)
   - **IMPORTANTE**: Executar uma vez ao final do mês

10. **APLICAR_RESERVA_CDB** - Aplicar 10% em Reserva Legal
    - Exige informar o sócio
    - Lançamento 1: D: 3.3 (Lucros Acumulados) / C: 3.2.1.{socio_id} (Reserva - Sócio)
    - Lançamento 2: D: 1.1.1.5 (Aplicação CDB) / C: 1.1.1.1 (Caixa Corrente)

### Fase 4: Pagamentos (Dia 20 do Mês Seguinte)
11. **PAGAR_SIMPLES** - Pagar Simples Nacional
    - D: 2.1.2.1 (Simples a Recolher)
    - C: 1.1.1.3 (Caixa Reservado - Simples)
    - **Validação**: Verifica saldos nas duas contas

12. **PAGAR_INSS** - Pagar INSS
    - D: 2.1.2.2 (INSS a Recolher)
    - C: 1.1.1.2 (Caixa Reservado - INSS)
    - **Validação**: Verifica saldos nas duas contas

13. **PAGAR_PRO_LABORE** - Pagar Pró-labore ao Sócio
    - D: 2.1.3.1 (Pró-labore a Pagar)
    - C: 1.1.1.4 (Caixa Reservado - Pró-labore)
    - **Validação**: Verifica saldos nas duas contas

### Operações Adicionais
14. **DISTRIBUIR_LUCROS** - Distribuir Lucros
    - D: 3.3 (Lucros Acumulados)
    - C: 1.1.1.1 (Caixa Corrente)

15. **PAGAR_DESPESA_FUNDO** - Pagar Despesa Geral
    - D: 5.2.x (Escolher subconta de despesa)
    - C: 1.1.1.1 (Caixa Corrente)

16. **RESGATAR_CDB_RESERVA** - Resgatar CDB da Reserva Legal
    - Exige informar o sócio
    - Lançamento 1: D: 1.1.1.1 (Caixa Corrente) / C: 1.1.1.5 (Aplicação CDB)
    - Lançamento 2: D: 3.2.1.{socio_id} (Reserva - Sócio) / C: 3.3 (Lucros Acumulados)

## 📈 Exemplo Prático - Junho/2025

### Valores de Referência
- Receita Bruta: R$ 1.500,00
- Simples (4,5%): R$ 67,50
- Pró-labore Bruto: R$ 621,40
- INSS Pessoal (11%): R$ 68,35
- INSS Patronal (20%): R$ 124,28
- Pró-labore Líquido: R$ 553,05
- INSS Total: R$ 192,63

### Sequência de Operações

1. **Recebimento**
   ```
   REC_HON: R$ 1.500,00
   → Caixa Corrente: R$ 1.500,00
   ```

2. **Verificar Previsão da Operação**
   - Acessar página "Previsão da Operação"
   - Verificar lucro líquido previsto e valores a separar

3. **Provisionar Simples**
   ```
   PROVISIONAR_SIMPLES: R$ 67,50
   → Despesa registrada
   → Passivo "Simples a Recolher" criado
   ```

4. **Provisionar Pró-labore e INSS**
   ```
   PRO_LABORE: R$ 621,40
   INSS_PESSOAL: R$ 68,35
   INSS_PATRONAL: R$ 124,28
   → Despesas registradas
   → Passivos criados
   ```

5. **Separar Caixas**
   ```
   SEPARAR_SIMPLES: R$ 67,50
   → Caixa Corrente: R$ 1.432,50
   → Caixa Reservado Simples: R$ 67,50

   SEPARAR_INSS: R$ 192,63
   → Caixa Corrente: R$ 1.239,87
   → Caixa Reservado INSS: R$ 192,63

   SEPARAR_PRO_LABORE: R$ 553,05
   → Caixa Corrente: R$ 686,82
   → Caixa Reservado Pró-labore: R$ 553,05
   ```

6. **Apurar Resultado (Final do Mês)**
   ```
   APURAR_RESULTADO: (calcular lucro líquido)
   → Lucro transferido para Lucros Acumulados
   ```

7. **Aplicar Reserva Legal (Informar Sócio: André)**
   ```
   APLICAR_RESERVA_CDB: 10% do lucro líquido
   → Reserva Legal (PL) criada
   → CDB aplicado
   ```

8. **Pagamentos no Dia 20/07**
   ```
   PAGAR_SIMPLES: R$ 67,50
   → Baixa do passivo
   → Sai do Caixa Reservado Simples

   PAGAR_INSS: R$ 192,63
   → Baixa do passivo
   → Sai do Caixa Reservado INSS

   PAGAR_PRO_LABORE: R$ 553,05
   → Baixa do passivo
   → Sai do Caixa Reservado Pró-labore
   ```

## 🎯 Vantagens do Sistema

1. **Visibilidade de Liquidez**: Sempre sabe quanto tem disponível vs. reservado
2. **Prevenção de Insuficiência**: Caixa separado garante recursos para obrigações
3. **Gestão por Socio**: Reservas individualizadas para cada sócio
4. **Conformidade Contábil**: Regime de competência mantido corretamente
5. **Fluxo Realista**: Alinhado com a operação diária do escritório

## ⚠️ Observações Importantes

- **PRO_LABORE**: Agora apenas provisiona (D-Despesa / C-Passivo), não paga
- **PAGAR_INSS**: Modificado para usar Caixa Reservado INSS (não Caixa Geral)
- **Operações SEPARAR_***: Não afetam DRE, apenas reorganizam o Ativo
- **APLICAR_RESERVA_CDB**: Exige informar o sócio (cria subconta dinâmica 3.2.1.{socio_id})
- **Contas Removidas**: 2.1.4, 2.1.5, 2.1.6 (eram duplicatas)

### 💰 Regime de Competência - Despesas vs Pagamentos

**IMPORTANTE**: No regime de competência, despesas **não diminuem** quando pagas!

**Despesa** (grupo 5):
- É reconhecida quando **incorrida** (ex: PRO_LABORE registra despesa)
- Permanece acumulada durante todo o período
- Afeta a DRE do mês em que foi registrada
- **Nunca** é diminuída quando paga

**Pagamento** (ex: PAGAR_PRO_LABORE):
- Apenas **baixa o passivo** (conta 2.x.x)
- **Não afeta** a conta de despesa (5.x.x)
- Retira dinheiro do caixa

**Exemplo**:
1. **Junho**: PRO_LABORE R$ 621,40
   - D: 5.1.1 (Despesa) → **R$ 621,40** na DRE de junho
   - C: 2.1.3.1 (Pró-labore a Pagar) → Passivo de R$ 621,40

2. **Julho (dia 20)**: PAGAR_PRO_LABORE R$ 621,40
   - D: 2.1.3.1 (Pró-labore a Pagar) → Passivo zerado
   - C: 1.1.1.4 (Caixa Reservado) → Sai dinheiro
   - Conta 5.1.1 **NÃO é tocada** - a despesa continua R$ 621,40 na DRE de junho

**Quando zeram?**: As despesas são zeradas no fechamento anual pela operação APURAR_RESULTADO, que transfere o resultado líquido (receitas - despesas) para Lucros Acumulados.

## 🔧 Arquivos Modificados

### Backend
- `database/init_plano_contas.py`: Estrutura de contas de caixa
- `database/init_operacoes.py`: Definição das 16 operações
- `database/crud_contabilidade.py`: 6 novos executores + 2 modificados + dispatcher
- `database/crud_plano_contas.py`: Função de criação de subconta de reserva

### Frontend
- `frontend/react-app/src/pages/OperacoesContabeis.jsx`: Atualizado necessitaSocio array

## 📝 Status da Implementação

✅ Estrutura de contas criada
✅ 16 operações definidas
✅ 8 executores implementados
✅ Dispatcher atualizado
✅ Frontend ajustado
✅ Docker containers reconstruídos
✅ Banco de dados inicializado
✅ Bug corrigido: APLICAR_RESERVA_CDB e RESGATAR_CDB_RESERVA agora criam 2 lançamentos cada
✅ Sistema pronto para uso

## 🐛 Correções Aplicadas (04/12/2025)

### Problema Identificado
Operações `APLICAR_RESERVA_CDB` e `RESGATAR_CDB_RESERVA` estavam sendo registradas **sem lançamentos contábeis**, aparecendo vazias no histórico.

### Causa
Executores criavam apenas 1 lançamento cada, quando deveriam criar 2:
- **APLICAR_RESERVA_CDB**: Faltava o lançamento da aplicação no CDB (só criava D-Lucros / C-Reserva)
- **RESGATAR_CDB_RESERVA**: Faltava o lançamento do resgate do CDB (só criava D-Reserva / C-Lucros)

### Solução
Corrigidas as funções `_executar_reservar_fundo()` e `_executar_baixar_fundo()`:

**APLICAR_RESERVA_CDB** agora cria:
1. D-3.3 (Lucros Acum) / C-3.2.1.{socio_id} (Reserva Legal)
2. D-1.1.1.5 (Aplicação CDB) / C-1.1.1.1 (Caixa Corrente)

**RESGATAR_CDB_RESERVA** agora cria:
1. D-1.1.1.1 (Caixa Corrente) / C-1.1.1.5 (Aplicação CDB)
2. D-3.2.1.{socio_id} (Reserva Legal) / C-3.3 (Lucros Acum)

---

**Última atualização**: 04/12/2025 17:46
**Versão**: 2.1 - Sistema de Fluxo de Caixa Completo + Correção de Lançamentos
