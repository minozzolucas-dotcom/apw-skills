---
name: apw-counterparty-assessment
description: Monta um "Counterparty Assessment" — deck executivo (inglês, 16:9) na identidade oficial Radius/APWireless avaliando uma operadora de telecom como contraparte de portfólio da APW Brasil. Entrega PDF + PowerPoint nativo editável e mapa interativo de ERBs quando o deal tem geografia. Use quando o Lucas precisar responder a uma dúvida do comitê (San Diego) ou de um manager sobre manter/aprovar exposição a uma operadora — quando o tema não é o ticket de um deal, mas a sustentabilidade da operadora como pagadora de longo prazo. Aciona com "counterparty assessment", "monta o deck da [operadora]", "avaliação da [Algar/Vivo/Claro/TIM/Oi] como contraparte", "robust NO do manager", ou pedido para defender um deal cuja contraparte virou pergunta estratégica. NÃO use para submission/IC (apw-submission-writer), dossê por código L (apw-deal-dossier), análise de cláusula (apw-telecom-real-estate-counsel) ou credit worthiness puro (apw-credit-worthiness-site).
---

# APW Counterparty Assessment

## O que esta skill entrega

1. **Deck executivo em PDF** — gerado de HTML/CSS via weasyprint, na identidade
   visual oficial da Radius.
2. **PowerPoint nativo editável** — mesmo deck, construído com pptxgenjs
   (texto, tabelas e gráficos como objetos reais editáveis).
3. **Mapa interativo de ERBs** (Leaflet, HTML à parte) — quando o deal é um
   ground lease com geografia, com seletor de cenários de consolidação.

O gatilho típico: um deal pequeno (ex. ground lease de ~US$25k) é barrado não
pelo tamanho, mas porque a CONTRAPARTE (a operadora) virou uma dúvida
estratégica no comitê. O deck não defende o deal — introduz e avalia a
contraparte com frieza factual.

## Princípio #1 — TOM (a lição mais cara desta skill)

O comitê Radius rejeita material que "vende". Feedback real recebido:
"several passages are a little bit naïf… lack of professionalism… we do not
need to sell internally."

Regras de tom, inegociáveis:
- Factual e seco. Afirma o dado, deixa o leitor concluir. NUNCA linguagem de
  venda: nada de "engine of the deal", verdicts triunfantes.
- A IA é a assistente, não a analista. Nunca confessar dependência de IA no
  material nem em e-mails. O analista é o Lucas.
- Honestidade sobre lacunas > número inventado. Campo marcado
  "[ to confirm with AM ]" é melhor que um número fabricado.
- Mitigante honesto. NUNCA enquadrar um risco como neutralizado quando não
  está. Ex.: "a aquisição não extingue o lease" é verdade, MAS é desonesto
  parar aí — o adquirente pode descomissionar por sobreposição de sinal. O
  mitigante reconhece o risco residual, não o varre para baixo do tapete.
- Riscos ditos abertamente. Esconder um risco destrói credibilidade quando
  descoberto. Apresentar e enquadrar.
- Não usar "defensive value of the land" como tese. O Guglielmo é explícito:
  o valor de revenda do terreno nunca motivou a decisão de investimento. Pode
  aparecer como consideração secundária, nunca como argumento central.
- "Counterparty assessment", não "deal memo". Responde à pergunta de portfólio
  sobre a operadora, não ao ticket do deal.

## Princípio #2 — IDENTIDADE VISUAL OFICIAL DA RADIUS

Extraída do template oficial APWireless-Radius_Standard (style guide no slide 1).
É a marca da empresa — seguir à risca.

Fonte: Arial, regular e bold. Só Arial.

Paleta oficial (hex exatos):
- Navy (cor primária de título) — #012B5E
- Azul primário — #1C75BB
- Azul claro — #4F91C7
- Cinza-texto (o texto é cinza escuro, NUNCA preto puro) — #5D5D5D
- Cinza-azulado (2a cor de título, captions) — #91A5A4
- Verde-oliva (destaque APW, usar com parcimônia) — #A7AF00
- Fundo suave — #F0F0F0 ; Branco — #FFFFFF

Regras de estilo do guideline:
- Títulos: CAIXA ALTA, bold, BICOLOR — primeira parte navy #012B5E, segunda
  parte cinza-azulado #91A5A4. Ex.: "EXECUTIVE summary", "RISK assessment".
- Bullets: quadrados azuis (#1C75BB). HTML: width:5px;height:5px;background.
  pptxgenjs: bullet:{code:"25AA"}.
- Texto de corpo: cinza #5D5D5D, não preto.
- Títulos de slide ~22pt.

## Princípio #3b — SLIDE DE RELACIONAMENTO & ABORDAGEM COMERCIAL

O slide de Relationship History deve integrar a ABORDAGEM COMERCIAL — não como
slide separado. Conteúdo: timeline do relacionamento + tabela das ofertas
(preço, múltiplo de aluguel, IRR implícita) + a nuance de por que não fechou.
Caso Algar (referência): 2021 Lote 1 = 63 sites reversíveis, 1a oferta R$11,3M
(66x, IRR 19,5%), revisada R$14M (82x, IRR 17,0%), não fechou — bloqueio = ativo
reversível (crédito sem lastro), e gap vs. benchmark de custo de capital da
própria Algar (IRR 8,38–10,96%). 2024 = 21 ativos não-reversíveis, oferta final
R$6,5M. A regra-chave: o motivo de um deal não fechar muitas vezes NÃO é preço —
identificar o bloqueio estrutural real (aqui, natureza do ativo) e dizê-lo.

## Princípio #3 — ESTRUTURA do deck

Capa + 11 slides (ajustar conforme o caso):
1 Cover · 2 Executive Summary · 3 Brazil Mobile Market · 4 Brazil Fixed
Broadband · 5 Operadora Snapshot (incluir sponsors institucionais, ex. GIC na
Algar — fundo soberano de Cingapura ~25,3% via Archy LLC) · 6 Financials &
Credit Rating · 7 Tower Counterparty (ex. Winity) · 8 Radius Exposure ·
9 Relationship History · 10 Risk Assessment · 11 Competitive Grid / Mapa ERBs ·
12 Consolidation Scenarios. Slides 11-12 só com risco geográfico.

## Princípio #4 — CÁLCULOS

Capital invested (quando AM não dá): soma dos aluguéis mensais × 75. Marcar
como aproximado e declarar o método. FX padrão R$/US$ = 5.00.
Mapa de ERBs (lista Anatel): contar sites por operadora e quantos têm 5G;
distância por haversine (R=6.371.000 m).
Cenários de consolidação: distância do site objeto ao site próprio mais
próximo de cada adquirente. <250m alto / 250-600m médio / >600m baixo. Empate
de tecnologia → decide qualidade do ativo físico (Greenfield > rooftop); site
sem 5G é o primeiro candidato a corte.

## Princípio #5 — FONTES

Teleco (bloqueia robôs; dados por UF via Claude in Chrome no navegador do
Lucas). Anatel (ERBs, sanções). Research institucional (tower co capital
fechado — citar contratos/emissões, não balanço inexistente). S&P/Fitch
(ratings). PPTX internos APW (histórico). Share estadual dilui posição
municipal — sempre enquadrar.

## Workflow

1 Identificar operadora e gatilho. 2 Ler uploads. 3 Pesquisar mercado.
4 Calcular (75×, ERBs, cenários). 5 Montar HTML na paleta oficial. 6 PDF via
weasyprint; conferir pageno E kickers. 7 PPTX nativo via pptxgenjs (mesma
paleta); QA visual; corrigir overlaps; parar após 1 ciclo. 8 Mapa Leaflet se
houver geografia. 9 present_files PDF+PPTX+mapa. 10 Marcar pendências reais.

## Princípio #6 — USAR O TEMPLATE OFICIAL .pptx COMO BASE

A APW tem um template oficial (APWireless-Radius_Standard, 48 slides). A capa
(slide 26) e o encerramento (slide 47) são os elementos que mais carregam a
marca. Técnica validada para reconstruir o deck "dentro" do template sem
quebrar os layouts densos:

1. Abrir o .pptx oficial com python-pptx. Editar o texto placeholder da capa
   (TextBox TITLE HERE e o subtítulo) com o título do assessment, preservando
   a formatação dos runs do template.
2. Renderizar a capa e o encerramento editados para PNG (via soffice + pdftoppm
   a 150dpi).
3. Embutir essas PNGs como background full-bleed no slide 1 e no último slide
   do deck pptxgenjs (s.background={data:...}).
4. O miolo (slides de conteúdo) é construído com pptxgenjs na paleta/regras
   oficiais — os layouts do template oficial são leves demais para tabelas de
   risco, cenários e mapas, então não servem para o miolo.

Resultado: capa e encerramento são literalmente os oficiais da Radius; o miolo
é indistinguível em identidade. python-pptx e pptxgenjs não se fundem num
arquivo — por isso a capa entra como imagem, não como slide nativo do template.

## Armadilhas conhecidas

- Logos: respeitar aspect ratio real (Radius ~1.18:1, quase quadrado).
- Logos base64 quebram str_replace — usar splice por Python em âncoras.
- Ao inserir slides, renumerar pageno E kickers.
- Tabelas 4+ colunas: table-layout:fixed + colgroup, senão estoura.
- Teleco bloqueia automação; Claude in Chrome opera no navegador do Lucas e
  não vê arquivos do ambiente; pode dar timeout se desconectado.
- PPTX nativo não é pixel-idêntico ao PDF — PDF é referência, PPTX é p/ editar.
- pptxgenjs: nunca "#" no hex; nunca opacity no hex; nunca reusar option object.

## Companion: e-mails ao manager

Reconhecer o desconforto UMA vez com classe; transformar falta de padrão em
proposta, não queixa; humor só em call; proporcionalidade do ticket como
alinhamento de escopo, não discordância.
