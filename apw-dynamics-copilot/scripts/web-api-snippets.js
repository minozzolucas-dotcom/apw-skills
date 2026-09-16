/* ============================================================
   APW Dynamics Copilot — JS snippets reutilizáveis
   ============================================================

   Cada bloco abaixo é um IIFE async pronto pra colar no
   `Claude in Chrome:javascript_tool` da aba do Dynamics.

   Convenções:
   - Todos retornam objeto JSON (não chama JSON.stringify).
   - Headers padrão sempre incluídos.
   - Tratamento de erro com try/catch.
   - Parâmetros marcados com `// SET:` precisam ser preenchidos antes de colar.

   ============================================================ */


/* ------------------------------------------------------------
   [1] LOOKUP — buscar deal(s) por código L
   ------------------------------------------------------------ */
(async () => {
  const lnumbers = ['12345', '789']; // SET: lista de números sem prefixo L
  try {
    const filter = lnumbers.map(n => `apwip_autonumberid eq '${n}'`).join(' or ');
    const url = `${window.location.origin}/api/data/v9.2/opportunities`
      + `?$filter=(${filter}) and statecode eq 0`
      + `&$select=opportunityid,apwip_autonumberid,name,estimatedclosedate,closeprobability,stepname,apwip_rfexpertnotes`
      + `&$expand=ownerid($select=fullname)`;
    const r = await fetch(url, {
      headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.include-annotations=*'}
    });
    if (!r.ok) return {error: r.status, text: await r.text()};
    const d = await r.json();
    return {count: d.value.length, deals: d.value};
  } catch (e) { return {exception: e.message}; }
})();


/* ------------------------------------------------------------
   [2] VIEW — pegar fetchxml de uma view salva
   ------------------------------------------------------------ */
(async () => {
  const viewId = ''; // SET: GUID da view (sem chaves)
  const headers = {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'};
  try {
    let r = await fetch(`${window.location.origin}/api/data/v9.2/userqueries(${viewId})?$select=name,fetchxml`, {headers});
    if (!r.ok) {
      r = await fetch(`${window.location.origin}/api/data/v9.2/savedqueries(${viewId})?$select=name,fetchxml`, {headers});
    }
    if (!r.ok) return {error: r.status, text: await r.text()};
    const d = await r.json();
    return {name: d.name, fetchxml: d.fetchxml};
  } catch (e) { return {exception: e.message}; }
})();


/* ------------------------------------------------------------
   [3] VIEW — executar view via savedQuery
   ------------------------------------------------------------ */
(async () => {
  const viewId = '';   // SET: GUID
  const entity = 'opportunities'; // SET: collection name
  const select = 'opportunityid,apwip_autonumberid,name'; // SET
  try {
    const url = `${window.location.origin}/api/data/v9.2/${entity}?savedQuery=${viewId}&$select=${select}`;
    const r = await fetch(url, {
      headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.include-annotations=*,odata.maxpagesize=5000'}
    });
    if (!r.ok) return {error: r.status, text: await r.text()};
    const d = await r.json();
    return {count: d.value.length, hasMore: !!d['@odata.nextLink'], sample: d.value.slice(0,3), all: d.value};
  } catch (e) { return {exception: e.message}; }
})();


/* ------------------------------------------------------------
   [4] FETCHXML — executar XML customizado com paginação
   ------------------------------------------------------------ */
(async () => {
  const fetchXml = `<fetch version='1.0' mapping='logical'>
    <entity name='opportunity'>
      <attribute name='opportunityid'/>
      <attribute name='apwip_autonumberid'/>
      <attribute name='name'/>
      <filter type='and'>
        <condition attribute='statecode' operator='eq' value='0'/>
      </filter>
    </entity>
  </fetch>`; // SET: seu fetchxml
  const entity = 'opportunities'; // SET: collection name
  try {
    const headers = {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.include-annotations=*,odata.maxpagesize=5000'};
    const url = `${window.location.origin}/api/data/v9.2/${entity}?fetchXml=${encodeURIComponent(fetchXml)}`;
    const r = await fetch(url, {headers});
    if (!r.ok) return {error: r.status, text: await r.text()};
    const d = await r.json();
    return {count: d.value.length, hasMore: !!d['@odata.nextLink'], data: d.value};
  } catch (e) { return {exception: e.message}; }
})();


/* ------------------------------------------------------------
   [5] PAGINAÇÃO — coletar todos os records de um endpoint
   ------------------------------------------------------------ */
(async () => {
  let url = ''; // SET: URL inicial completa
  const headers = {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.include-annotations=*,odata.maxpagesize=5000'};
  const all = [];
  try {
    while (url) {
      const r = await fetch(url, {headers});
      if (!r.ok) return {error: r.status, text: await r.text(), partial: all.length};
      const d = await r.json();
      all.push(...d.value);
      url = d['@odata.nextLink'];
    }
    return {total: all.length, sample: all.slice(0,3), all};
  } catch (e) { return {exception: e.message, partial: all.length}; }
})();


/* ------------------------------------------------------------
   [6] PATCH — update single record (após confirmação do Lucas)
   ------------------------------------------------------------ */
(async () => {
  const entity = 'opportunities'; // SET: collection
  const id = '';                   // SET: GUID
  const updates = {                // SET: campos
    // apwip_rfexpertnotes: 'novo texto',
    // apwip_auditcheckbox: true
  };
  try {
    const r = await fetch(`${window.location.origin}/api/data/v9.2/${entity}(${id})`, {
      method: 'PATCH',
      headers: {
        'Accept':'application/json','Content-Type':'application/json',
        'OData-MaxVersion':'4.0','OData-Version':'4.0','If-Match':'*'
      },
      body: JSON.stringify(updates)
    });
    return {status: r.status, ok: r.ok, body: r.ok ? null : await r.text()};
  } catch (e) { return {exception: e.message}; }
})();


/* ------------------------------------------------------------
   [7] BATCH PATCH paralelo (pequeno volume, até ~10)
   ------------------------------------------------------------ */
(async () => {
  const entity = 'opportunities'; // SET
  const updates = [               // SET: array de {id, body}
    // {id: 'GUID_1', body: {apwip_auditcheckbox: true}},
  ];
  const headers = {
    'Accept':'application/json','Content-Type':'application/json',
    'OData-MaxVersion':'4.0','OData-Version':'4.0','If-Match':'*'
  };
  try {
    const results = await Promise.all(updates.map(async u => {
      const r = await fetch(`${window.location.origin}/api/data/v9.2/${entity}(${u.id})`, {
        method:'PATCH', headers, body: JSON.stringify(u.body)
      });
      return {id: u.id, status: r.status, ok: r.ok};
    }));
    const failures = results.filter(r => !r.ok);
    return {total: results.length, succeeded: results.length - failures.length, failures};
  } catch (e) { return {exception: e.message}; }
})();


/* ------------------------------------------------------------
   [8] DESCOBERTA — listar campos de uma entidade
   ------------------------------------------------------------ */
(async () => {
  const entityName = 'opportunity'; // SET: nome lógico (singular)
  const prefix = 'apwip_';          // SET: filtro de prefixo, ou '' pra todos
  try {
    const filter = prefix ? `&$filter=startswith(LogicalName,'${prefix}')` : '';
    const r = await fetch(
      `${window.location.origin}/api/data/v9.2/EntityDefinitions(LogicalName='${entityName}')/Attributes`
      + `?$select=LogicalName,DisplayName,AttributeType${filter}`,
      {headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}}
    );
    if (!r.ok) return {error: r.status, text: await r.text()};
    const d = await r.json();
    return d.value.map(a => ({
      logical: a.LogicalName,
      display: a.DisplayName?.UserLocalizedLabel?.Label || null,
      type: a.AttributeType
    })).sort((a,b) => a.logical.localeCompare(b.logical));
  } catch (e) { return {exception: e.message}; }
})();


/* ------------------------------------------------------------
   [9] DESCOBERTA — listar entidades custom da APW
   ------------------------------------------------------------ */
(async () => {
  try {
    const r = await fetch(
      `${window.location.origin}/api/data/v9.2/EntityDefinitions`
      + `?$select=LogicalName,LogicalCollectionName,DisplayName`
      + `&$filter=startswith(LogicalName,'apwip_')`,
      {headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}}
    );
    if (!r.ok) return {error: r.status, text: await r.text()};
    const d = await r.json();
    return d.value.map(e => ({
      singular: e.LogicalName,
      collection: e.LogicalCollectionName,
      display: e.DisplayName?.UserLocalizedLabel?.Label || null
    })).sort((a,b) => a.singular.localeCompare(b.singular));
  } catch (e) { return {exception: e.message}; }
})();


/* ------------------------------------------------------------
  [10] PICKLIST — descobrir labels e valores de um option set
  ------------------------------------------------------------ */
(async () => {
  const entityName = 'opportunity'; // SET
  const attrName = 'apwip_rating';  // SET
  try {
    const r = await fetch(
      `${window.location.origin}/api/data/v9.2/EntityDefinitions(LogicalName='${entityName}')`
      + `/Attributes(LogicalName='${attrName}')/Microsoft.Dynamics.CRM.PicklistAttributeMetadata`
      + `?$expand=OptionSet`,
      {headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}}
    );
    if (!r.ok) return {error: r.status, text: await r.text()};
    const d = await r.json();
    return d.OptionSet.Options.map(o => ({
      value: o.Value,
      label: o.Label?.UserLocalizedLabel?.Label
    }));
  } catch (e) { return {exception: e.message}; }
})();


/* ------------------------------------------------------------
  [11] AG-GRID FALLBACK — extrair linhas da view renderizada
  ------------------------------------------------------------ */
(() => {
  try {
    const grid = document.querySelector('[role="grid"]');
    const api = grid?.__agComponent?.gridOptions?.api
             || grid?.gridOptions?.api
             || window.agGridApi;
    const rows = [];
    if (api && api.forEachNode) {
      api.forEachNode(node => rows.push(node.data));
    }
    return {count: rows.length, sample: rows.slice(0, 3), all: rows};
  } catch (e) { return {exception: e.message}; }
})();


/* ------------------------------------------------------------
  [12] HEALTH CHECK — confirmar que a sessão está OK
  ------------------------------------------------------------ */
(async () => {
  try {
    const r = await fetch(`${window.location.origin}/api/data/v9.2/WhoAmI`, {
      headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}
    });
    if (!r.ok) return {error: r.status, text: await r.text()};
    const d = await r.json();
    return {
      origin: window.location.origin,
      userId: d.UserId,
      businessUnitId: d.BusinessUnitId,
      organizationId: d.OrganizationId
    };
  } catch (e) { return {exception: e.message}; }
})();
