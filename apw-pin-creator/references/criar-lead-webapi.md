# Criar o Lead via Web API

Procedimento do passo 6. Só execute depois do "confirma" explícito do Lucas (passo 5).

## Pré-condições

1. **Aba aberta no tenant Brasil.** Confirme com `tabs_context_mcp` que existe aba em `apwbrasil.crm2.dynamics.com`. Se não houver, peça ao Lucas para abrir e logar — **a skill não faz login**.
2. A confirmação do passo 5 já aconteceu. Sem isso, não prossiga.

## Por que tem um passo de descoberta

O `leadsearch2.aspx` é uma **página customizada da APW**, não um form padrão do Dynamics. O botão `Create Lead` pode:
- (a) gravar na entidade `lead` **nativa** do Dynamics via `/api/data/v9.2/leads`; ou
- (b) chamar um endpoint custom da APW (um plugin, uma action, um web resource próprio).

Não dá pra saber de antemão. Por isso o passo 6 **começa descobrindo**, em vez de assumir.

## Descoberta — via javascript_tool

Com a página do form `leadsearch2.aspx` aberta, inspecione (sem screenshot, sem clicar em `Create Lead`):

1. Leia o handler do botão `Create Lead` — qual função JavaScript ele dispara.
2. Veja se essa função monta um `fetch`/`XMLHttpRequest` para `/api/data/v9.x/leads` (caso a — entidade nativa) ou para outra URL (caso b — endpoint custom).
3. Identifique os nomes lógicos dos campos que a função envia no payload. Os campos custom da APW usam o prefixo `apwip_`. Os campos de Lead nativos têm nomes padrão (`firstname`, `lastname`, `address1_city`, `address1_latitude`, `address1_longitude`, `subject`, `description`, etc.).
4. Anote o método (`POST`) e os headers que a página usa.

O objetivo é **reproduzir a mesma chamada que o botão faria**, com os valores que o Lucas confirmou — não construir uma chamada nova adivinhada.

## Executar a criação

Caso (a) — entidade `lead` nativa:
```js
fetch(`${window.location.origin}/api/data/v9.2/leads`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'OData-MaxVersion': '4.0',
    'OData-Version': '4.0'
  },
  body: JSON.stringify({
    // mapear os campos confirmados no passo 5 para os nomes lógicos
    // descobertos na inspeção. Ex.:
    // subject, firstname, lastname, address1_city, address1_stateorprovince,
    // address1_latitude, address1_longitude, description, ...
  })
}).then(r => r.ok ? r.headers.get('OData-EntityId') : r.json())
```
O retorno do `OData-EntityId` contém o GUID do Lead criado.

Caso (b) — endpoint custom: reproduza exatamente a chamada descoberta na inspeção, com os valores confirmados.

## Confirmação de sucesso

- Se a API retornar sucesso, extraia o ID/GUID do Lead criado e devolva ao Lucas: "Lead criado — ID `<...>`."
- **Não tire screenshot pra "comprovar".** Confie no retorno da API. Screenshot depois de ação bem-sucedida é proibido (regra herdada da `apw-dynamics-copilot`).
- Se quiser, ofereça abrir o Lead recém-criado para o Lucas conferir — mas como ação a pedido dele, não automática.

## Fallback honesto

Se a descoberta falhar — endpoint não reproduzível, função ofuscada, payload que depende de estado de sessão da página — **não force um POST cego.** Um POST num endpoint errado pode criar lixo no CRM ou falhar silenciosamente.

Em vez disso: entregue ao Lucas o mapeamento 100% pronto, na ordem exata dos campos do form, para ele colar manualmente no `leadsearch2.aspx` e clicar `Create Lead`. A skill já economizou todo o trabalho pesado (ler contrato, farejar coordenada, montar o resumo) — os três cliques finais na mão são um custo aceitável e seguro.

Diga ao Lucas claramente que caiu no fallback e por quê. Não simule que criou.
