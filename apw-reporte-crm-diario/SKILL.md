---
name: apw-reporte-crm-diario
description: >
  Reporte Diário de Produtividade do CRM Dynamics 365 Brasil da APW — consolida as
  movimentações do dia e o acumulado da semana (Stage 1, Stage 3, Repropostas,
  Atividades e Substantivas) por diretor de aquisição, com radar de metas, lista de
  L-numbers movidos, destaques do dia/semana e frase motivacional, e entrega um PNG
  pronto pra colar no e-mail. Use SEMPRE que o Lucas disser "roda o reporte de hoje",
  "reporte diário", "reporte CRM", "movimentações do dia", "produtividade dos diretores",
  ou mencionar as views, os 13 diretores Brasil, as metas semanais, ou o fechamento de um dia anterior.
  NÃO use para dossiê de deal único (apw-deal-dossier), forensics de atividades coladas
  (apw-opp-activity-forensics), nem consulta pontual ao CRM (apw-dynamics-copilot).
---

# Reporte Diário CRM Brasil — APW

Reporte de produtividade dos 13 diretores de aquisição Brasil, lido do Dynamics 365 via
Web API e entregue como **imagem PNG** na identidade APW Brasil (skill `apw-brand`).

## Como roda (pipeline)

1. **Coleta** — via **Claude in Chrome**, numa aba autenticada em `https://apwireless.crm.dynamics.com`.
   Cole `references/collection.js` no `javascript_tool`. Ele usa a sessão do Lucas, puxa tudo
   por **Web API JSON** e devolve o `data.json` (faltando só os destaques).
2. **Destaques + Leitura do dia** — o Claude preenche `destaque_dia`, `destaque_semana` e `leitura_dia` no data.json:
   - **Dia** = diretor com maior movimento HOJE (peso: Stage 3 > Stage 1 > reproposta; empate → mais substantivas no dia).
   - **Semana** = maior movimento na semana (mesmo critério). Texto **factual, sem adjetivo** ("4 Stage 1, 3 repropostas, 68 atividades (17 substantivas · 25%)").
3. **Build** — `python3 references/build_report.py data.json <saida> <YYYY-MM-DD>` → gera HTML + **PNG**.
   (PNG via Chrome headless `/opt/google/chrome/chrome` + playwright. Requer `pip install playwright`.)
4. **Entrega** — apresenta o **PNG** ao Lucas. Ele cola/arrasta no corpo do e-mail. Envio é **manual** do Lucas (nunca enviar/agendar sem ordem explícita).

> Por que PNG: o Outlook, ao colar HTML, **zera as cores do texto** (vira tudo preto). A imagem preserva a marca 100%. Não brigar com paste de HTML.

## Constantes (validadas em produção)

- **Host:** `https://apwireless.crm.dynamics.com/api/data/v9.2` (NÃO apwbrasil.crm2).
- **Views (userQuery):** Stage 1 `a020dfbe-4a3f-f111-88b4-00224805b156` · Stage 3 `50aca927-4b3f-f111-88b4-00224805b156` · Pricing `e85d5310-8c42-f111-88b4-6045bd07461c` (todas entidade `opportunities`, exceto pricing = `apwip_pricingoptions`).
- **13 diretores:** GUIDs no `collection.js`. Excluir sempre pools/system e qualquer owner fora dos 13.
  **Bruna Matos removida em 24/07/2026** (desligamento) — GUID fora do `collection.js` e `N_DIR=13` no `build_report.py`. Ao entrar/sair diretor, mexer nos DOIS arquivos.
- **Campos de data ("dia" = este campo no dia / "semana" = este campo na semana):**
  - Stage 1 → `apwip_stage1_obtainedleaseeconomics`
  - Stage 3 → `apwip_stage3date`
  - Pricing → `createdon`
- **Pricing lookup da oportunidade:** `_apwip_opportunityid_value` (com "id"). O L-number vem da opp (`apwip_opportunityautonumberid`).
- **Owner efetivo (S1/S3):** owner direto; se for pool/system, cai pro `_apwip_stage1owner_value` / `_apwip_stage3owner_value`.
- **Reproposta (v2):** usa `_apwip_stage3owner_value` + `_apwip_stage5owner_value` (quem moveu o estágio) e `_ownerid_value` (dono atual). Campo de stage5 owner é **farejado** (o schema pode não tê-lo com esse nome).

## Fechamento de dia anterior (retroativo)

As views são **snapshot ao vivo** — rodar hoje traz também o que já entrou hoje. Para fechar um dia
passado (ex.: "fecha ontem"), no `collection.js`: fixar `ALVO=<YYYY-MM-DD>`, cortar
`FIM=<ALVO+1>T03:00:00Z` e **descartar** S1/S3 com data de estágio `> ALVO` e pricing com
`createdon(BR) > ALVO`. Passar `ALVO` como 3º argumento do `build_report.py` (o pace do radar
recalcula sozinho). O acumulado da semana fica menor que o do reporte de hoje — isso é **correto**,
não erro; avisar o Lucas se ele for comparar os dois lado a lado.

**Drift:** duas coletas com minutos de diferença dão números diferentes. Sempre carimbar a hora do
corte ao entregar o PNG parcial e, se o Lucas pedir o reporte de novo no mesmo dia, **recoletar** —
nunca reaproveitar o data.json da rodada anterior.

## Regras de negócio (definições do Lucas)

- **Reproposta** (regra v2 — **por titularidade**, não por data; substituiu a regra de data em ago/2026):
  - Atribuição sempre pelo **dono atual da opp** (com fallback de pool → `_apwip_stage3owner_value`).
  - **Deal herdado** (Stage 3 **e** Stage 5 movidos por *outra* pessoa) → **toda** pricing do dono atual é reproposta.
  - **Deal que o próprio dono moveu** para Stage 3/5 no **ano corrente** → a **1ª pricing é orgânica** (não conta); da **2ª em diante, conta**.
  - Dedup: no máx. 1 crédito por opp por dia. **Meta: 4/semana**.
  - **Dependência:** precisa de `_apwip_stage3owner_value` e `_apwip_stage5owner_value`. O collection.js **fareja** o campo de stage5 owner (tenta com, cai pra sem). Se `stage5owner` não existir no schema, a regra usa **só o S3 owner** para decidir herdado/próprio — validar `_meta.stage5owner_disponivel` na 1ª rodada e, se vier `"verificar"`, confirmar o nome real do campo no Dynamics.
  - ⚠ **Não validada contra dados reais ainda** — a 1ª rodada com a regra v2 deve ser conferida deal-a-deal pelo Lucas antes de virar número oficial de meta.
- **Atividade substantiva** = descrição com conteúdo estratégico: `len ≥ 180` OU (`len ≥ 140` e ≥2 sinais). Sinais: valor/número, contraparte (síndico, proprietário, operadora…), próximo passo, objeção/info. Independe do canal.
  - **Filtro de automática (v2):** descarta a atividade quando descrição **e** subject são automáticos. `AUTO_ANY` (casa no texto todo): Mail Merge, "automatic activity", "template using the", "completed automatically by the", **XL Calculator**. `AUTO_START` (casa no início): begin work, **Pricing Desk**, **MANAGEMENT TASK**, "Create Verbal/Written proposal", moved to stage, workflow, reminder. Isso tira do denominador o ruído de sistema que a v1 ("net-inclusive") deixava passar.
  - ⚠ **LIMITAÇÃO CONHECIDA (auditada em 18/08/2026).** O critério mede **tamanho de texto**, não conteúdo. O ramo `len ≥ 180` ignora os sinais → colagem de WhatsApp e corpo de formulário passam como substantivas (15 falsos positivos em 42 no dia). E notas curtas e densas (<140 car., 2+ sinais) são rejeitadas (10 no dia) — ex.: *"AGE aprovada por unanimidade. Proposta R$ 1.100.000 à vista, IRR 16,81. Enviada LOI"* (123 car.). Na prática **premia quem cola transcrição e pune quem sintetiza**. **Serve para pegar o extremo** (quem só escreve "FUP"), **não para ranquear diretores entre si.** Revisão do critério pendente (rodar 30 dias com regra alternativa `(≥2 sinais e ≥45 car.) OU (≥300 car. e ≥1 sinal)` + sinal de valor com magnitude R$ 5+ dígitos, antes de mudar meta com o time).
- **Metas/diretor (semana):** S1 3 · S3 2 · Repropostas 4 · Atividades 100 (20/dia) · **Substantivas 35% (7 de 20/dia)**.
- **Radar (time):** "no ritmo" se atual ≥ ritmo esperado × meta semanal (ritmo = dias úteis decorridos ÷ dias úteis da semana). "Hoje" = atual do dia ≥ meta diária (meta semanal ÷ dias úteis).

## Tom e formato

- **Dia separado da semana.** Sem troféu. Dois destaques (dia + semana), factuais, sem juízo de valor.
- Radar no topo (verde/vermelho, barra com marcador de ritmo). Substantivas como **barra visual** com marcador da meta 35% (sem coluna de "falta" textual).
- Lista de **L-numbers** movidos por diretor (azul = hoje).
- **Leitura do dia** no rodapé (substituiu a frase motivacional, descontinuada em 24/07/2026): 1–3 frases do Claude lendo o número do dia — o que o dado mostra, quem destoa, o que olhar amanhã. Factual e direto, sem coaching, sem adjetivo vazio, sem citação de guru. Se `leitura_dia` vier vazio, o bloco simplesmente não é renderizado.
- Identidade visual: skill `apw-brand`.

## Anti-travamento / compliance (apw-chrome-agent-lean-compliance)

- Tudo por **Web API JSON**. PROIBIDO `read_page`/`get_page_text`/**screenshot** em domínio Dynamics.
- Paginar via `@odata.nextLink` (guard < 20). NÃO usar `$select` junto de `userQuery` (dá 400) — ler do payload da view.
- Auth 401/403 → reabrir aba, esperar, 1 retry; senão parar e avisar (não inventar dado).
- Não persistir dados do CRM em arquivo além do necessário pro build.

## 100% automático (futuro)

Rodar sem o Lucas exige App Registration (Entra) + Application User no Dynamics (auth de serviço) + agendador + Microsoft Graph (Mail.Send). Isso é **integração de dados do CRM** → requer autorização do **Risk Management Officer** da APW antes de construir. Sem aval, manter o fluxo "um comando por dia".
