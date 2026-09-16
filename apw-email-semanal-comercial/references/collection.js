/* =====================================================================
   APW Brasil — coleta do e-mail semanal comercial (Dynamics 365 Web API)

   COMO USAR
   1. Aba do Chrome já autenticada em https://apwireless.crm.dynamics.com
   2. Colar este bloco inteiro no javascript_tool
   3. Ajustar ALVO se for fechar uma segunda passada (default = hoje)
   4. O retorno é o esqueleto do data.json — falta só o bloco financeiro
      do ano (adquirido / meta / pipeline / pct), que vem do Power BI.

   COMPLIANCE (apw-chrome-agent-lean-compliance)
   Tudo por Web API JSON. Proibido read_page / get_page_text / screenshot
   em domínio Dynamics. 401/403 → reabrir aba, 1 retry, depois parar.

   POR QUE DESCOBERTA EM RUNTIME
   Os nomes dos campos de data de estágio não são estáveis entre ambientes
   e nem seguem o padrão que se espera: `apwip_stage1date` NÃO EXISTE (o
   campo de Stage 1 é apwip_stage1_obtainedleaseeconomics), enquanto
   stage2..stage9 e stage100 existem. Stage 5 e Stage 8 nunca foram
   confirmados. Em vez de chutar e receber 400, o script lê o metadata da
   entidade e casa por regex. Se algum estágio não resolver, ele avisa em
   `_faltando` — daí você pergunta ao Lucas ou usa o print do Power BI
   para aquela coluna, em vez de entregar zero como se fosse fato.
   ===================================================================== */
(async () => {
  const API = "https://apwireless.crm.dynamics.com/api/data/v9.2";
  const H = {
    "Accept": "application/json",
    "OData-MaxVersion": "4.0",
    "OData-Version": "4.0",
    "Prefer": 'odata.include-annotations="OData.Community.Display.V1.FormattedValue"'
  };

  // ---------- janelas ----------
  const ALVO = null;                       // "2026-08-03" para fechar dia passado
  const hoje = ALVO ? new Date(ALVO + "T12:00:00") : new Date();
  const iso = d => d.toISOString().slice(0, 10);
  const menos = n => { const d = new Date(hoje); d.setDate(d.getDate() - n); return d; };

  const JAN = {
    semana: iso(menos(6)),                 // últimos 7 dias, igual ao recorte do Power BI
    mes:    iso(menos(30)),                // últimos 30 dias corridos, NÃO mês calendário
    ano:    hoje.getFullYear() + "-01-01"
  };
  const FIM = iso(hoje);

  // BR = UTC-3. Converte um UTC do CRM para a data local brasileira.
  const brDate = utc => {
    if (!utc) return null;
    const d = new Date(utc); d.setHours(d.getHours() - 3);
    return d.toISOString().slice(0, 10);
  };

  // ---------- fetch paginado ----------
  async function pg(url) {
    const out = []; let next = url, guard = 0;
    while (next && guard++ < 20) {
      const r = await fetch(next, { headers: H, credentials: "include" });
      if (!r.ok) throw new Error(r.status + " em " + next.slice(0, 120));
      const j = await r.json();
      out.push(...(j.value || []));
      next = j["@odata.nextLink"] || null;
    }
    return out;
  }

  // ---------- 1. descobrir os campos de data de estágio ----------
  const attrs = await pg(
    API + "/EntityDefinitions(LogicalName='opportunity')/Attributes" +
    "?$select=LogicalName,AttributeType" +
    "&$filter=startswith(LogicalName,'apwip_stage')"
  );
  const nomes = attrs
    .filter(a => /DateTime/i.test(a.AttributeType || ""))
    .map(a => a.LogicalName);

  // Padrões conhecidos primeiro; depois qualquer campo de data que cite o estágio.
  const acha = (n, prefer) => {
    for (const p of prefer) if (nomes.includes(p)) return p;
    return nomes.find(x => new RegExp("stage" + n + "(?!\\d)").test(x)) || null;
  };
  const F = {
    s1:  acha(1, ["apwip_stage1_obtainedleaseeconomics"]),
    s3:  acha(3, ["apwip_stage3date"]),
    s5:  acha(5, ["apwip_stage5date"]),
    s8:  acha(8, ["apwip_stage8date"]),
    s99: acha(99, ["apwip_stage99closedandfundeddeal", "apwip_stage99date"])
  };
  const faltando = Object.entries(F).filter(([, v]) => !v).map(([k]) => k);

  // ---------- 2. puxar as oportunidades de cada estágio ----------
  // Uma query por estágio, filtrando pelo campo de data desde o início do ano.
  // O recorte de semana/mês é feito em memória — evita 5x3 = 15 round-trips.
  const SEL = "apwip_opportunityautonumberid,name,_ownerid_value," +
              "_apwip_stage1owner_value,_apwip_stage3owner_value";

  const bruto = {};
  for (const [k, campo] of Object.entries(F)) {
    if (!campo) { bruto[k] = []; continue; }
    bruto[k] = await pg(
      API + "/opportunities?$select=" + SEL + "," + campo +
      "&$filter=" + campo + " ge " + JAN.ano + "T00:00:00Z and " +
      campo + " le " + FIM + "T23:59:59Z"
    );
  }

  // ---------- 3. owner efetivo ----------
  // Se o owner é pool/system, o dono real do movimento está no campo de owner
  // do estágio. Sem isso, movimentos verdadeiros de diretor caem em "pool".
  const POOL = /pool|system|admin|integra|crm|queue/i;
  const eff = (r, k) => {
    const nome = r["_ownerid_value@OData.Community.Display.V1.FormattedValue"];
    if (nome && !POOL.test(nome)) return nome;
    const alt = k === "s1" ? "_apwip_stage1owner_value"
              : k === "s3" ? "_apwip_stage3owner_value" : null;
    const an = alt && r[alt + "@OData.Community.Display.V1.FormattedValue"];
    return an || nome || "(pool)";
  };

  // ---------- 4. agregar ----------
  const D = {};                              // nome -> {semana:{}, mes:{}, ano:{}}
  const zero = () => ({ s1: 0, s3: 0, s5: 0, s8: 0, s99: 0 });
  const put = (nome, jan, k) => {
    D[nome] = D[nome] || { semana: zero(), mes: zero(), ano: zero() };
    D[nome][jan][k]++;
  };
  const tot = { semana: zero(), mes: zero(), ano: zero() };
  const ls = { semana: {}, mes: {} };         // L-numbers movidos, pra conferência

  for (const [k, campo] of Object.entries(F)) {
    if (!campo) continue;
    for (const r of bruto[k]) {
      const dia = brDate(r[campo]);
      if (!dia || dia > FIM) continue;
      const nome = eff(r, k);
      const L = r.apwip_opportunityautonumberid;
      const jans = ["ano"];
      if (dia >= JAN.mes) jans.push("mes");
      if (dia >= JAN.semana) jans.push("semana");
      for (const j of jans) {
        put(nome, j, k); tot[j][k]++;
        if (j !== "ano") { (ls[j][k] = ls[j][k] || []).push(L); }
      }
    }
  }

  // ---------- 5. montar o esqueleto do data.json ----------
  const fmtJan = (de, ate) => {
    const p = s => s.slice(8, 10) + "/" + s.slice(5, 7) + "/" + s.slice(0, 4);
    return p(de).slice(0, 5) + " – " + p(ate);
  };
  const diretores = Object.entries(D)
    .filter(([n]) => !POOL.test(n))
    .map(([nome, v]) => ({
      nome,
      semana: { s1: v.semana.s1, s3: v.semana.s3, s5: v.semana.s5, s99: v.semana.s99 },
      mes: v.mes,
      // adquirido e pct vêm do Power BI — deixados null de propósito
      ano: { deals: v.ano.s99, adquirido: null, pct: null }
    }))
    .sort((a, b) => b.ano.deals - a.ano.deals || a.nome.localeCompare(b.nome));

  const out = {
    referencia: FIM.slice(8, 10) + "/" + FIM.slice(5, 7) + "/" + FIM.slice(0, 4),
    janelas: {
      semana: fmtJan(JAN.semana, FIM),
      mes: fmtJan(JAN.mes, FIM),
      ano: fmtJan(JAN.ano, FIM)
    },
    meta_ano_deals: 100,
    n_diretores: diretores.length,
    meses_restantes: 12 - (hoje.getMonth() + 1) + 1,
    hot_deals: null,                        // Power BI / view de pipeline
    totais: {
      semana: { s1: tot.semana.s1, s3: tot.semana.s3, s5: tot.semana.s5,
                s8: tot.semana.s8, s99: tot.semana.s99 },
      mes: tot.mes,
      ano: { deals: tot.ano.s99, leases: tot.ano.s99,
             adquirido: null, meta: null, pipeline: null, pct: null }
    },
    diretores,
    obs: "",
    _campos_usados: F,
    _faltando: faltando,
    _l_numbers: ls
  };

  console.log(JSON.stringify(out, null, 2));
  if (faltando.length) {
    console.warn("ATENÇÃO: sem campo de data para " + faltando.join(", ") +
                 " — preencher pelo Power BI, NÃO deixar zero.");
  }
  return out;
})();
