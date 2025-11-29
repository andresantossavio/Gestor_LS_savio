# Sistema de Contabilidade - Gestor LS

## ✅ Implementado com Sucesso

### Backend

#### Modelos de Dados (`database/models.py`)
- **`SimplesFaixa`**: Tabela de faixas do Simples Nacional com histórico de vigências
  - Campos: `limite_superior`, `aliquota`, `deducao`, `vigencia_inicio`, `vigencia_fim`, `ordem`
- **`DREMensal`**: Consolidação mensal da DRE
  - Campos: `mes` (YYYY-MM), `receita_bruta`, `receita_12m`, `aliquota`, `aliquota_efetiva`, `deducao`, `imposto`, `inss_patronal`, `despesas_gerais`, `lucro_liquido`, `reserva_10p`, `consolidado`

#### Helpers (`utils/`)
- **`datas.py`**: Funções para manipular meses (formato YYYY-MM, janelas de 12 meses, início/fim do mês)
- **`simples.py`**: Cálculo da faixa do Simples baseado em receita acumulada 12m, alíquota efetiva, e inicialização de faixas padrão

#### CRUD (`database/crud_contabilidade.py`)
- **Faixas Simples**: `create_simples_faixa`, `get_simples_faixas_vigentes`, `get_all_simples_faixas`, `update_simples_faixa`, `delete_simples_faixa`
- **DRE Mensal**: `consolidar_dre_mes`, `get_dre_mensal`, `get_dre_ano`
  - Consolidação calcula: receita bruta, receita 12m, alíquota/dedução do Simples, despesas gerais, lucro líquido, reserva 10%

#### Endpoints (`backend/main.py`)
- **Sócios**: `GET/POST /api/contabilidade/socios`, `PUT/DELETE /api/contabilidade/socios/{id}`
- **Entradas**: `GET/POST /api/contabilidade/entradas` (com rateio por sócio via `entradas_socios`)
- **Despesas**: `GET/POST /api/contabilidade/despesas` (com sócios responsáveis via `despesas_socios`)
- **DRE**: `GET /api/contabilidade/dre?year=YYYY` (retorna 12 linhas, jan–dez)
  - `POST /api/contabilidade/dre/consolidar?mes=YYYY-MM&forcar=false`
- **Faixas Simples**: `GET/POST/PUT/DELETE /api/contabilidade/simples-faixas/{id}`
  - `POST /api/contabilidade/simples-faixas/inicializar` (popula faixas padrão 2025)

### Frontend

#### Páginas criadas
- **`pages/DRE.jsx`**: Tabela com 12 meses do ano selecionado
  - Colunas: Mês, Receita Bruta, Receita 12m, Alíquota, Alíquota Efetiva, Dedução, Imposto Mês, INSS (20%), Despesas Gerais, Lucro Líquido, Reserva 10%
  - Botões: Consolidar (mês não consolidado) / Recalcular (mês consolidado)
- **`pages/ConfigSimples.jsx`**: CRUD de faixas do Simples
  - Formulário: Limite Superior, Alíquota (%), Dedução, Vigência Início/Fim, Ordem
  - Tabela: Editar/Deletar faixas existentes
- **`pages/Contabilidade.jsx`**: Dashboard atualizado com links para DRE e ConfigSimples

#### Navegação (`App.jsx`)
- Rotas adicionadas: `/contabilidade/dre`, `/contabilidade/config-simples`
- Já existentes: `/contabilidade/entradas/nova`, `/contabilidade/despesas/nova`, `/contabilidade/socios`

### Infraestrutura

#### Docker (`docker-compose.yml`)
- Volumes montados: `./backend`, `./database`, `./utils` (permite hot-reload sem rebuild)
- Containers: `gestor_app` (FastAPI), `gestor_nginx` (frontend estático)

#### Dependências (`requirements.txt`)
- Adicionado: `python-dateutil==2.8.2` (para manipulação de datas)

---

## 🔧 Como usar

### 1. Inicializar faixas do Simples (primeira vez)
```bash
# Via API (recomendado):
curl -X POST http://localhost:8080/api/contabilidade/simples-faixas/inicializar
```

### 2. Cadastrar sócios
- Acesse: `http://localhost:8080/contabilidade/socios`
- Crie sócios (ex.: André Savio, Bruna Leão, etc.)
- **Importante**: O administrador deve ter `funcao` contendo "Administrador" (usado para aplicar 5%)

### 3. Cadastrar entradas
- Acesse: `http://localhost:8080/contabilidade/entradas/nova`
- Preencha: Cliente, Data, Valor, Percentuais por sócio
- **Nota**: A soma dos percentuais pode ser < 1 (rateio parcial permitido)

### 4. Consolidar DRE
- Acesse: `http://localhost:8080/contabilidade/dre`
- Selecione o ano
- Clique em "Consolidar" para cada mês com dados
- **Cálculo automático**: Receita 12m, alíquota Simples, imposto, lucro líquido, reserva 10%

### 5. Ajustar faixas Simples (quando a lei mudar)
- Acesse: `http://localhost:8080/contabilidade/config-simples`
- Adicione novas faixas com vigência futura
- Encerre faixas antigas definindo "Vigência Fim"
- **Importante**: Meses consolidados não recalculam automaticamente; use "Recalcular" na DRE quando necessário

---

## 📊 Estrutura da DRE

A DRE mensal apresenta 11 colunas:
1. **Mês**: YYYY-MM
2. **Receita Bruta**: Soma das entradas do mês
3. **Receita 12m**: Acumulado dos últimos 12 meses (para cálculo da alíquota Simples)
4. **Alíquota**: Alíquota nominal da faixa aplicável (4,5%, 9%, 10,2%, 14%, 22%, 33%)
5. **Alíquota Efetiva**: (Receita_12m × Alíquota - Dedução) / Receita_12m
6. **Dedução**: Valor de dedução da faixa (R$ 0, 8.100, 12.420, 39.780, 183.780, 828.000)
7. **Imposto Mês**: Receita Bruta × Alíquota Efetiva
8. **INSS (20%)**: INSS patronal sobre pró-labore (TODO: calcular pró-labore de André)
9. **Despesas Gerais**: Soma das despesas do mês (água, luz, etc.)
10. **Lucro Líquido**: Receita Bruta - Imposto - INSS - Despesas
11. **Reserva 10%**: 10% do Lucro Líquido

---

## 🚧 Pendências

### Pró-Labore Iterativo
- **Regra**: Pró-labore de André = participação nas Entradas + 5% do lucro líquido, limitado a R$ 1.518,00
- **Cálculo iterativo**: O INSS patronal (20%) sobre o pró-labore reduz o lucro, que por sua vez reduz os 5%
- **Onde implementar**: Criar função `calcular_prolabore_iterativo(mes)` em `utils/simples.py` e chamar em `consolidar_dre_mes` para preencher `inss_patronal`
- **Convergência**: Iterar até delta < R$ 0,01 entre pró-labore calculado e pró-labore anterior

### Endpoint Pró-Labore
- **Criar**: `GET /api/contabilidade/prolabore?month=YYYY-MM`
- **Retorno**: Pró-labore bruto, INSS pessoal (11%), INSS patronal (20%), pró-labore líquido, lucro André (líquido)

### Lucros Disponíveis
- **Criar**: `GET /api/contabilidade/lucros?month=YYYY-MM`
- **Cálculo**: Somar rateios de Entradas por sócio, aplicar reservas (5% admin creditado ao André; 10% fundo deduz do distribuível), subtrair efeitos de INSS patronal, apresentar lucro líquido por sócio

### Frontend: Páginas Pró-Labore e Lucros
- `pages/ProLabore.jsx`: Tabela mensal com campos do cálculo iterativo
- `pages/Lucros.jsx`: Tabela por mês e por sócio com valores brutos, reservas, líquidos

---

## ✅ Pronto para uso

O sistema está operacional para:
- ✅ Cadastrar sócios, entradas e despesas manualmente
- ✅ Configurar e editar faixas do Simples Nacional
- ✅ Consolidar DRE mensal com cálculo automático de impostos
- ✅ Visualizar relatórios anuais de DRE (12 meses)
- ✅ Recalcular meses consolidados quando necessário (correção de erros ou mudança de faixas)

---

## 🗄️ Banco de Dados

- **Arquivo**: `gestor_ls.db` (SQLite, montado no Docker)
- **Tabelas novas**: `simples_faixas`, `dre_mensal`
- **Migrações**: Não há framework de migração; `Base.metadata.create_all()` cria tabelas ao iniciar (se não existirem)
- **Backup recomendado**: Copiar `gestor_ls.db` antes de mudanças estruturais

---

## 🔄 Reiniciar sistema

```bash
cd C:\PythonProjects\GESTOR_LS
docker-compose down
docker-compose up -d
```

---

## 📝 Notas importantes

1. **Import CSV removido**: Endpoints de import CSV e listagem de recebimentos foram comentados no backend e removidos do frontend. Agora todas as entradas são manuais via formulário.

2. **Consolidação é editável**: Meses consolidados podem ser recalculados a qualquer momento (botão "Recalcular" na DRE). Use com cautela para evitar inconsistências em relatórios já fechados.

3. **Histórico de faixas**: Ao mudar a legislação do Simples, não delete faixas antigas; encerre-as com "Vigência Fim" e adicione novas com "Vigência Início" futura. Isso permite recalcular meses passados com as regras vigentes na época.

4. **Chave de mês**: Padronizado em `YYYY-MM` (ex.: `2025-11`). Não há chaves numéricas tipo Excel serial.

5. **Percentuais de entrada**: Aceita soma < 1 (rateio parcial). Exemplo: entrada de R$ 1.000 com 30% André, 40% Bruna = R$ 300 André, R$ 400 Bruna, R$ 300 não atribuído.
