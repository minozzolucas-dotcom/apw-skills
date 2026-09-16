---
name: apw-dd-report-review
description: Use SEMPRE que o Lucas colar um REPORT de Due Diligence (parcial ou final) de escritório externo da APW Brasil — ES Advogados/Elian Sanchez (eliansanchez.adv.br) ou o 2º escritório — e pedir "analisa esse report", "lê o report da DD", "quais os riscos apontados", "soluções e próximos passos", "esse report fecha", "audita a DD do escritório". Gatilho também: e-mail de DD report com blocos numerados (Imóvel/Contrato/Proprietários), seção "DOCUMENTOS PENDENTES", certidões dos proprietários, ou Márcia Sena encaminhando parecer externo. A skill faz a leitura crítica APW: traduz cada achado em selo, cruza contra as regras APW que o escritório não conhece (matriz de TowerCo, DRS não dispara ROFR, POP define a torreira, débito quitável vira desconto no preço) e fecha os gates de estrutura da APW. NÃO refaz a DD de documento bruto (apw-pre-dd-legal); NÃO grava no CRM (apw-crm-key-notes-writer); NÃO emite parecer final (apw-telecom-real-estate-counsel).
---

# APW DD Report Review

Leitura crítica APW sobre o **report de DD redigido por escritório externo**. O
escritório entrega o parecer registral/cartorário/judicial; esta skill o **traduz
em decisão de deal** no padrão APW.

## Onde entra no funil

Depois que a APW manda o kit de documentos ao escritório externo, ele devolve um
**DD report** — primeiro **parcial**, depois **final**. O insumo desta skill é
esse report já escrito, **não** o documento bruto. Ler matrícula/ata/contrato do
zero é a `apw-pre-dd-legal`. Aqui o trabalho começa no parecer pronto.

Sequência típica: APW salva o deal e pede previsão → escritório dá prazo → envia
**report parcial** (com pendências) → APW resolve pendências → **report final**.

## Princípio fundamental

**O report do escritório é insumo, não o veredito final do deal.** O escritório
responde *"o imóvel e os proprietários têm pendência registral/judicial/fiscal?"*.
A APW responde *"o deal fecha, como (estrutura), e por quanto?"*. Três movimentos,
sempre nesta ordem:

1. **Traduzir** cada achado do escritório em **selo APW** — ✅ resolvido · ⚠️
   contornável · 🟥 estrutural · ⬜ pendente · 🟦 nota.
2. **Cruzar** contra as regras APW que o escritório **não** domina — matriz de
   TowerCo, DRS×ROFR, POP define a torreira, débito quitável = desconto no preço.
3. **Fechar os gates que são da APW** — o escritório **não decide a estrutura**
   (DRS / C&V / Cessão) nem a **viabilidade pela torreira**. Um report pode estar
   impecável e o deal ainda travar na matriz de TowerCo.

**Onde o report e a regra APW divergem, apontar explicitamente.** Não engolir o
parecer do escritório nem contradizê-lo em silêncio. O escritório acerta o direito
imobiliário; a APW acrescenta o conhecimento de torreira e de estrutura de deal.

**A peneira continua valendo:** onde for ambíguo ou for redação contratual final,
⚠️ e devolver ao jurídico (`apw-telecom-real-estate-counsel`). A skill **não
atesta**.

## Os dois escritórios externos

| Escritório | Domínio | Contatos | Interlocução APW |
|---|---|---|---|
| **ES Advogados / Elian Sanchez** (eliansanchez.adv.br) | DD registral/cartorária | Rodrigo Elian Sanchez, Flavia Pluchino, Vanessa Freitas, Lucas Macedo, Marcelo Barretto, Aline Hitomi | Márcia Sena (Jurídico), Aline Felix |
| **[2º escritório]** | *calibrar quando chegar o 1º report dele* | — | — |

**Formato típico do report** (ES Advogados): e-mail com (1) **resumo por blocos
numerados** — *Do Imóvel · Do Contrato de Locação · Dos Proprietários*; (2)
**análise pormenorizada** — CONTRATO DE LOCAÇÃO / IMÓVEL / CERTIDÕES DOS
PROPRIETÁRIOS / DOCUMENTOS DOS PROPRIETÁRIOS; (3) **DOCUMENTOS PENDENTES**. O report
parcial já traz o veredito de cada bloco; o final fecha as pendências. Quando o 2º
escritório mandar o primeiro report, registrar o formato dele aqui.

## Como ler o report — bloco a bloco

### Bloco do imóvel / registral
- **Ônus e gravames** — "livre e desembaraçada" / "sem ônus, ações reipersecutórias"
  → ✅. Qualquer hipoteca, penhora, alienação fiduciária, usufruto, indisponibilidade
  → ler com a `apw-pre-dd-legal` (matriz de achados) e classificar.
- **Cadeia dominial** — escritura de aquisição + transmitente identificados, R-/AV-
  conferidos → ✅ regular.
- **Renumeração de matrícula** (unificação registral / decreto judicial) → 🟦 nota.
  Não interfere no negócio. Ação: atualizar a numeração no **próximo aditivo** do
  contrato com a torreira. Nunca tratar como condição precedente.
- **Área** — matrícula × cadastro municipal batem → ✅. Divergência → ⚠️ (regra de
  área da `apw-pre-dd-legal`).
- **Tributos do imóvel (IPTU/ITU)** — certidão **positiva** com débito → ver "débito
  quitável" abaixo.
- **Contrato averbado na matrícula?** Não averbado → 🟦 nota; **não trava o DRS** (o
  DRS institui direito novo, independe da averbação da locação).

### Bloco do contrato / TowerCo
- **POP define a torreira.** Confirmar que o report identificou a locatária pelos
  comprovantes de pagamento, não só pelo nome no contrato. Operadora no contrato +
  POP de torreira = cessão consumada, não divergência.
- **Reconciliação do aluguel** — valor do POP × valor contratual × índice. Bate → ✅.
- **Cláusulas de preferência / vedação** — aqui mora o **gate** (ver seção própria).
  O escritório costuma analisar preferência (ROFR) e não-concorrência; a APW
  acrescenta a leitura por torreira.

### Bloco dos proprietários / certidões
- **Estado civil** — comunhão universal/parcial, coproprietários → **todos comparecem
  à escritura** como coinstituidores. Requisito de fechamento, não risco.
- **Apontamento judicial em que o proprietário é AUTOR** (polo ativo, busca crédito —
  ex.: expurgos do Plano Collor vs. banco) → 🟦 nota, **sem risco de constrição**.
  Só vira ⚠️/🟥 quando o proprietário é **réu** em execução/cobrança que possa
  recair sobre o imóvel.
- **Certidões negativas** (federal/PGFN, trabalhista/CNDT, JF, cível) limpas → ✅.
- **Certidão que não pôde ser emitida** (ex.: CND municipal de um cônjuge) → ⬜
  pendente. Exigir o relatório fiscal pra saber o que bloqueia — pode esconder dívida
  ativa. Material se o titular é coinstituidor.

### Bloco "DOCUMENTOS PENDENTES"
Transcrever como ⬜ no output e jogar direto nos **próximos passos com responsável**.
Pendência documental não mata o deal — é o que o report **final** vai fechar.

## Regras APW para cruzar SEMPRE (o escritório não as aplica)

| Regra | Efeito na leitura |
|---|---|
| **DRS não dispara ROFR** | Direito de preferência (art. 27 Lei 8.245) alcança **aquisição** do imóvel; DRS não é compra → preferência não tem objeto. Mesmo com ROFR averbado: 🟦 nota, nunca bloqueio. O escritório que conclui isso está alinhado. |
| **POP define a TowerCo** | A torreira do deal é quem paga no comprovante, não o nome no contrato. |
| **Débito pequeno / ônus quitável** | IPTU/ITU/tributo municipal em aberto de monta ínfima → ⚠️ contornável: **quitar com desconto do preço** ou condição precedente de quitação. Somar todos os débitos e dar o total. Não é bloqueador. |
| **Comunhão / coproprietários** | Todos os titulares assinam a escritura do DRS/C&V. Instrução, não risco. |
| **Renumeração de matrícula** | 🟦 nota; atualizar no próximo aditivo. |
| **Locação não averbada** | Não trava o DRS. |
| **Matriz de TowerCo** | Decide se a **estrutura** (DRS/Cessão/C&V) é viável. É o gate da APW. |

## O gate que o escritório NÃO fecha — estrutura × torreira

O escritório externo analisa o **imóvel e os proprietários**; ele não tem o
conhecimento de torreira da APW e **não decide a estrutura do deal**. Esse veredito é
sempre da APW. Aplicar a **matriz de TowerCo** (fonte: `apw-pre-dd-legal`):

- **ATC (American Tower)** — autoriza Cessão e DRS sem anuência prévia. Cláusula de
  vedação ATC → 🟦 nota.
- **SBA** — veda no papel (cl. 7.2), mas a APW opera o **SBA Program**: notifica →
  anuência (contrapartida = desconto de aluguel). 🟦 nota.
- **Highline / Vivo / TIM** — fazem Cessão e DRS **somente se não houver vedação
  expressa ao LOCADOR** de onerar/instituir direito real. **Ponto de atenção:** o
  report pode cobrir preferência e não-concorrência e **não** varrer a cláusula
  anti-agregador (vedação ao locador a alienar/onerar/instituir direito real). Esse é
  o gate: exigir varredura do contrato inteiro nessa chave antes de avançar. Se
  vedar → 🟥 bloqueador.
- **Claro / TBSA** — C&V e Cessão condicionada → caso a caso.
- **IHS / QMC / BTC / GTS / Phoenix (PTI)** — vedam de fato → caminho é **compra**;
  condomínio inviável → 🟥 bloqueador real.
- Equivalência de nomes (Global Sites/T4U → Highline; Centennial/CSS → IHS; GTS →
  SBA; etc.): ver `apw-pre-dd-legal` / `referencia_torreiras_APW.html`.

**Regra dura:** se o report não disser explicitamente que **não há vedação ao locador
a instituir a estrutura pretendida**, isso é um **gate aberto** — registrar como ⚠️ e
encaminhar à `apw-telecom-real-estate-counsel`, mesmo que todo o resto esteja ✅.

## Output (no chat)

```
LEITURA APW — Report <parcial/final> · L<número> · <caso>   [TRILHA A/B · <estrutura>]
ESCRITÓRIO: <ES Advogados / 2º escritório>  ·  data do report

VEREDITO
<1-2 linhas: saúde do deal + qual é o único gate de verdade>

DADOS-CHAVE
<endereço · TowerCo (pelo POP) · matrícula · áreas · aluguel/índice · proprietários/regime>

RISCOS E ACHADOS  (report → selo APW → solução)
[tabela: # · achado do escritório · selo · leitura/solução APW]

PENDÊNCIAS DOCUMENTAIS  (⬜ — travam o report final)
<numerado>

GATE DE ESTRUTURA × TORREIRA
<o escritório fechou? · matriz APW · o que falta confirmar>

DIVERGÊNCIAS / GAPS vs. o escritório
<onde a leitura APW difere ou complementa o parecer — ou "nenhuma">

PRÓXIMOS PASSOS  (ordenados, com responsável)
<numerado: quem faz o quê>
```

Bottom-line-first, denso, ADHD-friendly. Reescrever o output inteiro a cada
atualização (parcial → final) para o Lucas ter a foto completa numa mensagem só.

## Quick reference

| Sintoma no report | O que fazer |
|---|---|
| "Livre e desembaraçada / sem ônus" | ✅ registral. Seguir pros proprietários e pro gate de torreira. |
| Renumeração de matrícula | 🟦 nota; atualizar no próximo aditivo. Não é condição precedente. |
| IPTU/tributo em aberto, monta pequena | ⚠️ quitável: desconto no preço ou CP. Somar todos e dar o total. |
| Direito de preferência (ROFR) e o deal é DRS | Não incide — DRS não é compra. 🟦 nota. Se o escritório já concluiu isso, alinhado. |
| Cláusula de não-concorrência (locar a concorrente) | APW não é operadora → não alcança o DRS. **Mas:** isso não é a cláusula anti-agregador. Checar vedação ao LOCADOR a onerar/instituir direito real. |
| Report cobriu preferência + concorrência, mas não a vedação ao locador | ⚠️ **gate aberto** — varrer contrato da torreira; counsel. |
| Proprietário é AUTOR de ação | 🟦 nota, sem risco. Réu em execução → ⚠️/🟥. |
| Comunhão/coproprietários | Todos assinam a escritura. Instrução de fechamento. |
| Certidão que não pôde ser emitida | ⬜ pendente — exigir relatório fiscal do bloqueio. |
| Locação não averbada na matrícula | 🟦 nota; não trava o DRS. |
| Report é parcial | Marcar [parcial]; listar o que o final ainda fecha. Não tratar como definitivo. |
| Torreira é IHS/Phoenix e a estrutura é DRS/Cessão | 🟥 bloqueador pela matriz — caminho é compra. Levantar mesmo se o report estiver limpo. |
| Vontade de dar "deal aprovado" | NÃO. A skill peneira, classifica e encaminha. Aprovação é do comercial/IC. |

## Limites
- **Não refaz a DD do zero** a partir de documento bruto — isso é `apw-pre-dd-legal`.
  Aqui o insumo é o report já redigido. (Se o Lucas colar matrícula/contrato em vez
  do report, redirecionar pra `apw-pre-dd-legal`.)
- **Não grava no CRM** (Key Notes/stage = `apw-crm-key-notes-writer`).
- **Não emite parecer nem redação final** — sugere estrutura e encaminha à
  `apw-telecom-real-estate-counsel` / jurídico humano.
- **Não atesta.** Onde for ambíguo, ⚠️ e devolve.
