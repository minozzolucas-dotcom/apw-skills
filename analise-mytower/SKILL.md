---
name: analise-mytower
description: >-
  Análise automatizada de contratos telecom (MyTower / Max Aureliano via Gmail
  OU batch de contratos enviados direto), cruzando endereços com leads e
  oportunidades do CRM APWireless (Dynamics 365 via leadsearch2.aspx) num raio
  de 150 metros. Detecta cláusulas anti-agregador (anti-DRS, anti-cessão de
  crédito, anti-usufruto, exclusividade telecom) que invalidam o site mesmo
  com lead próximo. Devolve e-mail HTML profissional com identidade visual
  APW Brasil oficial (azul #4e89bd, logo Logo-Brasil.svg, tipografia Arial,
  footer com razão social) consolidando matches classificados (golden, em
  pipeline, fechado, sem match, bloqueado por concorrente) e bloco de
  coordenadas com links Google Maps para acesso rápido. Use SEMPRE que o
  Lucas mencionar "análise MyTower", "contratos do Max", "Max Aureliano",
  "rodar análise de contratos", "cruzar contratos com CRM", "leads próximos
  aos sites do Max", ou enviar batch de contratos telecom (PDF/DOCX/XLSX)
  pedindo cruzamento com base APW.
---

# Análise MyTower — Contratos Telecom × CRM APW

Skill operacional APW Brasil. Cruza contratos telecom (Gmail/MyTower ou batch direto) com leads/oportunidades CRM APWireless. Produz e-mail HTML profissional com classificação por categoria + bloco de coordenadas.

## Quando usar

Gatilhos:
- "Roda análise MyTower"
- "Contratos do Max desta semana"
- "Cruza esses sites do Max com CRM"
- "Tem lead perto dos endereços que o Max mandou?"
- Lucas envia 1+ contratos telecom em anexo pedindo cruzamento (mesmo sem citar Max)
- `/analise-mytower`

## Pré-requisitos

- **Origem Gmail** (fluxo padrão): conector Gmail em `lminozzo@apwbrasil.com.br`. Conector off → parar, pedir conexão.
- **Origem batch direto** (Lucas anexa contratos): pular Passo 1, começar do Passo 2.
- Sessão ativa em `https://apw01.azurewebsites.net/MAPS/leadsearch2.aspx`. Sem aba → usar `agent-browser` pra abrir. Auto-login MCAS resolve se houver sessão Microsoft.
- Permissão explícita Lucas pra (a) ler Gmail+anexos *quando aplicável*, (b) consultar CRM via fetch, (c) compor e-mail. Pedir antes.
- **Compliance APW**: confirmar cobertura antes de produção. Aplicar skill `apw-chrome-agent-lean-compliance` (zero screenshots no Dynamics/leadsearch2, dados sensíveis só em `window.__*`, nunca em retorno de console).

---

## Pipeline

### Passo 1 — Ler e-mails Max Aureliano (últimos 15 dias) [só fluxo Gmail]

**Pular este passo se Lucas anexou contratos direto.**

Query Gmail:

```
from:(Max Aureliano) newer_than:15d has:attachment
```

Pra cada resultado: capturar `messageId`, assunto, data, anexos. Mostrar lista ao Lucas, perguntar se algum deve ser ignorado.

### Passo 2 — Baixar e parsear anexos

**Fluxo Gmail:** salvar em `/home/claude/contratos_max/<messageId>/`.
**Fluxo batch direto:** PDFs já vêm em `<document>` no contexto OU em `/mnt/user-data/uploads/`. Ler direto.

Tipos:
- `.pdf` → pdf-reading skill (`/mnt/skills/public/pdf-reading/SKILL.md`)
- `.docx` → docx skill
- `.xlsx` → xlsx skill (plan de sites comum)

Extrair por arquivo:

| Campo | Onde |
|---|---|
| Código site | Cabeçalho/p1. Padrões: `UF SCS01 0245-26`, `RS CZA11 3519-25`, `BR-MT-XXXX_MTYYY_A` (Phoenix), `MTBMS` (Vivo), `TT00XX` (Telecom Torres) |
| Endereço imóvel | Cláusula do objeto. **Não confundir com endereço do locador.** Só o do site |
| Operadora / Tower | Vivo (Telefônica) / Claro / TIM / Oi / Highline / SBA / IHS / American Tower / **Phoenix (PTI Brasil)** / Telxius / **Telecom Torres** / **CAW Infra** / outras |
| Tipo contrato | Locação original / cessão de crédito / DRS / aditivo |
| Coordenadas | Cláusula georreferenciada ou anexo técnico — se vier, pular geocoding |
| Aluguel | Valor mensal + índice de reajuste (IPCA padrão) |
| **Locador PF/PJ** | PF = oportunidade direta APW. PJ = checar se é torreira/agregador |
| **Cláusulas críticas** | Ver Passo 2.1 abaixo |

#### 2.1 Detecção de cláusulas anti-agregador (NOVO)

Procurar no contrato termos que indicam **blindagem contra modelo APW (lease aggregation / DRS / cessão de crédito)**. Marcar o site como **bloqueado por concorrente** se encontrar:

| Cláusula | Marcador no texto | Severidade |
|---|---|---|
| Anti-agregador de terras | "Agregador de Terras", "investimento para aquisição de direitos creditórios", "gestão de contratos de locação", multa por cessão a agregador | 🔴 alta |
| Anti-DRS / usufruto | "Direito Real de Superfície", "DRS", "Usufruto", "cessão de crédito sem anuência" + penalidade | 🔴 crítica (especialmente se multa = N× CAPEX) |
| Exclusividade telecom | "não permitir uso/instalação de outras infraestruturas de telecomunicações", "exceto administrados pela LOCATÁRIA" | 🔴 alta |
| Anti-cessão de crédito | "vedada a venda, transferência ou cessão dos créditos", "sem prévio consentimento por escrito da LOCATÁRIA" | 🟡 média (negociável) |
| **Anti-cessão pelo LOCADOR** | "é vedado ao LOCADOR realizar a cessão ou transferência parcial ou total do Contrato ou de quaisquer direitos dele decorrentes", "sem a anuência prévia e formal da LOCATÁRIA" | 🔴 alta — atinge cessão de crédito locatício, o produto APW |
| **Direito de preferência da TowerCo** | "dará preferência à LOCATÁRIA na aquisição", "venda, promessa de venda, cessão, promessa de cessão de direitos ou dação em pagamento" (art. 27 Lei 8.245/91), reforçado por cláusula de vigência contra terceiros | 🟡 alta — blinda também o DRS via terceiro adquirente |
| Vigência registrada em RGI | "averbação", "registro da sua cláusula de vigência", "registro do prazo adicional perante o Ofício de Registro de Imóveis" | 🟡 alerta (locador travado) |

⚠️ **Assimetria de cessão (sinal forte de blindagem):** quando o contrato dá à TowerCo cessão livre para si (só notifica o locador) MAS veda a cessão pelo locador — é blindagem deliberada contra agregador. Caso de referência: contrato Highline II (cláusula 9.1 cessão livre da locatária × 14.10 trava do locador).

**Quem usa essas cláusulas:** Phoenix/PTI Brasil sistematicamente, IHS em contratos novos (>2023), Highline (contratos novos vêm com anti-cessão pelo locador + direito de preferência), American Tower e SBA seletivamente, TorreSur/GTS (exclusividade telecom).
**Quem NÃO usa:** Vivo direto, Claro, TIM, Oi (contratos PF padrão sem trava de cessão).

#### 2.2 Conhecimento de torreiras — capacidade por modelo APW

A detecção de cláusula acima diz se ESTE contrato trava. Esta seção diz o que cada TowerCo costuma permitir como modelo de negócio — útil para classificar e para orientar o comercial. Importado da skill `apw-crm-key-notes-writer`.

**Regra de ouro — quem é a TowerCo:** o **comprovante de pagamento do aluguel (POP)** define a torreira, não o nome no contrato. Contratos antigos foram firmados com a operadora (TIM/Vivo/Claro/Oi) ou com torreira já incorporada; o pagador atual no POP reflete quem assumiu o site. Contrato em nome de operadora + POP de torreira = a torreira é a do POP (cessão já consumada, não é divergência). Form da diretora × contrato × POP: se conflitar, **o POP vence**.

**Matriz de capacidade por TowerCo:**

| TowerCo | C&V | Cessão de crédito | DRS | Nota |
|---|---|---|---|---|
| ATC (American Tower) | ✅ | ✅ | ✅ | Autoriza cessão e DRS sem exigir anuência prévia formal — cláusula genérica de vedação **não é bloqueador** |
| SBA | ✅ | ✅ | ✅ | Cláusula de vedação (tip. 7.2, "Infração Grave") **não bloqueia** — APW opera o SBA Program: notifica a SBA, ela concede anuência; desconto de aluguel é a contrapartida |
| Highline | ✅ | ⚠️ condicionada | ⚠️ condicionada | Quando o contrato veda cessão/DRS/alienação, **não há caminho por cessão ou DRS** — único caminho é compra do imóvel; em condomínio, inviável |
| IHS | ✅ | ❌ | ❌ | Quando o contrato veda cessão/DRS, só C&V; em condomínio inviável. Anuência teórica mas difícil — não contar com ela |
| Phoenix (PTI) | ✅ | ⚠️ | ❌ não reconhece DRS | Deal Phoenix por DRS é inviável — estruturar por compra |
| Vivo / TIM | — | ✅ | ✅ | Condicionados à ausência de vedação no contrato |
| Claro / TBSA | ✅ | ✅ condicionada | — | — |
| QMC / BTC / GTS (TorreSur) | ✅ | ❌ | ❌ | Só C&V no momento |
| Winity / Greenwich / AlfaERB | ✅ | — | — | Sem histórico — compra é possível, resto caso a caso |

Para torreiras fora da matriz, não assumir padrão — acionar `apw-telecom-real-estate-counsel`.

**Mapa de equivalência de nomes** (contrato antigo → torreira atual): Global Sites → Highline · T4U → Highline · Centennial → IHS · CSS → IHS · GTS → SBA · ZSites → Zoppone · Winity → Pátria (fundo controlador). Ao ler contrato antigo, o nome da contraparte pode ser de entidade já incorporada.

Marcar campo `bloqueios[]` no contrato + nº das cláusulas + tipo de penalidade.

Montar `contratos[]` com campos + caminho anexo + messageId origem (se Gmail).

**PDF escaneado:** parser sem texto → avisar, seguir sem o contrato. OCR só com permissão explícita.

### Passo 3 — Geocodificar endereços

Contratos sem coordenadas:

1. `places_search` com `<endereço completo>, Brasil`
2. Primeiro resultado com score alto. Validar: lat ∈ [-34, +5], long ∈ [-75, -34]. Fora → erro parsing, revisar.
3. **Ambíguo** → marcar `coordSource: "aproximada"` e parar pra confirmar:
   - Endereço sem número (ex.: "Av. Heitor Winckler") → centro da cidade, marcar aproximada
   - **Rodovia federal cruzando vários estados** (ex.: "BR-020 km 18" — passa por DF, GO, BA, CE) → Google pode jogar no estado errado. Forçar query incluindo UF explicitamente.
   - Fazendas / sítios → quase sempre nome de fazenda diferente. Marcar aproximada e pedir croqui.
   - Município repetido em UFs diferentes (Cruzeiro, Itapema, São José) → forçar UF na query

⚠️ **Regra geocoding rural/genérico**: se Google retornar um POI específico (museu, comércio, estabelecimento), **não confiar** — usar coord do centro do município + flag `coordSource: "aproximada"`. Lucas precisa confirmar com croqui antes de campo.

4. **Coords nos contratos** vêm em **DMS** (`15°18'10.69"S 55°09'38.96"W`). Converter pra decimal:
   - DD = D + M/60 + S/3600
   - Sinal: S e W → negativo
   - Ex.: 15°18'10.69"S → -(15 + 18/60 + 10.69/3600) = -15.303053

### Passo 4 — Consultar CRM via agent-browser

Antes do primeiro comando agent-browser, carregar doc atual:

```bash
agent-browser skills get core
```

**Sempre carregar `apw-chrome-agent-lean-compliance` ANTES de qualquer chamada.** Sem screenshots, sem `read_page` em painel CRM, sem retorno de texto bruto pelo console.

Garantir aba autenticada em `leadsearch2.aspx`. Sem aba → criar grupo MCP, navegar, esperar 3s pra `window.criteriavalues` popular.

**Agrupar contratos por cidade** (ou bbox compacta). Pra cada grupo:

#### 4.1 Bounding box

Extremos das coords do grupo + margem **~0.02°** (≈2 km) em cada direção. **Não usar ±0.1° fixo** — cidades grandes (Campinas, Sorocaba) retornam >5000 leads, resposta trunca. Grupo de 1: `(lat ± 0.02, lng ± 0.02)`.

Referência calibrada: São Caetano (latn=-23.55, lats=-23.68, longe=-46.50, longw=-46.64) → 1024 leads (~2 MB) com folga.

**Para sites rurais MT/MS/GO** com 0-2 leads esperados, manter ±0.02°. Bbox vazia é informação válida (sem cobertura CRM).

#### 4.2 Fetch feed

Rodar via `agent-browser` na aba autenticada:

```js
// Esperar criteriavalues popular após carregar leadsearch2.aspx
const criteria = window.criteriavalues;
if (!criteria) return { error: 'criteriavalues não populou - sessão pode estar incompleta' };

const url = '/MAPS/LeadSearch2DataFeed.aspx?criteria=' + encodeURIComponent(criteria) +
  '&type=pull&autonumber=xx&APN=xx&user=xx' +
  '&latn=' + latn + '&lats=' + lats + '&longe=' + longe + '&longw=' + longw;

const r = await fetch(url, {credentials: 'include'});
const txt = new TextDecoder('utf-8').decode(await r.arrayBuffer());
window.__leadsRaw = txt;
return { bytes: txt.length, sectionCount: (txt.match(/§/g) || []).length, httpStatus: r.status };
```

Params obrigatórios (faltou um → página erro ASP.NET, não JSON): `criteria`, `type=pull`, `autonumber=xx`, `APN=xx`, `user=xx`, `latn`, `lats`, `longe`, `longw`.

⚠️ Resposta envelopada em HTML wrapper. Delimitadores § (record) e ƒ (field) ficam dentro. Splitar por § funciona: `parts[0]` = wrapper (descartar), `parts[1..]` = registros.

⚠️ **Não retornar texto bruto pelo console agent-browser** — aciona bloqueio "Cookie/query string data". Guardar em `window.__leadsRaw`, retornar só stats (`bytes`, `sectionCount`).

⚠️ **Múltiplos sites em cidades diferentes:** rodar fetch em loop dentro de **uma única chamada `javascript_tool`** (await sequencial). Reduz chamadas de tool e mantém contexto. Não fazer N chamadas separadas.

#### 4.3 Parsing

```js
const SECTION = String.fromCharCode(167);  // §
const FUNC = String.fromCharCode(402);     // ƒ

function fixMojibake(s) {
  if (!s || !/Ã/.test(s)) return s;
  try {
    const bytes = new Uint8Array([...s].map(c => c.charCodeAt(0) & 0xff));
    return new TextDecoder('utf-8').decode(bytes);
  } catch(e) { return s; }
}

function parseLeads(raw) {
  if (!raw) return [];
  const parts = raw.split(SECTION);
  const leads = [];
  // BUGFIX v4.1 (jul/2026): regex aceita espaço opcional após vírgula entre coords.
  // O feed APW às vezes retorna "-16.74892, -43.86997" (com espaço) e a versão
  // anterior "/(-?\d+\.\d+),(-?\d+\.\d+)/" dropava esses registros silenciosamente
  // — foi assim que L1355146 (Fresh Pool, Rua Herculano Miranda, Montes Claros)
  // sumiu de uma análise real. Fix duplo:
  // (1) \s* no regex tolera espaço após a vírgula;
  // (2) fallback varre todos os campos se f[2] não tiver coords — leads
  //     Fresh Pool / Sites at Risk podem ter estrutura diferente de opps com Stage.
  const COORD_RE = /(-?\d{1,3}\.\d+),\s*(-?\d{1,3}\.\d+)/;
  for (let i = 1; i < parts.length; i++) {  // pula wrapper em parts[0]
    const f = parts[i].split(FUNC);
    if (f.length < 3) continue;

    // Tenta f[2] primeiro; se não achar coords, varre f[0..n]
    let m = f[2] ? f[2].match(COORD_RE) : null;
    if (!m) {
      for (let j = 0; j < f.length; j++) {
        const attempt = f[j] ? f[j].match(COORD_RE) : null;
        if (attempt) { m = attempt; break; }
      }
    }
    if (!m) continue;

    const ownerM = f[1].match(/Owner:[^<]*<[^>]+>([^<]+)/i);
    const stageM = f[1].match(/Stage:[^<]*<[^>]+>([^<]+)/i);
    const addrM  = f[1].match(/Address:[^<]*<[^>]+>([^<]+)/i);
    const srM    = f[1].match(/Status Reason:[^<]*<[^>]+>([^<]+)/i);
    const stM    = f[1].match(/Status:\s*<\/[^>]+>([^<]+)/i);
    const lnumM  = f[0].match(/L\d+/);

    leads.push({
      lnum: lnumM ? lnumM[0] : '',
      owner: ownerM ? ownerM[1].trim() : '',
      stage: stageM ? stageM[1].trim() : '',
      address: fixMojibake(addrM ? addrM[1].trim() : ''),
      statusReason: srM ? srM[1].trim() : '',
      status: stM ? stM[1].trim() : '',
      lat: parseFloat(m[1]),
      lng: parseFloat(m[2]),
      isLead: !stageM
    });
  }
  return leads;
}
```

#### 4.4 Match haversine

```js
function hav(a, b) {
  const R = 6371000, toRad = d => d * Math.PI / 180;
  const dLat = toRad(b.lat - a.lat), dLng = toRad(b.lng - a.lng);
  const x = Math.sin(dLat/2)**2 + Math.cos(toRad(a.lat))*Math.cos(toRad(b.lat))*Math.sin(dLng/2)**2;
  return 2 * R * Math.asin(Math.sqrt(x));
}
```

Pra cada contrato do grupo: achar lead mais próximo em `window.__leadsParsed`. **Reportar SEMPRE o lead mais próximo + distância**, mesmo que >150m — útil pro Lucas saber se "tem nada por perto" ou se "passa de 700m". Match efetivo só ≤150m.

### Passo 5 — Classificar matches

Ordem de precedência (top-down, primeiro que matar ganha):

| Categoria | Critério | Ação |
|---|---|---|
| 🚫 **Bloqueado por concorrente** (NOVO) | Site tem cláusulas anti-agregador detectadas no Passo 2.1, **independente** do match CRM | Marcar no CRM "bloqueado por concorrente". **Não prospectar.** Reportar cláusula + penalidade ao jurídico/comercial. Se a torreira é nova no radar (ex.: Phoenix no MT), alerta de inteligência competitiva |
| 🟢 **Golden** | `isLead=true` **E** Status=`Open` **E** Status Reason=`New` **E** Owner≈`Fresh Pool` **E** ≤150m | Nunca abordado, sem bloqueio. Atribuir a SD, iniciar prospecção |
| 🟡 **Em pipeline** | Stage preenchido (1-99), Owner ≠ Fresh Pool, ≤150m | Já tem dono. Confirmar com owner se contrato afeta a oportunidade |
| 🟡 **Match fora do raio** (NOVO) | Lead 150m < dist ≤ ~1000m, mesma rua/quadra/microregião | Revisar contexto. Pode ser site movido, lead com coord imprecisa, ou oportunidade adjacente |
| 🔵 **Fechado / morto** | Status=`Inactive` ou Stage=`Won`/`Lost` ou Pool=`Purged` | Nosso, perdido, ou expurgado. Pra Purged: avaliar reativação. Pra Won/Inactive: só registrar |
| ⚪ **Vivo direto / PF urgência** (NOVO) | Locatária = Vivo/Claro/TIM/Oi (não-tower), Locador = PF, sem cláusula de cessão restritiva, sem match CRM | **Prioridade alta**: tipo de contrato-alvo APW clássico, janela aberta antes que agregador chegue. Criar lead, alocar SD com urgência |
| ⚪ **Sem match (padrão)** | Nenhum lead ≤150m, sem bloqueio, locatária é tower company | Site novo. Avaliar criar lead |

### Passo 6 — Gerar entrega (e-mail HTML + opcionalmente compose)

#### 6.1 Modo padrão: HTML pronto pra colar — identidade APW Brasil

Gerar arquivo em `/mnt/user-data/outputs/email_<descricao>_<N>contratos.html` seguindo **estritamente** o brand visual APW Brasil (extraído de www.apwbrasil.com.br).

##### Paleta oficial APW Brasil

| Token | Hex | Uso |
|---|---|---|
| `apw-blue` | **`#4e89bd`** | Cor primária. Headers de tabela, headers de bloco, links, filetes divisores, accent. Vem do `meta-theme-color` do site. |
| `apw-blue-light` | `#f4f8fb` | Fundo de zebrado das linhas pares, sumário executivo, legendas |
| `apw-blue-border` | `#d6dde5` | Bordas de células, divisores sutis |
| `apw-text` | `#1f2d3d` | Texto principal (títulos, headers de bloco) |
| `apw-text-soft` | `#2c3e50` | Texto de corpo das tabelas |
| `apw-text-muted` | `#6b7a8c` | Subtítulos, metadados (cidade/UF, descrições) |
| `apw-text-mute2` | `#8a96a3` | Números de linha, traços vazios |
| `apw-bg` | `#eef2f6` | Background do e-mail (fora do card branco) |
| `apw-red` | **`#a83232`** | EXCLUSIVO da categoria "Bloqueados por concorrente" — header de tabela, cláusulas críticas |
| `apw-red-light` | `#fdf3f3` | Zebrado das linhas de Bloqueados |
| `apw-amber-bg` | `#fff8e7` | Fundo de linha Vivo direto / PF urgência |
| `apw-amber-border` | `#e8b94e` | Borda das células Vivo direto / PF urgência |
| `apw-amber-accent` | **`#d68910`** | Borda-esquerda 4px da linha Vivo direto (sinal de prioridade) |
| `apw-amber-text` | `#a04a00` | Texto "URGÊNCIA" |
| `apw-green` | `#2b8a3e` | Status "precisa" das coordenadas |
| `apw-amber-warn` | `#a06b1a` | Status "aproximada" das coordenadas |
| `apw-footer` | `#1f2d3d` | Faixa de rodapé escura com razão social |

##### Tipografia

**Família única:** `Arial, Helvetica, sans-serif` (corresponde ao site APW Brasil — não usar Georgia serif). Para coords em tabela: `Consolas, 'Courier New', monospace`.

**Hierarquia:**
- H1 título principal: 24px, weight normal, `#1f2d3d`, line-height 1.3
- Headers de bloco: 18px, weight 600, `#1f2d3d`
- "Categoria 0X": 10px, letter-spacing 3px, uppercase, `#4e89bd` bold (vermelho `#a83232` no bloco Bloqueados)
- Headers de tabela: 11px, letter-spacing 1px, uppercase, weight bold, texto branco sobre fundo `#4e89bd` (ou `#a83232` no Bloqueados)
- Corpo de tabela: 13px, line-height 1.5
- Metadados secundários: 11-12px, `#6b7a8c`

##### Estrutura obrigatória (top→bottom)

1. **Header com logo APW**
   - Fundo branco, padding 24px/36px, **borda inferior 4px sólida `#4e89bd`**
   - Coluna esquerda: `<img src="https://www.apwbrasil.com.br/wp-content/uploads/2020/11/Logo-Brasil.svg" alt="APW Brasil" width="180">` (SVG oficial do CDN APW)
   - Coluna direita alinhada à direita: tag "ANÁLISE COMERCIAL INTERNA" em `#4e89bd` + data abaixo em `#6b7a8c`

2. **Título e subtítulo** (padding 32px/36px)
   - H1 com o nome da análise
   - Subtítulo em itálico `#6b7a8c` com escopo/origem (ex.: "Batch MyTower + contratos adicionais · Vivo direto / Phoenix MT")

3. **Sumário executivo** em caixa `#f4f8fb` com borda-esquerda 4px `#4e89bd`, título "SUMÁRIO EXECUTIVO" em uppercase azul

4. **Blocos por categoria**, cada um com cabeçalho padrão:
   ```
   ┌─ "Categoria 0X" (10px uppercase #4e89bd letter-spacing 3px) ─
   ├─ Nome da categoria (18px weight 600 #1f2d3d)
   └─ Borda inferior 2px sólida #4e89bd
   ```
   Ordem (sem alteração de v2):
   1. Match efetivo no CRM — ação imediata
   2. Lead existente fora do raio direto — revisar contexto
   3. Sem cobertura CRM — candidatos a lead novo
   4. Bloqueados por concorrente — não prospectar (header em **vermelho `#a83232`**, não azul)
   5. Acesso rápido — Coordenadas dos 9 sites

5. **Linha de urgência Vivo direto / PF** dentro da Categoria 3:
   - Fundo `#fff8e7`, todas as bordas `#e8b94e`, **borda-esquerda 4px sólida `#d68910`** na primeira célula
   - Texto "URGÊNCIA" em `#a04a00` bold

6. **Bloco de Coordenadas** com 5 colunas: `#` (zero-padded), Site, Lat-Lng (monospace), Maps (link `abrir ›` em `#4e89bd` bold sem underline), Precisão (verde/âmbar)
   - URL do link: `https://www.google.com/maps?q=LAT,LNG`
   - Linha Vivo direto reutiliza o mesmo destaque âmbar deste bloco também

7. **Legenda das coords** em caixa `#f4f8fb` com borda-esquerda 3px `#4e89bd`

8. **Próximos passos** com numeração 01/02/03 grande em `#4e89bd` bold à esquerda

9. **Assinatura** com filete superior `#d6dde5`:
   ```
   Abs,
   Lucas Minozzo
   APW Brasil · Aquisições
   ```

10. **Footer escuro** (`#1f2d3d`, padding 18px/36px) com:
    - Esquerda: "APWireless Brasil Invest. Imob. LTDA" branco bold + "Análise interna · Confidencial" cinza 10px
    - Direita: link `www.apwbrasil.com.br` em cinza claro

##### Compatibilidade obrigatória (e-mail clients)

- Tabelas aninhadas com `cellpadding="0" cellspacing="0" border="0"`
- Inline styles em **todos** elementos (Outlook desktop strippa `<style>`)
- Sem CSS variables, sem flexbox, sem grid
- Fontes universais (Arial, Consolas/Courier New) — **nunca usar Google Fonts ou fontes externas**
- Largura fixa **760px max**, role="presentation" nas tabelas estruturais
- Logo SVG do CDN APW funciona em Gmail/Apple Mail/Outlook Web. Se destinatário for Outlook desktop e logo não renderizar, ter plano B: hostar PNG internamente ou usar fallback em texto "APW Brasil" estilizado

Apresentar arquivo via `present_files`. Informar tamanho aproximado (referência: 9 sites = ~31 KB).

#### 6.2 Modo opcional: `message_compose_v1`

Se Lucas pedir explicitamente "compose o e-mail" ou "manda pelo Mail", usar `message_compose_v1` com `kind=email`. Caso contrário, o HTML pronto resolve.

**Para:** `lminozzo@apwbrasil.com.br`. CC: perguntar antes (Max? Diogo? Diretor regional? Jurídico se houver cláusulas Phoenix? Roana?).

**Assunto:** `Cruzamento <N> contratos × CRM APW — ações por categoria` ou variante com a data/origem.

### Passo 7 — Confirmação chat

Após gerar e apresentar:

- Tabela resumo contratos por categoria (texto compacto no chat).
- Lista Golden + Vivo-direto-PF com lnum + distância + urgência.
- Lista Bloqueados com cláusula + penalidade.
- Avisos: endereços ambíguos pendentes, anexos não parseáveis, bboxes >2000 leads (sinal pra particionar), coords aproximadas que precisam de croqui.
- Próximas ações sugeridas (criar leads, marcar bloqueados no CRM, repassar inteligência competitiva ao comercial).

---

### Passo 8 — Ação no CRM: criar pin / marcar L existente (opcional, requer autorização)

A análise (Passos 1-7) é leitura. Criar ou editar lead é **escrita no CRM** — exige confirmação explícita do Lucas de que a **criação/edição** (não só a leitura) está coberta pela autorização do Risk Officer. Leitura autorizada ≠ escrita autorizada. Pedir antes, sempre.

**Criar pin (lead novo)** — para sites da categoria "Sem cobertura" / "Vivo direto-PF". O `leadsearch2.aspx` não tem endpoint de criação; o lead nasce pela interface do mapa: **botão direito no ponto → "criar pin" → formulário** abre para preencher. Preencher com os dados do contrato já extraídos (endereço, operadora, locador, aluguel, coordenada).
- ⚠️ **Nunca criar pin com coordenada aproximada.** Lead com lat/long imprecisa vira match falso permanente e manda SD ao lugar errado. Site com coord aproximada → segurar, pedir croqui/endereço exato à MyTower antes.
- ⚠️ Site **bloqueado por concorrente não recebe pin** — não se cria lead para site inviável.

**Marcar L existente como bloqueado** — quando o cruzamento acha um lead já cadastrado (≤150m) num site que a análise classificou como bloqueado. É **edição** de registro existente no Dynamics 365 (não o fluxo do mapa) — abrir o lead e ajustar status/status reason. Ação urgente: lead bloqueado em pool de prospecção (Fresh Pool etc.) faz a APW alocar SD para site inviável. Sinalizar isso com destaque.

**Deep-link:** o `leadsearch2.aspx` **não tem deep-link por coordenada** — abre sempre a tela inicial do mapa. Para link por linha em planilha/relatório, usar Google Maps. Link direto de lead no Dynamics exige o **GUID interno** do registro (não o L-number visível).

---

## Notas operacionais

- **Idempotência (fluxo Gmail):** log em `/home/claude/contratos_max/_processados.json`. messageId já processado → sinalizar, não duplicar.
- **Política IA APW:** confirmar com Lucas se fluxo está coberto pela autorização atual antes de produção. Skill `apw-chrome-agent-lean-compliance` é mandatória pra qualquer toque em CRM/Dynamics. **Leitura e escrita são escopos distintos** — autorização para consultar não cobre criar/editar lead; confirmar separado.
- **Aba do leadsearch2 pode fechar entre chamadas** — se `tabId no longer exists`, recriar grupo MCP, renavegar, esperar `criteriavalues` popular (~5s) antes de novo fetch.
- **Limite feed:** bbox >2000 leads ou >5 MB → particionar em sub-bboxes. Truncamento silencioso é pior dos mundos.
- **Mojibake:** `Address` vem em UTF-8 mal lido como Latin-1 às vezes. `fixMojibake` resolve. `Ã§` / `Ã£` no e-mail final → rodar de novo.
- **Coords aproximadas + sem L-number:** sinalizar fortemente. Mandar Lucas/Diogo confirmar antes de campo. Sites Madalena/CE típicos: Google embaralha com Brasília-DF (mesma rodovia BR-020).
- **bbox estreita com sectionCount 0 é resultado válido** (sem cobertura CRM). Para reportar o lead mais próximo mesmo assim, rerodar com bbox ampliada (±0.1°). O wrapper HTML do feed (`<!DOCTYPE html><form...>`) é normal — não confundir com página de erro.
- **Triagem visual de torre é verificação humana.** O Claude não tem visão confiável para confirmar "há torre" em satélite/Street View — não marcar isso por conta própria. Montar o painel com links de satélite (`maps/@LAT,LNG,250m/data=!3m1!1e3`) e Street View (`maps?q=&layer=c&cbll=LAT,LNG`) e deixar a coluna de status para o Lucas/Diogo preencherem.
- **Cláusulas anti-agregador são informação estratégica:** quando detectadas em torreira nova (ex.: Phoenix expandindo MT, Highline com contratos novos travados), reportar como **inteligência competitiva** ao bloco de Ações. Não só "não prospectar este site" — também "a torreira X está movendo na região Y, alertar comercial".
- **HTML do e-mail:** sempre testar abrindo no navegador antes de assumir que renderiza. Outlook desktop é o pior cliente; se renderiza nele, renderiza em qualquer um.

## Encadeamento com outras skills

- `pdf-reading` — anexos PDF
- `docx` / `xlsx` — anexos não-PDF; `xlsx` também para a planilha consolidada do batch (dados do caso moram aqui, não na skill)
- `agent-browser` — `leadsearch2.aspx` (sempre `skills get core` antes da 1ª chamada)
- **`apw-chrome-agent-lean-compliance`** — MANDATÓRIA antes de qualquer ação CRM
- `apw-telecom-real-estate-counsel` — quando detectar cláusulas anti-agregador, encadear pra análise jurídica detalhada
- `apw-crm-key-notes-writer` — origem da matriz de torreiras do Passo 2.2; usar para gravar Key Notes / Pricing Option e montar dossiê quando um site do batch virar deal
- `caveman-compress` — este SKILL.md está em formato comprimido. Backup natural em `SKILL.md.original.md`

## Changelog

- **v4.1 (jul/2026) — BUGFIX parsing:** `parseLeads` corrigido para não dropar registros com coordenadas no formato `-16.748, -43.869` (espaço após vírgula). Bug original: regex `/(-?\d+\.\d+),(-?\d+\.\d+)/` sem `\s*` fazia match falhar silenciosamente — L1355146 (Fresh Pool, Rua Herculano Miranda, Montes Claros/MG) foi perdido numa análise real por isso. Fix: `COORD_RE = /(-?\d{1,3}\.\d+),\s*(-?\d{1,3}\.\d+)/` + fallback que varre todos os campos `f[0..n]` caso `f[2]` não tenha coords (leads Fresh Pool/Sites at Risk podem ter estrutura diferente de opps com Stage). Adicionado `{1,3}` para a parte inteira do número (evita falso-match em strings longas).
- **v4 (mai/2026):** Passo 2.1 expandido — detecção de **anti-cessão pelo locador** e **direito de preferência da TowerCo** (caso Highline II), regra da assimetria de cessão como sinal de blindagem; Highline e TorreSur/GTS adicionadas à lista de quem usa cláusulas restritivas. Nova seção **2.2 Conhecimento de torreiras** importada da `apw-crm-key-notes-writer` — regra de ouro do POP, matriz de capacidade C&V/Cessão/DRS por TowerCo (ATC, SBA, Highline, IHS, Phoenix, Vivo/TIM, Claro/TBSA, QMC/BTC/GTS, Winity/Greenwich/AlfaERB), mapa de equivalência de nomes (Global Sites→Highline etc.). Novo **Passo 8** — fluxo de criar pin (botão direito no mapa → formulário) e marcar L existente como bloqueado, com a distinção leitura×escrita de autorização. Notas operacionais novas: aba do leadsearch2 fechando entre chamadas, bbox vazia como resultado válido, wrapper HTML do feed não é erro, triagem visual de torre é verificação humana (Claude não confirma torre por imagem), deep-link inexistente no leadsearch2.
- **v3 (mai/2026):** identidade visual APW Brasil aplicada — paleta extraída do site oficial (`#4e89bd` primária + `#a83232` exclusivo para Bloqueados); tipografia Arial/Helvetica (não mais Georgia serif); logo oficial APW Brasil no header (SVG do CDN apwbrasil.com.br); footer escuro `#1f2d3d` com razão social "APWireless Brasil Invest. Imob. LTDA" + link www.apwbrasil.com.br; largura aumentada 720→760px; header com tag "ANÁLISE COMERCIAL INTERNA" + data à direita; assinatura completa "Lucas Minozzo · APW Brasil · Aquisições"; tokens de cor nomeados e documentados em tabela; categoria Bloqueados ganhou header vermelho próprio (diferenciação visual forte). Especificação visual agora prescritiva, não sugestiva.
- **v2 (mai/2026):** adicionado fluxo batch direto (sem Gmail); detecção de cláusulas anti-agregador no Passo 2.1; nova categoria "Bloqueado por concorrente" com precedência sobre match; nova categoria "Vivo direto / PF urgência" com flag de timing; entrega padrão virou HTML pronto pra colar (não mais `message_compose_v1` default); bloco "Acesso rápido — Coordenadas" com links Google Maps; regras de geocoding rural/genérico (rodovia federal, fazenda, sem número); conversão DMS→decimal documentada; mandato de skill `apw-chrome-agent-lean-compliance`; loop fetch único em vez de N chamadas; reporte de lead mais próximo mesmo >150m.
- **v1:** versão inicial fluxo Gmail-only.
