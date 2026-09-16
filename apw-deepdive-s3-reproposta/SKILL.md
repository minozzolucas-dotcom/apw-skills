---
name: apw-deepdive-s3-reproposta
description: >-
  Deep dive de coaching nos Stage 3 novos e repropostas (pricing options)
  criados ontem na APW Brasil. Por deal, lê do Dynamics as atividades, o nº de
  pricing options e os dados comerciais, e devolve card denso no chat com a
  temperatura do deal, o índice de profundidade da relação com proprietário/
  síndico e onde o Lucas entra pra fechar. Norte: quão fundo o diretor entrou
  (vida, como o LL pensa dinheiro, dependência do aluguel) e que estrutura cabe
  (à vista, parcelado, compra de parcela), educando em valor do dinheiro no
  tempo. Use quando o Lucas disser "deep dive de ontem", "o que rolou nos S3/
  repropostas de ontem", "onde posso ajudar nos deals novos", "analisa os stage
  3 novos", ou passar um L/data. NÃO use para dossiê reativo de um L
  (apw-deal-dossier), reporte de produtividade (apw-reporte-crm-diario),
  forensics de atividades coladas (apw-opp-activity-forensics), pré-DD
  (apw-pre-dd-legal) nem análise de cláusula (apw-telecom-real-estate-counsel).
---

# APW Deep Dive — Stage 3 novos & Repropostas (coaching)

Varre os **S3 novos + repropostas criados ontem** e, por deal, mede **temperatura**
e **profundidade da relação** com o landlord/síndico pra apontar **onde o Lucas
entra**. Não é dossiê neutro: termina sempre num direcional de negociação.

## Pré-requisito de compliance
Siga `apw-chrome-agent-lean-compliance` — é pré-requisito, não complemento.
- Opera na **sessão autenticada** que o Lucas já tem aberta (`apwireless.crm.dynamics.com`). Nunca loga, nunca faz OAuth. Sem aba → pede pro Lucas abrir.
- **Web API/JSON via `javascript_tool`**. PROIBIDO `read_page`/`get_page_text`/**screenshot** em domínio Dynamics/M-Files/APW.
- **Read-only.** Não grava no CRM, não mexe no M-Files, não cria arquivo por default.
- Conteúdo de deal (L, PII, valores) **não** vai pra `memory_user_edits`.

## Disciplina de token (design)
- **1 job de coleta** (`references/collect.js`) puxa tudo de uma vez. Não fica fatiando chamada.
- `javascript_tool` **não aguarda Promise** → padrão **polling**: dispara o job (`window.__DD`), lê o status nas chamadas seguintes. Retorno trunca ~1500 chars → puxa o resultado em pedaços por L se precisar.
- Card **scannável, veredito primeiro**, sem preâmbulo. Deal limpo encolhe. Sem arquivo salvo (a não ser que o Lucas peça).

## Escopo de entrada
- **Default:** S3 com `stage3date` = ontem (BR) + repropostas com `createdon` = ontem (regra: `createdon BR ≠ stage3date e ≠ stage5date`; mesmo owner conta; dedup 1/opp).
- Aceita **data específica** ("deep dive de sexta") ou **L avulso** ("deep dive do L977219" → roda só ele, ignora a janela de data).

## Pipeline
1. **CRM** — `references/collect.js` (polling). Por deal traz: L, site/nome, stage, owner, tipo, **campos de aluguel/valor** (sweep `rent|aluguel|amount|value|monthly`, sem chutar nome de campo), RF Notes, **todas as atividades não-automáticas com descrição completa**, **lista/contagem de pricing options**, flag novo-S3 vs reproposta.
2. **M-Files (triagem, fase 2)** — busca o L em `mfilesus.apwip.com` e **inventaria** o que está arquivado (contrato, aditivos, matrícula, POP) vs faltando. **Não lê conteúdo de PDF** (o visualizador não expõe texto; o container não alcança o domínio). Conteúdo profundo de um contrato/matrícula → o Lucas dropa o PDF no chat, ou puxa-se o que o `apw-pre-dd-legal` já analisou. Enquanto a fase 2 não estiver provada, rode CRM-side e marque M-Files como "não verificado".
3. **Cruzamento + diagnóstico** — monta o card abaixo.

## Card por deal (template — denso)
```
L[código] · [site] · [novo S3 | REPROPOSTA] · [torreira] · [tipo]
> [1 frase: o que é + onde está a relação + onde o Lucas entra.]

🌡️ Temperatura  — [N] interações · [N] pricing options · descrições [substantivas X% | rasas] · última ativ. [data]
💰 Comercial    — aluguel [R$ exato] · torreira → [DRS ok / Programa resolve / só compra-venda] · cláusula bloqueio DRS/cessão: [sim+trecho / não visto] · docs M-Files: [ok / faltam X / não verificado]
🤝 Profundidade — Nível [0–4]: [nome]. [1 linha de evidência da atividade.]
🎯 Onde entrar  — [o que falta descobrir · o que mandar ouvir/perguntar · estrutura sugerida · frase de educação pronta]
```
Novo S3 tende a ser raso (pouca atividade, 1 pricing) — não infle. Reproposta exige mais: **por que** repreciou (LL empacou no valor? concorrente? descobriu dependência → reestrutura?) e se o M-Files tem doc novo justificando.

## Índice de profundidade (núcleo — ler descrições das atividades)
- **0 Transacional** — só ping de valor, zero pessoa.
- **1 Funcional** — sabe decisor/contato, nada pessoal.
- **2 Rapport** — entrou em vida/profissão/família; há confiança.
- **3 Financeiro** — entende como o LL pensa dinheiro: dependência do aluguel mensal, liquidez, objetivos, uso do capital.
- **4 Estratégico** — achou a alavanca (necessidade de caixa, evento de vida, aversão a risco de descomissionamento) **e** já educou em TVM / fez o pitch dos ~20% de 30 anos → caminho claro pra à vista, parcelado ou compra de parcela.

Sempre diga **o degrau** e **o que falta pra subir**. Subir de degrau = a recomendação de coaching.

## Motor de coaching
Cruza degrau × fatos comerciais e gera o bloco "Onde entrar":
- **Matriz torreira (viabilidade de estrutura):** ATC = DRS viável · SBA = Programa resolve anti-cessão · IHS/Phoenix = bloqueio real (só compra e venda). Se a estrutura buscada não casa com a torreira/cláusula → é o primeiro alerta.
- **Alavancas a caçar na escuta:** dependência alta do mensal · necessidade de caixa/evento de vida · desconforto com risco de a torre sair · desconhecimento de TVM.
- **Estrutura por sinal:** dependência alta do mensal → **comprar só uma parcela** (reduz risco do LL, mantém renda) · necessidade de caixa → **à vista** · meio-termo → **parcelado**.
- **Biblioteca de educação (frases prontas, tom de par):**
  - *"30 anos de aluguel não são garantidos — a operadora pode desativar a torre. A gente antecipa hoje, certo, no teu bolso."*
  - *"Nossa proposta é ~20% de tudo que você receberia em 30 anos — mas trazido a valor de hoje, sem o risco de o site sair antes."*
  - *"Dá pra estruturar do jeito que faz sentido pra ti: tudo agora, parcelado, ou a gente compra só uma parte do aluguel e você segue recebendo o resto."*

## Regras de análise
- **Toda afirmação rastreável** a campo do CRM ou atividade datada. Sem evidência → "sem sinal nas fontes".
- **Números exatos** de aluguel/valor (não "~6k").
- **Não inflar deal raso** nem inventar profundidade que a atividade não mostra. Deal mal documentado é, em si, um achado de coaching.
- Em **batch**, um card por deal, na ordem; ao fim, um **resumo de 1 linha** de prioridade (onde o Lucas rende mais hoje).

## Quando NÃO usar
- Pedido externo de contexto de UM L → `apw-deal-dossier`.
- Reporte de produtividade dos 14 → `apw-reporte-crm-diario`.
- Forensics de view de atividades colada → `apw-opp-activity-forensics`.
- Pré-DD registral / cláusula → `apw-pre-dd-legal` / `apw-telecom-real-estate-counsel`.

## Arquivos
- `references/collect.js` — coletor batch (polling) dos S3 novos + repropostas de uma data, com atividades e pricing. Leia antes de executar o Passo 1.
