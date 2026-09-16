---
name: apw-opp-deepdive-snippet
description: >-
  Deep dive completo de UMA oportunidade da APW Brasil a partir de um codigo L, extraindo tudo
  via snippet de console (F12) na aba autenticada do Dynamics 365 - sem agente de navegador,
  sem screenshot. Puxa o registro inteiro da opp, o historico de atividades com as descricoes
  longas, notas, anexos e todas as pricing options com IRR e estrutura de pagamento; depois
  varre o M-Files. Entrega dossie no chat com deriva de preco, divergencias de CRM, cadeia de
  bloqueio e caminho de retomada (avancar x reestruturar x surrender). Use SEMPRE que o Lucas
  mandar um codigo L pedindo "deep dive", "entender esse caso", "pega todas as atividades",
  "quero retomar esse deal", "por que parou", "quais propostas ja foram feitas", "puxa tudo
  desse L", "snippet F12", ou colar nome de opp (Lxxxxxx_Nome) sem contexto. Acione tambem ao
  herdar opp antiga. NAO use para dossie via agente + Outlook (apw-deal-dossier), atividades
  coladas (apw-opp-activity-forensics), varias opps (apw-pool-forensics) nem On Hold
  (apw-onhold-reassessment).
---

# APW — Deep Dive de Oportunidade via Snippet (F12)

Reconstrói a história inteira de **uma** oportunidade da APW a partir de um único código L, extraindo os dados por snippets que o Lucas cola no console do navegador. O método é F12 por escolha: não consome tokens com agente de navegador, não gera screenshot em domínio corporativo, e traz a íntegra dos campos longos que a UI trunca.

## Princípios inegociáveis

1. **Sempre F12, nunca agente**, salvo se o Lucas pedir o contrário. Antes de começar, confirme numa linha: *"Vou por snippet F12 — você cola no console da aba do Dynamics."* Se ele disser "usa o Chrome agent", troque e siga `apw-chrome-agent-lean-compliance`.
2. **Zero screenshot** em Dynamics / M-Files / Microsoft 365.
3. **Dados em memória.** O dossiê vai no corpo do chat. Não crie arquivo com dump bruto do CRM. Só gere arquivo se o Lucas pedir explicitamente — e aí só o dossiê, nunca o JSON.
4. **Não persista PII** em `memory_user_edits`. Padrão de uso, sim; conteúdo de deal, não.
5. **Toda afirmação rastreável.** Conclusão sem campo, atividade ou pricing option com data não entra no dossiê.

## Workflow

### Passo 0 — Identificar tenant e código

Pergunte (ou infira) em qual tenant a opp vive. **Não assuma.** Os dois têm schemas DIFERENTES:

| Tenant | URL | Campo do código L |
|---|---|---|
| Global/US (a maioria dos L antigos, inclusive Brasil legado) | `apwireless.crm.dynamics.com` | `apwip_opportunityautonumberid` |
| Brasil | `apwbrasil.crm2.dynamics.com` | confirmar via metadata antes de filtrar |

O snippet do Passo 1 já resolve isso sozinho — ele descobre o campo antes de filtrar. **Não hardcode nome de campo.** Ver `references/crm-snippets.md` § "Armadilhas de schema" para o histórico de erros que isso causa.

### Passo 1 — Extração do CRM

Entregue o **Snippet 1 (localizar + extrair tudo)** de `references/crm-snippets.md`. Ele faz numa tacada:

- descobre o campo do código L via metadata (regex apertado, sem `AttributeType` no `$select`)
- acha a opp testando os formatos de filtro (numérico → `'Lxxxxx'` → `'xxxxx'` → `contains`)
- puxa o registro **completo sem `$select`**, filtrando só o que tem valor, e anexa os rótulos formatados
- puxa `activitypointers` + `tasks`/`emails`/`phonecalls`/`appointments` diretos
- puxa `annotations` (notas e anexos)
- descobre o campo de vínculo de `apwip_pricingoptions` e traz todas
- guarda em `window.__L` e instrui `copy(window.__L)`

Peça pro Lucas colar o retorno. Se passar de ~300KB, mande o filtro de corte (§ "Payload grande" no reference).

### Passo 2 — Extração do M-Files

Só depois que o CRM voltar. Entregue o **Snippet M-Files** de `references/mfiles.md`. O CRM quase nunca tem anexo (`annotations` vazio é o normal) — os documentos do deal estão todos no M-Files.

Se o Lucas não precisar dos docs (ex.: só quer entender por que parou), pule e diga que pulou.

### Passo 3 — Análise

Leia `references/analise.md` antes de escrever o dossiê. Ele traz as sete lentes obrigatórias:
deriva de preço/IRR · cadeia de bloqueio · divergências de CRM · mapa de atores · esforço real × teatro de CRM · risco de instrumento · veredito de retomada.

### Passo 4 — Entrega

Dossiê no chat, no template abaixo. Português informal, denso, escaneável, bottom-line primeiro.

---

## Template do dossiê

```markdown
# Dossiê — L[código] · [nome curto]

> [Uma ou duas frases: o que é o deal + o veredito. Se está morto, diga que
> está morto. Se o bloqueio nunca foi preço, diga isso na primeira linha.]

**Tipo:** [Fee Simple / DRS / Cessão de crédito] · **Site:** [endereço, área, coordenada]
**Stage:** [x] · **Status:** [statuscode] · **On Hold desde:** [data real das atividades]
**Owner:** [atual, desde quando] · **Antes:** [quem tocou de fato]
**Contraparte:** [decisor] · **Gatekeeper:** [quem realmente responde]
**Back-office:** [legal, paralegal, processor, RF, closer]

## 1. O que está acontecendo agora
[Estado real. Quando foi a última interação HUMANA — ignore notificação
automática de CRM e reatribuição. Quantos meses de silêncio.]

## 2. A cadeia de bloqueio
[Tabela cronológica só dos fatos que travaram. Separe bloqueios independentes
e diga quais estão fora do controle da APW.]

## 3. Deriva de preço e IRR
[Tabela: data · estrutura · valor · IRR · aluguel base. Marque a Chosen Pricing
Option e a proposta verbalmente aceita. Comente a tendência da IRR — se caiu
enquanto o preço subiu, isso é custo afundado disfarçado de atualização.]

## 4. Divergências abertas 🔴
[Tabela: item · fonte A · fonte B · implicação. Este é o bloco de maior valor.]

## 5. Documentação
[O que existe ✔ / o que falta. Cruze com handoff notes e M-Files.]

## 6. Caminho de retomada
[Não é "atualizar a proposta". É: qual hipótese destrava o bloqueio real,
o que precisa ser checado antes, e a ordem prática. Termine com a condição
binária que decide avançar × surrender.]
```

Se o deal for simples e limpo, encolha para as seções 1, 3 e 6. Não infle.

---

## Erros que já custaram rodadas (leia antes de gerar snippet)

- `apwip_autonumberid` **não existe** em opportunity no tenant US — é `apwip_opportunityautonumberid`. E é `Edm.String`: filtro numérico dá 400.
- `$select=LogicalName,AttributeType` no endpoint de Attributes dá **501**. Use só `LogicalName`.
- `$expand=ownerid($select=fullname)` em opportunity/activitypointer dá **400** (lookup polimórfico). Não use expand — pegue `_ownerid_value@OData.Community.Display.V1.FormattedValue`.
- `stepname`, `apwip_dealtypecode`, `apwip_rfexpertnotes` podem não existir. Nunca monte `$select` com campo não verificado — puxe o registro inteiro.
- `copy()` é utilitário de console e **não funciona dentro de IIFE async**. Guarde em `window.__L` e mande o Lucas rodar `copy(window.__L)` depois.
- Regex de busca de campo com `/apw/` casa com os 886 campos `apwip_*` e trunca a saída. Use termos específicos.

---

## Arquivos

- `references/crm-snippets.md` — snippets prontos, armadilhas de schema, troubleshooting por código HTTP, corte de payload grande.
- `references/mfiles.md` — snippet do M-Files, fallbacks de endpoint, mapa de classes de documento APW.
- `references/analise.md` — as sete lentes de análise, catálogo de divergências típicas, regras APW de instrumento (DRS × Fee Simple × Cessão) e vocabulário de risco.

## Quando NÃO usar

- Dossiê rápido cruzando CRM + thread do Outlook via agente → `apw-deal-dossier`
- Atividades já coladas no chat, sem acesso ao CRM → `apw-opp-activity-forensics`
- Várias opps / view / lista → `apw-pool-forensics`
- Estoque On Hold por torreira → `apw-onhold-reassessment`
- Um campo pontual → `apw-dynamics-copilot`
- Análise registral de matrícula → `apw-pre-dd-legal`
