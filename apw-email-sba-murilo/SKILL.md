---
name: apw-email-sba-murilo
description: Gera e-mails curtos e padronizados para o Murilo Gonçalves da SBA Torres a partir de inputs brutos do time APW (linhas de planilha, mensagens de Teams, parágrafos, ou listas em batch). Use SEMPRE que o Lucas mandar dados de um deal — código L, ID SBA, endereço, coordenadas, operadoras, aluguel — pedindo "manda pro Murilo", "monta e-mail Murilo SBA", "encaminha pro Murilo", "faz o e-mail desse caso", ou colar transcrição/print do time interno (Anaclara, Letícia, etc.) com casos para abrir com a SBA. Também acione com menções a sbasite.com, MGoncalves@sbasite.com, ou IDs SBA no formato BRxxxxx-A. NÃO use para outras torreiras (American Tower, IHS, ATC, Highline), nem para a rotina diária de varredura/atualização de planilha (essa é apw-sba-daily-routine), nem para análise de cláusula contratual (apw-telecom-real-estate-counsel).
---

# apw-email-sba-murilo

Gera e-mails individuais para o Murilo da SBA (MGoncalves@sbasite.com) a partir de qualquer formato bruto de input — mensagem de Teams do time interno APW, linha de planilha, parágrafo solto, ou batch de casos numa lista só.

## Tom e formato (FIXO — não improvisar)

Murilo é técnico, operacional, lê dezenas de e-mails por dia. O padrão é **curto, com cabeçalho de campos em negrito, sem narrativa de contexto, sem call to action longo**.

Template canônico:

```
Murilo, [bom dia / boa tarde].

Encaminho abaixo caso para análise.

**Deal:** L[xxxxxx] - [Nome do LL / contraparte]
**Site SBA:** BR[xxxxx]-A
**Endereço:** [logradouro], [nº], [bairro], [Cidade]/[UF]
**Coordenadas:** [lat], [long]
**Operadoras no site:** [Operadora] ([gerações]) e [Operadora] ([gerações])
**Aluguel:** R$ [valor]

Abs,
```

**Assunto fixo:**
`L[xxxxxx] - [BR_ID] - [Cidade]/[UF] - [Nome do LL]`

Se algum campo não vier no input, **OMITIR a linha inteira** (não escrever "não informado", não inventar). Se o aluguel não vier, perguntar se quer omitir, pedir confirmação do Murilo, ou pôr aproximado.

## Parsing

O input do time costuma vir em formatos variados:

**Formato 1 — linha curta colada:**
`BR66231-A- L368344_SBA_Enio Zanan- RUA PARACAIMA 223, Rio de Janeiro / RJ - TIM 2G/3G/4G/5G - R$ 6.437,42`

**Formato 2 — bloco com labels:**
```
Trajano Carlos Porto – L969223
Endereço do site: Rua Rouxinol, s/n°, ...
-23.18192 -47.09403 ID site: BR635969-A
O site possui duas operadoras: Vivo 2G/3G/4G e Claro 3G/4G.
O aluguel no POP é: 7.205,50.
```

**Formato 3 — batch (vários casos numa mensagem só):** trate cada caso como e-mail separado.

### Extração

Procure (case-insensitive, regex tolerante):

- **L number:** `L\d{5,7}` — pode vir com underscore (`L368344_SBA_...`), traço (`- L368344`), ou dois pontos
- **SBA ID:** `BR\d{4,7}-[A-Z]` — case sensitive no `BR` mas `-a` / `-A` aceitar ambos
- **Nome do LL:** geralmente após o L ou SBA ID, separado por `_`, `-`, ou em linha própria ("Trajano Carlos Porto")
- **Endereço:** depois de "Endereço:", "Rua", "Av", "Avenida", "Travessa" — capturar até cidade/UF
- **Coordenadas:** dois floats com sinal, separados por espaço/vírgula, no range BR (lat: -33 a 5, long: -74 a -34)
- **Operadoras:** Vivo, TIM, Claro, Oi, Algar, Brisanet — seguidas de gerações (2G/3G/4G/5G). Frase "O site possui X operadoras" é dica
- **Aluguel:** `R$ X.XXX,XX` ou número solto após "aluguel", "POP é", "rent" — normalizar para `R$ X.XXX,XX` BR

### Normalização

- **Endereço:** capitalizar (não MAIÚSCULAS), padronizar `Rua` em vez de `RUA`, `nº` em vez de `n°` se quiser, manter vírgulas
- **Cidade/UF:** sempre `Cidade/UF` (com barra, sem espaço)
- **Operadoras:** sempre `Vivo`, `TIM` (maiúsculo), `Claro`, `Oi`, `Algar`, `Brisanet`; gerações entre parênteses: `Vivo (2G/3G/4G)`
- **Coordenadas:** `-23.18192, -47.09403` (com vírgula entre e ponto decimal)
- **Aluguel:** sempre BR — `R$ 7.205,50`

## Saudação

- Default: usar `boa tarde` se for entre 12:00–18:00 BRT, `bom dia` antes, `boa noite` depois.
- Se não souber a hora, usar `boa tarde` (é o padrão histórico do Lucas).

## Entrega

Use SEMPRE o `message_compose_v1` com `kind: "email"`. **Um variant por caso.** Para batch de N casos, gerar 1 chamada com N variants (cada um com label `L[xxxxxx] - [Nome curto]`).

**Não** entregar como bloco de texto no chat — sempre via `message_compose_v1`, porque o Lucas copia direto do widget.

## Edge cases

1. **Aluguel ausente:** perguntar 1x ao Lucas — "quer omitir, pedir confirmação ao Murilo, ou pôr como aproximado?". Se ele já indicou preferência antes na conversa, seguir.
2. **Typo óbvio no valor** (ex: `R$ 35.00,00`): sinalizar e perguntar antes.
3. **Coordenadas faltando:** OK omitir, são úteis mas não bloqueantes.
4. **Site sem ID SBA:** OK omitir a linha `Site SBA:`. Pode ser caso que ainda não está no inventário deles.
5. **Endereço com `s/n°`:** preservar exatamente assim, é comum em terrenos rurais.
6. **Múltiplos casos numa mensagem:** gerar 1 variant por caso, todos numa única chamada de `message_compose_v1`.
7. **Lucas pede "sem aluguel" ou "pede pra ele confirmar":** ajustar conforme — esses padrões já viraram preferência durante o uso.

## Pós-envio

Depois de gerar o e-mail, listar (curto) os campos extraídos vs. os que foram omitidos, para Lucas validar antes de copiar. Não fazer postâmbulo longo.
