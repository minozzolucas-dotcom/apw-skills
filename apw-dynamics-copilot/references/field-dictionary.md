# Dicionário de campos — APW Dynamics 365

Lista dos campos lógicos mais usados nos workflows do Lucas. Use isso para evitar tentativa-e-erro com nomes.

**Aviso**: esta lista é baseada em workflows observados em conversas anteriores. Se um campo não funcionar, faz query de descoberta (ver final desta página) — não assume que o dicionário está sempre atualizado.

## Entidade principal: `opportunity`

### Identificação
| Campo lógico | Tipo | Descrição |
|---|---|---|
| `opportunityid` | GUID | Chave primária |
| `apwip_autonumberid` | String | Código L (sem prefixo no banco, com "L" na UI) |
| `name` | String | Nome/descrição do deal (geralmente endereço/torre) |
| `apwip_dealtypecode` | OptionSet | Tipo: lease aggregation, asset purchase, etc. |

### Estado e stage
| Campo lógico | Tipo | Descrição |
|---|---|---|
| `statecode` | Int | 0=Open, 1=Won, 2=Lost |
| `statuscode` | Int | Detalha sub-estados |
| `stepname` | String | Nome do stage atual (legacy, nem sempre confiável) |
| `apwip_rating` | OptionSet | Hot/Warm/Cold |

### Datas de stage
| Campo lógico | Tipo | Descrição |
|---|---|---|
| `apwip_stage1` | DateTime | Entrada Stage 1 |
| `apwip_stage3` | DateTime | Entrada Stage 3 |
| `apwip_stage99closedandfundeddeal` | DateTime | Fechamento (Stage 99) |
| `estimatedclosedate` | DateTime | Close esperado |
| `actualclosedate` | DateTime | Close real |

### Financeiro
| Campo lógico | Tipo | Descrição |
|---|---|---|
| `closeprobability` | Int | Probabilidade % |
| `apwip_chosenoptionid` | Lookup | Pricing option escolhida (ref. entidade pricing option) |

### Notas e auditoria
| Campo lógico | Tipo | Descrição |
|---|---|---|
| `apwip_rfexpertnotes` | Memo | Notas de RF (inspeção técnica) |
| `apwip_auditcheckbox` | Boolean | Checkbox de auditoria |

### Atribuição
| Campo lógico | Tipo | Descrição |
|---|---|---|
| `ownerid` | Lookup | Owner (geralmente sales director) — usa `_ownerid_value` em GET |
| `createdby` | Lookup | Quem criou |
| `modifiedby` | Lookup | Última modificação |

## Entidades relacionadas

### `systemuser`
Para resolver `_ownerid_value` → nome do diretor.
- `systemuserid` (GUID)
- `fullname`
- `domainname`
- `internalemailaddress`

### Pricing Options (custom)
Nome lógico provável: `apwip_pricingoption` ou similar. **Confirma o nome quando precisar** via descoberta.
- `apwip_pricingoptionid`
- `apwip_purchaseprice`
- `apwip_acf` (Annual Cash Flow)
- `_apwip_opportunityid_value` (FK pra opportunity)

### ACF / Aluguel (custom)
Nome lógico provável: `apwip_acf` ou `apwip_groundrent`. **Confirma o nome quando precisar**.

## Descoberta de campos quando o dicionário falha

Se você precisar de um campo que não está aqui, ou se um campo do dicionário retornar 400, descubra os metadados:

```js
// Lista TODOS os campos da entidade opportunity
(async () => {
  const r = await fetch(`${window.location.origin}/api/data/v9.2/EntityDefinitions(LogicalName='opportunity')/Attributes?$select=LogicalName,DisplayName,AttributeType&$filter=startswith(LogicalName,'apwip_')`, {
    headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}
  });
  const d = await r.json();
  return d.value.map(a => ({
    logical: a.LogicalName,
    display: a.DisplayName?.UserLocalizedLabel?.Label,
    type: a.AttributeType
  }));
})();
```

Pra descobrir entidades custom da APW:

```js
(async () => {
  const r = await fetch(`${window.location.origin}/api/data/v9.2/EntityDefinitions?$select=LogicalName,DisplayName,LogicalCollectionName&$filter=startswith(LogicalName,'apwip_')`, {
    headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}
  });
  const d = await r.json();
  return d.value.map(e => ({
    logical: e.LogicalName,
    collection: e.LogicalCollectionName,
    display: e.DisplayName?.UserLocalizedLabel?.Label
  }));
})();
```

A `LogicalCollectionName` é o que vai no path da URL (ex: `apwip_pricingoptions`), enquanto `LogicalName` é o singular usado em FetchXML.

## Convenções de nome

- **`apwip_`** é o prefixo do publisher APW. Campos custom criados pela APW começam com isso.
- **`msdyn_`** = Microsoft Dynamics standard extension (cuidado ao modificar, tem lógica embutida).
- **`new_`** = publisher default Dataverse — raro na APW mas pode aparecer em dev/sandbox.
- Campos lookup em **GET** vêm como `_FIELDNAME_value` (GUID) e podem ser expandidos com `$expand=FIELDNAME($select=...)`.
- Campos lookup em **PATCH** usam sintaxe `FIELDNAME@odata.bind`.
