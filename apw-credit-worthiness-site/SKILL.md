---
name: apw-credit-worthiness-site
description: Gera relatório HTML de Credit Worthiness (qualidade de crédito) de uma operadora de telecom locatária, para sustentar a aquisição de um terreno/site pela APW Brasil perante investidores Radius. Use SEMPRE que o Lucas mencionar "credit worthiness", "análise de crédito da operadora", "atestar números saudáveis", "due diligence do pagador", "a operadora paga o aluguel", "comprar o terreno da torre", "convencer investidores Radius", ou enviar o nome de uma tele (Algar, Vivo, Claro, TIM, Oi, Brisanet, etc.) pedindo para avaliar se ela é um pagador sólido para um aluguel de site. Também acione quando ele pedir comparativo financeiro entre operadoras telecom no contexto de aquisição. NÃO use para análise de cláusula contratual (apw-telecom-real-estate-counsel) nem dossiê de deal por código L (apw-deal-dossier).
---

# APW Credit Worthiness — Site / Operadora Locatária

## O que esta skill faz

Gera um relatório HTML profissional, na identidade visual APW Brasil, que **atesta a qualidade de crédito da operadora de telecom locatária** de um site cuja propriedade (o terreno) a APW pretende adquirir. O documento é feito para ser apresentado aos **investidores da Radius**, que exigem ver "números saudáveis" antes de aprovar a aquisição.

O output é um arquivo `.html` autocontido, pronto para abrir no navegador, exportar para PDF ou enviar por email.

## A tese central (não esqueça disto)

A APW **não compra o risco de equity da operadora** — compra **o terreno** e, junto, o direito de receber o aluguel. Toda análise se organiza em **duas camadas de proteção**:

1. **Camada 1 — fluxo de aluguel.** A operadora consegue honrar uma despesa operacional pequena e recorrente (aluguel da ERB) pelo prazo do contrato? Aluguel de site é custo de rede, altamente prioritário — das últimas contas que uma tele deixa de pagar.
2. **Camada 2 — ativo real.** Se a Camada 1 falhar (default, descomissionamento, M&A), a APW **ainda é dona do terreno**. O capital fica lastreado em imóvel real, com opção de relocação ou venda.

É a Camada 2 que transforma o caso de "bom" em **"alternativa segura"**. Sempre enquadre o negócio como **risco assimétrico**: downside limitado (perda total improvável), upside no fluxo + valorização do solo.

Pontos de enquadramento que o Lucas valoriza:
- **Ticket baixo** → reforçar que é valor reduzido em USD, posição pequena de portfólio.
- **Portfolio approach** → o caso é o tipo de aquisição que estabiliza o portfólio; alternativa segura de alocação.
- **Prejuízo contábil ≠ incapacidade de pagar** → prejuízo de operadora telecom costuma ser não-caixa (depreciação, amortização, despesa financeira). Sempre explicar isso.

## Quando acionar

Gatilhos típicos: "monta o credit worthiness da [operadora]", "preciso atestar que a [tele] é boa pagadora", "due diligence do pagador do aluguel", "os investidores da Radius querem ver números", "vamos comprar o terreno onde a [tele] é locatária", "compara os financials da [tele] com Vivo/Claro/TIM".

NÃO use para: análise de cláusula de cessão/contrato (`apw-telecom-real-estate-counsel`), dossiê de deal por código L (`apw-deal-dossier`), forensics de atividades (`apw-opp-activity-forensics`).

## Inputs — pergunte só o que faltar

Antes de gerar, confirme (UMA vez, agrupado):

| Input | Obrigatório? | Default se omitido |
|---|---|---|
| Operadora locatária | Sim | — perguntar |
| Valor da aquisição (ticket) | Sim | — perguntar; mencionar que é baixo em USD |
| Idioma (PT / EN / ambos) | Não | PT; gerar ambos se houver investidor estrangeiro |
| Foto da torre/site | Não | placeholder estilizado (instruções no template) |
| Localização do terreno | Não | omitir; sinalizar como item de due diligence |

Se o Lucas não der o ticket, ainda assim gere — mas deixe o card de valor como `[A DEFINIR]` e sinalize.

## Workflow

### 1. Buscar dados financeiros recentes (web_search)
Para a operadora-alvo, buscar **o trimestre mais recente + o ano fechado mais recente + o rating de crédito mais recente**. Queries enxutas (1-4 palavras): `"[operadora] resultado trimestre"`, `"[operadora] resultado anual"`, `"[operadora] rating S&P Fitch Moody's"`, `"[operadora] dívida vencimento"`.

KPIs a extrair: receita líquida, EBITDA e margem, dívida líquida, alavancagem (Dív.Líq./EBITDA), fluxo de caixa operacional livre, capex/receita, resultado líquido, perfil de vencimento da dívida, rating + perspectiva.

**Sempre cite as fontes** no rodapé e use `<cite>` ao afirmar números na resposta do chat.

### 2. Buscar comparativo setorial (se pedido ou se agregar valor)
Buscar os mesmos KPIs para **Vivo (Telefônica Brasil), Claro (América Móvil), TIM Brasil** — os três grandes nacionais. Servem de benchmark.

**Regra de honestidade:** se a operadora-alvo for menor/mais fraca que os três grandes (quase sempre será, exceto se for um dos três), **diga isso abertamente** no relatório e em seguida explique por que não derruba a tese (crédito ainda sólido + aluguel é despesa crítica + a tese não depende só do pagador, pois há o terreno). Investidores confiam mais em análise que reconhece a fraqueza do que em peça de venda.

### 3. Montar o HTML
Usar `assets/template.html` como base. É um template completo, já no brand APW. Substituir os blocos marcados com `{{...}}` e ajustar seções. Estrutura fixa do documento:

1. Header (operadora, CNPJ, data-base, finalidade)
2. **O Ativo** — foto da torre (ou placeholder) + legenda
3. **Veredito do Comitê** — banner verde "Alternativa Segura / risco muito baixo"
4. **Economia do Negócio** — 3 cards (ticket / natureza do ativo / perfil de risco) + callout verde de downside protection
5. **KPIs** — grid de 8 indicadores do trimestre mais recente
6. **Rating de crédito** — strip com badge
7. **Comparativo Setorial** — tabela operadora-alvo vs. Vivo/Claro/TIM (coluna do alvo destacada) + callout de leitura honesta
8. **Trajetória** — barras de EBITDA trimestral (recuperação/tendência)
9. **O Que Realmente Importa** — bloco das duas camadas de proteção
10. **Riscos × Pontos Favoráveis** — duas colunas
11. **Cenários Probabilísticos** — base / otimista / adverso (no adverso, sempre frisar que a APW retém o terreno → perda total improvável)
12. **Ponto de Atenção / Viés** — callout âmbar (alertar contra superestimar valor de revenda do terreno)
13. **Próximos Passos** — lista numerada
14. Footer com fontes

### 4. Entregar
Salvar em `/mnt/user-data/outputs/` como `credit_worthiness_[operadora]_APW.html` (e `_EN.html` se bilíngue). Chamar `present_files`. Resposta no chat curta, com os 3-4 números-chave citados e os caveats (foto, avaliação do terreno).

## Identidade visual APW Brasil (não desviar)

Paleta oficial, já embutida no template como CSS variables:

| Token | Hex | Uso |
|---|---|---|
| `--apw-blue` | `#4e89bd` | Cor primária: header, headers de tabela, filetes, badges |
| `--apw-blue-dark` | `#3b6e99` | Header da coluna destacada |
| `--apw-blue-light` | `#f4f8fb` | Zebrado, fundos suaves |
| `--apw-blue-border` | `#d6dde5` | Bordas |
| `--apw-text` | `#1f2d3d` | Texto/títulos |
| `--apw-green` | `#2b8a3e` | Veredito positivo, downside protection, cenário base |
| `--apw-red` | `#a83232` | Riscos, cenário adverso |
| `--apw-amber-accent` | `#d68910` | Callout de atenção/viés |
| `--apw-bg` | `#eef2f6` | Fundo da página |

Tipografia: **Arial** (web-safe, consistente com material APW). Card branco centralizado, máx. 920px. Sem emojis no corpo (o ícone de antena no placeholder é a única exceção). Tom: analítico, direto, sem floreio de venda.

## Princípios inegociáveis

1. **Nunca invente números.** Todo dado financeiro vem de web_search com fonte citada. Se não achar, deixe `[verificar na fonte]` e sinalize.
2. **Sempre as duas camadas.** O relatório sem a Camada 2 (terreno) é só metade da tese — e a metade fraca.
3. **Honestidade no benchmark.** Reconheça a fraqueza da operadora-alvo vs. pares; investidor sofisticado detecta peça de venda.
4. **Prejuízo contábil é explicado, não escondido.** Sempre distinguir prejuízo não-caixa de incapacidade de pagar.
5. **Caveat do terreno.** Sempre incluir o aviso de não superestimar valor de revenda no cenário adverso, e recomendar avaliação conservadora na due diligence.
6. **Disclaimer.** Rodapé sempre deixa claro: documento interno de suporte à decisão, não é recomendação de investimento nem auditoria.

## Erros comuns a evitar

- Tratar o caso como análise de equity da operadora (é análise de *capacidade de pagar aluguel* + *valor do terreno*).
- Esconder o prejuízo líquido ou a alavancagem alta — minar a credibilidade.
- Esquecer a foto: o template tem placeholder com instrução; se o upload não chegar, manter o placeholder e avisar o Lucas.
- Usar dados de trimestres antigos quando há resultado mais recente — sempre buscar o último divulgado.
- Gerar só PT quando há investidor Radius (estrangeiro) envolvido — nesse caso, gerar EN também.
