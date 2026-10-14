// ═══════════════════════════════════════════════════════════════
// APW · HARVEST 1/3 · Rent Acquired YTD por diretor
// Rodar em aba autenticada do Dynamics 365 (apwbrasil.crm2.dynamics.com)
// F12 → Console → cola tudo → Enter → aguarda ~10-20s → baixa JSON
// ═══════════════════════════════════════════════════════════════
(async () => {
  const BR = 'FEA663A6-5B28-E211-BCD6-00155D00D805';
  const orgUrl = Xrm.Utility.getGlobalContext().getClientUrl();
  const ANO = new Date().getFullYear();

  // ─── 1. descobrir qual campo de rent existe neste tenant ───
  const CANDIDATOS = [
    'apwip_annualrentbrl',
    'apwip_annualrent',
    'apwip_newrentbrl',
    'apwip_newrentannualbrl',
    'apwip_rentacquired',
    'apwip_annualrentbr',
    'apwip_rentannualbrl'
  ];
  let RENT_FIELD = null;
  for (const f of CANDIDATOS) {
    try {
      const r = await fetch(`${orgUrl}/api/data/v9.2/opportunities?$select=${f}&$top=1`,
        {headers:{'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}});
      if (r.ok) { RENT_FIELD = f; break; }
    } catch(e) {}
  }
  if (!RENT_FIELD) {
    console.error('✗ Nenhum campo de rent encontrado. Candidatos testados:', CANDIDATOS);
    console.error('  → Abra uma opp S99 no CRM, inspecione os campos de valor, me passe o nome real.');
    return;
  }
  console.log(`✓ Campo de rent detectado: ${RENT_FIELD}`);

  // ─── 2. puxar todas S99 do ano com rent + owner ───
  const fx = `<fetch>
    <entity name="opportunity">
      <attribute name="apwip_opportunityautonumberid"/>
      <attribute name="name"/>
      <attribute name="apwip_stage99_date"/>
      <attribute name="apwip_stage8_date"/>
      <attribute name="_apwip_stage99owner_value"/>
      <attribute name="_apwip_stage8owner_value"/>
      <attribute name="_apwip_carrier_value"/>
      <attribute name="_apwip_towerco_value"/>
      <attribute name="${RENT_FIELD}"/>
      <attribute name="statuscode"/>
      <filter>
        <condition attribute="apwip_countryfilter" operator="eq" value="{${BR}}"/>
        <condition attribute="apwip_stage99_date" operator="on-or-after" value="${ANO}-01-01"/>
        <condition attribute="apwip_stage99_date" operator="on-or-before" value="${ANO}-12-31"/>
      </filter>
      <order attribute="apwip_stage99_date" descending="false"/>
    </entity>
  </fetch>`.replace(/\s+/g,' ').trim();

  const resp = await fetch(`${orgUrl}/api/data/v9.2/opportunities?fetchXml=${encodeURIComponent(fx)}`,
    {headers:{'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0',
              'Prefer':'odata.include-annotations="*"'}});
  if (!resp.ok) { console.error('Erro:', resp.status, await resp.text()); return; }
  const data = await resp.json();
  const rows = data.value || [];

  // ─── 3. agrupar por owner s99 + por mês ───
  const porOwner = {};
  rows.forEach(o => {
    const nome = o['_apwip_stage99owner_value@OData.Community.Display.V1.FormattedValue'] || '(sem owner s99)';
    const rent = Number(o[RENT_FIELD]) || 0;
    const dt = (o.apwip_stage99_date||'').substring(0,10);
    const mes = dt.substring(0,7);
    if (!porOwner[nome]) porOwner[nome] = { total_rent: 0, n_deals: 0, por_mes: {}, deals: [] };
    porOwner[nome].total_rent += rent;
    porOwner[nome].n_deals += 1;
    porOwner[nome].por_mes[mes] = (porOwner[nome].por_mes[mes]||0) + rent;
    porOwner[nome].deals.push({
      L: o.apwip_opportunityautonumberid,
      nome: o.name,
      dt_s99: dt,
      dt_s8: (o.apwip_stage8_date||'').substring(0,10) || null,
      rent: rent,
      carrier: o['_apwip_carrier_value@OData.Community.Display.V1.FormattedValue'] || null,
      towerco: o['_apwip_towerco_value@OData.Community.Display.V1.FormattedValue'] || null,
      status: o['statuscode@OData.Community.Display.V1.FormattedValue'] || null
    });
  });

  // ─── 4. console log formatado ───
  console.log(`\n════════ RENT ACQUIRED YTD ${ANO} (${rows.length} deals em S99) ════════\n`);
  Object.keys(porOwner).sort((a,b)=>porOwner[b].total_rent - porOwner[a].total_rent).forEach(n => {
    const p = porOwner[n];
    console.log(`${n}: R$ ${p.total_rent.toLocaleString('pt-BR',{minimumFractionDigits:0})} (${p.n_deals} deals)`);
  });

  // ─── 5. baixar JSON ───
  const out = {
    generatedAt: new Date().toISOString(),
    campo_rent: RENT_FIELD,
    ano: ANO,
    total_deals: rows.length,
    total_rent_geral: rows.reduce((s,o)=>s+(Number(o[RENT_FIELD])||0), 0),
    porOwner: porOwner
  };
  const blob = new Blob([JSON.stringify(out, null, 2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `apw_rent_acquired_${new Date().toISOString().substring(0,10)}.json`;
  a.click();
  console.log(`\n✓ Baixado: ${a.download}`);
})();
