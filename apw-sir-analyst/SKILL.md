---
name: apw-sir-analyst
description: >-
  Analisa um Site Inspection Report / vistoria técnica de torre de telecom (PDF/DOCX) e
  entrega um parecer de RF + risco de churn pra decidir se a APW compra o ativo. Não descreve
  a vistoria — prevê a probabilidade de a operadora desativar o site (decommission) e a APW
  perder a receita, via painel de personas (RF, asset manager de TowerCo, planejador de rede
  do carrier, underwriter) e um Churn Risk Index ponderado. Use SEMPRE que o Lucas enviar uma
  vistoria/relatório fotográfico de torre, ou perguntar "vale a pena comprar essa torre?",
  "risco de churn desse site?", "analisa a RF", "tem overlap de sinal?", "esse site vai ser
  desativado?", "por que perdemos essa torre?", falar em reduzir/antecipar churn, os 10% de
  churn, ou triar um lote de vistorias por risco. Gatilhos técnicos: antenas RF/TX, RRU,
  setores, GF/greenfield, RT/rooftop, tenancy, IHS/SBA/American Tower/TIM/Vivo/Claro/Oi. NÃO
  use para cláusula contratual, credit worthiness, counterparty assessment nem submission/IC
  (skills apw-* dedicadas).
---

# APW RF & Churn Analyst — Parecer técnico de aquisição de torre

Skill analítica APW Brasil. Lê uma vistoria técnica de site de telecom e entrega um **parecer de RF + risco de churn** que responde a uma pergunta de underwriting: *este ativo vai sobreviver os anos que a gente está precificando, ou a operadora vai desativar e a gente perde a receita?*

O business da APW (lease aggregation) compra um fluxo de aluguel de longa duração sob uma torre e paga um múltiplo por ele. **Churn — a operadora/TowerCo desativar o site e parar de pagar — é o risco existencial.** ~10% de churn de portfólio significa que 1 em cada 10 torres compradas vira prejuízo. Esta skill existe pra **mover a detecção do churn para ANTES da compra**, lendo os sinais de engenharia de rádio e de rede que a vistoria revela.

## Quando usar

Gatilhos:
- Lucas envia um Site Inspection Report / vistoria técnica / relatório fotográfico (PDF/DOCX) de uma torre
- "Vale a pena comprar essa torre / esse ativo?"
- "Qual o risco de churn / de desativação desse site?"
- "Analisa a RF / a cobertura / o overlap desse site"
- "Por que perdemos essa torre?" (post-mortem de churn)
- "Tria esse lote de vistorias por risco de churn"
- Qualquer pedido pra reduzir/antecipar churn de torres
- `/apw-sir-analyst`

## A pergunta central (não perca isso de vista)

A vistoria descreve o site **hoje**. O underwriting precisa saber o site **daqui a 5–10 anos**. O gap entre os dois é o churn. Toda a análise converge para:

> **Probabilidade de a operadora/TowerCo desativar este site dentro do horizonte de precificação — e o que torna isso mais ou menos provável.**

Tudo que a vistoria mostra (tenancy, tecnologia, torres próximas, papel de RF, tipo de site) é input pra essa estimativa.

## Cadeia de churn — entenda QUEM pode te derrubar

Antes de pontuar, mapeie a estrutura do ativo. Em site de TowerCo (IHS, SBA, American Tower, Highline) o churn tem **duas camadas**:

1. **Churn de operador (tenant)** — o carrier (TIM/Vivo/Claro/Oi) sai da torre da TowerCo.
2. **Churn de TowerCo (lease)** — sem tenant, a TowerCo desativa a torre e para de pagar o ground lease que a APW comprou.

A camada 1 dispara a camada 2. Por isso **site mono-operadora de TowerCo é duplamente frágil**: a torre tem um único tenant; se ele sai, a TowerCo não tem motivo pra manter o aluguel do terreno. Em site direto da operadora (greenfield próprio do carrier), a cadeia é mais curta mas o gatilho — racionalização de rede — é o mesmo.

Identifique no relatório: **quem é o dono da torre** (placa da torre, campo CARRIER/operadora) vs **quem é o operador de RF** (antenas instaladas). Eles raramente são a mesma entidade.

## Workflow

### Passo 1 — Extrair os fatos técnicos
Leia o relatório inteiro (não só a Seção 1). Extraia para uma ficha estruturada:

- **Identificação**: código L, endereço, coordenadas, cidade/UF, data da vistoria
- **Estrutura**: tipo (Greenfield/Rooftop/Mastro), altura, tipo de torre (autoportante/estaiada)
- **Tenancy**: quantas operadoras NO site, quem é dono da torre (TowerCo vs operadora)
- **Configuração de RF por setor**: nº de setores, antenas RF por setor, RRUs, presença de MW/TX (microondas = backhaul)
- **Tecnologia**: 2G / 3G / 4G / 5G — explícito ou inferido pela config de RRU/banda
- **Torres próximas (Seção 4/5)**: para cada uma — operadora, distância, altura, tipo (GF/RT). **Marque quais compartilham operadora com o site** (→ F1). **E marque quais são de OUTRA torreira/estrutura e poderiam hospedar o tenant do site** (→ F9): estrutura concorrente com folga de capacidade (greenfield tenancy 1, rooftop com espaço) num raio de relocação é candidata a poaching. Puxe TODAS as operadoras do entorno (não só a do site) — ex.: `anatel_lookup.py --near LAT,LNG --radius 600 --cluster`.
- **Cobertura**: qualidade reportada por operadora, papel aparente (cobertura única vs capacidade/densificação)
- **Regulatório**: situação legal/licenciamento, zoneamento, conclusão de licenciabilidade
- **Econômico**: valor da locação do site vs valor médio da região (sinal de incentivo a cortar)
- **Patologias**: estado de conservação, abandono, falta de zeladoria (sinal de site de baixa prioridade pro operador)

Se um dado crítico faltar, **não invente** — registre como gap e diga que pesa na incerteza, não no score.

### Passo 2 — Rodar o painel de personas
Avalie o site por 4 lentes (detalhe em `references/churn-rf-framework.md`). Cada uma faz UMA pergunta:

1. **Engenheiro de RF / planejamento de rede** — *este site faz trabalho de rádio real e insubstituível, ou é redundante?* (setores, bandas, RRU/MIMO, overlap, papel cobertura vs capacidade)
2. **Asset manager de TowerCo** — *quão grudado é esse tenant?* (tenancy ratio, mono vs multi, capacidade estrutural pra novo tenant)
3. **Planejador de rede do carrier** (o cara que de fato desativa) — *eu cortaria esse site pra economizar opex?* (redundância, tráfego provável, tech legada, custo)
4. **Underwriter de infra (buy-side APW/Radius)** — *o cashflow ajustado a churn justifica o múltiplo?* (tradução em preço/risco/proteção contratual)

### Passo 3 — Pontuar o Churn Risk Index (CRI)
Aplique o rubric ponderado (8 fatores, 0–100; **maior = mais risco**) detalhado em `references/churn-rf-framework.md`. Resumo dos fatores e pesos:

| # | Fator | Peso | Pior caso (10) |
|---|-------|------|----------------|
| F1 | Redundância mesmo-operador (torre próxima do MESMO carrier) | 22 | carrier presente <300m em outra torre |
| F2 | Tenancy do site (nº de operadoras) | 18 | mono-operadora |
| F3 | Geração tecnológica / exposição a sunset | 14 | 2G/3G-âncora, sem 4G/5G |
| F4 | Papel de RF (cobertura única → capacidade/redundante) | 13 | densificação urbana com overlap |
| F9 | **Migração p/ torreira concorrente vizinha (arbitragem de fee/lease)** | 12 | torreira neutra concorrente com slot <300m e fee menor; tenant sem capex recente |
| F5 | Tipo de site + capacidade estrutural pra co-location | 7 | mono-tenant que precisa reforço pra crescer |
| F6 | Regulatório / licenciamento | 6 | irregular/não verificado/contestável |
| F7 | Contraparte (operador + TowerCo): saúde e estratégia de rede | 5 | operador em consolidação/redução agressiva |
| F8 | Renda vs mercado (incentivo econômico a cortar) | 3 | aluguel muito acima do mercado |

> **F9 (novo)** captura um vetor que F1 não vê: F1 é a rede do PRÓPRIO carrier (racionalização); F9 é uma **torreira CONCORRENTE** vizinha que pode **abocanhar o tenant** por um fee menor. Peso carveado principalmente de F1 (que absorvia isso implicitamente) + F4/F5. Fichas pontuadas antes desta versão: se houver estrutura concorrente relevante no entorno, **repontuar F9**.

Bandas do CRI → leitura (probabilidades são **heurísticas de partida**, a calibrar contra o churn real da APW — ver Passo 5):

- **0–25 — Baixo** (~<5% churn no horizonte): ativo grudado, comprar é seguro do ponto de vista de RF
- **26–45 — Moderado** (~5–12%): comprável, mas vale uma proteção contratual leve
- **46–65 — Elevado** (~12–25%): só com desconto no múltiplo E/OU proteção contratual de decommission
- **66–100 — Alto/Crítico** (>25%): perfil clássico de site que a operadora corta — passar, ou comprar só com proteção forte e preço de risco

### Passo 4 — Escrever o parecer
Use o template de saída abaixo. Comece pelo **veredito** (o Lucas tem ADHD e múltiplos deals — o bottom line vem primeiro, sempre).

### Passo 5 — Fechar o loop anti-churn (o que torna isso preventivo)
Toda análise termina apontando:
- **Mitigantes acionáveis**: o que a APW pode negociar pra blindar o ativo (cláusula de notice/termination fee de decommission, exigência de 2º tenant, desconto no múltiplo, ROFR).
- **Gaps a puxar antes do IC**: o MLA/contrato real (notice de desativação?), dado de tráfego/decommission da operadora, se a torre próxima do mesmo operador é co-localizada ou complementar.
- **Contribuição pro dataset de churn**: a ficha estruturada do Passo 1 + o CRI viram uma LINHA num dataset. Se a APW logar isso pra cada site e depois marcar quais churnaram, em ~12–24 meses dá pra **calibrar os pesos empiricamente** e transformar este rubric heurístico num modelo preditivo de verdade. Sempre sugira registrar a ficha. (Ver seção "Calibração" do framework.)

## Formato de saída

ALWAYS comece com o bloco VEREDITO. Estrutura fixa:

```
## VEREDITO — L[código] · [cidade/UF]
**Churn Risk Index: [score]/100 → [banda]**
**Recomendação: [Comprar / Comprar com condições / Passar]** em 1 frase.

## 1. O que é o ativo (ficha técnica)
[5–8 bullets densos: estrutura, tenancy, dono da torre vs operador, RF, tecnologia]

## 2. Leitura de RF
[O site faz trabalho de rádio insubstituível ou é redundante? Setores, bandas inferidas,
overlap, cobertura vs capacidade. Use o glossário do framework se precisar destravar termos.]

## 3. Decomposição do risco de churn (CRI)
[Tabela: fator | nota 0–10 | peso | contribuição | racional em 1 linha — inclui F9]
[Total + banda]
[Sempre que houver estrutura de OUTRA torreira no entorno, dedicar 1-2 linhas ao vetor de MIGRAÇÃO (F9): quem é a estrutura candidata, distância, se tem folga, e por que o tenant migraria — ou não (capex recente 5G, custo de relocação, incentivo da TowerCo atual a reter flexibilizando o próprio fee).]

## 4. Painel de personas
[1 parágrafo por lente — RF, asset manager, planejador do carrier, underwriter]

## 5. Cenários (probabilístico)
[Base / Bull / Bear — o que precisaria ser verdade pra cada um, e o gatilho de churn em cada]

## 6. Minha cegueira / o que não dá pra ver na vistoria
[Honesto: tráfego real, termos do MLA, planos da operadora, 5G futuro. O que muda o veredito.]

## 7. Mitigantes & próximos passos
[Proteções contratuais acionáveis + gaps a puxar antes do IC + linha pro dataset de churn]

## 8. CRM Key Notes (English — paste-ready)
[Bloco em inglês IC-ready pro Lucas colar nas Key Notes do Dynamics — ver formato abaixo]
```

### CRM Key Notes (English) — formato fixo
SEMPRE feche o parecer com um bloco em **inglês**, prosa limpa, pronto pra colar na Investment Opportunity / Key Notes do CRM. Funde o **Inventário Solene (Seção 6)** + **Conclusão Final (Seção 7)** da vistoria com o veredito de RF/churn. Quatro parágrafos rotulados, sem bullets pesados, tom de submission APW:

```
L[código] — [Proprietário] | [endereço]

Site Inventory (per technical inspection, [data]): [tipo, área, tower height, setores/RF/RRU,
operadora(s), dono da torre vs tenant, energia, backhaul, fechamento — em inglês].

Licensing / Zoning (Final Conclusion): [zoneamento, lei municipal, conformidade de altura/recuo,
status legal/registral, observação de co-location — em inglês].

RF & Churn Assessment (APW): Churn Risk Index [score]/100 — [BANDA]. Primary drivers: [i, ii, iii].
Main mitigant: [se houver].

Recommendation: [comprar/condições/passar] + pre-IC actions: [gaps a puxar].
```
Mantenha números do relatório (área, altura, aluguel) e converta termos pro inglês de telecom (greenfield, self-supporting tower, single-tenant, RF sectors, RRUs, backhaul, co-location, decommission, termination fee). Não invente dados ausentes.

### Deliverable rico (opcional)
Quando o Lucas pedir "monta o dossiê / faz em HTML / pra mandar pro IC", gere um relatório HTML com a identidade APW usando `assets/report-template.html` como base (substitua os placeholders `{{...}}`). Salve em `/mnt/user-data/outputs/` e apresente com `present_files`. Para chat rápido / triagem de lote, fique no markdown acima.

### Triagem de lote
Se vierem vários relatórios de uma vez, NÃO escreva o parecer completo de cada um. Produza uma **tabela de triagem** (código L | tenancy | overlap mesmo-operador | tech | CRI | banda | ação) ordenada por CRI decrescente, e ofereça aprofundar os de maior risco.

## Tom e princípios
- **Bottom line primeiro.** Veredito e recomendação antes do desenvolvimento.
- **Probabilístico, não binário.** Churn é uma distribuição; dê bandas e cenários, não certezas.
- **Honesto sobre o que não vê.** A vistoria é uma foto externa. Não confunda ausência de dado com ausência de risco — e diga isso.
- **Acionável.** Todo risco vem com um mitigante ou um próximo passo.
- **Não dá conselho jurídico nem de IC final** — produz o insumo técnico de RF/churn pra decisão do Lucas e do comitê.

## Referências
- `references/churn-rf-framework.md` — metodologia completa: drivers de decommission, glossário RF/TX/RRU/MIMO/azimute, rubric detalhado fator-a-fator com tabelas de distância e de sunset tecnológico, e o loop de calibração contra o churn real. **Leia antes de pontuar** se tiver qualquer dúvida sobre um fator ou termo de RF.
- `assets/report-template.html` — esqueleto HTML com identidade APW pro deliverable rico.
