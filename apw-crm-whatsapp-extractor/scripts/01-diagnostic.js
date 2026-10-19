// APW CRM → WhatsApp Extractor | Diagnóstico
// Roda no console do Dynamics 365 com a view-alvo aberta.
// Confirma: (1) userQuery vs savedQuery, (2) campos de telefone preenchidos no lead.

(async () => {
  const VIEW = "572e1df3-7198-eb11-b1ac-000d3a32d0bd"; // ← ajustar
  const HOT = [
    "mobilephone",
    "new_whatsapp",
    "telephone1", "telephone2", "telephone3",
    "new_currentownermobilephonenumber",
    "new_currentownerphonenumber",
    "apwip_ownerphonenumber",
    "apwip_marketingcampaignphonenumber",
    "address1_telephone1", "address2_telephone1"
  ];

  // 1) Qual tipo de view?
  let kind, opps;
  for (const k of ["userQuery", "savedQuery"]) {
    try {
      const r = await Xrm.WebApi.retrieveMultipleRecords(
        "opportunity",
        `?${k}=${VIEW}&$top=10&$select=opportunityid,name,_apwip_leadopportunityid_value,_originatingleadid_value`
      );
      console.log(`✅ ${k}: ${r.entities.length} opps`);
      kind = k; opps = r.entities; break;
    } catch (e) {
      console.warn(`❌ ${k}: ${e.message}`);
    }
  }
  if (!opps) return console.error("Nenhum tipo de view funcionou");

  // 2) Qual preenchimento de cada campo quente?
  const matrix = [];
  for (const o of opps) {
    const leadId = o._apwip_leadopportunityid_value || o._originatingleadid_value;
    if (!leadId) continue;
    try {
      const lead = await Xrm.WebApi.retrieveRecord(
        "lead", leadId, `?$select=${HOT.join(",")}`
      );
      const row = { opp: (o.name || "").slice(0, 40) };
      HOT.forEach(f => row[f] = lead[f] || "");
      matrix.push(row);
    } catch (e) { console.warn(o.name, e.message); }
  }

  console.table(matrix);

  const fill = {};
  HOT.forEach(f => fill[f] = matrix.filter(r => r[f]).length);
  console.log(`\n📊 Preenchimento por campo (de ${matrix.length}):`);
  console.table(fill);
  console.log(`\n✅ Diagnóstico pronto. Tipo de view: ${kind}. Dados em window.__apwDiag.`);
  window.__apwDiag = { kind, matrix, fill };
})();
