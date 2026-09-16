---
name: apw-opp-activity-forensics
description: >-
  Análise forense palavra-a-palavra das descrições de atividades
  (tasks/follow-ups) de uma oportunidade no Dynamics 365 CRM da APW Brasil. Lê o
  histórico completo de uma opp ao longo de anos e de vários donos e extrai o
  que nenhum campo estruturado do CRM revela — divergências de dados (operadora
  real vs. Anatel vs. planilha, aluguel declarado vs. calculado, deriva de
  preço), red flags de receita e de site (atraso de aluguel, retirada de
  equipamento, descomissionamento), mapa político de contrapartes e diagnóstico
  estratégico do estágio real do deal. Use SEMPRE que o Lucas colar uma view de
  atividades do CRM (linhas com Subject, Description, Activity Owner, Status,
  Created On, Actual End), mencionar "investigar atividades", "análise forense
  de deal", "o que aconteceu nessa opp", "histórico do Lxxxxx", "forensics de
  atividade", ou enviar um código L pedindo para entender o que se passou. NÃO
  use para puxar dados do CRM (apw-dynamics-copilot) nem análise contratual
  (apw-telecom-real-estate-counsel).
---

# APW Opportunity Activity Forensics

Investiga **palavra por palavra e contexto por contexto** as descrições das atividades de uma oportunidade do Dynamics 365. O CRM tem campos estruturados (stage, owner, valor) — mas a verdade operacional de um deal vive na prosa solta dos follow-ups. Esta skill lê essa prosa como um detetive lê um arquivo: cada frase é evidência.

## Por que isso importa

Uma view de atividades é um **arquivo histórico em camadas**. Uma única opp pode acumular 40+ tasks ao longo de 5-7 anos, escritas por 3-5 donos diferentes, cada um com seu estilo, suas abreviações e seus vieses. Lida superficialmente, é ruído. Lida forensicamente, ela revela:

- **Contradições entre fontes** que ninguém reconciliou — a operadora que a Anatel registra ≠ a da planilha ≠ a do contrato físico.
- **O gatekeeper real** do deal — frequentemente não é a pessoa no campo "contato".
- **Sinais de risco enterrados** numa frase de passagem ("retiraram uns equipamentos") que valem mais que o stage atual.
- **Por que o deal não anda** — e se a causa é preço, política, ou perfil da contraparte.

O trabalho é transformar esse arquivo em **inteligência acionável**, sem perder nenhuma evidência relevante. A saída de maior peso é o diagnóstico estratégico com próximo passo — é o que o Lucas lê primeiro — mas ele só é confiável se sustentado pelas divergências de dados, pelo mapa político e pelas red flags.

## Workflow

### Passo 1 — Ingerir e normalizar

O input padrão é **texto colado de uma view do CRM**: linhas tabulares com colunas `Subject | Description | Activity Owner | Status | Created On | Actual End`. As descrições frequentemente têm quebras de linha internas, bullets e mensagens de WhatsApp coladas — o parser precisa aguentar isso.

Use o script de parsing para estruturar os dados de forma robusta:

```bash
python3 scripts/parse_activities.py <arquivo_de_input.txt>
```

O script lida com descrições multi-linha, identifica o código L, ordena cronologicamente por `Created On`, e devolve um JSON estruturado. Se o input vier muito sujo e o script falhar, leia `references/parsing-edge-cases.md` para tratar manualmente.

O parser também aceita **JSON de atividades já extraídas via `apw-dynamics-copilot`**, caso o Lucas cole esse formato — é um caminho de entrada secundário, suportado, mas o fluxo normal é texto colado da view.

**Sempre ordene cronologicamente (mais antigo → mais recente) antes de analisar.** O CRM normalmente lista do mais recente pro mais antigo; a história só faz sentido na ordem em que aconteceu.

### Passo 2 — Leitura forense (o núcleo da skill)

Leia **toda** atividade, da primeira à última. Não amostre, não pule "tasks automáticas" — até um "Assignment of Lxxxxx" marca uma troca de dono que muda a cadência. Para cada descrição, faça as sete perguntas forenses:

1. **Que fato novo isso introduz?** (valor, nome, data, condição)
2. **Isso contradiz algo dito antes ou em outra fonte?** (operadora, aluguel, preço, prazo)
3. **Há um número aqui?** Capture-o exato. Números são âncoras.
4. **Há uma pessoa nova?** Quem é, que papel, que poder tem.
5. **Há um sinal de risco?** (atraso, retirada de equipamento, silêncio, "surrender")
6. **Qual o tom/perfil da contraparte revelado?** ("desconfiada", "confusa", "sempre viajando")
7. **O que mudou o estado do deal?** (avançou, travou, mudou de dono, ressuscitou)

A leitura completa abastece os seis eixos de extração abaixo. Consulte `references/forensic-lenses.md` para o catálogo completo de padrões a caçar — sinais de risco telecom, vocabulário de gatekeeper, marcadores de deriva de preço, divergências de dados típicas, jargão interno APW (FUP, ARI, CI, SURRENDER, Pricing Desk).

### Passo 3 — Extrair os seis eixos

Toda análise produz estes seis blocos. Se um eixo não tiver evidência, diga "Sem evidência nas atividades" — nunca invente.

**A. Linha do tempo reconstruída.** Cronologia enxuta dos marcos reais (não toda task — só o que mudou o deal). Cada marco: data, dono, evento, e a frase-evidência entre aspas. Marque visivelmente os pontos de virada: morte (SURRENDER), ressurreição, travamento.

**B. Mapa político de contrapartes.** Quem é quem. Para cada pessoa: nome, organização, papel, poder no deal (decisor / influenciador / gatekeeper / executor), e perfil comportamental extraído do texto. Marque explicitamente quem **trava** e quem **destrava** — esse é o item mais acionável do mapa.

**C. Divergências de dados.** Seção própria. Toda vez que duas ou mais fontes discordam sobre o mesmo fato, registre — esse é frequentemente o achado mais valioso da leitura palavra a palavra. Formato de tabela: Fato | Fonte A (valor) | Fonte B (valor) | Fonte C | Implicação para o deal. Os suspeitos de sempre: operadora (texto da atividade vs. Anatel vs. planilha vs. contrato físico), valor do aluguel (declarado de memória vs. calculado exato), qual contrato a APW realmente possui, prazo contratual. Não concilie silenciosamente as contradições — exiba-as. Uma divergência que ameaça o deal também deve ser citada nas Red Flags (eixo D), com a severidade, mas seu lugar de registro completo é aqui.

**D. Red flags / riscos.** Sinais que ameaçam o deal ou o site. Classifique cada um: 🔴 Crítico (risco de o site/deal morrer) / 🟡 Atenção / 🟢 Resolvido. Sempre cite a frase-evidência e a atividade de origem. Atraso de aluguel, retirada de equipamento e descomissionamento são os riscos clássicos. Quando uma divergência de dados (eixo C) representa risco — ex.: precificar a operadora errada — ela aparece também aqui como red flag, remetendo ao eixo C.

**E. Deriva de preço.** Histórico de todos os valores propostos/pedidos, em ordem, com data. Mostre o movimento da âncora e o gap entre o que a contraparte pede e o que é viável. Pode ser uma tabela curta.

**F. Diagnóstico estratégico + próximo passo (a saída principal).** Síntese: em que estágio o deal *realmente* está (≠ stage do CRM, frequentemente), qual o bloqueador raiz, qual o provável blind spot do dono atual, e os próximos passos mais alavancados. Use raciocínio probabilístico ("~60% de chance de o deal travar na administradora, não no preço"). Este é o eixo que o Lucas lê primeiro — entregue-o com a maior densidade.

### Passo 4 — Entregar

Produza **os dois artefatos**, salvos em `/mnt/user-data/outputs/`:

1. **Briefing Markdown** (`forensics-Lxxxxx-briefing.md`) — executivo, scannável, ADHD-friendly. Estrutura fixa no template abaixo.
2. **Dashboard HTML dark** (`forensics-Lxxxxx-dashboard.html`) — timeline navegável, mapa político em cards, divergências em tabela, red flags destacadas, diagnóstico em evidência. Use o template em `assets/dashboard-template.html` como base.

Apresente os arquivos com `present_files`. No corpo da resposta do chat, entregue o **diagnóstico estratégico + próximo passo direto**, em português casual — é o que o Lucas lê primeiro.

## Template do briefing Markdown

SEMPRE use esta estrutura exata (8 seções — diagnóstico e próximo passo fecham o documento):

```markdown
# Forensics — L[código] [nome da opp]

> [Uma frase: o que essa opp é e o veredito de uma linha]

**Janela analisada:** [primeira data] → [última data] · **[N] atividades** · **[N] donos**

## 1. O que realmente está acontecendo
[2-4 frases. O estado real do deal, não o do CRM.]

## 2. Linha do tempo reconstruída
[Marcos. Data — dono — evento. Frase-evidência entre aspas. Marcar viradas.]

## 3. Mapa político
[Cada contraparte: nome · org · papel · poder · perfil. Marcar quem trava / destrava.]

## 4. Divergências de dados
[Tabela. Fato | Fontes em conflito (com valores) | Implicação para o deal.]

## 5. Red flags
[Lista classificada com 🔴🟡🟢. Cada uma com frase-evidência. Divergências que
representam risco aparecem aqui também, remetendo à seção 4.]

## 6. Deriva de preço
[Sequência curta de valores com datas. Movimento da âncora. Gap atual.]

## 7. Provável blind spot
[O viés ou ponto cego do dono atual do deal.]

## 8. Diagnóstico e próximo passo
[Estágio real do deal. Bloqueador raiz. 1-3 ações concretas em ordem de
prioridade. Raciocínio probabilístico.]
```

## Princípios da investigação

- **Toda afirmação é rastreável.** Nenhuma conclusão sem a frase-evidência que a sustenta. Cite a atividade (data + dono).
- **Nunca invente para preencher.** Eixo sem evidência = "Sem evidência nas atividades". Um deal mal documentado é em si um achado.
- **Contradição é ouro, não erro.** Quando duas atividades (ou fontes) discordam sobre o mesmo fato, isso não é ruído a limpar — é o achado mais valioso. Registre na seção de Divergências com as fontes em conflito explícitas; não concilie silenciosamente.
- **Números exatos, sempre.** "Aluguel ~14k" e "R$ 15.286,34" são fatos *diferentes*. Capture os dois e marque a divergência.
- **Leia o subtexto.** "Não senti firmeza nela" e "SURRENDER - sumiu" carregam tanta informação quanto um valor. Tom é dado.
- **O stage do CRM mente.** Uma opp pode estar "Open/Stage 3" e estar morta há um ano, ou estar "ressuscitada" depois de um surrender. O diagnóstico vem do texto, não do campo.
- **Respeite o compliance.** Não persista dados do CRM em arquivos além dos dois artefatos de saída solicitados. Não envie dados de CRM para ferramentas externas. O processamento é local.

## Arquivos da skill

- `scripts/parse_activities.py` — parser robusto de view de atividades (texto colado ou JSON do Dynamics) → JSON estruturado e ordenado.
- `references/forensic-lenses.md` — catálogo de padrões: sinais de risco telecom, vocabulário de gatekeeper, marcadores de deriva de preço, divergências de dados, jargão interno APW. Leia no Passo 2.
- `references/parsing-edge-cases.md` — como tratar inputs sujos quando o parser falha.
- `assets/dashboard-template.html` — esqueleto do dashboard HTML dark.
