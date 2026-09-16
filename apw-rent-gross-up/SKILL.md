---
name: apw-rent-gross-up
description: Reconcilia aluguel de site da APW Brasil entre líquido (net) na conta do locador PF, bruto (gross) contratual, reajuste IPCA escalonado e retenção de IR — e gera o e-mail em inglês (tom do Lucas) explicando discrepâncias ao underwriting/investidores em San Diego. Use SEMPRE que o Lucas mandar comprovante de pagamento (TED/print de extrato), perguntar "qual o aluguel bruto", "gross-up", "conta inversa do líquido", "o net não bate com o cálculo exato", "por que o aluguel subiu fora da escalation", "reconciliar aluguel", "explica pra Paulina/San Diego", ou colar net pedindo o bruto considerando IR na fonte. Também acione com menção a IRRF, retenção na fonte, redutor da Lei 15.270/2025, escalonamento IPCA de aluguel, ou diferença de retenção entre 2025 e 2026. NÃO use para submission/IC (apw-submission-writer), análise de cláusula (apw-telecom-real-estate-counsel), nem dossiê por código L (apw-deal-dossier).
---

# APW Rent Gross-Up & Reconciliation

Skill para reconciliar aluguel de site telecom da APW Brasil entre **net (líquido)**, **gross (bruto)**, **reajuste IPCA** e **retenção de IR (IRRF)**, e gerar o e-mail em inglês explicando para o time de San Diego (underwriting/investidor) por que os números aparentam não bater.

## Por que essa skill existe

O comprovante bancário que o locador PF recebe é **líquido de IR retido na fonte (IRRF)**. O time de San Diego frequentemente:
1. Pega o net do comprovante e faz a conta inversa pra chegar no bruto → não bate com o "cálculo exato" formal.
2. Vê o net subir de um ano pro outro e acha que houve reajuste fora da data de escalation — quando na verdade foi a **mudança da tabela de IR** (a partir de jan/2026 o redutor da Lei 15.270/2025 derrubou a retenção).

Essa skill separa os efeitos (reajuste contratual vs. retenção de IR), faz o gross-up com a tabela correta de cada ano e devolve o e-mail pronto.

## Quando acionar

- Lucas manda **comprovante de pagamento** (print de TED, extrato bancário) e pede o bruto.
- Lucas pergunta "qual o gross rent", "faz a conta inversa", "gross-up do líquido".
- Lucas diz "o net não bate com o cálculo exato / cálculo formal".
- San Diego (Paulina ou outro) questiona "por que o aluguel subiu fora da escalation" ou "reconcilia o gross contra as retenções".
- Pedido explícito: "explica isso pra Paulina", "monta o e-mail pra San Diego", "reconcilia o aluguel".

## REGRA FIXA — Tabela de IR (IRRF) por ano

A fonte pagadora (carrier/TowerCo) retém IRRF sobre aluguel pago a **pessoa física**. A tabela mudou em jan/2026.

### Tabela 2025 e anteriores (SEM redutor)
Faixa topo 27,5%, parcela a deduzir R$ 896,00.
```
IRRF = base × 0,275 − 896,00      (para base na faixa de 27,5%, > R$ 4.664,68)
net  = bruto − IRRF
```
Gross-up reverso (achar o bruto a partir do net):
```
bruto = (net − 896,00) / 0,725
```

### Tabela 2026 em diante (COM redutor — Lei 15.270/2025)
Mesma tabela progressiva, MAS com um redutor adicional para renda bruta mensal entre **R$ 5.000,01 e R$ 7.350,00**:
```
redutor = 978,62 − (0,133145 × bruto)
IRRF    = (bruto × 0,275 − 896,00) − redutor
net     = bruto − IRRF
```
Gross-up reverso (faixa do redutor):
```
bruto = (net − 1.874,62) / 0,591855
```
> Derivação: net = bruto − [(0,275·bruto − 896) − (978,62 − 0,133145·bruto)]
> = bruto·(1 − 0,275 − 0,133145) + 896 + 978,62 = 0,591855·bruto + 1.874,62

⚠️ **Sempre confirmar a faixa depois de calcular.** Se o bruto sair **acima de R$ 7.350,00**, o redutor não se aplica — usar a tabela sem redutor (`bruto = (net − 896,00)/0,725`). O redutor nunca gera crédito.

⚠️ **Usar a tabela do ANO do pagamento.** Comprovante de 2025 → tabela antiga. Comprovante de 2026 → tabela com redutor. Comparar net de anos diferentes SEM corrigir a tabela é o erro clássico que gera o falso "aumento de aluguel".

Tabela progressiva mensal completa e exemplos: ver `references/ir-tables.md`.

## REGRA FIXA — Escalonamento IPCA do aluguel

Contratos de site são tipicamente reajustados **anualmente pelo IPCA**, no mês-aniversário do contrato (campo "Escalation Month" do submission).

```
valor_reajustado = valor_base × (1 + IPCA_acum_12m)
```
encadeando a cada aniversário. O IPCA aplicado é o **acumulado 12 meses até o mês anterior** ao reajuste (ex.: reajuste de julho usa IPCA acumulado jul-ano-anterior → jun-ano-atual).

- **Sempre buscar o IPCA real** (web_search "IPCA acumulado 12 meses [mês/ano] IBGE") — não usar de memória, muda todo mês.
- O reajuste do ano corrente **só é materializável depois** que o IPCA do mês-base é divulgado (ex.: reajuste de jul só fecha com o IPCA de jun, divulgado em jul).
- Para o reajuste ainda não materializado, **NÃO projetar inflação** — usar o **3% default** (ver abaixo).


## REGRA FIXA — "Gross vigente HOJE" (a partir do net)

O gross-up do comprovante entrega o **bruto na data do pagamento** — não o de hoje. Para o bruto vigente HOJE:

1. Gross-up do net (tabela do ano do pagamento) = bruto na data do POP.
2. Aplicar **só os reajustes ocorridos entre a data do POP e hoje** (consciente do aniversário): o gross-up já embute todos os reajustes até a data do pagamento; falta encadear os aniversários seguintes.

```
gross_hoje = gross_do_POP × Π (1 + reajuste de cada aniversário entre o POP e hoje)
```

3. **Cross-check** contra a cadeia contratual desde a base (valor-base × índice em cada aniversário). Os dois caminhos têm que cair perto (gap < ~1%). O contratual é a fonte de verdade; o do net é sanity check.

Mecânica do aniversário: reajuste de **abril** usa IPCA 12m **até março**; de julho usa até junho; etc. Puxar a **série mensal do IPCA** (IBGE/dadosdemercado) e computar os acumulados 12m em Python — não montar de snippets soltos de busca.

## REGRA FIXA — O "3% default"

A APW carrega um **+3% padrão** sobre o valor contratual vigente quando o deal fecha **um pouco antes** do próximo reajuste IPCA. É o que **o investidor considera** como proxy do reajuste que está por vir, já que não se pode bookar uma projeção de inflação.

```
valor_carregado = valor_contratual_vigente × 1,03
```

⚠️ **Paulina e o time de San Diego JÁ conhecem essa regra.** Não explicar como novidade — citar como referência conhecida ("the usual 3% default", "the standard 3% we carry"). Não soar didático sobre isso.

## Fluxo de trabalho

1. **Coletar inputs** (do comprovante + contrato/submission):
   - Net rent (valor do comprovante) + **data do pagamento** (define a tabela de IR)
   - Valor-base do contrato + data-base (do aditivo)
   - Escalation month + indexador (default IPCA)
   - Se houver, comprovante de outro ano (segundo data point — MUITO valioso)
   - **Torreira pelo POP:** o nome do pagador no extrato identifica a TowerCo (ex.: "American Tower … Cessão de Infra" = ATC), mesmo quando o contrato/operadora é outro (Vivo, Claro). Não confundir operadora-âncora com pagador.
   - **Extrato com vários lançamentos:** isolar a competência mensal do aluguel. Lançamentos extras no mesmo dia (retroativo de reajuste, IPTU, 2ª competência) ficam de fora do gross-up — sinalizar e pedir confirmação. Estornos de cartão/visa são ruído, ignorar.

2. **Gross-up de cada comprovante** com a tabela do ano correspondente. Sempre rodar via Python (bash_tool) pra não errar conta — ver snippet em `references/calc-snippet.py`.

3. **Escalonar o valor-base pelo IPCA** até o reajuste vigente. Buscar IPCA real via web_search.

4. **Decompor o que mudou** entre dois pagamentos (quando houver dois comprovantes):
   - Quanto do aumento do net é **reajuste de aluguel** (bruto subiu)
   - Quanto é **queda de retenção de IR** (tabela mudou)
   - Esse é o argumento mais forte: se o bruto implícito mal mudou (<1-2%) e o net subiu, **quase tudo foi IR**, não escalation.

5. **Reconciliar** contra o 3% default: `contratual × 1,03` costuma cair perto do bruto implícito do comprovante → mostrar que os métodos convergem.

6. **Gerar o e-mail** no tom do Lucas (ver template) ou devolver só os números, conforme o pedido.

## Honestidade (CRÍTICO)

- **Nunca afirmar uma causa que não se sustenta na verificação.** Se o bruto implícito do comprovante ficar consistentemente ~4% acima do contratual escalonado (estável em mais de um ano), isso **NÃO é "arredondamento" nem "retenção"** — esses explicam centavos e a diferença ano-a-ano, não um gap estrutural. Nesse caso, sinalizar honestamente ao Lucas que a base real do aluguel pode não ser a assumida, e perguntar como tratar (defender o bruto real observado, manter o contratual + 3% com ressalva, ou investigar a base real).
- **Não cravar o índice pelo gross-up.** Se o caminho contratual com IPCA bate no gross-up, isso **não prova** que o índice é IPCA — IPC-FIPE/IGP-M têm magnitude parecida em vários períodos e dariam gap semelhante. Reportar o bruto como robusto, mas marcar o índice como "a confirmar no aditivo/acordo assinado". Nunca afirmar "confirma IPCA" só porque fechou.
- O gross-up de **um pagamento isolado** é **sanity check**, não fonte de verdade — sempre enquadrar assim. A fonte de verdade é o valor contratual (aditivo + índice oficial).
- Não inventar IPCA de memória. Buscar sempre.

## Template do e-mail (tom do Lucas)

O Lucas escreve e-mails para San Diego em **inglês**, tom **conversado e humano** — primeira pessoa, direto, assume as coisas com naturalidade, sem estrutura de relatório com seções numeradas. Abre com a resposta, não com preâmbulo. Fecha leve oferecendo call.

Padrão validado (curto):

```
Hi [Nome],

Good catch — I looked into it and it's mostly a tax thing, not a rent increase.

In Brazil the rent has income tax withheld at the source, so what hits the account is net, not gross. The withholding table changed in Jan-2026 (new federal law that lowered the tax on this range), so the net went up even though the rent basically didn't.

I pulled [other year]'s proof of payment to compare: landlord netted R$ [net_A] then vs R$ [net_B] now. Grossing each one up with the table in force that year, the actual gross moved less than [X]% — so this isn't an off-cycle escalation, it's the [year]-vs-[year] tax change.

The only real escalation is the annual [month] IPCA adjustment: base R$ [base] ([date]) → R$ [current] today, next one due [next date]. On top of that we carry the usual 3% default (R$ [current] × 1.03 = R$ [carried]), which is right around where the grossed-up payments land anyway. The gross-up off a single net payment is just a sanity check — the contractual R$ [current] is the real figure, tied to the amendment and the index.

Happy to jump on a quick call if it's easier.

Best,
Lucas
```

Regras do e-mail:
- **Inglês**, valores em formato R$ X,XXX.XX (vírgula milhar, ponto decimal).
- Citar o 3% default como **referência conhecida**, nunca explicar do zero.
- Usar o **segundo comprovante** (outro ano) como prova quando disponível — dois data points reais valem muito mais que teoria pra quem audita.
- Frase-chave que responde diretamente: *"this isn't an off-cycle escalation, it's the [ano]-vs-[ano] tax change."*
- Não usar emojis no corpo do e-mail. Pode usar 1-2 na conversa lateral com o Lucas.
- Sempre usar o tool `message_compose_v1` (kind=email) pra entregar.

## Comportamento esperado

- Sempre rodar os cálculos via Python (bash_tool), nunca de cabeça.
- Sempre buscar o IPCA real via web_search antes de escalonar.
- Confirmar com o Lucas qual número defender quando houver gap estrutural (>3%) entre bruto implícito e contratual.
- Ao final, oferecer UMA melhoria opcional (ex.: "Quer a tabela visual dos dois comprovantes lado a lado pra anexar?").
- Confirmar a grafia do nome do destinatário antes de finalizar o e-mail.
- Quando o Lucas pedir só os números (sem e-mail), entregar a reconciliação em formato scaneável (verdict first).

## Referências auxiliares

- `references/ir-tables.md` — tabela IRRF completa 2025 vs 2026, fórmulas, exemplos numéricos validados
- `references/calc-snippet.py` — snippet Python pronto pra gross-up reverso (ambas as tabelas) e decomposição reajuste-vs-IR
- `references/worked-example.md` — casos validados: **L943649** (Claro/TBSA Mojú-PA) e **L884023** (ATC/Vivo, Ferreira Gomes-AP, com método "gross hoje" + honestidade de índice)
