---
name: "apw-crm-key-notes-writer"
description: "Use quando o Lucas pedir para gravar/preencher os Key Notes (texto de Investment Opportunity) de oportunidades da APW no Dynamics 365, escolher e linkar a Pricing Option de um deal, ou processar um lote de deals da planilha de submission diretamente no CRM. Aciona com \"preenche o CRM\", \"grava as key notes\", \"linka a pricing option\", \"roda esses deals no Dynamics\", \"joga no CRM\", menção a Lnumber + Dynamics/CRM. NÃO use para apenas redigir o texto do submission sem gravar (isso é apw-submission-writer), para análise registral/cartorária de documentos ou montagem do dossiê de pré-DD (isso é apw-pre-dd-legal), nem para análise de cláusula contratual (apw-telecom-real-estate-counsel)."
---

# APW CRM Key Notes Writer

Opera o Dynamics 365 da APW Brasil via Claude in Chrome: grava o texto de Investment Opportunity ("Key Notes") e linka a Pricing Option correta de cada oportunidade, na sessão autenticada do Lucas. Esta skill **opera** o CRM — não apenas redige.

## Princípio fundamental

**Parar antes do Stage 8. Sempre.** Esta skill preenche Pricing Option e Key Notes. A promoção de estágio é ação irreversível e auditável que **só o Lucas executa, manualmente**. Violar a letra desta regra é violar o espírito dela — não promova stage nem sob "ok genérico" anterior, nem sob pressa, nem como "último passo natural".

O texto do Investment Opportunity é produzido pela skill `apw-submission-writer`. Esta skill assume esse texto pronto e cuida de gravá-lo **corretamente e por inteiro** no campo certo.

## PASSO ZERO OBRIGATÓRIO — puxar a linha do deal na planilha do Forms

**Antes de gravar qualquer coisa no CRM, ler a resposta do diretor na planilha do Forms.** Ela é a fonte primária dos dados comerciais do deal (investimento, prazo, condições de pagamento, IRR, expectativa de fechamento). Sem ela, não há como validar a Pricing Option nem checar o Key Notes.

Se o Lucas já trouxe o texto do Investment Opportunity pronto (produzido por `apw-submission-writer`, que já consultou a planilha nesta mesma sessão), **não repetir a extração** — reaproveitar os dados já lidos.

### Identificação do arquivo (verificado em produção)

| Item | Valor |
|---|---|
| Nome | `"Stage 6(aceite verbal) ou7(LOI recebida) – Informações da Negociação".xlsx` |
| Host | `apwireless-my.sharepoint.com` |
| Site (web) | `/personal/lminozzo_apwbrasil_com_br` |
| UniqueId (sourcedoc) | `b45b8db5-a7bc-4154-a201-ac714a5fc1e6` |
| Drive item id | `01VJ5HVY5VRVN3JPFHKRA2EANMOFFF7QPG` |
| Estrutura | 1 aba (`sheet1`), header = linha 1, dados a partir da linha 2 |
| Chave de busca | coluna **F** = L-number (formato `L884789`) |

### Como ler (Claude in Chrome, sem screenshot)

`get_page_text` **não funciona** no Excel Online (canvas). A API `workbook/worksheets` retorna 404 nesse tenant. O caminho que funciona é baixar os bytes do arquivo por REST e descompactar o XLSX no próprio browser.

1. `navigate` para qualquer página do SharePoint do Lucas (mesma origem), ex.: `https://apwireless-my.sharepoint.com/personal/lminozzo_apwbrasil_com_br/_layouts/15/onedrive.aspx`
2. Rodar via `javascript_tool` (trocar o `LNUM`):

```javascript
window.__APW=null;(async()=>{try{
const SITE="/personal/lminozzo_apwbrasil_com_br";
const GUID="b45b8db5-a7bc-4154-a201-ac714a5fc1e6";
const LNUM="L884789";                                   // <<< L-number do deal
const r=await fetch(`${SITE}/_api/web/GetFileById(guid'${GUID}')/$value`);
const buf=new Uint8Array(await r.arrayBuffer()),dv=new DataView(buf.buffer);
let e=-1;for(let i=buf.length-22;i>=0;i--){if(dv.getUint32(i,true)===0x06054b50){e=i;break;}}
const cnt=dv.getUint16(e+10,true),cd=dv.getUint32(e+16,true);let p=cd;const ent={};
for(let k=0;k<cnt;k++){const nl=dv.getUint16(p+28,true),el=dv.getUint16(p+30,true),cl=dv.getUint16(p+32,true);
 ent[new TextDecoder().decode(buf.subarray(p+46,p+46+nl))]={m:dv.getUint16(p+10,true),cs:dv.getUint32(p+20,true),lo:dv.getUint32(p+42,true)};
 p+=46+nl+el+cl;}
const unz=async n=>{const x=ent[n],nl=dv.getUint16(x.lo+26,true),el=dv.getUint16(x.lo+28,true),s=x.lo+30+nl+el,d=buf.subarray(s,s+x.cs);
 return x.m===0?new TextDecoder().decode(d)
  :await new Response(new Blob([d]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).text();};
const dec=s=>s.replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&apos;/g,"'").replace(/_x000D_/g,'').replace(/&amp;/g,'&');
const sst=[...(await unz('xl/sharedStrings.xml')).matchAll(/<si>([\s\S]*?)<\/si>/g)]
  .map(m=>dec([...m[1].matchAll(/<t[^>]*>([\s\S]*?)<\/t>/g)].map(x=>x[1]).join('')));
const sh=await unz('xl/worksheets/sheet1.xml');const rows={};
for(const m of sh.matchAll(/<row[^>]*r="(\d+)"[^>]*>([\s\S]*?)<\/row>/g)){const o={};
 for(const c of m[2].matchAll(/<c r="([A-Z]+)\d+"([^>]*?)(?:\/>|>([\s\S]*?)<\/c>)/g)){
  const t=/t="([^"]+)"/.exec(c[2]),b=c[3]||'',v=/<v>([\s\S]*?)<\/v>/.exec(b);
  let val=v?v[1]:'';
  if(t&&t[1]==='s'&&v)val=sst[+val];
  else if(t&&t[1]==='inlineStr'){const i2=/<t[^>]*>([\s\S]*?)<\/t>/.exec(b);val=i2?dec(i2[1]):'';}
  o[c[1]]=dec(String(val));}
 rows[m[1]]=o;}
window.__H=rows['1'];
window.__APW=Object.entries(rows).filter(([k,o])=>k!=='1'&&(o.F||'').toUpperCase().includes(LNUM.toUpperCase()))
  .map(([k,o])=>({row:k,id:o.A,...o}));
}catch(err){window.__APW="ERR "+err}})();"go"
```

> **Atenção ao regex das células.** O Excel grava célula vazia auto-fechada (`<c r="O112" s="15"/>`). Um regex ingênuo (`([^>]*)\/?>(?:...)?`) faz a célula vazia consumir até o `</c>` da célula seguinte — as colunas deslizam e valores aparecem na coluna errada (sintomas: P/R/Z/AB/AE falsamente vazias, números absurdos). O script acima já usa a forma correta `(?:\/>|>([\s\S]*?)<\/c>)`. Antes de gravar qualquer coisa no CRM, conferir 2–3 valores lidos contra o esperado.

3. Ler o resultado em fatias (o `javascript_tool` trunca ~1000 chars por retorno):

```javascript
window.__APW.length + " | " + window.__APW.map(x=>x.row+":"+x.F+" "+x.G).join(" ; ")
```

```javascript
(o=>["L="+o.F,"deal="+o.G,"tipo="+o.L,"towerco="+o.P,"invest="+o.AM,"prazo="+o.AN,"irr="+o.AP,"pagto="+o.AQ,"fech="+o.AF].join(" | "))(window.__APW[0])
```

### Colunas que importam para esta skill

| Col | Conteúdo | Uso aqui |
|---|---|---|
| F | L-number | chave de busca |
| G | Nome do Deal | **confirmar que bate com o nome da opp no CRM** |
| L | Tipo da negociação (DRS / Cessão / C&V) | sanity check do tipo de Pricing Option |
| P | Towerco | sanity check |
| AF | Expectativa de Fechamento (serial Excel) | Closing Expectation no Deal Overview |
| AM | Investimento | valor da operação |
| AN | Prazo (anos) | **match da Pricing Option** |
| AP | IRR da calculadora | conferência contra `apwip_suggestedpayoutirr` |
| AQ | Condições de pagamento | **match da Pricing Option** (nº de parcelas) |

Mapa completo das 55 colunas (A..BC) e regras de parsing dos valores: skill **`apw-submission-writer`**.

Se o L-number **não** estiver na planilha, ou houver mais de uma resposta para o mesmo L: **parar e avisar o Lucas** (duplicata → usar a de maior Id na coluna A e sinalizar).

### Fallback quando a planilha do Forms está incompleta ou ausente

Quando o L-number não estiver na planilha, ou o diretor tiver preenchido só parte das colunas, **não deixar o Key Notes em branco.** Puxar as informações faltantes pelas fontes abaixo, na ordem, sinalizando de onde veio cada bloco no rascunho pro Lucas:

1. **LOIs (Cartas de Intenção)** — **sempre a fonte primária de `Termo` (anos) e `Investment / Payment Structure`**. Se são vários contratos/rooftops no mesmo deal, checar TODAS as LOIs; o termo pode divergir por site e a soma de investimentos vem por LOI.
2. **SIR (Site Inspection Report — FCA Telecom / Filipe Cabral El Alam)** — fonte primária de **estrutura física por rooftop**: altura AGL (Above Ground Level, do solo até a antena — **não confundir com área locada em m²**), nº de setores, tecnologia por setor (2G/3G/4G/5G), tenancy visual, patologias (equipamento desinstalado, vestígio de 3ª operadora), cobertura RF qualitativa ("ÓTIMA/BOA/RUIM"), medidor identificado, acesso.
3. **Contratos + aditivos (dossiê pré-DD)** — fonte primária de **área locada em m²**, escalation index (IPC-FIPE, IGP-M, IPCA, INPC), vigência, cadeia de sub-rogação TowerCo, precedentes de cessão, cláusulas de anuência.
4. **Base Anatel local** (skill `apw-erb-towerco-triage`, SMP jul/2026 embutida) — validar carrier/tenancy/tech oficial e sinalizar divergência vs SIR/planilha.
5. **Levantamento de arredores** (WebSearch + Google Earth) — quando o texto precisar contextualizar **densidade urbana, vias principais, comércio, distância a estações metrô/CPTM/rodovias**, e comparar rent vs benchmark regional. Argumento comercial recorrente: "**rents on this site are below the regional benchmark for rooftop 4G/5G in [bairro] → reduces churn risk + upside on renewal**" — usar quando os dois lados (rent contratual + benchmark regional levantado) suportarem.

**Regra:** Se puxou de fallback, marcar no rascunho do Key Notes ou em "Pontos de atenção antes de submeter" que a origem foi fallback (não planilha) e listar os campos afetados. Isso preserva a auditoria da submission.

### Nomenclatura crítica (não confundir)

- **AGL (Above Ground Level)** = altura em metros da antena acima do solo (do chão até a antena) — vem do SIR. **NÃO é área locada.**
- **Área locada (m²)** = superfície do rooftop cedida à TowerCo — vem do contrato/aditivo.
- **Assignment of Rents** = nomenclatura APW oficial em inglês pra "Cessão de Créditos" (rent stream). **NUNCA usar "Credit Assignment", "Assignment of Credit Rights", "receivables assignment" ou "CDC" no texto em inglês.** Ver skill `apw-submission-writer`.
- **Tratamento de TowerCos:** ATC e SBA reconhecem cessão pelo real estate desk como transação padrão. NÃO usar linguagem defensiva do tipo "no clause prohibits" — pitch é de cessão como processo standard.

## Pré-requisitos (confirmar antes de começar)

1. Lucas logado em `apwireless.crm.dynamics.com` na aba do Chrome.
2. Confirmação explícita do Lucas de que o uso do CRM por agente está alinhado com a Radius. A Radius pediu: **sem screenshots** em domínio Dynamics.
3. Lista de L-numbers a processar, confirmada com o Lucas.
4. Linha da planilha do Forms extraída (Passo Zero) OU fallback declarado.

## Regra de compliance de navegação

Domínio Dynamics é sensível. **Zero screenshots.** Usar apenas `navigate`, `read_page`, `get_page_text`, `javascript_tool`, `find`, `form_input`. Ver skill `apw-chrome-agent-lean-compliance`. Declarar o plano de ferramentas no início e o consumo no fim.

## Mapa de campos do CRM (verificado em produção)

| Conceito | Campo lógico D365 | Tipo | Localização na tela |
|---|---|---|---|
| Key Notes (texto do Investment Opportunity) | `apwip_opportunitysummary` | string, maxlength 10000 | Aba **Sales Manager** > card "Investor Submission Worksheet" |
| Chosen Pricing Option | `apwip_chosenpricingoption` | lookup → `apwip_pricingoption` | Aba **Pricing Options** > "Pricing Options Notes" |
| Registros de Pricing Option | entidade `apwip_pricingoptions` | collection | subgrid `Pricing_Options` |

Lookup que liga Pricing Option à opp: **`_apwip_opportunityid_value`**.
Campos úteis do registro de pricing: `apwip_name`, `apwip_transactiontermyears`, `apwip_numberofpayments`, `apwip_suggestedpayoutirr`, `createdon`.

⚠️ "Key Notes" NÃO é um campo chamado "keynotes" — é `apwip_opportunitysummary`. Outros campos com "notes" no nome (`apwip_notes`, `new_notes`, `apwip_payoutoptionnotesdirector`) NÃO são o campo certo. Não confundir.

## Fluxo de execução (por deal)

### 0. Puxar a linha do deal na planilha do Forms

Ver "PASSO ZERO OBRIGATÓRIO" acima. Guardar prazo (AN), condições de pagamento (AQ), investimento (AM) e IRR (AP) — são eles que sustentam o match da Pricing Option no passo 3. Se planilha incompleta, ver "Fallback quando a planilha do Forms está incompleta ou ausente".

### 1. Localizar a opp pelo L-number (Web API, não busca visual)

```javascript
fetch("/api/data/v9.2/opportunities?$select=opportunityid,name&$filter=contains(name,'L929703')",
  {headers:{Accept:"application/json"}}).then(r=>r.json())
```

Abrir via `navigate` para `.../pagetype=entityrecord&etn=opportunity&id=<opportunityid>`.
**Checkpoint:** confirmar no chat que a opp aberta é o L-number certo (o nome do deal tem que bater com a coluna G da planilha) ANTES de tocar em qualquer campo. URLs do Dynamics usam GUID, não L-number — nunca assumir.

### 2. Ler os Pricing Options da opp

```javascript
fetch(`/api/data/v9.2/apwip_pricingoptions?$select=apwip_name,apwip_transactiontermyears,apwip_numberofpayments,apwip_suggestedpayoutirr,createdon&$filter=_apwip_opportunityid_value eq <oppId>&$orderby=createdon desc`)
```

### 3. CHECKPOINT obrigatório de Pricing Option

Fazer o match por **parâmetros** (prazo + nº de pagamentos) vindos da planilha (AN + AQ) ou das LOIs (fallback), pois a planilha NÃO traz o nome do registro:
- "à vista" / lump sum → registro `LumpSum` (1 pagamento)
- "ato + N semestrais em X anos" → registro `XYr-(N+1)Pay` (ato conta como pagamento)
- Fee Simple → tipicamente `99_YrTerm_LumpSum`

**Parar e perguntar ao Lucas quando:**
- Mais de um registro bate com os parâmetros (escolher entre eles é dele).
- Nenhum registro bate (provável divergência form×CRM — Lucas faz o pricing manual).
- A busca retorna zero ou múltiplas opps.
- O IRR da planilha (AP) diverge do `apwip_suggestedpayoutirr` do registro escolhido.
- **LOI e Pricing Option divergem em prazo (ex.: LOI 30 anos, PO 20 anos).** Não linkar PO desatualizada; Lucas precisa recalcular ou emitir PO nova antes.

NUNCA linkar Pricing Option no chute. Linkar errado contamina a submission e é auditável.

### 4. Verificar que o Key Notes está vazio

```javascript
window.Xrm.Page.getAttribute('apwip_opportunitysummary').getValue()  // deve ser null
```
Se já tiver conteúdo, **parar e avisar** — não sobrescrever sem o ok do Lucas.

### 5. Gravar (setValue + fireOnChange + save)

```javascript
const a = window.Xrm.Page.getAttribute('apwip_opportunitysummary');
a.setValue(txt); a.fireOnChange();
const po = window.Xrm.Page.getAttribute('apwip_chosenpricingoption');
po.setValue([{id:'<pricingOptionId>', name:'<nome>', entityType:'apwip_pricingoption'}]);
await window.Xrm.Page.data.save();
```

### 6. READBACK OBRIGATÓRIO — verificar a persistência no banco

`save()` retornar "OK" **não garante** que o texto foi gravado inteiro. Já houve truncamento silencioso (texto cortado, save sem erro). SEMPRE reler do banco e comparar o tamanho:

```javascript
const r = await fetch(`/api/data/v9.2/opportunities(<oppId>)?$select=apwip_opportunitysummary`,
  {headers:{Accept:'application/json','Cache-Control':'no-cache'}});
const t = (await r.json()).apwip_opportunitysummary || '';
// t.length DEVE ser igual ao length do texto enviado. Se for menor → truncou → regravar.
```

Só declarar o deal concluído quando `persisted.length === expected.length`.

### 7. Parar. Não promover Stage.

Reportar ao Lucas: linha da planilha usada (nº da linha + Id) OU fallback declarado, Pricing Option linkado, Key Notes gravado e verificado, stage intocado.

## Regras de formato do Key Notes (herdadas de apw-submission-writer)

- **Abertura punchy obrigatória:** o primeiro parágrafo do DEAL OVERVIEW é uma sentença única no formato `Investment Opportunity is for a [N]-year Assignment of Rents on [K] rooftop(s) [...] hosting [carrier] on [TowerCo], [...]`. Sem lead-in institucional antes.
- **Closing Expectation** vai no bloco **Deal Overview**, nunca em Timeline/Negotiation Notes.
- Deal **TBSA**: **NÃO** incluir bloco "TBSA UNDERWRITING INSTRUCTION" nem CAPEX Fee. A verba TBSA / CAPEX Fee está **DESCONTINUADA** — não escrever "TBSA Project" nem instrução de IRR mínimo de 16% mesmo que a coluna Q da planilha venha preenchida em respostas antigas. TBSA é TowerCo comum. Prazo < 30 anos em deal TBSA continua exigindo justificativa própria no Negotiation Notes.
- **IRR sem vírgula** vindo da planilha = decimal com uma casa (ex.: "162" = 16,2%). Ambíguo ("16", "1620") → perguntar.
- Investment com valor implausível (ex.: "600" para um deal de aluguel alto) → assumir milhares com nota, ou perguntar.
- **Fee Simple com split escritura+registro:** quando o form indicar pagamento em duas parcelas (ato + registro), usar `Payment Structure: Two installments — (i) partial payment upon deed execution; (ii) balance upon registration of the acquisition at the CRI. Exact split TBD in final agreement.` Nunca inventar percentuais.
- **TowerCo identificada pelo POP:** se o POP mostrar TowerCo diferente do que está no contrato (ex.: contrato com operadora, POP da ATC), a TowerCo do Key Notes é a do POP — não a do contrato nem a da planilha. Registrar a cessão consumada no Negotiation Notes.
- **Deal com múltiplos rooftops/contratos no mesmo condomínio:** discriminar Site A / Site B (…) com TowerCo, carrier hospedado, tecnologia por setor, AGL e área locada. Somar rents e listar índices de escalation separadamente.
- **Rents below regional benchmark:** quando o levantamento de arredores + rent contratual suportarem, adicionar bullet no Negotiation Notes: "*Rents on [site(s)] are below the regional benchmark for rooftop 4G/5G in [bairro/subprefeitura] — reduces churn risk (below-market rent = high renewal probability from carriers) and offers upside on renewal/reset.*" Não inventar magnitude; se não puxou benchmark, escrever qualitativo e listar em Pontos de atenção.
- Texto em inglês, institucional, IC-ready. Sem emojis. Attention items honestos — gaps reais entram no texto, não se escondem.

## Hierarquia de fontes (quando divergem)

1. **LOIs** — mandam sobre prazo, investment, payment structure.
2. **Documentos do deal** (contrato, aditivos, matrícula, POP) — mandam sobre área locada, escalation, TowerCo por POP, vigência.
3. **SIR (FCA Telecom)** — manda sobre estrutura física (AGL, setores, tecnologia por setor, tenancy visual, RF qualitativa, patologias).
4. **Base Anatel** — manda sobre a planilha para tecnologia/operadora oficial do site.
5. **Planilha do Forms** — dados comerciais (investimento, prazo, pagamento, IRR, expectativas) quando LOI ainda não estiver disponível.
6. **CRM** — o que já está gravado.

Divergência nunca é corrigida em silêncio: entra em "Pontos de atenção" e vai ao Lucas.

## Pré-triagem documental e dossiê de pré-DD

Análise registral/cartorária de documentos (matrícula, certidão, contrato, ata, CCIR, POP), classificação de achados e montagem do dossiê de pré-DD do caso **não são desta skill** — são da skill **`apw-pre-dd-legal`**, que mantém o dossiê vivo do deal conforme os documentos chegam.

Esta skill (`apw-crm-key-notes-writer`) cuida só de **operar o CRM**: gravar Key Notes e linkar Pricing Option. Quando o Lucas mandar documento de deal para leitura jurídica, ou pedir "monta o dossiê" / "pré-DD do Lxxxx", usar `apw-pre-dd-legal`.

## Snapshot Anatel do site (enriquecer/validar o Key Notes)

Quando o deal tiver coordenada ou endereço, puxar o retrato do site na base Anatel LOCAL embutida na skill `apw-erb-towerco-triage` (SMP jul/2026 — automático, sem planilha) ANTES de gravar o Key Notes:

```bash
python3 /mnt/skills/user/apw-erb-towerco-triage/scripts/anatel_lookup.py \
  --near=<LAT>,<LNG> --radius 150 --cluster --json
```

Uso no texto do Investment Opportunity: confirmar carrier(s) do site, tenancy (multi-operadora = ativo core), tecnologia (5G/3500 = site investido) e coerência rooftop×greenfield com a trilha do deal. **Divergência** (ex.: planilha diz Vivo, base só tem TIM no ponto; ou planilha diz rooftop, base diz greenfield) = listar em "Pontos de atenção", NÃO corrigir sozinho no CRM. Nenhuma estação em 300 m = sinalizar ao Lucas antes de gravar.

## Tratamento especial — V.tal fiber shelter / passive fiber POP

Quando o Site Type do deal for **fiber shelter, POP de fibra, ground lease para operador neutro (V.tal, Nio Fibra, Alloha, Desktop, Brisanet), ou empty lot com shelter telecom sem antenas de celular**, o Key Notes segue lógica diferente do padrão rooftop/greenfield SMP. Não é torre. Não hospeda operadora de celular direto. É um nó da rede de transporte/agregação de fibra — o modelo de risco muda.

### Como reconhecer o tipo

- Contrato com V.TAL (CNPJ 02.041.460/0001-93), Nio Fibra, Oi Móvel S.A. herdado por V.tal via cessão, Alloha, Desktop, ou qualquer ISP neutro
- Fotos: shelter fechado permanente, muro/cerca, energia trifásica (tomada industrial azul), sem torre visível, sem antenas de painel de celular
- Área locada tipicamente 200-400 m² (ou lote inteiro)
- Sem coluna P (TowerCo) tradicional preenchida — porque o tenant *é* o operador de rede, não uma TowerCo

### Blocos obrigatórios no Technology Context (além do Anatel SMP padrão)

**1. Anatel STEL — Estações Terrenas (satélite)** — puxar SEMPRE em cidades médias com radiodifusão:
```
Fonte: https://sistemas.anatel.gov.br/stel/consultas (base pública, JavaScript requer sessão manual)
Alternativa: dados abertos da Anatel se o Lucas colar
Filtro: mesmas coord/endereço num raio de 500m
Serve pra: identificar CORREDOR TELECOM da cidade (concentração de broadcasters = fibra troncal ali)
```
Se 3+ broadcasters aparecerem no raio de 500m, é sinal forte de corredor histórico → mencionar no bloco "Portfolio approach / strategic case" que o sunk fiber CAPEX ali é infra irreproduzível barata.

**2. Expected access technology (heurística V.tal)** — parágrafo padrão pra deals V.tal:
- Baseline **GPON (ITU-T G.984, 2.5G↓/1.25G↑)** com overlay **XGS-PON (ITU-T G.9807.1, 10G simétrico)** nos ports premium
- Vendor: **Nokia 7360 ISAM** ou **Huawei MA5800** (dominantes pós-Oi)
- Backbone DWDM **Nokia 1830** ou **Ciena** 100G até o hub regional
- Power: trifásico + DC plant 48V + banco de baterias 8-24h + gerador diesel
- Passive plant: ODF com fiber-count nas centenas
- **Framing correto:** "mature, modular, commodity infrastructure — not bleeding-edge" (cuts both ways: teoricamente migratável, mas fibra troncal ancora o site)

**3. POP scale and role (best-effort inference)** — estimativa de nº residências:
- Puxar população IBGE da cidade → dividir por 2.8 hab/domicílio = domicílios
- % FTTH regional (interior SP: 60-70%; interior nordeste: 30-50%)
- Share V.tal (ex-Oi Fibra) no interior: 40-50% dos FTTH
- Ex: Garça 43k hab → 15.400 domicílios → 9-10k FTTH → **4-6k rodando em V.tal** (via Nio Fibra)
- Sempre marcar como "best-effort inference from public data; V.tal does not disclose POP-level subscriber counts"
- Fechar com: "Taking this POP offline would darken meaningful portions of the town for hours to days" — argumento operacional de baixo churn

**4. Distinction from last-mile cabinet** — dizer explicitamente:
> "This is not a last-mile street cabinet — the shelter footprint (Xm² fenced lot, permanent structure, three-phase power) is consistent with a fiber aggregation POP rather than a passive distribution point."

Sem essa frase, o IC pode achar que é um cabinet de rua descartável.

**5. Data provenance disclaimer** — fechar Technology Context com:
> "All technology-context information above was extracted from Anatel's public databases ([STEL], [MOSAICO for mobile stations — SMP dataset dated <mês/ano>], extracted on <data> for this analysis). A SIR will be commissioned to consolidate these findings on the ground — active shelter equipment (OLT model, port density, cross-connect count, ODF capacity), power redundancy (genset, DC plant), and fiber-entry count. The SIR will be attached to the submission package before IC."

Sempre incluir a data de extração — dado Anatel é atualizado mensalmente, o IC quer saber a fresqueza.

### Diferenças no Deal Overview

- **TowerCo / Tenant category:** escrever "V.tal (fiber neutral wholesale carrier — not a traditional tower company; direct tenant, no lease aggregator in the middle)" ou equivalente pro operador
- **Tenancy:** sempre 1 nesses deals (single tenant é o operador de fibra) — mas o *impacto* é multi-tenant por baixo (residenciais + backhaul de torres celulares próximas + B2B de broadcasters)
- **Tenant(s) & Technologies:** "V.tal — fiber optic transport (GPON baseline with XGS-PON overlay expected — see Technology Context); serves as regional POP for FTTH residential (via Nio Fibra subsidiary) and mobile backhaul for co-located TIM/Vivo sites"

### Nio Fibra — regra fixa

Nio Fibra é subsidiária V.tal, absorveu 4M+ clientes ex-Oi Fibra em fev/2025. **NÃO** escrever "contracts guaranteed through January 2028" nem qualquer prazo específico de garantia contratual dos clientes — não é público-confirmado e envelhece rápido. Escrever apenas: "Its residential B2C arm Nio Fibra absorbed the 4M+ former Oi Fibra client base in February 2025."

### Portfolio approach — quando o IRR fica apertado

Deals V.tal costumam ter IRR desafiado (proprietário anchor alto, ativo core mas commodity). Quando o IRR não maximiza standalone, **usar o argumento de portfolio explicitamente**:

> "Under a portfolio-level lens, this is a strong add: legacy telecom corridor, institutional tenant with rated debt profile, low decommissioning risk over 5-10 years, and structurally difficult to replace given the sunk fiber CAPEX in the corridor. The kind of site the portfolio benefits from holding, even when the standalone IRR does not maximize."

Isso não é jogar poeira em gap financeiro — é reconhecer que ativo core em corredor telecom vale mais que a soma dos multiples individuais.

### Counterparty risk framing

V.tal tem perfil público institucional (BTG Pactual, AS8167 herdado Telemar/Oi, ~426.000 km de fibra em 2.380 municípios, 3.4M eyeballs APNIC). Escrever esse framing na íntegra no Negotiation Notes — o IC de San Diego não conhece o mercado brasileiro de fibra neutra, precisa da tradução.

### SIR obrigatório antes do IC

Deals fiber shelter **sempre** requerem SIR antes de submeter. Não porque a estrutura registral peça, mas porque:
- Confirma equipamento ativo (OLT model → estimar port count → estimar receita indireta)
- Confirma power redundancy (autonomia real do site)
- Confirma fiber-entry count (dual-homed = resiliente; single-fiber = ponto de falha)
- Documenta o layout físico pra futuras negociações de reajuste

Listar "SIR being commissioned" em Documentation Pending. Se o Lucas quiser submeter sem SIR, listar em Pontos de atenção.

### ROFR — sempre disparado em Fee Simple

Contratos V.tal (herdados de Oi Móvel S.A.) têm cláusula padrão de ROFR (right of first refusal) na venda do imóvel. **Cessão de créditos (DRS/Assignment of Rents) NÃO dispara**, mas **Fee Simple SIM**. Regra fixa: "V.tal will be formally notified with the transaction terms and given the contractual 30-day window to match or waive. Since V.tal has no operational interest in becoming a real-estate holder, refusal is the base case."

Embutir os **30 dias no Closing Expectation** — nunca "closing em Sep-15" se a notificação sai em Sep-1. Trabalhar Q4 se possível.

### Croqui do corredor telecom — exhibit obrigatório

Sempre que houver 3+ broadcasters no raio de 500m ou 2+ torres 5G próximas, gerar **croqui SVG/PNG do corredor** (sem logo APW, uso interno) como exhibit anexo. Formato: anéis de distância + emissoras como cluster + torres celulares como diamantes + eixo da avenida traçado + legenda + fontes Anatel. Salvar como `croqui_pop_L<lnum>_<cidade>.svg` + .png em /mnt/user-data/outputs.

## Levantamento de arredores (Google Earth + WebSearch)

Quando o texto se beneficiar de contexto urbano (proximidade a metrô/CPTM/rodovias, densidade, comércio, benchmark de aluguel), puxar:

- **Google Earth URLs prontas** (o Lucas costuma abrir logado na conta dele — mandar 3 níveis):
  - Site centrado 45° oblíquo (~600m): `https://earth.google.com/web/@LAT,LNG,780a,600d,35y,0h,45t,0r`
  - Zoom rasante nos rooftops (~200m, 70°): `https://earth.google.com/web/@LAT,LNG,760a,200d,35y,0h,70t,0r`
  - Raio 2km (mostra estações e arteriais): `https://earth.google.com/web/@LAT,LNG,900a,2000d,35y,0h,0t,0r`
- **WebSearch** com queries do tipo `"[rua/CEP]" "[bairro]" comércio densidade avenida` e `"[bairro]" perfil comercial vias principais`.
- Destacar no texto: distância a estações metrô/CPTM/rodovias, arteriais principais, torres concorrentes próximas (já do dossiê pré-DD), sinal de mercado (torre Claro greenfield a X metros = demanda RF ativa).

## Quick reference

| Sintoma | O que fazer |
|---|---|
| Vontade de gravar Key Notes sem abrir a planilha | NÃO. Passo Zero é obrigatório (ou fallback declarado). |
| `get_page_text` no Excel Online volta vazio | Normal (canvas). Usar o script de REST + inflate. |
| `javascript_tool` retorna `{}` | Não faz await. Guardar em `window.__X` e ler na chamada seguinte. |
| Colunas da planilha deslizadas / P,R,Z,AB,AE "vazias" | Regex das células errado. Usar `(?:\/>\|>([\s\S]*?)<\/c>)`. |
| L-number não aparece na planilha | Fallback: LOIs → SIR → contratos → Anatel → arredores. Marcar em Pontos de atenção. |
| Duas respostas para o mesmo L | Usar a de maior Id (coluna A) e sinalizar ao Lucas. |
| `save()` deu "OK" | Não confiar. Fazer readback do banco e comparar tamanho. |
| URL do Dynamics tem GUID, não L-number | Nunca assumir qual deal é. Confirmar pelo nome no chat. |
| Vários registros de Pricing Option batem | Parar e perguntar. Não escolher sozinho. |
| LOI e Pricing Option divergem em prazo (ex.: LOI 30 anos, PO 20) | Não linkar PO desatualizada. Lucas recalcula ou emite PO nova. |
| Campo "Key Notes" não encontrado | É `apwip_opportunitysummary`, não "keynotes". |
| Form×CRM divergem (pricing) | Lucas faz manual. Só preencher Key Notes. |
| Vontade de promover pro Stage 8 | NÃO. Só o Lucas, manualmente, com instrução explícita. |
| Resultado de tool volta "[BLOCKED]" | Dado sensível no retorno. Reformular para devolver só metadados (tamanho, booleanos), não o conteúdo. |
| "Cai dentro da bounding box" | Não basta. Testar ponto-em-polígono de verdade; folga pequena = indício, não prova. |
| Escrever "Credit Assignment" ou "Assignment of Credit Rights" | ERRADO. Usar **Assignment of Rents**. |
| Confundir AGL com área locada | AGL = altura em metros (SIR). Área locada = m² (contrato). |
| Deal com 2 rooftops sob 1 opp | Discriminar Site A / Site B, somar rents, listar escalation por site, checar todas as LOIs. |

## Quando o Lucas manda um lote

Baixar a planilha **uma vez só** e filtrar todos os L-numbers do lote de uma vez (trocar o filtro por `LIST.some(l=>(o.F||'').toUpperCase().includes(l))`). Depois processar **um deal por vez** no CRM, com os checkpoints de cada um.

Ao final, entregar tabela-resumo: L-number, nome, linha da planilha usada (ou fallback declarado), Pricing Option linkado (ou "manual"), tamanho do Key Notes persistido, stage. Listar os attention items que bloqueiam Stage 8 por deal, e os L-numbers do lote que **não** tinham resposta na planilha.

