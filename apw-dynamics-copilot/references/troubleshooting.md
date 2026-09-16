# Troubleshooting — Dynamics 365 Web API

Coisas que dão errado e como diagnosticar. Esta lista vem de horas de tentativa-e-erro do Lucas — não reinvente a roda.

## "FetchXML retorna array vazio mas a view mostra dados"

**Diagnóstico em ordem:**

1. **Verifica que está executando contra a sessão certa**:
```js
window.location.origin
```
Tem que ser `apwbrasil.crm2.dynamics.com` ou `apw.crm.dynamics.com` (com o protocolo `https://` no `origin`).

2. **Verifica que o filtro está usando o tipo certo do campo**:
- Option set (picklist) → valor é Int (`<condition attribute='apwip_rating' operator='eq' value='100000001'/>`)
- Boolean → valor é `'true'` ou `'false'` em string
- DateTime → ISO format
- Lookup → use `_FIELDNAME_value` no `$filter`, valor é GUID em aspas

3. **Verifica o nome lógico do campo**:
Faz query mínima sem filtro pra confirmar que entidade e campo existem:
```js
fetch(`${window.location.origin}/api/data/v9.2/opportunities?$top=1&$select=opportunityid,apwip_autonumberid,apwip_NOME_DO_CAMPO`)
```
Se 400 → campo errado. Usa o descobridor em `field-dictionary.md`.

4. **Verifica visibilidade**: a view pode estar usando filtros do tipo "minhas oportunidades" que dependem do usuário logado. Se você está mandando o `fetchXml` cru via API, talvez precise adicionar manualmente `<condition attribute='ownerid' operator='eq-userid'/>`.

## "Status 400 Bad Request"

Lê o corpo da resposta — quase sempre tem mensagem útil:

```js
const r = await fetch(url, {...});
if (!r.ok) {
  const errText = await r.text();
  return {status: r.status, error: errText};
}
```

Erros comuns:
- `Resource not found for the segment 'XXX'` → entidade ou navegação errada. Confirma `LogicalCollectionName`.
- `Could not find a property named 'XXX'` → campo não existe nessa entidade. Confirma com descobridor.
- `Invalid character in identifier` → você botou aspas ou caracter especial no GUID. GUID vai sem chaves, sem aspas, sem hífens... espera, **com** hífens. Sem chaves, sem aspas.

## "Status 401 / sessão expirada"

A sessão do navegador expirou. **Não tente fazer login você mesmo.** Avisa o Lucas:

> "A sessão do Dynamics expirou. Atualiza a aba do CRM, faz login se pedir, e me avisa que eu sigo daqui."

Após ele confirmar, refaça o `tabs_context_mcp` pra pegar o tab ID novo (se a aba foi recarregada, o ID pode mudar).

## "Status 403 Forbidden"

Usuário não tem permissão pra esse recurso. Acontece em:
- Tabelas administrativas (`solutions`, `workflows`)
- Campos que requerem security role específica
- Records owned por outras unidades de negócio sem cross-team access

**Não tente** contornar com endpoints alternativos. Avisa o Lucas: "Sem permissão pra ler X. Você consegue ver isso direto no CRM?".

## "Resultado paginado em 5000 records mas eu sei que tem mais"

`@odata.nextLink` no final do JSON. Pagina assim:

```js
(async () => {
  const headers = {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.maxpagesize=5000,odata.include-annotations=*'};
  let url = `${window.location.origin}/api/data/v9.2/opportunities?$select=...&$filter=...`;
  const all = [];
  while (url) {
    const r = await fetch(url, {headers});
    const d = await r.json();
    all.push(...d.value);
    url = d['@odata.nextLink']; // já vem com paging cookie
  }
  return {total: all.length, sample: all.slice(0,3)};
})();
```

## "Quero usar `$expand` mas dá erro"

Sintaxe correta:
```
$expand=ownerid($select=fullname,internalemailaddress)
```

- Lookup pra entidade única → expand direto
- Relação 1:N → `$expand=opportunity_strongest_pricing_options($select=apwip_acf;$top=1)`
- Múltiplos expands → separar por vírgula: `$expand=ownerid($select=fullname),createdby($select=fullname)`

## "JavaScript_tool tab ID errado"

O `tabId` muda quando:
- A aba é fechada e reaberta
- A página recarrega completamente (F5, login refresh)
- O Chrome reinicia

Antes de cada bloco de execução longo, refaz `tabs_context_mcp` pra confirmar que a aba certa ainda existe com o ID que você lembra. Se sumiu, pergunta pro Lucas qual aba ele quer usar.

## "Network request travado / pendente"

Os snippets nesta skill usam `await fetch(...)` dentro de IIFE async. O `javascript_tool` precisa que a Promise resolva no `return` do IIFE pra ver o resultado. Se um snippet "trava", é provavelmente porque:

1. Faltou o `return` final do `await`
2. Foi feito `.then()` sem `await` no fim
3. Status real foi 401 e o navegador está esperando login interativo — checa a aba

Padrão seguro:
```js
(async () => {
  try {
    const r = await fetch(url, {headers});
    if (!r.ok) return {error: r.status, text: await r.text()};
    const d = await r.json();
    return {count: d.value?.length, sample: d.value?.slice(0,3)};
  } catch (e) {
    return {exception: e.message};
  }
})();
```

## "Resultado vem como string em vez de objeto"

`javascript_tool` serializa o retorno. Se você retornar objeto, vem como string JSON. Não precisa fazer `JSON.stringify` no return — só retorna o objeto e ele aparece como JSON na resposta. Mas se retornar uma string que **é** um JSON, dá pra parsear no contexto da conversa.

## Quando nada funciona

Se três tentativas diferentes falharam e você não está fazendo progresso, **para e fala com o Lucas**. Mostra:
1. O que tentou
2. Qual erro deu
3. O que você acha que está acontecendo
4. Pergunta se ele quer abrir a view no navegador e você lê dela direto via `get_page_text`, como fallback.

Não fica 20 minutos batendo cabeça em silêncio.
