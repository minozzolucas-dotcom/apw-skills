# APW Brasil — Skills

Repositório de skills que operam sobre o dia a dia da Diretoria de Aquisições da APW Brasil (APWireless Brasil): pipeline no Dynamics 365, dossiês de operação, propostas comerciais, análise contratual, relatórios de time, integrações com torreiras (SBA, ATC, IHS, Highline, MyTower/Phoenix), fluxo de fechamento com o jurídico e financeiro, e inteligência setorial.

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

**Via GitHub Desktop:** editar arquivos → o app mostra as mudanças → escrever mensagem → **Commit to main** → **Push origin**.

**Via terminal:**
```bash
./push.sh                                    # timestamp automático como mensagem
./push.sh "adiciona apw-nova-skill"          # mensagem sua
```

O `push.sh` só commita se houver mudança, mostra o diff antes e faz o push.

---

## Skills

### Meta e orquestração

| Skill | O que faz |
|---|---|
| [apw-router](./apw-router) | Skill mestre — triagem conversacional e roteamento para a skill certa em qualquer demanda APW |
| [apw-brand](./apw-brand) | Identidade visual e verbal APW (paleta, tipografia, wordmark, razão social, regras de e-mail) |
| [apw-chrome-agent-lean-compliance](./apw-chrome-agent-lean-compliance) | Regras de uso do Claude in Chrome em domínios corporativos APW/Microsoft (bloqueio de screenshots em CRM/Teams) |

### Consulta e análise do CRM (Dynamics 365)

| Skill | O que faz |
|---|---|
| [apw-dynamics-copilot](./apw-dynamics-copilot) | Assistente para consultas ao Dynamics via Web API / FetchXML / OData |
| [apw-deal-dossier](./apw-deal-dossier) | Dossiê completo de uma oportunidade a partir de um código L (CRM + Outlook) |
| [apw-opp-deepdive-snippet](./apw-opp-deepdive-snippet) | Deep dive de uma opp via snippet F12 direto no console do Dynamics |
| [apw-opp-activity-forensics](./apw-opp-activity-forensics) | Análise forense palavra a palavra das descrições de atividades de uma opp |
| [apw-pool-forensics](./apw-pool-forensics) | Análise de views/listas: em que stage pegaram, por que caíram na pool, esforço real |
| [apw-onhold-reassessment](./apw-onhold-reassessment) | Reavaliação do estoque On Hold; buckets de reabordagem conforme regras vigentes de torreira |
| [apw-pipeline-reativacao](./apw-pipeline-reativacao) | Reativação de pipeline frio (Purged Pool, Surrender Pool, Sites at Risk, Carrier Owned) |
| [apw-deepdive-s3-reproposta](./apw-deepdive-s3-reproposta) | Coaching nos Stage 3 novos e repropostas criados ontem — temperatura + profundidade |
| [apw-crm-key-notes-writer](./apw-crm-key-notes-writer) | Gravação de Key Notes / Investment Opportunity em opps do Dynamics; link da Pricing Option |
| [apw-pin-creator](./apw-pin-creator) | Criação de Lead geolocalizado (PIN) a partir de contrato de site novo |
| [apw-acf-lease-fill](./apw-acf-lease-fill) | Preenchimento do Abstracted Cash Flow no tenant Radius (apwip_lease) |

### Reportes e performance do time

| Skill | O que faz |
|---|---|
| [apw-reporte-crm-diario](./apw-reporte-crm-diario) | Reporte diário de produtividade dos 14 diretores no Dynamics — Stage 1/3/Repropostas/Atividades. PNG na marca |
| [apw-calor-do-dia](./apw-calor-do-dia) | Reporte interno cruzando o que moveu de estágio no dia com o conteúdo das atividades |
| [apw-diretor-pace-score](./apw-diretor-pace-score) | Dashboard de pace dos 14 diretores via snippets Dynamics 365 (stages + owners + audit) |
| [apw-email-semanal-comercial](./apw-email-semanal-comercial) | E-mail semanal de KPIs do time comercial + 2 PNGs (consolidado e por diretor) |
| [apw-performance-patterns](./apw-performance-patterns) | Benchmark dos 14 diretores: padrões de top vs low performers no funil |
| [apw-stage1-quality-audit](./apw-stage1-quality-audit) | Auditoria de integridade da qualificação Stage 1 (sólida vs rasa vs suspeita) |
| [apw-arbitragem-lead](./apw-arbitragem-lead) | Julgamento de disputas de titularidade de lead entre diretores (0800 + código de marketing) |
| [apw-recruta-aquisicoes](./apw-recruta-aquisicoes) | Avaliação de candidatos para vaga de diretor(a) de aquisições (framework Hogan/Awair) |

### Torreiras, ativos e vistorias

| Skill | O que faz |
|---|---|
| [apw-sba-daily-routine](./apw-sba-daily-routine) | Rotina diária Lucas × Murilo (SBA); scan Outlook + planilha SBA Spread + drafts individuais |
| [apw-email-sba-murilo](./apw-email-sba-murilo) | E-mails padronizados para o Murilo/SBA a partir de dados brutos do time |
| [apw-erb-towerco-triage](./apw-erb-towerco-triage) | Triagem de ERBs via base Anatel embutida; trilha A/B e tenancy; cluster de co-location |
| [apw-mytower-acerto](./apw-mytower-acerto) | Acerto mensal de remuneração da MyTower pelos envios de contratos e leads |
| [analise-mytower](./analise-mytower) | Cruzamento de contratos MyTower/Max Aureliano com leads e opps do CRM (raio 150m) |
| [apw-sir-request](./apw-sir-request) | Pedido de SIR (vistoria de campo) à FCA Telecom com dados extraídos do Dynamics |
| [apw-sir-analyst](./apw-sir-analyst) | Análise de SIR / vistoria técnica de torre (parecer de RF + churn risk index) |
| [apw-credit-worthiness-site](./apw-credit-worthiness-site) | Relatório HTML de qualidade de crédito da operadora locatária para investidores Radius |
| [apw-counterparty-assessment](./apw-counterparty-assessment) | Deck executivo (PDF + PPT) avaliando operadora como contraparte de portfólio |

### Propostas e dossiês para o cedente

| Skill | O que faz |
|---|---|
| [apw-proposta-comercial](./apw-proposta-comercial) | Propostas HTML de Cessão de Direitos Creditórios (condomínios) e DRS (PF/PJ). Enquadramento APW como veículo de investimento com lógica de seguradora; zero anglicismos; neutralidade entre opções |
| [apw-dossie-cessao](./apw-dossie-cessao) | Material informativo de Cessão de Direitos Creditórios para condomínios (PDF 2 páginas) |
| [apw-dossie-drs](./apw-dossie-drs) | Material informativo de DRS para proprietários PF (tributação, redutores, simulação IR) |

### Jurídico e contratual

| Skill | O que faz |
|---|---|
| [apw-telecom-real-estate-counsel](./apw-telecom-real-estate-counsel) | Advogado(a) sênior PhD em direito imobiliário aplicado a telecom (análise de cláusula) |
| [apw-pre-dd-legal](./apw-pre-dd-legal) | Pré-DD registral/documental em Stage 7 (matrícula, ata, edital, POP) + e-mail ao jurídico |
| [apw-dd-certidoes](./apw-dd-certidoes) | Coleta em paralelo do kit de DD (certidões, matrícula, ônus, IPTU, POP) via agentes browser |
| [apw-dd-report-review](./apw-dd-report-review) | Leitura crítica de report de DD de escritório externo (ES Advogados etc.) |
| [apw-negociacao-contrato](./apw-negociacao-contrato) | Negociador para fechar deal: diagnóstico + reframe + redline pronto |
| [apw-negociacao-fechamento](./apw-negociacao-fechamento) | Variação da anterior focada em fechamento (versão em consolidação com apw-negociacao-contrato) |
| [apw-rent-escalation](./apw-rent-escalation) | Reajuste vigente a partir de cadeia de aditivos (IPC-FIPE, IGP-M, IPCA, INPC) |
| [apw-rent-gross-up](./apw-rent-gross-up) | Reconciliação líquido × bruto de aluguel; e-mail em EN para underwriting/San Diego |
| [apw-triagem-cessao-drs](./apw-triagem-cessao-drs) | Triagem jurídica em lote de sites: livres para notificar cessão / constituir DRS |

### Submission ao comitê de investimento

| Skill | O que faz |
|---|---|
| [apw-submission-writer](./apw-submission-writer) | Texto de Investment Opportunity em inglês para o IC da Radius |
| [apw-stage7-sub](./apw-stage7-sub) | E-mail de subida da operação de Stage 7 (LOI recebida) para Stage 8 (Submission) |

### Fechamento

| Skill | O que faz |
|---|---|
| [apw-closing-call-brief](./apw-closing-call-brief) | Briefing deal-a-deal da call semanal de closing/processing com o jurídico |
| [apw-request-for-wire](./apw-request-for-wire) | E-mail de RFW a partir da Closing Statement + ISW, com análise de variância |
| [apw-mfiles-upload](./apw-mfiles-upload) | Upload padronizado de documentos de deal ao M-Files (via agente de navegador) |

### Reuniões

| Skill | O que faz |
|---|---|
| [apw-meeting-brief](./apw-meeting-brief) | Transcrição crua (sem pontuação, sem quem fala) → briefing executivo estruturado |

### Financeiro operacional

| Skill | O que faz |
|---|---|
| [apw-reembolso-cartao](./apw-reembolso-cartao) | Fechamento mensal do cartão corporativo (Form C/C + PDF consolidado + Excel + e-mail Luiz) |
| [apw-vendor-payment](./apw-vendor-payment) | Processamento de pagamento de fornecedor (NF-e + CNPJ + Vendor Form → PDF + Excel + e-mail AP) |

### Inteligência setorial

| Skill | O que faz |
|---|---|
| [apw-telecom-intel-daily](./apw-telecom-intel-daily) | Radar telecom (torreiras, MNOs, ISPs, veículos concorrentes, Anatel) — e-mail HTML editorial |

### Adjacentes (Braus, dentro deste repo por convenção de prefixo)

| Skill | O que faz |
|---|---|
| [apw-braus-competitive-intel](./apw-braus-competitive-intel) | Radar semanal de inteligência competitiva de jiu-jitsu apparel para Braus / Alliance Fight |

---

## Notas de segurança

Este repositório contém instruções que refletem a operação da APW Brasil. Todo dado sensível — comprovantes bancários, CPF/CNPJ, contratos, dumps do CRM, planilhas de deal, exportações do M-Files, base Anatel de ERBs — fica **fora** do repositório por regra do `.gitignore`. Se algo com esse teor precisa ficar versionado, deve ir em repositório privado separado.

Skills que envolvem inteligência interna (regra APW sobre torreiras, playbook de negociação, arbitragem entre diretores, avaliação de contrapartes) devem ser mantidas em repositório privado. A visibilidade do repositório é revisada periodicamente.
