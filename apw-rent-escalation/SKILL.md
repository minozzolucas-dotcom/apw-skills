---
name: apw-rent-escalation
description: Lê cadeia de aditivos de contrato telecom (site, ERB, rooftop, DRS) da APW Brasil e extrai o rent escalation vigente — valor mensal atual, índice (IPC-FIPE, IGP-M, IPCA, INPC), e data-base do reajuste — citando os trechos exatos das cláusulas. Use SEMPRE que o Lucas mandar aditivos pedindo "quando é o reajuste", "qual o rent escalation", "qual o índice", "data-base", "monta a cadeia de aditivos", "aditivo vigente", "aluguel hoje", "explica pro underwriting/IC" — ou colar contratos VIVO, Claro, TIM, Oi, TBSA, ATC, SBA, IHS, Highline, Algar pedindo análise. Também acione com discrepância entre valor pago e contratual, conflito entre aditivos, sobreposição de índices (IGP-M → IPC-FIPE → IPCA), ou pedido de resumo bilíngue PT+EN pra San Diego/Radius. NÃO use para análise jurídica de cláusula (apw-telecom-real-estate-counsel) nem pré-DD registral (apw-pre-dd-legal); DELEGUE pra apw-rent-gross-up quando pedir bruto/líquido.
---

# APW Rent Escalation Reader

Skill especializada em ler **cadeias de aditivos** de contratos de locação telecom da APW Brasil e devolver o rent escalation vigente de forma estruturada, sem inventar e sem se perder em datas conflitantes.

## Princípio operacional

Uma cadeia de aditivos sobrescreve a anterior **por camadas**, não por substituição total. Cada aditivo pode alterar:

- **Valor cheio** (renegociado, não calculado por índice)
- **Índice de reajuste** (IGP-M → IPC-FIPE → IPCA é a sequência típica em contratos antigos)
- **Data-base do reajuste** (o "aniversário" anual — pode mudar entre aditivos)
- **Data de eficácia do novo valor** (diferente da data-base de reajuste — confunde com frequência)

**O que manda hoje é o último aditivo que tocou em cada uma dessas camadas.** Se o 4º aditivo só alterou valor e data-base mas não tocou no índice, o índice vem **por ratificação** do aditivo anterior que o fixou.

## Erros recorrentes a evitar

Esses são os erros que já apareceram em análises do Lucas e que esta skill existe pra prevenir:

1. **Confundir data de eficácia com data-base de reajuste.** Quando um aditivo diz "a partir de 01/01/20XX o aluguel passa a R$ Y, com data-base de reajuste em 01/12/20XX", a data-base é **dezembro**, não janeiro. Janeiro é só quando o valor começa a ser cobrado.

2. **Achar que data-base é o mês de cobrança.** O IPC-FIPE de referência de dezembro só fecha/é divulgado no começo de janeiro, então o reajuste com data-base dez/X muitas vezes aparece **na competência de janeiro** no extrato. Isso não muda a data-base contratual — só o lag operacional.

3. **Extrapolar índice quando o último aditivo é silente.** Se o aditivo vigente não menciona índice, ele vem por ratificação do anterior. Cite a cláusula de ratificação para sustentar.

4. **Encadear índices acumulados pra reconstruir histórico.** Cada aditivo costuma fixar valor cheio renegociado. Não dá pra pegar valor de 1998 e aplicar 30 anos de índice — o valor que vale é o do último aditivo, e o índice corre **a partir da data-base** dele.

5. **Confundir formato de data BR (dd/mm) com US (mm/dd).** Quando for output em inglês, sempre escrever o mês **por extenso** ("December 1st" em vez de "12/01" ou "01/12") para eliminar ambiguidade com o leitor americano (San Diego, Radius).

## Workflow padrão

### 1. Inventário da cadeia

Receba todos os aditivos disponíveis. Para cada um, extraia:

- Número do aditivo (1º, 2º, 3º, 4º... ou "Aditivo VIVO 2009", "Aditivo TBSA 2023")
- Data de assinatura
- Locatária na data (VIVO/Telesp/Telefônica/Claro/TIM/Oi → TBSA/ATC/SBA/IHS/Highline quando há cessão)
- Cessão registrada? (operadora → towerco)
- Cláusulas relevantes ao escalation (Cláusula do Aluguel, Cláusula de Reajuste, Cláusula de Ratificação)

### 2. Identificar o aditivo vigente por camada

Para cada uma das 4 camadas, qual aditivo manda:

| Camada | Onde olhar | Exemplo |
|---|---|---|
| Valor cheio | Cláusula "Do Aluguel" do último aditivo que fixou valor | 4º Aditivo (ATC, 01/03/2016): R$ 4.100,00 |
| Índice | Última cláusula explícita sobre índice (pode estar em aditivo anterior) | Aditivo VIVO (25/05/2009): IPC-FIPE |
| Data-base do reajuste | Última cláusula que fixou aniversário | 4º Aditivo: 01/12 (dezembro) |
| Cláusula de ratificação | Item final do aditivo vigente | "Ficam ratificadas todas as demais cláusulas..." |

### 3. Montar o quadro estruturado

Output obrigatório (sempre sai). Veja `references/output-template.md` para o formato exato.

### 4. Citar os trechos

Cada conclusão do quadro precisa de citação:
- Trecho original em **português** (entre `<cite>` se vier de documento processado)
- Tradução para **inglês** com mês escrito por extenso quando houver risco de confusão
- Referência: número do aditivo + cláusula + item

### 5. Verificações de sanidade (antes de entregar)

Antes de mandar pro Lucas, rodar mentalmente:

- [ ] O valor cheio bate com a expectativa do índice acumulado entre o aditivo anterior e o atual? Se sim, era reajuste. Se não, era renegociação cheia — sinalizar.
- [ ] A data-base que eu escolhi aparece literalmente em alguma cláusula? Ou eu estou inferindo?
- [ ] O índice vem de cláusula explícita ou por ratificação? Se for ratificação, mostrar o caminho (qual aditivo introduziu, qual ratificou).
- [ ] Há conflito entre aditivos? Se sim, o mais recente vence — mas registrar o conflito explicitamente.
- [ ] Mês escrito por extenso no output em inglês? (jun/dec/jan são os campeões de confusão).

### 6. Outputs opcionais (sob demanda)

**Valor atual:** se o Lucas pedir "calcula o valor hoje" ou "qual o aluguel em [mês/ano]":
1. Partir do valor cheio do aditivo vigente + sua data-base
2. Buscar série histórica do índice (IPC-FIPE pela FGV/FIPE; IPCA pelo IBGE; IGP-M pela FGV)
3. Aplicar reajuste em cada aniversário sucessivo até a data alvo
4. Mostrar memória de cálculo (não só o número final)

**Gross-up bruto/líquido:** se o Lucas pedir "bruto", "líquido", "IR", "retenção", "conta inversa" — **DELEGAR PARA A SKILL `apw-rent-gross-up`** passando o valor atual já calculado. Não reimplementar.

**Email pra San Diego:** se pedir, gerar email em inglês com o quadro estruturado, datas por extenso, e tom direto/técnico (ver `references/email-template-en.md`).

## Formato de output padrão

Sempre que a skill rodar, o **output mínimo** é o quadro estruturado da cadeia + citação dos trechos. Ver `references/output-template.md` para o template completo com exemplo preenchido.

## Quando NÃO entregar conclusão

Se a cadeia recebida estiver incompleta (ex.: faltam aditivos intermediários, há lacunas óbvias entre o valor de 1998 e o de 2016 sem aditivos para preencher), **dizer explicitamente o que está faltando** antes de cravar o escalation vigente. Não inventar índice nem data-base por dedução.

Se houver dois aditivos da mesma data ou conflito real entre aditivos sobrepostos, **levantar o conflito** e pedir orientação antes de decidir.

## Delegação para outras skills APW

| Pedido do Lucas | Skill que assume |
|---|---|
| "Calcula o bruto/líquido", "gross-up", "IR retido" | `apw-rent-gross-up` (passar valor atual já calculado) |
| "Analisa essa cláusula", "pode ceder?", "tem ROFR?" | `apw-telecom-real-estate-counsel` |
| "Pré-DD da matrícula", "ata de assembleia", "edital" | `apw-pre-dd-legal` |
| "Monta o submission", "investment opportunity", "IC" | `apw-submission-writer` |
| "Dossiê do Lxxxxx", "contexto desse deal" | `apw-deal-dossier` |

Esta skill foca **só no escalation**. Quando o pedido extrapolar, sinalizar a skill correta e (quando aplicável) entregar o quadro pronto pra ela consumir.
