/* ===== REPORTE DIÁRIO CRM (APW) — 14 diretores — ALVO 09/09/2026 =====
   Aba logada em https://apwireless.crm.dynamics.com → F12 → Console → cola TUDO → Enter
   Baixa: reporte_2026-09-09.json  (regex via new RegExp — cola sem erro de barra) */
(async () => {
  const API="https://apwireless.crm.dynamics.com/api/data/v9.2",FV="OData.Community.Display.V1.FormattedValue";
  const H={"Accept":"application/json","OData-MaxVersion":"4.0","OData-Version":"4.0","Prefer":'odata.maxpagesize=5000,odata.include-annotations="'+FV+'"'};
  const VIEW_S1="a020dfbe-4a3f-f111-88b4-00224805b156",VIEW_S3="50aca927-4b3f-f111-88b4-00224805b156",VIEW_PRC="e85d5310-8c42-f111-88b4-6045bd07461c";
  const F_S1="apwip_stage1_obtainedleaseeconomics",F_S3="apwip_stage3date",F_S5="apwip_stage5date",F_PRC="createdon";
  const NM={"70a07063-6fdf-e311-8265-00155d00fe04":"Jose Daniel Ramos","c336d752-e6fb-ed11-8849-000d3a5a8269":"Regina Silveira","b5ece3de-6c3c-ee11-bdf4-000d3a5a8e5c":"Kamilla Rosa","0f5c2d0c-d6d4-e911-a9a8-000d3a360ed5":"Felipe Porto","342e4168-9660-e911-a997-000d3a360ed5":"Fabio Boturao","2d3010fa-61f4-ed11-8848-000d3a5a82bf":"Aline Sanzi","f41da072-58a6-ed11-aad1-000d3a5a8baa":"Victoria Navarro","bd19844f-8b38-ee11-bdf4-6045bd095340":"Daiane dos Santos","cb48e1a0-4959-ee11-be6f-000d3a317ead":"Gisele Tognolo","edbec271-d59d-ef11-8a6a-0022480985f3":"Andressa Bueno","bea2794a-97c3-ef11-b8e9-000d3a3355b9":"Roana Reboredo","d49fdec3-f849-ef11-a317-000d3a5be4ff":"Carolina Brentzel","06a1eeda-93d7-f011-8543-6045bd0a09fc":"Aline Felix","8e616ea9-8d8a-f111-ab0f-70a8a5b0fc4c":"Marcia Mangiulli"};
  const DIR=Object.keys(NM),POOL=new RegExp("pool|apwreports|surrender|disqualified|system|admin|integra|crm|queue","i");
  const norm=v=>(v||"").toString().toLowerCase().replace(/[{}]/g,""),isDir=g=>!!NM[norm(g)];
  const hoje=new Date("2026-09-09T12:00:00"),iso=d=>d.toISOString().slice(0,10),DIA=iso(hoje);
  const semIni=(()=>{const d=new Date(hoje),dow=(d.getDay()+6)%7;d.setDate(d.getDate()-dow);return iso(d);})();
  const FIM_UTC=(()=>{const d=new Date(hoje);d.setDate(d.getDate()+1);return iso(d)+"T03:00:00Z";})(),semIniUTC=semIni+"T03:00:00Z";
  const diasU=(()=>{let n=0;const a=new Date(semIni+"T12:00:00"),b=new Date(DIA+"T12:00:00");for(let d=new Date(a);d<=b;d.setDate(d.getDate()+1)){const w=d.getDay();if(w>=1&&w<=5)n++;}return n;})();
  const brDate=u=>{if(!u)return null;const d=new Date(u);d.setHours(d.getHours()-3);return d.toISOString().slice(0,10);};
  const inSem=dia=>dia&&dia>=semIni&&dia<=DIA,isDia=dia=>dia===DIA;
  async function pg(u){const o=[];let n=u,g=0;while(n&&g++<20){const r=await fetch(n,{headers:H,credentials:"include"});if(!r.ok)throw new Error("HTTP_"+r.status);const j=await r.json();o.push(...(j.value||[]));n=j["@odata.nextLink"]||null;}return o;}
  const view=(e,i)=>pg(API+"/"+e+"?userQuery="+i);
  const zero=()=>({s1:0,s3:0,rep:0,ativ:0,subst:0}),D={};
  DIR.forEach(g=>{D[g]={nome:NM[g],guid:g,dia:zero(),semana:zero(),ls:{dia:{},semana:{}}};});
  const tot={dia:zero(),semana:zero()};
  const bump=(g,c,dia,L)=>{if(!isDir(g))return;const gg=norm(g);if(inSem(dia)){D[gg].semana[c]++;tot.semana[c]++;if(L)(D[gg].ls.semana[c]=D[gg].ls.semana[c]||[]).push(L);}if(isDia(dia)){D[gg].dia[c]++;tot.dia[c]++;if(L&&c!=="ativ"&&c!=="subst")(D[gg].ls.dia[c]=D[gg].ls.dia[c]||[]).push(L);}};
  const eff=(r,k)=>{const nm=r["_ownerid_value@"+FV]||"";if(!POOL.test(nm)&&isDir(r._ownerid_value))return norm(r._ownerid_value);if(k&&r[k])return norm(r[k]);return norm(r._ownerid_value);};
  const fk=(row,rx)=>Object.keys(row||{}).find(k=>rx.test(k))||null,Lof=r=>r.apwip_opportunityautonumberid||r["apwip_opportunityautonumberid@"+FV]||null;
  const av=[];
  let s1=[];try{s1=await view("opportunities",VIEW_S1);}catch(e){av.push("S1:"+e.message);}
  const k1=s1.length?fk(s1[0],/_apwip_stage1owner_value$/):null;
  for(const r of s1){const dia=brDate(r[F_S1]);if(!dia||dia>DIA)continue;bump(eff(r,k1),"s1",dia,Lof(r));}
  let s3=[];try{s3=await view("opportunities",VIEW_S3);}catch(e){av.push("S3:"+e.message);}
  const k3=s3.length?fk(s3[0],/_apwip_stage3owner_value$/):null;
  for(const r of s3){const dia=brDate(r[F_S3]);if(!dia||dia>DIA)continue;bump(eff(r,k3),"s3",dia,Lof(r));}
  let prc=[];try{prc=await view("apwip_pricingoptions",VIEW_PRC);}catch(e){av.push("PRC:"+e.message);}
  const kOpp=prc.length?(fk(prc[0],/_apwip_opportunityid_value$/)||"_apwip_opportunityid_value"):"_apwip_opportunityid_value";
  const prcBy={},oppIds=new Set();
  for(const p of prc){const oid=norm(p[kOpp]);if(!oid)continue;const dia=brDate(p[F_PRC]);if(!dia||dia>DIA)continue;(prcBy[oid]=prcBy[oid]||[]).push({dia,createdon:p[F_PRC]});oppIds.add(oid);}
  const oppList=[...oppIds],oI={};let s5disp="verificar";
  async function chunk(ids,w5){const sel="apwip_opportunityautonumberid,_ownerid_value,_apwip_stage3owner_value,"+F_S3+(w5?",_apwip_stage5owner_value,"+F_S5:"");const f=ids.map(g=>"opportunityid eq "+g).join(" or ");return pg(API+"/opportunities?$select="+sel+"&$filter=("+f+")");}
  for(let i=0;i<oppList.length;i+=20){const ch=oppList.slice(i,i+20);let rows=null;try{rows=await chunk(ch,true);s5disp=true;}catch(e){try{rows=await chunk(ch,false);s5disp="verificar";}catch(e2){av.push("opp:"+e2.message);rows=[];}}for(const r of rows){const oid=norm(r.opportunityid);oI[oid]={L:Lof(r),owner:norm(r._ownerid_value),ownerNm:r["_ownerid_value@"+FV]||"",s3owner:r["_apwip_stage3owner_value"]?norm(r._apwip_stage3owner_value):null,s5owner:r["_apwip_stage5owner_value"]?norm(r._apwip_stage5owner_value):null,s3date:brDate(r[F_S3]),s5date:r[F_S5]?brDate(r[F_S5]):null};}}
  const ano=hoje.getFullYear(),inY=d=>d&&(+d.slice(0,4)===ano);
  for(const oid of oppList){const info=oI[oid];if(!info)continue;let dono=info.owner;if((POOL.test(info.ownerNm)||!isDir(dono))&&info.s3owner)dono=info.s3owner;if(!isDir(dono))continue;const s3o=info.s3owner&&info.s3owner!==dono,s5o=s5disp===true?(info.s5owner&&info.s5owner!==dono):s3o,herd=s3o&&s5o;const ps=(prcBy[oid]||[]).slice().sort((a,b)=>(a.createdon||"").localeCompare(b.createdon||""));if(!ps.length)continue;const prop=!herd&&((info.s3owner===dono&&inY(info.s3date))||(s5disp===true&&info.s5owner===dono&&inY(info.s5date))||(!info.s3owner&&!info.s5owner));const cont=herd?ps:(prop?ps.slice(1):ps);[...new Set(cont.map(p=>p.dia))].forEach(dia=>bump(dono,"rep",dia,info.L));}
  const SIG=[new RegExp("\\b(r\\$|\\d{1,3}(\\.\\d{3})*(,\\d{2})?|\\d+\\s?(reais|mil|k))\\b","i"),new RegExp("(síndico|sindico|proprietári|proprietari|administrador|condomínio|condominio|operadora|torre|locador|advogad)","i"),new RegExp("(próximo passo|proximo passo|retornar|agendar|enviar|aguard|follow|reuni|visita|proposta|marcar|ligar)","i"),new RegExp("(objeç|objec|recus|negociaç|negociac|contraproposta|exig|condiç|condic|quer|pediu|preocupa)","i")];
  const nSig=t=>SIG.reduce((n,rx)=>n+(rx.test(t)?1:0),0),isSub=t=>{const L=(t||"").trim().length;return L>=180||(L>=140&&nSig(t)>=2);};
  const AA=new RegExp("(mail merge|automatic activity|template using the|completed automatically by the|xl calculator)","i"),AS=new RegExp("^\\s*(begin work|pricing desk|management task|create (verbal|written) proposal|moved to stage|workflow|reminder)","i"),isAuto=t=>{const s=(t||"").trim();return AA.test(s)||AS.test(s);};
  const oF=DIR.map(g=>"_ownerid_value eq "+g).join(" or ");
  let acts=[];try{acts=await pg(API+"/activitypointers?$select=activityid,subject,description,createdon,_ownerid_value&$filter=(createdon ge "+semIniUTC+" and createdon lt "+FIM_UTC+") and ("+oF+")");}catch(e){av.push("act:"+e.message);}
  for(const a of acts){const g=norm(a._ownerid_value);if(!isDir(g))continue;const dia=brDate(a.createdon);if(!dia||dia>DIA)continue;const de=a.description||"",su=a.subject||"";if(isAuto(de)&&isAuto(su))continue;bump(g,"ativ",dia,null);if(isSub(de))bump(g,"subst",dia,null);}
  const dmy=s=>s.slice(8,10)+"/"+s.slice(5,7)+"/"+s.slice(0,4);
  const diretores=DIR.map(g=>D[g]).sort((a,b)=>{const mv=x=>x.semana.s3*100+x.semana.s1*10+x.semana.rep;return mv(b)-mv(a)||b.semana.subst-a.semana.subst||a.nome.localeCompare(b.nome);});
  const out={referencia:dmy(DIA),alvo:DIA,corte_hora:new Date().toISOString(),dia:dmy(DIA),semana_janela:dmy(semIni)+" – "+dmy(DIA),dias_uteis:{decorridos:diasU,total:5},metas:{s1:3,s3:2,repropostas:4,atividades:100,substantivas_pct:35,ativ_dia:20,subst_dia_pct:35},n_diretores:DIR.length,diretores,totais:{dia:tot.dia,semana:tot.semana},destaque_dia:null,destaque_semana:null,_meta:{host:location.origin,stage5owner_disponivel:s5disp,contagem:{s1_rows:s1.length,s3_rows:s3.length,pricing_rows:prc.length,opps_detalhadas:oppList.length,atividades:acts.length},avisos:av}};
  const blob=new Blob([JSON.stringify(out,null,1)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="reporte_"+DIA+".json";document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},1000);
  console.log("%c[REPORTE 09/09] baixou reporte_"+DIA+".json","color:green;font-weight:bold",{totais:out.totais,contagem:out._meta.contagem,avisos:out._meta.avisos});
})();
