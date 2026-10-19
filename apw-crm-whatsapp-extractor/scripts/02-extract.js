// APW CRM → WhatsApp Extractor | Versão completa
// Output: CSV com code, name, contact, email, best_phone, is_mobile, all_mobiles,
// all_phones, multi_source_flag, opportunityId, leadId.
//
// Ajuste VIEW (viewid da URL do Dynamics) e, se quiser teste, LIMITE.

(async () => {
  const VIEW = "572e1df3-7198-eb11-b1ac-000d3a32d0bd"; // ← ajustar
  const LIMITE = null; // null = tudo; número = $top=N
  const LEAD_SEL = [
    "leadid", "fullname", "emailaddress1",
    "mobilephone", "telephone1", "telephone2", "telephone3",
    "new_currentownermobilephonenumber", "new_currentownerphonenumber"
  ].join(",");

  // 1) Lista opps da view (paginando)
  const topClause = LIMITE ? `&$top=${LIMITE}` : "";
  let opps = [], next = `?userQuery=${VIEW}${topClause}&$select=opportunityid,name,_apwip_leadopportunityid_value,_originatingleadid_value&$count=true`;
  do {
    const r = await Xrm.WebApi.retrieveMultipleRecords("opportunity", next, 500);
    opps = opps.concat(r.entities);
    next = (!LIMITE && r.nextLink) ? r.nextLink.split("/opportunities")[1] : null;
  } while (next);
  console.log(`📋 ${opps.length} opps na view`);

  // 2) Helpers
  const splitNumbers = raw => {
    if (!raw) return [];
    return String(raw)
      .split(/[\/;,]|\s-\s|\be\b/i)
      .map(s => s.replace(/\(.*?\)/g, "").trim())
      .filter(Boolean);
  };
  const toE164 = raw => {
    const d = String(raw || "").replace(/\D/g, "");
    if (!d || d.length < 10) return "";
    if (d.startsWith("55") && d.length >= 12) return "+" + d;
    if (d.length === 10 || d.length === 11) return "+55" + d;
    return "+" + d;
  };
  const isMobileBR = e164 => {
    const m = e164.match(/^\+55(\d{2})(\d{8,9})$/);
    return m && m[2].length === 9 && m[2].startsWith("9");
  };

  // 3) Pra cada opp: puxa lead + extrai todos os telefones
  const rows = [], skipped = [];
  for (let i = 0; i < opps.length; i++) {
    const o = opps[i];
    const leadId = o._apwip_leadopportunityid_value || o._originatingleadid_value;
    if (!leadId) { skipped.push({ id: o.opportunityid, name: o.name, reason: "sem lead" }); continue; }

    try {
      const l = await Xrm.WebApi.retrieveRecord("lead", leadId, `?$select=${LEAD_SEL}`);
      const code = (o.name || "").match(/L\d{5,}/)?.[0] || "";

      const sources = [
        ["mobilephone", l.mobilephone],
        ["telephone1", l.telephone1],
        ["telephone2", l.telephone2],
        ["telephone3", l.telephone3],
        ["new_currentownermobilephonenumber", l.new_currentownermobilephonenumber],
        ["new_currentownerphonenumber", l.new_currentownerphonenumber]
      ];

      const seen = new Set();
      const phones = [];
      for (const [src, raw] of sources) {
        for (const part of splitNumbers(raw)) {
          const e164 = toE164(part);
          if (!e164 || seen.has(e164)) continue;
          seen.add(e164);
          phones.push({ src, raw: part, e164, mobile: isMobileBR(e164) });
        }
      }

      const mobiles = phones.filter(p => p.mobile);
      const best = mobiles[0] || phones[0] || {};

      rows.push({
        code,
        name: o.name || "",
        contact: l.fullname || "",
        email: l.emailaddress1 || "",
        best_phone: best.e164 || "",
        best_source: best.src || "",
        is_mobile: best.mobile ? "SIM" : (best.e164 ? "fixo" : ""),
        all_mobiles: mobiles.map(p => p.e164).join(" | "),
        all_phones: phones.map(p => p.e164).join(" | "),
        multi_source_flag: phones.length > 1 ? "revisar" : "",
        opportunityId: o.opportunityid,
        leadId
      });
    } catch (e) {
      skipped.push({ id: o.opportunityid, name: o.name, reason: e.message });
    }
    if ((i + 1) % 25 === 0) console.log(`${i + 1}/${opps.length}...`);
  }

  // 4) CSV + clipboard
  const esc = v => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const header = ["code", "name", "contact", "email", "best_phone", "best_source", "is_mobile", "all_mobiles", "all_phones", "multi_source_flag", "opportunityId", "leadId"];
  const csv = [header.join(","), ...rows.map(r => header.map(h => esc(r[h])).join(","))].join("\n");

  await navigator.clipboard.writeText(csv);
  const comMobile = rows.filter(r => r.is_mobile === "SIM").length;
  console.log(`\n✅ CSV no clipboard`);
  console.log(`   Total: ${rows.length} | com celular: ${comMobile} | só fixo: ${rows.filter(r => r.is_mobile === "fixo").length} | sem nada: ${rows.filter(r => !r.best_phone).length} | pulados: ${skipped.length}`);
  console.table(rows.slice(0, 10));
  if (skipped.length) { console.log("Pulados:"); console.table(skipped.slice(0, 20)); }
  window.__apwExport = { rows, csv, skipped };
})();
