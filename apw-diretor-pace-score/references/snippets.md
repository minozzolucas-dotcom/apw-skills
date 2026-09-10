# Snippets — APW Diretor Pace Score

Todos os snippets rodam no **console F12** de uma aba autenticada do Dynamics 365 CRM
(`apwireless.crm.dynamics.com`). Nenhum precisa de agente de navegador.

---

## 1. HARVEST — puxa contagens agregadas de todos os stages

Cola no console. Ao final ele oferece um botão de download automático do JSON
(muito mais confiável que `copy()` para volumes grandes).

```javascript
(async function apwPaceHarvest(){
  const base = Xrm.Utility.getGlobalContext().getClientUrl();
  const H = { 'Accept':'application/json', 'OData-MaxVersion':'4.0', 'OData-Version':'4.0',
              'Prefer':'odata.include-annotations="*"' };
  const BR = 'FEA663A6-5B28-E211-BCD6-00155D00D805'; // GUID Brazil no lookup apwip_countryfilter

  const STAGES = [
    { n:1,  date:'apwip_stage1_obtainedleaseeconomics', owner:'apwip_stage1owner' },
    { n:3,  date:'apwip_stage3date',                    owner:'apwip_stage3owner' },
    { n:5,  date:'apwip_stage5date',                    owner:'apwip_stage5owner' },
    { n:8,  date:'apwip_stage8date',                    owner:'apwip_stage8owner' },
    { n:99, date:'apwip_stage99closedandfundeddeal',    owner:'apwip_stage99owner' },
  ];

  const out = { generatedAt: new Date().toISOString(), country: 'Brazil', stages: {} };

  for (const s of STAGES) {
    const fx = `<fetch aggregate="true"><entity name="opportunity">
      <attribute name="${s.owner}" alias="ownerId" groupby="true"/>
      <attribute name="opportunityid" alias="cnt" aggregate="count"/>
      <attribute name="${s.date}" alias="yr" groupby="true" dategrouping="year"/>
      <attribute name="${s.date}" alias="mo" groupby="true" dategrouping="month"/>
      <filter type="and">
        <condition attribute="apwip_countryfilter" operator="eq" uiname="Brazil" uitype="apwip_country" value="{${BR}}"/>
        <condition attribute="${s.date}" operator="not-null"/>
        <condition attribute="${s.owner}" operator="not-null"/>
      </filter>
    </entity></fetch>`;

    try {
      const url = `${base}/api/data/v9.2/opportunities?fetchXml=${encodeURIComponent(fx)}`;
      const r = await fetch(url, {headers:H, credentials:'include'});
      if (!r.ok) throw new Error(`HTTP ${r.status}: ${(await r.text()).slice(0,300)}`);
      const j = await r.json();
      const rows = (j.value || []).map(row => ({
        ownerId: row['_ownerId_value'] || row.ownerId || null,
        ownerName: row['_ownerId_value@OData.Community.Display.V1.FormattedValue']
                || row['ownerId@OData.Community.Display.V1.FormattedValue'] || null,
        year: row.yr, month: row.mo, count: row.cnt
      })).filter(r => r.ownerId);
      out.stages[`s${s.n}`] = rows;
      console.log(`✅ Stage ${s.n}: ${rows.length} linhas (owner×mês)`);
    } catch(e) {
      out.stages[`s${s.n}_error`] = String(e);
      console.warn(`❌ Stage ${s.n}:`, e);
    }
  }

  // Owners únicos + metadata
  const uniqueOwners = new Set();
  Object.values(out.stages).forEach(rows => Array.isArray(rows) && rows.forEach(r => r.ownerId && uniqueOwners.add(r.ownerId)));
  const ownerIds = [...uniqueOwners];
  console.log(`📇 Owners únicos: ${ownerIds.length}`);

  out.owners = {};
  for (let i=0; i<ownerIds.length; i+=15) {
    const chunk = ownerIds.slice(i, i+15);
    const filter = chunk.map(id => `systemuserid eq ${id}`).join(' or ');
    try {
      const url = `${base}/api/data/v9.2/systemusers?$select=systemuserid,fullname,domainname,createdon,isdisabled,title,jobtitle,new_adphiredate&$filter=${encodeURIComponent(filter)}`;
      const r = await fetch(url, {headers:H, credentials:'include'});
      const j = await r.json();
      (j.value || []).forEach(u => { out.owners[u.systemuserid] = u; });
    } catch(e) { console.warn('owner chunk fail', e); }
  }

  window.__APW_PACE = out;

  // Download automático — muito mais confiável que copy() pra volumes grandes
  const blob = new Blob([JSON.stringify(out, null, 2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `apw_pace_harvest_${new Date().toISOString().slice(0,10)}.json`;
  document.body.appendChild(a); a.click(); a.remove();

  console.log('%c✅ Harvest concluído — download disparado. Rode build_pace.py com o JSON.',
    'color:#fff;background:#1C75BB;padding:6px 10px;font-weight:bold;font-size:13px');
  return out;
})();
```

**Saída**: `apw_pace_harvest_YYYY-MM-DD.json` baixado automaticamente. Estrutura:

```json
{
  "generatedAt": "2026-09-09T18:14:02.046Z",
  "country": "Brazil",
  "stages": {
    "s1":  [{ ownerId, ownerName, year, month, count }, ...],
    "s3":  [...],
    "s5":  [...],
    "s8":  [...],
    "s99": [...]
  },
  "owners": {
    "<systemuserid>": { fullname, title, domainname, createdon, isdisabled, new_adphiredate }
  }
}
```

---

## 2. SCOUT (só na primeira vez, se schema mudar)

Descoberta de schema. Rodar UMA vez para validar que os campos `apwip_stageXdate` /
`apwip_stageXowner` continuam existindo no tenant. Se algo mudou, o harvest quebra
e a mensagem de erro no console mostra qual campo sumiu.

```javascript
(async function apwCRMScout(){
  const VIEWID = 'bfe460c6-ae83-e811-8140-e0071b6a12f1'; // "Análise de Fechamentos"
  const base = Xrm.Utility.getGlobalContext().getClientUrl();
  const H = { 'Accept':'application/json', 'OData-MaxVersion':'4.0', 'OData-Version':'4.0',
              'Prefer':'odata.include-annotations="*"' };
  const out = {};

  // View — pode ser savedqueries ou userqueries
  for (const entity of ['savedqueries','userqueries']) {
    try {
      const r = await fetch(`${base}/api/data/v9.2/${entity}(${VIEWID})?$select=name,fetchxml,layoutxml`,
        {headers:H, credentials:'include'});
      if (r.ok) { out.view = await r.json(); out.view_kind = entity; break; }
    } catch(e){}
  }

  // Metadata dos campos stage
  const r = await fetch(`${base}/api/data/v9.2/EntityDefinitions(LogicalName='opportunity')/Attributes?$select=LogicalName,AttributeType`,
    {headers:H, credentials:'include'});
  const meta = await r.json();
  out.stageFields = (meta.value||[])
    .filter(f => /stage|purge|surrender|hold/i.test(f.LogicalName))
    .filter(f => !/reason|comment|note|description/i.test(f.LogicalName))
    .map(f => ({logical:f.LogicalName, type:f.AttributeType}))
    .sort((a,b)=>a.logical.localeCompare(b.logical));

  window.__APW_CRM_SCOUT = out;
  console.log('Scout salvo em __APW_CRM_SCOUT — rode copy(__APW_CRM_SCOUT)');
  return out;
})();
```

**Saída esperada** (validação): os campos abaixo devem existir. Se algum sumir, o
harvest precisa ser ajustado.

| Stage | Campo timestamp | Campo owner (Lookup) |
|---|---|---|
| 1 | `apwip_stage1_obtainedleaseeconomics` | `apwip_stage1owner` |
| 3 | `apwip_stage3date` | `apwip_stage3owner` |
| 5 | `apwip_stage5date` | `apwip_stage5owner` |
| 8 | `apwip_stage8date` | `apwip_stage8owner` |
| 99 | `apwip_stage99closedandfundeddeal` | `apwip_stage99owner` |

---

## 3. HIRE DATES (opcional — só se `createdon` não bater com o real)

O harvest v2 já traz `new_adphiredate` embutido (o campo custom vindo do ADP). Se
por algum motivo estiver vazio no seu tenant, este snippet standalone confere:

```javascript
(async function apwHireDates(){
  const base = Xrm.Utility.getGlobalContext().getClientUrl();
  const H = { 'Accept':'application/json', 'OData-MaxVersion':'4.0', 'OData-Version':'4.0',
              'Prefer':'odata.include-annotations="*"' };
  // Filtro por título — pega TODOS os diretores ativos automaticamente
  const filter = `(title eq 'Acquisition Director' or title eq 'Sr Acquisition Director' or title eq 'Director, Commercial Sale' or title eq 'Director, Sales') and isdisabled eq false`;
  const url = `${base}/api/data/v9.2/systemusers?$select=systemuserid,fullname,title,createdon,new_adphiredate,apwip_annualpurchasetarget&$filter=${encodeURIComponent(filter)}`;
  const j = await (await fetch(url, {headers:H, credentials:'include'})).json();
  const data = j.value.map(u => ({
    name: u.fullname,
    title: u.title,
    adp_hire: (u.new_adphiredate || '').slice(0,10) || '(vazio)',
    createdon_proxy: u.createdon.slice(0,10),
    target_usd: u.apwip_annualpurchasetarget
  }));
  console.table(data);
  window.__APW_HIRES = data;
  console.log('Rode copy(__APW_HIRES) pra colar.');
})();
```

**Bônus**: `apwip_annualpurchasetarget` é a **meta anual em USD** de cada diretor. Se
existir, dá pra montar métrica de "Achievement %" complementar ao pace (comparar o
score projetado do ano vs. target). Ainda não incorporado na v2 do dashboard — feature
futura.

---

## Troubleshooting

- **`Xrm is not defined`** — não está numa aba do Dynamics. Abre `apwireless.crm.dynamics.com` primeiro.
- **`403 Forbidden`** — sessão expirou. F5 na aba e tenta de novo.
- **Harvest retorna `[]` em alguma stage** — abre o console e olha se veio erro; provavelmente permissão de leitura em `opportunity` foi revogada pro seu user (pedir pra IT).
- **`copy(__APW_PACE)` retorna undefined mas nada foi pro clipboard** — normal. Use o helper de download embutido no snippet (já está integrado).
- **Dashboard mostra PI muito alto (>3) pra alguém novo** — baseline curta demais distorce. Marcar mentalmente. A regra dos 90 dias evita o pior caso mas rampas 3-9 meses ainda podem inflar.
