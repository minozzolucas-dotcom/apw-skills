---
name: apw-atividades-semana
description: >
  Auditoria das atividades CONCLUÍDAS pelos diretores de aquisição da APW Brasil num período
  (dia, semana ou intervalo) — lê o conteúdo de cada atividade, uma a uma, e responde se o
  diretor está trabalhando de verdade ou só registrando: classifica cada atividade (Real /
  Tentativa / Rasa / Suspeita / Automática), detecta fechamento em rajada, texto copiado entre
  opps, tarefa vencida fechada em lote e disparo em massa, cruza com avanço de estágio (S1/S3/
  reproposta) e SEMPRE destaca o que foi concluído no dia atual. ANTES DE RODAR, SEMPRE pergunta
  período, diretor(es) e modo de execução. Use com "atividades concluídas", "atividades da
  semana", "o que os diretores fizeram", "estão trabalhando mesmo?", "analisa as atividades da
  [diretora]", "auditoria de atividades", "conteúdo das atividades de [período]", "o que foi
  concluído hoje". NÃO use para o reporte diário de volume (apw-reporte-crm-diario), deals que
  moveram no dia (apw-calor-do-dia), profundidade de qualificação S1 (apw-stage1-quality-audit)
  nem forensics de UMA opp (apw-opp-activity-forensics).
---

# APW — Atividades concluídas: auditoria por diretor (v2)

Pergunta que a skill responde: **o diretor está trabalhando de verdade ou só alimentando o CRM?**
Complementa a suíte: `apw-reporte-crm-diario` mede volume; `apw-calor-do-dia` mede os deals que
moveram; esta lê **todas** as atividades concluídas no período, inclusive das opps que não moveram.

## §1 Perguntas obrigatórias — SEMPRE, antes de rodar

Regra do Lucas (22/09/2026): **sempre perguntar**, mesmo que o pedido pareça completo. Usar o
`ask_user_input_v0` (1 toque no celular), numa chamada só, com as 3 perguntas:

1. **Período** — de quando até quando? Opções: `Hoje` · `Semana corrente (seg → hoje)` ·
   `Semana passada (seg → sex)` · `Outro período`. Se o pedido já trouxe datas, a 1ª opção é
   exatamente essas datas (ex.: `14/09 → 22/09 (o que você pediu)`).
2. **Diretor(es)** — `Todos os 14` · `Um(a) específico(a)` · `Alguns`. Se escolher específico,
   o nome vem na resposta seguinte; aceitar nome parcial ("Regina", "Kamilla").
3. **Execução** — `Agente (Claude in Chrome)` · `Snippet F12` (regra transversal APW).

Só depois das respostas: preencher `PERIODO_INI`, `PERIODO_FIM` e `DIRETORES` no
`references/collect_semana.js` e rodar/entregar.

## §2 Dia atual — SEMPRE identificar

Toda saída tem um bloco **"Concluídas no dia atual"**, por diretor.
- Dia atual = **hoje (BRT)**. Se o período não inclui hoje, é o **último dia do período**
  (rotular como tal).
- Marcar **backlog fechado hoje**: atividade criada há ≥7 dias ou com prazo vencido há >3 dias,
  concluída no dia atual. Sem texto = 🔴 (limpeza de pendência pra inflar número).
- No JSON cada atividade traz `hoje: true/false`; no Markdown aparece **HOJE** na lista.

## §3 Pipeline

1. **Coleta** — `references/collect_semana.js` no console (F12) da aba autenticada em
   `https://apwireless.crm.dynamics.com`, ou via agente com `javascript_tool` (mesmo código).
   Baixa `atividades_<ini>_a_<fim>[_diretor].json`. Traz: atividades concluídas (statecode=1,
   `actualend` na janela 00h→23h59 BRT) com hora completa de criação/conclusão/prazo, quem criou,
   tipo e nome do regarding, texto sem HTML (cap 5.000); movimentações S1/S3/reproposta do período;
   opps enriquecidas (L, nome, dono atual, fase). Tudo num run só.
2. **Classificação** — `python3 references/audit_atividades.py <json> <saida>` → Markdown
   (scorecard, veredito, dia atual, evidências, lista uma a uma) + `_classificada.json`.
3. **Leitura humana (obrigatória)** — o Claude lê o texto integral de todas as não-automáticas,
   diretor por diretor (em lotes se passar de ~1.500), e corrige o tier quando o texto contradiz a
   regra. A regex é o 1º filtro, não o veredito.
4. **Entrega** — no chat: scorecard por diretor + veredito + 2–3 evidências textuais (L, hora,
   trecho) + bloco do dia atual. Arquivo MD completo como anexo. PNG/PDF na marca (opcional):
   `python3 references/build_semana.py <json> - <saida>` — aceita o JSON v2 direto.

## §4 Classificação de cada atividade

Ordem de avaliação: Automática → Suspeita → Real → Tentativa → Rasa.

| Tier | Regra |
|---|---|
| ⚪ Automática | mail merge, "begin work", "assigned", "moved to stage", workflow; criada por sistema sem texto; e-mail com o mesmo assunto em ≥10 envios do mesmo diretor (disparo). Fica fora do denominador. |
| 🔴 Suspeita | texto idêntico (normalizado) em ≥3 registros distintos · fechada em rajada (≥5 em 10 min) **sem texto** · backlog (criada ≥7d ou vencida >3d) **sem texto** · sem vínculo e sem texto. "Sem texto" = descrição < 60 car. |
| 🟢 Real | substantiva (≥180 car., ou ≥140 com 2+ sinais) com contraparte nomeada ou 2+ sinais; ou ≥80 car. com 2+ sinais. Sinais: valor, contraparte (síndico, proprietário, administradora, herdeiro, advogado…), próximo passo, objeção/negociação/interesse. |
| 🟡 Tentativa | não atendeu, caixa postal, recado, sem retorno, número errado; ou texto operacional ≥60 car. sem avanço claro. Trabalho legítimo, mas raso. |
| 🟠 Rasa | sem texto útil ou texto genérico ("follow-up", "contato"). |

Rajada **com** texto real não é suspeita — vira nota "registrada em lote" (logar no fim do dia é
normal).

## §5 Veredito por diretor (heurístico — a leitura decide)

- 🔴 **Indício de maquiagem de CRM** — Suspeitas ≥ 20% das úteis.
- 🟡 **Volume baixo** — úteis < 40% da mediana do time → confirmar se trabalha fora do CRM.
- ✅ **Trabalho real registrado** — Real ≥ 35% e Suspeita < 10%.
- ⚠️ **Volume sem substância** — úteis ≥ mediana e Real < 20%.
- 🟡 **Misto** — o resto; decidir pelas evidências.

Contexto no scorecard: opps distintas tocadas, S1/S3/reproposta movidos no período, dias com
registro, atividades após 19h e no fim de semana, concluídas no dia atual.

**Ressalva sempre dita na entrega:** o CRM mede **registro**, não trabalho. Diretor que negocia no
WhatsApp e não registra aparece como fraco — isso é problema de gestão, mas é outro problema.

## §6 Constantes

14 diretores (Bruna Matos fora desde 24/07/2026; Marcia Mangiulli desde 25/08/2026):

| GUID | Diretor |
|---|---|
| 70a07063-6fdf-e311-8265-00155d00fe04 | Jose Daniel Ramos |
| c336d752-e6fb-ed11-8849-000d3a5a8269 | Regina Silveira |
| b5ece3de-6c3c-ee11-bdf4-000d3a5a8e5c | Kamilla Rosa |
| 0f5c2d0c-d6d4-e911-a9a8-000d3a360ed5 | Felipe Porto |
| 342e4168-9660-e911-a997-000d3a360ed5 | Fabio Boturao |
| 2d3010fa-61f4-ed11-8848-000d3a5a82bf | Aline Sanzi |
| f41da072-58a6-ed11-aad1-000d3a5a8baa | Victoria Navarro |
| bd19844f-8b38-ee11-bdf4-6045bd095340 | Daiane dos Santos |
| cb48e1a0-4959-ee11-be6f-000d3a317ead | Gisele Tognolo |
| edbec271-d59d-ef11-8a6a-0022480985f3 | Andressa Bueno |
| bea2794a-97c3-ef11-b8e9-000d3a3355b9 | Roana Reboredo |
| d49fdec3-f849-ef11-a317-000d3a5be4ff | Carolina Brentzel |
| 06a1eeda-93d7-f011-8543-6045bd0a09fc | Aline Felix |
| 8e616ea9-8d8a-f111-ab0f-70a8a5b0fc4c | Marcia Mangiulli |

- Views: Stage 1 `a020dfbe-4a3f-f111-88b4-00224805b156` · Stage 3 `50aca927-4b3f-f111-88b4-00224805b156` · Pricing `e85d5310-8c42-f111-88b4-6045bd07461c`.
- Owner efetivo das movimentações: se o dono da opp é pool/system, cai pro `_apwip_stage1owner_value`/`_apwip_stage3owner_value`.
- Reproposta = pricing option criada no período fora da data de S3/S5 (não-orgânica).
- Janela: `actualend ge <ini>T03:00Z` e `lt <fim+1>T03:00Z` — nunca "agora" (não vaza o dia seguinte).

## §7 Compliance / anti-travamento

- Só Web API JSON. PROIBIDO screenshot/read_page/get_page_text em domínio Dynamics
  (`apw-chrome-agent-lean-compliance`).
- Paginação `@odata.nextLink` (guard 40). 401/403 → reabrir aba, 1 retry, senão parar.
- Select de atividade com fallback automático (se algum campo não existir, cai pro básico).
- Não persistir dados do CRM além do JSON necessário pra análise.

## Histórico

- **v1 (16/09/2026)** — relatório por diretor com todas as opps trabalhadas (movidas + só atividade);
  2 snippets (collect + enrich).
- **v2 (22/09/2026)** — vira auditoria: perguntas obrigatórias (período, diretor, execução), bloco
  do dia atual, classificação atividade a atividade, janela fechada, hora completa, enrich embutido,
  `audit_atividades.py`. Este SKILL.md substituiu uma versão corrompida no repo (tinha o conteúdo da
  skill `nano-banana-edit`). `enrich_opps_template.js` fica como legado para JSON v1.
