/* ═══════════════════════════════════════════════════════════════════════
   apw-atividades-semana · COLETA v2 (auditoria de atividades concluídas)

   ANTES DE RODAR, o Claude SEMPRE pergunta ao Lucas (ver SKILL.md §1):
     1. Período — de quando até quando
     2. Diretor(es) — todos os 14 ou quais
     3. Execução — agente (Claude in Chrome) ou snippet F12
   e preenche os 3 parâmetros abaixo.

   Puxa, no período:
     • TODAS as atividades CONCLUÍDAS (statecode=1) dos diretores escolhidos,
       com hora completa (criação/conclusão/prazo/modificação), quem criou,
       tipo e nome do "regarding", texto sem HTML (cap 5.000 car.)
     • Flag `hoje` = concluída no DIA ATUAL (hoje BRT; se a janela não inclui
       hoje, o último dia da janela)
     • Movimentações S1/S3/Reproposta no período (cruzar atividade × avanço)
     • Enriquecimento das opps tocadas (L, nome, dono atual, fase) — tudo num
       run só; o enrich_opps_template.js virou legado.

   COMO RODAR: aba autenticada em https://apwireless.crm.dynamics.com → F12 →
   Console → cola tudo → Enter. Baixa atividades_<ini>_a_<fim>[_diretor].json.

   COMPLIANCE: só Web API JSON; proibido screenshot/read_page/get_page_text no
   Dynamics. 401/403 → reabrir aba, 1 retry. Paginação @odata.nextLink (guard 40).
   ═══════════════════════════════════════════════════════════════════════ */
(async () => {
  // ═══ PARÂMETROS (preenchidos pelo Claude a partir das respostas) ═══
  const PERIODO_INI = "";   // "YYYY-MM-DD"  ·  "" = hoje
  const PERIODO_FIM = "";   // "YYYY-MM-DD"  ·  "" = hoje (fecha 23:59 BRT)
  const DIRETORES   = [];   // [] = todos os 14  ·  ex.: ["Regina", "Kamilla Rosa"] (parcial, sem acento ok)

  // ═══ DERIVADOS ═══
  const HOJE = new Date(Date.now()-3*3600*1000).toISOString().slice(0,10);   // hoje BRT
  const FIM  = PERIODO_FIM || HOJE;
  const INI  = PERIODO_INI || FIM;
  if (INI > FIM) { console.error("✖ PERIODO_INI depois de PERIODO_FIM"); return; }
  const DIA_ATUAL = (HOJE >= INI && HOJE <= FIM) ? HOJE : FIM;
  const D0 = INI+"T03:00:00Z";
  const D1 = new Date(new Date(FIM+"T03:00:00Z").getTime()+24*3600*1000).toISOString();

  if (!/dynamics\.com$/i.test(location.hostname)) { console.error("✖ Rode na aba do Dynamics"); return; }
  const base = location.origin + "/api/data/v9.2";
  const FV = "OData.Community.Display.V1.FormattedValue";
  const LN = "Microsoft.Dynamics.CRM.lookuplogicalname";
  const h  = { "Accept":"application/json","OData-MaxVersion":"4.0","OData-Version":"4.0",
               "Prefer":'odata.maxpagesize=5000,odata.include-annotations="*"' };
  const VIEW = { stage1:"a020dfbe-4a3f-f111-88b4-00224805b156",
                 stage3:"50aca927-4b3f-f111-88b4-00224805b156",
                 pricing:"e85d5310-8c42-f111-88b4-6045bd07461c" };

  // ═══ 14 DIRETORES (Bruna Matos fora desde 24/07; Marcia Mangiulli desde 25/08/2026) ═══
  const NM_ALL = {
    "70a07063-6fdf-e311-8265-00155d00fe04":"Jose Daniel Ramos",
    "c336d752-e6fb-ed11-8849-000d3a5a8269":"Regina Silveira",
    "b5ece3de-6c3c-ee11-bdf4-000d3a5a8e5c":"Kamilla Rosa",
    "0f5c2d0c-d6d4-e911-a9a8-000d3a360ed5":"Felipe Porto",
    "342e4168-9660-e911-a997-000d3a360ed5":"Fabio Boturao",
    "2d3010fa-61f4-ed11-8848-000d3a5a82bf":"Aline Sanzi",
    "f41da072-58a6-ed11-aad1-000d3a5a8baa":"Victoria Navarro",
    "bd19844f-8b38-ee11-bdf4-6045bd095340":"Daiane dos Santos",
    "cb48e1a0-4959-ee11-be6f-000d3a317ead":"Gisele Tognolo",
    "edbec271-d59d-ef11-8a6a-0022480985f3":"Andressa Bueno",
    "bea2794a-97c3-ef11-b8e9-000d3a3355b9":"Roana Reboredo",
    "d49fdec3-f849-ef11-a317-000d3a5be4ff":"Carolina Brentzel",
    "06a1eeda-93d7-f011-8543-6045bd0a09fc":"Aline Felix",
    "8e616ea9-8d8a-f111-ab0f-70a8a5b0fc4c":"Marcia Mangiulli"
  };
  const fold = s => (s||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().trim();
  let NM = NM_ALL;
  if (DIRETORES.length) {
    NM = {};
    for (const q of DIRETORES) {
      const hit = Object.entries(NM_ALL).filter(([g,n]) => fold(n).includes(fold(q)));
      if (hit.length !== 1) {
        console.error("✖ Diretor '"+q+"' → "+(hit.length?"ambíguo: "+hit.map(x=>x[1]).join(", "):"não encontrado")+
                      ". Nomes válidos: "+Object.values(NM_ALL).join(", ")); return;
      }
      NM[hit[0][0]] = hit[0][1];
    }
  }
  const DIR   = Object.keys(NM);
  const norm  = v => (v||"").toString().toLowerCase().replace(/[{}]/g,"");
  const isDir = g => DIR.includes(norm(g));
  const POOL  = /pool|apwreports|surrender|disqualified|system/i;
  const brISO = iso => iso ? new Date(new Date(iso).getTime()-3*3600*1000).toISOString().slice(0,19).replace("T"," ") : "";
  const brDate = iso => brISO(iso).slice(0,10);
  const ta = document.createElement("textarea");
  const txt = s => {
    let t = (s||"").replace(/<(script|style)[^>]*>[\s\S]*?<\/\1>/gi," ")
      .replace(/<br\s*\/?>|<\/p>|<\/div>|<\/tr>|<\/li>/gi,"\n").replace(/<[^>]{0,400}>/g," ");
    ta.innerHTML = t; t = ta.value;
    return t.replace(/[ \t\r\u00a0]+/g," ").replace(/\n\s*\n+/g,"\n").trim();
  };
  async function pg(u) {
    let out=[], next=u, guard=0;
    while (next && guard<40) {
      const r = await fetch(next, {headers:h, credentials:"include"});
      if (r.status===401 || r.status===403) throw new Error("AUTH_"+r.status+" — reabra a aba logada");
      if (!r.ok) throw new Error("HTTP_"+r.status+" @ "+next.slice(0,140));
      const j = await r.json(); out = out.concat(j.value||[]);
      next = j["@odata.nextLink"] || null; guard++;
    }
    return out;
  }
  const eff = (r, sof) => (POOL.test(r["_ownerid_value@"+FV]||"") && r[sof]) ? r[sof] : r._ownerid_value;

  console.log("%cJanela "+INI+" → "+FIM+" · dia atual "+DIA_ATUAL+" · "+DIR.length+" diretor(es): "+Object.values(NM).join(", "),
              "color:#1C75BB;font-weight:bold");

  // ═══ [1/5] Movimentações de estágio ═══
  const movidos = [];
  const addMov = (r, tipo, data, sof) => {
    const og = eff(r, sof); if (!isDir(og)) return;          // só dos diretores escolhidos
    movidos.push({ opp:norm(r.opportunityid), L:r.apwip_opportunityautonumberid||"?", nome:r.name||"",
      tipo, data, dono:NM[norm(og)], dono_guid:norm(og), pool:POOL.test(r["_ownerid_value@"+FV]||"") });
  };
  console.log("[1/5] Stage 1...");
  for (const r of await pg(base+"/opportunities?userQuery="+VIEW.stage1)) {
    const d = (r.apwip_stage1_obtainedleaseeconomics||"").slice(0,10);
    if (d && d>=INI && d<=FIM) addMov(r,"S1",d,"_apwip_stage1owner_value");
  }
  console.log("[2/5] Stage 3...");
  for (const r of await pg(base+"/opportunities?userQuery="+VIEW.stage3)) {
    const d = (r.apwip_stage3date||"").slice(0,10);
    if (d && d>=INI && d<=FIM) addMov(r,"S3",d,"_apwip_stage3owner_value");
  }
  console.log("[3/5] Repropostas...");
  const pr = await pg(base+"/apwip_pricingoptions?userQuery="+VIEW.pricing);
  const sm = pr[0]||{};
  const kS3d = Object.keys(sm).find(k => /stage3date$/.test(k) && !k.includes("@"));
  const kS5d = Object.keys(sm).find(k => /stage5date$/.test(k) && !k.includes("@"));
  const kOpp = Object.keys(sm).find(k => /_apwip_opportunityid_value$/.test(k) && !k.includes("@"));
  const repMap = {};
  for (const r of pr) {
    const cd = brDate(r.createdon);
    if (!cd || cd<INI || cd>FIM) continue;
    if (cd===(r[kS3d]||"").slice(0,10) || cd===(r[kS5d]||"").slice(0,10)) continue;   // orgânica
    const g = norm(r[kOpp]); if (g && !repMap[g]) repMap[g] = cd;
  }
  const repG = Object.keys(repMap);
  for (let i=0; i<repG.length; i+=15) {
    const f = repG.slice(i,i+15).map(x => "opportunityid eq "+x).join(" or ");
    (await pg(base+"/opportunities?$select=opportunityid,name,apwip_opportunityautonumberid,_ownerid_value,_apwip_stage3owner_value&$filter=("+f+")"))
      .forEach(o => addMov(o,"REPROP",repMap[norm(o.opportunityid)],"_apwip_stage3owner_value"));
  }

  // ═══ [4/5] Atividades concluídas ═══
  console.log("[4/5] Atividades concluídas...");
  const ownerF = DIR.map(g => "_ownerid_value eq "+g).join(" or ");
  const FILT = "&$filter=(actualend ge "+D0+" and actualend lt "+D1+") and statecode eq 1 and ("+ownerF+")&$orderby=actualend asc";
  const SEL_FULL  = "$select=activityid,subject,description,activitytypecode,createdon,modifiedon,actualend,scheduledend,actualdurationminutes,statecode,statuscode,_ownerid_value,_regardingobjectid_value,_createdby_value,_modifiedby_value";
  const SEL_BASIC = "$select=activityid,subject,description,activitytypecode,createdon,modifiedon,actualend,statecode,_ownerid_value,_regardingobjectid_value,_createdby_value";
  let raw;
  try { raw = await pg(base+"/activitypointers?"+SEL_FULL+FILT); }
  catch(e) { if (/AUTH/.test(e.message)) throw e; console.warn("select completo falhou — usando básico"); raw = await pg(base+"/activitypointers?"+SEL_BASIC+FILT); }
  const acts = raw.map(a => {
    const d = txt(a.description), conc = brISO(a.actualend);
    return {
      id:a.activityid, tipo:a.activitytypecode||"", tipo_nome:a["activitytypecode@"+FV]||a.activitytypecode||"",
      status:a["statuscode@"+FV]||"", subject:(a.subject||"").trim(),
      desc: d.length>5000 ? d.slice(0,5000)+" […]" : d, desc_len:d.length,
      criada:brISO(a.createdon), concluida:conc, modificada:brISO(a.modifiedon), prazo:brISO(a.scheduledend),
      dur_min:(a.actualdurationminutes ?? null), hoje: conc.slice(0,10)===DIA_ATUAL,
      owner_guid:norm(a._ownerid_value), owner:NM[norm(a._ownerid_value)]||a["_ownerid_value@"+FV]||"",
      criada_por:a["_createdby_value@"+FV]||"", modificada_por:a["_modifiedby_value@"+FV]||"",
      reg_guid:norm(a._regardingobjectid_value), reg_tipo:a["_regardingobjectid_value@"+LN]||"",
      reg_nome:a["_regardingobjectid_value@"+FV]||""
    };
  });

  // ═══ [5/5] Enriquecimento das opps ═══
  console.log("[5/5] Enriquecendo opps...");
  const oppG = [...new Set(acts.filter(a => a.reg_tipo==="opportunity" && a.reg_guid).map(a => a.reg_guid))];
  const opps = {};
  let OSEL = "$select=opportunityid,name,apwip_opportunityautonumberid,_ownerid_value,_apwip_stage1owner_value,_apwip_stage3owner_value,stepname,statecode,createdon";
  for (let i=0; i<oppG.length; i+=20) {
    const f = oppG.slice(i,i+20).map(g => "opportunityid eq "+g).join(" or ");
    let rs;
    try { rs = await pg(base+"/opportunities?"+OSEL+"&$filter=("+f+")"); }
    catch(e) { if (/AUTH/.test(e.message)) throw e;
      OSEL = "$select=opportunityid,name,apwip_opportunityautonumberid,_ownerid_value,_apwip_stage3owner_value,statecode";
      rs = await pg(base+"/opportunities?"+OSEL+"&$filter=("+f+")"); }
    rs.forEach(o => { opps[norm(o.opportunityid)] = {
      L:o.apwip_opportunityautonumberid||"?", nome:o.name||"",
      dono_atual:o["_ownerid_value@"+FV]||"", dono_guid:norm(o._ownerid_value),
      s1owner:o["_apwip_stage1owner_value@"+FV]||"", s3owner:o["_apwip_stage3owner_value@"+FV]||"",
      fase:o.stepname||"", estado:o["statecode@"+FV]||"", criada:brDate(o.createdon) }; });
  }

  // ═══ SAÍDA ═══
  const out = {
    versao:"v2", janela:{ ini:INI, fim:FIM, dia_atual:DIA_ATUAL, d0:D0, d1:D1 },
    coletado_em:new Date().toISOString(), diretores:NM, movidos, atividades:acts, opps,
    _meta:{ n_dir:DIR.length, n_acts:acts.length, n_hoje:acts.filter(a=>a.hoje).length,
            n_movidos:movidos.length, n_opps:Object.keys(opps).length,
            n_sem_regarding:acts.filter(a=>!a.reg_guid).length }
  };
  const suf = DIRETORES.length ? "_"+Object.values(NM).map(n=>fold(n).split(" ")[0]).join("-") : "";
  const fname = "atividades_"+INI+"_a_"+FIM+suf+".json";
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([JSON.stringify(out)], {type:"application/json"}));
  link.download = fname; link.click();
  try { copy(JSON.stringify(out)); } catch(e) {}

  // prévia por diretor
  const P = {};
  for (const a of acts) {
    const b = P[a.owner] = P[a.owner] || { ativ:0, hoje:0, task:0, phone:0, email:0, sem_texto:0, rajada:0, _t:[] };
    b.ativ++; if (a.hoje) b.hoje++;
    if (a.tipo==="task") b.task++; else if (a.tipo==="phonecall") b.phone++; else if (a.tipo==="email") b.email++;
    if (a.desc_len < 30) b.sem_texto++;
    b._t.push(new Date(a.concluida.replace(" ","T")+"Z").getTime());
  }
  for (const b of Object.values(P)) {        // rajada = ≥5 fechadas dentro de 10 min
    const t = b._t.sort((x,y)=>x-y), f = new Set();
    for (let i=0,j=0; i<t.length; i++) { while (t[i]-t[j] > 600000) j++; if (i-j+1 >= 5) for (let k=j;k<=i;k++) f.add(k); }
    b.rajada = f.size; delete b._t;
  }
  console.log("%c✔ PRONTO — "+fname,"color:#009877;font-weight:bold;font-size:14px");
  console.table(Object.fromEntries(Object.entries(P).sort((a,b)=>b[1].ativ-a[1].ativ)));
  return "OK — "+acts.length+" atividades ("+out._meta.n_hoje+" no dia atual "+DIA_ATUAL+") · "+movidos.length+" movimentações";
})()
