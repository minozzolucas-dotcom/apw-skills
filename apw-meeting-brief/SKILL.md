---
name: apw-meeting-brief
description: >-
  Transforma transcrições cruas de reuniões — áudio transcrito sem pontuação,
  sem identificação de quem fala, com erros de ASR — em briefings executivos
  estruturados para o Lucas (APW Brasil / telecom infra). Extrai decisões
  tomadas, próximos passos com responsável e prazo, mapa político de quem quer o
  quê, riscos e condicionantes em aberto, números citados, e um glossário que
  corrige os erros de transcrição (ERBs, leads, LGPD, nomes de empresas). Gera
  uma versão interna APW (com leitura política e trechos sensíveis) e uma versão
  limpa compartilhável com a contraparte. Use SEMPRE que o Lucas colar uma
  transcrição de reunião, call ou meeting, mencionar "briefing de reunião",
  "organizar essa transcrição", "resumo da reunião", "o que ficou decidido na
  call", "extrair os próximos passos da reunião", "transformar em ata", ou
  enviar um bloco longo de fala transcrita pedindo estruturação. NÃO use para
  atividades de CRM (apw-opp-activity-forensics) nem análise de contratos
  (apw-telecom-real-estate-counsel).
---

# APW Meeting Brief

Transforma a transcrição crua de uma reunião num **briefing executivo acionável**. O input típico é o pior caso: áudio transcrito automaticamente, sem pontuação confiável, sem rótulo de quem fala, com erros de reconhecimento que viram palavras sem sentido. O trabalho é reconstruir a estrutura — quem decidiu o quê, quem ficou responsável por quê, até quando — sem propagar o lixo do transcritor e sem perder nenhuma decisão ou risco.

## Por que isso é difícil (e por que importa)

Uma transcrição de áudio é enganosa: parece informação, mas é um fluxo contínuo de fala onde decisões, dúvidas, divagações e ruído de ASR estão todos no mesmo nível. Lida superficialmente, vira um resumo vago que perde o que importa. Lida bem, ela revela:

- **As decisões reais** — frequentemente ditas de passagem, no meio de uma frase longa ("então até sexta a gente manda pelo menos a primeira leva").
- **Quem ficou com o quê** — o responsável raramente é nomeado de forma limpa; é preciso inferir de "eu e o Diogo a gente já consegue mandar".
- **O mapa de interesses** — numa reunião com contraparte (cliente, fornecedor, parceiro), cada lado tem uma dor e uma agenda. O briefing precisa separá-las.
- **Riscos e condicionantes** — o "asterisco", a cláusula que bloqueia, a aprovação interna pendente. São os pontos que matam um acordo depois.
- **Trechos sensíveis** — coisas ditas "out of the record", barreiras internas, fraquezas admitidas. Não podem vazar para a versão externa.

O Lucas tem ADHD: o briefing precisa ser escaneável, com estrutura que corta o ruído cognitivo. E como muitas reuniões dele são negociações com terceiros, a skill produz **duas versões**.

## Workflow

### Passo 1 — Ingerir e fazer a primeira leitura

O input é texto colado da transcrição (de Teams, Meet, Zoom, gravador, etc.). Leia o bloco inteiro **uma vez de ponta a ponta antes de extrair qualquer coisa** — uma transcrição só revela quem é quem e qual é o assunto depois que você viu o todo. Numa primeira leitura sem identificação de speakers, você monta o elenco e o tema; só então a segunda leitura extrai a estrutura.

Se a transcrição tiver marcação de quem fala (alguns sistemas dão), use-a. Se não tiver — o caso comum — infira os interlocutores pelo conteúdo: quem se apresenta ("é a Gisele da APW"), quem é tratado por nome ("fala Max", "fala Thiago"), quem fala em nome de qual lado ("nós somos líderes mundiais dos independentes" = lado APW).

### Passo 2 — Corrigir o ASR enquanto lê

Transcrição de áudio em português técnico de telecom está cheia de erros previsíveis. Construa um **glossário de correções** conforme lê — toda vez que uma palavra não faz sentido no contexto, registre o que o ASR escreveu e o que era de verdade. Consulte `references/asr-corrections.md` para o catálogo de erros recorrentes no vocabulário APW/telecom (ERBs, operadoras, torreiras, termos de negociação). Nunca "limpe" silenciosamente — o glossário vai no briefing, porque ajuda o leitor a confiar no resto e a reconhecer os termos da próxima vez.

Regra: corrija no briefing, mas se um termo é ambíguo (você não tem certeza do que o ASR quis dizer), marque com `[?]` em vez de chutar.

### Passo 3 — Extrair os sete eixos

Releia a transcrição com olhar de extração. Consulte `references/extraction-lenses.md` para o catálogo de padrões — como uma decisão "soa" numa fala corrida, como um compromisso é assumido, como um risco é mencionado de passagem. Produza estes sete eixos:

**A. Contexto da reunião.** Quem participou (nome + organização + lado), qual o objetivo declarado, e o veredito de uma linha: a reunião avançou, travou, ou só alinhou.

**B. Decisões tomadas.** O que ficou efetivamente decidido — não o que foi discutido, o que foi *decidido*. Cada uma: a decisão, e a evidência (a frase que a confirma). Se algo foi discutido mas não decidido, vai para Pontos em aberto, não aqui.

**C. Próximos passos / plano de ação.** Tabela: Ação | Responsável | Prazo | Origem (quem assumiu). Esta é a saída principal — extraia com rigor. Se o prazo não foi dito, "Sem prazo definido"; se o responsável é ambíguo, "[a confirmar]". Nunca invente um prazo.

**D. Mapa político / de interesses.** Para cada lado e cada pessoa-chave: qual a dor, qual a agenda, o que querem extrair da relação, onde têm resistência. Numa reunião de negociação isto é o que dá vantagem na próxima rodada.

**E. Riscos, condicionantes e pontos em aberto.** Tudo que pode travar o que foi acordado: aprovações internas pendentes, cláusulas bloqueadoras, dependências, dúvidas não resolvidas. Classifique 🔴 / 🟡 quando fizer sentido.

**F. Números e fatos citados.** Toda métrica, valor, volume, percentual, prazo mencionado. Capture exato. Números soltos numa fala corrida se perdem fácil e costumam ser o dado mais útil depois.

**G. Trechos sensíveis (só versão interna).** Coisas ditas "off the record", fraquezas admitidas, barreiras internas, leitura política franca. Marque claramente — este eixo NUNCA entra na versão externa.

### Passo 4 — Entregar as duas versões

Produza, salvos em `/mnt/user-data/outputs/`:

1. **Briefing interno** (`briefing-[reuniao]-interno.md`) — todos os sete eixos, incluindo mapa político franco e trechos sensíveis. Estrutura no template abaixo.
2. **Versão externa limpa** (`briefing-[reuniao]-externo.md`) — só Contexto, Decisões, Próximos passos e Pontos em aberto não-sensíveis. Sem mapa político, sem trechos sensíveis, sem leitura de fraquezas. É o que pode ser enviado à contraparte como alinhamento/ata.
3. **Dashboard HTML dark** (`briefing-[reuniao]-dashboard.html`) — versão interna em formato visual: plano de ação em destaque, mapa político em cards, riscos sinalizados. Use `assets/dashboard-template.html`.

Apresente os três com `present_files`. No corpo da resposta do chat, entregue o **contexto + decisões + plano de ação direto**, em português casual — é o que o Lucas lê primeiro.

Antes de gerar a versão externa, sempre confirme com o Lucas para quem ela vai e se há algo que ele quer cortar — a fronteira entre sensível e compartilhável depende do destinatário.

## Template do briefing interno (Markdown)

```markdown
# Briefing — [Reunião X] · [data se disponível]

> [Uma frase: o que foi a reunião e o veredito.]

**Participantes:** [Nome (Org, lado)] · ...
**Objetivo declarado:** [...]

## 1. Decisões tomadas
[Lista. Cada decisão + frase-evidência.]

## 2. Plano de ação
[Tabela: Ação | Responsável | Prazo | Quem assumiu.]

## 3. Mapa político / de interesses
[Por lado e por pessoa: dor, agenda, resistência.]

## 4. Riscos e pontos em aberto
[Lista classificada 🔴🟡. Condicionantes, aprovações pendentes, dúvidas.]

## 5. Números e fatos citados
[Toda métrica/valor/volume mencionado, exato.]

## 6. Trechos sensíveis — INTERNO APW
[Off the record, fraquezas, barreiras internas. NÃO vai para a versão externa.]

## 7. Glossário (correções de transcrição)
[Termo do ASR → termo correto. Itens ambíguos marcados [?].]
```

## Princípios

- **Decisão ≠ discussão.** Só entra em "Decisões" o que foi fechado. O resto é "Ponto em aberto". Não promova um "talvez" a decisão.
- **Toda ação tem dono.** Um próximo passo sem responsável é um próximo passo que não acontece. Se a transcrição não nomeia, marque "[a confirmar]" — mas registre a lacuna.
- **Nunca invente prazo nem número.** "Sem prazo definido" é uma resposta honesta e útil. Um prazo chutado é uma mentira operacional.
- **Corrija o ASR, não esconda.** O glossário vai no briefing. Termo ambíguo recebe `[?]`, não um chute.
- **A fronteira sensível é sagrada.** O que foi dito "out of the record" ou revela fraqueza interna fica só na versão interna. Na dúvida, não vaza — pergunte ao Lucas.
- **Fala corrida esconde decisão.** As decisões mais importantes costumam estar enterradas no meio de uma frase longa, sem ênfase. Leia devagar; não amostre.
- **Separe os lados.** Numa negociação, a dor da APW e a dor da contraparte são coisas diferentes e ambas importam. Não funda os interesses.

## Arquivos da skill

- `references/asr-corrections.md` — catálogo de erros de transcrição recorrentes no vocabulário APW/telecom e como reconhecê-los.
- `references/extraction-lenses.md` — como uma decisão, um compromisso, um risco "soam" numa transcrição de fala corrida.
- `assets/dashboard-template.html` — esqueleto do dashboard HTML dark.
