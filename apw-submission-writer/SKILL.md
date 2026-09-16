---
name: "apw-submission-writer"
description: "Converte resumos de deals telecom da APW Brasil em textos de Investment Opportunity / Submission padronizados em inglês, prontos para o IC da Radius. ANTES DE ESCREVER, SEMPRE puxa a linha do deal na planilha-mãe do SharePoint \"Stage 6(aceite verbal) ou 7(LOI recebida) – Informações da Negociação\" (respostas do Microsoft Forms dos diretores) — é a fonte primária de dados, mesmo que o Lucas já tenha colado algo. Acione SEMPRE que o Lucas mandar dados de um deal APW — L-number, linhas de planilha, PDF do Forms, transcrição de áudio — ou pedir \"cria o submission\", \"monta o investment opportunity\", \"faz as key notes desse deal\", \"gera o texto\". Também acione com DRS, Surface Right Deed, Cessão de Créditos, Assignment of Rents, Compra e Venda, Fee Simple, TBSA, ROFR, redução SBA em contexto APW/telecom/torre. O output segue formato fixo (Overview, Financials, Negotiation Notes, Documentation, Timeline) e termina com \"Pontos de atenção antes de submeter\" em português."
---

# APW Submission Writer

Skill para converter resumos de deals da APW Brasil em textos de **Investment Opportunity** padronizados em inglês, prontos para submission ao IC da Radius.

## Quando acionar

- Lucas manda um L-number e pede o submission / as Key Notes
- Lucas cola linha(s) de planilha de submission da APW (com Lnumber, TowerCo, operadora, aluguel etc.)
- Lucas manda PDF do Microsoft Forms do deal preenchido
- Lucas transcreve por voz a descrição de um deal e pede pra montar o texto
- Lucas pede explicitamente: "cria o texto", "monta o submission", "faz pra esse caso", "gera o investment opportunity"
- Qualquer menção a Lnumber (L12345) + dados de deal

---

# FONTE DE DADOS PRIMÁRIA — planilha do Forms (OBRIGATÓRIA)

**REGRA DURA: antes de escrever uma única linha do Investment Opportunity, abrir a planilha-mãe e puxar a linha do deal.** Vale mesmo quando o Lucas já colou dados no chat — o que ele cola costuma ser parcial ou de memória. A planilha é a resposta que o próprio diretor de aquisição deu no Microsoft Forms, e é ela que o IC audita.

Se por qualquer motivo a planilha não puder ser lida (sessão deslogada, extensão do Chrome fora do ar, arquivo movido), **dizer isso ao Lucas antes de escrever** e só seguir com o que ele colou se ele mandar seguir — registrando no topo dos "Pontos de atenção" que o texto foi feito sem a planilha.

## Identificação do arquivo

| Item | Valor |
|---|---|
| Nome | `"Stage 6(aceite verbal) ou7(LOI recebida) – Informações da Negociação".xlsx` |
| Site (web) | `/personal/lminozzo_apwbrasil_com_br` (OneDrive do Lucas em `apwireless-my.sharepoint.com`) |
| UniqueId (sourcedoc) | `b45b8db5-a7bc-4154-a201-ac714a5fc1e6` |
| Drive item id | `01VJ5HVY5VRVN3JPFHKRA2EANMOFFF7QPG` |
| Link | https://apwireless-my.sharepoint.com/:x:/r/personal/lminozzo_apwbrasil_com_br/_layouts/15/doc2.aspx?sourcedoc=%7BB45B8DB5-A7BC-4154-A201-AC714A5FC1E6%7D |
| Estrutura | 1 aba (`sheet1`), linha 1 = cabeçalho, dados a partir da linha 2, colunas **A..BC** (55) |
| Chave do deal | coluna **F** = L-number no formato `L884789` |

## Como ler (Claude in Chrome, sem screenshot)

Domínio corporativo → vale a `apw-chrome-agent-lean-compliance`: **zero screenshots**. E atenção: o Excel Online renderiza em **canvas** — `get_page_text` e `read_page` **não retornam a grade**. Não perder tempo tentando.

O caminho que funciona: navegar para o link (só para ter a sessão autenticada na origem `apwireless-my.sharepoint.com`) e, via `javascript_tool`, baixar os bytes do arquivo pela REST do SharePoint e descompactar o XLSX na própria página com `DecompressionStream('deflate-raw')`. Nada sai para disco, nada aparece em imagem.

Passo 1 — navegar para o link acima (qualquer `action=`).

Passo 2 — rodar no `javascript_tool` (trocar o `LNUM`):

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

Passo 3 — ler o resultado em fatias (o retorno do `javascript_tool` trunca em ~1.000 chars):

```javascript
window.__APW.length + " | " + window.__APW.map(x=>x.row+":"+x.F+" "+x.G).join(" ; ")
```
```javascript
(()=>{const r=window.__APW[0];return ['F','G','H','L','P','R','S','W','X','AO','AN']
  .map(c=>c+"="+String(r[c]||'').replace(/\s+/g,' ').slice(0,120)).join(' | ');})()
```

Ler campo a campo em blocos de 8–12 colunas. Os campos longos (T, U, V, AD, AS) puxar um por vez, inteiros — são eles que viram a narrativa.

**Se voltar mais de uma linha para o mesmo L-number:** usar a de **maior Id (coluna A)** e avisar o Lucas de que há resposta duplicada, listando o que mudou entre elas. Não fundir as duas em silêncio.
**Se voltar zero linhas:** avisar antes de escrever. O deal pode ter L-number digitado errado no form (`L 884789`, `884789`, `L88478`) — tentar busca por trecho numérico e por nome do deal (coluna G) antes de desistir.

## Mapa das colunas → campos do Investment Opportunity

| Col | Pergunta do Forms (resumida) | Vira o quê no texto |
|---|---|---|
| A | Id da resposta | controle (desempate de duplicata) |
| B / C | Hora de início / conclusão | data da resposta (serial Excel) — contexto de quão fresco é o dado |
| D / E | Email / Nome do respondente | diretor de aquisição dono do deal |
| **F** | **Lnumber** | chave de busca / cabeçalho |
| G | Nome do Deal | cabeçalho `Investment Opportunity – Lxxxxx \| Nome` |
| H | Cidade e Estado | 1º parágrafo + Location |
| I | Deal veio por qual meio | **Lead Source** (Timeline) |
| J | Em que estágio a opp foi assinada a você | contexto de Timeline |
| K | Quando a opp/lead foi assinada a você | **Lead Assigned** (Timeline) |
| L | Tipo da negociação | tradução FIXA: DRS → Surface Right Deed; Cessão de Créditos → Assignment of Rents; Compra e Venda → Fee Simple |
| M | Metragem da área locada (último contrato/aditivo) + área total do terreno/laje | **Leased Area** (e base do check de área vs. matrícula) |
| N | Número de andares do edifício | **Building: N-story** (só rooftop) |
| O | IPTU anual (só compra e venda) | **Annual Property Tax (IPTU)** |
| P | Towerco / torreira | **TowerCo** |
| Q | TBSA Capex Fee / verba TBSA | **DESCONTINUADO — ignorar.** Não escrever CAPEX Fee nem "TBSA Project" mesmo se a coluna vier preenchida |
| R | Operadora(s) | **Tenant(s)** |
| S | Tecnologias | **Technologies** (junto com R) |
| T | Razão de o site não ter 5G / há sites 5G ao redor | bloco **Technology Context** |
| U | Região de cobertura + pontos de interesse (nomes próprios) | **2º parágrafo (cobertura)** — insumo, não texto final |
| V | "Peculiaridades do Deal" | **Negotiation Notes** — matéria-prima da narrativa estratégica |
| W | Área de localização do site (Urbana/Rural) | **Location: Urban / Rural** |
| X | Tipo de landlord no contrato | **Landlord** (Individual / Legal Entity / Condominium) |
| Y | Se rural, tem CCIR/CAR/ITR | Documentation Status + gatilho de pré-DD |
| Z | Site teve redução recente de aluguel | **Recent Rent Reduction** |
| AA | Quanto de redução | idem (mostrar antes e depois) |
| AB | Tem todos os contratos e aditivos | **Documentation Status** |
| AC | Considerou verba de advogado para o proprietário | Financials / ponto de atenção se vazio em DRS ou C&V |
| AD | Histórico SBA (quanto a SBA pediu, quanto a APW fechou) | **Negotiation Notes** — aplicar o wording fixo da regra SBA |
| AE | Expectativa de Submission | **Timeline** (costuma vir vazia — ver abaixo) |
| AF | Expectativa de Fechamento | **Closing Expectation — vai no Deal Overview**, nunca só no Timeline |
| AG | Matrícula limpa e em nome do proprietário | pontos de atenção / pré-DD |
| AH | Nº e endereço da matrícula batem com o contrato | pontos de atenção / pré-DD |
| AI | Matrícula tem coordenadas georreferenciadas | pontos de atenção / pré-DD |
| AJ | Aluguel líquido (comprovante bancário) | **Net Rent (Bank Proof)** |
| AK | Aluguel bruto | **Gross Rent** |
| AL | Aluguel pelo cálculo exato | **Exact Calculation Rent** |
| AM | Valor do investimento | **Investment Amount** (base do Implied Multiple) |
| AN | Prazo do deal | **Term (years)** |
| AO | Tipo do site | **Site Type** (Rooftop / Greenfield / Lattice / Monopole) |
| AP | IRR mostrado na calculadora | **IRR (Calculator)** — aplicar a regra da casa decimal |
| AQ | Condições de pagamento | **Payment Structure** |
| AR | Fotos atualizadas do site (equipamento ativo) | Documentation Status |
| AS | Quais documentos você já possui | **Documentation Status** |
| AT | Objetivo do preenchimento do form | contexto (submission nova × reproposta × atualização) |
| AU | Contrato/recebimento em nome de 1 ou mais PFs | Landlord + gatilho de gross-up de IR e de assinatura múltipla |
| AV | Quando foi firmado o último contrato/aditivo | **Last Amendment** |
| AW | Mês de reajuste pelo indexador | **Escalation Month** |
| AX | É competição? | Negotiation Notes |
| AY | Termos da proposta da concorrência | Negotiation Notes (justifica prazo não-padrão) |
| AZ, BA, BB, BC | duplicatas/instruções órfãs do form | **colunas mortas — 0 preenchimento em 114 respostas. Ignorar.** |

### O que a planilha NÃO tem (buscar em outra fonte, não inventar)

- **Escalation Index** (IGP-M / IPCA / IPC-FIPE / INPC) → contrato/aditivos (`apw-rent-escalation`)
- **Lease Commencement / Lease Expiration** e runway contratual → contrato/aditivos
- **Tenancy** (nº de operadoras no site) e faixas em MHz → base Anatel (`apw-erb-towerco-triage`)
- **Coordenadas** → contrato, matrícula ou CRM
- **Implied Multiple** → calcular (AM ÷ aluguel do POP)

## Regras de parsing da planilha (aprendidas na marra)

1. **Datas voltam como serial do Excel.** `AF=46265` não é número, é data. Converter: `new Date(Date.UTC(1899,11,30)+serial*86400000)`. Vale para B, C, K, AE, AF, AV.
2. **Valores de aluguel vêm sem padrão de separador.** Exemplo real: `AJ=506192` (= R$ 5.061,92) e `AK=5.1148100000000003` (= R$ 5.114,81). O diretor digita como quer e o Excel converte. **Nunca reportar o número cru.** Normalizar, cruzar AJ × AK × AL entre si, e checar contra o POP/comprovante bancário. Se não fechar, `[to be confirmed]` + ponto de atenção.
3. **IRR (AP):** aparece tanto já com decimal (`17.8` = 17,8%) quanto sem (`162` = 16,2%; `1674` = 16,74%). Uma casa decimal implícita quando vier inteiro. Nunca reportar 162%. Ambíguo → `[to be confirmed]`.
4. **Campos que vêm vazios com frequência nas respostas recentes** — checar sempre e cobrar do diretor em vez de assumir: **P (Towerco)**, **R (Operadora)**, **U (cobertura/pontos de interesse)**, **Z (redução de aluguel)**, **AE (expectativa de submission)**, **AB (contratos e aditivos)**. AE em branco é regra, não exceção — puxar a data com o Lucas.
5. **Q (verba TBSA)** aparece preenchida em respostas antigas. **Está descontinuada** — não migrar para o texto em nenhuma hipótese.
6. **AX × AZ** e **AP × BC**: só a primeira de cada par é viva. AZ/BA/BB/BC estão zeradas.
7. Quebras de linha nas respostas longas (V, AD, AS) vêm como `_x000D_` — já limpas pelo script; se aparecer, remover.
8. **Células vazias auto-fechadas quebram o parser ingênuo.** O Excel grava célula vazia como `<c r="O112" s="15"/>`. Um regex do tipo `([^>]*)\/?>(?:...)?` casa o `/` dentro do grupo e continua consumindo até o `</c>` da célula SEGUINTE — resultado: a célula vazia **rouba o valor da vizinha** e todas as colunas seguintes deslizam. Sintomas típicos: colunas críticas (P, R, Z, AB, AE) aparecendo falsamente vazias e colunas numéricas com valores absurdos (`O=63`, `AD=46254`). O regex correto, já embutido no script acima, é:
   ```
   /<c r="([A-Z]+)\d+"([^>]*?)(?:\/>|>([\s\S]*?)<\/c>)/g
   ```
   **Sanity check obrigatório antes de escrever o texto:** conferir 2–3 valores lidos contra o que se espera (aluguel na casa dos milhares, L-number na coluna F, cidade legível em H). Se algo vier deslocado, dumpar o XML cru da linha e conferir o regex antes de seguir.

## Ordem de prevalência quando as fontes divergirem

Planilha (Forms) × CRM (Dynamics) × documentos (contrato, matrícula, POP) × Anatel:

1. **Documento vence a planilha** em fato jurídico e em valor pago (contrato, aditivo, matrícula, comprovante bancário/POP).
2. **POP define a TowerCo** — se o comprovante mostrar torreira diferente da coluna P, vale o POP (cessão já consumada), e a divergência entra no Negotiation Notes.
3. **Anatel** vence em tecnologia/faixa/tenancy; a coluna S serve de sanity check.
4. **Planilha vence o CRM** em intenção comercial (prazo, investimento, condições, expectativa de fechamento), porque foi o diretor que declarou.
5. Qualquer divergência relevante **entra nos "Pontos de atenção"** com as duas versões lado a lado. Nunca escolher em silêncio.

---

## Princípios fundamentais

1. **Idioma**: texto principal sempre em **inglês**. "Pontos de atenção antes de submeter" sempre em **português**.
2. **Tom**: institucional, IC-ready, sem floreio. Lucas é o gestor que defende o deal — o texto precisa antecipar perguntas do comitê.
3. **Honestidade**: nunca inventar dados que não estão no form. Faltou → "pending", "to be confirmed", ou ponto de atenção.
4. **Narrativa estratégica**: quando o ativo tiver diferenciais (5G ativo, multi-tenant, landlord recorrente, landmark urbano, DRS sem vedação, prazo competitivo), reforçar no Negotiation Notes — não enterrar como bullet técnico.

## Tradução de tipos de negociação (REGRA FIXA)

| Português (form) | Inglês (output) |
|---|---|
| DRS / Direito Real de Superfície / Direito de Superfície | **Surface Right Deed (DRS)** |
| Cessão de Créditos | **Assignment of Rents** |
| Compra e Venda | **Fee Simple Purchase** ou **Fee Simple Interest (ground only)** |
| Híbrido (cessão + DRS) | só usar se Lucas pedir explicitamente — caso contrário tratar como o tipo final que vai prevalecer |

⚠️ **NÃO usar "Credit Assignment", "Surface Rights Assignment", "Service Right Deed"**.

## TowerCos / Torreiras (REGRA FIXA)

- **ATC** → "ATC (American Tower)" ou "ATC" depois da primeira menção
- **SBA** → "SBA"; **IHS** → "IHS"
- **TBSA** → "TBSA (Torres do Brasil)". TowerCo comum. **NÃO existe mais "TBSA Project" e NÃO existe mais CAPEX Fee**
- **Highline** → "Highline" (Phoenix foi integrada à Highline → IHS)
- **Z-Sites**, **Winnity**, **GlobalSites**, **DT Towers Brasil**, **PTI**, **Torres do Brasil**, **ITC**, **LMITC**
- **Vivo / Telefônica** (como TowerCo, não como tenant)

Para torreiras menos conhecidas, incluir nota institucional curta após o overview.

## Estrutura padrão do texto

```
## Investment Opportunity – [Lnumber] | [Nome do Deal]

[Parágrafo 1: tipo de negociação + prazo + TowerCo + tipo de site + operadora(s) + tecnologias + cidade/estado]

[Parágrafo 2: cobertura — bairro, pontos de interesse com nomes próprios, contexto urbano/rural]

[Se aplicável: bloco "Technology Context"]

**Deal Overview**
- TowerCo / Site Type / Building (se rooftop) / Leased Area / Landlord / Location
- Tenant(s) & Technologies / Tenancy
- Lease Commencement / Lease Expiration / Last Amendment
- Escalation Index / Escalation Month
- Recent Rent Reduction
- Annual Property Tax (IPTU) — só Fee Simple
- **Closing Expectation:** (REGRA FIXA — sempre neste bloco)

**Financials**
- Net Rent (Bank Proof) / Gross Rent / Exact Calculation Rent / Adjusted Rent
- Investment Amount / Implied Multiple / Term / IRR (Calculator) / Payment Structure

**Negotiation Notes**
[narrativa estratégica]

**Documentation Status**
[docs já obtidos]

**Timeline**
- Lead Source / Lead Assigned / Submission Expectation
[Closing Expectation NÃO vai aqui]

---

**Pontos de atenção antes de submeter:** [em português]
```

## Parágrafo de cobertura/entorno (REGRA FIXA — sempre fazer)

O 2º parágrafo é obrigatório e CONSTRUÍDO ATIVAMENTE a partir da coluna U + mapa/ortofoto/Street View — não só transcrito do form. Descrever mix do entorno (residencial × comercial × misto × industrial), pontos de interesse com NOMES PRÓPRIOS (shopping, estação, avenidas-eixo, igreja/escola/hospital), densidade e contexto urbano/rural. Fechar ligando o entorno à tese de churn. Com coordenadas, cruzar Anatel e checar sites vizinhos.

## Contagem de andares (rooftop)

"Building: N-story" → CONTAR os pavimentos pelas fotos da fachada, não chutar (a coluna N vem preenchida em menos da metade dos casos). Casa de máquinas e térreo comercial não contam como pavimento-tipo. Sem confiança → `[to be confirmed]`.

## Regras automáticas (CHECKLIST)

1. **Gross vs Net Rent**: se diferentes, explicar (taxas/IR). Se iguais e Lucas quiser destacar — manter ambos.
2. **Exact Calculation vs Net Rent**: gap > 5% → pontos de atenção. Pode ser cenário IGPM→IPCA (clássico Claro).
3. **TBSA (descontinuado)**: sem "TBSA Project", sem CAPEX Fee. Prazo < 30 anos em deal TBSA continua exigindo justificativa própria.
4. **IRR** — regra da casa decimal implícita (ver parsing acima).
5. **Prazo não-padrão (< 30 anos)**: explicar racional no Negotiation Notes — competição direta (coluna AY), landlord benchmark effect, aprovação em assembleia.
6. **SBA + rent reduction** (coluna AD): "as per SBA request, a X% rent reduction was applied". Mostrar valor antes e depois.
7. **ROFR**: incluir como condition no closing — "subject to the expiration of [TowerCo]'s right of first refusal".
8. **Datas em inglês**: April 30, 2026 (não 30/04/2026).
9. **Valores em R$**: formato R$ X,XXX.XX (padrão americano do IC).
10. **Operadoras com tecnologias**: "Claro (3G/4G/5G)", "Vivo (4G and 5G)".
11. **Fee Simple**: "fee simple purchase of the ground only". Prazo perpétuo — "Perpetual (Fee Simple)".
12. **Technology Context via Anatel** (sempre que houver endereço ou coordenada): rodar `anatel_lookup.py` da `apw-erb-towerco-triage`, escrever número da estação, classificação, tecnologias e faixas em MHz. 3500 MHz ativo = capital recém-desembolsado → argumento de baixo churn.
13. **Runway contratual**: dizer até quando corre o contrato e quantos anos restam na assinatura.
14. **ROFR em DRS**: antecipar que a preferência não é disparada — "No ROFR condition therefore applies at closing."
15. **Condições precedentes de título** (gravame, retificação de área, regularização fiscal): em prosa no Negotiation Notes e refletidas no Closing Expectation. "Being worked in parallel", nunca omitido.

## Detecção de inconsistências (pontos de atenção)

Sempre levantar em PT no final quando detectar:

- Net Rent ≠ Gross Rent ≠ Exact Calculation com gap > 5%, ou valores da planilha com separador ambíguo
- Colunas críticas vazias no form: P (Towerco), R (operadora), U (cobertura), AE (expectativa de submission), AB (contratos/aditivos)
- Matrícula não limpa / sem coordenadas georreferenciadas (AG, AI)
- Número/endereço da matrícula não bate com o contrato (AH)
- Faltam contratos/aditivos (AB)
- Last Amendment (AV) com data suspeita ou conflitando com o mês de reajuste (AW)
- Submission/Closing apertados demais (< 5 dias)
- Verba de advogado (AC) em branco quando deal é DRS/compra e venda
- Operadora/tecnologia inconsistente entre o form e a Anatel
- SBA rent reduction sem confirmação interna (AD sem menção ao Murilo)
- Cidade/estado com erro de digitação
- Documentação (AS) muito enxuta pra valor do deal
- Form indica competição (AX) mas não traz termos da concorrência (AY)
- **IRR em branco ou tabela de custas incompleta** — não submeter
- **Menção herdada a "TBSA Project" ou CAPEX Fee** — remover
- **Resposta duplicada do mesmo L-number na planilha** — dizer qual foi usada e o que mudou
- **LOI classificada no M-Files como "(F) Signed Offer Agreement" mas sem assinatura** — abrir o PDF e conferir
- **LOI vencida ou vencendo** ("Offer Expires")
- **Matrícula entregue como visualização** ("PARA SIMPLES CONSULTA") em vez de certidão
- **Gravame ativo na matrícula**, mesmo já quitado economicamente
- **Área locada do contrato incompatível com a matrícula** (coluna M vs. descrição registral)
- **Anexo de croqui/planta do contrato ausente**
- **Tenancy 1** — antecipar o argumento mitigante
- Lead Source (I) / Lead Assigned (K) não identificáveis

## Narrativa estratégica (quando reforçar)

- **Landmark / institutional landlord**: "institutional landlord + central [cidade] + 5G multi-tenant = low churn / high strategic value"
- **Multi-tenant ativo**: densidade de receita + redundância de risco
- **Cluster strategy**: APW já comprou sites vizinhos / mesmo landlord (citar L-numbers)
- **5G multi-banda**: "fully deployed multi-band 5G capability, confirming relevance within operator network densification strategy"
- **DRS sem vedação**: "DRS without restriction clauses, providing additional flexibility"
- **Landlord recorrente**: "trusted counterparty with proven closing record"
- **Tower critical for TX/repeater**: "decommissioning risk extremely low"
- **Highline tentando reduzir e LL não concorda**: "clear window of opportunity for APW to secure current rent levels"
- **Site único na cidade**: "1 of N sites in the municipality"

## Comportamento esperado

- **Sempre** declarar em uma linha, antes do texto, que puxou a linha X da planilha (e a data da resposta). Uma linha só, sem cerimônia.
- **Nunca** começar com preâmbulo tipo "Aqui está...". Já entregar com `## Investment Opportunity – ...`.
- **Sempre** terminar com pontos de atenção em PT (se não houver gap: "Nenhuma inconsistência relevante identificada no form").
- **Após o texto**, oferecer UMA melhoria opcional, curta.
- **Nunca** emojis no texto institucional. Pode 1-2 na conversa lateral com o Lucas.
- Campo crítico faltando → `[to be confirmed]`, nunca invenção.

## Quando Lucas mandar vários deals juntos

Puxar a planilha **uma vez só** (o script carrega o arquivo inteiro) e filtrar os vários L-numbers em memória. Processar um por um, mantendo o padrão. Ao final, oferecer pacote consolidado.

## Handoff

Texto pronto e aprovado → gravar no Dynamics é a `apw-crm-key-notes-writer` (que também confere a linha da planilha antes de gravar). Análise registral de documento → `apw-pre-dd-legal`. Cláusula → `apw-telecom-real-estate-counsel`.

