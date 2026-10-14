# apw-quarter-performance-review

Avaliação de desempenho dos 14 diretores de aquisição APW Brasil no modelo
UKG (2026 First/Second Half Semi-Annual Performance Review – Sales).

Não é plano prospectivo (`apw-90day-plan`), não é reporte diário
(`apw-reporte-crm-diario`). É **avaliação formal com nota do gestor**,
texto pronto pra colar no UKG e PDF de evidência pra arquivar.

## Ordem de execução (fluxo completo ≈ 15 min)

### 1. Rodar os 3 snippets no CRM (console F12)

Abre `apwbrasil.crm2.dynamics.com` autenticado, F12 → Console, cola cada
snippet, aguarda download:

| Ordem | Snippet | O que puxa | Tempo |
|:---:|---|---|---|
| opcional | `1_harvest_rent_acquired.js` | Rent Acquired YTD por diretor | ~20s |
| ✅ | `2_harvest_activities.js` | Atividades (phonecall/email/task/appt) YTD | ~2min |
| ✅ | `3_harvest_keynotes_sample.js` | Últimos 10 Key Notes de cada diretor | ~1min |
| opcional | `4_ukg_scrape_autoavaliacao.js` | Captura autoaval do UKG direto | ~5s/diretor |

> **Snippet 1 é opcional porque os dados oficiais do PBI já estão em
> `data/rent_pbi_oficial_YYYY-MM-DD.csv`.** Use quando quiser detalhe por
> deal (L-numbers) ou refresh entre atualizações do PBI.

### 2. Reusar harvest da pace-score

Esta skill também precisa de `apw_pace_harvest_YYYY-MM-DD.json` da skill
`apw-diretor-pace-score`. Se você já rodou no mesmo dia, reusa.

### 3. Autoavaliações (manual ou scrape)

Pra cada diretor, criar `inputs/<slug-diretor>/autoavaliacao.md` com os 7
campos preenchidos (copiar do UKG) OU rodar o snippet 4 na página de
avaliação do diretor pra gerar o JSON automaticamente.

Formato esperado do markdown:

```markdown
# Autoavaliação - Fabio F. Boturao
Ciclo: 2026 Second Half Semi-Annual Performance Review - Sales
Data: 2026-10-14

## Meta 1 - Pipeline Generation
Nota: Needs Improvement
Comentário: Um pouco atrás da meta, mas com tempo. Vou participar mais
das campanhas da Fila e qualificar mais.

## Meta 2 - Business Results
Nota: Needs Improvement
Comentário: Um deal grande no pipeline (+R$144k) e alguns em
regularização...

## Meta 3 - CRM, DEI & Development
Nota: Meets
Comentário: Registros mais resumidos, porém claros nas ações. DEI...

## Meta 4 - Excellence & Attitude
Nota: Meets
Comentário: Acredito que completo as ações acima.

## Meta 5 - Company Goal DEI
Nota: Meets
Comentário: ...

## Meta 6 - Company Goal Training & Development
Nota: Meets
Comentário: ...

## Meta 7 - CRM Usage
Nota: Meets
Comentário: Domínio completo do CRM do Stg 1 ao 99.
```

### 4. Rodar o build

```bash
python3 references/build_review.py \
  --harvest=apw_pace_harvest_2026-10-14.json \
  --activities=apw_activities_2026-10-14.json \
  --keynotes=apw_keynotes_sample_2026-10-14.json \
  --rent-pbi=data/rent_pbi_oficial_2026-10-14.csv \
  --inputs=inputs/ \
  --periodo=H2-2026 \
  --out=performance-review-H2-2026/
```

Flags de período:
- `H1-2026` (jan-jun) → meta pro-rata × 50%
- `9M-2026` (jan-set) → × 75%
- `Q3-2026` (jul-set, isolado) → × 25%
- `H2-2026` (jul-dez) → × 50%
- `FY-2026` (ano todo) → × 100%

### 5. Revisar

- Abre `performance-review-<ciclo>/consolidado-time.html` — radar com nota
  final dos 14, pra bater o olho
- Pra cada diretor, abre `<diretor>/review-<diretor>.html` com evidência
  completa e texto pronto
- Edita `nota-por-meta.csv` se quiser calibrar sua nota antes de colar no
  UKG (o build é um ponto de partida, não decisão final)

### 6. Colar no UKG

Pro cada diretor, abre a página dele no UKG, copia o conteúdo de
`<diretor>/texto-pronto-ukg.md` meta por meta.

## O que a skill DECIDE sozinha vs o que você revê

| Decisão | Automatizada | Precisa você revisar |
|---|:---:|:---:|
| Nota quantitativa Pipeline (meta 1) | ✅ | — |
| Nota quantitativa Business (meta 2) | ✅ | — |
| Nota qualitativa CRM Quality (meta 3) | — | ✅ (default Meets, puxa pra 1/3 se evidência) |
| Nota qualitativa Excellence (meta 4) | — | ✅ |
| Nota qualitativa DEI (meta 5) | — | ✅ |
| Nota qualitativa Training (meta 6) | — | ✅ (depende de autoaval citar curso) |
| Nota semi-quantitativa CRM Usage (meta 7) | ✅ | (puxa pra 1 se < 50 ativ/mês) |
| Texto de comentário por meta | ✅ (template) | ✅ (ajuste de tom) |
| Nota final ponderada | ✅ | — |

## Arquivos nesta skill

```
apw-quarter-performance-review/
├── SKILL.md
├── README.md
├── data/
│   └── rent_pbi_oficial_2026-10-14.csv    ← target + acquired YTD/Q3 do PBI
└── references/
    ├── 1_harvest_rent_acquired.js         ← opcional (detalhe por deal)
    ├── 2_harvest_activities.js            ← obrigatório
    ├── 3_harvest_keynotes_sample.js       ← obrigatório
    ├── 4_ukg_scrape_autoavaliacao.js      ← opcional (acelera coleta)
    └── build_review.py                    ← próxima entrega
```

## Status

- ✅ SKILL.md, README.md, 4 snippets JS
- ✅ CSV oficial PBI embutido (sem precisar rodar snippet 1)
- 🔄 `build_review.py` — próxima entrega (vou fazer depois que você rodar
  os snippets 2 e 3 e me mandar os JSONs — assim já calibro o build com
  dado real)
