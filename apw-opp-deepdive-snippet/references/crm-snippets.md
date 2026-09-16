# CRM — Snippets de extração via console

Todos rodam na aba autenticada do Dynamics (F12 → Console). Usam `window.location.origin`, então funcionam em qualquer tenant sem edição — **exceto** o código L, que o Lucas troca na primeira linha.

---

## Snippet 1 — Localizar e extrair TUDO

Único snippet necessário no caso normal. Troque `LN` pelo número do código L (sem o "L").

```js
window.__L = null;
(async () => {
  const LN = '931470';                       // <<< só isso muda
  const O = window.location.origin;
  const H = {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.include-annotations="*"'};
  const j = async u => { const r = await fetch(u,{headers:H}); const t = await r.text();
    try { return r.ok ? JSON.parse(t) : {__err:r.status,__msg:JSON.parse(t)?.error?.message}; }
    catch { return {__err:r.status,__raw:t.slice(0,300)}; } };

  // A) descobre o campo do código L (sem AttributeType — dá 501)
  const meta = await j(`${O}/api/data/v9.2/EntityDefinitions(LogicalName='opportunity')/Attributes?$select=LogicalName`);
  const N = (meta.value||[]).map(a=>a.LogicalName);
  const cands = N.filter(n=>/autonumber|auto_number|lnumber|l_number|dealnumber|opportunitynumber/i.test(n));
  console.log('🔑 campos candidatos:', cands);
  if (!cands.length) return console.log('❌ nenhum campo de código — tenant errado?');

  // B) acha a opp: campo × formato
  let opp=null, usado=null;
  for (const c of cands) for (const f of [`${c} eq 'L${LN}'`, `${c} eq '${LN}'`, `${c} eq ${LN}`, `contains(${c},'${LN}')`]) {
    const d = await j(`${O}/api/data/v9.2/opportunities?$filter=${encodeURIComponent(f)}&$select=opportunityid,name&$top=5`);
    if (d.value?.length) { opp=d.value[0]; usado=f; break; }
  }
  if (!opp) return console.log(`❌ L${LN} não existe em ${O} — tente o outro tenant`);
  const id = opp.opportunityid;
  console.log('✅', opp.name, '| filtro:', usado, '| guid:', id);

  // C) registro completo, SEM $select e SEM $expand (lookup polimórfico dá 400)
  const full = await j(`${O}/api/data/v9.2/opportunities(${id})`);
  const dados = {}, fmt = {};
  for (const [k,v] of Object.entries(full)) {
    if (k.includes('FormattedValue')) { fmt[k.split('@')[0]] = v; continue; }
    if (k.includes('@')) continue;
    if (v!==null && v!=='' && v!==false) dados[k]=v;
  }
  for (const [k,v] of Object.entries(fmt)) if (v!==null && v!=='') dados[k+' ⟨texto⟩']=v;

  // D) atividades
  const act = await j(`${O}/api/data/v9.2/activitypointers?$filter=_regardingobjectid_value eq ${id}&$select=subject,description,activitytypecode,scheduledstart,actualend,createdon,statecode,_ownerid_value&$orderby=createdon asc`);
  const atividades = (act.value||[]).map(a=>({
    data:a.createdon, dono:a['_ownerid_value@OData.Community.Display.V1.FormattedValue'],
    tipo:a.activitytypecode, status:a['statecode@OData.Community.Display.V1.FormattedValue'],
    subject:a.subject, description:a.description }));

  // E) entidades de atividade diretas (redundância proposital)
  const extra = {};
  for (const e of ['tasks','emails','phonecalls','appointments']) {
    const d = await j(`${O}/api/data/v9.2/${e}?$filter=_regardingobjectid_value eq ${id}&$orderby=createdon asc`);
    if (d.value?.length) extra[e] = d.value.map(x=>({data:x.createdon,subject:x.subject,description:x.description||x.body||x.descriptionbody}));
  }

  // F) notas e anexos
  const notes = await j(`${O}/api/data/v9.2/annotations?$filter=_objectid_value eq ${id}&$select=subject,notetext,filename,filesize,createdon&$orderby=createdon asc`);

  // G) pricing options — descobre o lookup em vez de chutar
  let pricing = null;
  const am = await j(`${O}/api/data/v9.2/apwip_pricingoptions?$top=1`);
  if (am.value?.length) {
    const lk = Object.keys(am.value[0]).filter(k=>/^_.*_value$/.test(k));
    for (const f of lk) {
      const d = await j(`${O}/api/data/v9.2/apwip_pricingoptions?$filter=${f} eq ${id}`);
      if (d.value?.length) { pricing = {campo:f, rows:d.value}; break; }
    }
    if (!pricing) pricing = {campos_testados:lk, resultado:'nenhuma pricing vinculada'};
  }

  const out = {tenant:O, filtroUsado:usado, opp:dados, atividades, extra, notas:notes.value||[], pricing};
  window.__L = JSON.stringify(out,null,1);
  console.log(out);
  console.log(`📊 campos:${Object.keys(dados).length} | atividades:${atividades.length} | notas:${(notes.value||[]).length} | pricing:${pricing?.rows?.length??0} | ${(window.__L.length/1024).toFixed(0)}KB`);
  console.log('👉 agora roda:  copy(window.__L)');
})();
```

Depois, no console: `copy(window.__L)` e colar no chat.

---

## Payload grande (>300KB)

Quase sempre é o HTML das notificações de e-mail do CRM. Rode isto **antes** do `copy` — corta o lixo sem perder conteúdo humano:

```js
(() => {
  const o = JSON.parse(window.__L);
  const lixo = /^(Notification: Opportunity Moved|Proposal for .* will expire|Assignment of |Pricing Desk for|MANAGEMENT TASK|Mail Merge Template|U\/W ACTION REQUIRED|LEGAL ACTION REQUIRED|Country Leader has Approved|Confirm Option Agreement)/i;
  const strip = s => typeof s==='string' && /<\/?[a-z][\s\S]*>/i.test(s)
    ? s.replace(/<style[\s\S]*?<\/style>/gi,'').replace(/<!--[\s\S]*?-->/g,'')
       .replace(/<[^>]+>/g,' ').replace(/&nbsp;/g,' ').replace(/\s+/g,' ').trim().slice(0,1200)
    : s;
  const limpa = a => (a||[]).filter(x=>!lixo.test(x.subject||''))
    .map(x=>({...x, description: strip(x.description)}));
  o.atividades = limpa(o.atividades);
  for (const k in (o.extra||{})) o.extra[k] = limpa(o.extra[k]);
  // pricing: só o que importa
  if (o.pricing?.rows) o.pricing.rows = o.pricing.rows.map(p=>({
    nome:p.apwip_name, id:p.apwip_autonumberid, criado:p.createdon,
    status:p['statuscode@OData.Community.Display.V1.FormattedValue'],
    payout:p.apwip_presentedpayout, irr:p.apwip_maxpayoutirr,
    parcelas:p.apwip_numberofpayments, inicial:p.apwip_initialpayment,
    subsequente:p.apwip_supsequentpayment,
    tipo:p['apwip_transactiontype@OData.Community.Display.V1.FormattedValue'],
    prazo:p.apwip_transactiontermyears, freq:p['apwip_paymentfrequencypricingoption@OData.Community.Display.V1.FormattedValue'],
    calc:p.apwip_calculatorvariables, comissao:p.apwip_projectedcommission,
    notasCom:p.new_commissionnotes }));
  window.__L = JSON.stringify(o,null,1);
  console.log('✂️', (window.__L.length/1024).toFixed(0)+'KB — roda copy(window.__L)');
})();
```

**Cuidado:** as notificações automáticas *não são* 100% lixo. A de "U/W ACTION REQUIRED" e a de "LEGAL ACTION REQUIRED" carregam **Key Notes, IRR aprovado, payout apresentado e o time de back-office designado** — dados que não estão em campo estruturado. Antes de cortar, extraia esses dois. Se preferir, remova-os da regex `lixo`.

---

## Armadilhas de schema (o histórico de erros)

| Erro | Causa | Correção |
|---|---|---|
| `501 Not Implemented` no Attributes | `$select=LogicalName,AttributeType` | só `LogicalName` |
| `400` — *Could not find a property named 'apwip_autonumberid'* | campo é `apwip_opportunityautonumberid` no tenant US | descobrir via metadata, nunca hardcode |
| `400` — *incompatible types 'Edm.String' and 'Edm.Int32'* | código L é string | filtrar com aspas: `eq 'L931470'` |
| `400` no `$expand=ownerid($select=fullname)` | lookup polimórfico (owner = user ou team) | não usar expand; ler `_ownerid_value@...FormattedValue` |
| `400` num `$select` com `stepname` / `apwip_dealtypecode` | campo não existe naquele tenant | puxar registro inteiro sem `$select` |
| `ReferenceError: copy is not defined` | `copy()` não vive em escopo async | salvar em `window.__L`, rodar `copy()` depois |
| lista de campos truncada e inútil | regex com `apw` casa 886 campos | usar termos específicos |
| `401` | sessão expirou | recarregar a aba do Dynamics e logar |
| opp existe mas atividades vazias | filtro no campo errado | conferir `_regardingobjectid_value`; rodar as entidades diretas do bloco E |

---

## Campos que importam no registro da opp

Não existem em todo tenant — leia do que voltou, não presuma.

**Identidade e estágio:** `apwip_opportunityautonumberid`, `name`, `apwip_opportunitystage`, `statuscode`, `statecode`, `apwip_customopportunityname`
**Datas de stage:** `apwip_stage1_obtainedleaseeconomics` … `apwip_stage7date`, `apwip_apapprovaldate`, `apwip_mostrecentstagedate`, `apwip_surrenderedon`
**Donos por stage:** `_apwip_stage1owner_value` … `_apwip_stage7owner_value` — revelam se um diretor só herdou ou trabalhou de fato
**On Hold:** `new_onholddate`, `new_onholdcategoryreason`, `new_boombustcurrentpotname`, `apwip_surrenderreasonopp`, `apwip_surrenderreasonlegal`, `new_rvpcommentsnew`
**Narrativa:** `apwip_opportunitysummary`, `apwip_sitedescription`, `apwip_handoffnotes`, `apwip_notes`, `apwip_3monthsrentstubsnotes`, `apwip_payoutoptionnotesdirector`, `apwip_noteslegal`
**Localização:** `apwip_street1`, `apwip_city`, `apwip_stateprovince`, `apwip_zippostalcode`, `apwip_address1latitude/longitude`
**Contato:** `apwip_contactfirstname/lastname`, `apwip_contactemailaddress`, `apwip_mobilephone`, `apwip_businessphone`
**Back-office:** `_apwip_legaldepartment_value`, `_apwip_paralegalowneruser_value`, `_apwip_processingdepartment_value`, `_apwip_rfexpertowner_value`, `_apwip_closerowner_value`, `_apwip_reviewmanager_value`, `_apwip_pricingmanager_value`
**Escolha comercial:** `_apwip_chosenpricingoption_value` — **compare sempre com a pricing ativa mais recente**
**Checklist documental:** `apwip_receivesignedloi`, `apwip_leaseswallamendments`, `apwip_sitephoto`, `apwip_3monthsrentstubs`, `apwip_completedleaseabstractions`, `apwip_obtainedleaseeconomics`, `apwip_fullyexecutedtermsofagreement`, `apwip_agreedtoterms`

## Campos que importam na pricing option

`apwip_name` · `apwip_autonumberid` (Pxxxxxx) · `createdon` · `statuscode` (Active/Inactive) · `apwip_presentedpayout` · `apwip_maxpayoutirr` · `apwip_numberofpayments` · `apwip_initialpayment` · `apwip_supsequentpayment` · `apwip_transactiontype` · `apwip_transactiontermyears` · `apwip_paymentfrequencypricingoption` · `apwip_percentageofrentspurchased` · `apwip_projectedcommission` · `new_commissionnotes` · **`apwip_calculatorvariables`**

O `calculatorvariables` é ouro: traz o aluguel base, a operadora, o escalador, o mês de fechamento assumido e o tipo de estrutura de cada rodada. É com ele que se monta a tabela de deriva de preço com o aluguel correto em cada data.
