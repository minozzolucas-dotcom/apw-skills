---
name: apw-closing-call-brief
description: >-
  Use SEMPRE que o Lucas colar a transcrição da call semanal de closing /
  processing da APW (revisão deal-a-deal com o jurídico — Michelle, Anderson,
  Márcia, Diogo — e os diretores) JUNTO com a lista/print da Processing View
  "Closing Milestones" do Dynamics (códigos L), e pedir "resumo deal-a-deal",
  "principais demandas, próximos passos e responsáveis", "casos com potencial de
  fechamento rápido", "faz a referência com os códigos das oportunidades do
  CRM", "quem ficou com o quê", ou "monta o briefing da call de fechamento".
  Gatilhos: transcrição de reunião de closing + screenshot/lista de L-numbers,
  menção a pró-rata, anuência SBA, ATA registrada, LAIR, wire, estágio final,
  próxima leva. NÃO use para reunião genérica/negociação com contraparte (use
  apw-meeting-brief), forensics de atividades de uma opp (apw-opp-activity-
  forensics), nem consulta solta ao CRM (apw-dynamics-copilot).
---

# APW Closing Call Brief

## Overview
A call semanal de closing da APW é uma varredura deal-a-deal: o jurídico e os diretores percorrem a **Processing View "Closing Milestones"** discutindo um caso de cada vez. O Lucas grava, o ASR cospe uma transcrição crua (sem pontuação, sem speakers, nomes de deal mangados), e ele manda **junto com o print/lista da view** para que cada caso falado seja amarrado ao seu **código L do CRM**.

**Princípio central:** a entrega não é um resumo da reunião — é um **tracker de fechamento deal-a-deal, cada deal colado ao seu L**, organizado pelo **tier de prontidão que o próprio time declara**, com resumo / demandas / próximo passo / responsável / bloqueio por caso. O cruzamento transcrição ↔ L-codes é o coração do deliverable.

Esta skill **reusa a disciplina de ASR e extração da `apw-meeting-brief`** (não duplicar — consultar `references/asr-corrections.md` de lá) e **carrega `apw-brand`** para cor/tipografia do dashboard.

## Inputs (sempre os dois)
1. **Transcrição crua** da call de closing (ASR, pior caso).
2. **Print ou lista da Processing View** — colunas: Opportunity Name (com o L), Closing date, Probability, Opportunity Stage, RF Expert, Owner (diretor), Paralegal Owner, Tower Co, City.

Verdades operacionais que governam o cruzamento:
- **Nem todo deal da lista é discutido** na call.
- **Nem todo deal discutido está na lista/print** (deals novos ou abaixo da dobra) → vira flag "falta o L".
- **Stage 99 = já fechado/ganho** — não é "pendente".

## Workflow

### 1. Ler a transcrição inteira uma vez
Antes de extrair qualquer coisa. Monte o elenco (diretores, jurídico, fechamento) e o roteiro de deals. Corrija ASR conforme lê; registre no glossário, nunca limpe em silêncio. Termo incerto → `[?]`, nunca chute. Erros recorrentes desta call (além do catálogo da meeting-brief):

| ASR | É | Pista |
|---|---|---|
| "DBSA" | **SBA** | torreira que faz remanejamento |
| "aire" / "lair" | **LAIR** (pedido) [?] | "solicitar o aire", "pedido de lair" |
| "ESW" | planilha de forecast | preparada pelo time do Anderson, ajustada com o Close do Newton |
| "nifute" | **input** (sinal da SBA) | "esse nifute da SBA é importante" |
| "Virante de Ipirituba" | **Mirante de Pirituba** | nome de deal mangado |
| "Fontaine" / "Fontana" / "Aditivole" | Fontainebleau / Fontana de Tivoli | nomes de prédio |
| "miguezada / migué" | sumir/enrolar após receber o deal | risco de não-devolução |

### 2. Montar o roster de deals discutidos e casar com os L
Para cada deal falado, ache o L na Processing View por **nome + cidade + tower co**. Nome mangado → fuzzy match e marque `[?]` se não tiver certeza. **Nunca invente um L.** Sem match na lista → flag explícito "falta o código L, me passa".

### 3. Extrair por deal (5 campos)
- **Resumo** — situação real do caso em 1–2 linhas.
- **Demandas / pontos em aberto** — o que a contraparte exige, cláusula travando, divergência de área/aluguel.
- **Próximo passo** — a ação concreta.
- **Responsável** — diretor (Owner) + paralegal + quem do jurídico + quem assumiu na call.
- **Bloqueio / risco** — o asterisco que mata o deal depois.

### 4. Tier pela fala do próprio time
O time **declara o tiering** no fim da call ("os três mais avançados são…", "estágio final", "próxima leva", "deixa pra depois"). Use a fala deles, **não chute a sua**. Tiers padrão:
- **Tier 0 — Praticamente fechados** (wires da semana).
- **Tier 1 — Estágio final** (aguardando confirmações: anuência, ATA, conselho).
- **Tier 2 — Próxima leva** (fase anterior; SBAs recentes).
- **Tier 3 — Parado / radar** (passivos, blocker, deprioritizado).

### 5. Capturar o transversal
- **Mapa político (sensível, só interno):** diretor insistente, deal já perdido, quem precisa de ajuda pra dar má notícia, fraqueza admitida.
- **Números globais do pipeline:** "X possíveis, meta Y, Z encaminhados/pagos/avançados".
- **Notas de processo:** regras tipo "enviar todas as anuências SBA mas não cobrar", "flag Newton no LAIR pra evitar pushback da Paulina".

### 6. Entregar
Salvos em `/mnt/user-data/outputs/`:
1. **Markdown interno** (`briefing-closing-call-interno.md`) — todos os tiers, plano de ação consolidado (tabela Ação | Deal-L | Responsável | Prazo), riscos 🔴🟡, números, mapa político, flags de L faltante, casos da lista não discutidos, glossário.
2. **Dashboard HTML dark** (`briefing-closing-call-dashboard.html`) — cards por deal coloridos por tier (verde/amarelo/laranja/vermelho; roxo = sem L), plano de ação, riscos, KPIs do pipeline. Estética dark editorial APW (vars do `apw-brand`).

No **chat**, entregar primeiro: estado do pipeline (números) → tiers com deal-a-deal conciso → 2 pedidos de ação ao Lucas (os L que faltam + os `[?]` a confirmar).

**Não gerar versão externa por padrão** — a call de closing é interna (sem contraparte na sala). Só montar "ata limpa" se o Lucas pedir explicitamente, e perguntar pra quem vai.

## Regras fixas
- **Cross-ref é o produto.** Cada deal discutido sai com seu L ou com o flag "falta o L".
- **Nunca inventar L nem prazo.** "Sem prazo definido" e "[a confirmar]" são respostas honestas.
- **Tier vem da fala do time**, não da sua intuição.
- **Stage 99 = fechado**, não pendente.
- **`[?]` para tudo que o ASR deixou ambíguo** — termo, nome de deal, nome de pessoa.
- **Sempre listar os dois grupos de borda:** deals na lista não discutidos, e deals discutidos sem L.
- **Mapa político e fraquezas só no interno.** Nunca na ata externa.

## Erros comuns
- Resumir a reunião em vez de entregar deal-a-deal → perde o cruzamento, que é o ponto.
- Forçar um nome mangado num L errado por excesso de confiança → sempre `[?]` na dúvida.
- Tratar Stage 99 como pendência → eles já fecharam.
- Esquecer os deals discutidos que não estão no print → o Lucas precisa saber quais L faltam.
- Promover um "talvez" a "fechado" → tier 0 é só o que o time chamou de concluído/wire.

## Glossário (semente — expandir por call)
pró-rata (SBA usa 3 meses; negociável p/ 1 mês = +30 dias) · anuência (SBA/operadora) · ATA registrada (assembleia aprovando a operação) · LAIR (pedido) · ESW (forecast financeiro) · CIR · e-notariado · remanejamento (relocação de site pela torreira) · averbação pré-monitória · DRS (Direito Real de Superfície) · CDC (Cessão de Direitos Creditórios) · "vacinar" (encaminhar wire).
