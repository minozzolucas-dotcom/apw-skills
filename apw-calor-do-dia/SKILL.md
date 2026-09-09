---
name: apw-calor-do-dia
description: >
  Reporte INTERNO de gestão que cruza o que MOVEU de estágio no dia (S1/S3/Repropostas)
  com o CONTEÚDO real das atividades, mais um radar de "calor" (deals avançando) e uma
  seção de "qualificações com bandeira" — S1 novos onde a torreira/estrutura indica que a
  APW NÃO fecha (IHS em rooftop/cessão, TBSA em condomínio, PTI/Phoenix com cláusula,
  vedação/exclusividade). A "última atividade" mostrada é sempre a do DONO ATUAL da opp
  (não de diretor que saiu), com data. Entrega PNG + PDF na marca APW. Use quando o Lucas
  pedir "calor do dia", "compilado de atividades de ontem", "o que tem de quente nos deals",
  "reporte de gestão do dia", "atividades dos códigos que moveram", "tem torreira que não
  fechamos nas qualificações". NÃO use para o reporte de produtividade por diretor
  (apw-reporte-crm-diario), forensics de uma opp (apw-opp-activity-forensics), nem dossiê de
  deal único (apw-deal-dossier).
---

# APW — Calor do Dia (reporte interno de gestão)

Complementa o `apw-reporte-crm-diario`: aquele mede **volume/produtividade**; este mede
**substância e risco** — o que os deals que moveram realmente são, o que está quente, e
quais qualificações são armadilha (torreira/estrutura que a APW não monetiza).

## Pipeline (igual ao reporte diário — F12, sem screenshot)

1. **Coleta** — `references/collect_calor.js` no console (F12) da aba autenticada em
   `https://apwireless.crm.dynamics.com`. `ALVO_IN` no topo: `""` = **hoje** (default); `"YYYY-MM-DD"`
   para retroativo. Baixa `calor_<data>.json`. Puxa: L-codes que moveram S1/S3/Reprop **+ dono atual**
   de cada opp; **atividades regarding** dessas opps (histórico, com owner por atividade); **todas as
   atividades concluídas no dia** (statecode=Completed, actualend no dia) pelos 13 diretores.
2. **Build** — `python3 references/build_calor.py calor_<data>.json <saida>` → gera 2 HTML e renderiza
   **PNG (resumo) + PDF (completo)** via Chrome headless (playwright, `/opt/google/chrome/chrome`).
3. **Entrega** — **PNG = resumo executivo** (painel + calor + bandeiras + situação), colável no e-mail.
   **PDF = documento completo** com o §5 HISTÓRICO COMPLETO (todas as atividades, cronológico, texto
   integral). Separados de propósito: com o histórico embutido o PNG passa de 40 000 px / 16 MB e o
   Outlook não renderiza. Envio é manual do Lucas.

> Sempre perguntar ao Lucas se quer executar via **agente (Claude in Chrome)** ou **snippet F12**
> antes de rodar (regra transversal APW).

## Regras de negócio (o que define o report)

### Última atividade = do DONO ATUAL
Para cada deal movido, a "situação" mostra a última nota **escrita pelo dono atual** da opp
(quem moveu o estágio hoje), com **data**. Se não houver nota do dono atual, o campo mostra
**em vermelho** de quem/quando é a última nota disponível — nunca passar nota de ex-diretor
(ex.: Giuseppe) como se fosse o estado atual do deal.

### Histórico completo de atividades — TODOS os deals que moveram
Seção que despeja **todas as atividades com conteúdo** (não-auto) de cada deal que moveu no
dia — **S1, S3 e repropostas** — em ordem cronológica (mais antiga → recente), com data, autor,
tipo e texto integral. É onde a gestão lê "o que foi falado". Atividade de quem **não é o dono
atual** vem marcada em vermelho. Deals de **pool** entram normalmente (todas as pools incluídas),
com selo POOL.

### Qualificações com bandeira — matriz de torreira APW
Cobre **todos** os estágios (S1, S3, repropostas), com prioridade visual pra S1 novos. Heurística sobre **nome do deal + descrições não-automáticas**
(nunca texto de template). Bandeiras:

| Sinal | Bandeira | Razão |
|---|---|---|
| IHS / CSS / Centennial em rooftop/cessão | 🟡 | IHS **só compra terreno** — cessão/DRS não fecha |
| TBSA / Torres do Brasil em **condomínio** | 🔴 | Cessão **travada** |
| TBSA fora de condomínio | 🟡 | Rotear via **DRS** (só fecha se não-condomínio) |
| PTI / Phoenix / QMC | 🟡 | Confirmar **cláusula anti-agregador** |
| vedação / anti-cessão / anti-DRS / exclusividade telecom no texto | 🔴 | Trava contratual |
| SBA / GTS / Highline | 🟢 (não sinaliza) | Fecha normal |
| **ATC / American Tower** | **não sinaliza** | APW **fecha** ATC; no texto costuma ser **pagador**, não detentora — não confundir |

A detecção é **heurística** — o report diz explicitamente "confirmar detentora e trilha no CRM".
Não cravar dead-end; sinalizar para o diretor checar.

### Calor (deal avançando)
Sinais fortes: AGE aprovada, aceite/LOI, assinatura/DocuSign, proposta/contraproposta, valor
cheio (R$ com milhar), edital/matrícula, desconto/majoração, síndico/proprietário interessado.
Ordena por nº de sinais. O trecho quente exibido também respeita a regra do dono atual.

### Substantiva / Auto
Mesmo critério do reporte diário: substantiva = descrição estratégica (≥180 car. ou ≥140 com
2+ sinais). Auto (Mail Merge, "begin work", "assigned", "moved to stage", "response generated
by…") é descartada do conteúdo — só polui o report de gestão.

## Constantes

- 13 diretores (Bruna Matos fora). GUIDs no `collect_calor.js`.
- Views: Stage 1 `a020dfbe-4a3f-f111-88b4-00224805b156` · Stage 3 `50aca927-4b3f-f111-88b4-00224805b156` · Pricing `e85d5310-8c42-f111-88b4-6045bd07461c`.
- Owner efetivo: se owner da opp é pool/system, cai pro `_apwip_stage1owner_value`/`_apwip_stage3owner_value`.
- Janela concluídas: `actualend` entre `ALVO T03:00Z` e `ALVO+1 T03:00Z`; `statecode eq 1`.

## Anti-travamento / compliance

- Tudo por Web API JSON. PROIBIDO screenshot/read_page/get_page_text em domínio Dynamics
  (ver `apw-chrome-agent-lean-compliance`).
- Paginar por `@odata.nextLink` (guard 40). Auth 401/403 → reabrir aba, 1 retry, senão parar.
- Não persistir dados do CRM além do JSON necessário pro build.

## Evolução futura

- Ler a **detentora/torreira** de campo estruturado da opp (quando o nome do campo for
  confirmado no CRM) em vez de heurística de texto — elimina falso positivo/negativo.
- Cruzar com `apw-erb-towerco-triage` (base Anatel) pra derivar trilha por coordenada.
- Puxar atividade do **lead de origem** quando o S1 novo não tem atividade no nível da opp.
