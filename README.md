# APW Brasil — Skills

Repositório de skills que operam sobre o dia a dia da Diretoria de Aquisições da APW Brasil (APWireless Brasil): pipeline no Dynamics 365, dossiês de deal, propostas comerciais, análise contratual, relatórios de time, integrações com torreiras (SBA, ATC, IHS, Highline, MyTower/Phoenix), fluxo de closing com o jurídico e financeiro, e inteligência setorial.

Cada skill é uma pasta autocontida com um `SKILL.md` (frontmatter + instruções) e, quando faz sentido, uma subpasta `references/` com scripts, snippets e templates.

---

## Estrutura do repositório

```
apw-skills/
├── README.md                       ← este arquivo
├── .gitignore
├── push.sh                         ← commit + push em um comando
│
├── <nome-da-skill>/
│   ├── SKILL.md
│   ├── references/                 ← scripts, snippets, templates
│   └── assets/                     ← logos, imagens fixas (opcional)
```

Convenção: uma skill = uma pasta = um `SKILL.md`. Nome da pasta em `kebab-case`, sempre em minúsculas, com prefixo `apw-` para as skills APW.

---

## Como commitar

**Via GitHub Desktop (recomendado):**
1. Abrir GitHub Desktop → repo `apw-skills`
2. Editar / adicionar arquivos na pasta local
3. O app mostra o que mudou → escrever mensagem embaixo → clicar **Commit to main** → clicar **Push origin**

**Via terminal:**
```bash
./push.sh                                    # timestamp automático como mensagem
./push.sh "adiciona apw-negociacao-contrato" # mensagem sua
```

O `push.sh` só commita se houver mudança e faz o `push` para `origin/main`.

---

## Skills no repositório

| Skill | O que faz |
|---|---|
| [apw-reporte-crm-diario](./apw-reporte-crm-diario) | Reporte diário de produtividade dos 14 diretores no Dynamics — Stage 1, Stage 3, Repropostas, Atividades. Entrega PNG na marca. |
| [apw-calor-do-dia](./apw-calor-do-dia) | Reporte interno cruzando o que moveu de estágio no dia com o conteúdo das atividades. Radar de "calor" e qualificações com bandeira. |
| [apw-diretor-pace-score](./apw-diretor-pace-score) | Dashboard de pace dos 14 diretores via snippets Dynamics 365 (stages + stage owners + audit). Sub-status Early Stage vs Conversão. |
| [apw-crm-key-notes-writer](./apw-crm-key-notes-writer) | Gravação de Key Notes / Investment Opportunity em oportunidades do Dynamics 365; escolha e link da Pricing Option; processamento em lote via planilha de submission. |
| [apw-stage7-sub](./apw-stage7-sub) | E-mail de subida do deal de Stage 7 (LOI recebida) para Stage 8 (Submission), endereçado ao jurídico interno (Michelle, Anderson, Márcia Sena; cc Diogo). |

---

## Roadmap — skills a migrar para este repositório

Skills que rodam hoje no ambiente e serão trazidas para o repo conforme forem estabilizando. Agrupadas por função.

### Meta / orquestração
- `apw-router` — skill mestre; triagem conversacional e roteamento para a skill certa
- `apw-brand` — identidade visual e verbal APW (paleta, tipografia, wordmark, razão social, regras de e-mail)
- `apw-chrome-agent-lean-compliance` — regras de uso do Claude in Chrome em domínios corporativos

### Consulta e análise do CRM (Dynamics 365)
- `apw-dynamics-copilot` — assistente para consultas ao Dynamics via Web API / FetchXML / OData
- `apw-deal-dossier` — dossiê completo de uma oportunidade a partir de um código L (CRM + Outlook)
- `apw-opp-deepdive-snippet` — deep dive de uma opp via snippet F12 no Dynamics
- `apw-opp-activity-forensics` — análise forense palavra a palavra das atividades de uma opp
- `apw-pool-forensics` — análise de views/listas de oportunidades (por que caíram na pool, em que stage foram pegas)
- `apw-onhold-reassessment` — reavaliação do estoque On Hold; buckets de reabordagem
- `apw-pipeline-reativacao` — reativação de pipeline frio (Purged, Surrender, Sites at Risk, Carrier Owned)
- `apw-deepdive-s3-reproposta` — coaching nos Stage 3 novos e repropostas criados ontem
- `apw-pin-creator` — criação de Lead geolocalizado (PIN) a partir de contrato de site novo
- `apw-acf-lease-fill` — preenchimento do Abstracted Cash Flow no tenant Radius (apwip_lease)

### Reportes e performance
- `apw-email-semanal-comercial` — e-mail semanal de KPIs para o time comercial + PNGs de metas
- `apw-performance-patterns` — benchmark dos 14 diretores; padrões de top vs low performers
- `apw-stage1-quality-audit` — auditoria de integridade da qualificação Stage 1
- `apw-arbitragem-lead` — julgamento de disputas de titularidade entre diretores
- `apw-recruta-aquisicoes` — avaliação de candidatos para vaga de diretor(a) de aquisições

### Torreiras e ativos
- `apw-sba-daily-routine` — rotina diária com o Murilo Gonçalves (SBA Torres); scan Outlook + Spread + drafts
- `apw-email-sba-murilo` — e-mails padronizados para o Murilo/SBA a partir de dados brutos
- `apw-erb-towerco-triage` — triagem de ERBs via base Anatel embutida; trilha A/B e tenancy
- `apw-mytower-acerto` — acerto de remuneração da MyTower pelos envios de contratos e leads
- `analise-mytower` — cruzamento de contratos MyTower/Max Aureliano com leads do CRM
- `apw-sir-request` — pedido de SIR (vistoria de campo) à FCA Telecom
- `apw-sir-analyst` — análise de SIR / vistoria técnica de torre (parecer de RF + churn risk index)
- `apw-credit-worthiness-site` — relatório de qualidade de crédito da operadora locatária
- `apw-counterparty-assessment` — deck de counterparty assessment (marca Radius/APW)

### Propostas e dossiês para cliente
- `apw-proposta-comercial` — propostas HTML de Cessão de Direitos Creditórios e DRS
- `apw-dossie-cessao` — material informativo de Cessão (condomínios)
- `apw-dossie-drs` — material informativo de DRS (proprietários PF/PJ)

### Jurídico / contratual
- `apw-telecom-real-estate-counsel` — advogado(a) sênior em direito imobiliário de telecom
- `apw-pre-dd-legal` — pré-DD registral em Stage 7 e handoff ao jurídico
- `apw-dd-certidoes` — coleta em paralelo do kit de DD (certidões, matrícula, ônus, IPTU, POP)
- `apw-dd-report-review` — leitura crítica de report de DD de escritório externo
- `apw-negociacao-contrato` / `apw-negociacao-fechamento` — negociador para fechar deal; diagnóstico + redline
- `apw-rent-escalation` — reajuste vigente a partir de cadeia de aditivos (índice + data-base)
- `apw-rent-gross-up` — reconciliação líquido × bruto de aluguel; e-mail em EN para San Diego
- `apw-triagem-cessao-drs` — triagem jurídica em lote de sites (livres para notificar cessão / DRS)

### Submission e comitê de investimento
- `apw-submission-writer` — texto de Investment Opportunity em EN para o IC da Radius

### Closing e fechamento
- `apw-closing-call-brief` — briefing deal-a-deal da call semanal de closing/processing
- `apw-request-for-wire` — e-mail de RFW a partir da Closing Statement + ISW
- `apw-mfiles-upload` — upload padronizado de documentos de deal ao M-Files

### Reuniões
- `apw-meeting-brief` — transcrição crua → briefing executivo estruturado

### Financeiro operacional
- `apw-reembolso-cartao` — fechamento mensal do cartão corporativo (Form C/C + PDF + Excel + e-mail)
- `apw-vendor-payment` — processamento de pagamento de fornecedor (NF-e + CNPJ + Vendor Form)

### Inteligência setorial
- `apw-telecom-intel-daily` — briefing telecom (torreiras, MNOs, ISPs, lease aggregators, Anatel)

---

## Notas de segurança

Este repositório contém instruções que refletem a operação da APW Brasil. Todo dado sensível — comprovantes bancários, CPF/CNPJ, contratos, dumps do CRM, planilhas de deal, exportações do M-Files — fica **fora** do repositório por regra do `.gitignore`. Se algo com esse teor precisa ficar versionado, deve ir em repositório privado separado.

Skills que envolvem inteligência interna (regra APW sobre torreiras, playbook de negociação, arbitragem entre diretores, avaliação de contrapartes) devem ser mantidas em repositório privado. A visibilidade do repositório é revisada periodicamente.
