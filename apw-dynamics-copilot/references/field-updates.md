# Atualização de campos

Quando o Lucas pede pra atualizar RF Expert Notes, checkboxes de auditoria, stage, ou qualquer outro campo. Updates são via `PATCH` na Web API.

## Regra de ouro: confirma antes de escrever

Updates são irreversíveis pelo usuário comum. **Sempre** mostra o diff pro Lucas antes:

```
Vou atualizar L12345:
  apwip_rfexpertnotes:
    de: "Inspeção pendente"
    pra: "Inspeção concluída em 18/05. Estrutura OK. Sem observações."
  apwip_auditcheckbox:
    de: false
    pra: true
Confirma? (sim/não)
```

Espera "sim" / "confirmado" / "segue". Qualquer ambiguidade, pergunta de novo. Não interprete "ok" sozinho como autorização de write em massa.

## Snippet PATCH single record

```js
(async () => {
  const opportunityId = 'GUID_AQUI'; // sem chaves
  const updates = {
    apwip_rfexpertnotes: 'Texto novo aqui',
    apwip_auditcheckbox: true
  };
  const r = await fetch(`${window.location.origin}/api/data/v9.2/opportunities(${opportunityId})`, {
    method: 'PATCH',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'OData-MaxVersion': '4.0',
      'OData-Version': '4.0',
      'If-Match': '*'  // garante update (não upsert)
    },
    body: JSON.stringify(updates)
  });
  return {status: r.status, ok: r.ok, statusText: r.statusText};
})();
```

Status 204 = sucesso. 412 = pré-condição falhou (provavelmente record não existe). 400 = payload inválido (tipo errado de campo, ou campo não existe).

## Batch update (vários deals de uma vez)

Para mais de 5 updates, vale usar `$batch` da Web API. Mas tem complexidade extra (multipart/mixed). Para volumes pequenos (até ~10), prefere `Promise.all` com PATCHes individuais:

```js
(async () => {
  const updates = [
    {id: 'GUID_1', body: {apwip_auditcheckbox: true}},
    {id: 'GUID_2', body: {apwip_auditcheckbox: true}},
    {id: 'GUID_3', body: {apwip_auditcheckbox: true}}
  ];
  const headers = {
    'Accept':'application/json',
    'Content-Type':'application/json',
    'OData-MaxVersion':'4.0',
    'OData-Version':'4.0',
    'If-Match':'*'
  };
  const results = await Promise.all(updates.map(async u => {
    const r = await fetch(`${window.location.origin}/api/data/v9.2/opportunities(${u.id})`, {
      method:'PATCH', headers, body: JSON.stringify(u.body)
    });
    return {id: u.id, status: r.status, ok: r.ok};
  }));
  return results;
})();
```

## Lookups (campos que referenciam outras entidades)

Lookups precisam de sintaxe `@odata.bind`. Exemplo: atribuir owner:

```js
const updates = {
  'ownerid@odata.bind': '/systemusers(GUID-DO-USUARIO)'
};
```

Não use `_ownerid_value` no body do PATCH — esse é só para leitura. Para escrita, sempre `@odata.bind`.

## Opção sets (picklist)

Picklists são valores inteiros. Quando o Lucas falar em "muda pra Hot", você precisa do código numérico. Exemplo: `apwip_rating = 100000001` (Hot). Os códigos costumam ser 100000000, 100000001, 100000002 etc.

Pra descobrir os códigos:

```js
(async () => {
  const r = await fetch(`${window.location.origin}/api/data/v9.2/EntityDefinitions(LogicalName='opportunity')/Attributes(LogicalName='apwip_rating')/Microsoft.Dynamics.CRM.PicklistAttributeMetadata?$expand=OptionSet`, {
    headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}
  });
  const d = await r.json();
  return d.OptionSet.Options.map(o => ({value: o.Value, label: o.Label.UserLocalizedLabel?.Label}));
})();
```

## RF Expert Notes — caso particular

Este campo recebe texto livre vindo de PDFs de inspeção técnica processados pelo Filipe. Workflow consolidado:
1. PDF chega por email
2. Você extrai os pontos-chave (estrutura, vegetação, acesso, observações)
3. Formata como texto contínuo (não markdown, o campo não renderiza)
4. Mostra o draft pro Lucas
5. Após confirmação, faz o PATCH em `apwip_rfexpertnotes`
6. Geralmente também marca `apwip_auditcheckbox: true` (depende do fluxo)

Confirma com o Lucas se o checkbox de auditoria deve ser marcado junto — depende se a inspeção fechou todos os pontos ou não.

## Não tente

- **Não tente** mudar `statecode` (Open/Closed Won/Closed Lost) via PATCH direto — Dynamics rejeita. Para fechar oportunidade, usa a ação `Win`/`Lose` (POST em endpoint específico). Geralmente o Lucas faz isso pela UI mesmo.
- **Não tente** mudar `createdby`, `createdon`, `modifiedby`, `modifiedon` — campos read-only.
- **Não tente** mudar campos com prefixo de publisher de terceiros (ex: `msdyn_`) sem antes confirmar com o Lucas — pode ser de extensão Microsoft que tem lógica própria.
