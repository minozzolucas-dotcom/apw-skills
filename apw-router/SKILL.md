---
name: "apw-router"
description: "Skill mestre da APW Brasil. Acionar SEMPRE como primeiro passo em qualquer demanda APW — substitui a necessidade de o Lucas saber qual skill chamar. Faz triagem conversacional (máx 2 perguntas) e aciona a skill certa. Triggers: \"APW\", \"deal\", \"L-number\", qualquer código L, \"torreira\", \"CRM\", \"submission\", \"pré-DD\", \"contrato\", \"minuta\", \"reajuste\", \"proposta\", \"dossiê\", \"CCIR\", \"matrícula\", \"CAR\", \"SBA\", \"ATC\", ou quando o Lucas colar um documento telecom sem contexto."
---

# APW Router — Skill Mestre

Ponto de entrada único para todas as demandas APW Brasil. O Lucas não precisa saber qual skill chamar — o router identifica e aciona.

## Como funciona

1. Lê a mensagem do Lucas
2. Se o intent for claro → aciona a skill diretamente, sem perguntar
3. Se ambíguo → faz NO MÁXIMO 2 perguntas de triagem (botões quando possível)
4. Nunca explica qual skill vai usar — só entrega o resultado

## REGRA TRANSVERSAL — planilha do Forms é obrigatória em submission/Key Notes

Sempre que a demanda envolver **submission / Investment Opportunity / Key Notes / gravar no CRM** para um L-number, a primeira coisa a fazer é **puxar a linha do deal na planilha do Forms** dos diretores de aquisição:

- Arquivo: `"Stage 6(aceite verbal) ou7(LOI recebida) – Informações da Negociação".xlsx`
- Host: `apwireless-my.sharepoint.com`, site `/personal/lminozzo_apwbrasil_com_br`
- UniqueId: `b45b8db5-a7bc-4154-a201-ac714a5fc1e6`
- Chave: coluna **F** = L-number

Nunca escrever ou gravar submission sem essa consulta. O script de extração (Claude in Chrome, sem screenshot) e o mapa completo das colunas ficam na skill `apw-submission-writer`; a versão condensada para o CRM fica em `apw-crm-key-notes-writer`.

Se o L-number não estiver na planilha, avisar o Lucas antes de seguir — provavelmente o diretor não preencheu o form.

## Mapa de triagem

### Sinal: código L (Lxxxxx) ou "esse deal"
→ Perguntar: "O que precisa sobre esse deal?"
  [A] Contexto / o que rolou → apw-deal-dossier
  [B] Análise de documentos (matrícula, contrato, certidões) → apw-pre-dd-legal
  [C] Escrever o submission / Investment Opportunity → apw-submission-writer (com a planilha)
  [D] Gravar no CRM (Key Notes / Pricing Option) → apw-crm-key-notes-writer (com a planilha)

### Sinal: documento anexado (PDF/DOCX) sem contexto
→ Identificar o tipo:
  - Matrícula / certidão de inteiro teor / CCIR / CND → apw-pre-dd-legal
  - Contrato de locação ATC/SBA/Highline/IHS → apw-pre-dd-legal + apw-telecom-real-estate-counsel
  - Vistoria fotográfica / SIR → apw-sir-analyst
  - Contrato de compra e venda / DRS / cessão → apw-telecom-real-estate-counsel
  - Transcrição de reunião → apw-meeting-brief
  - Planilha de ERBs / Anatel → apw-erb-towerco-triage

### Sinal: "proposta" / "oferta" / "quanto pagar"
→ apw-proposta-comercial

### Sinal: "submission" / "IC" / "investment opportunity" / "San Diego"
→ apw-submission-writer — **abrir a planilha do Forms primeiro**

### Sinal: "reajuste" / "IGP-M" / "IPCA" / "aluguel atual" / "quanto tá pagando"
→ apw-rent-escalation

### Sinal: "bruto" / "líquido" / "gross-up" / "IR na fonte" / "Paulina"
→ apw-rent-gross-up

### Sinal: "CRM" / "Dynamics" / "gravar" / "Key Notes" / "Pricing Option"
→ apw-crm-key-notes-writer — **abrir a planilha do Forms primeiro**

### Sinal: "reporte" / "produtividade" / "diretores" / "meta"
→ apw-reporte-crm-diario

### Sinal: "SBA" + "Murilo" / "email SBA"
→ apw-email-sba-murilo

### Sinal: "Anatel" / "ERB" / "lista de torres" / "enriquece leads"
→ apw-erb-towerco-triage

### Sinal: "crédito" / "contraparte" / "counterparty" / "San Diego quer saber"
→ apw-credit-worthiness-site ou apw-counterparty-assessment

### Sinal: "radar" / "briefing telecom" / "notícias do setor"
→ apw-telecom-intel-daily

### Sinal: "cadastro no CRM" / "criar PIN" / "site novo"
→ apw-pin-creator

### Sinal: "transcrição" / "reunião" / "call" / "ata"
→ apw-meeting-brief

### Sinal: "vistoria" / "SIR" / "churn" / "vai desativar"
→ apw-sir-analyst

### Sinal: "pré-DD" / "matrícula" / "cartório" / "CAR" / "hipoteca"
→ apw-pre-dd-legal

### Sinal: "cláusula" / "minuta" / "DRS" / "cessão" / "anuência" / "vedação"
→ apw-telecom-real-estate-counsel

### Sinal: "dossiê do deal" / "o que rolou" / "me situa"
→ apw-deal-dossier

### Sinal: "navegador" / "Chrome" / "abre o site" / "acessa o CRM"
→ apw-chrome-agent-lean-compliance (instrução de ferramentas para Chrome agent)

## Regras do router

- **Nunca nomear a skill** no output — o Lucas quer o resultado, não a burocracia
- **Máximo 2 perguntas** — se ainda ambíguo após 2, chuta pelo sinal mais forte
- **Intent composto** (ex.: "pré-DD + submission + CRM"): acionar as 3 skills em sequência, declarar só "vou trabalhar nesses três pontos" sem listar skills
- **Novo deal sem contexto**: perguntar trilha (condomínio ou terreno?) + o que precisa
- **Zero screenshots** em domínio corporativo (Dynamics, SharePoint, Teams, Outlook, Power BI) — ver apw-chrome-agent-lean-compliance
- **Lucas manda só "oi"**: perguntar "O que temos hoje?" com as 4 opções mais frequentes:
  [A] Deal novo / análise de documento
  [B] Submission / IC
  [C] CRM / reporte
  [D] Contrato / cláusula

## Skills disponíveis (índice completo)

| Skill | O que faz |
|---|---|
| apw-pre-dd-legal | Pré-análise registral/cartorária, dossiê incremental, CAR, croqui |
| apw-submission-writer | Investment Opportunity / submission para o IC Radius (lê a planilha do Forms) |
| apw-crm-key-notes-writer | Grava Key Notes e Pricing Option no Dynamics 365 (lê a planilha do Forms) |
| apw-telecom-real-estate-counsel | Análise e redação de cláusulas contratuais |
| apw-deal-dossier | Dossiê de contexto de um deal por código L (CRM + email) |
| apw-rent-escalation | Extrai rent escalation, índice e data-base de contratos |
| apw-rent-gross-up | Reconcilia aluguel net/gross, IR na fonte, explica pra San Diego |
| apw-sir-analyst | Análise de vistoria técnica, risco de churn, Churn Risk Index |
| apw-proposta-comercial | Proposta comercial HTML para cedente (DRS ou Cessão) |
| apw-email-sba-murilo | Emails padronizados para Murilo (SBA Torres) |
| apw-erb-towerco-triage | Base Anatel embutida, clusteriza ERBs, deriva trilha |
| apw-credit-worthiness-site | Relatório de crédito de operadora telecom |
| apw-counterparty-assessment | Deck executivo de avaliação de contraparte |
| apw-telecom-intel-daily | Radar diário telecom BR (towercos, MNOs, ISPs) |
| apw-pin-creator | Cria lead geolocalizado no CRM a partir de contrato |
| apw-meeting-brief | Transforma transcrição de reunião em briefing executivo |
| apw-reporte-crm-diario | Reporte diário de produtividade CRM por diretor |
| apw-opp-activity-forensics | Análise forense de atividades de opp no Dynamics |
| apw-dynamics-copilot | Consulta e operação geral do Dynamics 365 |
| apw-chrome-agent-lean-compliance | Regras de ferramentas para Chrome agent |
| analise-mytower | Análise de contratos MyTower/Max cruzados com CRM |
| tower-intel-br | Inteligência de infraestrutura passiva telecom Brasil |

