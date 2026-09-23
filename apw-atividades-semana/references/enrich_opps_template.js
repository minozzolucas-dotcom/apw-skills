/* ═══════════════════════════════════════════════════════════════════════
   SNIPPET 2/2 — ENRIQUECIMENTO DE OPPS EXTRAS (apw-atividades-semana · APW)

   COMO USAR (Claude preenche isto e entrega pronto pro Lucas):
   1. Extraia do JSON produzido pelo snippet 1 (atividades_semana_*.json)
      o conjunto EXTRAS = { opp de cada acts_semana } - { opp de cada deals }.
      Ou seja, as opps que tiveram atividade mas NÃO moveram estágio.
   2. Substitua o placeholder __GUIDS_JSON__ abaixo pelo array JS literal desses
      GUIDs (ex.: ["5921ef75-99a8-...", "9c5eecae-4b24-..."]). Não use aspas
      simples nem trailing comma — precisa ser JSON parseável por JS.
   3. Substitua __ARQUIVO_SAIDA__ pelo nome do arquivo (ex.:
      "opps_extras_2026-09-14_a_2026-09-16.json").
   4. Entregue o snippet preenchido pro Lucas colar no console F12 da mesma
      aba autenticada. Baixa o arquivo + copia JSON pro clipboard.

   COMPLIANCE: mesma regra do collect_semana.js — só Web API, sem screenshot.
   ═══════════════════════════════════════════════════════════════════════ */
(async () => {
  const GUIDS = __GUIDS_JSON__;
  const OUT_FILE = "__ARQUIVO_SAIDA__";

  const base = location.origin + "/api/data/v9.2";
  const FV   = "OData.Community.Display.V1.FormattedValue";
  const h = { "Accept":"application/json","OData-MaxVersion":"4.0","OData-Version":"4.0",
    "Prefer":'odata.maxpagesize=5000,odata.include-annotations="'+FV+'"' };

  console.log("Enriquecendo "+GUIDS.length+" opps em batches de 20...");
  const out = {};
  const CHUNK = 20;
  for (let i = 0; i < GUIDS.length; i += CHUNK) {
    const batch = GUIDS.slice(i, i + CHUNK);
    const filt  = batch.map(g => "opportunityid eq " + g).join(" or ");
    const url   = base + "/opportunities?$select=opportunityid,name,apwip_opportunityautonumberid,_ownerid_value,_apwip_stage3owner_value&$filter=(" + filt + ")";
    let r;
    try { r = await fetch(url, {headers:h, credentials:"include"}); }
    catch(e) { console.error("fetch fail batch", i, e); continue; }
    if (r.status===401 || r.status===403) { console.error("AUTH "+r.status+" — reabra a aba"); return; }
    if (!r.ok) { console.error("HTTP "+r.status+" batch "+i); continue; }
    const j = await r.json();
    for (const o of (j.value||[])) {
      out[(o.opportunityid||"").toLowerCase()] = {
        L: o.apwip_opportunityautonumberid || "?",
        nome: o.name || "",
        dono_atual: o["_ownerid_value@"+FV] || "",
        dono_guid: (o._ownerid_value||"").toLowerCase(),
        s3owner: (o._apwip_stage3owner_value||"").toLowerCase()
      };
    }
    if (i % 60 === 0) console.log("  ...", Math.min(i+CHUNK, GUIDS.length), "/", GUIDS.length);
  }

  const blob = new Blob([JSON.stringify(out,null,1)], {type:"application/json"});
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
  a.download = OUT_FILE; a.click();
  try {
    copy(JSON.stringify(out));
    console.log("%c✔ PRONTO — "+Object.keys(out).length+" opps enriquecidas ("+OUT_FILE+")","color:#009877;font-weight:bold;font-size:14px");
    console.log("%cJSON copiado pro clipboard ✅","color:#009877");
  } catch(e) {}
  return "OK: "+Object.keys(out).length;
})()
