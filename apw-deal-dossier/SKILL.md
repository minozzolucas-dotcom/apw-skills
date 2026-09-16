---
name: apw-deal-dossier
description: >-
  Monta o dossiê completo de uma oportunidade da APW Brasil a partir de UM
  único código L. Acessa o Dynamics 365 CRM (dados e atividades da opp) E o
  Outlook (a thread de emails do caso), cruza as duas fontes e devolve no chat
  um briefing rápido e scannável: o que o deal é, o que foi negociado, com
  quem, a situação atual, divergências em aberto e o próximo passo. Use SEMPRE que o Lucas mandar um
  código L pedindo "contexto", "o que rolou nesse caso", "monta o dossiê", "me
  situa nesse deal", "o que foi negociado", "resumo do Lxxxxx", ou encaminhar
  um email de asset management/torreira pedindo ajuda num caso. Use também quando ele colar uma
  thread de email de um deal e pedir para entender a situação — a skill usa a
  thread como atalho e complementa com o CRM. NÃO use para dados brutos do CRM
  sem narrativa (apw-dynamics-copilot), forensics só de atividades coladas
  (apw-opp-activity-forensics), análise de cláusula contratual
  (apw-telecom-real-estate-counsel), nem a rotina diária SBA
  (apw-sba-daily-routine).
---

# APW Deal Dossier

Skill para o Lucas (APW Brasil) reconstruir, **a partir de um único código L**, a história completa de uma oportunidade — cruzando o que o Dynamics 365 CRM sabe com o que os emails do Outlook contam.

## O problema que isso resolve

Toda hora chega um pedido tipo o da Marcelina: *"@Lucas, @Diogo, podem ajudar?"* num caso que o Lucas não tem na cabeça. Pra responder, ele teria que: abrir o CRM, achar a opp, ler os campos, abrir o Outlook, caçar a thread, ler 8 emails encadeados, e só então entender que o L1256097 é um DRS em Sorocaba com aluguel reduzido pra R$6k e uma divergência aberta sobre isenção de reajuste. Isso são 15 minutos de garimpo manual por caso.

Esta skill faz isso sozinha. Input: `L1256097`. Output: o dossiê pronto, com a divergência já isolada e o próximo passo claro.

O **CRM dá o esqueleto** (stage, owner, valor, tipo de deal, RF Notes) e as **atividades + emails dão a carne** (o que foi efetivamente negociado, com quem, o que travou, o que está pendente). Nenhuma das duas fontes sozinha conta a história inteira — o valor da skill é a fusão.

---

## Princípios de operação (não-negociáveis)

Esta skill toca dados sensíveis da APW (PII de proprietários, valores de contrato, threads internas) e roda dentro do contexto de compliance de IA da empresa. Antes de qualquer coisa, **siga a skill `apw-chrome-agent-lean-compliance`** — ela é pré-requisito, não complemento.

1. **Sessão autenticada do navegador, nunca login próprio.** Você opera dentro das abas que o Lucas já tem abertas no Chrome (Dynamics e Outlook). Você não autentica, não armazena credencial, não faz OAuth. Se a aba não existir, peça pro Lucas abrir.

2. **Texto estruturado antes de pixel.** Ordem de ferramentas: `javascript_tool` (Web API / extração via DOM) → `get_page_text` → `read_page` → `read_network_requests` → `computer` (screenshot, último recurso). Em domínio APW / Dynamics / Outlook / Microsoft 365, **screenshot é proibido** sem confirmação explícita do Lucas no chat. Ver `apw-chrome-agent-lean-compliance`.

3. **Dados em memória, não em disco.** O processamento acontece no JS do navegador ou no contexto da conversa. Por padrão você **não** cria arquivos com dados brutos do CRM/email. O dossiê vai no corpo do chat. Só gere arquivo se o Lucas pedir — e mesmo assim, o arquivo final, não o dump.

4. **Não persista PII em memória de longo prazo.** Não use `memory_user_edits` para gravar códigos L específicos, nomes de proprietários, valores. Padrão de uso tudo bem; conteúdo de deal, não.

---

## Os dois caminhos de entrada

**Caminho A — código L sozinho (principal).** O Lucas manda `L1256097` ou "monta o dossiê do L1256097". A skill busca tudo: CRM + Outlook. É o fluxo completo.

**Caminho B — thread de email colada ou encaminhada (atalho).** O Lucas cola/encaminha uma thread (como o email da Marcelina) e pede contexto. A skill extrai o código L do assunto da thread (`L1256097_NP_ACF203515_MARILENE VERDUGO_SBA` → `L1256097`), usa a thread como fonte de email já pronta, e **complementa** indo ao CRM buscar o esqueleto estruturado. Não precisa varrer o Outlook de novo — a thread já está na mão.

Se o Lucas mandar **vários códigos L** ("monta dossiê do L1256097, L1245001 e L1233890"), faça **um dossiê por código**, na ordem que ele mandou, cada um completo e independente. Não misture casos.

Se não conseguir extrair um código L de jeito nenhum (Caminho B sem L no assunto), peça o código ao Lucas — não chute.

---

## Workflow

### Passo 0 — Preparar o ambiente

1. `tabs_context_mcp` para ver as abas abertas.
2. Confirmar que existe aba no Dynamics. Tenant Brasil: `apwbrasil.crm2.dynamics.com` (ou o que estiver na URL — o caso da Marcelina usa `apwireless.crm.dynamics.com`, então **não assuma o subdomínio, leia da aba ativa**). Tenant US: `apw.crm.dynamics.com`.
3. Confirmar que existe aba no Outlook (`outlook.cloud.microsoft` ou `outlook.office.com`). Atalho pro tenant certo do Lucas: `https://outlook.cloud.microsoft/mail/?realm=apwbrasil.com.br&login_hint=LMinozzo@apwbrasil.com.br`.
4. Se faltar alguma aba, peça pro Lucas abrir e logar antes de seguir. Não tente logar você.
5. Declare o plano em uma linha: *"Plano: extraio o L1256097 via Web API do Dynamics + busca da thread no Outlook, sem screenshots."*

### Passo 1 — CRM: o esqueleto do deal

Puxe a opp por código L via Web API. O snippet completo e os campos estão em **`references/crm-extraction.md`** — leia antes de executar. O essencial:

- Entidade base: `opportunity`. Campos custom: prefixo `apwip_`.
- Código L = campo `apwip_autonumberid` (use só o número, sem o "L").
- Traga: `name`, `stepname` (stage), `ownerid` (diretor), `estimatedclosedate`, `closeprobability`, `apwip_rfexpertnotes`, `apwip_dealtypecode`, e os campos de valor/aluguel.
- **Depois** puxe as **atividades** da opp (`activitypointer` filtrado por `regardingobjectid`) — é onde mora o histórico de follow-ups. Snippet em `references/crm-extraction.md`.

Se o array vier vazio, o campo `apwip_autonumberid` pode ser numérico vs. string — alterne o formato (`eq 1256097` vs `eq 'L1256097'`) e tente de novo.

### Passo 2 — Outlook: a carne da negociação

Caminho A: busque a thread no Outlook pelo código L. Caminho B: você já tem a thread, pule a busca.

A mecânica de busca, parsing de thread encadeada e extração ordenada está em **`references/outlook-extraction.md`** — leia antes de executar. O essencial:

- Buscar pelo código L no search do Outlook (o L aparece no assunto dos emails APW). Se não achar, fallback: buscar pelo nome do site / proprietário / contraparte (ex.: "MARILENE VERDUGO", "Sorocaba", "BR62831").
- A thread vem encadeada e fora de ordem (o email mais recente no topo, citações aninhadas embaixo). **Reordene cronologicamente** — do mais antigo pro mais recente — antes de analisar. A história só faz sentido na ordem em que aconteceu.
- Cada mensagem: data, remetente, destinatário, e o fato novo que ela introduz.

### Passo 3 — Cruzar as duas fontes (o núcleo)

Aqui está o valor da skill. Com CRM + atividades + thread de email na mão, leia tudo procurando:

1. **O que o deal é** — tipo (DRS, cessão de crédito, asset purchase), site, operadora, contraparte, valor.
2. **O que foi negociado** — sequência de termos acordados, e o que mudou ao longo do tempo (deriva de preço, mudança de condição).
3. **Divergências entre fontes** — o achado mais valioso. CRM diz X, email diz Y, sistema interno diz Z. No caso da Marcelina: a SBA afirma que o acordo entre matrizes previa isenção de reajuste em 2026; a ISW (sistema APW) **não** prevê isso. Isso é uma divergência aberta que trava o caso — tem que aparecer destacada.
4. **Mapa de quem é quem** — APW (asset managers, advogados), contraparte (torreira, operadora), proprietário. Quem decide, quem trava, quem está só executando.
5. **O que está pendente / qual a pergunta em aberto** — o que efetivamente falta pra destravar. É isso que o Lucas precisa pra responder o pedido de "podem ajudar?".
6. **Riscos** — atraso de aluguel, retirada de equipamento, descomissionamento, dado bancário errado, prazo estourando.

Ver `references/cross-analysis.md` para o catálogo de padrões a caçar (vocabulário de risco telecom, jargão APW, tipos de divergência típicos).

### Passo 4 — Entregar o dossiê

Entregue o dossiê **no corpo do chat**, em português brasileiro casual, seguindo o template abaixo. Sem dump de JSON, sem floreio. A saída é sempre conversacional e scannável — **não gere arquivo**. O Lucas quer ler na hora e seguir; criar um `.md` só adiciona um clique e um artefato a mais sem ganho.

Exceção única: se o Lucas pedir **explicitamente** um arquivo ("salva isso", "me dá em .md", "quero mandar pra alguém"), aí gere — um Markdown limpo em `/mnt/user-data/outputs/dossie-Lxxxxx.md` com só o dossiê estruturado (nunca o dump bruto), apresentado com `present_files`. Se o destino for a contraparte (SBA, torreira), gere versão **limpa** — sem leitura política interna, sem trechos sensíveis. Mas isso é exceção: o default é chat e só chat.

Ao final, declare o consumo de ferramentas em uma linha (compliance / visibilidade): *"Concluído. 3 chamadas javascript_tool, 1 get_page_text, 0 screenshots."*

---

## Template do dossiê

SEMPRE use esta estrutura. É ADHD-friendly: o veredito vem primeiro, o detalhe vem depois, o próximo passo fecha. Mantenha **enxuto e scannável** — o Lucas lê isso no meio de um pedido urgente ("podem ajudar?") e precisa do panorama em segundos, não de um relatório. Frases curtas, bullets diretos, sem parágrafo gordo. Se uma seção cabe em uma linha, deixe em uma linha.

```markdown
# Dossiê — L[código] · [nome curto do deal]

> [Uma frase: o que é o deal + o veredito da situação atual.]

**Tipo:** [DRS / cessão de crédito / asset purchase]  ·  **Site:** [ID / endereço]
**Stage CRM:** [stepname]  ·  **Owner:** [diretor]  ·  **Contraparte:** [torreira/operadora]

## 1. O que está acontecendo agora
[2-4 frases. O estado real do caso e por que ele chegou até o Lucas. Se veio
de um pedido de "podem ajudar?", responda diretamente: ajudar com o quê.]

## 2. O que foi negociado
[Sequência dos termos acordados, em ordem. Valores exatos, datas, condições.
Marque o que mudou ao longo do tempo.]

## 3. Divergências em aberto
[O bloco mais importante quando existe. Tabela ou lista:
Fato | Fonte A diz | Fonte B diz | Implicação.
Se não houver divergência, escreva "Nenhuma divergência aberta identificada".]

## 4. Quem é quem
[APW: asset managers, advogados envolvidos. Contraparte. Proprietário.
Marque quem decide e quem trava.]

## 5. Linha do tempo
[Marcos cronológicos enxutos: data — quem — o que aconteceu.
Só o que mudou o caso, não todo email.]

## 6. Riscos / pontos de atenção
[Lista classificada 🔴 crítico / 🟡 atenção / 🟢 ok. Cada um com a evidência.]

## 7. Próximo passo
[1-3 ações concretas em ordem de prioridade. O que o Lucas precisa fazer ou
decidir para destravar. Se há uma pergunta a responder pra contraparte ou
para a área interna, formule-a explicitamente.]
```

Se o caso for trivial (deal limpo, sem divergência, sem risco), pode encolher: seções 1, 2, 5 e 7 bastam. Não infle um caso simples.

---

## Princípios da análise

- **Toda afirmação rastreável.** Conclusão sem evidência (campo do CRM, atividade, ou email com data) não entra. Quando citar um email, diga a data e o remetente.
- **Números exatos.** "Aluguel ~6k" e "R$ 6.000,00 efetivo a partir de ABRIL/2026, pago em MAIO/2026" são fatos diferentes. Capture o exato.
- **Divergência é ouro.** Quando CRM, email e sistema interno discordam, não concilie em silêncio — exiba o conflito. É frequentemente o motivo pelo qual o caso chegou ao Lucas.
- **O stage do CRM pode mentir.** Uma opp pode estar "Stage 99 / fechada" no CRM e ainda ter pendência operacional ativa nos emails (dado bancário, reajuste, aditivo não assinado). O diagnóstico vem do cruzamento, não do campo.
- **Responda o pedido real.** Se o caso chegou via "podem ajudar?", o dossiê tem que terminar respondendo: ajudar com o quê, e qual a recomendação. Não entregue um resumo neutro quando há uma decisão a tomar.
- **Não invente para preencher.** Seção sem evidência = "Sem informação nas fontes consultadas". Um deal mal documentado é, em si, um achado.

---

## Arquivos da skill

- `references/crm-extraction.md` — snippets Web API para puxar a opp e suas atividades do Dynamics 365. Leia no Passo 1.
- `references/outlook-extraction.md` — como buscar a thread pelo código L, parsear email encadeado e reordenar cronologicamente. Leia no Passo 2.
- `references/cross-analysis.md` — catálogo de padrões para o cruzamento: tipos de divergência, vocabulário de risco telecom, jargão APW, mapa de papéis típicos. Leia no Passo 3.

---

## Quando NÃO usar esta skill

- Lucas quer só um dado pontual do CRM sem narrativa ("qual o owner do L123") → `apw-dynamics-copilot`.
- Lucas colou uma view de atividades e quer forensics só dessas atividades → `apw-opp-activity-forensics`.
- Análise de cláusula contratual / minuta → `apw-telecom-real-estate-counsel`.
- Rotina diária de follow-up SBA com a planilha de controle → `apw-sba-daily-routine`.
- Qualquer coisa Braus / pessoal / finanças do Lucas — esta skill é só contexto APW corporativo.
