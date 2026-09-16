---
name: apw-pool-forensics
description: Forense de uma VIEW/LISTA de oportunidades do Dynamics 365 da APW Brasil. Responde por deal — (1) em que STAGE o diretor pegou e em que stage está hoje (trabalhamos ou só seguramos?), (2) quando foi ASSINADO e qual instrumento, (3) por que caiu numa POOL e não está com um diretor (data, motivo declarado × motivo real), (4) esforço real por deal separando ligação de disparo em massa. Use SEMPRE que o Lucas colar URL de view do Dynamics ou lista de códigos L pedindo "analisa essa view", "em que stage pegaram", "trabalhamos mesmo ou não", "deram foco?", "por que caíram na pool", "razão da queda", "quando foram assinados", "quem era o dono na época", "forense dessa lista", "quantas abordagens". NÃO use para um deal isolado (apw-deal-dossier), estoque On Hold por torreira (apw-onhold-reassessment), pipeline frio reabordável (apw-pipeline-reativacao), nem atividades já coladas no chat (apw-opp-activity-forensics).
---

# APW Pool Forensics

Autópsia de lote. Entra uma view do Dynamics, sai o diagnóstico deal a deal: **onde pegou · onde está · assinou? · por que morreu · trabalhamos ou não.**

Vale para qualquer view — pool, campanha, portfólio, lista de torreira. **Nunca presuma o universo: leia o fetchxml da view primeiro** (o script 01 faz isso e imprime).

## Fronteira com as skills que já existem

| Skill | Ela responde | Esta skill responde |
|---|---|---|
| `apw-onhold-reassessment` | o que dá pra reabordar hoje (regra de torreira) | o que aconteceu com estes no passado |
| `apw-pipeline-reativacao` | prioriza pool fria por potencial | reconstrói a entrada na pool |
| `apw-opp-activity-forensics` | lê atividades de UMA opp coladas no chat | conta e tipifica atividade de N opps |
| `apw-deal-dossier` | narrativa de UM L (CRM + Outlook) | tabela comparável de N deals |
| `apw-dynamics-copilot` | como falar com a Web API | o que perguntar a ela |

Reutilize dessas skills o regex de torreira e a taxonomia de pool. **Não reescreva.**

## Coleta — rota console é a padrão

**Rota A (padrão, robusta): F12 → Console.** O Lucas cola `scripts/01-coleta-base.js` (trocando só o `VIEW_ID`), o script baixa `apw_view_raw.json`, ele anexa no chat. Depois, se a pergunta for sobre esforço, roda `scripts/02-coleta-atividades.js` → `apw_sba_ativ_campanha.json`.
Se o Chrome bloquear colagem: digitar `allow pasting` + Enter.

**Rota B: Claude in Chrome (MCP).** Só quando o Lucas quiser que o Claude opere. Mais lenta, sujeita a queda de conexão (já caiu no meio de uma análise e levou junto tudo o que estava em memória na aba) e cada retorno trunca em ~1.500 chars, o que obriga a fatiar tabela em várias chamadas. Se usar, vale a `apw-chrome-agent-lean-compliance`: **zero screenshot em `*.dynamics.com`**, tudo via `javascript_tool`, e o padrão assíncrono `window.__x='pending'; (async()=>{...})(); 'kicked'` lendo o resultado na chamada seguinte.

**Análise: `scripts/03-analise.py apw_view_raw.json [apw_ativ.json]`** — genérico, não assume nada da view, imprime os blocos A–F e gera `apw_view_forense.csv`.

## Os quatro cortes

### 1. Stage de entrada × stage atual — o corte que mede foco
`apwip_assignedon` marca quando o deal caiu na mão atual. O stage naquele momento = **maior `apwip_stage{N}date` anterior ao assignedon**. Stages carimbados *depois* = o que o dono fez.

Saem daí as três perguntas que importam: **pegou em que stage · moveu alguma coisa · chegou onde.** Diretor que recebe 30 deals já em Stage 5 e devolve 30 em Stage 5 não teve o mesmo trabalho de quem recebeu em Stage 3.

### 2. Assinatura sem funding
Evidência, em ordem de força: `apwip_executedsignatureauthorizationdatestamp` → `apwip_signedapplicationdatestamp` → `apwip_stage6date` (LOI recebida). Cruzar com `apwip_stage99closedandfundeddeal` / `apwip_fundswireddate`.
**Assinado e não fundeado é o achado mais caro de qualquer view.** Marcar sempre, e marcar também quando `apwip_surrenderedon` for anterior à data de assinatura (furo de dado ou stage backfillado — não reabordar sem conferir no registro).

### 3. Por que está numa pool
Declarado: `apwip_surrenderreasonopp` (picklist) + `apwip_surrenderedon`. Real: atividades na janela −90/+30 da queda.
Classificar em cinco baldes: `ADMINISTRATIVO` · `CONTRAPARTE` · `TORREIRA/OPERADORA` · `TÍTULO/JURÍDICO` · `APW`.
Comparar **idade do estoque por pool**: pool com mediana de 2 meses é output de campanha em curso; pool com mediana de 5+ anos é estoque esquecido. São problemas diferentes e não devem ser somados.

### 4. Esforço real
`activitypointer` **conta eBlast, carta e tarefa de sistema junto com ligação.** Contagem bruta serve para o gradiente (mais toque → mais sobrevida), **nunca como meta nem para avaliar pessoa**. Só o split por `activitytypecode` (script 02) separa `phonecall` de disparo, e é o único número que distingue *"o proprietário disse não"* de *"ninguém ligou e surrendou como I Like My Rent"*.

## Interpretação — o que NÃO concluir

- **Stage parado ≠ diretor parado.** Deal em Stage 5 só sai se o proprietário assinar a LOI. Quem ligou dez vezes, ouviu "gosto do meu aluguel" e surrendou fez o certo e não moveu stage. Motivos como *I Like My Rent* e *Exhausted Contact Methods* **provam contato**. Movimento de stage mede conversão, não esforço.
- **Não nomeie diretor sem audit.** Ao cair na pool o `ownerid` é sobrescrito; o `apwip_stage{N}owner` é quem carimbou o stage lá atrás — frequentemente alguém que saiu da empresa anos antes. Usar isso para avaliar gente produz acusação errada. Se o assunto virar avaliação, rodar `RetrieveRecordChangeHistory` antes (funciona nesse tenant; 1 request/deal).
- **`apwip_assignedon` é sobrescrito.** Nos deals já em pool ele marca a entrada na pool, não a atribuição ao diretor. Não dá para medir tempo-em-carteira de deal morto sem audit.
- **Campo `carrier` é texto sujo** (`,TNL PCS S.A,,,`, `1278410 - TNL PCS S.A.`, `TELEMAR`, `Brasil Telecom Cel. S/A`). Normalizar por regex antes de contar — TNL PCS e Brasil Telecom são Oi. Sem isso a composição da carteira sai errada.
- **Motivo declarado ≠ motivo real.** Quando divergirem, mostrar os dois.

## Campos validados em produção (apwireless.crm.dynamics.com)

| Campo | O que é |
|---|---|
| 🔴 `apwip_opportunityautonumberid` | Código L (**não** é `apwip_autonumberid` — esse não existe em opportunity) |
| 🔴 `apwip_stage1date` **não existe** | Existem `apwip_stage2date`…`apwip_stage9date`, `apwip_stage100date` |
| `apwip_stage{N}owner` | Dono na época de cada stage (lookup → ler `_apwip_stage6owner_value` + FormattedValue) |
| `apwip_stage6_receivedsignedloi` / `apwip_stage6date` | LOI assinada recebida |
| `apwip_executedsignatureauthorizationdatestamp` | Signature Authorization executada (+ `...name`, `...note`) |
| `apwip_signedapplicationdatestamp`, `apwip_signingcompletedatnotarydatestamp` | Application assinada / assinatura em cartório |
| `apwip_stage99closedandfundeddeal`, `apwip_fundswireddate`, `apwip_dateclosed` | Fechado e fundeado / wire / close |
| `apwip_surrenderedon` | **Data da queda** (`modifiedon` não serve — job em massa reescreve) |
| `apwip_surrenderreasonopp` | Motivo declarado (I Like My Rent, Exhausted Contact Methods, Does Not Meet APW Standards, Unrealistic Expectations, Gone Dark, No Consensus between owners, Cannot Engage with landlord, Title Issues, Obsolete Technology, Major Account…) |
| `apwip_surrenderreason` / `apwip_surrenderreasonlegal` | Texto livre — ~99,8% vazio, não confiar |
| `apwip_legalopportunitystage`, `lastonholdtime`, `apwip_assignedon` | Complementares |

**Pools desse tenant**: Surrendered · Disqualified · Research Required · Purged · Low Priority Data Source · Overly Complex · Decommissioned · Quarantine Brasil · Major Account · Tower Company · Municipality · Sites at Risk.

**Descoberta de campo**: `EntityDefinitions(LogicalName='opportunity')/Attributes?$select=LogicalName,AttributeType` + regex no cliente. Muito melhor que bisseção por HTTP 400 — a mensagem de erro cita `'Opportunity'` antes do atributo ruim, então regex ingênuo pega a entidade errada.

**Views de campanha** costumam filtrar por `lead.apwip_dummy3` (tag de importação em lote, ex.: `Andy's SBA list`) via `link-entity` de `originatingleadid`. O script 01 extrai o filtro original e reinjeta.

## Armadilhas técnicas

1. `?fetchXml=` corta em **5.000 registros sem `@odata.nextLink`** — filtre na origem.
2. Sem `Prefer: odata.include-annotations=*` volta número de picklist e GUID; leia `campo@OData.Community.Display.V1.FormattedValue`.
3. FetchXML agregado tem teto de **50.000 registros processados** — quebre por ano, e por trimestre quando o ano estourar (o script 02 já faz janelas).
4. Retenção de auditoria pode ter expirado em deals de 2013–2017: ausência de audit **não** é ausência de evento.
5. `audits` filtra por `_objectid_value`, não `objectid`; prefira `RetrieveRecordChangeHistory`, que devolve old/new pareados.

## Saída

Bottom-line primeiro, no chat: **veredito em 3 linhas** → stage de entrada × atual por diretor → quedas por pool com idade do estoque → assinados sem funding → esforço (com o caveat do eBlast explícito) → **o que o dado não permite concluir**.

CSV em `/mnt/user-data/outputs/`. Dashboard HTML na marca (`apw-brand`) só quando pedido. Nunca despejar 300 linhas no chat. Nunca gravar nada no CRM nesta skill.
