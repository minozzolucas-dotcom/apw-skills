---
name: apw-stage1-quality-audit
description: >-
  Auditoria de integridade da qualificação Stage 1 da APW Brasil: varre o cohort de
  oportunidades movidas pra Stage 1 num ano (default 2026) no Dynamics 365, cruza com as
  atividades concluídas, e responde quem qualifica com critério e quem empurra Stage 1 só
  pra pontuar. Métrica o cohort (evolução p/ Stage 3, in progress, surrenders/motivos, owner
  pessoa-vs-pool, property type) E pontua a PROFUNDIDADE de cada qualificação contra a regra
  APW (proprietário/decisor · pitch completo · contato salvo), em Sólida/Rasa/Suspeita com
  evidência + scorecard por diretor. Use com "auditoria de Stage 1", "qualidade da
  qualificação", "quem qualifica sem critério", "profundidade das interações", "scorecard dos
  diretores", ou colar as views opportunity + activitypointer pedindo análise de gaming.
  Entrega PNG na marca + anexo Markdown. NÃO use pra dossiê de UM deal (apw-deal-dossier),
  forensics de UMA opp (apw-opp-activity-forensics), reporte diário (apw-reporte-crm-diario)
  nem consulta pontual (apw-dynamics-copilot).
---

# APW Stage 1 — Auditoria de Qualidade da Qualificação

Esta skill responde a UMA pergunta de gestão: **dos casos que os diretores moveram para
Stage 1 este ano, quantos foram qualificados de verdade — e quantos foram empurrados só
para pontuar?**

O CRM conta quantos Stage 1 cada diretor moveu (isso o `apw-reporte-crm-diario` já faz).
O que ele NÃO conta é se aquele Stage 1 tem lastro: se o diretor falou com o **decisor real**
do terreno/condomínio, se fez o **pitch completo**, se **salvou o contato**. A verdade dessa
qualificação vive na prosa das atividades. Esta skill lê essa prosa no cohort inteiro,
métrica o funil e pontua a profundidade caso a caso — com evidência rastreável, sempre como
**sinal para investigar, nunca como veredito**.

## A regra de qualificação real (o que estamos auditando)

Um Stage 1 só vale se o diretor:

1. **Decisor real** — falou com o **proprietário do terreno** ou com o **síndico/decisor do
   condomínio**, não com porteiro, zelador, recepção ou "o pessoal". Quem decide tem que ter
   sido tocado.
2. **Pitch completo** — apresentou o modelo APW (cessão de direitos creditórios / DRS /
   antecipação de aluguel) de forma completa e capturou a reação/objeção da contraparte —
   não "liguei, não atendeu, vou retornar".
3. **Contato salvo** — telefone/e-mail/contato do decisor registrado no CRM.

Quem bate os três tem qualificação **Sólida**. Um ou dois → **Rasa** (real mas incompleta,
coachable). Zero pilares com atividade só fina/automática → **Suspeita** (Stage 1 movido
sem lastro). A população prioritária de escrutínio é **quem foi qualificado este ano e
SEGUE em Stage 1** (não evoluiu, não foi surrendered) — mais um sinal secundário de gaming:
**surrender rápido** logo após uma qualificação rasa.

## Pipeline (2 fases)

### Fase 1 — Coleta (Claude in Chrome, Web API JSON)

Numa aba autenticada em `https://apwireless.crm.dynamics.com`, cole
`scripts/collection.js` no `javascript_tool`. O script:

1. **Descobre as colunas** lendo o `fetchxml` das duas views (não chuta nome de campo). As
   labels que o Lucas vê — "Stage 3 Completed Lease Abstractions", "Surrendered Reason",
   "Property Type", "Owner" — são mapeadas para os nomes lógicos exatos e devolvidas em
   `columns_discovered` para o Lucas conferir.
2. **Roda a view de opportunity** (Stage 1 do ano) → cohort completo.
3. **Puxa as atividades** das opps do cohort direto via `activitypointers` (`$select` com
   `description` + `_regardingobjectid_value`), em lotes de 20 opps, com dedup, **cap de
   descrição em 1000 chars** e **teto de 60 atividades por opp** (o scorer precisa de sinal,
   não do texto todo — isso mantém o payload sob controle em cohorts de 800+).

**Coleta em fatias (cohort grande).** Para não estourar o retorno do `javascript_tool`, o
`collection.js` **não devolve os dados inline**: ele guarda o JSON completo em
`window.__APW_AUDIT_STR` e retorna só um **cabeçalho** com `n_slices`, `total_opps`,
`columns_discovered` e contagem de lotes ok/erro. Em seguida:

- Rode `scripts/dump-slices.js` repetidamente, mudando o índice `I` de `0` até `n_slices-1`.
  Cada chamada devolve uma fatia (`chunk`) de ~500KB.
- **Concatene os `chunk` na ordem** e faça `JSON.parse` → salve como `raw.json` em
  `/home/claude`. Confira `columns_discovered` e `collection.chunks_err` (0 = coleta íntegra).

Se `chunks_err > 0`, alguns lotes falharam (rede/timeout) — rode de novo ou avise o Lucas que
o cohort veio parcial. **NUNCA** `read_page`/`get_page_text`/screenshot em domínio Dynamics —
só Web API JSON (regra `apw-chrome-agent-lean-compliance`).

**Views (constantes, tenant Brasil `apwireless.crm.dynamics.com`):** Opportunity (Stage 1 do
ano) `b844749b-eb6f-f111-ab0d-00224805b156` · Activity `ad83a393-ed6f-f111-ab0d-00224805b156`.
Ajuste `YEAR` e os IDs no topo do `collection.js` para auditar outro ano.

### Fase 2 — Scoring + render (local)

1. **Score determinístico:**
   ```bash
   python3 scripts/build_audit.py score raw.json audit.json
   ```
   Aplica a rubrica de `references/qualification-rubric.md` (léxico dos 3 pilares + heurístico
   de atividade substantiva), calcula as métricas do cohort, atribui o tier de cada opp e
   extrai as frases-evidência. Produz `audit.json`.

2. **Revisão forense (você, o modelo):** abra `audit.json` e leia os casos `🔴 Suspeita` e
   os `🟡 Rasa` de borderline. A regex é o primeiro filtro, não a palavra final — registro
   fino pode ser **trabalho real mal logado**, não gaming. Ajuste o `tier` e o
   `tier_reason` quando o texto justificar, sempre citando a frase. Leia a rubrica antes de
   sobrescrever. **Nunca** promova/rebaixe sem evidência no texto.

3. **Render:**
   ```bash
   python3 scripts/build_audit.py render audit.json /mnt/user-data/outputs <YYYY-MM-DD>
   ```
   Gera o **PNG** board-executivo na marca APW (`apw-brand`) + o **anexo Markdown de
   evidências** L-a-L. Apresente os dois com `present_files`. Envio do e-mail é **manual do
   Lucas** — nunca enviar/agendar sem ordem explícita.

## O que o PNG mostra (board executivo)

Layout enxuto, fundo claro / texto navy (sobrevive a paste de Outlook), uma tela:

1. **Funil do cohort:** Total S1 no ano → Evoluíram p/ Stage 3 (n, %) → Seguem em S1 (n) →
   Surrendered (n) [dos quais X rápidos]. 
2. **Property type** e **Owner (pessoa × pool)** em mini-barras.
3. **Scorecard de integridade por diretor** (o coração): Diretor · Cohort S1 · 🟢 Sólida ·
   🟡 Rasa · 🔴 Suspeita · % Suspeita · flag. Ordenado por % Suspeita desc. Outliers
   destacados (oliva = atenção). 
4. **Headline das suspeitas:** os L-numbers 🔴 com a razão de uma linha.
5. Rodapé: razão social + disclaimer "sinais para investigar, não veredito".

O detalhe — a frase-evidência por opp, o histórico de atividade, o motivo do tier — vai no
**anexo Markdown**, não no PNG. É o que torna a auditoria defensável.

## Métricas do cohort (definições)

- **Evoluiu p/ Stage 3** = campo de data de Stage 3 preenchido (a label "Stage 3 Completed
  Lease Abstractions" → nome lógico descoberto na Fase 1, tipicamente `apwip_stage3date`).
  Data preenchida = proposta enviada = evoluiu.
- **In progress / segue em S1** = sem data de Stage 3 e sem surrender reason (opp aberta).
- **Surrendered** = surrender reason preenchido (ou `statecode` perdido). Quantifique **por
  motivo** (cada valor do option set, com a contagem). 
- **Surrender rápido** = surrendered ≤ 14 dias (default, ajustável) após a entrada em
  Stage 1. Sinal de gaming quando combinado com qualificação rasa.
- **Owner** = onde a opp está HOJE: diretor (pessoa) ou pool/sistema (regex POOL). Quantifique
  os dois e, dentro de pessoa, por diretor.
- **Property type** = distribuição dos valores do campo (condomínio / terreno / rooftop /
  etc., conforme option set).

## Princípios da auditoria

- **Toda flag tem frase-evidência.** Nenhum tier 🔴/🟡 sem a citação da atividade (data +
  dono) que o sustenta. Sem evidência → não flagueia.
- **Registro fino ≠ trabalho fino.** Um Stage 1 com pouca atividade pode ser ótimo deal mal
  documentado. A skill flagueia para **verificar**, não para **condenar**. O texto manda.
- **Números exatos.** Contagens e percentuais reais do cohort, nunca arredondamento de
  impressão.
- **Outlier é relativo.** A % de suspeita de um diretor só vira flag comparada à mediana dos
  pares. Volume baixo (cohort pequeno) reduz a confiança — sinalize a incerteza.
- **Compliance.** Tudo em memória no Chrome; só o `raw.json` (cohort do Lucas, uso interno) e
  os dois artefatos finais tocam disco. Não ecoe/persista PII de contraparte (CPF, nome de
  proprietário, valor de contrato) — o anexo cita papel e frase-mínima, redige PII fora. Não
  mande dado de CRM pra ferramenta externa. Auditoria de pessoas (diretores) é dado sensível:
  o tom é factual e investigativo, não acusatório.

## Arquivos da skill

- `scripts/collection.js` — coletor Chrome: descobre colunas via fetchxml, roda as 2 views,
  junta opp×atividades com cap/dedup, guarda em `window.__APW_AUDIT_STR` e devolve o cabeçalho
  com `n_slices`. Cole no `javascript_tool`.
- `scripts/dump-slices.js` — devolve uma fatia do resultado guardado; rode `n_slices` vezes
  (índice `I` de 0 a n_slices-1) e remonte o `raw.json`.
- `scripts/build_audit.py` — `score` (raw → audit.json com tiers + métricas) e `render`
  (audit.json → PNG na marca + anexo Markdown). PNG via Chrome headless. O `render` aceita
  `--full` para detalhar também as 🟢 Sólidas no anexo (default: Sólidas resumidas em
  one-liner, evidência completa só nas 🔴/🟡).
- `references/qualification-rubric.md` — léxico dos 3 pilares, regras de tier, rollup por
  diretor e regra de outlier, guardrails anti-falso-positivo. Leia antes da revisão forense.
- `references/director-roster.md` — os 14 diretores Brasil (GUID→nome) e o regex de pool.
