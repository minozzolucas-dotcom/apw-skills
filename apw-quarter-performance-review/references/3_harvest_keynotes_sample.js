// ═══════════════════════════════════════════════════════════════
// APW · HARVEST 3/3 · Amostra Key Notes por diretor
// Puxa os ÚLTIMOS 10 Key Notes de cada diretor pra avaliar qualidade
// Mede: comprimento médio, tem outline estruturado?, menciona S99 road?
// ~30-60s pra rodar
// ═══════════════════════════════════════════════════════════════
(async () => {
  const BR = 'FEA663A6-5B28-E211-BCD6-00155D00D805';
  const orgUrl = Xrm.Utility.getGlobalContext().getClientUrl();
  const ANO = new Date().getFullYear();

  const DIRETORES = {
    "Aline Felix":"06a1eeda-93d7-f011-8543-6045bd0a09fc",
    "Aline Sanzi":"2d3010fa-61f4-ed11-8848-000d3a5a82bf",
    "Andressa Bueno":"edbec271-d59d-ef11-8a6a-0022480985f3",
    "Carolina Brentzel":"d49fdec3-f849-ef11-a317-000d3a5be4ff",
    "Daiane dos Santos":"bd19844f-8b38-ee11-bdf4-6045bd095340",
    "Fabio Boturao":"342e4168-9660-e911-a997-000d3a360ed5",
    "Felipe Porto":"0f5c2d0c-d6d4-e911-a9a8-000d3a360ed5",
    "Gisele Tognolo":"cb48e1a0-4959-ee11-be6f-000d3a317ead",
    "Jose Daniel Ramos":"70a07063-6fdf-e311-8265-00155d00fe04",
    "Kamilla Rosa":"b5ece3de-6c3c-ee11-bdf4-000d3a5a8e5c",
    "Marcia Mangiulli":"8e616ea9-8d8a-f111-ab0f-70a8a5b0fc4c",
    "Regina Silveira":"c336d752-e6fb-ed11-8849-000d3a5a8269",
    "Roana Reboredo":"bea2794a-97c3-ef11-b8e9-000d3a3355b9",
    "Victoria Navarro":"f41da072-58a6-ed11-aad1-000d3a5a8baa"
  };

  // tentar descobrir campo Key Notes (pode ser apwip_keynotes, apwip_investmentopportunity, apwip_notes)
  const CANDIDATOS = ['apwip_keynotes','apwip_investmentopportunity','apwip_notes','apwip_investmentkeynotes'];
  let NOTES_FIELD = null;
  for (const f of CANDIDATOS) {
    try {
      const r = await fetch(`${orgUrl}/api/data/v9.2/opportunities?$select=${f}&$top=1`,
        {headers:{'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}});
      if (r.ok) { NOTES_FIELD = f; break; }
    } catch(e) {}
  }
  if (!NOTES_FIELD) {
    console.error('✗ campo Key Notes não encontrado. Candidatos:', CANDIDATOS);
    console.error('  → abre uma opp no CRM, inspeciona campo Investment Opportunity / Key Notes, me manda o nome');
    return;
  }
  console.log(`✓ Campo Key Notes: ${NOTES_FIELD}`);

  const resultado = {};
  for (const [nome, guid] of Object.entries(DIRETORES)) {
    console.log(`→ ${nome}...`);
    // puxa últimas 10 opps com key notes preenchido do diretor em 2026
    const fx = `<fetch top="10">
      <entity name="opportunity">
        <attribute name="apwip_opportunityautonumberid"/>
        <attribute name="name"/>
        <attribute name="${NOTES_FIELD}"/>
        <attribute name="apwip_stage3date"/>
        <attribute name="apwip_stage8_date"/>
        <attribute name="modifiedon"/>
        <filter>
          <condition attribute="apwip_countryfilter" operator="eq" value="{${BR}}"/>
          <condition attribute="ownerid" operator="eq" value="${guid}"/>
          <condition attribute="${NOTES_FIELD}" operator="not-null"/>
          <condition attribute="modifiedon" operator="on-or-after" value="${ANO}-01-01"/>
        </filter>
        <order attribute="modifiedon" descending="true"/>
      </entity>
    </fetch>`.replace(/\s+/g,' ').trim();

    const resp = await fetch(`${orgUrl}/api/data/v9.2/opportunities?fetchXml=${encodeURIComponent(fx)}`,
      {headers:{'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}});
    if (!resp.ok) { resultado[nome] = {erro: resp.status}; continue; }
    const data = await resp.json();
    const amostras = (data.value||[]).map(o => ({
      L: o.apwip_opportunityautonumberid,
      nome_opp: o.name,
      dt_mod: (o.modifiedon||'').substring(0,10),
      dt_s3: (o.apwip_stage3date||'').substring(0,10)||null,
      dt_s8: (o.apwip_stage8_date||'').substring(0,10)||null,
      keynotes_raw: o[NOTES_FIELD] || '',
      keynotes_len: (o[NOTES_FIELD] || '').replace(/<[^>]*>/g,'').trim().length,
      tem_estrutura: /\b(Lease|Rent|Owner|Carrier|Tower|Site|Deal|Structure|Pricing|Risk|History)\b/i.test(o[NOTES_FIELD]||'')
    }));
    const total_len = amostras.reduce((s,a)=>s+a.keynotes_len, 0);
    const n = amostras.length;
    resultado[nome] = {
      n_amostras: n,
      len_media: n>0 ? Math.round(total_len/n) : 0,
      len_min: n>0 ? Math.min(...amostras.map(a=>a.keynotes_len)) : 0,
      len_max: n>0 ? Math.max(...amostras.map(a=>a.keynotes_len)) : 0,
      pct_estruturados: n>0 ? Math.round(100*amostras.filter(a=>a.tem_estrutura).length/n) : 0,
      amostras: amostras
    };
  }

  console.log(`\n════════ KEY NOTES QUALITY SAMPLE ${ANO} ════════\n`);
  console.log(`${'DIRETOR'.padEnd(22)} ${'n'.padStart(3)} ${'len_med'.padStart(8)} ${'len_min'.padStart(8)} ${'len_max'.padStart(8)} ${'% estrut'.padStart(10)}`);
  console.log('─'.repeat(70));
  Object.keys(resultado).forEach(n => {
    const R = resultado[n];
    if (R.erro) { console.log(`${n.padEnd(22)} erro ${R.erro}`); return; }
    console.log(`${n.padEnd(22)} ${String(R.n_amostras).padStart(3)} ${String(R.len_media).padStart(8)} ${String(R.len_min).padStart(8)} ${String(R.len_max).padStart(8)} ${(R.pct_estruturados+'%').padStart(10)}`);
  });

  const out = {
    generatedAt:new Date().toISOString(), campo:NOTES_FIELD, ano:ANO,
    criterio_estrutura:'contem palavras-chave: Lease|Rent|Owner|Carrier|Tower|Site|Deal|Structure|Pricing|Risk|History',
    diretores:resultado
  };
  const blob = new Blob([JSON.stringify(out,null,2)],{type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `apw_keynotes_sample_${new Date().toISOString().substring(0,10)}.json`;
  a.click();
  console.log(`\n✓ ${a.download}`);
})();
