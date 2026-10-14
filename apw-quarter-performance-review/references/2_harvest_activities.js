// ═══════════════════════════════════════════════════════════════
// APW · HARVEST 2/3 · Atividades CRM YTD por diretor
// Conta phonecall + email + task + appointment criadas pelo diretor
// Classifica como "substantiva" se description >= 50 chars
// Também separa por trimestre (Q1/Q2/Q3/Q4)
// ~1-3 min pra rodar (paginação, 4 entidades)
// ═══════════════════════════════════════════════════════════════
(async () => {
  const orgUrl = Xrm.Utility.getGlobalContext().getClientUrl();
  const ANO = new Date().getFullYear();
  const DT_INI = `${ANO}-01-01T00:00:00Z`;
  const DT_FIM = `${ANO}-12-31T23:59:59Z`;

  const DIRETORES = {
    "Aline Felix":        "06a1eeda-93d7-f011-8543-6045bd0a09fc",
    "Aline Sanzi":        "2d3010fa-61f4-ed11-8848-000d3a5a82bf",
    "Andressa Bueno":     "edbec271-d59d-ef11-8a6a-0022480985f3",
    "Carolina Brentzel":  "d49fdec3-f849-ef11-a317-000d3a5be4ff",
    "Daiane dos Santos":  "bd19844f-8b38-ee11-bdf4-6045bd095340",
    "Fabio Boturao":      "342e4168-9660-e911-a997-000d3a360ed5",
    "Felipe Porto":       "0f5c2d0c-d6d4-e911-a9a8-000d3a360ed5",
    "Gisele Tognolo":     "cb48e1a0-4959-ee11-be6f-000d3a317ead",
    "Jose Daniel Ramos":  "70a07063-6fdf-e311-8265-00155d00fe04",
    "Kamilla Rosa":       "b5ece3de-6c3c-ee11-bdf4-000d3a5a8e5c",
    "Marcia Mangiulli":   "8e616ea9-8d8a-f111-ab0f-70a8a5b0fc4c",
    "Regina Silveira":    "c336d752-e6fb-ed11-8849-000d3a5a8269",
    "Roana Reboredo":     "bea2794a-97c3-ef11-b8e9-000d3a3355b9",
    "Victoria Navarro":   "f41da072-58a6-ed11-aad1-000d3a5a8baa"
  };
  const guidToNome = Object.fromEntries(Object.entries(DIRETORES).map(([n,g])=>[g.toLowerCase(),n]));

  const TIPOS = ['phonecall','email','task','appointment'];
  const MIN_SUBST = 50;
  const resultado = {};
  for (const n of Object.keys(DIRETORES)) {
    resultado[n] = {
      total:0, substantivas:0,
      por_tipo:{phonecall:0,email:0,task:0,appointment:0},
      subst_por_tipo:{phonecall:0,email:0,task:0,appointment:0},
      por_trimestre:{Q1:0,Q2:0,Q3:0,Q4:0},
      por_mes:{}, pct_substantivas:0, media_dia:0, dias_c_atividade:new Set()
    };
  }

  function trimestre(mes) {
    const m = parseInt(mes);
    return m<=3?'Q1':m<=6?'Q2':m<=9?'Q3':'Q4';
  }

  for (const tipo of TIPOS) {
    console.log(`→ ${tipo}...`);
    let url = `${orgUrl}/api/data/v9.2/${tipo}s?$select=description,createdon,_ownerid_value&$filter=createdon ge ${DT_INI} and createdon le ${DT_FIM}&$top=5000`;
    let n = 0;
    while (url) {
      const resp = await fetch(url, {headers:{'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.include-annotations="*",odata.maxpagesize=5000'}});
      if (!resp.ok) { console.error(`erro ${tipo}:`, resp.status); break; }
      const d = await resp.json();
      for (const r of (d.value||[])) {
        const nome = guidToNome[(r._ownerid_value||'').toLowerCase()];
        if (!nome) continue;
        n++;
        const body = (r.description||'').trim();
        const subst = body.length >= MIN_SUBST;
        const dt = r.createdon||'';
        const mes = dt.substring(0,7);
        const dia = dt.substring(0,10);
        const trim = trimestre(dt.substring(5,7));
        const R = resultado[nome];
        R.total++; R.por_tipo[tipo]++;
        R.por_mes[mes] = (R.por_mes[mes]||0)+1;
        R.por_trimestre[trim]++;
        R.dias_c_atividade.add(dia);
        if (subst) { R.substantivas++; R.subst_por_tipo[tipo]++; }
      }
      url = d['@odata.nextLink']||null;
    }
    console.log(`  ${tipo}: ${n} dos 14 diretores`);
  }

  for (const n of Object.keys(resultado)) {
    const R = resultado[n];
    R.pct_substantivas = R.total>0 ? Math.round(100*R.substantivas/R.total) : 0;
    R.dias_c_atividade = R.dias_c_atividade.size;
    R.media_dia = R.dias_c_atividade>0 ? Math.round(R.total/R.dias_c_atividade*10)/10 : 0;
  }

  console.log(`\n════════ ATIVIDADES CRM ${ANO} ════════\n`);
  console.log(`${'DIRETOR'.padEnd(22)} ${'total'.padStart(5)} ${'subst'.padStart(5)} ${'%'.padStart(4)} ${'Q1'.padStart(5)} ${'Q2'.padStart(5)} ${'Q3'.padStart(5)} ${'Q4'.padStart(5)} ${'d/dia'.padStart(5)}`);
  console.log('─'.repeat(80));
  Object.keys(resultado).sort((a,b)=>resultado[b].total-resultado[a].total).forEach(n => {
    const R = resultado[n];
    console.log(`${n.padEnd(22)} ${String(R.total).padStart(5)} ${String(R.substantivas).padStart(5)} ${(R.pct_substantivas+'%').padStart(4)} ${String(R.por_trimestre.Q1).padStart(5)} ${String(R.por_trimestre.Q2).padStart(5)} ${String(R.por_trimestre.Q3).padStart(5)} ${String(R.por_trimestre.Q4).padStart(5)} ${String(R.media_dia).padStart(5)}`);
  });

  const out = {
    generatedAt:new Date().toISOString(), periodo:`${DT_INI} a ${DT_FIM}`,
    criterio_substantiva:`description >= ${MIN_SUBST} chars`, diretores:resultado
  };
  const blob = new Blob([JSON.stringify(out,null,2)],{type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `apw_activities_${new Date().toISOString().substring(0,10)}.json`;
  a.click();
  console.log(`\n✓ ${a.download}`);
})();
