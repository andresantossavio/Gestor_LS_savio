# Sistema de Operações Contábeis Padronizadas

## Visão Geral

Este sistema simplifica o registro de operações contábeis através de operações padronizadas que geram automaticamente os lançamentos correspondentes. A principal regra é que **cada operação utiliza exclusivamente o valor informado pelo usuário**, sem realizar cálculos automáticos de percentuais.

## Operações Disponíveis

### 1. Receber Honorários (REC_HON)
- **Lançamento:** D-Caixa / C-Receita
- **Uso:** Registrar o recebimento de honorários de clientes.

### 2. Reservar Fundo (RESERVAR_FUNDO)
- **Lançamento:** D-Lucros Acumulados / C-Reserva
- **Uso:** Transferir um valor do resultado da empresa para um fundo de reserva.

### 3. Pró-labore (Bruto) (PRO_LABORE)
- **Lançamento:** D-Despesa Pró-labore / C-Caixa
- **Uso:** Registrar o pagamento do valor bruto do pró-labore a um sócio. O valor informado é o valor que sai do caixa.

### 4. INSS Pessoal (sobre Pró-labore) (INSS_PESSOAL)
- **Lançamento:** D-Despesa Pró-labore / C-INSS a Recolher
- **Uso:** Provisionar o valor do INSS retido do sócio. Este valor é uma despesa para a empresa e uma dívida com o governo.

### 5. INSS Patronal (INSS_PATRONAL)
- **Lançamento:** D-Despesa INSS Patronal / C-INSS a Recolher
- **Uso:** Provisionar a contribuição patronal de INSS sobre o pró-labore.

### 6. Pagar INSS (PAGAR_INSS)
- **Lançamento:** D-INSS a Recolher / C-Caixa
- **Uso:** Efetuar o pagamento do valor total de INSS acumulado (pessoal + patronal).
- **Validação:** Verifica se há saldo suficiente na conta "INSS a Recolher".

### 7. Distribuir Lucros (DISTRIBUIR_LUCROS)
- **Lançamento:** D-Lucros Acumulados / C-Caixa
- **Uso:** Distribuir o lucro líquido aos sócios.
- **Validação:** Verifica se há saldo suficiente na conta "Lucros Acumulados".

### 8. Pagar Despesa via Fundo (PAGAR_DESPESA_FUNDO)
- **Lançamento:** D-Outras Despesas / C-Caixa
- **Uso:** Registrar o pagamento de despesas diversas.

### 9. Baixa do Fundo (BAIXAR_FUNDO)
- **Lançamento:** D-Reserva / C-Lucros Acumulados
- **Uso:** Reverter um valor do fundo de reserva de volta para a conta de lucros.
- **Validação:** Verifica se há saldo suficiente na conta "Reserva".


## Como Usar

### Interface Web

1.  Acesse **Contabilidade > Operações** no menu.
2.  Selecione a operação desejada.
3.  Preencha os campos:
    -   **Valor:** Montante exato da operação (em R$).
    -   **Data:** Data em que a operação ocorreu.
    -   **Descrição:** Histórico ou detalhe (opcional).
    -   **Sócio:** Opcional para `PRO_LABORE`, `INSS_PESSOAL`, `INSS_PATRONAL` e `DISTRIBUIR_LUCROS`.
4.  Clique em **Executar Operação**. Uma nota informativa aparecerá para reforçar que o valor deve ser o montante final, não um percentual.

### Histórico
- Filtre as operações por mês de referência.
- Expanda cada operação para visualizar os lançamentos contábeis gerados.
- Cancele operações se necessário (isso removerá os lançamentos associados).

## Exemplo de Fluxo Completo (Pró-labore e INSS)

Suponha um pró-labore bruto de **R$ 5.000,00**.
- INSS Pessoal (11%): R$ 550,00
- INSS Patronal (20%): R$ 1.000,00
- Valor líquido a receber: R$ 4.450,00

As operações devem ser registradas da seguinte forma:

**1. Registrar o pagamento do Pró-labore (líquido)**
- **Operação:** `Pró-labore (Bruto)`
- **Valor:** `4450.00`
- **Descrição:** "Pagamento do pró-labore líquido de João"
- **Lançamento Gerado:** D-Despesa Pró-labore (5.1.1) / C-Caixa (1.1.1) -> R$ 4.450,00

**2. Provisionar o INSS Pessoal**
- **Operação:** `INSS Pessoal (sobre Pró-labore)`
- **Valor:** `550.00`
- **Descrição:** "INSS retido do pró-labore de João"
- **Lançamento Gerado:** D-Despesa Pró-labore (5.1.1) / C-INSS a Recolher (2.1.5) -> R$ 550,00
> Após esta operação, a conta de despesa de pró-labore (5.1.1) terá um saldo devedor de R$ 5.000 (4.450 + 550), refletindo o custo bruto total.

**3. Provisionar o INSS Patronal**
- **Operação:** `INSS Patronal`
- **Valor:** `1000.00`
- **Descrição:** "INSS patronal sobre o pró-labore de João"
- **Lançamento Gerado:** D-Despesa INSS Patronal (5.1.3) / C-INSS a Recolher (2.1.5) -> R$ 1.000,00

**4. Pagar o INSS Total**
- A conta "INSS a Recolher" (2.1.5) agora tem um saldo credor de R$ 1.550,00 (550 + 1000).
- **Operação:** `Pagar INSS`
- **Valor:** `1550.00`
- **Descrição:** "Pagamento da guia do INSS referente ao mês X"
- **Lançamento Gerado:** D-INSS a Recolher (2.1.5) / C-Caixa (1.1.1) -> R$ 1.550,00
> A conta de INSS a Recolher (2.1.5) fica com saldo zero.

## Plano de Contas Necessário
Para o funcionamento correto das operações, as seguintes contas (ou equivalentes) devem existir no plano de contas:

- **1.1.1** - Caixa e Bancos (`Ativo`)
- **2.1.5** - INSS a Pagar (`Passivo`)
- **3.1** - Capital Social (`PL`)
- **3.2** - Reservas (`PL`)
- **3.3** - Lucros ou Prejuízos Acumulados (`PL`)
- **4.1.1** - Receita de Serviços (`Receita`)
- **5.1.1** - Pró-labore e Salários (`Despesa`)
- **5.1.3** - Encargos INSS (`Despesa`)
- **5.2** - Despesas Operacionais (`Despesa`)