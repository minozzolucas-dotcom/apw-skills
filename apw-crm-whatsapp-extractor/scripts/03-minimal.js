// APW CRM → WhatsApp Extractor | Versão minimalista
// Output: CSV só com code,phone — celular BR válido (11 dígitos, começa com 9).
// Ajuste VIEW e LIMITE conforme necessário.

(async () => {
  const VIEW = "572e1df3-7198-eb11-b1ac-000d3a32d0bd"; // ← ajustar
  const LIMITE = 200; // amostra; null = tudo

  const topClause = LIMITE ? `&$top=${LIMITE}` : "";
  let opps = [], next = `?userQuery=${VIEW}${topClause}&$select=opportunityid,name,_apwip_leadopportunityid_value,_originatingleadid_value`;
  do {
    const r = await Xrm.WebApi.retrieveMultipleRecords("opportunity", next, 500);
    opps = opps.concat(r.entities);
    next = (!LIMITE && r.nextLink) ? r.nextLink.split("/opportunities")[1] : null;
  } while (next);
  console.log(`${opps.length} opps`);

  const toMobile = raw => {
    const d = String(raw || "").replace(/\D/g, "");
    const n = d.startsWith("55") ? d.slice(2) : d;
    if (n.length !== 11 || n[2] !== "9") return "";
    return "+55" + n;
  };

  const rows = [];
  for (let i = 0; i < opps.length; i++) {
    const o = opps[i];
    const leadId = o._apwip_leadopportunityid_value || o._originatingleadid_value;
    if (!leadId) continue;
    try {
      const l = await Xrm.WebApi.retrieveRecord("lead", leadId,
        "?$select=mobilephone,telephone1,telephone2,telephone3");
      let cel = "";
      for (const raw of [l.mobilephone, l.telephone1, l.telephone2, l.telephone3]) {
        for (const part of String(raw || "").split(/[\/;,]/)) {
          cel = toMobile(part);
          if (cel) break;
        }
        if (cel) break;
      }
      if (!cel) continue;
      rows.push({
        code: (o.name || "").match(/L\d{5,}/)?.[0] || "",
        phone: cel
      });
    } catch (e) { }
    if ((i + 1) % 25 === 0) console.log(`${i + 1}/${opps.length}...`);
  }

  const csv = "code,phone\n" + rows.map(r => `${r.code},${r.phone}`).join("\n");
  await navigator.clipboard.writeText(csv);
  console.log(`✅ ${rows.length} celulares no clipboard (de ${opps.length} opps lidos)`);
  console.table(rows.slice(0, 10));
  window.__apw = rows;
})();
