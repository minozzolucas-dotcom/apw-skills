# Extração CRM e identificação de fontes

## Princípios

- Sempre via **sessão autenticada do navegador** (F12 → console), nunca screenshot em domínio corporativo — regra da `apw-chrome-agent-lean-compliance`.
- Não persistir dados do CRM em arquivo. O board consolidado pode ser salvo; dumps brutos não.
- Se a extração falhar por permissão, peça ao Lucas a view exportada em vez de insistir.

## Dynamics — lote por L-number

No console de `*.crm.dynamics.com` ou `apwbrasil.crm2.dynamics.com`, com a sessão aberta:

```js
const Ls = ["L961988","L364755","L411362"]; // completar o lote
const filtro = Ls.map(l => `name eq '${l}'`).join(" or ");
const url = `/api/data/v9.2/opportunities`
  + `?$select=name,_ownerid_value,statuscode,stepname,estimatedvalue,createdon`
  + `&$filter=${encodeURIComponent(filtro)}`;

const r = await fetch(url, { headers: { "Accept":"application/json", "OData-MaxVersion":"4.0", "OData-Version":"4.0" }, credentials:"include" });
const d = await r.json();
copy(JSON.stringify(d.value, null, 2));   // cola aqui no chat
```

Ajuste `$select` conforme o schema real do ambiente — os nomes lógicos de campos customizados (torreira, property type, on hold reason) variam. Para descobrir:

```js
const m = await (await fetch("/api/data/v9.2/EntityDefinitions(LogicalName='opportunity')/Attributes?$select=LogicalName,DisplayName", {credentials:"include"})).json();
console.table(m.value.map(a => ({ln:a.LogicalName, dn:a.DisplayName?.UserLocalizedLabel?.Label})));
```

Se preferir não montar query, a `apw-dynamics-copilot` já resolve extração — delegue e volte com o resultado.

## Campos que importam para a triagem

| Campo | Por quê |
|---|---|
| Stage atual | 🟢 em Stage 1 não vira notificação — não há instrumento |
| Owner | quem conduz a conversa com o locador |
| On hold reason | pode já haver histórico de recusa de cessão |
| Property type | pré-roteia Trilha A vs. B |
| Torreira / locatária | define destinatário da notificação |
| RVP / Legal Comments | parecer anterior sobre a mesma cláusula |
| Aluguel contratual | conferir contra a coluna da planilha e contra o POP |

## Identificação da locatária real

Os IDs de site trazem a assinatura da towerco. Padrão observado em portfólio legado Claro/SITES:

- Prefixo `TC` + UF + município abreviado + sequencial → safra Claro legado (ex.: `TCRSPOA0018` = RS / Porto Alegre)
- Prefixo `TT` + UF + município + sequencial → safra TIM/SITES
- Prefixo curto UF + sequencial (`SP03984`, `DF0046`, `EPE0037`) → cadastro antigo por estado

Isso é **indício**, não prova. A locatária de verdade sai de três fontes, nessa ordem de força:

1. **POP / comprovante de pagamento** — quem transfere o dinheiro hoje
2. Instrumento de cessão da locatária, se houver
3. Contrato original — só diz quem era no início

Sites de operadora Claro que migraram para a **SITES Latinoamérica** (towerco da América Móvil) são o caso clássico onde o contrato original nomeia a operadora e o pagador atual é outra pessoa jurídica. Notificar a operadora nesse cenário não produz efeito perante o devedor.

## Campanha de desconto

Quando a planilha traz coluna de desconto (5% / 10% / 15%), isso normalmente é campanha de redução de custo da towerco batendo no locador. Registre por deal:

- **Status:** pedido em aberto · assinado em aditivo · recusado pelo locador
- Se assinado: data, aditivo nº, novo valor — o crédito cedido passa a ser o pós-desconto
- Se em aberto: é a cunha comercial. O locador está sendo pressionado a perder receita permanente; a APW oferece valor à vista sobre o fluxo cheio. Sinalizar para o owner priorizar.

## Higiene de coordenadas

Faixa válida Brasil: **lat −34 a +6**, **long −74 a −34**.

Erros comuns: sinal invertido, lat/long trocadas, dígito extra. Exemplo real: `lat −80.98 / long −34.88` para um endereço em Recife — o correto fica em torno de `−8.09 / −34.88` (a latitude perdeu o ponto decimal). Sempre reportar a correção provável em vez de só apontar o erro.
