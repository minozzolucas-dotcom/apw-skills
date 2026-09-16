# Dataset Anatel de Estações (ERB) — como obter e preparar

## ⚡ Via 0 — BASE LOCAL EMBUTIDA (use esta primeiro)

A skill já carrega a base nacional em `assets/anatel_smp_base.csv.gz`
(extração fornecida em **jul/2026**, arquivo original `Mai26.csv`):
111.296 estações SMP únicas, 27 UFs, **sem cabeçalho**, 12 colunas `;`
(Estação; Operadora; UF; Município; Bairro; Logradouro; Lat; Long; IBGE;
ClassInfraFis; Tecs; Faixas). ~100 linhas têm `;` extra no logradouro —
os scripts reancoram pelos 6 campos finais.

- Consulta pontual: `scripts/anatel_lookup.py` (coordenada/endereço/município).
- Lote: `scripts/erb_towerco_triage.py` já usa esta base por default
  (exige `--uf`, `--mun` ou `--bbox` para recortar).
- Só desça às vias abaixo se precisar de dado MAIS NOVO que jul/2026 ou de
  campos que esta extração não tem (ex.: uma linha por emissão/frequência).

**Atualização da base:** quando o Lucas mandar extração nova, gzip -9 do CSV →
substituir `assets/anatel_smp_base.csv.gz`, atualizar as contagens aqui e no
SKILL.md, e re-salvar a skill.


Leia este arquivo no Passo 1 da skill, quando precisar obter as ERBs de uma
região.

## Lembrete central

Toda fonte da Anatel te dá a estação por **operadora** (detentora da outorga
SMP), **nunca por torreira**. A torreira é sempre inferida/confirmada por outra
fonte (deal APW + POP). Não existe base pública que mapeie ERB → TowerCo.

## Via 1 — Dados Abertos (dados.gov.br) — preferida para LOTE

Dataset oficial: **"Outorga e Licenciamento — Estações da Telefonia Móvel"**
(Estações Licenciadas a operar no Serviço Móvel Pessoal — SMP). É a relação de
ERBs com licença de instalação e funcionamento emitida pela Anatel.

- Portal: `dados.gov.br` → buscar `estacoes-licenciadas-a-operar-no-servico-movel-pessoal`.
- Painel interativo equivalente: Portal Anatel → **Painéis > Outorga e
  Licenciamento > Estações do SMP** (localização, operadora, tecnologia,
  frequência).
- Plano de Dados Abertos vigente 2025–2027 (a Anatel mira 85% de dados abertos
  até 2027), então a base é mantida/ampliada.

**Tamanho:** nacional tem ordem de centenas de milhares de estações e **milhões
de linhas** (uma linha por emissão/frequência). **Sempre filtre por UF/município
ANTES de processar** — nunca jogue o Brasil inteiro no motor.

### Como filtrar por região antes do motor

Se o arquivo vier por UF, use direto. Se vier nacional, recorte por bounding box
da região (mais robusto que filtrar por nome de município, que tem grafia
inconsistente):

```bash
# exemplo: recortar uma bbox antes de rodar o motor (csvkit ou awk)
# colunas variam; ajuste os índices de Lat/Long ao header real
awk -F';' 'NR==1 || ($LATCOL >= -23.30 && $LATCOL <= -23.10 && \
  $LNGCOL >= -46.65 && $LNGCOL <= -46.45)' estacoes_BR.csv > erb_regiao.csv
```

Ou, mais seguro, deixe o próprio motor ler o CSV regional já cortado pela UF.

## Via 2 — Painel SMP / Mosaico — para consulta PONTUAL (1–5 sites)

Para poucos sites, a interface do **Painel SMP** ou do **Mosaico**
(`sistemas.anatel.gov.br/se/public/view/b/licenciamento.php`) resolve sem
dataset. Aceita consulta por área/coordenada e mostra operadora, tecnologia,
frequência.

⚠️ É Power BI / ASP — **não raspar em lote** (caro em token, frágil). Use
`agent-browser` só aqui, e por ser site **público**, a `apw-chrome-agent-lean-compliance`
permite screenshot pontual (a restrição é para domínios APW/Dynamics/Microsoft).

## Via 3 — Forest-GIS (atalho geoespacial)

`forest-gis.com` publica os dados de ERB da Anatel já em **shapefile** com
lat/long, prontos para QGIS. Útil se você quer overlay geoespacial direto.
Converter shapefile → CSV (geopandas `to_csv`) e alimentar o motor.

## Campos da planilha "ERBs Mar26" (layout real do Lucas)

O motor reconhece variações de cabeçalho (case-insensitive, sem acento). Layout
confirmado da planilha do Lucas:

| Coluna | Cabeçalho | Uso no motor |
|---|---|---|
| A | `Número Estação` | **chave de deduplicação** |
| B | `Operadora` | TIM/VIVO/CLARO/OI... (normalizada) → tenancy |
| C | `Sigla` | UF |
| D | `MUN` | município |
| E | `Bairro` | bairro |
| F | `Logradouro` | endereço (validação do match) |
| G | `Latitude` | posição (aceita vírgula decimal) |
| H | `Longitude` | posição |
| I | `IBGE` | código do município |
| J | **`ClassInfraFis`** | **Greenfield / Rooftop → deriva a TRILHA APW** |
| K | `Tecs` | 2G 3G 4G 5G |
| L | `Faixa` | 700 / 850 / 900 / 1800... |

`ClassInfraFis` é o campo-chave do produto:
- **Rooftop** → Trilha A (Cessão de Direitos Creditórios / condomínio).
- **Greenfield** → Trilha B (Direito Real de Superfície / terreno).
- vazio / `(vazio)` / `-` → trilha indefinida (resolver por logradouro/satélite).

Valores `(vazio)`, `vazio` e `-` são tratados como ausência pelo motor.

## Deduplicação — por que a contagem assusta

1. **Por emissão:** a Anatel repete a mesma `NumEstacao` várias vezes (uma por
   frequência/emissão licenciada). O motor colapsa por `NumEstacao` → 1 estação.
2. **Por co-location:** operadoras diferentes licenciam estações próprias na
   **mesma torre**. O motor clusteriza estações ≤ `--radius-colocation` (30 m
   padrão) → **1 site físico** com a lista de operadoras. É esse número que
   importa para "quantas torres", não a contagem de estações.

Sequência real: linhas (milhões) ≫ estações únicas ≫ **sites físicos**.

## Fontes

- Anatel — Estações Rádio Base / Mosaico: `gov.br/anatel` (Outorga e
  Licenciamento) e `sistemas.anatel.gov.br/se/public/view/b/licenciamento.php`.
- dados.gov.br — `estacoes-licenciadas-a-operar-no-servico-movel-pessoal`.
- Painel SMP — Portal Anatel > Painéis > Outorga e Licenciamento > Estações do SMP.
- Forest-GIS — shapefile de ERB Anatel (`forest-gis.com`).
- Plano de Dados Abertos Anatel 2025–2027 (meta 85% até 2027).
