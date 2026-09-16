# CRM Extraction — puxar a opp e suas atividades do Dynamics 365

Leia no Passo 1 do workflow. Todos os snippets rodam via `Claude in Chrome:javascript_tool` dentro da aba autenticada do Dynamics. Não precisa de token — a sessão do navegador já carrega o cookie.

## Antes de começar

Pegue o `origin` da aba ativa do Dynamics — **não hardcode o subdomínio**. O Lucas tem tenants diferentes (`apwbrasil.crm2.dynamics.com`, `apwireless.crm.dynamics.com`, `apw.crm.dynamics.com`). Todos os snippets usam `window.location.origin`, que resolve isso sozinho desde que a aba ativa seja a do Dynamics.

## Estrutura do código L

- Campo lógico: `apwip_autonumberid`.
- Formato exibido: `L` + número (`L1256097`).
- No banco pode ser número puro (`1256097`) ou string com prefixo. Tente sem prefixo primeiro; se vier vazio, tente com `'L1256097'`. Ver seção "Troubleshooting" no fim.

## Snippet 1 — a opp por código L

```js
(async () => {
  const ln = '1256097'; // o número, sem o "L"
  const sel = [
    'opportunityid','apwip_autonumberid','name','stepname',
    'estimatedclosedate','closeprobability','apwip_rfexpertnotes',
    'apwip_dealtypecode','statecode','statuscode','createdon'
  ].join(',');
  // tenta numérico e string; statecode sem filtro pra pegar deal fechado também
  for (const f of [`apwip_autonumberid eq ${ln}`, `apwip_autonumberid eq 'L${ln}'`, `apwip_autonumberid eq '${ln}'`]) {
    const url = `${window.location.origin}/api/data/v9.2/opportunities`
      + `?$filter=${encodeURIComponent(f)}`
      + `&$select=${sel}`
      + `&$expand=ownerid($select=fullname)`;
    const r = await fetch(url, {headers:{'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.include-annotations=*'}});
    const d = await r.json();
    if (d.value && d.value.length) return {filtroUsado:f, opp:d.value[0]};
  }
  return {erro:'nenhum resultado — confira o código L e o tenant'};
})();
```

Guarde o `opportunityid` (GUID) que voltar — os próximos snippets dependem dele.

## Snippet 2 — as atividades da opp

As atividades (tasks, emails logados, follow-ups) são onde mora o histórico operacional. Filtra por `regardingobjectid` = GUID da opp.

```js
(async () => {
  const oppId = 'COLE-O-GUID-AQUI';
  const url = `${window.location.origin}/api/data/v9.2/activitypointers`
    + `?$filter=_regardingobjectid_value eq ${oppId}`
    + `&$select=activityid,subject,description,activitytypecode,scheduledstart,actualend,createdon,statecode`
    + `&$expand=ownerid($select=fullname)`
    + `&$orderby=createdon asc`;
  const r = await fetch(url, {headers:{'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.include-annotations=*'}});
  const d = await r.json();
  return (d.value||[]).map(a => ({
    data: a.createdon, dono: a.ownerid?.fullname, tipo: a.activitytypecode,
    subject: a.subject, description: a.description
  }));
})();
```

`description` é o campo que importa — é a prosa do follow-up. Pode vir longo; processe em memória.

## Snippet 3 — campos de valor (quando precisa do aluguel/preço)

Os campos de valor variam por tenant e por tipo de deal. Os candidatos comuns no publisher `apwip_`:

- Aluguel atual / mensal: campos com `rent`, `monthlyrent`, `currentrent` no nome lógico.
- Valor proposto / preço de aquisição: `estimatedvalue`, ou campos `apwip_` com `purchase`/`offer`/`price`.

Se não souber o nome lógico exato, descubra os campos disponíveis assim:

```js
(async () => {
  const url = `${window.location.origin}/api/data/v9.2/EntityDefinitions(LogicalName='opportunity')/Attributes`
    + `?$select=LogicalName,DisplayName&$filter=startswith(LogicalName,'apwip_')`;
  const r = await fetch(url, {headers:{'Accept':'application/json'}});
  const d = await r.json();
  return d.value
    .map(a => ({campo:a.LogicalName, label:a.DisplayName?.UserLocalizedLabel?.Label}))
    .filter(x => /rent|valor|aluguel|price|preco|offer/i.test((x.campo+x.label)));
})();
```

Depois inclua os campos achados no `$select` do Snippet 1.

## Snippet 4 — abrir o deal no form (se o Lucas quiser ver)

```
https://{origin}/main.aspx?etn=opportunity&pagetype=entityrecord&id={opportunityid-GUID}
```

Use `tabs_create_mcp` + `navigate` para abrir em aba nova. Só faça se o Lucas pedir explicitamente para ver — o dossiê normalmente dispensa.

## Como apresentar o que voltou do CRM

Não despeje JSON no chat. O CRM alimenta as seções 1, 4 e 5 do template do dossiê. Extraia:

- `name` → identificação do site no cabeçalho.
- `stepname` → "Stage CRM".
- `ownerid.fullname` → "Owner".
- `apwip_dealtypecode` → "Tipo" (mapeie o código pro nome: DRS, cessão, asset purchase).
- `apwip_rfexpertnotes` → contexto extra pra seção 1; se longo, resuma.
- atividades → matéria-prima da linha do tempo (seção 5).

## Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| `value: []` no Snippet 1 | formato do `apwip_autonumberid` | o snippet já tenta 3 formatos; se ainda vazio, o L está errado ou é outro tenant |
| HTTP 401 | sessão expirou | peça pro Lucas recarregar a aba do Dynamics e logar |
| HTTP 400 no `$filter` | nome de campo errado | rode o Snippet 3 (metadata) pra achar o nome lógico certo |
| atividades vazias mas a opp existe | follow-ups podem estar como `task`/`email` separados | confirme `_regardingobjectid_value`; alguns deals têm pouca atividade mesmo |

Não persista nenhum desses payloads em arquivo. Processamento em memória, conforme os princípios da skill.
