/* ═══════════════════════════════════════════════════════════════════════
   SNIPPET 2/2 — CALOR DO DIA (reporte interno de gestão · APW)
   Data-alvo FIXADA: 2026-08-18 (terça)
   13 diretores (Bruna Matos removida)

   NOTA: a pasta references/ da skill apw-calor-do-dia está VAZIA no
   ambiente — este collect foi reconstruído a partir da especificação
   do SKILL.md. Rode DEPOIS do snippet 1.

   COMO RODAR:
   1. Mesma aba logada em https://apwireless.crm.dynamics.com
   2. F12 → Console → cole TUDO → Enter
   3. Vai baixar: calor_2026-08-18.json
   4. Me mande esse arquivo no chat
   ═══════════════════════════════════════════════════════════════════════ */
(async () => {
  const ALVO_IN = ""; // "" = hoje; "YYYY-MM-DD" p/ retroativo
  const _H=(ALVO_IN||new Date(new Date().getTime()-3*3600*1000).toISOString().slice(0,10));
  const D0     = _H+"T03:00:00Z";
  const D1     = new Date(new Date(_H+"T03:00:00Z").getTime()+24*3600*1000).toISOString();
  const SEMINI = _H;

  const base = location.origin + "/api/data/v9.2";
  const FV = "OData.Community.Display.V1.FormattedValue";
  const h  = { "Accept":"application/json","OData-MaxVersion":"4.0","OData-Version":"4.0",
    "Prefer":'odata.maxpagesize=5000,odata.include-annotations="'+FV+'"' };
  const hA = { "Accept":"application/json","OData-MaxVersion":"4.0","OData-Version":"4.0",
    "Prefer":'odata.maxpagesize=5000,odata.include-annotations="'+FV+'"' };
  const VIEW = { stage1:"a020dfbe-4a3f-f111-88b4-00224805b156", stage3:"50aca927-4b3f-f111-88b4-00224805b156", pricing:"e85d5310-8c42-f111-88b4-6045bd07461c" };

  const NM={
    "70a07063-6fdf-e311-8265-00155d00fe04":"Jose Daniel Ramos",
    "c336d752-e6fb-ed11-8849-000d3a5a8269":"Regina Silveira",
    "b5ece3de-6c3c-ee11-bdf4-000d3a5a8e5c":"Kamilla Rosa",
    "0f5c2d0c-d6d4-e911-a9a8-000d3a360ed5":"Felipe Porto",
    "342e4168-9660-e911-a997-000d3a360ed5":"Fabio Boturao",
    "2d3010fa-61f4-ed11-8848-000d3a5a82bf":"Aline Sanzi",
    "f41da072-58a6-ed11-aad1-000d3a5a8baa":"Victoria Navarro",
    "bd19844f-8b38-ee11-bdf4-6045bd095340":"Daiane dos Santos",
    "cb48e1a0-4959-ee11-be6f-000d3a317ead":"Gisele Tognolo",
    "edbec271-d59d-ef11-8a6a-0022480985f3":"Andressa Bueno",
    "bea2794a-97c3-ef11-b8e9-000d3a3355b9":"Roana Reboredo",
    "d49fdec3-f849-ef11-a317-000d3a5be4ff":"Carolina Brentzel",
    "06a1eeda-93d7-f011-8543-6045bd0a09fc":"Aline Felix"
  };
  const DIR=Object.keys(NM);
  const isDir=g=>DIR.includes((g||"").toLowerCase());
  const norm=v=>(v||"").toString().toLowerCase().replace(/[{}]/g,"");
  const POOL=/pool|apwreports|surrender|disqualified|system/i;
  const brDate=iso=>iso?new Date(new Date(iso).getTime()-3*3600*1000).toISOString().slice(0,10):"";

  async function pg(u,hh){let o=[],n=u,g=0;while(n&&g<40){const r=await fetch(n,{headers:hh,credentials:"include"});if(r.status===401||r.status===403)throw new Error("AUTH_"+r.status+" — reabra a aba logada");if(!r.ok)throw new Error("HTTP_"+r.status+" @ "+n.slice(0,120));const j=await r.json();o=o.concat(j.value||[]);n=j["@odata.nextLink"]||null;g++;}return o;}
  function eff(r,sof){const nm=r["_ownerid_value@"+FV]||"";if(POOL.test(nm)&&r[sof])return r[sof];return r._ownerid_value;}

  const out={alvo:_H,deals:[],acts_dia:[],_meta:{}};
  const dealMap={};   // oppGuid -> deal
  function upsert(guid,o,tipo,ownerGuid,ownerNome,pool){
    const k=norm(guid); if(!k)return;
    if(!dealMap[k]) dealMap[k]={opp:k,L:o.apwip_opportunityautonumberid||"?",nome:o.name||"",
      dono_atual:ownerNome,dono_guid:norm(ownerGuid),pool:!!pool,tipos:[],atividades:[]};
    if(!dealMap[k].tipos.includes(tipo)) dealMap[k].tipos.push(tipo);
  }

  console.log("[1/5] Stage 1 movidos em "+_H+"...");
  const s1=await pg(base+"/opportunities?userQuery="+VIEW.stage1,h);
  for(const r of s1){
    if((r.apwip_stage1_obtainedleaseeconomics||"").slice(0,10)!==_H)continue;
    const og=eff(r,"_apwip_stage1owner_value"); const onm=r["_ownerid_value@"+FV]||"";
    const pool=POOL.test(onm);
    const nome=isDir(norm(og))?NM[norm(og)]:(onm||"—");
    upsert(r.opportunityid,r,"S1",og,nome,pool);
  }

  console.log("[2/5] Stage 3 movidos...");
  const s3=await pg(base+"/opportunities?userQuery="+VIEW.stage3,h);
  for(const r of s3){
    if((r.apwip_stage3date||"").slice(0,10)!==_H)continue;
    const og=eff(r,"_apwip_stage3owner_value"); const onm=r["_ownerid_value@"+FV]||"";
    const pool=POOL.test(onm);
    const nome=isDir(norm(og))?NM[norm(og)]:(onm||"—");
    upsert(r.opportunityid,r,"S3",og,nome,pool);
  }

  console.log("[3/5] Repropostas...");
  const pr=await pg(base+"/apwip_pricingoptions?userQuery="+VIEW.pricing,h);
  const sm=pr[0]||{};
  const kS3d=Object.keys(sm).find(k=>/stage3date$/.test(k)&&!k.includes("@"));
  const kS5d=Object.keys(sm).find(k=>/stage5date$/.test(k)&&!k.includes("@"));
  const kOpp=Object.keys(sm).find(k=>/_apwip_opportunityid_value$/.test(k));
  const repGuids=[];
  for(const r of pr){
    if(brDate(r.createdon)!==_H)continue;
    const cd=_H,s3d=(r[kS3d]||"").slice(0,10),s5d=(r[kS5d]||"").slice(0,10);
    if(cd===s3d||cd===s5d)continue;                 // orgânica
    const g=norm(r[kOpp]); if(g&&!repGuids.includes(g))repGuids.push(g);
  }
  if(repGuids.length){
    for(let i=0;i<repGuids.length;i+=15){
      const f=repGuids.slice(i,i+15).map(x=>"opportunityid eq "+x).join(" or ");
      const rs=await pg(base+"/opportunities?$select=opportunityid,name,apwip_opportunityautonumberid,_ownerid_value,_apwip_stage3owner_value&$filter="+f,hA);
      rs.forEach(o=>{const og=eff(o,"_apwip_stage3owner_value");const onm=o["_ownerid_value@"+FV]||"";
        upsert(o.opportunityid,o,"REPROP",og,isDir(norm(og))?NM[norm(og)]:(onm||"—"),POOL.test(onm));});
    }
  }

  const dealGuids=Object.keys(dealMap);
  console.log("   → "+dealGuids.length+" deals moveram em "+_H);

  console.log("[4/5] Histórico de atividades dos deals movidos...");
  const ASEL="$select=activityid,subject,description,activitytypecode,createdon,actualend,statecode,_ownerid_value,_regardingobjectid_value";
  for(let i=0;i<dealGuids.length;i+=10){
    const f=dealGuids.slice(i,i+10).map(x=>"_regardingobjectid_value eq "+x).join(" or ");
    const rs=await pg(base+"/activitypointers?"+ASEL+"&$filter=("+f+")&$orderby=createdon asc",hA);
    rs.forEach(a=>{
      const k=norm(a._regardingobjectid_value); if(!dealMap[k])return;
      dealMap[k].atividades.push({
        id:a.activityid, tipo:a.activitytypecode||"", subject:a.subject||"",
        desc:a.description||"", data:brDate(a.createdon),
        owner_guid:norm(a._ownerid_value), owner:a["_ownerid_value@"+FV]||"",
        concluida:a.statecode===1
      });
    });
    if(i%50===0)console.log("   ...",i,"/",dealGuids.length);
  }

  console.log("[5/5] Atividades CONCLUÍDAS no dia (13 diretores)...");
  const ownerF=DIR.map(g=>"_ownerid_value eq "+g).join(" or ");
  const ad=await pg(base+"/activitypointers?"+ASEL+"&$filter=(actualend ge "+D0+" and actualend lt "+D1+") and statecode eq 1 and ("+ownerF+")",hA);
  ad.forEach(a=>out.acts_dia.push({
    id:a.activityid, tipo:a.activitytypecode||"", subject:a.subject||"", desc:a.description||"",
    data:brDate(a.actualend||a.createdon), owner_guid:norm(a._ownerid_value),
    owner:NM[norm(a._ownerid_value)]||a["_ownerid_value@"+FV]||"",
    opp:norm(a._regardingobjectid_value)
  }));

  out.deals=Object.values(dealMap);
  out._meta={alvo:_H,d0:D0,d1:D1,sem_ini:SEMINI,coletado_em:new Date().toISOString(),n_dir:13,
    n_deals:out.deals.length,n_acts_dia:out.acts_dia.length,
    n_acts_hist:out.deals.reduce((n,d)=>n+d.atividades.length,0)};

  const blob=new Blob([JSON.stringify(out,null,1)],{type:"application/json"});
  const a=document.createElement("a"); a.href=URL.createObjectURL(blob);
  a.download="calor_"+_H+".json"; a.click();
  console.log("%c✔ PRONTO — calor_"+_H+".json baixado","color:#009877;font-weight:bold;font-size:14px");
  console.table(out.deals.map(d=>({L:d.L,Tipo:d.tipos.join("+"),Dono:d.dono_atual,Pool:d.pool?"POOL":"",Ativs:d.atividades.length})));
  return "OK";
})()
