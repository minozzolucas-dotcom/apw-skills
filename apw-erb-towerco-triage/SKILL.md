---
name: apw-erb-towerco-triage
description: >-
  CONTÉM A BASE ANATEL NACIONAL EMBUTIDA (SMP jul/2026 — 111.296 estações, 27
  UFs): é a fonte automática de consulta de ERB/site da APW Brasil. NÃO peça
  planilha — consulte a base local primeiro. Use SEMPRE que precisar saber se
  existe ERB/torre num endereço, coordenada, bairro ou município ("tem torre
  nesse endereço?", "qual operadora atende esse site?", "busca na base Anatel",
  "ERB perto de lat,long", "rooftop ou greenfield?", "que trilha", "tenancy") —
  inclusive como apoio às outras skills apw quando surgir endereço/coordenada
  de site. Também tria prospecção em lote: clusteriza co-location em sites
  físicos, deriva a TRILHA APW (Rooftop=Trilha A/CDC; Greenfield=Trilha B/DRS),
  conta tenancy e cruza com leads do CRM (opcional). Gera CSV+HTML com Maps.
  Torreira NÃO é derivável da Anatel — sai "a confirmar". NÃO use para deal
  único por código L (apw-deal-dossier) nem lead a partir de contrato
  (apw-pin-creator).
---

# APW — Enriquecimento de ERB por trilha (Anatel raw × CRM)

Skill operacional APW Brasil. Pega a **lista raw da Anatel** (planilha tipo
"ERBs Mar26") e transforma cada ponto em **site físico qualificado** — pronto
para enriquecer um lead sem informação ou virar prospecção.

## As três verdades que governam a skill

1. **A Anatel licencia por OPERADORA, nunca por torreira.** Não existe coluna de
   torreira nos dados raw, nem proxy honesto. O motor marca torreira como
   **"a confirmar"** e pronto — não inventa. (Cravar a torreira é trabalho de
   campo/contrato/POP, **fora** do que a Anatel entrega.)
2. **O sinal útil da Anatel raw é o `ClassInfraFis`** (Greenfield × Rooftop), que
   mapeia direto no produto APW:
   - **Rooftop** (topo de prédio) → **Trilha A — Cessão de Direitos Creditórios**
     (condomínio).
   - **Greenfield** (torre no solo) → **Trilha B — Direito Real de Superfície**
     (terreno, PF/PJ dona).
3. **Co-location:** várias operadoras na mesma estrutura = **1 site = 1 torre**.
   O nº de operadoras (tenancy) é indício de quão "core" é o site.

> Este é o nexo: a Anatel não diz **de quem** é a torre, mas diz **que tipo** de
> ativo é — e isso já tria o lead pelado para a trilha certa, sem POP.


## Base Anatel LOCAL (embutida) — consulte antes de pedir qualquer planilha

A skill carrega a base nacional em `assets/anatel_smp_base.csv.gz`:

- **Extração fornecida pelo Lucas em jul/2026** (arquivo original `Mai26.csv`).
- **111.296 estações SMP únicas**, 27 UFs. Operadoras: Vivo 38k, TIM 36,9k,
  Claro 31,9k, Brisanet 3k, Algar 753, Unifique 644, Sercomtel 72.
- ClassInfraFis: ~56,4k "Nao Informada", 42,4k Greenfield, 7,1k Rooftop,
  resto Indoor/SmallCell/RanSharing etc. (~100 linhas têm colunas deslocadas
  por `;` no logradouro — os scripts reancoram pelo fim automaticamente).
- Layout: **12 colunas `;` SEM cabeçalho** — Estação; Operadora; UF; Município;
  Bairro; Logradouro; Lat; Long; IBGE; ClassInfraFis; Tecs; Faixas.

**Regra de ouro:** qualquer pergunta com endereço, coordenada ou "tem
site/torre aí?" → rode `anatel_lookup.py` direto. Só peça planilha nova ao
Lucas se ele disser que tem extração mais recente.

### Consulta pontual — `scripts/anatel_lookup.py`

```bash
# por coordenada (use --near=... por causa do sinal negativo)
python3 scripts/anatel_lookup.py --near=-23.48298,-46.64489 --radius 300

# por endereço / bairro / município / estação / operadora (combináveis)
python3 scripts/anatel_lookup.py --addr "MARECHAL DEODORO" --mun "Juiz de Fora"
python3 scripts/anatel_lookup.py --estacao 1000001986
python3 scripts/anatel_lookup.py --mun "Capao da Canoa" --operadora TIM

# --cluster agrupa co-location (1 linha por SITE, com tenancy)
python3 scripts/anatel_lookup.py --near=-23.48298,-46.64489 --cluster

# --json para outra skill consumir programaticamente
python3 scripts/anatel_lookup.py --near=-23.48,-46.64 --radius 200 --json
```

Roda em ~2–3 s sobre a base inteira (stdlib pura). Saída traz operadora,
infra→trilha, tec/faixa, distância e link Maps.

### Uso pelas outras skills apw (encadeamento automático)

- **apw-pin-creator** — ao farejar coordenada de um contrato, confirmar na base
  se há ERB licenciada no ponto (`--near` + `--radius 150`) e herdar
  operadora/infra/tec para o Lead.
- **apw-deal-dossier / apw-pre-dd-legal / apw-proposta-comercial** — quando o
  deal tem endereço/coordenada, um `--near` dá o retrato do site (tenancy,
  5G, trilha) sem abrir o Mosaico.
- **analise-mytower** — validar que o endereço do contrato do Max tem ERB ativa.
- **tower-intel-br** — recortes regionais e mapas partem desta base local antes
  de qualquer download do dados.gov.br.

## Quando usar

Gatilhos: Lucas manda a planilha de ERBs da Anatel; "cruza Anatel com o CRM";
"enriquece esses leads sem info"; "esse site é rooftop ou greenfield / que
trilha"; "mapa de torres da região"; "triar ERB"; `/apw-erb-towerco-triage`.

## Pré-requisitos

- **Nenhum para consulta pontual** — a base nacional já está embutida
  (`assets/anatel_smp_base.csv.gz`, jul/2026).
- Para lote, o motor usa a base embutida por default (`--uf`/`--mun`/`--bbox`
  obrigatórios para recortar) ou uma lista externa via `--erb`. O motor
  lê as colunas reais (ver `references/anatel_dataset.md`), detecta separador,
  deduplica por Número Estação, descarta linha fora do Brasil.
- **(Opcional) leads do CRM** para o cruzamento — só se quiser separar
  "já tem lead" de "prospecção". Sem leads, o motor só qualifica os sites.
- Se for puxar leads: sessão em `leadsearch2.aspx` + `apw-chrome-agent-lean-compliance`
  (zero screenshots em Dynamics; somente leitura).
- Python 3 (motor é stdlib pura). ⚠️ Download do dados.gov.br não roda em sandbox
  de rede restrita — rodar no Cowork ou passar o CSV já baixado.

---

## Pipeline

### Passo 1 — Carregar a lista Anatel

Recortar por região se a lista for grande (bbox ou filtro por UF/MUN). Não é
preciso limpar: o motor reconhece `Número Estação, Operadora, Sigla, MUN,
Bairro, Logradouro, Latitude, Longitude, IBGE, ClassInfraFis, Tecs, Faixa`
(e variações).

### Passo 2 — (Opcional) puxar leads do CRM

Só se for cruzar. Mecânica idêntica à `analise-mytower` §4 (fetch no
`LeadSearch2DataFeed.aspx`, parse §/ƒ, `fixMojibake`). Exportar como JSON
(`lnum, stage, status, lat, lng`) em `/home/claude/leads_<regiao>.json`.

> Mesmo sem nenhuma info no lead, o cruzamento serve: ele diz **qual ERB física
> está embaixo daquele lead pelado** — e o motor herda operadora, trilha, tec,
> tenancy e endereço para dentro dele.

### Passo 3 — Rodar o motor

```bash
# default: base embutida — basta recortar
python3 scripts/erb_towerco_triage.py \
  --mun "São Bernardo do Campo" --uf SP \
  --region-label "São Bernardo do Campo / SP" \
  --out-prefix /mnt/user-data/outputs/erb_sbc

# ou com planilha externa mais recente
python3 scripts/erb_towerco_triage.py \
  --erb /caminho/ERBs_<regiao>.csv \
  --leads /home/claude/leads_<regiao>.json \   # opcional
  --radius-colocation 30 \                      # m, agrupa co-location
  --radius-match 150 \                          # m, casa site × lead
  --region-label "São Bernardo do Campo / SP" \
  --out-prefix /mnt/user-data/outputs/erb_<regiao>
```

Deduplica → clusteriza co-location → deriva trilha do `ClassInfraFis` → conta
tenancy → (se houver leads) cruza → gera `.csv` e `.html`.

### Passo 4 — Ler a saída

Uma linha por **site físico**:

| Campo | O que é |
|---|---|
| INFRA → TRILHA | Greenfield→Trilha B (DRS) · Rooftop→Trilha A (CDC) · vazio→indefinido |
| TENANCY | nº de operadoras na torre + quais (multi-operadora = site core) |
| TEC / FAIXA | tecnologias e faixas consolidadas |
| TORREIRA | **sempre "a confirmar"** — não vem da Anatel |
| CRM (se cruzou) | 🔵 "já tem lead Lxxxx a Xm" · 🔴 "sem lead = prospecção" |
| COORD / MAPS | lat/long + link Google Maps |

`present_files` no `.html` + resumo no chat: contagem Trilha A/B, multi-operadora,
e — se cruzou — quantos sites são prospecção nova (ERB ativa sem lead APW).

---

## Caveats honestos

- **Torreira não sai daqui.** Se alguém quiser a torreira, a resposta é: campo,
  contrato ou POP. A skill não chuta. Não há heurística confiável.
- **ClassInfraFis às vezes vem vazio** → trilha "indefinido"; resolver olhando
  o logradouro/satélite (verificação humana).
- **Co-location**: `--radius-colocation` 30 m. Rooftop urbano denso pode colar
  prédios vizinhos; greenfield rural fica seguro. Ajustar e re-rodar se o cluster
  parecer errado.
- **Lat/long Anatel ≠ lat/long do lead** — ambos imprecisos. `dist_m` na saída
  do cruzamento existe pra calibrar o olho.
- **Prospecção (sem lead) é o produto, não sobra:** ERB ativa sem lead APW = site
  com aluguel acontecendo onde a APW não está. Lead bruto.
- **Triagem visual de torre é humana** — o Claude não confirma "tem torre" por
  satélite.

## Encadeamento

- `analise-mytower` — fonte da mecânica leadsearch2 (fetch/parse/haversine/bbox).
- `apw-chrome-agent-lean-compliance` — MANDATÓRIA se tocar no CRM. Só leitura.
- `apw-pin-creator` — sites de prospecção que viram lead novo.
- `apw-proposta-comercial` / `apw-submission-writer` — quando o site qualificado
  (já com trilha) avança para deal.
- `apw-telecom-real-estate-counsel` — análise de cláusula quando o contrato chega.

## Changelog

- **v3 (jul/2026):** base Anatel nacional EMBUTIDA na skill
  (`assets/anatel_smp_base.csv.gz`, extração jul/2026, 111.296 estações) —
  consultas passam a ser automáticas, sem upload de planilha. Novo
  `scripts/anatel_lookup.py` (consulta pontual por coordenada/endereço/
  bairro/município/estação/operadora, `--cluster`, `--json`). Motor de
  triagem agora lê a base sem cabeçalho e `.gz`, usa a base embutida como
  default e ganhou recortes `--uf`/`--mun`/`--bbox`. Reparo automático de
  linhas com `;` extra no logradouro.

- **v2 (jun/2026):** eixo recalibrado de "estimar torreira" para **enriquecimento
  de lead + triagem de trilha**, após o Lucas cravar que não há POP nesses casos
  e a fonte é só a lista raw da Anatel. Motor reescrito para ler as colunas reais
  da planilha "ERBs Mar26" (incl. `ClassInfraFis`, `Tecs`, `Faixa`, `MUN`,
  `Bairro`, `Logradouro`, `IBGE`); deriva Trilha A (rooftop/CDC) × Trilha B
  (greenfield/DRS); tenancy de operadoras; `--leads` agora opcional; torreira
  fixada em "a confirmar". POP removido como pré-requisito.
- **v1 (jun/2026):** versão inicial (estimativa de torreira via cruzamento com
  deals de torreira conhecida + POP). Substituída pela v2.
