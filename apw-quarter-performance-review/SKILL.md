---
name: apw-quarter-performance-review
description: >
  Monta a avaliação de desempenho trimestral/semestral/anual dos diretores
  de aquisição da APW Brasil no modelo UKG/UltiPro (2026 First/Second Half
  Semi-Annual Performance Review – Sales). Entrega por diretor: nota do
  gestor por meta (escala 4 pontos UKG), evidência quantitativa auditável
  do CRM Dynamics 365 (Pipeline Generation = S1/S3/S5, Business Results =
  S99 e Rent Acquired YTD), avaliação qualitativa (CRM Quality, DEI,
  Excellence & Attitude, Training & Development, CRM Usage) a partir de
  autoavaliação parseada + sinais do CRM (contagem de atividades, amostra
  de Key Notes, qualidade de Stage 1), nota final ponderada, texto pronto
  pra colar nos 7 campos do UKG, e PDF de evidência pra arquivar. Também
  gera consolidado do time com radar e tabela comparativa.
  Metas: Sr Experientes (Fabio Boturao, Felipe Porto, Jose Daniel Ramos)
  = S1 100/S3 60/S5 60/S8 12/S99 10/ano. Novos+Plenos = S1 140/S3 70/
  S5 70/S8 10/S99 8/ano. Marcia Mangiulli = pro-rata × meses de casa.
  Excluídos do ciclo: Lucas Minozzo, Diogo Bueno. Pro-rata do período:
  H1 = 50%, 9m YTD = 75%, Q3 isolado = 25%, FY = 100%.
  Pesos UKG (confirmar RH): Pipeline Generation 30% · Business Results 20%
  · CRM/DEI/Development 15% · Excellence & Attitude 15% · Company Goal DEI
  5% · Company Goal Training 5% · CRM Usage 5% = 95% (anomalia 5% — build
  normaliza pra 100% com flag na saída).
  Use SEMPRE que o Lucas pedir "avalia os diretores", "monta a avaliação
  UKG", "performance review Q3/H2/FY", "nota do gestor", "roda a avaliação
  do semestre", "performance semi-anual", "manager assessment", "feedback
  final", "preenche o UKG" ou colar autoavaliação de diretor pedindo
  análise. NÃO use para plano prospectivo 90 dias (apw-90day-plan),
  reporte diário (apw-reporte-crm-diario), pace puro (apw-diretor-pace-
  score), nem recrutamento (apw-recruta-aquisicoes). Esta skill consome o
  harvest da apw-diretor-pace-score como input principal e complementa com
  3 snippets próprios (Rent Acquired, atividades, Key Notes amostragem).
---

# APW Quarter/Semi-Annual Performance Review

Materializa a avaliação de desempenho dos 14 diretores de aquisição da APW
Brasil no modelo oficial UKG (2026 First/Second Half Semi-Annual
Performance Review – Sales).

Não é plano de ação (isso é a `apw-90day-plan`) — é **avaliação formal com
nota do gestor**, texto pronto pra colar no UKG e PDF de evidência pra
arquivar.

## Escala UKG (4 pontos)

| Nota | Rótulo | Critério |
|:---:|---|---|
| 1 | Needs Improvement / Below Expectations | Não atinge expectativas nem metas, não bate alvos com consistência |
| 2 | Meets Expectations | Atinge com consistência, às vezes supera. Entrega confiável |
| 3 | Exceeds Expectations | Supera com frequência, entregas claramente acima do exigido |
| 4 | Exceptional | Impacto material positivo. Supera tudo com consistência |

## As 7 metas e pesos oficiais

| # | Meta | Peso | Natureza | Fonte principal |
|:---:|---|:---:|---|---|
| 1 | Pipeline Generation (S1 + S3 + S5) | 30% | Quantitativo | Harvest pace-score |
| 2 | Business Results (S99 + Rent Acquired) | 20% | Quantitativo | Harvest + snippet rent |
| 3 | CRM Quality + DEI + Development | 15% | Misto | Autoaval + amostra Key Notes |
| 4 | Excellence & Attitude | 15% | Qualitativo | Autoaval + observação gestor |
| 5 | Company Goal: DEI | 5% | Qualitativo | Autoaval + observação |
| 6 | Company Goal: Training & Development | 5% | Qualitativo | Autoaval (Udemy, cursos) |
| 7 | CRM Usage | 5% | Quantitativo + qualitativo | Snippet contagem atividades |

**Soma = 95%**. O build normaliza pra 100% (divide tudo por 0.95) e
destaca essa anomalia na saída pra levantar com RH.

## Régua quantitativa (metas 1, 2, 7)

Pontuação a partir do % da meta anual atingido, ajustado pelo pro-rata do
período:

| % da meta pro-rata | Nota |
|:---:|:---:|
| ≥ 110% | 4 Exceptional |
| 90-109% | 3 Exceeds |
| 70-89% | 2 Meets |
| < 70% | 1 Needs Improvement |

**Pro-rata do período:**
- H1 (jan-jun) → 50% da meta anual
- 9m YTD (jan-set) → 75% da meta anual
- Q3 isolado (jul-set) → 25% da meta anual
- H2 (jul-dez) → 50% da meta anual
- FY (jan-dez) → 100%

**Marcia Mangiulli:** meta anual × (meses de casa no período / meses totais
do período).

## Régua qualitativa (metas 3, 4, 5, 6)

Default = **2 Meets** quando autoavaliação diz Meets e não há
contraindicação da observação do gestor. Puxa para 3 se cita evidência
concreta (curso específico, iniciativa específica). Puxa para 1 se há
contradição óbvia (ex.: "domínio completo CRM" mas Key Notes resumidas).

## Pacote de entrega

```
performance-review-<ciclo>/
├── metodologia.md                     ← régua, pro-rata, pesos (defesa)
├── consolidado-time.html/pdf          ← radar com nota final dos 14
├── consolidado-time.csv               ← tabela editável
└── <diretor>/
    ├── review-<diretor>.html          ← versão rica pra você revisar
    ├── review-<diretor>.pdf           ← anexo pra arquivar
    ├── nota-por-meta.csv              ← meta × autoaval × sua nota × evidência
    └── texto-pronto-ukg.md            ← texto pros 7 campos do UKG
```

## Inputs

1. **Harvest pace-score** (`apw_pace_harvest_YYYY-MM-DD.json`) — reusa da
   skill `apw-diretor-pace-score`. Produz contagens S1/S3/S5/S8/S99 por
   diretor por mês desde 2012.
2. **Rent Acquired YTD** (`apw_rent_acquired_YYYY-MM-DD.json`) — snippet
   próprio `references/1_harvest_rent_acquired.js`.
3. **Atividades CRM YTD** (`apw_activities_YYYY-MM-DD.json`) — snippet
   próprio `references/2_harvest_activities.js`. Conta phonecall/email/
   task/appointment por owner e marca os substantivos (≥ 50 chars no
   corpo).
4. **Amostra de Key Notes** (`apw_keynotes_sample_YYYY-MM-DD.json`) —
   snippet próprio `references/3_harvest_keynotes_sample.js`. Puxa os
   últimos 10 Key Notes de cada diretor pra avaliar qualidade.
5. **Metas Rent Acquired por diretor** — arquivo CSV embutido (editável).
6. **Autoavaliação do diretor** — texto colado em `inputs/<diretor>/
   autoavaliacao.md` com os 7 campos preenchidos.
7. **Período** — flag `--periodo=H1-2026|9M-2026|Q3-2026|H2-2026|FY-2026`.

## Reuso dos snippets

Os 3 snippets (`1_harvest_rent_acquired.js`, `2_harvest_activities.js`,
`3_harvest_keynotes_sample.js`) são rodados **uma vez por ciclo** no
console F12 do Dynamics 365 (`apwbrasil.crm2.dynamics.com`). Cada um baixa
um JSON correspondente. Depois disso o `build_review.py` processa tudo
localmente.

## Como rodar

```bash
# 1. coletar dados (console F12 do Dynamics 365)
#    - roda os 3 snippets desta pasta (./references/)
#    - reusa o harvest da apw-diretor-pace-score (se já tiver do dia)

# 2. preencher autoavaliações manualmente em inputs/<diretor>/autoavaliacao.md
#    (ou colar via Chrome scrape se UKG permitir — ver references/4_ukg_scrape.js)

# 3. rodar build
python3 references/build_review.py \
  --harvest=apw_pace_harvest_2026-10-14.json \
  --rent=apw_rent_acquired_2026-10-14.json \
  --activities=apw_activities_2026-10-14.json \
  --keynotes=apw_keynotes_sample_2026-10-14.json \
  --metas-rent=metas_rent_2026.csv \
  --inputs=inputs/ \
  --periodo=9M-2026 \
  --out=performance-review-9M-2026/
```

## Skills relacionadas

- Consome harvest de [[apw-diretor-pace-score]]
- Complementa [[apw-90day-plan]] (prospectivo) com a avaliação retrospectiva
- Usa amostra de Key Notes como base cruzada com [[apw-stage1-quality-audit]]
