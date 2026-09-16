# Views salvas e FetchXML

Quando o Lucas pede "puxa a view X" ou "as 21 hot deals" — ele está se referindo a uma view salva no Dynamics.

## Tipos de view

- **savedquery** — views do sistema, visíveis a todos
- **userquery** — views pessoais, salvas pelo próprio Lucas

Quando não souber qual, tenta `userquery` primeiro (mais provável que seja dele); se 404, cai pra `savedquery`.

## Pegar o fetchxml de uma view

A `viewid` aparece na URL quando ele abre a view no navegador (parâmetro `viewid=` ou `?viewType=...&viewid=...`).

```js
(async () => {
  const viewId = 'COLE_AQUI'; // sem chaves, só o GUID
  // tenta userquery primeiro
  let r = await fetch(`${window.location.origin}/api/data/v9.2/userqueries(${viewId})?$select=name,fetchxml`, {
    headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}
  });
  if (!r.ok) {
    r = await fetch(`${window.location.origin}/api/data/v9.2/savedqueries(${viewId})?$select=name,fetchxml`, {
      headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}
    });
  }
  const d = await r.json();
  return {name: d.name, fetchxml: d.fetchxml};
})();
```

Inspeciona o `fetchxml` retornado pra entender quais campos e filtros a view usa. **Importante**: usa o nome exato dos campos lógicos no XML — copia eles pro teu `$select` ou pra construir queries OData equivalentes.

## Executar uma view via savedQuery (rota direta)

Quando o objetivo é só rodar a view sem mexer no fetchxml:

```js
(async () => {
  const viewId = 'COLE_AQUI';
  const url = `${window.location.origin}/api/data/v9.2/opportunities`
    + `?savedQuery=${viewId}`
    + `&$select=opportunityid,apwip_autonumberid,name,estimatedclosedate,closeprobability`;
  const r = await fetch(url, {
    headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.include-annotations=*'}
  });
  const d = await r.json();
  return {count: d.value.length, sample: d.value.slice(0,3), nextLink: d['@odata.nextLink']};
})();
```

Equivalente pra userquery: `?userQuery=${viewId}`.

## Executar FetchXML customizado

Quando precisar de filtros que a view não tem, monta o fetchxml e executa:

```js
(async () => {
  const fetchXml = `<fetch version='1.0' mapping='logical' distinct='false'>
    <entity name='opportunity'>
      <attribute name='opportunityid'/>
      <attribute name='apwip_autonumberid'/>
      <attribute name='name'/>
      <attribute name='estimatedclosedate'/>
      <filter type='and'>
        <condition attribute='statecode' operator='eq' value='0'/>
        <condition attribute='estimatedclosedate' operator='this-fiscal-year'/>
      </filter>
      <order attribute='apwip_autonumberid' descending='false'/>
    </entity>
  </fetch>`;
  const url = `${window.location.origin}/api/data/v9.2/opportunities?fetchXml=${encodeURIComponent(fetchXml)}`;
  const r = await fetch(url, {
    headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.include-annotations=*'}
  });
  const d = await r.json();
  return {count: d.value.length, data: d.value};
})();
```

## Paginação

Se o resultado tiver `@odata.nextLink`, faz fetch nele com os mesmos headers. Repete até `nextLink` sumir. Mostra pro Lucas o count parcial enquanto pagina (não some por 30 segundos sem dar sinal de vida).

## Fallback: extração via ag-grid (quando Web API falha)

Em raros casos a view tem dados calculados em JS que não estão expostos como campos OData. Aí extrai do próprio grid:

```js
(() => {
  const grid = document.querySelector('[role="grid"]');
  const api = grid?.__agComponent?.gridOptions?.api
           || grid?.gridOptions?.api
           || window.agGridApi;
  const rows = [];
  if (api && api.forEachNode) {
    api.forEachNode(node => rows.push(node.data));
  }
  return {count: rows.length, rows: rows.slice(0, 5), allRows: rows};
})();
```

O ag-grid mantém todas as linhas em memória mesmo virtualizadas. Não tenta scrollar.

## Erros comuns

- **Array vazio com FetchXML mas a view mostra resultados** — provável incompatibilidade de tipo de campo (option set vs string) ou prefixo de publisher errado. Ver `troubleshooting.md`.
- **400 Bad Request com `apwip_X`** — campo não existe nessa entidade, ou o nome lógico real é diferente. Tira o filtro, faz `$select` só dos campos padrão pra confirmar que a entidade está certa, depois adiciona campos custom um a um.
- **403** — você está numa aba que não tem permissão pra esse recurso. Confirma com o Lucas que ele consegue ver no navegador normalmente.
