# M-Files — varredura dos documentos do deal

O CRM da APW quase nunca tem anexo: `annotations` voltar vazio é o **normal**, não um erro. Os documentos do deal (matrícula, contrato, aditivos, LOI, extratos, certidões, memorial, fotos) vivem no M-Files em `mfilesus.apwip.com`.

Rode o snippet na aba do M-Files já logada, **não** na do Dynamics.

## Snippet — busca por código L

```js
window.__MF = null;
(async () => {
  const Q = 'L931470';                      // <<< só isso muda
  const O = window.location.origin, H = {'Accept':'application/json'}, out = [];
  let vaults = [];
  try { vaults = await (await fetch(`${O}/REST/session/vaults`,{headers:H})).json(); } catch(e){}
  if (!Array.isArray(vaults) || !vaults.length) {
    console.log('⚠️ não listou vaults. Abra', O+'/REST/session/vaults', 'e me mande o retorno');
    return;
  }
  for (const v of vaults) {
    const r = await fetch(`${O}/REST/objects?q=${encodeURIComponent(Q)}&limit=300`,
      {headers:{...H,'X-Vault':v.GUID}});
    if (!r.ok) { console.log('⚠️', v.Name, '→ HTTP', r.status); continue; }
    const d = await r.json();
    for (const it of (d.Items||[])) out.push({
      vault: v.Name,
      id: it.ObjVer?.ID,
      tipo: it.ObjVer?.Type,
      titulo: it.Title,
      classe: (it.Properties||[]).find(p=>p.PropertyDef===100)?.TypedValue?.DisplayValue,
      criado: it.Created,
      alterado: it.LastModified,
      files: (it.Files||[]).map(f=>f.Name+'.'+f.Extension).join(' | ')
    });
  }
  out.sort((a,b)=> (a.criado||'').localeCompare(b.criado||''));
  console.log('📁 docs:', out.length); console.table(out);
  window.__MF = JSON.stringify(out,null,1);
  console.log('👉 roda:  copy(window.__MF)');
})();
```

## Fallbacks

| Sintoma | Tentar |
|---|---|
| `404` em `/REST/objects` | versão antiga: `/REST/objects.aspx?q=...` |
| `/REST/session/vaults` vazio ou 404 | pegar o GUID do vault da própria URL da aba e fixar em `vaults=[{Name:'x',GUID:'{...}'}]` |
| `401` | sessão expirou — recarregar e logar |
| busca por L não retorna nada | buscar pelo nome do proprietário, pelo município, ou pelo ID do site da torreira |
| retorna centenas de itens | o `q` casou com outro L parecido — filtrar `titulo.includes('L931470')` no `out` |

## Ler o conteúdo de um documento

A skill **não** baixa nem lê PDF do M-Files. Se a análise depender do conteúdo de um documento específico (tipicamente a **matrícula**), peça ao Lucas que baixe e anexe no chat. Aponte exatamente qual arquivo, pelo título que apareceu na tabela.

## Classes de documento APW e o que cada uma responde

| Classe / título típico | Responde |
|---|---|
| Matrícula / Certidão de inteiro teor | proprietário real, gravames, restrições de destinação, viabilidade de DRS × Fee Simple |
| Contrato de locação + Termos Aditivos | quem é o pagador (operadora × torreira), índice e data-base do reajuste, cláusula de cessão/anuência, ROFR |
| POP / extrato bancário / comprovante | quem **de fato** paga hoje e quanto — sobrepõe o contrato |
| LOI / Carta de Intenção assinada | valor e estrutura efetivamente aceitos |
| Carta Proposta | o que foi apresentado (≠ o que foi aceito) |
| IPTU / cadastro imobiliário | dedução do ACF, débito municipal |
| Certidões (cível, fiscal, protesto, CNIB) | risco de fraude à execução — mata deal independentemente do instrumento |
| Memorial descritivo / planialtimétrico | viabiliza DRS sem desmembramento |
| SIR / relatório fotográfico | risco de churn do site |
| Ata / procuração / documentos societários | legitimidade de quem assina |

## Cruzamento obrigatório

Compare os documentos do M-Files com o **checklist documental do CRM** (`apwip_receivesignedloi`, `apwip_3monthsrentstubs`, `apwip_sitephoto`, `apwip_leaseswallamendments`, etc.) e com o `apwip_handoffnotes`. Divergência entre "checkbox marcado no CRM" e "documento ausente no M-Files" — ou o inverso — é achado e vai para o bloco 4 do dossiê.
