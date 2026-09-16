---
name: apw-onhold-reassessment
description: Reavalia o estoque de oportunidades ON HOLD da APW Brasil no Dynamics 365 para identificar deals reabordáveis hoje — cruza hold spot (statuscode), on hold reason, on hold date, RVP/Legal Comments, torreira, operadora e landlord type, e classifica cada deal em buckets de reabordagem segundo as regras vigentes de relacionamento com torreiras (SBA/GTS destravou; TBSA e Claro não-condomínio reabordáveis via DRS; Highline fecha; IHS/CSS/Centennial só compra de terreno). Use SEMPRE que o Lucas pedir "analisa os deals on hold", "o que dá pra reabordar", "reassessment dos holds", "old deals assessment", "por que esse deal parou", "quais holds venceram", "recicla o pipeline parado", "quem são essas opps em hold e em que pool estão", ou colar view do Dynamics com deals On Hold / statuscode Pending Carrier Recognition. NÃO use para dossiê de um único deal (apw-deal-dossier), consulta pontual ao CRM (apw-dynamics-copilot), forensics de atividades (apw-opp-activity-forensics) nem reporte diário (apw-reporte-crm-diario).
---

# APW On Hold Reassessment

Pipeline de reciclagem do estoque On Hold do Dynamics 365 da APW Brasil. Responde três perguntas: **por que cada deal parou**, **com quem ele parou** (torreira/operadora/pool) e **o que dá pra reabordar hoje** dado o estado atual do relacionamento com as torreiras.

Herda TODAS as regras de compliance da `apw-dynamics-copilot` (sessão autenticada do navegador, zero screenshot em *.dynamics.com, dados em memória, nunca persistir dump bruto em disco) e da `apw-chrome-agent-lean-compliance`. Leia ambas se ainda não estiverem no contexto.

---

## Universo de dados

**Tenant**: `apwireless.crm.dynamics.com` (verificar aba ativa; há também apwbrasil.crm2 e apw.crm).

**Statuscodes de On Hold** (opportunity.statuscode — usar valores numéricos, não label):

| Valor | Label |
|---|---|
| 2 | On Hold |
| 870410008 | On Hold - Pending Competitor Funding |
| 870410009 | On Hold - Pending Consolidation Verification |
| 870410012 | On Hold - Pending Carrier Recognition/Litigation |
| 870410013 | On Hold - Pending Carrier Negotiation with Site Owner |

**Filtro de país Brasil**: `apwip_countryfilter eq {FEA663A6-5B28-E211-BCD6-00155D00D805}`

**Filtro de estágio — REGRA PADRÃO (pedido explícito do Lucas, 03/07/2026): considerar SOMENTE deals em Stage 7 para frente.** O racional: Stage 7+ = proposta comercial aceita em diante (DD/closing) — são os holds com valor real investido. Stage <7 em hold é ruído de qualificação (era ~80% do universo bruto e quase todo o legado litigation 2013–2017). Valores numéricos de `apwip_opportunitystage` a incluir:

| Valor | Stage |
|---|---|
| 100000006 | Stage 7 |
| 870410006 | Stage 7.1 |
| 100000007 | Stage 8 |
| 100000008 | Stage 9 |
| 870410000 | Stage 10 |
| 870410001 | Stage 11 |
| 870410007 | Stage 99 |
| 870410008 | Stage 100 |

Só analisar o universo completo (todos os stages) se o Lucas pedir explicitamente ("varre tudo", "inclui os stages iniciais") — e nesse caso apresentar os dois cortes separados, nunca misturados. Ordem de grandeza para sanity check (07/2026): Stage 7+ ≈ 108 deals (Stage 9 concentra ~65%, statuscode quase todo "On Hold" puro, ~80% com dono ativo); universo completo ≈ 573 (75% legado litigation, 83% órfão em pools).

**Campos que importam** (descobertos e validados em produção 07/2026):

| Campo | Entidade | O que é |
|---|---|---|
| `statuscode` | opportunity | Hold spot (formatted value dá o label) |
| `new_onholdcategoryreason` | opportunity | On Hold Reason (Picklist: Title Issues, Seller Renegotiation, SNDA Not Obtainable, ROFR, Other...) |
| `new_onholddate` | opportunity | On Hold Date (frequentemente é data de RETOMADA programada, não de entrada) |
| `apwip_onholddatelegal` / `lastonholdtime` | opportunity | Datas de hold alternativas (fallback) |
| `new_rvpcommentsnew` | opportunity | RVP/Legal Comments — o motivo REAL em texto livre |
| `apwip_surrenderreasonopp` | opportunity | Surrender reason (quando preenchido) |
| `ownerid` | opportunity | Dono/pool (formatted value) |
| `apwip_carrier` | lead (via `apwip_leadopportunityid`) | Operadora (string livre) |
| `apwip_towercompany` | lead | Torreira (Lookup — MAS ~83% vazio) |
| `apwip_landlordtype` | lead | Private Owner / Associations-Cooperative / Business... |
| `apwip_propertytype` | lead | Tipo de imóvel |
| `address1_city` | account (via `customerid`) | Praça |

---

## Armadilhas conhecidas (custaram tempo — não repita)

1. **A rota `?fetchXml=` da Web API corta em 5.000 registros SEM `@odata.nextLink`.** Nunca puxe a view inteira (ALL OPPS tem 5.000+) esperando paginar. Filtre pelos 5 statuscodes de hold direto no FetchXML — o universo On Hold Brasil cabe numa página (~600).
2. **`new_onholdcategoryreason` está vazio em ~84% dos registros** e **`apwip_towercompany` (lead) vazio em ~83%**. A verdade está no texto: infira a torreira por regex sobre `nome + rvp + carrier` (padrão abaixo). Sempre rotule o resultado como *inferido*.
3. **Formatted values**: sem o header `Prefer: odata.include-annotations=*` você recebe só números de picklist e GUIDs de lookup. Ler via `campo@OData.Community.Display.V1.FormattedValue`.
4. **`javascript_tool` não espera Promise**: use o padrão `window.__var = 'pending'; (async()=>{...; window.__var = resultado})(); 'kicked'` e leia `window.__var` na chamada seguinte. Saída trunca ~1.500 chars — devolva fatias (`slice`) e agregados, nunca o array inteiro.
5. **A aba pode morrer no meio** (Lucas fecha o navegador): não dependa de estado acumulado em `window.*` entre etapas longas — cada etapa deve ser re-executável do zero.
6. **Criação de view pessoal (userquery) via POST `/userqueries`**: a UCI **rejeita silenciosamente** (fallback pra view default) layoutxml com quebras de linha/indentação. Formato exigido: **single-line**, `icon="false"` (não `icon="1"`), e `disableSorting="1"` em toda cell de entidade linkada (`alias.attribute`). O deep-link por URL pode continuar redirecionando por cache do seletor mesmo com a view válida — o caminho garantido é trocar pela lista do seletor (a view aparece em "My Views"); via automação, o item `role="menuitemradio"` só responde à sequência completa pointerdown→mousedown→pointerup→mouseup→click (`.click()` sintético não troca a view). Campos mínimos do POST: `name`, `returnedtypecode:'opportunity'`, `querytype:0`, `fetchxml`, `layoutxml`. View criada em produção: "ON HOLD REASSESSMENT - Stage 7+ (BR)" (userquery do Lucas) — atualizar via PATCH em vez de criar duplicata.

---

## Mapeamento torreira (regex de inferência, nesta ordem)

```
/gts/                    → SBA (via GTS)
/sba/                    → SBA
/torres do brasil|tbsa/  → TBSA
/highline/               → Highline
/centennial/             → IHS (via Centennial)
/\bcss\b/                → IHS (via CSS)
/\bihs\b/                → IHS
/american tower|\batc\b/ → ATC
/phoenix/ /qmc/          → Phoenix / QMC
/\bclaro\b/              → Claro (direto)   [carrier, sem torreira identificada]
/\bvivo\b|telefonica/    → Vivo (direto)
/\btim\b/                → TIM (direto)
/\boi\b/                 → Oi (direto)
senão                    → (indefinida)
```

Condomínio: `llType` contém `condom|associa` OU nome/propType contém `condom`. Quando `llType` vazio, o nome é proxy — rotular como inferido.

## Regras de reabordagem (estado 07/2026 — CONFIRMAR com Lucas se mudaram)

| Bucket | Critério | Ação |
|---|---|---|
| 🟢 Reabordar JÁ | Torreira SBA, GTS ou Highline | SBA destravou (canal Murilo Gonçalves); Highline fecha normal |
| 🟢 Reabordar via DRS | TBSA **ou** Claro (direto), e **não**-condomínio | Direito Real de Superfície no terreno |
| 🔴 Travado | TBSA/Claro em condomínio | Cessão segue travada |
| 🟡 Só compra de terreno | IHS (inclui CSS e Centennial) | Reabordar apenas se LL vende o terreno |
| 🟡 Política a confirmar | ATC | Perguntar ao Lucas a política vigente |
| ⚪ Enriquecer | (indefinida) | RVP vazio + lead vazio → precisa pesquisa |

## Pipeline

1. Confirmar aba autenticada em `*.dynamics.com` (`tabs_context_mcp`; se não houver, pedir pro Lucas abrir).
2. FetchXML: opportunity com os 5 statuscodes + país Brasil + **stage 7+ (tabela de valores acima — filtro padrão)** + links lead/account (campos da tabela acima), header `Prefer: odata.include-annotations=*`.
3. Em memória no navegador: inferir torreira, flag condomínio, montar buckets, distribuições (hold spot, hold reason, torreira, pool/owner, praça, ano do hold).
4. Separar **holds recentes** (hold date ≥ ano corrente −2): esses têm dono ativo e RVP real — motivo costuma ser do LL (title issues, inventário, SUB/AGE reprovada, recuperação judicial), não da torreira. Sinalizar hold dates **vencidos** (data de retomada no passado).
5. Entregar no chat: números agregados + buckets + lista priorizada (🟢 primeiro, agrupada por pool/praça) + caveats de inferência. Estrutura: (1) o que está acontecendo, (2) torreira×operadora, (3) buckets, (4) recentes/vencidos, (5) riscos da inferência, (6) próximos passos.
6. **Nunca** gravar nada no CRM nesta skill. Se o Lucas quiser mover deals de pool ou reabrir, isso é ação separada com confirmação explícita (apw-dynamics-copilot, field-updates).

## Saída — o que NÃO fazer

- Não despejar 600 linhas no chat: agregados + top N + listas acionáveis (🟢) apenas.
- Não criar arquivo com dump bruto do CRM (nomes de LL, valores). Arquivo final só com agregados aprovados pelo Lucas.
- Não tratar "On Hold - Pending Carrier Recognition/Litigation" (legado 2013–2017) como problema vivo: o hold spot diz por que parou NA ÉPOCA. Antes de reabordar em massa, amostrar RVPs e cruzar vida do site (Anatel/decommission).
