---
name: apw-pipeline-reativacao
description: >-
  Reativa pipeline frio da APW Brasil varrendo pools esquecidas há 2+ anos:
  Purged Pool, Surrender Pool, Sites at Risk, Carrier Owned, Tower Company Owned.
  Varre Stage 5 antigos contando pricing options e hot signals. Regras de
  torreira: SBA=GTS, IHS=CSS=Centennial, ATC=Telxius=BR Torres,
  Highline/Phoenix/PTI. Prioridade máxima: deals SBA/GTS surrendered/purgados
  (APW não fechava SBA antes — AGORA FECHA). Use SEMPRE com: "pipeline frio",
  "reativar pipeline", "cold deals", "purged pool", "surrender pool", "pools
  frias", "sites at risk", "carrier owned", "tower company owned", "deals
  parados 2 anos", "Stage 5 antigos", "SBA que travou", "GTS abandonado",
  "filtro SBA", "rent range", "prospecção Anatel", "campanha de cartas", "cold
  pipeline", "oportunidades esquecidas". NÃO use para ON HOLD
  (apw-onhold-reassessment), dossiê único (apw-deal-dossier) ou reporte diário
  (apw-reporte-crm-diario).
---

# APW Pipeline Reativação

Skill de reciclagem de pipeline frio da APW Brasil. Varre pools que ficam
esquecidas no CRM — deals que saíram do radar de diretores, foram surrendered,
ou ficaram estagnados em Stage 5 sem nunca fechar.

**Lógica central:** não é sobre stage, é sobre POOLS e TEMPO. Um deal na
Purged Pool há 3 anos pode ser mais quente que um Stage 1 de 6 meses. A pool
conta a história de como o deal saiu do pipeline ativo.

Herda **TODAS** as regras de compliance de `apw-chrome-agent-lean-compliance`
(zero screenshot em domínios APW/Dynamics, dados em memória, Web API autenticada
via sessão do navegador) e de `apw-dynamics-copilot` (Web API first, FetchXML
como segundo recurso, ag-grid como terceiro). Carregue as duas antes de qualquer
consulta ao Dynamics.

---

## Regras de consolidação de torreiras (CRÍTICO — memorizar)

Antes de qualquer análise, internalizar estas equivalências. Um deal pode
mencionar o nome antigo; traduzir para o atual antes de qualquer decisão:

| Nome antigo / alternativo | Nome atual | Viabilidade APW |
|---|---|---|
| GTS | **SBA** (SBA adquiriu GTS) | ✅ REABORDAR — APW agora fecha com SBA |
| ACF (código interno) | **SBA** (inferir) | ✅ REABORDAR — confirmar torreira |
| CSS, Centennial | **IHS** (IHS adquiriu ambos) | ⚠️ Analisar caso a caso |
| Telxius, BR Torres | **ATC** (ATC adquiriu ambos) | ⚠️ Analisar caso a caso |
| Highline | **Highline** | ✅ REABORDAR — bom parceiro |
| Phoenix Tower | **Phoenix Tower** | ✅ REABORDAR — bom parceiro |
| PTI | **PTI** | ✅ REABORDAR — bom parceiro |

> **ALERTA SBA/GTS:** No passado, a APW Brasil NÃO fechava deals com SBA/GTS.
> Hoje FECHA. Isso significa que qualquer deal que foi surrendered, purgado ou
> abandonado com SBA/GTS como motivo de travamento é um **candidato direto de
> reativação**. Esses casos têm prioridade máxima na varredura.

---

## Detecção de modo

Identifique o que o Lucas quer e anuncie o modo antes de começar.
O Lucas pode pedir múltiplos modos na mesma sessão — rodá-los em sequência.

| Sinal no pedido | Modo | Skill principal |
|---|---|---|
| "pools frias", "purged", "surrender", "sites at risk", "carrier owned", "tower owned", "deals parados", "reativar pipeline", sem contato 2+ anos | **MODO 1 — Pools Frias** | Esta skill + apw-dynamics-copilot |
| "Anatel", "condomínios", "cartas", "campanha", "ClassInfraFis Rooftop" | **MODO 2 — Prospecção Anatel** | apw-erb-towerco-triage (delegação direta) |
| "Stage 5", "pricing options", "propostas feitas", "deals Stage 5 antigos" | **MODO 3 — Stage 5 Antigos** | Esta skill + apw-dynamics-copilot |
| "SBA", "GTS", "rent range", "R$4 a 8k", "SBA que travou" | **MODO 4 — SBA/GTS Revival** | Esta skill + apw-email-sba-murilo |

> Modo 4 (SBA/GTS Revival) pode ser combinado com Modos 1 e 3 — é uma lente
> que se aplica sobre os resultados dos outros modos, não um fluxo isolado.

---

## Pré-requisito geral

1. Leia `apw-chrome-agent-lean-compliance` (regras de browser e compliance).
2. Confirme aba autenticada em `apwbrasil.crm2.dynamics.com` via `tabs_context_mcp`.
   Se não houver, peça ao Lucas abrir antes de continuar.
3. Descubra os GUIDs das pools-alvo com a sonda de teams/users abaixo.
4. Confirme stage values com a sonda de stages.

### Sonda de pools (teams/queues)

```js
// Busca teams/queues com nomes de pools conhecidas
window.__poolsProbe = 'pending';
(async () => {
  try {
    const r = await fetch(
      `${window.location.origin}/api/data/v9.2/teams` +
      `?$select=teamid,name,teamtype` +
      `&$filter=contains(name,'urge') or contains(name,'urrender') or contains(name,'isk') or contains(name,'arrier') or contains(name,'ower') or contains(name,'ool')` +
      `&$top=50`,
      { headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}}
    );
    const d = await r.json();
    window.__poolsProbe = JSON.stringify((d.value||[]).map(t=>({id:t.teamid,name:t.name,type:t.teamtype})));
  } catch(e) { window.__poolsProbe = 'error: '+e.message; }
})();
'pools probe kicked'
// Na chamada seguinte: window.__poolsProbe
```

Se pools forem `systemusers` e não `teams`, adaptar:
`/api/data/v9.2/systemusers?$select=systemuserid,fullname&$filter=contains(fullname,'Pool')`

---

## MODO 1 — Pools Frias (Purged + Surrender + outras)

### Hierarquia de prioridade das pools

| Pool | Prioridade | Raciocínio |
|---|---|---|
| **Purged Pool** | 🔥 Alta | Saiu do pipeline de um diretor após 3 meses sem contato — não foi uma decisão deliberada de desistir. O LL pode ainda estar disponível. |
| **Sites at Risk** | 🔥 Alta | Site com risco identificado mas não resolvido — pode ter mudado de situação. |
| **Tower Company Owned** | 🌡️ Média | Torreira é dona → restrições contratuais, mas dependendo da torreira (SBA, Highline, Phoenix) vale reabordar. |
| **Carrier Owned** | 🌡️ Média | Operadora é dona → restrições, mas algumas operadoras fazem sale & leaseback. |
| **Surrender Pool** | ❄️ Baixa | Alguém apertou o botão de surrender — houve uma decisão. Mas se o motivo foi SBA (APW não fechava), agora é diferente. |

### Query principal — Pools frias por 2+ anos

```js
// MODO 1 — Varredura de opps em pools frias há 2+ anos
// Substituir os GUIDs_* pelos valores encontrados na sonda de pools
window.__poolsFrias = 'pending';
(async () => {
  try {
    const DATA_2A = '2024-07-15T00:00:00Z'; // hoje − 2 anos (ajustar data)
    const BRASIL  = 'FEA663A6-5B28-E211-BCD6-00155D00D805';

    // OData não suporta 'in' nativo — usar múltiplos OR com GUIDs reais das pools
    const poolFilter = `(_ownerid_value eq GUID_PURGED or _ownerid_value eq GUID_SURRENDER or _ownerid_value eq GUID_SITES_AT_RISK or _ownerid_value eq GUID_CARRIER_OWNED or _ownerid_value eq GUID_TOWER_OWNED)`;

    const filter = [
      poolFilter,
      `apwip_countryfilter eq ${BRASIL}`,
      `statecode eq 0`,
      `modifiedon le ${DATA_2A}`
    ].join(' and ');

    const url = `${window.location.origin}/api/data/v9.2/opportunities` +
      `?$filter=${encodeURIComponent(filter)}` +
      `&$select=opportunityid,name,apwip_opportunitystage,modifiedon,createdon,_ownerid_value,new_rvpcommentsnew` +
      `&$expand=apwip_leadopportunityid($select=apwip_carrier,apwip_towercompany,address1_city,apwip_monthlyrent)` +
      `&$orderby=modifiedon asc` +
      `&$top=200`;

    const r = await fetch(url, {
      headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.include-annotations=*'}
    });
    const d = await r.json();
    const count = d.value?.length || 0;

    // Aplicar regex de torreiras em memória
    const sbaPat  = /\b(sba|gts|acf)\b/i;
    const highPat = /highline|phoenix|pti/i;
    const ihsPat  = /\b(ihs|css|centennial)\b/i;
    const atcPat  = /\b(atc|telxius|br\s*torres)\b/i;

    const enriched = (d.value || []).map(v => {
      const txt = [
        v.name, v.new_rvpcommentsnew,
        v.apwip_leadopportunityid?.apwip_carrier,
        v.apwip_leadopportunityid?.['apwip_towercompany@OData.Community.Display.V1.FormattedValue']
      ].filter(Boolean).join(' ');

      let torreira = 'desconhecida';
      if (sbaPat.test(txt))       torreira = 'SBA/GTS';
      else if (highPat.test(txt)) torreira = 'Highline/Phoenix/PTI';
      else if (ihsPat.test(txt))  torreira = 'IHS/CSS/Centennial';
      else if (atcPat.test(txt))  torreira = 'ATC/Telxius/BR Torres';

      return {
        id: v.opportunityid,
        name: v.name?.slice(0,50),
        modified: v.modifiedon?.slice(0,10),
        stage: v['apwip_opportunitystage@OData.Community.Display.V1.FormattedValue'],
        pool: v['_ownerid_value@OData.Community.Display.V1.FormattedValue'],
        city: v.apwip_leadopportunityid?.address1_city,
        rent: v.apwip_leadopportunityid?.apwip_monthlyrent,
        torreira
      };
    });

    window.__poolsFrias = JSON.stringify({
      total: count,
      nextLink: d['@odata.nextLink'] ? 'sim' : 'não',
      sba_gts: enriched.filter(v=>v.torreira==='SBA/GTS').length,
      highline_etc: enriched.filter(v=>v.torreira==='Highline/Phoenix/PTI').length,
      ihs_etc: enriched.filter(v=>v.torreira==='IHS/CSS/Centennial').length,
      atc_etc: enriched.filter(v=>v.torreira==='ATC/Telxius/BR Torres').length,
      desconhecida: enriched.filter(v=>v.torreira==='desconhecida').length,
      top_sba: enriched.filter(v=>v.torreira==='SBA/GTS').slice(0,10),
      top_outros: enriched.filter(v=>v.torreira!=='SBA/GTS').slice(0,10)
    });
    window.__poolsFriasAll = enriched; // manter em memória para scoring
  } catch(e) { window.__poolsFrias = 'error: '+e.message; }
})();
'pools query kicked'
// Na chamada seguinte: window.__poolsFrias
```

### Passo 2 — Puxar atividades (top 50 candidatos)

Priorizar os candidatos SBA/GTS primeiro, depois os de alta prioridade.
Para cada deal, puxar as **últimas 5 atividades** via tasks endpoint:

```js
// Buscar atividades de uma opp — rodar em lotes de 10
window.__acts = 'pending';
(async () => {
  const OPP_GUID = 'SUBSTITUIR';
  try {
    const r = await fetch(
      `${window.location.origin}/api/data/v9.2/tasks` +
      `?$filter=_regardingobjectid_value eq ${OPP_GUID}` +
      `&$orderby=createdon desc&$top=5` +
      `&$select=subject,description,createdon,_ownerid_value`,
      { headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}}
    );
    const d = await r.json();
    window.__acts = JSON.stringify(d.value?.map(a => ({
      subject: a.subject?.slice(0,60),
      desc: a.description?.slice(0,300),
      date: a.createdon?.slice(0,10),
      owner: a['_ownerid_value@OData.Community.Display.V1.FormattedValue']
    })) || []);
  } catch(e) { window.__acts = 'error: '+e.message; }
})();
'acts query kicked'
```

### Passo 3 — Scoring de hot signals

Aplicar catálogo de `references/hot-signals.md`. Para deals SBA/GTS, adicionar
automaticamente **+3 bônus** pelo fato de APW agora fechar (motivo do travamento
original foi removido).

| Score (+ bônus SBA) | Label | Ação |
|---|---|---|
| 7–10 | 🔥 Quente frio | Nova proposta imediata |
| 4–6 | 🌡️ Morno | Pesquisar antes de reabordar |
| 1–3 | ❄️ Frio | Baixa prioridade |
| ≤ 0 | 💀 Sem viabilidade | Surrender definitivo |

### Passo 4 — Output do Modo 1

```
POOLS FRIAS — [N] deals · parados 2+ anos

🔥 SBA/GTS REVIVAL ([N]) — PRIORIDADE MÁXIMA
  APW agora fecha com SBA → esses deals travaram por motivo que não existe mais

  L12345 · [nome] · [cidade] · Pool: Purged · modificado [data]
  Torreira: GTS → SBA · Aluguel: R$ 5.800 · Score: 9/10 (base 6 + bônus SBA +3)
  Sinal: "aguardando resposta da GTS" (atividade jun/2022)
  → Próximo passo: apw-email-sba-murilo

🔥 HIGHLINE/PHOENIX/PTI ([N]) — alta prioridade
  ...

🌡️ IHS/ATC ([N]) — média prioridade
  ...

❄️ DESCONHECIDA ([N]) — sem torreira identificada
  [só count — pedir ao Lucas se quer aprofundar]

TOTAIS POR POOL:
  Purged: [N] · Surrender: [N] · Sites at Risk: [N]
  Carrier Owned: [N] · Tower Owned: [N]
```

---

## MODO 2 — Prospecção Anatel (Condomínios)

Este modo **delega diretamente** à skill `apw-erb-towerco-triage`. Não
reimplemente a lógica aqui — carregue a skill e siga seu pipeline.

O que este modo acrescenta: orientar o Lucas a **filtrar por `ClassInfraFis =
Rooftop`** na lista Anatel antes de rodar a triage. Rooftop = prédio comercial
ou residencial = condomínio = **Trilha A (Cessão de Direitos Creditórios)** =
candidato a campanha de cartas.

### Checklist antes de rodar apw-erb-towerco-triage

1. ✅ Baixou a lista Anatel da região/estado desejado em CSV?
2. ✅ Sabe qual bairro/cidade quer focar?
3. ✅ Quer cruzar com leads do CRM já existentes, ou só ver os ERBs crus?
4. ✅ O resultado vai para campanha de cartas (só Rooftop) ou prospecção ampla?

Se tudo sim → acione `apw-erb-towerco-triage` passando o CSV.
Quando o HTML de saída sair, filtrar para manter só `ROOFTOP / TRILHA A`.

> **Dica:** se o volume for grande, dividir por MUN (município) e priorizar os
> com tenancy ≥ 2 operadoras — sinal de site core com aluguel sólido.

---

## MODO 3 — Stage 5 Antigos (2+ anos sem movimento)

### Por que Stage 5 merece análise diferenciada

Stage 5 = proposta feita, estava em negociação/pricing. Se travou por 2+ anos
é porque: (a) negociação com torreira empacou, (b) LL sumiu, (c) dono do deal
saiu. Diferente dos outros modos, aqui queremos saber **quanto trabalho já foi
feito** — número de pricing options criadas é o indicador.

Mais pricing options = mais rodadas de negociação = LL engajado = vale retomar.

### Query Stage 5 antigos

```js
// MODO 3 — Stage 5 antigos com 2+ anos parados
window.__stage5 = 'pending';
(async () => {
  try {
    const DATA_2A = '2024-07-15T00:00:00Z'; // ajustar data
    const BRASIL  = 'FEA663A6-5B28-E211-BCD6-00155D00D805';

    const filter = [
      `apwip_opportunitystage eq 100000004`, // Stage 5 — confirmar com sonda
      `apwip_countryfilter eq ${BRASIL}`,
      `statecode eq 0`,
      `modifiedon le ${DATA_2A}`
    ].join(' and ');

    const url = `${window.location.origin}/api/data/v9.2/opportunities` +
      `?$filter=${encodeURIComponent(filter)}` +
      `&$select=opportunityid,name,modifiedon,createdon,_ownerid_value,new_rvpcommentsnew` +
      `&$expand=apwip_leadopportunityid($select=apwip_carrier,apwip_towercompany,address1_city,apwip_monthlyrent)` +
      `&$orderby=modifiedon asc` +
      `&$top=100`;

    const r = await fetch(url, {
      headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.include-annotations=*'}
    });
    const d = await r.json();
    window.__stage5 = JSON.stringify({
      total: d.value?.length || 0,
      nextLink: d['@odata.nextLink'] ? 'sim' : 'não',
      sample: d.value?.slice(0,10).map(v => ({
        id: v.opportunityid,
        name: v.name?.slice(0,50),
        modified: v.modifiedon?.slice(0,10),
        pool: v['_ownerid_value@OData.Community.Display.V1.FormattedValue'],
        city: v.apwip_leadopportunityid?.address1_city,
        rent: v.apwip_leadopportunityid?.apwip_monthlyrent,
        carrier: v.apwip_leadopportunityid?.apwip_carrier
      })) || []
    });
    window.__stage5All = d.value || [];
  } catch(e) { window.__stage5 = 'error: '+e.message; }
})();
'stage5 query kicked'
```

### Contagem de pricing options por opp

```js
// Contar pricing options de uma opp
window.__pricingCount = 'pending';
(async () => {
  const OPP_GUID = 'SUBSTITUIR';
  try {
    const r = await fetch(
      `${window.location.origin}/api/data/v9.2/apwip_pricingoptions` +
      `?$filter=_apwip_opportunityid_value eq ${OPP_GUID}` +
      `&$select=apwip_pricingoptionid,createdon,apwip_name` +
      `&$orderby=createdon desc&$top=20`,
      { headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}}
    );
    const d = await r.json();
    window.__pricingCount = JSON.stringify({
      count: d.value?.length || 0,
      dates: d.value?.map(p=>p.createdon?.slice(0,10)) || []
    });
  } catch(e) {
    // Se entidade não existir, descobrir nome via schema probe
    window.__pricingCount = 'error: '+e.message+' — rodar schema probe';
  }
})();
'pricing count kicked'
```

> **Se o endpoint de pricing options falhar:** rodar schema probe para descobrir
> o nome correto da entidade:
> `GET /api/data/v9.2/EntityDefinitions?$select=LogicalName,DisplayName`
> filtrar por "pricing" no nome.

### Scoring Stage 5 (adicionar ao hot signals padrão)

| Indicador Stage 5 | Pontos |
|---|---|
| ≥ 3 pricing options criadas | +3 (muitas rodadas = LL engajado) |
| 2 pricing options | +2 |
| 1 pricing option | +1 |
| Torreira SBA/GTS identificada | +3 (APW agora fecha) |
| Aluguel R$4k–R$8k | +2 (faixa viável SBA) |

### Output do Modo 3

```
STAGE 5 ANTIGOS — [N] deals · parados 2+ anos

[L-number] · [nome] · [cidade] · Aluguel R$X · Torreira: [nome atual]
Pricing options: [N] · Modificado: [data] · Pool atual: [pool]
Score: [N]/10 · [🔥/🌡️/❄️]
Próximo passo: [reativar direto / dossiê / email SBA]
```

---

## MODO 4 — SBA/GTS Revival (lente sobre Modos 1 e 3)

Este modo não é uma varredura separada — é uma **lente de priorização** que
se aplica sobre os resultados dos Modos 1 e 3.

### Lógica

1. Pegar todos os resultados do Modo 1 e/ou Modo 3
2. Aplicar regex: `/\b(sba|gts|acf)\b/i` em name, rvpcomments, carrier, towercompany
3. Para cada match: verificar nas atividades se o motivo de travamento foi
   "SBA não aprovava", "GTS não fechava", "torreira não aceitou" → se sim,
   **prioridade máxima** (motivo histórico foi removido — APW hoje fecha)
4. Para esses deals: acionar `apw-email-sba-murilo` diretamente

### Regex de triagem em memória

```js
// Filtrar SBA/GTS dos resultados já em memória
const sbaPat = /\b(sba|gts|acf)\b/i;
const sbaDeals = (window.__poolsFriasAll || []).filter(v =>
  sbaPat.test([v.name, v.torreira].join(' '))
);
JSON.stringify({count: sbaDeals.length, deals: sbaDeals.slice(0,20)})
```

---

## Regras herdadas (não rediscutir aqui)

- **Dados em memória:** nenhum dump bruto de CRM em arquivo. Só exportar
  lista com L-number, cidade, score/label e aluguel agregado — sem PII de LL,
  sem CPF, sem nome de proprietário.
- **Anti-screenshot:** zero screenshots em domínios `*.dynamics.com`. Usar
  `javascript_tool` → `read_page` → `get_page_text` nessa ordem.
- **Promise pattern:** `window.__var = 'pending'; (async()=>{...window.__var=JSON.stringify(r)})(); 'kicked'`
  → ler com chamada seguinte.
- **Truncamento:** saída do `javascript_tool` trunca em ~1.500 chars. Devolver
  slices ou agregados, nunca o array inteiro.
- **Filtro por diretor:** se o Lucas pedir "para [nome do diretor]", adicionar
  filtro `_ownerid_value eq [GUID do diretor]` OU buscar deals onde o diretor
  foi owner antes de mover para a pool via histórico de atividades.

---

## Encadeamento com outras skills

| Quando... | Use |
|---|---|
| Quer aprofundar um deal frio específico | `apw-deal-dossier` (código L) |
| Quer ler atividades coladas de um deal | `apw-opp-activity-forensics` |
| Quer reabrir com Murilo/SBA | `apw-email-sba-murilo` |
| Quer criar novo lead de site Anatel sem CRM | `apw-pin-creator` |
| Quer fazer proposta para deal quente frio | `apw-proposta-comercial` |
| Quer submeter deal reativado ao IC | `apw-submission-writer` |
| Quer vasculhar deals ON HOLD | `apw-onhold-reassessment` |
| Qualquer outra demanda APW não mapeada | `apw-router` |

---

## Referências desta skill

- `references/hot-signals.md` — catálogo completo de sinais de calor +
  pontuação por sinal (inclui sinais específicos para contexto SBA)
- `references/fetchxml-queries.md` — templates FetchXML prontos para os modos
  principais (copiar e ajustar GUIDs/datas no `javascript_tool`)
