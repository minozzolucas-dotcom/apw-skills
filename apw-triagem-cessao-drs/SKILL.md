---
name: apw-triagem-cessao-drs
description: Triagem jurídica em LOTE de sites da APW Brasil — descobre quais deals estão livres para NOTIFICAR a cessão de direitos creditórios (art. 290 CC) ou constituir DRS (art. 1.369 CC), e quais exigem anuência prévia. Lê contrato de locação e a cadeia de aditivos, roteia cada deal para Trilha A (crédito/condomínio) ou Trilha B (superfície/terreno) e devolve semáforo com a cláusula citada e a minuta de notificação nos verdes. Use SEMPRE que o Lucas mandar planilha/lista de sites (ID towerco, ID APW, locador, aluguel, desconto, endereço) pedindo "analisa esses casos", "quais dá pra notificar", "cláusulas impeditivas", "tria esse lote", "quais travam a cessão", "posso notificar sem anuência" — ou subir contrato de torre (SITES, Claro, TIM, Vivo, Highline, SBA, ATC) perguntando se dá pra ceder o crédito ou onerar o imóvel. NÃO use para parecer de cláusula isolada (apw-telecom-real-estate-counsel), pré-DD registral (apw-pre-dd-legal), redline com condomínio (apw-negociacao-contrato).
---

# APW — Triagem Cessão × DRS em lote

Skill de **triagem**, não de parecer. O objetivo é separar um lote de sites em três baldes acionáveis — *notifica hoje*, *notifica com parecer*, *precisa de anuência* — com a cláusula literal na mão para sustentar cada veredito.

O erro que essa skill existe para evitar: ler "é vedada a cessão deste contrato" e carimbar 🔴. Na maioria dos contratos de locação de torre, essa cláusula veda **cessão de posição contratual**, e não alcança a cessão de crédito. Confundir as duas mata deals que estão livres.

## Regra de ouro

**A pergunta nunca é "o contrato permite?". É "o contrato veda *especificamente* o que a APW quer fazer?"**

Art. 286 CC: o crédito é cedível salvo se a isso se opuser a natureza da obrigação, a lei ou a **convenção com o devedor**. O default legal é a liberdade de ceder. O ônus é achar a vedação, não achar a permissão. Silêncio contratual = 🟢.

---

## Fase 0 — Montar o lote

Entrada típica: planilha ou bloco colado com `ID towerco | ID APW (L-number) | Locador | aluguel | desconto | endereço | cidade | UF | lat | long`.

Antes de qualquer coisa, faça a **higiene do lote** e reporte no chat:

- **Coordenadas fora do Brasil.** Faixa válida: lat entre −34 e +6, long entre −74 e −34. Qualquer valor fora disso é erro de digitação (lat/long trocados, sinal invertido). Sinalize com a correção provável — não deixe entrar como input de análise.
- **L-number duplicado ou ausente.**
- **Locador PF vs. PJ vs. condomínio** — isso já pré-roteia a trilha.
- **Coluna de desconto.** Se o lote vem de campanha de redução da towerco, pergunte ao Lucas de uma vez: *o desconto é pedido em aberto ou já foi assinado em aditivo?* Isso muda o crédito que está sendo cedido e portanto o valuation. Não trave a análise jurídica esperando a resposta — mas registre a pendência no board.

Depois, puxe do Dynamics os campos que o lote não traz (stage atual, owner, torreira, property type, on hold reason). Ver `references/crm-e-fontes.md` para os snippets de Web API — sempre via sessão autenticada, nunca screenshot em domínio corporativo.

## Fase 1 — Rotear a trilha

Cada deal entra em **uma** trilha. Rodar o checklist errado gera vermelho falso.

| Locador | Ativo | Trilha | Instrumento | Teste jurídico |
|---|---|---|---|---|
| Condomínio edilício | Rooftop | **A** | Cessão de Direitos Creditórios | Art. 286/290 CC — vedação convencional à cessão de **crédito** |
| PJ (empresa, clube, diocese, igreja) | Rooftop ou terreno | **A** | Cessão de Direitos Creditórios | Idem + capacidade/representação do estatuto |
| PF proprietária | Terreno / greenfield | **B** | Direito Real de Superfície | Art. 1.369 CC — vedação a **onerar** o imóvel + preferência registrada |
| PF / PJ com terreno onde a APW quer o ativo | Terreno | **B** | DRS (ou compra) | Idem |

Casos híbridos (PJ dona de terreno onde cabem as duas) rodam as duas trilhas e o board mostra as duas saídas — a escolha é comercial, não jurídica.

## Fase 2 — Ler o contrato e a cadeia de aditivos

O Lucas baixa os documentos do M-Files e sobe no chat. Peça, por deal:

1. Contrato de locação original
2. **Todos** os aditivos — a vedação costuma nascer no 3º aditivo, não no original
3. Instrumento de cessão da locatária, se a towerco assumiu de outra (Claro → SITES, por ex.)
4. POP (comprovante de pagamento recente) — define **quem é o devedor de verdade**, que é quem vai ser notificado

Se vierem 10+ contratos, faça o **teste de template primeiro**: contratos de safra legado de uma mesma towerco costumam ser padronizados. Analise um a fundo, depois rode os demais em modo diferença — só o que desvia do template precisa de leitura integral. É isso que transforma 15 deals em horas em vez de dias.

Se o PDF for escaneado sem camada de texto, diga isso explicitamente e peça o anexo como imagem — não invente leitura de um documento que não foi lido. Nunca marque semáforo sem cláusula citada.

**Sempre cite o texto literal da cláusula** (número + transcrição) ao lado do veredito. Veredito sem citação não é auditável e não sustenta uma notificação.

## Fase 3 — Semáforo

Aplique a taxonomia completa de `references/taxonomia-clausulas.md`. Resumo operacional:

### Trilha A — Cessão de Direitos Creditórios

| | Achado | Veredito |
|---|---|---|
| 🟢 | Silêncio sobre cessão | Notifica. Art. 290 e segue. |
| 🟢 | Veda "cessão **deste contrato**" / "da posição contratual" / "sublocação" | Notifica. Não alcança cessão de crédito — o locador permanece locador com todas as obrigações. |
| 🟡 | Veda cessão a **concorrente** / terceiro do setor | Notifica com parecer anexo: APW não é operadora nem towerco, não concorre com a locatária. |
| 🟡 | Exige aditivo para alteração de dados bancários | Fricção operacional, não impedimento. Notifica e trata o pagamento em paralelo. |
| 🟡 | Permite compensação de créditos pela locatária | Cede-se com as exceções (art. 294). Precifica o risco, não bloqueia. |
| 🟡 | Vedação genérica a "transferência de direitos" sem qualificar | Zona cinzenta. Escalar para parecer antes de notificar. |
| 🔴 | Veda expressamente cessão **de créditos/recebíveis** | Vira pedido de anuência. Outro fluxo, outro prazo. |
| 🔴 | Exige **anuência prévia e escrita** da locatária para cessão de crédito | Idem. |

### Trilha B — DRS

| | Achado | Veredito |
|---|---|---|
| 🟢 | Contrato silente sobre oneração do imóvel | Constitui DRS. A locação segue íntegra. |
| 🟢 | ROFR redigido sobre "**venda/alienação** do imóvel" | DRS não é alienação de domínio — não dispara ROFR. Regra fixa APW. |
| 🟡 | ROFR amplo: "venda, cessão **ou qualquer transferência de direitos** sobre o imóvel" | Redação alcança o DRS por leitura literal. Parecer antes de escriturar. |
| 🟡 | Preferência **registrada na matrícula** (art. 167 LRP) | Eficácia real. Tratar antes, não depois. |
| 🔴 | Vedação expressa a instituir ônus real / gravame sobre o imóvel | Bloqueia. Renegociar ou migrar para compra. |
| 🔴 | Imóvel com alienação fiduciária / indisponibilidade ativa | Bloqueio registral, não contratual. Vai para `apw-pre-dd-legal`. |

### Camadas que não são cláusula, e mesmo assim travam

Verifique sempre, porque um 🟢 contratual com essas pendências é um falso verde:

- **Condomínio:** a convenção exige assembleia para ceder crédito? Qual quórum? Há ata válida e síndico com mandato vigente?
- **PJ:** o estatuto/contrato social dá poderes ao signatário? Diocese, clube e associação costumam exigir aprovação de conselho.
- **Devedor real:** quem consta no contrato ainda é quem paga? Se houve cessão da locatária, a notificação vai para a entidade errada e não produz efeito.
- **Desconto da towerco:** já assinado em aditivo? Se sim, o crédito cedido é o pós-desconto.

## Fase 4 — Saídas

Sempre entregue, nessa ordem:

**1. Board do lote** (tabela no chat, um deal por linha):
`L-number | Locador | Trilha | 🟢🟡🔴 | Cláusula-chave (nº) | Veredito em 1 linha | Próximo passo | Bloqueio não-contratual`

**2. Ficha por deal** — só para 🟡 e 🔴, e para os 🟢 que vão virar notificação. Cláusula transcrita, leitura jurídica, o que destrava.

**3. Fila de ação**, agrupada: `Notificar agora` · `Notificar com parecer` · `Pedir anuência` · `Falta documento`.

**4. Minuta de notificação** para os verdes — modelo em `assets/modelo-notificacao.md`.

## Gate de sequência — não pule

Notificação é **ato irreversível de exposição**. No instante em que a towerco recebe, ela sabe que a APW está comprando aquele fluxo — e o incentivo dela é oposto ao da APW, ainda mais em ano de campanha de redução de custo.

```
cláusula 🟢  →  instrumento de cessão ASSINADO com o locador  →  notificação
```

Nunca gere notificação para deal sem instrumento assinado. Se o Lucas pedir, entregue a minuta marcada **"MINUTA — NÃO ENVIAR ANTES DA ASSINATURA"** e diga o porquê em uma linha. Ele decide, mas decide sabendo.

## Registro

O board do lote é incremental. A cada rodada, atualize o mesmo board em vez de criar um novo — deal que estava 🟡 por falta de aditivo vira 🟢 quando o aditivo chega. Salve em `/mnt/user-data/outputs/` como Markdown, e ofereça a versão PNG/HTML na marca (carregue `apw-brand`) quando o Lucas for circular internamente.

## Handoffs

- Cláusula precisa de redação nova ou redline → `apw-negociacao-contrato`
- Matrícula, cadeia dominial, gravame, croqui → `apw-pre-dd-legal`
- Parecer jurídico formal sobre uma cláusula isolada → `apw-telecom-real-estate-counsel`
- Gravar veredito nas Key Notes → `apw-crm-key-notes-writer`
- Reajuste/índice do aluguel → `apw-rent-escalation`

## Referências

- `references/taxonomia-clausulas.md` — taxonomia completa, termos de busca no PDF, fundamento legal de cada veredito
- `references/crm-e-fontes.md` — extração Dynamics via Web API, campos úteis, identificação de towerco
- `assets/modelo-notificacao.md` — minuta de notificação (Trilha A) e checklist de escritura (Trilha B)
