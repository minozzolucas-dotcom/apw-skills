# Form C/C — "Solicitação de Cartão de Crédito · APW Brasil"

## Planilha de referência (canônica)

Google Sheets ID: `1G3EdXizNyJgFc_-Gnyl_XdsZnZXm8BoZDUAOrYFK6kw`

https://docs.google.com/spreadsheets/d/1G3EdXizNyJgFc_-Gnyl_XdsZnZXm8BoZDUAOrYFK6kw/edit

Use sempre esta planilha como modelo de layout e de convenções. Cada mês o Lucas
tira uma cópia ("Cópia de Form C/C Lucas - <Mês> <Ano>"). Para ler o conteúdo:
`Google Drive:download_file_content` com `exportMimeType: text/csv`.

## Cabeçalho (campos fixos)

| Campo | Valor |
|---|---|
| ÁREA DO REQUERENTE | ACQUISITION |
| NOME DO REQUERENTE | LUCAS MINOZZO |
| NOME DO APROVADOR | LUIZ ALFREDO |
| PERÍODO DA DESPESA | DE: / ATÉ: (datas do ciclo do cartão) |

Data do documento no canto superior direito.

## Colunas de lançamento

`Data | Descrição de Despesa | (descrição livre/justificativa) | Categoria | Valor | Total`

A coluna de descrição livre é onde entra a justificativa — é ali que o Lucas
escreve coisas como "lanches visita kevin e barbara e johhan" ou "almoço visita".
Despesa que precisa de contexto para o aprovador ganha texto aqui, não no e-mail.

## Taxonomia de categorias — FECHADA

Só existem estas oito, e são as colunas do resumo no rodapé:

`MATERIAL DE ESCRITÓRIO · TRANSPORTE · CARTÓRIO · ALIMENTAÇÃO · HOSPEDAGEM · ENTRETENIMENTO · MISCELANEA · KM`

Não invente categoria. "Tarifa bancária", "Assinatura", "Ensino" não existem — e
quando uma categoria fora da lista é usada, o valor some do resumo do rodapé
(aconteceu com JUSBRASIL lançado como "ENSINO" em jun/2026).

### Precedentes de classificação do Lucas

- **Anuidade do cartão** (ANUIDADE 0X/04) → MISCELANEA
- **iFood / delivery** (IFD*BR) → MISCELANEA
- **Restaurante presencial** (ex.: 1791 Parrilla Jardins) → ALIMENTAÇÃO
- **Ônibus** (Buson, ClickBus / BUS SERVICOS*CLIC) → TRANSPORTE

A distinção delivery-vs-presencial é dele; siga o precedente em vez de
reclassificar por conta própria.

## Rodapé

- **TOTALIZADOR** — soma de todas as linhas
- **Linha de resumo por categoria** — uma coluna por categoria
- Blocos de ASSINATURA DO FUNCIONÁRIO e ASSINATURA DO SUPERVISOR (Luiz Alfredo),
  com o texto de certificação de que os gastos são comerciais e reembolsáveis

## Armadilhas verificadas

**O resumo por categoria não reconcilia sozinho.** No form de jun/2026 as fórmulas
do rodapé não cobriam todas as linhas: categorias somavam R$ 1.747,15 contra um
TOTALIZADOR de R$ 3.126,81 (o TOTALIZADOR estava certo). Sempre confira
`soma das categorias == TOTALIZADOR` e avise o Lucas quando não bater.

**Formato de data inconsistente.** A mesma planilha mistura `27/05/2026` (dd/mm)
e `5/26/2026` (mm/dd) porque o Sheets interpreta parte das entradas como data
americana. Ao ler, desambigue pelo contexto do ciclo; ao escrever, padronize
dd/mm/aaaa.

**PERÍODO DA DESPESA costuma vir mal preenchido** (em jun/2026 estava "DE: 1/1/2026",
"ATÉ:" vazio). Preencha com as datas reais do ciclo.

## Convenção de período

O ciclo do cartão vai de ~dia 28 a ~dia 26 do mês seguinte, e a fatura fecha no
mês subsequente. O Lucas rotula pelo **ciclo**, não pelo mês da fatura — as pastas
históricas no Drive são "2 mar a 2 abr", "2/set a 2/out". Confirme com ele quando
houver ambiguidade.
