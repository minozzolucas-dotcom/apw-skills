/* =====================================================================
   APW Brasil — coleta do REPORTE DIÁRIO de produtividade (Dynamics 365 Web API)

   COMO USAR
   1. Aba do Chrome já autenticada em https://apwireless.crm.dynamics.com
   2. Colar este bloco inteiro no javascript_tool
   3. Para FECHAR UM DIA PASSADO: setar ALVO="YYYY-MM-DD" (default = hoje).
   4. O retorno é o esqueleto do data.json — faltam só os destaques
      (destaque_dia, destaque_semana, leitura_dia), que o Claude preenche.

   COMPLIANCE (apw-chrome-agent-lean-compliance)
   Tudo por Web API JSON. PROIBIDO read_page / get_page_text / screenshot
   em domínio Dynamics. 401/403 → reabrir aba, 1 retry, depois parar.
   Paginar via @odata.nextLink (guard < 20). NÃO usar $select junto de
   userQuery (dá 400) — ler as colunas do payload da view.

   O QUE ESTE SCRIPT MEDE (por diretor, no DIA e na SEMANA)
     Stage 1        — apwip_stage1_obtainedleaseeconomics (data do estágio)
     Stage 3        — apwip_stage3date
     Repropostas    — pricing options que contam pela regra v2 (por titularidade)
     Atividades     — activitypointer não-automáticas
     Substantivas   — atividades com conteúdo estratégico (regra de tamanho+sinais)

   HOST/VIEWS/CAMPOS — validados em produção (ver SKILL.md).
   ===================================================================== */
(async () => {
  const API = "https://apwireless.crm.dynamics.com/api/data/v9.2";
  const FV = "OData.Community.Display.V1.FormattedValue";
  const H = {
    "Accept": "application/json",
    "OData-MaxVersion": "4.0",
    "OData-Version": "4.0",
    "Prefer": 'odata.maxpagesize=5000,odata.include-annotations="' + FV + '"'
  };

  if (!/apwireless\.crm\.dynamics\.com/i.test(location.origin))
    return JSON.stringify({ error: "Aba errada. Abra https://apwireless.crm.dynamics.com e rode de novo." });

  // ---------- views (userQuery) ----------
  const VIEW_S1  = "a020dfbe-4a3f-f111-88b4-00224805b156"; // opportunities — Stage 1
  const VIEW_S3  = "50aca927-4b3f-f111-88b4-00224805b156"; // opportunities — Stage 3
  const VIEW_PRC = "e85d5310-8c42-f111-88b4-6045bd07461c"; // apwip_pricingoptions — Pricing

  // ---------- campos de data (SKILL.md, validados) ----------
  const F_S1  = "apwip_stage1_obtainedleaseeconomics";
  const F_S3  = "apwip_stage3date";
  const F_S5  = "apwip_stage5date";                        // farejado (pode não existir)
  const F_PRC = "createdon";

  // ---------- 13 diretores Brasil (HARDCODED; Bruna Matos removida 24/07/2026) ----------
  // Ao entrar/sair diretor, mexer AQUI e em N_DIR no build_report.py.
  const NM = {
    "70a07063-6fdf-e311-8265-00155d00fe04": "Jose Daniel Ramos",
    "c336d752-e6fb-ed11-8849-000d3a5a8269": "Regina Silveira",
    "b5ece3de-6c3c-ee11-bdf4-000d3a5a8e5c": "Kamilla Rosa",
    "0f5c2d0c-d6d4-e911-a9a8-000d3a360ed5": "Felipe Porto",
    "342e4168-9660-e911-a997-000d3a360ed5": "Fabio Boturao",
    "2d3010fa-61f4-ed11-8848-000d3a5a82bf": "Aline Sanzi",
    "f41da072-58a6-ed11-aad1-000d3a5a8baa": "Victoria Navarro",
    "bd19844f-8b38-ee11-bdf4-6045bd095340": "Daiane dos Santos",
    "cb48e1a0-4959-ee11-be6f-000d3a317ead": "Gisele Tognolo",
    "edbec271-d59d-ef11-8a6a-0022480985f3": "Andressa Bueno",
    "bea2794a-97c3-ef11-b8e9-000d3a3355b9": "Roana Reboredo",
    "d49fdec3-f849-ef11-a317-000d3a5be4ff": "Carolina Brentzel",
    "06a1eeda-93d7-f011-8543-6045bd0a09fc": "Aline Felix",
    "8e616ea9-8d8a-f111-ab0f-70a8a5b0fc4c": "Marcia Mangiulli"
  };
  const DIR_GUIDS = Object.keys(NM);
  const POOL = /pool|apwreports|surrender|disqualified|system|admin|integra|crm|queue/i;
  const norm = v => (v || "").toString().toLowerCase().replace(/[{}]/g, "");
  const isDir = g => !!NM[norm(g)];

  // ---------- janelas ----------
  const ALVO = null;                          // "2026-08-03" para fechar um dia passado
  const hoje = ALVO ? new Date(ALVO + "T12:00:00") : new Date();
  const iso = d => d.toISOString().slice(0, 10);
  const DIA = iso(hoje);                       // dia-alvo em data local BR

  // início da semana = segunda-feira da semana do dia-alvo
  const semIni = (() => {
    const d = new Date(hoje); const dow = (d.getDay() + 6) % 7; // 0=segunda
    d.setDate(d.getDate() - dow); return iso(d);
  })();
  const anoIni = hoje.getFullYear() + "-01-01";

  // corte superior: fim do dia-alvo em BR = ALVO+1 03:00:00Z (BR = UTC-3)
  const FIM_UTC = (() => {
    const d = new Date(hoje); d.setDate(d.getDate() + 1);
    return iso(d) + "T03:00:00Z";
  })();
  const semIniUTC = semIni + "T03:00:00Z";     // 00:00 BR
  const anoIniUTC = anoIni + "T03:00:00Z";

  // dias úteis (seg–sex) decorridos na semana até o dia-alvo (inclusive)
  const diasUteisDecorridos = (() => {
    let n = 0; const a = new Date(semIni + "T12:00:00"), b = new Date(DIA + "T12:00:00");
    for (let d = new Date(a); d <= b; d.setDate(d.getDate() + 1)) {
      const w = d.getDay(); if (w >= 1 && w <= 5) n++;
    }
    return n;
  })();

  // BR = UTC-3. Converte um UTC do CRM para a data local brasileira (YYYY-MM-DD).
  const brDate = utc => {
    if (!utc) return null;
    const d = new Date(utc); d.setHours(d.getHours() - 3);
    return d.toISOString().slice(0, 10);
  };
  const inSemana = dia => dia && dia >= semIni && dia <= DIA;   // seg..dia-alvo
  const isDia    = dia => dia === DIA;

  // ---------- fetch paginado ----------
  async function pg(url) {
    const out = []; let next = url, guard = 0;
    while (next && guard++ < 20) {
      const r = await fetch(next, { headers: H, credentials: "include" });
      if (r.status === 401 || r.status === 403) throw new Error("AUTH_" + r.status);
      if (!r.ok) throw new Error("HTTP_" + r.status + " @ " + next.slice(0, 120));
      const j = await r.json();
      out.push(...(j.value || []));
      next = j["@odata.nextLink"] || null;
    }
    return out;
  }
  // roda uma view por userQuery (sem $select — dá 400 junto de userQuery)
  async function view(entity, id) {
    return pg(API + "/" + entity + "?userQuery=" + id);
  }

  // ---------- estrutura acumuladora ----------
  const zero = () => ({ s1: 0, s3: 0, rep: 0, ativ: 0, subst: 0 });
  const D = {};                                // guid -> {nome, dia, semana, ls}
  DIR_GUIDS.forEach(g => { D[g] = { nome: NM[g], guid: g, dia: zero(), semana: zero(),
                                    ls: { dia: {}, semana: {} } }; });
  const tot = { dia: zero(), semana: zero() };
  const bump = (g, campo, dia, L) => {
    if (!isDir(g)) return;
    const gg = norm(g);
    if (inSemana(dia)) { D[gg].semana[campo]++; tot.semana[campo]++;
      if (L) (D[gg].ls.semana[campo] = D[gg].ls.semana[campo] || []).push(L); }
    if (isDia(dia))    { D[gg].dia[campo]++;    tot.dia[campo]++;
      if (L && campo !== "ativ" && campo !== "subst")
        (D[gg].ls.dia[campo] = D[gg].ls.dia[campo] || []).push(L); }
  };

  // owner efetivo de S1/S3: owner direto; se pool/system, cai pro *stageXowner*
  const effOwner = (r, stageOwnerKey) => {
    const nm = r["_ownerid_value@" + FV] || "";
    if (!POOL.test(nm) && isDir(r._ownerid_value)) return norm(r._ownerid_value);
    if (stageOwnerKey && r[stageOwnerKey]) return norm(r[stageOwnerKey]);
    return norm(r._ownerid_value);
  };
  const findKey = (row, rx) => Object.keys(row || {}).find(k => rx.test(k)) || null;
  const Lof = r => r.apwip_opportunityautonumberid || r["apwip_opportunityautonumberid@" + FV] || null;

  const avisos = [];

  // ================= 1. STAGE 1 =================
  let s1rows = [];
  try { s1rows = await view("opportunities", VIEW_S1); }
  catch (e) { avisos.push("Stage 1 view: " + e.message); }
  const k1owner = s1rows.length ? findKey(s1rows[0], /_apwip_stage1owner_value$/) : null;
  for (const r of s1rows) {
    const dia = brDate(r[F_S1]);
    if (!dia || dia > DIA) continue;           // descarta o que passou do dia-alvo
    const g = effOwner(r, k1owner);
    bump(g, "s1", dia, Lof(r));
  }

  // ================= 2. STAGE 3 =================
  let s3rows = [];
  try { s3rows = await view("opportunities", VIEW_S3); }
  catch (e) { avisos.push("Stage 3 view: " + e.message); }
  const k3owner = s3rows.length ? findKey(s3rows[0], /_apwip_stage3owner_value$/) : null;
  for (const r of s3rows) {
    const dia = brDate(r[F_S3]);
    if (!dia || dia > DIA) continue;
    const g = effOwner(r, k3owner);
    bump(g, "s3", dia, Lof(r));
  }

  // ================= 3. REPROPOSTAS (regra v2 — por titularidade) =================
  // 3a. pricing options da view, dentro da janela (<= dia-alvo)
  let prcRows = [];
  try { prcRows = await view("apwip_pricingoptions", VIEW_PRC); }
  catch (e) { avisos.push("Pricing view: " + e.message); }

  const oppKeyPrc = prcRows.length
    ? (findKey(prcRows[0], /_apwip_opportunityid_value$/) || "_apwip_opportunityid_value")
    : "_apwip_opportunityid_value";

  const prcByOpp = {};                          // oppId -> [{dia, createdon}]
  const oppIds = new Set();
  for (const p of prcRows) {
    const oid = norm(p[oppKeyPrc]); if (!oid) continue;
    const dia = brDate(p[F_PRC]);
    if (!dia || dia > DIA) continue;            // descarta pricing além do dia-alvo
    (prcByOpp[oid] = prcByOpp[oid] || []).push({ dia, createdon: p[F_PRC] });
    oppIds.add(oid);
  }

  // 3b. detalhe das opps referenciadas: owner atual + stage3/5 owner + stage3/5 date + L
  //     farejamento do campo de stage5 owner: tenta COM, cai pra SEM.
  const oppList = [...oppIds];
  const oppInfo = {};
  let stage5ownerDisp = "verificar";
  async function fetchOppChunk(ids, withS5) {
    const sel = "apwip_opportunityautonumberid,_ownerid_value," +
                "_apwip_stage3owner_value," + F_S3 +
                (withS5 ? ",_apwip_stage5owner_value," + F_S5 : "");
    const filt = ids.map(g => "opportunityid eq " + g).join(" or ");
    return pg(API + "/opportunities?$select=" + sel + "&$filter=(" + filt + ")");
  }
  for (let i = 0; i < oppList.length; i += 20) {
    const chunk = oppList.slice(i, i + 20);
    let rows = null;
    try { rows = await fetchOppChunk(chunk, true); stage5ownerDisp = true; }
    catch (e) {
      // schema pode não ter _apwip_stage5owner_value → regra usa só S3 owner
      try { rows = await fetchOppChunk(chunk, false); stage5ownerDisp = "verificar"; }
      catch (e2) { avisos.push("Opp detail chunk: " + e2.message); rows = []; }
    }
    for (const r of rows) {
      const oid = norm(r.opportunityid);
      const s5o = r["_apwip_stage5owner_value"] ? norm(r._apwip_stage5owner_value) : null;
      oppInfo[oid] = {
        L: Lof(r),
        owner: norm(r._ownerid_value),
        ownerNm: r["_ownerid_value@" + FV] || "",
        s3owner: r["_apwip_stage3owner_value"] ? norm(r._apwip_stage3owner_value) : null,
        s5owner: s5o,
        s3date: brDate(r[F_S3]),
        s5date: r[F_S5] ? brDate(r[F_S5]) : null
      };
    }
  }

  // 3c. crédito de reproposta por opp, deduplicado a 1/opp/dia, atribuído ao dono atual
  const anoCorrente = hoje.getFullYear();
  const inThisYear = d => d && (+d.slice(0, 4) === anoCorrente);
  for (const oid of oppList) {
    const info = oppInfo[oid]; if (!info) continue;
    // dono efetivo: dono atual; se pool/system, cai pro s3owner
    let dono = info.owner;
    if ((POOL.test(info.ownerNm) || !isDir(dono)) && info.s3owner) dono = info.s3owner;
    if (!isDir(dono)) continue;                 // fora dos 13

    // herdado = Stage 3 E Stage 5 movidos por OUTRA pessoa (não o dono atual)
    // (se stage5owner indisponível, decide só pelo S3 owner)
    const s3other = info.s3owner && info.s3owner !== dono;
    const s5other = stage5ownerDisp === true ? (info.s5owner && info.s5owner !== dono) : s3other;
    const herdado = s3other && s5other;

    // ordena as pricing da opp por data
    const ps = (prcByOpp[oid] || []).slice().sort((a, b) =>
      (a.createdon || "").localeCompare(b.createdon || ""));
    if (!ps.length) continue;

    // deal que o PRÓPRIO dono moveu p/ S3/S5 no ano corrente → 1ª pricing é orgânica
    const proprioMoveu = !herdado &&
      ((info.s3owner === dono && inThisYear(info.s3date)) ||
       (stage5ownerDisp === true && info.s5owner === dono && inThisYear(info.s5date)) ||
       // sem stage5owner e sem sinal de herdado, tratamos como próprio
       (!info.s3owner && !info.s5owner));

    const contam = herdado ? ps : (proprioMoveu ? ps.slice(1) : ps);
    // dedup: no máx. 1 crédito por opp por dia
    const diasComCredito = [...new Set(contam.map(p => p.dia))];
    for (const dia of diasComCredito) bump(dono, "rep", dia, info.L);
  }

  // ================= 4. ATIVIDADES + SUBSTANTIVAS =================
  // sinais de conteúdo estratégico
  const SIG = [
    /\b(r\$|\d{1,3}(\.\d{3})*(,\d{2})?|\d+\s?(reais|mil|k))\b/i,                 // valor/número
    /(s[íi]ndico|propriet[áa]ri|administrador|condom[íi]nio|operadora|torre|locador|advogad)/i, // contraparte
    /(pr[óo]ximo passo|retornar|agendar|enviar|aguard|follow|reuni|visita|proposta|marcar|ligar)/i, // próximo passo
    /(obje[çc]|recus|negocia[çc]|contraproposta|exig|condi[çc]|quer|pediu|preocupa)/i            // objeção/info
  ];
  const nSig = t => SIG.reduce((n, rx) => n + (rx.test(t) ? 1 : 0), 0);
  const isSubst = t => { const L = (t || "").trim().length;
    return L >= 180 || (L >= 140 && nSig(t) >= 2); };
  // filtro de automática v2 (casa no texto todo OU no início)
  const AUTO_ANY   = /(mail merge|automatic activity|template using the|completed automatically by the|xl calculator)/i;
  const AUTO_START = /^\s*(begin work|pricing desk|management task|create (verbal|written) proposal|moved to stage|workflow|reminder)/i;
  const isAutoText = t => { const s = (t || "").trim(); return AUTO_ANY.test(s) || AUTO_START.test(s); };

  // atividades dos 13 diretores na janela da semana (createdon)
  const orFilterOwner = DIR_GUIDS.map(g => "_ownerid_value eq " + g).join(" or ");
  let actRows = [];
  try {
    actRows = await pg(API + "/activitypointers?$select=activityid,subject,description," +
      "createdon,_ownerid_value&$filter=(createdon ge " + semIniUTC +
      " and createdon lt " + FIM_UTC + ") and (" + orFilterOwner + ")");
  } catch (e) { avisos.push("Activities: " + e.message); }

  for (const a of actRows) {
    const g = norm(a._ownerid_value); if (!isDir(g)) continue;
    const dia = brDate(a.createdon); if (!dia || dia > DIA) continue;
    const desc = a.description || "", subj = a.subject || "";
    const auto = isAutoText(desc) && isAutoText(subj);   // descarta só se AMBOS automáticos
    if (auto) continue;
    bump(g, "ativ", dia, null);
    if (isSubst(desc)) bump(g, "subst", dia, null);
  }

  // ================= 5. montar o esqueleto do data.json =================
  const brDMY = s => s.slice(8, 10) + "/" + s.slice(5, 7) + "/" + s.slice(0, 4);
  const diretores = DIR_GUIDS
    .map(g => D[g])
    .sort((a, b) => {
      // ordena por movimento na semana (S3 > S1 > rep), depois substantivas
      const mv = x => x.semana.s3 * 100 + x.semana.s1 * 10 + x.semana.rep;
      return mv(b) - mv(a) || b.semana.subst - a.semana.subst || a.nome.localeCompare(b.nome);
    });

  const out = {
    referencia: brDMY(DIA),
    alvo: DIA,
    corte_hora: new Date().toISOString(),               // carimbo do corte (drift)
    dia: brDMY(DIA),
    semana_janela: brDMY(semIni) + " – " + brDMY(DIA),
    dias_uteis: { decorridos: diasUteisDecorridos, total: 5 },
    metas: { s1: 3, s3: 2, repropostas: 4, atividades: 100, substantivas_pct: 35,
             ativ_dia: 20, subst_dia_pct: 35 },
    n_diretores: DIR_GUIDS.length,
    diretores,
    totais: { dia: tot.dia, semana: tot.semana },
    destaque_dia: null,          // Claude preenche (maior movimento HOJE)
    destaque_semana: null,       // Claude preenche (maior movimento na SEMANA)
    leitura_dia: "",             // Claude preenche (1–3 frases factuais; vazio = bloco não renderiza)
    _meta: {
      host: location.origin,
      views: { s1: VIEW_S1, s3: VIEW_S3, pricing: VIEW_PRC },
      campos: { s1: F_S1, s3: F_S3, s5: F_S5, pricing: F_PRC },
      stage5owner_disponivel: stage5ownerDisp,          // true | "verificar"
      contagem: { s1_rows: s1rows.length, s3_rows: s3rows.length,
                  pricing_rows: prcRows.length, opps_detalhadas: oppList.length,
                  atividades: actRows.length },
      avisos
    }
  };

  console.log(JSON.stringify(out, null, 2));
  if (stage5ownerDisp === "verificar")
    console.warn("ATENÇÃO: _apwip_stage5owner_value indisponível — regra de reproposta usou só o S3 owner. " +
                 "Confirmar o nome real do campo de stage5 owner no Dynamics.");
  if (avisos.length) console.warn("AVISOS:", avisos.join(" | "));
  return out;
})();
