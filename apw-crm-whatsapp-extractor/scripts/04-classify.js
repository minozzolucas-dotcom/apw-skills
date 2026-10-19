// APW CRM → WhatsApp Extractor | PARTE 2: Classificação por stage/status/owner
// Roda no console do Dynamics DEPOIS do extract (02-extract.js ou 03-minimal.js).
// Objetivo: identificar opps com DIRETOR ESPECÍFICO como owner (não Pool) → remover do batch.
//
// Como usar:
// 1. Preenche o array CODES com os códigos L extraídos (vem do CSV do extract)
// 2. Cola no console do Dynamics (qualquer view aberta)
// 3. Analisa os 3 console.table de output
// 4. Remove opps com owner=diretor específico ou owner=próprio Lucas do batch

(async () => {
  // ⚠️ Preencher com os códigos L do extract atual
  const CODES = [
    // "L1107858","L1067923",...
  ];

  if (CODES.length === 0) {
    console.error("❌ Preencha o array CODES com os códigos L do extract antes de rodar.");
    return;
  }

  const filter = CODES.map(c => `contains(name,'${c}')`).join(" or ");
  const r = await Xrm.WebApi.retrieveMultipleRecords(
    "opportunity",
    `?$select=opportunityid,name,apwip_opportunitystage,statuscode,statecode,apwip_mostrecentstagedate,_ownerid_value&$filter=(${filter})&$top=500`
  );

  const rows = r.entities.map(o => ({
    code: (o.name || "").match(/L\d{5,}/)?.[0] || "?",
    stage: o["apwip_opportunitystage@OData.Community.Display.V1.FormattedValue"] || "(sem)",
    status: o["statuscode@OData.Community.Display.V1.FormattedValue"] || "(sem)",
    state: o["statecode@OData.Community.Display.V1.FormattedValue"] || "(sem)",
    ultimomov: o["apwip_mostrecentstagedate@OData.Community.Display.V1.FormattedValue"] || "(sem)",
    owner: o["_ownerid_value@OData.Community.Display.V1.FormattedValue"] || "(sem)"
  }));

  // 1. Distribuição stage × status
  const grupo = {};
  rows.forEach(r => {
    const key = `${r.stage} / ${r.status}`;
    grupo[key] = (grupo[key] || 0) + 1;
  });
  console.log(`\n📊 Distribuição stage × status (${rows.length} opps):`);
  console.table(grupo);

  // 2. Owner distribution
  const porOwner = {};
  rows.forEach(r => {
    porOwner[r.owner] = (porOwner[r.owner] || 0) + 1;
  });
  console.log(`\n👤 Owner atual das opps:`);
  console.table(porOwner);

  // 3. Opps com RISCO POLÍTICO (owner = diretor específico, não Pool)
  const POOLS_SEGUROS = ["Surrendered Pool", "Purged Pool", "Lead Pool", "(sem)"];
  const risco = rows.filter(r =>
    !POOLS_SEGUROS.includes(r.owner) &&
    r.owner !== "Lucas Minozzo" // próprio Lucas = separado
  );
  console.log(`\n⚠️ RISCO POLÍTICO — opps com diretor específico (${risco.length}):`);
  if (risco.length) {
    console.table(risco);
    console.log("👉 REMOVER esses códigos do batch de disparo.");
  } else {
    console.log("✅ Zero opps com diretor específico. Pode disparar.");
  }

  // 4. Opps do próprio Lucas (tratar manualmente)
  const proprias = rows.filter(r => r.owner === "Lucas Minozzo");
  if (proprias.length) {
    console.log(`\n🔸 Opps do próprio Lucas (${proprias.length}) — tratar manualmente, não disparo frio:`);
    console.table(proprias);
  }

  // CSV detalhado pro clipboard (todas as classificações)
  const esc = v => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const header = ["code", "stage", "status", "state", "ultimomov", "owner", "flag"];
  const classif = rows.map(r => {
    let flag = "OK";
    if (!POOLS_SEGUROS.includes(r.owner) && r.owner !== "Lucas Minozzo") flag = "RISCO POLITICO";
    else if (r.owner === "Lucas Minozzo") flag = "OPP PROPRIA";
    return { ...r, flag };
  });
  const csv = [
    header.join(","),
    ...classif.map(r => header.map(h => esc(r[h])).join(","))
  ].join("\n");

  try {
    await navigator.clipboard.writeText(csv);
    console.log(`\n✅ CSV detalhado (${rows.length} linhas) copiado pro clipboard`);
  } catch (e) {
    console.log(`\n⚠️ Clipboard bloqueado. CSV disponível em window.__apwClassCSV`);
  }

  window.__apwClass = classif;
  window.__apwClassCSV = csv;
  console.log("\nDetalhe em window.__apwClass | CSV em window.__apwClassCSV");
})();
