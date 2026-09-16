# Lookup patterns — consulta rápida de deals

Quando o Lucas pede "me mostra o L12345" ou "o que está rolando no L789 e L456".

## Estrutura do código L

- Campo lógico: `apwip_autonumberid`
- Formato exibido: `L` + número (ex.: `L12345`)
- O valor no banco é o número puro como string ou int — quando filtrar, use só o número.

## Snippet base — lookup por código L

```js
(async () => {
  const lnumbers = ['12345', '789', '456']; // strip the "L" prefix
  const filter = lnumbers.map(n => `apwip_autonumberid eq '${n}'`).join(' or ');
  const url = `${window.location.origin}/api/data/v9.2/opportunities`
    + `?$filter=(${filter}) and statecode eq 0`
    + `&$select=opportunityid,apwip_autonumberid,name,estimatedclosedate,closeprobability,apwip_rfexpertnotes`
    + `&$expand=ownerid($select=fullname)`;
  const r = await fetch(url, {
    headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.include-annotations=*'}
  });
  const d = await r.json();
  return d.value;
})();
```

**Nota sobre o tipo do campo**: em algumas instalações `apwip_autonumberid` é numérico (use `eq 12345` sem aspas), em outras é string com prefixo (use `eq 'L12345'`). Se a primeira tentativa retornar array vazio, troque o formato e tente de novo. Ver `troubleshooting.md`.

## Snippet — abrir um deal direto no form

Se o Lucas quiser **ver** o deal (não só dados), construa a URL e abra em aba nova:

```
https://{tenant}/main.aspx?etn=opportunity&pagetype=entityrecord&id={opportunityid-GUID}
```

Para Brasil: `apwbrasil.crm2.dynamics.com`
Para US: `apw.crm.dynamics.com`

Use `tabs_create_mcp` ou `navigate` na própria aba ativa, dependendo do que ele pediu.

## Campos mais pedidos em lookup

Inclua sempre que ele pedir "me mostra o deal":

- `apwip_autonumberid` — o L
- `name` — descrição do deal (geralmente endereço/identificador da torre)
- `estimatedclosedate` — close esperado
- `closeprobability` — probabilidade %
- `apwip_rfexpertnotes` — notas de RF (Filipe escreve aqui)
- `stepname` — stage atual
- `apwip_chosenoptionid` — pricing option escolhida (lookup pra outra entidade)
- `ownerid` — diretor responsável
- `apwip_stage99closedandfundeddeal` — data de Stage 99 quando fechado
- `apwip_dealtypecode` — tipo do deal (lease aggregation, asset purchase, etc.)

## Como apresentar pro Lucas

Não dump JSON. Estrutura assim:

```
L12345 — [name resumido]
  Stage: [stepname]
  Close esperado: [data] ([prob]%)
  Owner: [diretor]
  RF Notes: [primeiras 200 chars] [...]
```

Se ele pedir "tudo", aí sim mostra mais. Default é resumo.
