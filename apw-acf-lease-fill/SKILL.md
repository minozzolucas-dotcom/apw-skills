---
name: apw-acf-lease-fill
description: Use quando o Lucas pedir pra preencher o Abstracted Cash Flow (ACF) da entidade apwip_lease no Dynamics 365 tenant Radius (apwireless.crm.dynamics.com) a partir do contrato + aditivos de um deal APW. Gatilhos — "preenche o ACF", "roda o cash flow", "abstracted cash flow do L#####", "faz o ACF desse deal", "preenche apwip_lease", "traz dados do contrato pro ACF", "atualiza o lease no Dynamics", "cash flow do lease", "atualiza direitos no lease", "mapeia contrato pra Radius". Também acione ao colar URL apwireless.crm.dynamics.com/main.aspx com etn=apwip_lease. NÃO use pro PIN/Lead inicial no tenant Brasil (apw-pin-creator), Key Notes na opp (apw-crm-key-notes-writer), parecer de cláusula (apw-telecom-real-estate-counsel), dossiê do deal (apw-deal-dossier) ou reajuste bruto/líquido (apw-rent-gross-up).
---

# APW ACF Lease Fill

Skill pro Lucas (APW Brasil) preencher o form **Abstracted Cash Flow** — entidade `apwip_lease` — no tenant **Radius US** (`apwireless.crm.dynamics.com`), a partir do contrato de locação e cadeia de aditivos de um deal já cadastrado no CRM.

O caso de uso: o Lead já foi criado no tenant Brasil (via `apw-pin-creator`), a opportunity espelhou pro tenant US com prefixo `L######`, e agora precisa alimentar o Cash Flow Abstracto pra valuation/IC. Os dados vêm do contrato + aditivos.

**Esta skill NÃO grava sozinha.** Preenche o form via `Xrm.Page.setValue`, marca o form como dirty, e devolve pro Lucas conferir visualmente e clicar Save. Zero risco de POST cego.

---

## Herança

- **Anti-screenshot / não-retenção** — herda de `apw-dynamics-copilot`. Domínio corporativo sensível, screenshot bloqueado.
- **Análise de cláusulas** — reusa o mapa de cessão/direitos que `apw-pre-dd-legal` e `apw-telecom-real-estate-counsel` já produzem. Se a cadeia contratual ainda não foi analisada, rode `apw-pre-dd-legal` primeiro.
- **Rent escalation** — se o reajuste vigente precisar ser calculado (não está no contrato), delegue a `apw-rent-escalation`.

---

## Workflow — 5 passos

### 1. Confirmar contexto

Confirme com o Lucas antes de qualquer coisa:

- **URL do form:** `https://apwireless.crm.dynamics.com/main.aspx?...&etn=apwip_lease&pagetype=entityrecord`
- **Lead/Opportunity já existe** no CRM Brasil e espelhou pro tenant US? O `apwip_account` e `apwip_opportunity` do form devem vir pré-preenchidos com o `L######`. Se não vieram, pare — o sync ainda não rodou.
- **Contract package na mão:** contrato base + todos os aditivos + comprovante de aluguel vigente (se houver — ajuda a validar current rent).

### 2. Descoberta do form (obrigatória)

Cada form apwip_lease pode ter tabs colapsados, campos hidden por Business Process Flow, e o schema muda com o tempo. Nunca preencha às cegas.

Rode `references/snippet-diagnostico.js` no console do Chrome (Lucas já autenticado). Ele:
- Detecta `Xrm` no escopo certo (window, parent, top, iframes)
- Lista os 60+ attributes do form (nome interno, tipo, required level, valor atual, opções dos optionsets)
- Baixa como `lease_form_diagnostico.json`

Lucas anexa o JSON. Você lê e valida contra `references/campos-acf.md` — se o schema mudou (campo novo, opção nova), atualize o mapeamento.

### 3. Extrair dados do contrato

Leia contrato + aditivos e extraia:

| Bloco | Campos a extrair |
|---|---|
| Partes | Locador (nome, CPF/CNPJ), Locatária (nome, CNPJ — vira `apwip_carrier` lookup) |
| Datas | Início contrato, fim contrato consolidado, data-base do reajuste, próxima data de pagamento |
| Valores | Aluguel inicial, aluguel vigente (validar com comprovante se houver) |
| Prazo | Anos do prazo inicial consolidado, quantidade de renovações (0 se o aditivo travou renovação por acordo) |
| Escalator | Índice (IPCA/IGP-M/INPC), frequência (anual), amount **(SEMPRE 3% — padrão APW, não usar % real)** |
| Rights | Cessão pelo landlord, cessão pelo tenant, sublocação, uso, early termination, 24/7 access, auto-renewal |
| IDs | Nome do lessor, tax ID do lessor, carrier site ID (ID interno do carrier — SP-XX-XXX ou BTSA1000000XXXXX) |

**Divergências no contrato são flag.** CPF diferente entre cabeçalho e dados bancários, CEP genérico, área conflitando com croqui — sinalize ao Lucas antes de gravar. Nunca escolha calado.

### 4. Padrões fixos APW — DECORE

Estes valores SÃO padronizados pra Radius/APW, INDEPENDENTE do que o contrato específico diz. Não invente.

| Campo | Valor fixo | Racional |
|---|---|---|
| `apwip_escalatoramount` | **3** (decimal, sem %) | Padrão Radius de normalização — nunca use o % real do IPCA acumulado |
| `apwip_escalatortype` | **100000000** (Index) | Reajustes brasileiros são index-based (IPCA, IGP-M, INPC) |
| `apwip_paymenttype` | **100000000** (Rent) | Ground/Rooftop Lease NÃO é o padrão — Radius usa "Rent" genérico |
| `apwip_paymentfrequency` | **100000000** (Monthly) | Aluguel brasileiro é mensal por default |
| `apwip_escalatorfrequency` | **100000000** (1 ano) | Reajuste anual — 100000000 é o value para "1" (não é o value literal 1) |

Estes 5 nunca mudam sem o Lucas explicitamente pedir. Não perca tempo perguntando.

### 5. Preencher, conferir, salvar

Rode `references/snippet-preenchimento.js` (adaptado com os valores extraídos no passo 3). Ele:

- Faz `setValue` em todos os campos + `fireOnChange`
- Busca `apwip_carrier` via Web API `/accounts?$filter=contains(name,'V.tal')` — se achar, preenche o lookup; se não achar, deixa em branco e loga
- Devolve `console.table` com o status de cada `setValue`
- Marca o form como dirty **mas NÃO salva**

Lucas confere visualmente cada tab (Economics + Provisions), corrige o que precisar, clica Save. Se um campo deu erro, aparece no console table — ajuste no mesmo prompt.

**Nunca dispare `formContext.data.entity.save()` da skill.** Save é ação humana.

---

## Mapeamento de rights via cláusulas contratuais

Este é o pedaço que exige leitura jurídica. Use como referência as cláusulas típicas de contrato de site telecom BR (Oi, TIM, Claro, Vivo padrão) — mas **releia o contrato específico** antes de gravar. O padrão típico:

| Campo ACF | Valor padrão | Cláusula típica que sustenta |
|---|---|---|
| `apwip_landlordassignmentrights` | Unlimited (870410000) | "Alienação a terceiros não interrompe vigência" — landlord pode ceder livremente |
| `apwip_landlordassignmentconsentrequired` | False | Contratos telecom BR não pedem consent do carrier pra alienação do imóvel |
| `apwip_assignmentrights` (tenant) | Notice Required (870410002) | Cláusula de cessão pela LOCATÁRIA "mediante notificação escrita" |
| `apwip_tenantsubletrightsv2` | Unlimited (870410001) | Cláusula que "autoriza a LOCATÁRIA a sublocar" |
| `apwip_userights` | Unlimited (870410000) | Uso amplo pra atividade telecom + compartilhamento (Res. 274 Anatel) |
| `apwip_tenantearlyterminationrights` | Unlimited (870410000) | Cláusula que permite denúncia "a qualquer tempo com aviso prévio" |
| `new_earlyterminationbycarrier` | Yes (100000000) | Mesma cláusula acima |
| `apwip_247accesslegal` | True | Cláusula "24 horas por dia, 365 dias por ano" |
| `apwip_autorenewallegal` | **Depende** | True se o contrato tem renovação automática ativa; False se aditivo travou renovação por acordo |
| `apwip_carriersponsored` | False | Deal APW clássico, não é carrier-sponsored |

Divergências importantes que mudam o mapeamento:
- Contrato pede consent (não só notice) → `apwip_assignmentrights` = Consent Required (870410000)
- Contrato veda cessão pelo tenant → Assignment Not Allowed (870410004)
- Contrato veda sublocação → Silent (870410002) ou Limited (870410000)
- Contrato tem exclusividade telecom → sinalize no `apwip_directorscomment` E revise se o deal continua viável

---

## Onde os valores dos optionsets vêm

Os `value`s numéricos de optionset (100000000, 870410000, etc.) são específicos do schema Radius. Estão listados em `references/campos-acf.md`. Se o form mudar (novo campo, opção nova), o snippet de diagnóstico mostra as opções atualizadas — atualize `campos-acf.md`.

---

## Regra de ouro

**Todo dado gravado no ACF tem que ter fonte no contrato ou nos padrões fixos APW.** Se você não consegue apontar qual cláusula ou qual regra fixa sustenta um valor, não grave. Deixa em branco e sinaliza ao Lucas.

Contrato ambíguo → sinalize, não escolha.
Cláusula silente → padrão APW se houver; senão, em branco.
Divergência entre docs → nunca escolha calado.

---

## Quando NÃO usar

- Ainda não criou o Lead/PIN → use `apw-pin-creator` primeiro
- Analisar cláusula pra dar parecer → `apw-telecom-real-estate-counsel`
- Pré-DD / auditoria registral → `apw-pre-dd-legal`
- Escrever Key Notes da opportunity → `apw-crm-key-notes-writer`
- Calcular reajuste real (bruto/líquido) → `apw-rent-escalation` ou `apw-rent-gross-up`
- Montar submission pro IC → `apw-submission-writer`

## Estilo

- Português BR casual, direto, ADHD-friendly (tabelas > parágrafos)
- Sinalize divergências antes de gravar, nunca escolha calado
- Nunca eco PII sem necessidade
- Nunca screenshot depois do Save
