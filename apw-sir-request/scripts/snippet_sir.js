/* ============================================================
   APW — Extração de dados para pedido de SIR (FCA Telecom)
   Rodar no console (F12) com a aba do Dynamics aberta e logada.
   Troque o L-number na linha do const L.
   Aceita 1 L ou vários: const L = ["L969223","L368344"];
   ============================================================ */
(async () => {
  const L = "L969223"; // <<< TROQUE AQUI (string ou array de strings)
  const LS = Array.isArray(L) ? L : [L];

  const base = location.origin + "/api/data/v9.2";
  const g = async u => {
    const r = await fetch(u, {
      credentials: "include",
      headers: {
        "Accept": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Prefer": 'odata.include-annotations="*"'
      }
    });
    if (!r.ok) throw new Error(r.status + " " + u);
    return r.json();
  };

  // campos que interessam pro SIR (match por nome, tolerante a custom fields)
  const KW = /address|endere|logrado|street|bairro|neighbor|cidade|municip|city|state|_uf|zip|cep|postal|lat|lon|coord|phone|telefone|celul|mobile|email|mail|carrier|operadora|tower|torre|property|tipo|type|site|contact|owner/i;
  const RX_TEL = /(\(?\d{2}\)?[\s.-]?9?\d{4}[-\s.]?\d{4})/g;
  const RX_MAIL = /[\w.+-]+@[\w-]+\.[\w.]{2,}/g;

  const out = [];

  for (const code of LS) {
    try {
      const q = await g(`${base}/opportunities?$filter=name eq '${code}'&$top=1`);
      const o = q.value[0];
      if (!o) { out.push({ L: code, erro: "opp não encontrada" }); continue; }
      const id = o.opportunityid;

      // 1) campos relevantes da opp
      const opp = {};
      Object.keys(o).forEach(k => {
        const v = o[k];
        if (v !== null && v !== "" && KW.test(k)) opp[k] = v;
      });

      // 2) contatos cadastrados
      const contatos = [];
      if (o._parentcontactid_value) {
        try {
          const c = await g(`${base}/contacts(${o._parentcontactid_value})?$select=fullname,telephone1,telephone2,mobilephone,emailaddress1,emailaddress2,modifiedon`);
          contatos.push({ origem: "contact", ...c });
        } catch (e) {}
      }
      if (o._parentaccountid_value) {
        try {
          const a = await g(`${base}/accounts(${o._parentaccountid_value})?$select=name,telephone1,telephone2,emailaddress1,modifiedon`);
          contatos.push({ origem: "account", ...a });
        } catch (e) {}
      }

      // 3) atividades — onde mora o telefone que realmente atende
      let contatos_atividades = [];
      try {
        const act = await g(`${base}/activitypointers?$filter=_regardingobjectid_value eq ${id}&$select=subject,description,createdon,activitytypecode&$orderby=createdon desc&$top=25`);
        act.value.forEach(a => {
          const txt = `${a.subject || ""} ${a.description || ""}`;
          const tels = [...new Set(txt.match(RX_TEL) || [])];
          const mails = [...new Set(txt.match(RX_MAIL) || [])];
          if (tels.length || mails.length) {
            contatos_atividades.push({
              data: (a.createdon || "").slice(0, 10),
              tipo: a.activitytypecode,
              tels, mails,
              trecho: txt.replace(/\s+/g, " ").slice(0, 220)
            });
          }
        });
      } catch (e) {}

      out.push({ L: code, opportunityid: id, opp, contatos, contatos_atividades });
    } catch (e) {
      out.push({ L: code, erro: String(e) });
    }
  }

  console.log("=== RESUMO ===");
  out.forEach(r => {
    console.log("\n### " + r.L, r.erro ? "ERRO: " + r.erro : "");
    if (r.opp) console.table(r.opp);
    if (r.contatos && r.contatos.length) console.table(r.contatos);
    if (r.contatos_atividades && r.contatos_atividades.length) {
      console.log("-- contatos nas atividades (mais recente primeiro) --");
      console.table(r.contatos_atividades);
    }
  });

  console.log("\n=== COPIE O JSON ABAIXO E COLE NO CLAUDE ===\n");
  console.log(JSON.stringify(out, null, 2));
  try { copy(JSON.stringify(out, null, 2)); console.log("(já copiado pro clipboard)"); } catch (e) {}
})();
