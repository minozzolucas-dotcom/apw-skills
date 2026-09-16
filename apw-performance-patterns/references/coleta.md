# Plano de coleta — apw-performance-patterns

Tudo via `Claude in Chrome:javascript_tool` numa aba autenticada em
`https://apwireless.crm.dynamics.com`. Web API JSON puro, paginação por
`@odata.nextLink` (guard < 20 páginas por query). Nada em disco.

Janela: `[INICIO, FIM]` em UTC, mas **toda comparação de "mesmo dia" (regra de
reproposta) é em data BR** (America/Sao_Paulo) — converter antes de comparar.

## Q1 — Opps do funil
Uma query por campo de stage (não dá pra OR entre datas com eficiência; 4 queries):

```js
// template — repetir para stage1, stage3, stage8 (campo confirmado), stage99
const base = `${window.location.origin}/api/data/v9.2/opportunities`;
const sel = [
  'opportunityid','apwip_opportunityautonumberid','statecode','statuscode',
  'apwip_stage1_obtainedleaseeconomics','apwip_stage3date',
  /* STAGE5_FIELD, STAGE8_FIELD confirmados */ 'apwip_stage99closedandfundeddeal',
  '_ownerid_value','_apwip_stage1owner_value','_apwip_stage3owner_value'
].join(',');
let url = `${base}?$select=${sel}&$filter=apwip_stage3date ge ${INICIO} and apwip_stage3date le ${FIM}`;
// loop nextLink, acumular em Map por opportunityid (dedup entre as 4 queries)
```

Além das opps com stage NA janela, o cohort precisa do **destino** delas: as datas de
S8/S99 já vêm no `$select`, mesmo que fora da janela. Não precisa de query extra.

Para S8→S99 do cohort do diretor: opps cujo S8 caiu na janela — mesma query trocando o
campo do filtro.

## Q2 — Pricing options (repropostas)
```js
let url = `${window.location.origin}/api/data/v9.2/apwip_pricingoptions?$select=apwip_pricingoptionid,createdon,_ownerid_value,_apwip_opportunityid_value&$filter=createdon ge ${INICIO} and createdon le ${FIM}`;
```
Se `$select` der 400 nessa entidade, cair pro padrão da view do reporte (userQuery
`e85d5310-8c42-f111-88b4-6045bd07461c`) SEM `$select` e ler do payload — mas aí o filtro
de data é client-side.

Classificação de cada pricing (client-side, em memória):
1. Buscar a opp mãe (batch: `$filter=Microsoft.Dynamics.CRM.In(PropertyName='opportunityid',PropertyValues=[...])`
   ou lotes de `or opportunityid eq ...` de 25) para pegar `stage3date`, `stage5date`,
   `stage3owner`.
2. `dataBR(createdon) === dataBR(stage3date)` ou `=== dataBR(stage5date)` → **orgânica**
   (proposta original), descarta.
3. Caso contrário → **reproposta**, creditada ao `_ownerid_value` da pricing.
   Dedup: 1 por (opp, diretor) na janela — manter a mais recente.
4. Flag adicional: `stage3owner === ownerid da pricing`? Se sim, é reproposta do próprio
   deal dele (retrabalho); se não, é reproposta em deal de terceiro. As duas contam como
   reproposta, mas o mix entra na análise de padrões.

## Q3 — Atividades
```js
let url = `${window.location.origin}/api/data/v9.2/activitypointers?$select=activityid,activitytypecode,subject,description,statecode,actualend,_ownerid_value,_regardingobjectid_value&$filter=actualend ge ${INICIO} and actualend le ${FIM} and statecode eq 1`;
```
Filtrar client-side: owner ∈ 14 diretores. Descartar workflow tasks automáticas
(descrição padrão de sistema). Aplicar a regra de substantiva do reporte:
`len(description limpa) ≥ 180` OU (`≥ 140` e ≥2 sinais: número/valor R$, contraparte
[síndico, proprietário, operadora, advogado, zelador...], próximo passo [vou, agendei,
retorno, enviar...], objeção/informação nova).

Volume alto: paginar com `$top=5000` por página se aceito; senão default. Se estourar o
guard de 20 páginas, estreitar a janela e rodar em fatias mensais.

## Q4 — Amostragem qualitativa (fase 4 da skill)
Para os deals selecionados (3–5 convertidos por top, 3–5 mortos por low):
```js
let url = `${window.location.origin}/api/data/v9.2/activitypointers?$select=subject,description,actualend,_ownerid_value&$filter=_regardingobjectid_value eq ${OPP_GUID}&$orderby=actualend asc`;
```
Ler em memória, sintetizar padrões na conversa. Não colar descrições inteiras no chat —
parafrasear o comportamento, citar no máximo trechos curtos e sem PII desnecessária.

## Armadilhas conhecidas
- `$select` + `userQuery` juntos → 400. Um ou outro.
- Datas do Dynamics vêm em UTC; o corte de "dia" das regras do Lucas é BR.
- Owner pool/system em S1/S3 → usar `_apwip_stage1owner_value`/`_apwip_stage3owner_value`.
- Auth 401/403 → pedir pro Lucas reabrir/atualizar a aba, 1 retry, senão parar e avisar.
- Cohort verde (entrada recente < lead time mediano) → separar de cohort maduro, nunca
  somar no número oficial.
