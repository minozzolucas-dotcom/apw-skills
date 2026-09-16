---
name: apw-email-semanal-comercial
description: >
  Monta o e-mail semanal de resultados do time comercial da APW Brasil (o "e-mail de
  segunda" do Diogo) + os 2 PNGs de KPI na marca — consolidado (semana/mês/ano) e por
  diretor. Puxa Stage 1/3/5/8/99 por diretor do Dynamics via Web API e completa o bloco
  financeiro do ano com o Power BI. Calcula sozinha o desafio até dezembro (quantos
  deals faltam, por mês, por diretor) e a leitura de ranking e pipeline. Use SEMPRE
  com "e-mail semanal", "e-mail de segunda", "e-mail do time comercial", "monta o
  e-mail do Diogo", "roda os KPIs da semana", "KPIs semana mês ano", "PNG por diretor",
  "quantos deals faltam pro ano", ou ao colar prints do Power BI / da view Opportunity
  Stage by Owner pedindo o e-mail. Acione também se ele mandar só os números pedindo
  "monta igual ao do Diogo". NÃO use
  para reporte DIÁRIO (apw-reporte-crm-diario), deep dive de S3/repropostas
  (apw-deepdive-s3-reproposta), benchmark de conversão (apw-performance-patterns) nem
  consulta pontual ao CRM (apw-dynamics-copilot).
---

# E-mail Semanal Comercial — APW Brasil

Toda segunda-feira o time comercial recebe um e-mail com os resultados: o que fechou no
ano, como foram o mês e a semana, onde está o pipeline e o que precisa acontecer daqui
pra frente. Esta skill produz esse pacote inteiro — **o texto do e-mail + dois PNGs** —
a partir dos dados do CRM.

Carregue **`apw-brand`** junto: paleta, tipografia e razão social vêm de lá e não se
negocia cor aqui.

## O que é entregue

1. **Texto do e-mail** — em português, na voz do Diogo (ver `references/voz-do-email.md`),
   pronto pro Lucas colar no Outlook e ajustar o que quiser.
2. **PNG consolidado** — funil da semana e do mês lado a lado, cards do ano, faixa navy
   do desafio até dezembro.
3. **PNG por diretor** — uma linha por diretor com semana, mês e ano, ordenado por deals
   fechados no ano, com linha de TOTAL BRASIL.

Os dois PNGs saem do mesmo script (`scripts/build_png.py`) alimentado por um único
`data.json`. O e-mail o Claude escreve lendo esse mesmo `data.json` — assim texto e
imagem nunca divergem.

## Pipeline

### 1. Coleta — Dynamics primeiro

Via **Claude in Chrome**, numa aba já autenticada em `https://apwireless.crm.dynamics.com`,
cole `references/collection.js` no `javascript_tool`. Ele usa a sessão do Lucas, puxa tudo
por Web API JSON e devolve o esqueleto do `data.json` com os movimentos por diretor nas
três janelas.

Regras de compliance (skill `apw-chrome-agent-lean-compliance`): **tudo por Web API JSON**.
`read_page`, `get_page_text` e **screenshot** são proibidos em domínio Dynamics. Se der
401/403, reabra a aba, espere, tente uma vez — se persistir, pare e avise. Nunca invente
número.

### 2. Complemento — Power BI

Quatro campos do bloco do ano **não são derivados com segurança da Web API** e vêm dos
prints do Power BI que o Lucas manda (ou do relatório "Brazil — Acquisition Directors"):

- `ano.adquirido` (Acquired Rent / valor adquirido)
- `ano.meta` (Target do ano)
- `ano.pipeline` (valor em pipeline)
- `ano.pct` (% da meta) e o `%` por diretor

Motivo: esses valores dependem de regras de rateio e de câmbio que moram no modelo do
Power BI, não em campos crus da oportunidade. Tentar recalcular gera número que não bate
com o que a liderança vê — pior do que não ter. Peça o print ou o número; se o Lucas não
tiver, deixe o campo `null` e o PNG omite o card em vez de chutar.

Se o Lucas mandar **só os prints** (sem acesso ao CRM naquele momento), a skill roda em
modo manual: transcreva os números para o `data.json` e siga. O caminho Dynamics é o
preferido porque elimina erro de digitação, não porque o print seja inválido.

### 3. Conferência antes de renderizar

Sempre confira, e mostre a conferência ao Lucas em uma linha:

- soma dos diretores = total, em **cada** coluna de cada janela;
- se o total do ano não bater com a soma dos diretores, a diferença são deals de owner
  fora da lista (pool) — registre isso em `obs`, não force o número;
- deals do ano ≥ deals do mês ≥ deals da semana (se não, a janela está errada).

Divergência entre o que o Lucas afirma de cabeça e o que o CRM mostra acontece — o caso
clássico é submission: ele conta a submission enviada, o CRM só marca quando o estágio
vira. Quando isso acontecer, **use o número do Lucas no texto**, mantenha o número do CRM
na tabela, e diga a ele numa frase que os dois não batem e por quê. Não escolha em
silêncio.

### 4. Build dos PNGs

```bash
python3 scripts/build_png.py data.json /sessions/.../mnt/outputs
```

Gera `APW_KPIs_semana_mes_ano_<DD-MM-AAAA>.png` e `APW_KPIs_por_diretor_<DD-MM-AAAA>.png`.

Renderização é **Pillow puro**, sem navegador. Este sandbox não tem chromium nem
playwright — a tentação de reaproveitar o pipeline HTML→Chrome de outras skills APW
custa uma rodada inteira de debug. Pillow com supersampling 2× e downsample LANCZOS dá
resultado tipograficamente limpo e roda em qualquer lugar.

### 5. E-mail

Escreva o texto lendo o `data.json` e `references/voz-do-email.md`. Entregue **no chat**,
em texto corrido, pro Lucas copiar. Os PNGs ele arrasta pro corpo do e-mail.

**Nunca enviar e-mail** — nem via MCP, nem agendado. A skill produz; quem dispara é o
Lucas. Isso vale mesmo que ele diga "manda" — confirme que quer dizer "me entrega".

## A conta do desafio (faça sempre, é o coração do e-mail)

```
faltam        = meta_ano_deals − ano.deals
por_mes       = faltam ÷ meses_restantes
por_diretor   = faltam ÷ n_diretores
por_dir_mes   = por_diretor ÷ meses_restantes
```

Apresente arredondado e humano: "3 a 4 deals por diretor", "0,7 deal por diretor por mês",
"10,4 deals por mês no time". A graça dessa conta é que ela transforma um número que
assusta (52) em um que cabe no mês de uma pessoa. Não perca isso escrevendo só o total.

`meses_restantes` conta o mês corrente se ele ainda tem semanas úteis pela frente. Em
03/08/2026: agosto a dezembro = 5.

## A leitura (o que dá valor ao e-mail)

O e-mail não é um despejo de tabela. Depois dos números, entregue 2 a 4 observações que
só quem olhou os dados faria. Procure especificamente por:

- **Concentração** — quantos diretores respondem por metade dos deals do ano. Cinco
  pessoas segurando 30 de 48 é um fato acionável, não uma crítica.
- **Estoque parado** — diretor com muito Stage 1/Stage 5 no mês e zero fechamento. É o
  melhor lugar do e-mail: tem material, falta converter em carta de intenção.
- **Gargalo de submission** — de quantas pessoas diferentes vieram as submissions do mês.
  Motor estreito é o sintoma mais caro do pipeline APW.
- **Quem destoa pra cima** — sem troféu, sem superlativo. "Fez 21 Stage 1 e 8 Stage 3 no
  mês" já diz tudo.

Escreva como observação de quem lê o funil, não como avaliação de pessoa. O e-mail vai
pro time inteiro; ninguém deve se sentir exposto — e ninguém deve poder ignorar o dado.

## Vocabulário dos estágios

Stage 1 = qualificação · Stage 3 = proposta · Stage 5 = contrato enviado ·
Stage 6 = LOI assinada recebida · Stage 8 = submission (IC) · Stage 99 = fechado e fundeado.

No e-mail use a palavra em português (qualificação, proposta, contrato, submission,
fechamento) com o stage entre parênteses na primeira menção. No PNG cabe só o rótulo curto,
com a legenda no rodapé.

## Arquivos

- `references/collection.js` — coleta Web API. Descobre em runtime os campos de data de
  Stage 5 e Stage 8 (não são estáveis entre ambientes; `apwip_stage1date` **não existe** —
  o campo de Stage 1 é `apwip_stage1_obtainedleaseeconomics`). Leia antes de colar.
- `references/voz-do-email.md` — a voz do Diogo, a estrutura fixa do e-mail e o e-mail de
  referência real. Leia sempre antes de escrever o texto.
- `references/data.exemplo.json` — rodada real de 03/08/2026, com todos os campos
  preenchidos. Use como schema e como teste do `build_png.py`.
- `scripts/build_png.py` — renderizador Pillow dos dois PNGs.

## Janelas de data

- **Semana** — segunda a domingo anterior (o e-mail sai na segunda falando da semana que
  fechou). Em 03/08/2026: 28/07 a 03/08 conforme o recorte do Power BI (últimos 7 dias);
  confirme qual recorte o print usa e carimbe no PNG o que foi usado.
- **Mês** — últimos 30 dias corridos no Power BI ("last month"), não mês calendário.
  Escreva a data exata no PNG (04/07 – 03/08) pra ninguém confundir com "julho".
- **Ano** — 01/01 até hoje.

Carimbe sempre as datas reais no PNG. Semana que vem alguém vai comparar os dois e-mails
lado a lado, e a diferença de recorte precisa ser visível.
