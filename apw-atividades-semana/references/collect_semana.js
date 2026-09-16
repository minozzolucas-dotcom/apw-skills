/* ═══════════════════════════════════════════════════════════════════════
   SNIPPET 1/2 — COLETA BASE (apw-atividades-semana · APW Brasil)

   Puxa do Dynamics 365, entre SEM_INI e ALVO:
     1. Deals que MOVERAM S1 (apwip_stage1_obtainedleaseeconomics)
     2. Deals que moveram S3 (apwip_stage3date)
     3. Repropostas (pricingoption createdon, não-orgânica)
     4. Dono atual de cada opp (com fallback pool → stage3owner)
     5. Histórico completo de atividades desses deals
     6. TODAS as atividades concluídas (statecode=1) pelos 13 diretores no
        intervalo — TEM opps que NÃO estão no bloco 1-3 (opps trabalhadas
        que não moveram estágio). Essas opps vêm só como GUID no `opp` da
        atividade — o snippet 2 (enrich) resolve nome/L/dono delas.

   COMO RODAR:
   1. Aba autenticada em https://apwireless.crm.dynamics.com — F12 → Console
   2. Ajuste os parâmetros abaixo (SEM_INI_IN, ALVO_IN)
   3. Cole TUDO → Enter
   4. Baixa atividades_semana_<SEM_INI>_a_<ALVO>.json + copia pro clipboard
   5. Manda o arquivo/JSON pro Claude
   6. Claude gera o snippet 2 (enrich) com os GUIDs das opps extras

   COMPLIANCE (apw-chrome-agent-lean-compliance):
   Tudo por Web API JSON. PROIBIDO read_page/get_page_text/screenshot no
   Dynamics. 401/403 → reabrir aba, 1 retry, senão parar. Paginar via
   @odata.nextLink (guard 40).
   ═══════════════════════════════════════════════════════════════════════ */
(async () => {
  // ═══ PARÂMETROS ═══
  const ALVO_IN    = "";                 // "" = hoje BRT; "YYYY-MM-DD" p/ fechamento retroativo
  const SEM_INI_IN = "";                 // "" = ALVO (colapsa pra 1 dia); "YYYY-MM-DD" p/ semana

  // ═══ DERIVADOS ═══
  const _H = (ALVO_IN    || new Date(new Date().getTime()-3*3600*1000).toISOString().slice(0,10));
  const _S = (SEM_INI_IN || _H);
  const D0 = _S+"T03:00:00Z";              // início da janela (00h BRT do primeiro dia)
  const D1 = new Date().toISOString();     // agora — pega tudo até o momento do corte
  const SEMINI = _S;

  const base = location.origin + "/api/data/v9.2";
  const FV   = "OData.Community.Display.V1.FormattedValue";
  const h    = { "Accept":"application/json","OData-MaxVersion":"4.0","OData-Version":"4.0",
    "Prefer":'odata.maxpagesize=5000,odata.include-annotations="'+FV+'"' };
  const hA   = h;

  const VIEW = { stage1:"a020dfbe-4a3f-f111-88b4-00224805b156",
                 stage3:"50aca927-4b3f-f111-88b4-00224805b156",
                 pricing:"e85d5310-8c42-f111-88b4-6045bd07461c" };

  // ═══ DIRETORES (13 ativos — Bruna Matos removida 24/07/2026) ═══
  // ⚠ Marcia Mangiulli entrou 25/08/2026 — falta subir o GUID dela aqui.
  //   Enquanto não subir, atividades da Marcia NÃO entram no acts_semana.
  const NM = {
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
  const DIR    = Object.keys(NM);
  const isDir  = g => DIR.includes((g||"").toLowerCase());
  const norm   = v => (v||"").toString().toLowerCase().replace(/[{}]/g,"");
  const POOL   = /pool|apwreports|surrender|disqualified|system/i;
  const brDate = iso => iso ? new Date(new Date(iso).getTime()-3*3600*1000).toISOString().slice(0,10) : "";

  async function pg(u, hh) {
    let out=[], next=u, guard=0;
    while (next && guard<40) {
      const r = await fetch(next, {headers:hh, credentials:"include"});
      if (r.status===401 || r.status===403) throw new Error("AUTH_"+r.status+" — reabra a aba logada");
      if (!r.ok) throw new Error("HTTP_"+r.status+" @ "+next.slice(0,120));
      const j = await r.json();
      out = out.concat(j.value||[]);
      next = j["@odata.nextLink"] || null;
      guard++;
    }
    return out;
  }

  // owner efetivo: se pool/system, cai pro stageXowner
  function eff(r, sof) {
    const nm = r["_ownerid_value@"+FV]||"";
    if (POOL.test(nm) && r[sof]) return r[sof];
    return r._ownerid_value;
  }

  const out = { alvo:_H, janela_ini:_S, deals:[], acts_semana:[], _meta:{} };
  const dealMap = {};   // oppGuid -> deal
  function upsert(guid, o, tipo, ownerGuid, ownerNome, pool) {
    const k = norm(guid); if (!k) return;
    if (!dealMap[k]) dealMap[k] = {
      opp: k, L: o.apwip_opportunityautonumberid || "?", nome: o.name || "",
      dono_atual: ownerNome, dono_guid: norm(ownerGuid),
      pool: !!pool, tipos: [], atividades: []
    };
    if (!dealMap[k].tipos.includes(tipo)) dealMap[k].tipos.push(tipo);
  }

  // ═══ [1/5] Stage 1 movidos ═══
  console.log("[1/5] Stage 1 movidos entre "+_S+" e "+_H+"...");
  const s1 = await pg(base+"/opportunities?userQuery="+VIEW.stage1, h);
  for (const r of s1) {
    const d = (r.apwip_stage1_obtainedleaseeconomics||"").slice(0,10);
    if (!d || d<_S || d>_H) continue;
    const og = eff(r,"_apwip_stage1owner_value");
    const onm = r["_ownerid_value@"+FV]||"";
    const pool = POOL.test(onm);
    const nome = isDir(norm(og)) ? NM[norm(og)] : (onm||"—");
    upsert(r.opportunityid, r, "S1", og, nome, pool);
  }

  // ═══ [2/5] Stage 3 movidos ═══
  console.log("[2/5] Stage 3 movidos...");
  const s3 = await pg(base+"/opportunities?userQuery="+VIEW.stage3, h);
  for (const r of s3) {
    const d = (r.apwip_stage3date||"").slice(0,10);
    if (!d || d<_S || d>_H) continue;
    const og = eff(r,"_apwip_stage3owner_value");
    const onm = r["_ownerid_value@"+FV]||"";
    const pool = POOL.test(onm);
    const nome = isDir(norm(og)) ? NM[norm(og)] : (onm||"—");
    upsert(r.opportunityid, r, "S3", og, nome, pool);
  }

  // ═══ [3/5] Repropostas (pricings não-orgânicas) ═══
  console.log("[3/5] Repropostas...");
  const pr = await pg(base+"/apwip_pricingoptions?userQuery="+VIEW.pricing, h);
  const sm = pr[0]||{};
  const kS3d = Object.keys(sm).find(k => /stage3date$/.test(k) && !k.includes("@"));
  const kS5d = Object.keys(sm).find(k => /stage5date$/.test(k) && !k.includes("@"));
  const kOpp = Object.keys(sm).find(k => /_apwip_opportunityid_value$/.test(k));
  const repGuids = [];
  for (const r of pr) {
    const cd = brDate(r.createdon);
    if (!cd || cd<_S || cd>_H) continue;
    const s3d = (r[kS3d]||"").slice(0,10);
    const s5d = (r[kS5d]||"").slice(0,10);
    if (cd===s3d || cd===s5d) continue;         // orgânica
    const g = norm(r[kOpp]);
    if (g && !repGuids.includes(g)) repGuids.push(g);
  }
  if (repGuids.length) {
    for (let i=0; i<repGuids.length; i+=15) {
      const f = repGuids.slice(i,i+15).map(x => "opportunityid eq "+x).join(" or ");
      const rs = await pg(base+"/opportunities?$select=opportunityid,name,apwip_opportunityautonumberid,_ownerid_value,_apwip_stage3owner_value&$filter="+f, hA);
      rs.forEach(o => {
        const og = eff(o,"_apwip_stage3owner_value");
        const onm = o["_ownerid_value@"+FV]||"";
        upsert(o.opportunityid, o, "REPROP", og, isDir(norm(og))?NM[norm(og)]:(onm||"—"), POOL.test(onm));
      });
    }
  }

  const dealGuids = Object.keys(dealMap);
  console.log("   → "+dealGuids.length+" deals moveram entre "+_S+" e "+_H);

  // ═══ [4/5] Histórico completo de atividades dos deals movidos ═══
  console.log("[4/5] Histórico de atividades dos deals movidos...");
  const ASEL = "$select=activityid,subject,description,activitytypecode,createdon,actualend,statecode,_ownerid_value,_regardingobjectid_value";
  for (let i=0; i<dealGuids.length; i+=10) {
    const f = dealGuids.slice(i,i+10).map(x => "_regardingobjectid_value eq "+x).join(" or ");
    const rs = await pg(base+"/activitypointers?"+ASEL+"&$filter=("+f+")&$orderby=createdon asc", hA);
    rs.forEach(a => {
      const k = norm(a._regardingobjectid_value); if (!dealMap[k]) return;
      dealMap[k].atividades.push({
        id: a.activityid, tipo: a.activitytypecode||"", subject: a.subject||"",
        desc: a.description||"", data: brDate(a.createdon),
        owner_guid: norm(a._ownerid_value), owner: a["_ownerid_value@"+FV]||"",
        concluida: a.statecode===1
      });
    });
    if (i%50===0) console.log("   ...", i, "/", dealGuids.length);
  }

  // ═══ [5/5] Atividades CONCLUÍDAS pelos 13 diretores no intervalo ═══
  console.log("[5/5] Atividades concluídas na semana (13 diretores)...");
  const ownerF = DIR.map(g => "_ownerid_value eq "+g).join(" or ");
  const ad = await pg(base+"/activitypointers?"+ASEL+
    "&$filter=(actualend ge "+D0+" and actualend lt "+D1+") and statecode eq 1 and ("+ownerF+")", hA);
  ad.forEach(a => out.acts_semana.push({
    id: a.activityid, tipo: a.activitytypecode||"", subject: a.subject||"", desc: a.description||"",
    data: brDate(a.actualend||a.createdon),
    owner_guid: norm(a._ownerid_value),
    owner: NM[norm(a._ownerid_value)] || a["_ownerid_value@"+FV] || "",
    opp: norm(a._regardingobjectid_value)
  }));

  out.deals = Object.values(dealMap);
  out._meta = {
    alvo:_H, janela_ini:_S, d0:D0, d1:D1, sem_ini:SEMINI,
    coletado_em: new Date().toISOString(), n_dir: DIR.length,
    n_deals: out.deals.length, n_acts_semana: out.acts_semana.length,
    n_acts_hist: out.deals.reduce((n,d)=>n+d.atividades.length, 0),
    n_opps_extras: (() => {
      const dg = new Set(out.deals.map(d=>d.opp));
      return new Set(out.acts_semana.filter(a=>a.opp && !dg.has(a.opp)).map(a=>a.opp)).size;
    })()
  };

  // download + copy
  const fname = "atividades_semana_"+_S+"_a_"+_H+".json";
  const blob = new Blob([JSON.stringify(out,null,1)], {type:"application/json"});
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = fname; a.click();
  try {
    copy(JSON.stringify(out));
    console.log("%c✔ PRONTO — "+fname+" (janela "+_S+" → "+_H+")","color:#009877;font-weight:bold;font-size:14px");
    console.log("%cJSON também copiado pro clipboard ✅","color:#009877");
  } catch(e) {}

  console.log("Deals movidos:", out._meta.n_deals,
              "| Atividades concluídas:", out._meta.n_acts_semana,
              "| Opps extras (só ativ.):", out._meta.n_opps_extras);
  console.table(out.deals.map(d => ({L:d.L, Tipo:d.tipos.join("+"), Dono:d.dono_atual,
    Pool: d.pool?"POOL":"", Ativs: d.atividades.length})));
  return "OK — "+out._meta.n_deals+" deals · "+out._meta.n_acts_semana+" atividades · "+out._meta.n_opps_extras+" opps extras";
})()
