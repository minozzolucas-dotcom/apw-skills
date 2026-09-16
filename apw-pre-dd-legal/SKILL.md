---
name: apw-pre-dd-legal
description: >-
  Use na etapa de Stage 7 da APW (proposta comercial aceita) quando o Lucas enviar QUALQUER
  documento de um deal para pré-análise registral/cartorária e documental: matrícula, certidão de
  inteiro teor, contrato de locação, cessão, ata, edital, CCIR, comprovante de aluguel (POP), LOI,
  certidões, ou thread do jurídico. Aciona com "analisa essa matrícula", "confere essa ata", "chegou
  o edital", "pré-DD do Lxxxx", "atualiza o dossiê", "quais riscos", "cadê o croqui", usucapião,
  cadeia dominial, gravame, execução fiscal, cancelamento de locação, divergência de área, quórum.
  Também gera o E-MAIL-RESUMO AO JURÍDICO no handoff de Stage 7 — "monta o e-mail pro jurídico",
  "handoff do Lxxxx", "deal foi pro Stage 7". A pré-DD é INCREMENTAL: cada documento atualiza o
  mesmo dossiê (cadeia de contrato/aditivos, evolução de área, croqui top-down, veredito de vedação
  à cessão). NÃO use para gravar no CRM (apw-crm-key-notes-writer) nem para parecer/redação de
  cláusula (apw-telecom-real-estate-counsel).
---

# APW Pré-DD Legal

Pré-análise registral, cartorária e documental dos deals da APW Brasil (lease
aggregation telecom), na etapa de **Stage 7**. Atua como especialista em direito
imobiliário com visão cartorária/registral, lendo cada documento conforme ele
chega e mantendo um **dossiê vivo** do caso.

## Onde a skill entra no funil

A proposta comercial já foi aceita — existe um **"ok" comercial** do deal. O
próximo passo é a **questão documental**: descobrir, o mais rápido possível, se a
estrutura jurídica pretendida é viável e o que a trava. A skill é o **aparelhador**
dessa coleta — quanto antes o kit de certidões e documentos chega, melhor.

A pré-DD **não decide se o deal é bom** (isso o comercial já fez). Ela descobre se
a estrutura **fecha juridicamente** e aponta o que falta e o que trava.

## Princípio fundamental

**É uma peneira, não um parecer.** A pré-DD separa o que passa do que precisa de
olhar jurídico. Onde algo for ambíguo, marcar e devolver ao Lucas/jurídico —
**nunca "atestar" sozinho**. Parecer jurídico e redação contratual definitiva são
da `apw-telecom-real-estate-counsel` e do jurídico humano.

**O dossiê é vivo e incremental.** O caso não chega pronto — os documentos pingam
ao longo de semanas. Cada peça nova **atualiza** o mesmo dossiê do L-number, não
se reanalisa tudo do zero. Documento que ainda não chegou não trava nada: vira
**pendência apontada dentro do dossiê**.

**Output único: o dossiê.** Toda análise — de um documento só ou do caso inteiro —
é uma atualização do dossiê. O que muda é a maturidade.

**A conferência é sempre contra a condição comercial daquele deal.** Prazos,
valores e estrutura aprovados variam por deal. A skill confere os documentos
contra o "ok" comercial do Stage 7, **nunca contra números fixos**.

## As duas trilhas — bifurcar logo no início

A APW tem **dois mundos de deal, com objeto jurídico diferente**. A skill
identifica o tipo na primeira interação e carrega a trilha certa. Não é o mesmo
checklist com blocos ligados/desligados — são análises diferentes.

| | Trilha A — Cessão de Créditos | Trilha B — Imobiliária |
|---|---|---|
| Tipo de deal | Condomínio (antena em rooftop/área comum) | Terreno / PF (torre infield em terreno) |
| Natureza | Cessão de Direitos Creditórios — **não é operação imobiliária** | Operação imobiliária (compra e venda ou DRS) |
| Objeto jurídico | Crédito locatício + procuração pública 30 anos | Direito real sobre o imóvel |
| Matrícula | **Fora de escopo** — não há transferência de direito real | **Centro da análise** |
| Objetivo final | Procuração pública por 30 anos sobre a área do contrato | Averbar o DRS na matrícula / escritura de C&V |
| Burocracia | Mais enxuta | DD completa, como uma compra e venda corriqueira |
| Maior desafio | **Divergência de área** + dúvidas no contrato de cessão | Matrícula limpa + área/proporção no terreno |

**Primeira pergunta da skill ao rodar, se o tipo não estiver claro:** *"Este deal
é condomínio (Cessão de Créditos) ou terreno/PF (operação imobiliária)?"*

Em ambas as trilhas, o objetivo final é **averbar/garantir o direito da APW** — no
terreno, o DRS na matrícula; no condomínio, a procuração pública de 30 anos é o
equivalente funcional.

---

# TRILHA A — Cessão de Direitos Creditórios (condomínio)

Deal de antena em rooftop/área comum de condomínio. **Não é operação imobiliária:**
não há transferência de direito real, então **não se analisa a matrícula do
imóvel**. A APW obtém o crédito locatício + uma **procuração pública por 30 anos**
sobre a área do contrato — é isso que dá poderes equivalentes a um direito na
matrícula. DD mais enxuta, com foco próprio.

Arquivo de referência: `referencia/modelo-ata-edital-cessao.md` — modelo de ata,
texto-modelo APW e requisito de edital. **Carregar e ler esse arquivo** ao
analisar ata ou edital.

## Checklist Trilha A — <X de Y itens>

**Bloco A1 — Assembleia / edital**
- ⬜ Edital de convocação — cessão para a APW em **pauta exclusiva e separada**
- ⬜ Ata de assembleia — texto conforme o modelo APW
- ⬜ Quórum — 50% + 1 dos **presentes**
- ⬜ Convenção do condomínio + regimento interno
- ⬜ Ata de eleição do síndico em vigor — síndico realmente eleito
- ⬜ Certificado digital do síndico (assinatura do instrumento)

**Bloco A2 — Condomínio (pessoa)**
- ⬜ CNPJ do condomínio ativo e regular
- ⬜ Processos / passivos relevantes do CNPJ do condomínio
- ⬜ CPF do síndico — capacidade para representar

**Bloco A3 — Contrato / receita**
- ⬜ Contrato de locação telecom + aditivos
- ⬜ POP — comprovante de pagamento de aluguel recente (define a TowerCo)
- ⬜ Contrato de Cessão de Direitos Creditórios — dúvidas/considerações da contraparte
- ⬜ Anuência/notificação da TowerCo conforme a matriz

**Bloco A4 — Área (o maior desafio da finalização)**
- ⬜ Croqui da instalação — medição in loco pelo terceirizado
- ⬜ Reconciliação croqui in loco × área do contrato

## Como analisar cada documento da Trilha A

### Edital de convocação — checar ANTES da ata
A cessão de direitos creditórios para a APW Brasil **tem de ser item de pauta
exclusivo e separado**. Se entrou em "assuntos gerais" / "outros assuntos", ou
agregada a outro item → 🟥 **a deliberação é viciada**, a ata não se salva mesmo
com quórum e texto perfeitos. É condição de validade da assembleia.

### Ata de assembleia — conferir contra o modelo APW
Ler `referencia/modelo-ata-edital-cessao.md` e conferir, no corpo da ata:
1. **Quórum** — 50% + 1 dos presentes. Conferir nº de presentes × nº de aprovações.
2. **Ratificação da autorização** da instalação em área comum, com o contrato de
   locação identificado (operadora original, data, aditivos, incorporações,
   locatária atual, prazo, aluguel atual).
3. **Exposição do síndico** das condições da cessão — prazo da cessão *(variável,
   conferir contra a condição comercial do deal)*.
4. **Contrapartida da APW** — valor e prazo de pagamento *(variáveis, conferir
   contra a condição comercial)*.
5. **Aprovação tríplice**: (a) ratifica a instalação; (b) aprova celebrar o
   Contrato de Cessão; (c) **autoriza a outorga de procuração pública** com
   poderes plenos. O item (c) é o objetivo da trilha — ata sem ele não sustenta a
   operação → 🟥.
6. **Cláusula de notificação de novos proprietários**.
7. **Cláusula de cessão dos reajustes** (aluguel vigente + correções futuras).

Faltando 5, 6 ou 7, ou divergência nos variáveis vs. a condição comercial → 🟥 ou
⚠️ conforme a gravidade. Texto fora do padrão APW mas equivalente → ⚠️ VERIFICAR.

### Eleição do síndico
Conferir que o síndico que assina foi **realmente eleito** — ata de eleição
vigente, dentro do mandato. Síndico com mandato vencido → 🟥.

### CNPJ do condomínio
Verificar processos e passivos relevantes do CNPJ. Passivo grande pode gerar
constrição sobre o crédito locatício cedido → ⚠️, encaminhar ao jurídico.

### Divergência de área — REGRA DE DECISÃO FECHADA
O maior desafio da finalização em condomínio. O contrato de locação em geral não
tem croqui recente; quando o terceirizado mede in loco, aparece divergência —
outra área, equipamento numa sala além do terraço do rooftop.

**Regra APW: vale sempre a área apurada in loco, e sempre a MAIOR área.**

A skill não trata isso como pendência aberta nem renegociação caso a caso: aponta
a divergência e **já diz qual área prevalece** — a in loco, a maior. Registrar no
dossiê o número que vale e a origem (croqui do terceirizado).

### Contrato de Cessão
Quando enviado, a maioria dos casos volta com bastante dúvida/consideração da
contraparte. Listar as considerações como itens; encaminhar ao jurídico o que for
redação contratual.

---

# TRILHA B — Operação imobiliária (terreno / PF)

Deal de torre infield instalada em terreno. **É operação imobiliária de verdade** —
DD completa como uma compra e venda corriqueira. Estrutura: **compra e venda** ou
**Direito Real de Superfície (DRS)**. Decide-se quanto o equipamento representa no
terreno todo. Objetivo final: **averbar o DRS na matrícula** (ou escriturar a C&V).

A pré-DD da Trilha B exige **todo o conjunto documental de uma compra de imóvel**.
O dossiê **não pode passar a impressão de "quase fechado"** enquanto faltam peças.
O checklist nasce pré-populado, tudo ⬜, com **contador de maturidade** "X de Y".

A skill **expande só os blocos aplicáveis** ao deal. Bloco que não se aplica entra
como **uma linha N/A com o motivo** (ex.: `Bloco D — Vendedor PJ — N/A (vendedor é
PF)`) — não some do dossiê, custa uma linha. **"Aplicável" se revisa:** se um
documento novo revelar que um bloco N/A incide (ex.: PJ na cadeia dominial),
reabrir o bloco expandido.

## Checklist Trilha B

**Bloco B1 — Imóvel / registral**
- ⬜ Matrícula atualizada / certidão de inteiro teor (ficha completa, recente)
- ⬜ Certidão negativa de ônus reais e de ações reais/reipersecutórias
- ⬜ Cadeia dominial conferida (R-/AV-) ou título originário (usucapião) verificado
- ⬜ Descrição classificada — georreferenciada ou precária; área conferida
- ⬜ Planta / memorial descritivo / georreferenciamento
- ⬜ Habite-se ou averbação de construção (imóvel urbano edificado)
- ⬜ Contrato de locação telecom averbado na matrícula (ou anotar que não está)

**Bloco B2 — Tributário do imóvel**
- ⬜ IPTU do exercício quitado + carnê / certidão negativa de tributos imobiliários
- ⬜ ITR quitado + **CCIR atualizado em nome do vendedor** (rural — trava lavratura)
- ⬜ Inscrição cadastral municipal regular e em nome do proprietário atual
- ⬜ Certidão negativa de foro/laudêmio (se enfitêutico)

**Bloco B3 — Vendedor pessoa física**
- ⬜ Documento de identidade + CPF
- ⬜ Comprovante de estado civil — certidão de casamento/nascimento; pacto antenupcial
- ⬜ Certidões de feitos: distribuidores cíveis, execuções fiscais, execuções gerais
- ⬜ Certidão negativa trabalhista (CNDT) e de protesto
- ⬜ Certidões fiscais — Receita Federal (PGFN), estadual, municipal
- ⬜ Certidão negativa de interdição, tutela e curatela (capacidade civil)
- ⬜ Anuência do cônjuge coproprietário

**Bloco B4 — Vendedor pessoa jurídica**
- ⬜ Contrato/estatuto social consolidado + última alteração; ata de eleição da diretoria
- ⬜ Cartão CNPJ ativo e situação cadastral regular
- ⬜ Certidões: CND federal (PGFN/RFB), estadual, municipal, FGTS, trabalhista
- ⬜ Certidões de falência, recuperação judicial e concordata
- ⬜ Distribuidores cíveis e execuções fiscais da PJ
- ⬜ Prova de poderes de quem assina (procuração / representação societária)

**Bloco B5 — Estrutura e área**
- ⬜ Definição da estrutura — compra e venda ou DRS
- ⬜ Área do equipamento × área total do terreno — proporção apurada
- ⬜ Croqui / medição in loco da área ocupada pela torre
- ⬜ DRS: confirmar que a TowerCo permite a estrutura (ver matriz)

**Bloco B6 — Locação / receita**
- ⬜ Contrato de locação telecom + todos os aditivos
- ⬜ POP — comprovante de pagamento de aluguel recente (define a TowerCo)
- ⬜ Confirmação de vigência da locação (sem cancelamento averbado na matrícula)
- ⬜ Anuência da TowerCo / notificação do programa conforme a matriz

**Bloco B7 — Instrução do deal / fechamento**
- ⬜ LOI assinada e arquivada no M-Files (versão final)
- ⬜ SIR aprovado
- ⬜ Minuta do instrumento (DRS / C&V) validada
- ⬜ Tabela de custas dentro da planilha WS / IRR conferido
- ⬜ Cartório/tabelião alinhado para a lavratura

## Como analisar cada documento da Trilha B

### Matrícula / certidão de inteiro teor
A peça-rainha. Verificar **nesta ordem**:
1. **Identificação** — número e endereço batem com contrato/LOI/IPTU? Divergem →
   🟥. A LOI às vezes traz a matrícula do lote vizinho; cruzar com IPTU.
2. **Proprietário registrado** = vendedor do deal? Conferir cadeia (R-/AV-).
   "Venda em duplicidade" = red flag de evicção → jurídico.
3. **Gravames e ônus** — hipoteca, penhora, alienação fiduciária, indisponibilidade,
   usufruto, inalienabilidade, averbação premonitória, arresto, ações reais. Uma
   ficha só não fecha a leitura — exigir inteiro teor atualizado.
4. **Qualidade da descrição** — georreferenciada (coordenadas dos vértices) ou
   precária (só confrontantes). Registrar qual.
5. **Divergência de área** — campo "área total" vs. medidas dos lados vs. contrato.
   Lados batem mas o campo não fecha → provável erro de digitação, ⚠️ VERIFICAR,
   pendência = retificação.
6. **Contrato averbado?** — locação telecom consta como averbação? Averbado →
   resolve a pendência de benfeitoria. **Cancelamento de locação averbado** → 🟥
   red flag de receita.
7. **Estado civil / capacidade** — partilha pendente é item jurídico; vendedor
   idoso → certidão de interdição; cônjuge coproprietário assina o contrato.

### Título — usucapião
Usucapião transitada/registrada é título **originário** — reconstrói a propriedade
do zero, ignora a cadeia anterior, sem vendedores a auditar. Título forte.
- **Usucapião extrajudicial** (art. 1.238 §único CC) resolve **cadeia dominial
  quebrada** — matrículas bloqueadas/canceladas por provimento de corregedoria
  (ex.: Provimento 08/2021-CJC do PA) por origem de procedência duvidosa.
- Verificar: intimação de Município, Estado e União/SPU sem impugnação;
  confrontantes assinaram DRL; CNIB sem indisponibilidade.
- Cruzar matrícula nova × antigas: a nova **substitui** as canceladas; anotar a
  equivalência (ex.: "12.463 substitui 7.929 + 7.930; lotes unificados").
- **Alteração na descrição reabre prazo** — renotificar a TowerCo com os dados
  novos e aguardar os 30 dias de novo.

### Título de propriedade municipal sob condição resolutiva (regularização fundiária)
Comum no Norte (ex.: AP, via leis municipais de regularização). O imóvel nasce de um **Título de
Propriedade Sob Condição Resolutiva** (Município → adquirente). Separar **dois comandos** do
título, que têm prazos e efeitos diferentes:
- **Item da condição resolutiva propriamente dita** — obrigações de **quitar + registrar** o
  título dentro de um prazo (ex.: 5 anos). Descumprir esse item é o que poderia **desfazer a
  propriedade** (resolução).
- **Cláusula de restrição de alienação** (ex.: "VIII") — proíbe **alienar antes de liberada** a
  condição.

Vender **dentro da carência** fere a restrição de alienação, **não** a condição resolutiva (se as
obrigações de quitar/registrar foram cumpridas). Leitura provável: a transferência fica
**ineficaz/inqualificável no registro** até a liberação — é **impedimento registral, não gatilho
automático de resolução**. Reforço: se a Prefeitura deu **quitação** e nunca acionou a resolução,
o risco residual se neutraliza com o **termo de extinção** da Prefeitura. Isto é pré-triagem — a
validade da extinção é do counsel.

Prazos a checar: **carência** (ex.: 3 anos da outorga) e **prazo da condição** (ex.: 5 anos).
Decorridos ambos + quitação + obrigações cumpridas → a condição é **extinguível por averbação**.
O tempo cura o impedimento: o que era prematuro na outorga fica maduro depois.

**Caminho crítico (ordem obrigatória):** (1) Prefeitura emite termo de extinção da condição →
**averbação** na matrícula; (2) **registro da escritura** em nome do vendedor (o R- que falta),
com certidões atuais; (3) só então a APW instrui (**DRS recomendado** para evitar ROFR). Pôr o
**R- como condição precedente na LOI**, ônus/custo do lado vendedor, com **pagamento split**
(parte na escritura, saldo no registro do título da APW). Exigir certidões de feitos/execuções
do **antecessor** pelo período do gap (imóvel anos em nome de quem não é o vendedor do deal).

### PF vs. PJ
Imóvel que sai de **PJ inapta** para **PF** do mesmo dono **elimina** o risco de
fraude à execução fiscal via PJ. Confirmar pelo CPF na matrícula.

### CCIR / documento rural
Tabelião costuma exigir **CCIR atualizado** para lavrar escritura de imóvel rural —
em nome do vendedor. CCIR de terceiro não serve. **CCIR pendente trava a
lavratura** — pendência dura.

### Estrutura e área no terreno
Decidir entre C&V e DRS, e apurar quanto o equipamento representa no terreno todo.
A medição in loco também vale aqui — registrar a área ocupada e a proporção.

**O DRS não exige desmembramento** — grava a área da torre sem fracionar o imóvel,
a matrícula segue íntegra. Pendência de desmembramento não bloqueia o DRS; é nota.
Desmembramento é requisito de venda, não de DRS.

### DRS e direito de preferência (ROFR) — NÃO incide
**DRS não dispara o direito de preferência da locação.** A preferência legal (art.
27 da Lei 8.245/91) é um direito de **adquirir o imóvel** em igualdade de condições —
alcança venda, promessa de venda, cessão/promessa de cessão de direitos e dação
(alienação da propriedade). O **DRS não é compra e não transfere a propriedade**: o
dono mantém a matrícula e concede um direito real de superfície. Não há "aquisição"
para a TowerCo igualar, então a preferência **não tem objeto**.

Por isso, **mesmo quando o contrato/locação lista "instituição do direito de
superfície" numa cláusula genérica de preferência** — e mesmo com ROFR averbado na
matrícula — instituir o DRS **não exige oferta de ROFR à TowerCo**. Não é bloqueador
nem pendência dura: registrar como **NOTA**. Coerente com a matriz (ATC autoriza DRS
sem anuência prévia formal). A redação contratual final é do jurídico.

---

# Comum às duas trilhas

## POP — comprovante de pagamento de aluguel
**O POP define a TowerCo. Regra de ouro.** Quem aparece como pagador no POP/extrato
é a torreira do deal. Contrato em nome de operadora + POP de torreira = cessão já
consumada, **não é divergência**. Cruzar form da diretora × contrato × POP — o POP
vence. POP faltante/desatualizado = risco de receita aberto → ⬜.

## Cruzamento de operadora e geolocalização (ANATEL)
O POP define a TowerCo (quem paga). A ANATEL define o CARRIER ATIVO e a tecnologia
no ponto — cruzar as coordenadas do contrato/CRM com as estações licenciadas.

**Como cruzar (automático, sem pedir planilha):** a base Anatel nacional está
EMBUTIDA na skill `apw-erb-towerco-triage` (SMP jul/2026, 111.296 estações).
Sempre que o dossiê tiver coordenada ou endereço, rodar:

```bash
python3 /mnt/skills/user/apw-erb-towerco-triage/scripts/anatel_lookup.py \
  --near=<LAT>,<LNG> --radius 150 --cluster --json
# sem coordenada: --addr "TRECHO DO LOGRADOURO" --mun "Município" --uf XX
```

Registrar no dossiê: operadoras licenciadas no ponto (tenancy), ClassInfraFis
(rooftop×greenfield — confere com a trilha do deal?), tecnologias (5G/3500 =
site investido) e distância. Se NÃO houver estação em 300 m → achado de risco:
coordenada ruim, site novo ou possível descomissionamento — investigar antes
de avançar. As coordenadas dos pontos retornados alimentam direto a técnica de
ponto-no-polígono abaixo.
- Carrier com 5G ativo (banda 3500) = site investido → indício de baixo
  decomissionamento (churn/RF é da apw-sir-analyst; aqui é só nota).
- Linhagem contratual pode divergir do carrier atual (ex.: contrato Oi/TNL → torre
  hoje servida por TIM após a venda da Oi Móvel). Não é divergência — registrar a migração.
- CUIDADO COM VIZINHO: sites colados confundem (ex.: nº 56 × nº 68). Conferir qual
  L-number/endereço é o objeto e se o vizinho está Decommissioned/Lost no CRM.
  Confirmar no SIR que a estação ativa está na estrutura da TowerCo do nosso número.


## Acordo judicial homologado como contrato vigente — e o índice que não está nele
Quando a locação foi formalizada/renegociada por **transação judicial homologada**, esse acordo
é **título executivo** e costuma ser o **instrumento vigente** da relação, sobrepondo-se ao
contrato de locação original. Tratar o acordo como o "contrato atual" e o contrato antigo como a
base histórica da relação.

Atenção ao índice: o acordo homologado pode fixar **apenas o valor e o prazo, SEM cláusula de
índice de reajuste**. Quando isso ocorre, o reajuste observado na prática decorre de um
**contrato de locação em separado** que o próprio acordo menciona (e que muitas vezes ainda não
foi obtido). Regras:
- **Não afirmar o índice a partir do gross-up.** Um gross-up do líquido que bate com a magnitude
  do IPCA/IPC-FIPE é **sanity check do valor**, não prova do índice contratual.
- Registrar como **lacuna documental**: obter o contrato de locação assinado (verificar se
  **novou** o contrato antigo — ex.: IPC-FIPE de 2009 — ou se é continuidade) e o **POP atual**.
- **Operadora-âncora ≠ locatária/pagadora.** O contrato/processo pode estar em nome da operadora
  (ex.: Vivo/Telefônica) e de um proprietário antigo, mas o **POP define a pagadora** (ex.:
  "American Tower ... Cessão de Infra" = ATC). Não confundir a âncora hospedada com quem paga.

## Técnica — Verificação de coordenada: torre dentro do polígono da matrícula

Quando a matrícula é **georreferenciada** (vértices SIRGAS-2000) e há coordenada ANATEL da ERB, dá pra confirmar objetivamente se a torre cai dentro do lote adquirido:

1. Reconstruir o polígono da matrícula pelos vértices (E,N) no datum dela (ex.: UTM 22N / MC-51 → EPSG:31976). Conferir área/perímetro contra os valores oficiais da matrícula (tolerância pequena).
2. Converter a coordenada ANATEL (lat/lon SIRGAS-2000, EPSG:4674) para o **mesmo datum projetado** (pyproj) e rodar **ponto-no-polígono** (shapely).
3. **Interpretar com a tolerância da ANATEL:** coordenadas ANATEL têm precisão real de dezenas de metros; estações "co-locadas" no mesmo site costumam vir a 10–20 m uma da outra. Um ponto cair poucos metros fora da divisa **não** invalida — é ruído.
4. **Veredito padrão:** se os pontos caem sobre/no lote (mesmo com um deles a poucos metros da divisa), tratar como "ativo sobre o lote da matrícula" e recomendar **amarrar o footprint exato (torre + área locada) por levantamento topográfico no DD formal** — padrão para compra e venda greenfield. Plotar os pontos ANATEL sobre o polígono no croqui.

Snippet (pyproj + shapely): converter EPSG:4674→datum da matrícula, `Polygon(vertices).contains(Point(e,n))`, e medir `exterior.distance` para reportar a folga em metros.

## Achados de risco — peneira + cláusula de blindagem
Achado de risco não mata o deal por padrão. A skill classifica e, quando o risco é
**contornável**, sugere a estrutura da cláusula de blindagem — sempre marcando que
**a redação final é do jurídico**.

| Achado | Classificação | Encaminhamento |
|---|---|---|
| Execução fiscal contra o cedente/vendedor, penhora deferida | ⚠️ contornável | Cláusula de blindagem: declara ciência, afirma bens/renda suficientes, compromete o "Preço" à quitação, CESSIONÁRIA não se sub-roga, cedente segue único responsável |
| Ônus quitável (dívida pequena, tributo) | ⚠️ contornável | Segregar responsabilidade no instrumento, exigir baixa ou condicionar pagamento |
| Energia da antena nunca paga (condomínio) | ⚠️ contornável | Cláusula específica de energia para a cobrança não atingir a APW |
| Cessão em "assuntos gerais" no edital | 🟥 estrutural | Deliberação viciada — refazer a convocação e a assembleia |
| Síndico com mandato vencido | 🟥 estrutural | Sem poder de representação — regularizar a eleição |
| Cancelamento de locação averbado na matrícula | 🟥 estrutural | Confirmar com POP e operadora se há contrato vigente |
| Cadeia dominial quebrada, matrícula bloqueada | 🟥 estrutural até resolver | Regularização (usucapião) reconstrói o título |
| Cláusula de vedação a cessão/DRS da TowerCo | depende da TowerCo | Ver matriz |
| ROFR / direito de preferência averbado e o deal é **DRS** | NÃO incide | DRS não é alienação — a preferência não tem objeto. Nota, não bloqueia. Redação final do jurídico. |

Cláusula de blindagem-modelo (execução fiscal) — estrutura, não redação final:
(i) declara ciência da ação e penhora; (ii) declara bens/rendas suficientes e
compromete o Preço à quitação; (iii) o débito jamais afeta a operação; (iv)
CESSIONÁRIA não se sub-roga, único responsável até baixa das constrições.

## Matriz de TowerCo — capacidade por estrutura
- **ATC (American Tower)** — autoriza cessão e DRS sem anuência prévia formal.
  Cláusula genérica de vedação ATC não é bloqueador → NOTA.
- **SBA** — contrato veda cessão/superfície (cláusula 7.2). Não é bloqueador: a
  APW opera o SBA Program — notifica, a SBA concede anuência; o desconto de
  aluguel é a contrapartida. Cláusula SBA = nota cinza.
- **Highline e IHS** — vedam cessão/DRS/alienação → sem caminho por cessão ou DRS.
  Único caminho: compra do imóvel. Condomínio → inviável. Bloqueador real (🟥),
  registrar a compra como alternativa.
- **Phoenix (PTI)** — compra e venda sim; não reconhece DRS. Estruturar por compra.
- Resumo: ATC/SBA fazem tudo; Highline/Vivo/TIM fazem Cessão e DRS se não houver
  vedação; Claro/TBSA fazem C&V e Cessão condicionada; IHS/QMC/BTC/GTS só C&V.
- Equivalência de nomes: Global Sites → Highline; T4U → Highline; Centennial →
  IHS; CSS → IHS; GTS → SBA; ZSites → Zoppone; Winity → Pátria. Referência
  completa: `referencia_torreiras_APW.html` na pasta da skill `apw-crm-key-notes-writer`.
- Outras → analisar caso a caso ou acionar `apw-telecom-real-estate-counsel`.

## Croqui top-down — OBRIGATÓRIO em rooftop/condomínio

Sempre que o deal for **rooftop** (Trilha A condomínio, ou Trilha B com antena em
laje), o dossiê **tem de incluir o croqui top-down**: o retângulo da **área do
contrato em escala** sobreposto ao **footprint da laje visto de cima** (visão tipo
Google Maps por cima). Não é opcional, não é "quando útil" — é entregável fixo. Se o
Lucas precisa pedir "cadê o mapinha", a skill falhou.

- **Área do contrato**: usar a medida do aditivo vigente (ex.: 6,80 × 5,80 m =
  39,44 m²). Desenhar o retângulo **em escala**, com barra de escala (10 m).
- **Laje**: com matrícula georreferenciada/planta, usar medidas reais. Sem isso, **medir a
  laje no Google Earth Web** (régua/polígono — ver "Medição por Google Earth Web") e, em
  último caso, **estimar por proporção** (medidas da convenção + fotos da fachada) e
  **rotular "aproximado"**. Nunca fabricar vértices — laje precária é reconstrução pelas
  medidas, sempre marcada como estimada.
- **Posição**: colocar o retângulo onde o contrato descreve (ex.: "ao lado da caixa
  d'água, no topo"); marcar caixa d'água, torre/treliça e antenas conforme as fotos.
- **Painel lateral**: área do contrato, **histórico de aumentos de área** (cada
  aditivo), área estimada da laje e **proporção área/laje** (ex.: ≈ 5%).
- **Regra de área**: vale a **in loco, a maior** — o croqui é indício, não prova;
  ponto-em-polígono é indício. Sempre dizer qual área prevalece.
- **Render**: SVG inline no chat; para o PDF, SVG→PNG (`cairosvg`) embutido base64.

## Croqui do lote — OBRIGATÓRIO também em Trilha B (terreno / greenfield)

**Todo dossiê de Trilha B (terreno/PF, torre infield) inclui o croqui top-down do
lote + área locada — sem esperar o Lucas pedir "cadê o mapa".** Vale a mesma regra
do rooftop: entregável fixo, não "quando útil". Quando **área locada = área total do
imóvel**, o polígono do lote **é** a área objeto do DRS — desenhar o lote é desenhar
a área locada.

**Escada de origem dos vértices (usar a primeira que existir — nunca fabricar):**
1. **Matrícula georreferenciada** → vértices reais (SIRGAS-2000). Plotar polígono em
   escala, conferir área/perímetro contra a matrícula; plotar a coordenada ANATEL/torre
   e a folga até a divisa (técnica ponto-em-polígono).
2. **Coordenadas no Anexo do contrato** (croqui do site / laudo de vistoria — ex.: as 4
   "COORDENADAS DO SITE" do Anexo II) → reconstruir o polígono por essas coordenadas,
   projetar (ENU local ou UTM), calcular a área por shoelace e **conferir contra a
   nominal da matrícula** (tolerância de dezenas de metros na coordenada é normal; ex.:
   235 m² pelas coords × 250 m² nominais = OK). Rotular **indiciário**.
3. **Matrícula precária (só confrontantes)** e sem coords no contrato → reconstruir o
   terreno pelas **medidas dos lados** (vértices por interseção de círculos); rotular
   **reconstrução aproximada** (quadrilátero com 4 lados e nenhum ângulo não é
   determinado). Conferir área reconstruída × declarada. Torre = **ponto** do laudo,
   "posição aproximada", nunca polígono.
4. **Sem nada disso** → **GOOGLE EARTH WEB — obrigatório, não é opcional.** Quando não
   houver georreferenciamento na matrícula NEM coordenadas no contrato/anexos, a skill
   **entra no Google Earth Web e mede** — terreno e torre. Procedimento fechado na seção
   "Medição por Google Earth Web" abaixo. Sempre **indiciário**.
5. **Fallback do fallback** — imagem de satélite ruim/desatualizada, lote não identificável:
   estimar por ancoragem em dois pontos reais de rua + azimute derivado + medidas da
   matrícula (padrão usado no L1354712), e **registrar explicitamente que a medição por
   Google Earth não foi conclusiva**. Nunca omitir a tentativa.

Em qualquer caso: rodapé "croqui indiciário — uso interno APW Brasil"; recomendar
**amarrar o footprint exato (torre + área) por levantamento topográfico no DD formal**
(padrão greenfield). Nunca inventar vértice que documento nenhum fornece. Render
SVG→PNG (`cairosvg`) embutido no PDF; SVG/PNG inline no chat.

## Medição por Google Earth Web — quando NÃO há georreferenciamento

**Gatilho (automático, sem o Lucas pedir):** matrícula com descrição precária (só
confrontantes, "fundos até o igarapé", sem área, sem vértices) **E** contrato/anexos
sem coordenadas do site. Nesse cenário a skill **não** entrega "vértices indisponíveis"
e segue — ela **vai medir**.

**Vale para as duas trilhas:** Trilha B mede o **lote + footprint da torre**; Trilha A
mede o **footprint da laje** do prédio (a mesma régua resolve a proporção área/laje).

### Procedimento (Claro in Chrome / agente de navegador)
1. Abrir `https://earth.google.com/web/` e navegar até o ponto de partida — nesta ordem
   de confiança: coordenada ANATEL da ERB (`anatel_lookup.py`) → geocodificação do
   endereço do contrato → nº do imóvel na rua pelo Street View.
2. **Confirmar que é o site certo antes de medir.** Cruzar com as **fotos da torre** do
   deal (tipo de estrutura, muro, portão, edificações vizinhas, postes/rede aérea) e com
   o `ClassInfraFis` da ANATEL (Greenfield × Rooftop). Site vizinho colado é o erro
   clássico — se não der pra distinguir, marcar ⚠️ e **não** cravar.
3. **Ferramenta Medir** (régua) → modo **polígono**: contornar o lote pelos limites
   visíveis (muro, cerca, testada, divisas). Ler **área** e **perímetro**.
4. **Régua em modo linha** para cada lado do lote — anotar comprimento por lado. É isso
   que se confronta com as medidas da matrícula (ex.: testada de 5,50 m).
5. **Coordenadas dos vértices**: clicar em cada vértice e ler lat/long na barra inferior
   (ou "Copiar link desta vista" em cada canto). Registrar em WGS84/SIRGAS-2000 com
   **6 casas decimais**, na ordem SW → SE → NE → NW.
6. **Torre**: repetir para o footprint da torre/área locada — centro da estrutura
   (coordenada do ponto) + as 4 pernas quando visíveis, e o quadrado/retângulo da área
   cercada. Anotar a **cota da base** se disponível.
7. **Anotar a data da imagem** exibida pelo Google Earth (canto inferior) e, se houver,
   comparar com o histórico de imagens — imagem antiga pode não mostrar a torre.

### O que sai disso e onde entra no dossiê
- **Tabela de vértices** (lote e torre): ponto · lat · long · lado · extensão (m).
- **Área medida** × **área/medidas da matrícula** → linha de reconciliação. Divergência
  material vira achado, não nota de rodapé.
- **Área locada do contrato dentro do lote medido?** Ponto-em-polígono / conferência
  dimensional. Se a área locada **não couber** no lote medido → 🟥 (o DRS não pode gravar
  o que não está na matrícula) → pendência de **levantamento topográfico + retificação de
  área (art. 213 LRP)**.
- Os vértices alimentam direto o **croqui top-down obrigatório**.

### Regras duras
- **Sempre indiciário.** Google Earth é indício qualificado, **nunca** substitui memorial
  descritivo, levantamento topográfico ou georreferenciamento registral. Rótulo obrigatório
  no croqui e na tabela: *"medição indiciária por imagem de satélite — Google Earth Web,
  imagem de <data>"*.
- **Precisão declarada**: erro típico de ±1–3 m em zona urbana; pior em relevo/vegetação
  e em imagem oblíqua. Declarar a margem, não entregar número seco.
- **Nunca fabricar vértice** que a imagem não permita ver. Divisa encoberta por
  vegetação/telhado → marcar o lado como **estimado** e dizer qual.
- **Não usar** a medição do Google Earth para "resolver" divergência de área contra a
  matrícula. Ela **evidencia** a divergência; quem resolve é topografia + cartório.
- Sem acesso ao navegador na sessão, entregar as **coordenadas de partida + o roteiro
  acima** como pendência instruída — nunca deixar o item em branco.

## Cadeia contratual e de aditivos — bloco fixo do dossiê

O dossiê **sempre** traz a cadeia completa do contrato, em tabela, do original ao
aditivo vigente. Não basta "aluguel R$ X" — mostrar **como se chegou nele**.

Para cada peça: **data · locatária na época · aluguel · área · índice · prazo ·
o que mudou**. Aditivos **faltantes** entram como linha ⬜ (não sumir — a lacuna é
pendência). Inconsistência de numeração/datas entre aditivos (ex.: dois "2º
aditivos") é achado a registrar.

| # | Data | Locatária | Aluguel | Área | Índice | Prazo | Mudança |
|---|------|-----------|---------|------|--------|-------|---------|
| Orig | dd/mm/aaaa | ... | R$ ... | ... m² | ... | ... | celebração |
| 1º | ... | ... | ... | ... | ... | ... | ... |
| Nº (vigente) | ... | ... | **R$ ...** | **... m²** | ... | ... | rege hoje |

Sub-bloco **Evolução de área** (alimenta o croqui): cada salto de área com o aditivo
de origem e o % de variação. Sub-bloco **Reconciliação do aluguel**: do valor-base do
aditivo vigente, aplicar a escalation (índice + data-base) ano a ano até o aluguel do
POP e confirmar que **bate**. Linhagem da locatária (operadora → torreira por
incorporação) é nota, não divergência.

## Cláusulas de vedação à cessão — onde olhar e o veredito por torreira

O dossiê **sempre** responde, explicitamente: *existe cláusula que bloqueia a cessão
de créditos? Se existe, ela tem efeito para esta torreira?* Nunca deixar implícito.

**Onde olhar** (contrato + TODOS os aditivos):
- Cláusula de **cessão/transferência** — distinguir quem pode ceder. Cláusula que
  trata da **LOCATÁRIA** ceder é permissiva e **não restringe o LOCADOR**. O que
  importa é vedação ao **LOCADOR (condomínio)** ceder o crédito locatício.
- **Direito de preferência (ROFR)** — alcança **compra do imóvel**, não cessão de
  crédito (cessão de crédito ≠ alienação). Registrar, não bloquear.
- **Anuência × notificação** — cessão de **crédito** (recebível) precisa só de
  **notificação** ao devedor (art. 290 CC), não de anuência. Cessão de **contrato**
  (posição) precisa de anuência. Documento/edital falando "cessão do contrato" quando
  a estrutura APW é cessão de créditos = **linguagem solta**: condomínio é **sempre
  cessão de direitos creditórios**, segue como cessão de crédito.

**Veredito por torreira (REGRA — aplicar SEMPRE que achar cláusula de vedação):**
- **ATC (American Tower)** — autoriza cessão e DRS. **Qualquer cláusula de vedação à
  cessão NÃO tem efeito** → **nota cinza**, nunca bloqueador. Não trava o deal.
- **SBA** — veda no papel (cláusula 7.2), mas a APW opera o SBA Program: notifica, a
  SBA concede anuência (contrapartida = desconto de aluguel). Cláusula = nota cinza.
- **Highline / Vivo / TIM** — fazem cessão de crédito e DRS **se não houver vedação
  expressa ao LOCADOR**. Na cessão de crédito, só notificação; cláusula que restringe
  a LOCATÁRIA não conta.
- **Claro / TBSA** — C&V e cessão condicionada → caso a caso.
- **IHS / QMC / BTC / GTS / Phoenix (PTI)** — vedam de fato → caminho é **compra**;
  em condomínio é inviável → **bloqueador real (🟥)**.

Sempre dizer no dossiê: a cláusula encontrada (citar onde), a torreira do POP e o
**veredito** (tem efeito / não tem efeito / bloqueador). Onde for ambíguo, ⚠️ e
jurídico — nunca atestar sozinho.

## Não inferir contrato/receita sem prova

Crédito recebido de uma operadora no extrato (ex.: PIX da Claro) **não prova**
contrato direto — pode ser rateio, reembolso, evento pontual. Marcar como **indício a
confirmar**, nunca afirmar "tem contrato direto com X". Receita fora do POP do deal só
vira "segundo deal" depois de confirmada. O POP do contrato objeto é a única prova da
receita e da torreira.

## Estrutura do dossiê (no chat)

```
DOSSIÊ PRÉ-DD — L<número> · <nome do caso>   [TRILHA A / TRILHA B]
Atualizado com: <documentos já analisados>

SÍNTESE
<2-4 linhas: o que o caso é, trilha, estrutura pretendida, onde está>

CADEIA CONTRATUAL E ADITIVOS
[tabela: # · data · locatária · aluguel · área · índice · prazo · mudança]
Evolução de área: <cada salto, aditivo de origem, % variação>
Reconciliação do aluguel: <base do aditivo vigente → escalation → POP, bate?>

CHECKLIST DE PRÉ-DD — <X de Y itens resolvidos>
[checklist da trilha; blocos não-aplicáveis como 1 linha N/A com motivo]
✅ resolvido — <documento>   ⚠️ ressalva — <o que verificar>
🟥 corrigir — <o que está errado>   ⬜ pendente — <documento que falta>

VEDAÇÃO À CESSÃO
<cláusula encontrada (onde) · torreira do POP · veredito: tem efeito / não tem
efeito (ATC/SBA) / bloqueador (IHS etc.)>

ACHADOS POR DOCUMENTO
<documento> → <leitura, selo, o que prova / o que NÃO prova>

CROQUI TOP-DOWN  [rooftop/condomínio — obrigatório]
<área do contrato em escala sobre a laje (estimada/real), com proporção área/laje>

RISCOS E DOC FALTANTE
<numerado, com encaminhamento>

PENDÊNCIAS ANTES DO FECHAMENTO
<numerado>
```

O dossiê vive **dentro da conversa atual**. Ao atualizar, reescrever o dossiê
inteiro — o Lucas tem sempre a foto completa numa mensagem só (ADHD-friendly). Em
conversa nova, pedir que ele cole o último dossiê ou os documentos-chave.

## Dossiê PDF para o M-Files (quando o Lucas pedir)
- **Nome do arquivo (REGRA FIXA):** `dossie_preDD_L<número>.pdf` — `preDD` é string
  fixa, não data. Sem espaço, sem acento.
- Gerar **HTML** e converter para **PDF** (Playwright/Chromium headless, `page.pdf()`).
- **Zero referência a IA/assistente.** Voz de quem fez a diligência.
- Linguagem objetiva, institucional, português. Tom de pré-triagem.
- Estrutura: identificação do caso → síntese + trilha → **cadeia contratual e
  aditivos (tabela) + evolução de área** → checklist com selos → **veredito de
  vedação à cessão** → achados por documento → **croqui top-down (obrigatório em
  rooftop)** → riscos → pendências → conclusão. Rodapé: uso interno,
  conversões/croquis indiciários.
- Selos honestos: CONFIRMADO (verde), RESSALVA/VERIFICAR/NOTA (âmbar),
  CORRIGIR/jurídico (vermelho), PENDENTE (cinza). Não suavizar.
- Fotos da torre: sempre incluir se houver no lote.
- Croqui top-down (rooftop = **sempre**): SVG, coordenadas/escala em painel lateral;
  para o PDF converter SVG→PNG (`cairosvg`) e embutir base64. Georreferenciada →
  vértices reais; precária → reconstrução pelas medidas dos lados, rotulada
  "aproximada". Nunca fabricar vértices. Ponto-em-polígono é indício, não prova.

### Anexos do dossiê (pacote único do deal)
Quando o caso amadurece, o dossiê fecha com dois anexos depois da Conclusão:

- **Anexo A — Investment Opportunity / Key Notes (EN, IC-ready)** — *opcional, sob pedido.*
  Texto institucional em inglês para o campo Key Notes (`apwip_opportunitysummary`) do
  Dynamics 365 e a submissão ao IC da Radius. O TEXTO é produzido pela `apw-submission-writer`
  / `apw-crm-key-notes-writer`; aqui ele só é **embutido** como pacote único do deal. A pré-DD
  continua não gravando nada no CRM.
- **Anexo B — Transcrição literal (verbatim) dos trechos-chave** — *só quando os PDFs-fonte
  estão em mãos.* Reprodução fiel dos trechos materiais de cada documento: matrícula (R-/AV-,
  descrição/área); título (cláusulas da condição resolutiva e restrição de alienação); escritura
  (preço, partes, ciência da carência); contrato/acordo de locação (aluguel, prazo, índice,
  cessão, ROFR, sigilo). Convenção de destaque: **amarelo = ponto que sustenta a tese; vermelho =
  ponto de risco/atenção.** Cada trecho seguido de uma linha "Leitura:" (1-2 frases). Marcar
  `[sic]`/`[?]` onde o original abrevia ou está ilegível. Respeitar cláusula de sigilo de acordo
  judicial (uso restrito interno/DD). **Regra dura:** o Anexo B só é possível com o documento-fonte
  **relido** nesta sessão — nunca parafrasear de memória/resumo como se fosse verbatim. Em conversa
  nova sem os PDFs, pedir o re-anexo antes de prometer o Anexo B.

### CAR — Cadastro Ambiental Rural (imóvel rural, Trilha B)
Quando o deal for Trilha B (terreno/PF), a skill deve:
1. CONSULTAR o SICAR público automaticamente:
   - URL: consultapublica.car.gov.br/publico/imoveis/index
   - Buscar por CPF do vendedor ou por varredura no mapa pelo município
   - Extrair: número CAR (formato UF-IBGE7-hash), situação (AT/PE/CA),
     dataDisponibilizacao, área registrada, dataCriacao
   - Se o site bloquear acesso automatizado (robots.txt), registrar como
     ⬜ pendente e orientar o Lucas a consultar manualmente ou via Chrome agent
2. EXTRAIR COORDENADAS DO POLÍGONO via SICAR (quando disponível):
   - Endpoint público GeoJSON do SICAR:
     https://geoserver.car.gov.br/geoserver/wfs?service=WFS&version=1.0.0
     &request=GetFeature&typeName=sicar:cars_imoveis_x
     &CQL_FILTER=num_car='<NUMERO_CAR>'&outputFormat=application/json
   - Extrair vértices WGS84 (SW, SE, NE, NW), centro do polígono (centroide),
     área calculada e dimensões aproximadas (largura L-O e altura N-S em metros)
   - Montar link Google Maps: https://maps.google.com/?q=<lat_centro>,<lng_centro>
3. GERAR CROQUI DO DOSSIÊ com dois polígonos sobrepostos:
   - Polígono externo (azul claro): área total do imóvel pelo CAR (vértices reais)
   - Polígono interno (laranja): área locada à TowerCo (225 m² ou conforme contrato,
     posicionada pelo croqui do Anexo I do contrato ATC — coordenadas P1/P2/P3/P4)
   - Labels: área CAR em ha, área locada em m², número CAR, matrícula
   - SVG georreferenciado com escala, norte, coordenadas nos vértices
   - Para o PDF: converter SVG→PNG via cairosvg e embutir base64
   - Rodapé obrigatório: "Croqui indiciário — uso interno APW Brasil"
4. REGISTRAR no checklist Bloco B2:
   - ✅ CAR ativo: número + área + data inscrição + situação
   - ⚠️ se dataDisponibilizacao vazio: "polígono inscrito, validação geográfica
     pendente no órgão estadual — não bloqueia escritura, exigir comprovante"
   - 🟥 se ausente ou cancelado

- O Lucas salva no M-Files manualmente — a skill **não** faz upload. Entregar via
  `present_files`.

## E-mail de handoff ao jurídico (Stage 7)

Quando o deal entra no **Stage 7** — estágio em que o jurídico **recebe o caso para
processamento e análise** —, a skill gera, sob pedido, um **e-mail-resumo ao
jurídico** que abre o caso para a equipe. É o "release note" do diretor: o jurídico
não deve precisar reconstruir o caso do zero.

**Voz e regras**
- Voz do **diretor de aquisições** entregando o caso ao jurídico (Dra. Michelle /
  Anderson / Márcia / Diogo). **Zero menção a IA.** Português, objetivo, institucional.
- O e-mail **resume e abre o caso** — não substitui o dossiê pré-DD nem a planilha de
  diligência; **referencia** os dois.
- **Não atesta viabilidade.** Aponta as peculiaridades e diz o que precisa de parecer.
- **Honesto sobre o que falta** — pendências e documentos ainda não enviados entram
  explicitamente.
- Confere valor/prazo/condições **contra a condição comercial daquele deal**, nunca
  contra número fixo.

**Estrutura fixa do e-mail**
1. **Assunto:** `L<número> — <Proprietário/Condomínio> (<Cidade/UF>) — Stage 7 / handoff jurídico`
2. **Abertura:** informa que o deal foi **movido ao Stage 7** (processamento/análise) e
   que segue o resumo para a equipe iniciar.
3. **Resumo comercial** (o "ok" comercial): objeto e **estrutura** (C&V / DRS / Cessão de
   Créditos), **valor**, **forma de pagamento**, **prazo**, **tipo de transação** e
   **condições** especiais.
4. **Peculiaridades / pontos de atenção** — o coração do e-mail. Cada achado da pré-DD
   que o jurídico precisa tratar, com o **encaminhamento sugerido** (sem atestar):
   gravames (ex.: alienação fiduciária — quitação + baixa), migração de estrutura
   (C&V → DRS, efeito no ROFR e no ganho de capital), vedação à cessão por torreira
   (matriz), cláusulas do contrato (ex.: aluguel só após a obra), construção não
   regularizada (DRS não exige desmembramento), estado da cadeia dominial.
5. **Documentos enviados** (anexos / já no M-Files): contrato + aditivos, **matrícula
   atualizada**, escritura, **POP**, boletos/saldos (ex.: quitação), LOI, e o **status
   das certidões** (obtidas × pendentes).
6. **Pendências antes do fechamento:** numeradas, com responsável quando houver.
7. **Fechamento:** colocação à disposição + referência ao **dossiê pré-DD** e à
   **planilha de diligência**.

**Entregar** como **rascunho de e-mail** (o Lucas revisa e envia). Quando existirem,
acompanham o e-mail a **planilha de diligência** (abas: condições contratuais, custas,
checklist de documentos/certidões, andamento processual, cálculo do aluguel) e o
**dossiê pré-DD em PDF**. O Stage de fato no CRM é movido pela `apw-crm-key-notes-writer`
— a pré-DD **não promove stage**; aqui apenas se **redige o handoff**.

## Lendo documentos do M-Files
- M-Files Web: `https://mfilesus.apwip.com` — busca por L-number.
- O visualizador não expõe o texto do PDF no DOM. **Para LER o conteúdo, pedir ao
  Lucas que baixe o PDF e anexe no chat.** Pelo M-Files, só checagem de presença.

## Limites da skill
- **Não grava nada no CRM** — Key Notes, Pricing Option, stage são da
  `apw-crm-key-notes-writer`. Nunca promove stage.
- **Não emite parecer jurídico** nem redação contratual final — `apw-telecom-real-
  estate-counsel` e jurídico humano. Sugere estrutura de cláusula como peneira.
- **Não atesta** — onde for ambíguo, marca ⚠️ e devolve.

## Quick reference

| Sintoma | O que fazer |
|---|---|
| Tipo de deal não está claro | Perguntar: condomínio (Cessão) ou terreno/PF (imobiliária)? Carregar a trilha. |
| Deal de condomínio | Trilha A. Não analisar matrícula — não é operação imobiliária. |
| Deal de terreno/torre infield | Trilha B. DD imobiliária completa. |
| Chega 1 documento só | Atualizar o dossiê com ele; resto fica ⬜. Não esperar o caso completo. |
| Cessão em "assuntos gerais" no edital | 🟥 deliberação viciada. Checar o edital ANTES da ata. |
| Quórum na ata | 50% + 1 dos presentes — não do total de unidades. |
| Ata de condomínio | Conferir contra `referencia/modelo-ata-edital-cessao.md`. Itens 5/6/7 ausentes → 🟥. |
| Divergência de área (condomínio) | Vale a área in loco, sempre a MAIOR. Regra fechada — apontar qual vale. |
| Variáveis da ata (prazo, valor) | Conferir contra a condição comercial do deal, nunca contra número fixo. |
| Matrícula veio limpa (Trilha B) | NÃO é "quase fechado". Checklist pré-populado mostra o que falta. |
| Bloco não se aplica (Trilha B) | 1 linha N/A com o motivo. Não some. Reabre se documento novo revelar que incide. |
| Contrato em nome de operadora, POP de torreira | Cessão consumada — não é divergência. POP define a TowerCo. |
| Cancelamento de locação averbado | 🟥 risco de receita. Confirmar com POP + operadora. |
| Cláusula de vedação a cessão no contrato SBA/ATC | Não é bloqueador — nota. Highline/IHS → bloqueador. |
| ROFR/direito de preferência averbado e o deal é DRS | NÃO incide — DRS não é compra, não dispara preferência. Nota, nunca pendência dura. |
| Vontade de dar veredito de viabilidade | NÃO. A skill peneira e encaminha. Parecer é do jurídico. |
| Lucas pede "gera o PDF" | `dossie_preDD_L<número>.pdf`, voz de diligência, zero menção a IA. |
| Lucas pede "e-mail pro jurídico" / deal movido ao Stage 7 | Gerar o e-mail-resumo de handoff (Stage 7): resumo comercial + peculiaridades + docs enviados + pendências. Voz de diretor, zero IA. Referencia o dossiê e a planilha de diligência. |
| Deal é rooftop/condomínio | Croqui top-down é OBRIGATÓRIO no dossiê — área do contrato em escala sobre a laje (estimada/real). Não esperar ele pedir "o mapinha". |
| Deal é Trilha B (terreno/greenfield) | Croqui do lote + área locada é OBRIGATÓRIO também. Vértices pela escada: matrícula georref → coords do Anexo do contrato → reconstrução por confrontantes → estimativa Google Maps. Nunca fabricar; sempre indiciário. Não esperar ele pedir "cadê o mapa". |
| Montou o dossiê | Sempre incluir a CADEIA de contrato + aditivos (tabela) e a EVOLUÇÃO DE ÁREA. Não resumir só o aluguel final. |
| Achou cláusula de vedação à cessão | Dar o veredito por torreira. ATC/SBA → não tem efeito (nota cinza). IHS/Phoenix → bloqueador. Highline/Vivo/TIM → só notificação se não vedar o LOCADOR. |
| Crédito de operadora no extrato (ex.: PIX Claro) | Indício, não prova de contrato direto. Marcar "a confirmar", nunca afirmar segundo contrato. |
| Dois aditivos "iguais" com datas/áreas diferentes | Achado: registrar inconsistência de numeração e qual rege; não escolher em silêncio. |
| Matrícula precária + contrato sem coordenadas | **Entrar no Google Earth Web e medir** (lote + torre): área, lados, vértices lat/long, data da imagem. Ver "Medição por Google Earth Web". Não entregar "vértices indisponíveis". |
| Área locada do contrato não cabe no lote da matrícula | 🟥 — o DRS só grava o que está na matrícula. Pendência: levantamento topográfico + retificação de área (art. 213 LRP) e/ou área locada extravasando para vizinho/área pública. |
| Matrícula veio como "PARA SIMPLES CONSULTA — NÃO VALE COMO CERTIDÃO" | ⬜ item **não** cumprido. Visualização ONR ≠ certidão de inteiro teor com negativa de ônus. Exigir a certidão. |
| Descrição "fundos até o igarapé/rio/córrego" | Profundidade indeterminada + possível **APP** (faixa marginal) e/ou terreno reservado/bem público. Medir por satélite, apontar APP e checar se a torre está na faixa. |
| Alienação fiduciária quitada mas ainda na matrícula | Propriedade é resolúvel — o fiduciante **não pode** instituir DRS sozinho. Pendência dura: termo de quitação + averbação de cancelamento (art. 25, Lei 9.514/97) **antes** da lavratura. |
| LOI arquivada no M-Files como "(F) Signed Offer Agreement" sem assinatura | ⚠️ conferir a via assinada. Classificação no M-Files não prova assinatura — abrir o PDF e olhar. |
