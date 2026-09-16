/* collection.js — APW Stage 1 Quality Audit · coleta via Claude in Chrome (volume-safe)
   Rode no javascript_tool numa aba autenticada em https://apwireless.crm.dynamics.com
   Desenhado pra cohorts grandes (800+ opps): cap de descrição, dedup, teto por opp, e
   retorno EM FATIAS (guarda tudo em window.__APW_AUDIT_STR e devolve só o cabeçalho).
   Depois rode references/dump-slices.js para puxar as fatias e remontar o raw.json.
   PROIBIDO read_page/get_page_text/screenshot no CRM. Ajuste YEAR/VIEWs no topo. */
(async () => {
  // ---------- constantes ----------
  const YEAR = 2026;
  const VIEW_OPP = "b844749b-eb6f-f111-ab0d-00224805b156"; // opportunity: Stage 1 movidos no ano
  const VIEW_ACT = "ad83a393-ed6f-f111-ab0d-00224805b156"; // activitypointer (referência)
  const DESC_CAP = 1000;   // corta descrição (scorer só precisa de sinal, não do texto todo)
  const ACTS_CAP = 60;     // teto de atividades por opp (mantém as mais recentes)
  const SLICE = 500000;    // tamanho de cada fatia de retorno (~500KB, seguro p/ javascript_tool)

  const base = location.origin + "/api/data/v9.2";
  const FV = "OData.Community.Display.V1.FormattedValue";
  const h = { "Accept": "application/json", "OData-MaxVersion": "4.0", "OData-Version": "4.0",
    "Prefer": 'odata.maxpagesize=5000,odata.include-annotations="' + FV + '"' };

  if (!/apwireless\.crm\.dynamics\.com/i.test(location.origin))
    return JSON.stringify({ error: "Aba errada. Abra https://apwireless.crm.dynamics.com e rode de novo." });

  const NM = {
    "98e379bf-6d55-ed11-bba3-000d3a5a8269": "Bruna Matos", "70a07063-6fdf-e311-8265-00155d00fe04": "Jose Daniel Ramos",
    "c336d752-e6fb-ed11-8849-000d3a5a8269": "Regina Silveira", "b5ece3de-6c3c-ee11-bdf4-000d3a5a8e5c": "Kamilla Rosa",
    "0f5c2d0c-d6d4-e911-a9a8-000d3a360ed5": "Felipe Porto", "342e4168-9660-e911-a997-000d3a360ed5": "Fabio Boturao",
    "2d3010fa-61f4-ed11-8848-000d3a5a82bf": "Aline Sanzi", "f41da072-58a6-ed11-aad1-000d3a5a8baa": "Victoria Navarro",
    "bd19844f-8b38-ee11-bdf4-6045bd095340": "Daiane dos Santos", "cb48e1a0-4959-ee11-be6f-000d3a317ead": "Gisele Tognolo",
    "edbec271-d59d-ef11-8a6a-0022480985f3": "Andressa Bueno", "bea2794a-97c3-ef11-b8e9-000d3a3355b9": "Roana Reboredo",
    "d49fdec3-f849-ef11-a317-000d3a5be4ff": "Carolina Brentzel", "06a1eeda-93d7-f011-8543-6045bd0a09fc": "Aline Felix"
  };
  const POOL = /pool|apwreports|surrender|disqualified|system/i;
  const norm = v => (v || "").toString().toLowerCase().replace(/[{}]/g, "");

  async function pg(url, hh) {
    let out = [], n = url, g = 0;
    while (n && g < 40) {
      const r = await fetch(n, { headers: hh, credentials: "include" });
      if (r.status === 401 || r.status === 403) throw new Error("AUTH_" + r.status);
      if (!r.ok) throw new Error("HTTP_" + r.status + " @ " + n.slice(0, 120));
      const j = await r.json(); out = out.concat(j.value || []); n = j["@odata.nextLink"] || null; g++;
    }
    return out;
  }
  async function viewFetchXml(viewId) {
    for (const ent of ["savedqueries", "userqueries"]) {
      const r = await fetch(`${base}/${ent}(${viewId})?$select=name,fetchxml`, { headers: h, credentials: "include" });
      if (r.ok) { const d = await r.json(); return { name: d.name, fetchxml: d.fetchxml, kind: ent }; }
    }
    return null;
  }
  function discover(fxml) {
    const attrs = [...fxml.matchAll(/<attribute\s+name='([^']+)'/g)].map(m => m[1]);
    const find = (...rx) => attrs.find(a => rx.some(x => x.test(a))) || null;
    return {
      _attrs: attrs,
      L:        find(/opportunityautonumber/i, /autonumber/i),
      stage1:   find(/stage1.*lease|stage1.*econom|stage1$/i, /stage1/i),
      stage3:   find(/stage3.*abstrac|stage3.*lease|stage3date|stage3$/i, /stage3/i),
      surrender:find(/surrender.*reason/i, /surrender/i),
      proptype: find(/propertytype/i, /property_type/i, /typeofproperty/i, /tipoimovel/i),
    };
  }
  const valFV = (row, field) => field ? (row[field + "@" + FV] ?? row[field] ?? null) : null;
  const rawV  = (row, field) => field ? (row[field] ?? null) : null;

  // ---------- 1. colunas das views ----------
  const vOpp = await viewFetchXml(VIEW_OPP);
  const vAct = await viewFetchXml(VIEW_ACT);
  if (!vOpp) return JSON.stringify({ error: "View de opportunity não encontrada. Confira VIEW_OPP." });
  const col = discover(vOpp.fetchxml);

  // ---------- 2. cohort de opportunities ----------
  let oppRows = [];
  for (const param of [`savedQuery=${VIEW_OPP}`, `userQuery=${VIEW_OPP}`]) {
    try { oppRows = await pg(`${base}/opportunities?${param}`, h); if (oppRows.length) break; } catch (e) {}
  }
  if (!oppRows.length) return JSON.stringify({ error: "View de opportunity rodou vazia.", _meta: { columns: col } });

  const s1OwnerKey = Object.keys(oppRows[0]).find(k => /_apwip_stage1owner_value$/.test(k));
  function effOwner(r) {
    const directName = r["_ownerid_value@" + FV] || "";
    if (POOL.test(directName) && s1OwnerKey && r[s1OwnerKey])
      return { id: norm(r[s1OwnerKey]), name: r[s1OwnerKey + "@" + FV] || "" };
    return { id: norm(r._ownerid_value), name: directName };
  }

  const opps = {}; const cohortGuids = [];
  for (const r of oppRows) {
    const guid = norm(r.opportunityid); if (!guid) continue;
    const own = effOwner(r); const dirName = NM[own.id] || null;
    opps[guid] = {
      L: rawV(r, col.L) || r.apwip_opportunityautonumberid || r.apwip_autonumberid || "?",
      owner: dirName || own.name || "—", owner_is_director: !!dirName,
      is_pool: !dirName && (POOL.test(own.name) || !NM[own.id]),
      stage1_date: rawV(r, col.stage1) || r.apwip_stage1_obtainedleaseeconomics || null,
      stage3_date: rawV(r, col.stage3) || r.apwip_stage3date || null,
      surrender_reason: valFV(r, col.surrender),
      property_type: valFV(r, col.proptype),
      acts: []
    };
    cohortGuids.push(guid);
  }

  // ---------- 3. atividades (chunk de 20, dedup, cap) ----------
  const jan1 = `${YEAR}-01-01T00:00:00Z`;
  const sel = "$select=activityid,description,activitytypecode,isworkflowcreated,createdon,_ownerid_value,_regardingobjectid_value";
  const seen = new Set(); let chunksOk = 0, chunksErr = 0, actCount = 0;
  for (let i = 0; i < cohortGuids.length; i += 20) {
    const chunk = cohortGuids.slice(i, i + 20);
    const f = chunk.map(g => `_regardingobjectid_value eq ${g}`).join(" or ");
    const url = `${base}/activitypointers?${sel}&$filter=(createdon ge ${jan1}) and (${f})`;
    let rows = [];
    try { rows = await pg(url, h); chunksOk++; } catch (e) { chunksErr++; continue; }
    for (const a of rows) {
      const id = norm(a.activityid); if (id && seen.has(id)) continue; if (id) seen.add(id);
      const g = norm(a._regardingobjectid_value); if (!opps[g]) continue;
      opps[g].acts.push({
        desc: (a.description || "").slice(0, DESC_CAP),
        type: a["activitytypecode@" + FV] || a.activitytypecode || "",
        owner: a["_ownerid_value@" + FV] || "",
        auto: !!a.isworkflowcreated,
        created: a.createdon || ""
      });
      actCount++;
    }
  }
  // cap por opp (mais recentes)
  for (const g in opps) {
    const A = opps[g].acts;
    if (A.length > ACTS_CAP) { A.sort((x, y) => (y.created || "").localeCompare(x.created || "")); opps[g].acts = A.slice(0, ACTS_CAP); }
  }

  // ---------- 4. montar, guardar em window, devolver SÓ o cabeçalho ----------
  const out = {
    year: YEAR, host: location.origin, collected: new Date().toISOString(),
    _meta: {
      view_opp: { id: VIEW_OPP, name: vOpp.name, kind: vOpp.kind },
      view_act: vAct ? { id: VIEW_ACT, name: vAct.name, kind: vAct.kind } : null,
      columns_discovered: col, desc_cap: DESC_CAP, acts_cap: ACTS_CAP,
      collection: { opps: cohortGuids.length, activities: actCount, chunks_ok: chunksOk, chunks_err: chunksErr }
    },
    opps: Object.values(opps)
  };
  const str = JSON.stringify(out);
  window.__APW_AUDIT_STR = str;
  const nSlices = Math.ceil(str.length / SLICE);
  return JSON.stringify({
    ok: true, stored_in: "window.__APW_AUDIT_STR",
    total_opps: cohortGuids.length, total_activities: actCount,
    chunks_ok: chunksOk, chunks_err: chunksErr,
    str_len: str.length, slice_size: SLICE, n_slices: nSlices,
    columns_discovered: col,
    note: "Confira columns_discovered. Agora rode dump-slices.js " + nSlices + "x (i=0.." + (nSlices - 1) + ") e remonte o raw.json."
  });
})();
