---
name: apw-diretor-pace-score
description: >
  Mede o PACE de atividade dos 15 diretores de aquisição APW Brasil — quem está
  ganhando, mantendo ou perdendo velocidade vs. a PRÓPRIA média histórica. Puxa
  do Dynamics 365 via FetchXML aggregate a contagem de moves de Stage 1, Stage 3,
  Stage 8 e Stage 99 por diretor × mês desde a data de contratação, calcula
  baseline mensal, janelas recentes (12m/6m/3m/último mês/mês em curso) e o Pace
  Index (PI) por stage. Entrega dashboard HTML dark na marca APW com ranking,
  breakdown por stage, trend arrows e sinalização de onboarding. Use SEMPRE que
  o Lucas pedir "pace dos diretores", "quem tá acelerando/desacelerando", "força
  de atividade", "PI dos diretores", "pace score", "roda o pace do time",
  "ranking de ritmo", ou mencionar comparação do ritmo recente de um diretor
  com o histórico dele mesmo. NÃO use para reporte diário (apw-reporte-crm-diario),
  benchmark de conversão de funil (apw-performance-patterns), auditoria de
  qualidade S1 (apw-stage1-quality-audit), forensics de UMA opp
  (apw-opp-activity-forensics), nem consulta pontual ao CRM (apw-dynamics-copilot).
---

# APW Diretor Pace Score

Mede o **ritmo de atividade** dos diretores de aquisição APW Brasil em cada stage do
funil, comparando o desempenho recente contra a média histórica do PRÓPRIO diretor.
Responde uma pergunta: **quem está ganhando, mantendo ou perdendo velocidade?**

Esta skill NÃO é análise de conversão de funil (isso é `apw-performance-patterns`) nem
reporte de produtividade do dia/semana contra meta (isso é `apw-reporte-crm-diario`).
É especificamente sobre **tendência temporal de cada diretor vs. si mesmo**.

## O que ela responde

- Fabio Boturao está performando pior que a média histórica dele? Quanto?
- Quem tem PI > 1 em fechamento (S99) — o pipeline vai converter em receita?
- Diretores que quase pararam de qualificar (S1 caindo) mas seguem fechando (S99 estável) — é sinal de saída ou de estilo senior?
- Marcia acabou de entrar — não vale comparar, mostrar em ONBOARDING.
- Diretor com PI 3m > 1.3 em S1/S3/S8/S99 simultaneamente = está acelerando 4 frentes = merece elogio público.

## Métricas — regras (não improvisar)

### Contagem pura, por stage
- **S1** (Qualificação): count de opps com `apwip_stage1_obtainedleaseeconomics` no período onde `_apwip_stage1owner_value` = diretor
- **S3** (Pricing Option): count com `apwip_stage3date` + `_apwip_stage3owner_value`
- **S8** (Submission): count com `apwip_stage8date` + `_apwip_stage8owner_value`
- **S99** (Closed & Funded): count com `apwip_stage99closedandfundeddeal` + `_apwip_stage99owner_value`

**Regra dura**: cada stage é uma métrica SEPARADA. Não somar num "score composto ponderado"
— foi decisão explícita do Lucas (09/2026): a contagem pura por stage é mais legível e
não exige inventar pesos arbitrários. Ownership por stage é INDEPENDENTE (uma opp pode ter
Diretor A no S1, B no S3, C no S8, D no S99 — cada um pega crédito só pelo que moveu).

### Baseline e janelas
| Item | Definição |
|---|---|
| **Baseline mensal** | Total do stage desde `hire_date` até o último mês completo anterior a hoje ÷ meses ativos |
| **Últ. 12 meses** | Total nos 12 meses completos anteriores a hoje ÷ 12 (ajustado se diretor tem <12m de casa) |
| **Últ. 6 meses** | Mesmo, 6 meses completos |
| **Últ. 3 meses** | Mesmo, 3 meses completos |
| **Último mês** | Último mês fechado (o mês anterior ao corrente) |
| **Mês em curso** | Contagem do mês corrente (parcial) + projeção linear `× 30/dia_do_mês` |

### Pace Index (PI)
```
PI[stage, janela] = (moves do stage na janela ÷ meses da janela) ÷ baseline_mensal[stage]
```
Interpretação: PI > 1.0 = ritmo mais rápido que a própria média; PI < 1.0 = mais lento.

**Classificação por cor** (mesma escala para todas as janelas e stages):

| PI | Classe | Cor |
|---|---|---|
| ≥ 1.3 | 🔥 Acelerando forte | Verde APW `#009877` |
| 1.0 – 1.3 | 🟢 Acima da média | Verde claro `#5FBF8B` |
| 0.8 – 1.0 | 🟡 Leve queda | Oliva APW `#A7AF00` |
| 0.5 – 0.8 | 🟠 Desacelerando | Âmbar `#D97706` |
| < 0.5 | 🔴 Queda livre | Vermelho `#B91C1C` |

### Ranking
Ordenação default = **PI 3m médio dos 4 stages** (S1, S3, S8, S99). Só entram no cálculo
os stages com baseline > 0 (evita divisão por zero e distorção pra diretor que nunca fez
aquele stage). Onboarding vai pro final.

### Trend arrow
Compara PI 3m médio vs PI 12m médio:
- Δ > +0.2 → ▲▲ (acelerando vs. tendência longa)
- Δ > +0.05 → ▲ (ligeira aceleração)
- Δ entre -0.05 e +0.05 → = (estável)
- Δ > -0.2 → ▼ (ligeira desaceleração)
- Δ ≤ -0.2 → ▼▼ (desaceleração forte)

### Onboarding
Diretor com `hoje - hire_date < 90 dias` entra em **ONBOARDING** — mostra volume absoluto
mas não pontua PI (baseline curta demais pra ser confiável). Marcia Mangiulli (hire
28/07/2026) é o caso vivo em 09/2026.

## Filtro de "diretor ativo"

Systemuser onde:
- `isdisabled = false`
- `title` in `{'Acquisition Director', 'Sr Acquisition Director', 'Director, Commercial Sale', 'Director, Sales'}`
- Excluir `'Lucas Minozzo'` (é o líder do time, não entra no ranking de pares)

**15 diretores em 09/2026** (11 Acquisition Director + 2 Sr Acquisition Director [Fabio Boturao,
Felipe Porto] + 1 Director Commercial Sale [Jose Daniel Ramos] + 1 Director Sales [Diogo Bueno]).

## Pipeline de execução

### 1. HARVEST (obrigatório — snippet no console F12 do CRM)
Aba autenticada do Dynamics (`apwireless.crm.dynamics.com`), cola o snippet de
`references/snippets.md` seção HARVEST. Ele dispara 5 requests FetchXML aggregate (uma
por stage: S1, S3, S5, S8, S99 — inclui S5 pra futura extensão), busca metadata dos
owners únicos e retorna JSON estruturado. Baixa o `apw_pace_harvest.json` via helper
de download embutido no snippet (nunca `copy()` — o clipboard não é confiável pra
volumes grandes).

Volume esperado: ~7000 linhas agregadas cobrindo 2012-atual, ~90-100 owners históricos,
15 diretores ativos filtrados.

### 2. HIRE DATE OFICIAL (opcional mas recomendado)
Snippet complementar em `references/snippets.md` seção HIRE DATES puxa
`new_adphiredate` do systemuser (data real de contratação vinda do ADP). Se não rodar,
usa `createdon` do systemuser como proxy — funciona pra veteranos mas subestima tempo
de casa de quem foi migrado do CRM antigo.

### 3. BUILD (Python)
Rodar `references/build_pace.py` com o `harvest.json` no mesmo diretório. Gera
`apw_pace_dashboard.html` — HTML dark na marca APW, 1 card por diretor, com tabela
por stage × janela, PI colorido em cada célula, trend arrow, badges de onboarding.

Deliverable único: **HTML aberto no navegador**. Não gera PDF nem PNG por padrão —
se o Lucas pedir "pra colar em email", renderizar com Chrome headless em PNG.

## Regras de leitura (o que o Lucas quer ver primeiro)

Ao entregar o dashboard, comentar em prosa APÓS o link do arquivo:

1. **Top 3 por PI 3m médio** — quem tá acelerando geral.
2. **Diretores com S99 = 0 nos últimos 3 meses** — quem não fechou nada (sinal amarelo
   forte, mesmo se S8 estiver bom, pra investigar próxima leva).
3. **Padrão de senior vs junior** — diretor com S1 baixo mas S99 alto = perfil senior
   colhendo pipeline antigo (Diogo é o caso clássico). Não confundir com queda.
4. **Gargalos específicos** — PI forte no início do funil mas queda no S8/S99 = deal
   trava na hora de virar submission/fechar. Sinalizar o diretor + o stage que trava.
5. **Diretores em queda multi-frente** — PI < 0.8 simultaneamente em ≥3 stages.
   Bandeira vermelha real, não flutuação estatística.

## Skills relacionadas

- `apw-performance-patterns` — benchmark de CONVERSÃO do funil (taxa S3→S8, S8→S99, S1 pra gerar 1 S3). Complementar. Esta skill mede TENDÊNCIA temporal; aquela mede EFICIÊNCIA do funil.
- `apw-reporte-crm-diario` — produtividade do dia/semana contra meta operacional. Curto prazo; esta skill é análise estrutural.
- `apw-stage1-quality-audit` — auditoria de PROFUNDIDADE das qualificações S1 (gaming vs. crítica). Ortogonal.
- `apw-opp-activity-forensics` — análise forense de UMA opp específica. Não é comparativo.
- `apw-dynamics-copilot` — consulta pontual ao CRM. Esta skill usa o mesmo padrão de acesso (FetchXML via sessão autenticada).

## Padrões técnicos herdados

- **Snippet F12 no CRM autenticado** — mesmo padrão de `apw-opp-deepdive-snippet` e `apw-dynamics-copilot`. Nunca sair da sessão do usuário; nunca persistir tokens; nunca abrir agente de navegador (custa muito mais).
- **Marca APW** — segue `apw-brand` (Navy #012B5E, Azul APW #1C75BB, Sage #91A5A4, Verde #009877, Oliva #A7AF00). Wordmark em texto (`APW` branco + `Brasil` sage), Arial em tudo.
- **Filtro Brazil** — `apwip_countryfilter eq FEA663A6-5B28-E211-BCD6-00155D00D805` (GUID canônico do país no tenant Radius).
