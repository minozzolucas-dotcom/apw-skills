---
name: apw-performance-patterns
description: >
  Benchmark dos 14 diretores de aquisição da APW Brasil no Dynamics 365 — funil de
  conversão completo (S1 orgânico → S3 orgânico + Repropostas → Stage 8 → Stage 99) +
  volume/profundidade de atividades — para identificar os PADRÕES que separam top de
  low performers. Calcula a taxa de conversão oficial ((S3 orgânicos + repropostas) →
  S8), S8 → S99, quantos S1 pra gerar 1 S3, atividades substantivas, e fecha com
  forense qualitativa: amostra atividades de deals convertidos dos tops vs mortos dos
  lows e extrai diferenças de abordagem. Use SEMPRE que o Lucas pedir "padrões dos top
  performers", "compara os diretores", "taxa de conversão do funil", "quantos Stage 1
  pra um Stage 3", "conversão pra Stage 8/99", "o que os tops fazem diferente",
  "benchmark dos diretores", "orgânico vs reproposta". NÃO use para reporte diário
  (apw-reporte-crm-diario), auditoria de Stage 1 (apw-stage1-quality-audit), forensics
  de UMA opp (apw-opp-activity-forensics) nem consulta pontual (apw-dynamics-copilot).
---

# APW Performance Patterns — Top vs Low Performers

Benchmark do funil de conversão + comportamento dos 14 diretores de aquisição Brasil,
lido do Dynamics 365 via Web API (sessão autenticada, Claude in Chrome), para responder
uma pergunta: **o que os top performers fazem diferente dos low performers?**

Esta skill NÃO é o reporte diário (fluxo do dia/semana contra meta). Ela é análise
estrutural de período longo: conversão, eficiência e padrões de abordagem.

## Definições de métricas (regras do Lucas — não improvisar)

### Produção
| Métrica | Definição operacional |
|---|---|
| **S1 orgânico** | Opp com `apwip_stage1_obtainedleaseeconomics` no período; owner efetivo S1 = diretor (owner direto; se pool/system → `_apwip_stage1owner_value`) |
| **S3 orgânico** | Opp com `apwip_stage3date` no período; owner efetivo S3 = diretor. **Orgânico = o diretor foi quem moveu pra S3.** |
| **Reproposta (não-orgânica)** | Pricing option criada pelo diretor (`ownerid` da pricing = diretor) em opp cujo S3 **não foi movido por ele** (`stage3owner ≠ diretor`) OU pricing criada em dia BR diferente de `stage3date` e `stage5date` (regra validada do reporte diário). Dedup: 1 por oportunidade por diretor no período (mais recente). Pricing no mesmo dia do estágio = proposta original, não conta. |
| **Produção de proposta** | S3 orgânicos + Repropostas |

### Funil (taxas de conversão)
| Taxa | Cálculo |
|---|---|
| **S1 → S3** | Cohort: dos S1 orgânicos do diretor no período, % que atingiu S3 (por qualquer owner). Reportar também o inverso legível: "X Stage 1 pra gerar 1 Stage 3". |
| **Proposta → S8 (taxa oficial)** | Cohort: das opps com proposta do diretor no período (S3 orgânico OU reproposta dele), % que atingiu Stage 8. Uma opp que recebeu reproposta de mais de um diretor conta no denominador de cada um (mérito compartilhado) — sinalizar quando isso for relevante no N. |
| **S8 → S99** | Cohort: das opps do diretor que atingiram S8, % que atingiu S99 (fechado e fundado). |
| **S1 → S99 (end-to-end)** | Bônus de leitura, não métrica oficial. |

**Cohort vs fluxo:** default é **cohort** (acompanhar o destino dos deals que entraram no
período), porque fluxo (S8 do período ÷ S3 do período) mistura safras e distorce quando o
volume varia. MAS cohort exige **janela de maturação**: deals que entraram em S3 há menos
tempo que o lead time mediano S3→S8 ainda não tiveram tempo de converter. Regra prática:
1. Calcular lead time mediano S3→S8 e S8→S99 do dataset inteiro primeiro.
2. Reportar a conversão do cohort **maduro** (entrada + lead time mediano ≤ hoje) como
   número oficial, e o cohort verde separado como "em maturação".
3. Mostrar o ratio de fluxo do período só como sanity check, rotulado como tal.
Sempre comunicar o survivor bias e o N de cada célula. **N < 8 → mostrar o número mas
marcar como estatisticamente frágil; não ranquear diretor por célula frágil.**

### Comportamento (atividades)
| Métrica | Definição |
|---|---|
| Atividades concluídas | `activitypointer` completadas no período, owner = diretor |
| Substantiva | Regra do reporte diário: descrição `len ≥ 180` OU (`len ≥ 140` + ≥2 sinais: valor/número, contraparte, próximo passo, objeção/info). Workflow tasks automáticas descartadas. |
| % substantivas | substantivas ÷ total |
| Atividades por deal ativo | total ÷ nº de opps distintas tocadas |
| Atividades por proposta | total ÷ produção de proposta (custo de esforço por proposta gerada) |

## Pipeline de execução

### 0. Escopo com o Lucas (máx 2 perguntas, só se não estiver dito)
- Janela da análise (default: **últimos 12 meses**, cohort maduro conforme regra acima).
- Tenant Brasil (default) — 14 diretores, GUIDs do `collection.js` do reporte diário.

### 1. Descoberta do campo Stage 8 (obrigatória na primeira execução)
O dicionário confirma `apwip_stage1_obtainedleaseeconomics`, `apwip_stage3date`,
`apwip_stage99closedandfundeddeal`. O campo de data do **Stage 8 não está validado**.
Descobrir via metadados antes de qualquer query de funil:
```js
fetch(`${window.location.origin}/api/data/v9.2/EntityDefinitions(LogicalName='opportunity')/Attributes?$select=LogicalName,AttributeType&$filter=startswith(LogicalName,'apwip_stage')`,
  {headers:{'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'}})
  .then(r=>r.json()).then(d=>d.value.map(a=>a.LogicalName))
```
Mostrar os candidatos ao Lucas e confirmar qual é o S8 (e o S5, usado na regra de
reproposta). Depois de confirmado uma vez, gravar o nome no bloco "Constantes validadas"
desta skill (editar o SKILL.md) pra nunca mais perguntar.

### 2. Coleta — tudo Web API JSON, em memória
Ler `references/coleta.md` para o plano de queries completo. Espinha dorsal:
1. Opps com S1, S3, S8 ou S99 na janela (+ owners efetivos por stage).
2. Pricing options da janela (`createdon`, `ownerid`, `_apwip_opportunityid_value`) →
   classificar orgânica vs reproposta contra as datas de stage da opp mãe.
3. `activitypointer` concluídas da janela por diretor (descrição p/ substantivas).
4. Lead times S3→S8 e S8→S99 (só deals com ambas as datas; comunicar survivor bias).

Compliance (herdado de apw-dynamics-copilot + apw-chrome-agent-lean-compliance, inegociável):
- Sessão autenticada do Chrome; **nunca** OAuth próprio ou credencial armazenada.
- **PROIBIDO** screenshot/`read_page`/`get_page_text` em domínio Dynamics — só `javascript_tool` Web API.
- Paginar via `@odata.nextLink` (guard < 20). Não misturar `$select` com `userQuery`.
- Dados brutos ficam em memória. Nenhum dump com nome de proprietário/valor/PII em disco.
  Persistir no máximo agregados por diretor aprovados pelo Lucas.

### 3. Cálculo e ranking
- Montar a tabela mestre: diretor × {S1 org, S3 org, repropostas, produção, S1→S3,
  proposta→S8, S8→S99, S1→S99, atividades, substantivas, %subst, ativ/proposta} + N de cada célula.
- **Score composto para ranking** (não usar métrica única): normalizar por z-score e
  ponderar conversão oficial (peso 3), S8→S99 (2), S1→S3 (1), produção absoluta (1).
  Volume sem conversão não é top; conversão com N frágil também não.
- Separar quartis: **Top** (Q1) e **Low** (Q4) pelo score. Mostrar a régua inteira,
  não só os extremos.

### 4. Forense qualitativa — a parte das "abordagens"
Aqui está o valor real da skill. Com tops e lows identificados:
1. Amostrar 3–5 deals **convertidos** (chegaram a S8/S99) de cada top performer e
   3–5 deals **mortos ou estagnados** pós-proposta de cada low performer.
2. Puxar as descrições das atividades desses deals (em memória) e ler como o
   apw-opp-activity-forensics leria: sequência de abordagem, cadência de follow-up,
   como tratam objeção, quando e como sobem proposta, profundidade da relação com o
   proprietário/síndico (vida, como pensa dinheiro, dependência do aluguel), uso de
   reproposta como ferramenta vs. como desespero.
3. Extrair padrões contrastivos: "tops fazem X antes da proposta; lows fazem Y".
   Cada padrão precisa de **evidência** (deal + comportamento observado, sem citar PII
   desnecessária) — nunca afirmar padrão sem exemplo.
4. Correlações quantitativas de apoio: % substantivas vs conversão oficial,
   atividades/proposta vs conversão, mix orgânico/reproposta vs conversão. Correlação
   com N=14 é indicativa, não prova — dizer isso explicitamente.

### 5. Entrega
Relatório denso **no chat**, estrutura fixa:
1. **O funil do time** (agregado): números absolutos + taxas de cada etapa.
2. **Tabela mestre por diretor** (com N e flags de fragilidade).
3. **Ranking + quartis** (score composto, mostrando os componentes).
4. **Padrões top vs low** — o coração: 4–7 padrões contrastivos com evidência.
5. **Leitura estratégica pro Lucas**: onde ele intervém (coaching individual,
   redistribuição de carteira, regra de processo), 3 próximos passos.

PNG/dashboard na marca (apw-brand) só se o Lucas pedir — e só com agregados, sem PII.

## Constantes validadas (atualizar aqui conforme confirmação)
- Host: `https://apwireless.crm.dynamics.com/api/data/v9.2`
- S1: `apwip_stage1_obtainedleaseeconomics` · S3: `apwip_stage3date` · S99: `apwip_stage99closedandfundeddeal`
- S5: **[CONFIRMAR na 1ª execução]** · S8: **[CONFIRMAR na 1ª execução]**
- Pricing: entidade das views do reporte (`apwip_pricingoptions`), FK `_apwip_opportunityid_value`
- Owners efetivos: owner direto; pool/system → `_apwip_stage1owner_value` / `_apwip_stage3owner_value`
- 14 diretores: GUIDs do `collection.js` da skill apw-reporte-crm-diario (fonte única)

## Tom
Português direto, análise de mesa — o que os números dizem, o que não dizem (N, bias,
maturação), e onde o Lucas age. Sem troféu, sem adjetivo gratuito sobre diretor: padrão
+ evidência. Nunca simular dado que a query não retornou.
