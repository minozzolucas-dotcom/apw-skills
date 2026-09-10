# apw-diretor-pace-score

Skill do time APW Brasil que mede o **pace de atividade** dos 15 diretores de aquisição
no Dynamics 365 — quem está ganhando, mantendo ou perdendo velocidade vs. a própria
média histórica.

Cada diretor é comparado com **si mesmo**, não com o time. O Pace Index (PI) é
`ritmo mensal recente ÷ baseline mensal do próprio diretor`.

## O que entrega

Um dashboard HTML dark na marca APW, com 1 card por diretor. Cada card tem uma tabela
`stage × janela`:

| Stage | Baseline | Últ. 12m | Últ. 6m | Últ. 3m | Último mês | Mês em curso |
|---|---|---|---|---|---|---|
| S1 Qualificação | 8.5/mês | 10.2/mês (PI 1.20) | 9.1/mês (PI 1.07) | 12.0/mês (PI 1.41) | 11 (PI 1.29) | 6 (proj 20) |
| S3 Pricing Option | ... | ... | ... | ... | ... | ... |
| S8 Submission | ... | ... | ... | ... | ... | ... |
| S99 Closed & Funded | ... | ... | ... | ... | ... | ... |

PI é colorido: 🔥 Acelerando (≥1.3) · 🟢 Acima (1.0-1.3) · 🟡 Leve queda (0.8-1.0) ·
🟠 Desacelerando (0.5-0.8) · 🔴 Queda livre (<0.5).

## Como usar

### 1. Puxar os dados do CRM (uma vez por rodada)
- Abre `apwireless.crm.dynamics.com` autenticado
- F12 → Console
- Cola o snippet **HARVEST** de `references/snippets.md`
- Ele baixa `apw_pace_harvest_YYYY-MM-DD.json` automaticamente

### 2. Gerar o dashboard
```bash
python3 references/build_pace.py --harvest=apw_pace_harvest_2026-09-09.json --out=dashboard.html
```

Args opcionais:
- `--today=YYYY-MM-DD` (default: hoje) — fixa a data de referência
- `--harvest=PATH` (default: `harvest.json`)
- `--out=PATH` (default: `apw_pace_dashboard.html`)

Abre o HTML no navegador. Pronto.

## Estrutura

```
apw-diretor-pace-score/
├── SKILL.md                       # metodologia, regras, pipeline
├── README.md                      # este arquivo
└── references/
    ├── snippets.md                # snippets JS pra rodar no console do CRM
    └── build_pace.py              # processa o JSON e gera o HTML
```

## Dependências

- Python 3.9+ (só stdlib — `json`, `datetime`, `collections`, `pathlib`, `sys`)
- Acesso autenticado ao Dynamics 365 tenant `apwireless.crm.dynamics.com` com leitura em `opportunity` e `systemuser`

## Regras (não improvisar — ver SKILL.md pra detalhe completo)

- Contagem PURA por stage (S1, S3, S8, S99). Sem score composto.
- Baseline = total desde `new_adphiredate` (com fallback pra `createdon`) até o último mês completo, ÷ meses ativos.
- Janelas: 12m, 6m, 3m, último mês, mês em curso (projetado por regra `× 30/dia_do_mês`).
- Onboarding: diretor com <90 dias de casa não pontua PI (baseline curta demais).
- Ranking default: PI 3m médio dos 4 stages.
- Lucas Minozzo é excluído do ranking (líder do time).

## Skills relacionadas (APW)

- `apw-performance-patterns` — conversão de funil (complementar; esta mede tendência, aquela mede eficiência)
- `apw-reporte-crm-diario` — produtividade dia/semana contra meta operacional
- `apw-stage1-quality-audit` — auditoria de profundidade das qualificações S1
- `apw-dynamics-copilot` — consulta pontual ao CRM (mesmo padrão de FetchXML autenticado)

## Histórico de decisões

- **09/2026** — Fonte migrada do Power BI (report `ff741680-b1c1-404a-b69d-4a778ff7208c`) pro CRM Dynamics 365 via FetchXML aggregate. Motivo: granularidade diária, sem iframe, mesmo padrão de acesso das outras skills APW.
- **09/2026** — Métrica trocada de "score composto ponderado" (S1=1, S3=3, S5=6, S8=15, S99=30) pra "contagem pura por stage". Motivo: legibilidade — cada PI interpretável direto ("qualifica 8/mês em média, agora 12/mês"), sem inventar pesos.
- **09/2026** — S5 removido do dashboard mas mantido no harvest (extensão futura).
