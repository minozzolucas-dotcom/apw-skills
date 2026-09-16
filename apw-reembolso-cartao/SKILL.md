---
name: apw-reembolso-cartao
description: Fecha o reembolso mensal do cartão de crédito corporativo da APW Brasil — concilia o Form C/C (Solicitação de Cartão de Crédito APW) linha a linha contra os comprovantes, monta o PDF consolidado na ordem fixa (form → transporte por fornecedor → outras categorias → NFs uma por página com cabeçalho), limpa banners de extensão em prints exportados, converte HEIC/JPG em páginas A4 e gera o e-mail de aprovação pro Luiz Alfredo (cc contas a pagar). Use SEMPRE que o Lucas disser "reembolso do cartão", "form C/C", "formulário de cartão de crédito", "fecha o reembolso do mês", "prestação de contas do cartão", "junta os comprovantes num PDF", "manda pro Luiz aprovar", "cartão corporativo" — ou enviar a planilha de solicitação junto com recibos de Uber/ClickBus/Buser/99, NFs de restaurante ou comprovantes de hospedagem. Acione também se ele mandar só as fotos de NF perguntando se dá pra fechar. NÃO use para pagamento de fornecedor (apw-vendor-payment), wire de closing (apw-request-for-wire) nem despesas da Braus.
---

# APW Brasil — Reembolso do Cartão de Crédito Corporativo

Fecha o ciclo mensal: **conciliar → consolidar em PDF → enviar para aprovação**.

O deliverable é um PDF único, limpo, auditável, mais o e-mail de aprovação. Quem recebe (Luiz Alfredo e contas a pagar) precisa conferir em 30 segundos que cada linha do formulário tem comprovante. Todo o resto da skill existe para tornar essa conferência trivial.

## Contexto fixo

**Antes de qualquer coisa, leia `references/form-cc.md`.** Ele traz a planilha
canônica do Form C/C (Google Sheets `1G3EdXizNyJgFc_-Gnyl_XdsZnZXm8BoZDUAOrYFK6kw`),
a taxonomia fechada de categorias, os precedentes de classificação do Lucas e as
armadilhas já verificadas do formulário. Classificar despesa sem consultar esse
arquivo leva a categoria inventada, que some do resumo do rodapé.

| Item | Valor |
|---|---|
| Formulário | "Solicitação de Cartão de Crédito - APW Brasil" (Form C/C), Google Sheets |
| Aprovador | Luiz Alfredo (Country Leader) |
| Cópia | contasapagar@apwbrasil.com.br + Ana Silva |
| Nome do PDF | `Reembolso_Lucas_Minozzo_<mes>_<ano>.pdf` |
| Assunto do e-mail | `Aprovação Form C/C - <mes>/<mes2> <ano> - Lucas Minozzo` |

## Fluxo

### 1. Inventariar os anexos

Liste tudo que chegou em `/mnt/user-data/uploads` antes de qualquer coisa. Classifique cada arquivo:

- **Form C/C** — a planilha/PDF com as linhas de despesa e o TOTALIZADOR
- **Comprovante de transporte** — ClickBus, Buser, Uber, 99, passagem aérea, pedágio
- **Comprovante de outras categorias** — assinatura, anuidade, hospedagem, estacionamento
- **NF de alimentação/miscelânea** — foto ou print de cupom fiscal (frequentemente HEIC do iPhone)

Rode `scripts/inventario.py <pasta>` — ele lista os arquivos, calcula MD5 e **sinaliza duplicatas exatas**. Print duplicado é comum (o mesmo comprovante salvo duas vezes) e entra uma vez só no PDF.

### 2. Conciliar antes de montar

Extraia as linhas do Form C/C (data, descrição, categoria, valor) e case cada uma com um comprovante. Esta é a parte que mais gera retrabalho quando pulada — em junho/2026 o PDF foi montado e só depois se descobriu que a maior linha (restaurante) estava sem NF.

Monte a tabela de conciliação e mostre ao Lucas **antes** de gerar o PDF:

| # | Data | Descrição | Categoria | Valor | Comprovante |
|---|---|---|---|---|---|
| 1 | 12/06 | ClickBus SP→Atibaia | Transporte | R$ 68,90 | `clickbus_1206.pdf` ✅ |
| 2 | 14/06 | Restaurante X | Alimentação | R$ 187,50 | **faltando** ⚠️ |

Confira três somas, não uma:

1. soma das linhas do formulário == TOTALIZADOR
2. soma do resumo por categoria == TOTALIZADOR (esta é a que costuma quebrar)
3. TOTALIZADOR == total da fatura do cartão

Divergência de centavos costuma ser fórmula quebrada na planilha; divergência
maior costuma ser linha esquecida ou categoria fora da taxonomia, que não entra
em nenhuma coluna do resumo. Avise o Lucas em vez de corrigir em silêncio — a
planilha é dele e o erro pode estar na origem.

Se faltar comprovante, pergunte antes de montar. O Lucas normalmente tem a foto no celular e manda na hora.

### 3. Preencher o Form C/C e converter para PDF

Preencha as linhas no layout exato da planilha de referência (ver `references/form-cc.md`
para o mapa de células) e **sempre entregue também em PDF** — é o PDF que entra
como página 1 do consolidado; o `.xlsx` vai junto no e-mail para o financeiro
poder editar se precisar.

```bash
soffice --headless --convert-to pdf --outdir <dir> Form_CC_<periodo>.xlsx
```

Duas coisas que quebram silenciosamente na conversão e precisam ser conferidas
**renderizando o PDF**, não confiando no Excel:

- **Colunas estreitas viram `###`.** No Excel a célula expande e você não percebe;
  no PDF chega assim ao aprovador. Dê largura folgada às colunas de data e valor.
- **A planilha não cabe numa página.** `page_setup.fitToWidth = 1` sozinho não faz
  nada — o openpyxl precisa também de
  `ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)`.
  Sem isso as colunas de Valor e Total vão parar numa página 3 solta.

Confira sempre: PDF com **1 página** e sem `###` no texto extraído.

### Assinatura

Preencha o bloco do funcionário simetricamente ao do supervisor — linha de rubrica,
`LUCAS MINOZZO`, `NOME DO FUNCIONÁRIO` embaixo, mais o carimbo
"Assinado eletronicamente em <data>". É o padrão que o formulário já usa do lado
do Luiz Alfredo.

Nome digitado, nunca uma rubrica cursiva desenhada: inventar o traço da caligrafia
dele produz um autógrafo que o Lucas nunca fez, num documento que vai para o
financeiro. Se ele mandar a assinatura digitalizada em imagem, aí sim insira na
linha de rubrica.

### 4. Montar o PDF consolidado

Ordem fixa (é a ordem que o financeiro espera; não invente outra):

1. Form C/C preenchido e assinado (em PDF)
2. Comprovantes de transporte, **agrupados por fornecedor** (todos os ClickBus juntos, todos os Uber juntos)
3. Comprovantes de outras categorias
4. NFs de alimentação/miscelânea ao final, **uma por página**, cada uma com cabeçalho identificando estabelecimento, data, categoria e valor

Use `scripts/montar_pdf.py manifest.json` — o manifest declara os blocos na ordem. Ele cuida de:

- **Limpeza de banner**: prints exportados como PDF pelo navegador carregam a faixa "Claude is active in this tab group" e ícones de extensão. O script cobre a área com retângulo branco (padrão x=120–480, y=30–130 em A4) e **re-renderiza a página para você conferir visualmente**. Se sobrar sombra ou borda, aumente a área no manifest (`banner_box`) e rode de novo. Deixar isso passar é constrangedor num documento que vai pro financeiro.
- **HEIC/JPG/PNG**: converte via `pillow-heif` e encaixa a imagem numa página A4 nova, centralizada, preservando proporção, com o cabeçalho no topo.
- **Rotação**: fotos de cupom de celular vêm com EXIF girado. O script aplica `ImageOps.exif_transpose`.

Formato do manifest em `references/manifest-exemplo.json`.

### 5. Conferir antes de entregar

Renderize pelo menos duas páginas em PNG e mostre ao Lucas:
- uma página que teve banner removido (para provar que sumiu mesmo)
- uma página de NF (para conferir que o cabeçalho e o valor estão certos)

Reporte: número total de páginas, total do formulário, quantas linhas têm comprovante anexado.

Entregue o PDF com `present_files`.

### 6. E-mail de aprovação

Use o widget `message_compose_v1` (tipo `email`). Tom: direto, casual, PT-BR — é o tom que o Lucas usa com o Luiz.

```
Para: Luiz Alfredo
Cc: contasapagar@apwbrasil.com.br, Ana Silva
Assunto: Aprovação Form C/C - <mes>/<mes2> <ano> - Lucas Minozzo

Oi Luiz,

Segue para aprovação o formulário de cartão de crédito referente ao período
de <mes>/<mes2> <ano>, no valor total de R$ <total>.

Resumo por categoria:
- Transporte: R$ X (deslocamentos SP/Atibaia e visitas a sites)
- Alimentação: R$ Y (almoço com o time — team building a pedido do <fulano>)
- Hospedagem: R$ Z
[só as categorias com valor > 0]

No PDF anexo seguem:
- Formulário preenchido e assinado
- Comprovantes de transporte por fornecedor
- Notas fiscais de alimentação

Qualquer dúvida, me avisa.

Abraço,
Lucas
```

Regras do corpo:
- Liste **apenas categorias com valor > 0**.
- Despesa que precisa de justificativa (team building, jantar com contraparte, gasto a pedido de terceiro) ganha a observação entre parênteses na própria linha. Aprovador que precisa perguntar "o que é isso?" é aprovação atrasada.
- Nunca invente justificativa. Se a natureza da despesa não está clara no formulário, pergunte ao Lucas.

O widget gera rascunho — **o envio é sempre do Lucas**.

## Armadilhas conhecidas

- **Duplicata de print** — mesmo recibo salvo duas vezes com nomes diferentes. Sempre rode o MD5.
- **HEIC** — o Preview do Mac não converte sozinho; sem `pillow-heif` o arquivo simplesmente não abre.
- **Linha sem comprovante** — o erro mais caro, porque volta do financeiro e o ciclo reinicia. Concilie na etapa 2, não depois.
- **Banner de extensão** — some no print da tela mas aparece no PDF exportado.
- **Valor da NF ≠ valor da linha** — cupom com gorjeta incluída vs. valor lançado. Confira antes de incluir e sinalize a diferença.

## Escopo

Esta skill cobre o cartão corporativo **do Lucas**. Não cobre pagamento a fornecedor com NF-e e dados bancários (`apw-vendor-payment`), wire de closing (`apw-request-for-wire`) nem despesas pessoais/Braus.
