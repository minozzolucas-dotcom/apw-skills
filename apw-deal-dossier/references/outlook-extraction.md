# Outlook Extraction — achar e ler a thread do caso

Leia no Passo 2 do workflow. O objetivo: a partir de um código L, encontrar a conversa de email do caso e reconstruí-la em ordem cronológica.

## Antes de começar

Aba do Outlook precisa estar aberta e logada no tenant APW. Atalho direto:
`https://outlook.cloud.microsoft/mail/?realm=apwbrasil.com.br&login_hint=LMinozzo@apwbrasil.com.br`

Domínio sensível → **sem screenshot**. Use `javascript_tool`, `get_page_text`, `read_page`. Ver `apw-chrome-agent-lean-compliance`.

## Caminho B — thread já colada/encaminhada

Se o Lucas já colou ou encaminhou a thread (caso comum — foi como o pedido da Marcelina chegou), **não busque nada no Outlook**. Você já tem o material. Extraia o código L do assunto e vá direto para "Parsear a thread encadeada" abaixo.

Os assuntos de email da APW carregam o código L num padrão reconhecível:
```
L1256097_NP_ACF203515_MARILENE VERDUGO_SBA
BR62831 - Nova Aquisição APW - L1256097_NP_ACF203515_MARILENE VERDUGO_SBA
```
Regex para extrair: `/L\d{6,8}/` — pega o primeiro `L` seguido de 6-8 dígitos.

## Caminho A — buscar a thread pelo código L

### 1. Buscar no Outlook Web

Navegue para a URL de busca ou use a caixa de busca da interface. A busca por texto do Outlook Web aceita o código L direto:

```
https://outlook.cloud.microsoft/mail/search/{TERMO}
```

Ordem de tentativa dos termos de busca:

1. **Código L** (`L1256097`) — o L aparece no assunto da maioria dos emails APW. Resolve a maioria dos casos.
2. **Fallback: identificadores do site** — se o L não retornar nada, busque pelo ID do site (`BR62831`), nome do proprietário/contraparte (`MARILENE VERDUGO`, `Marilene Verdugo`), ou cidade do site (`Sorocaba`). Esses vêm do `name` da opp que você puxou no Passo 1 (CRM).
3. **Fallback do fallback** — número de incidente da torreira, se aparecer (`497582`, `Incident# 497582`).

### 2. Ler os resultados da busca

Extraia a lista de threads que voltou via `read_page` (pega a árvore com os `ref`) ou `javascript_tool` lendo os itens da lista:

```js
[...document.querySelectorAll('[role="option"], div[aria-label*="message"]')]
  .map(el => el.innerText.replace(/\s+/g,' ').trim())
  .filter(t => t.length > 10)
  .slice(0, 20)
```

Identifique a thread certa pelo assunto que contém o código L. Se houver várias threads do mesmo L (caso comum — re-encaminhamentos, "ENC:", "RES:"), pegue **a mais recente** — ela geralmente contém todas as anteriores citadas embaixo.

### 3. Abrir a thread e extrair o corpo

Clique no item (via `ref` do `read_page`) e use `get_page_text` para pegar o conteúdo completo da conversa. `get_page_text` resolve em uma chamada e já traz a thread encadeada inteira.

## Parsear a thread encadeada

Threads corporativas vêm **encadeadas e fora de ordem**: a mensagem mais recente no topo, e as anteriores citadas abaixo, cada uma com seu cabeçalho (`De:`/`From:`, `Enviada em:`/`Sent:`, `Para:`/`To:`, `Assunto:`/`Subject:`).

### Reordenar cronologicamente

Cada bloco de mensagem começa num cabeçalho. Identifique os blocos pelos marcadores:
- `De:` / `From:` seguido de nome/email
- `Enviada em:` / `Sent:` seguido de data
- `Assunto:` / `Subject:`

Separe a thread nesses pontos, parseie a data de cada bloco, e **ordene do mais antigo para o mais recente**. A negociação só faz sentido na ordem em que aconteceu — quem pediu o quê, quem respondeu, o que mudou.

Datas vêm em formatos mistos (`terça-feira, 19 de maio de 2026 14:36` / `Tuesday, May 5, 2026 11:07 AM`). Normalize ambos.

### O que extrair de cada mensagem

Para cada mensagem na ordem cronológica:

| Campo | O que pegar |
|---|---|
| Data | quando foi enviada |
| Remetente | nome + organização (pelo domínio do email: `@apwbrasil.com.br` = APW, `@sbasite.com` = SBA, `@apwip.com` = APW US/PM) |
| Destinatários | quem estava no "Para" — sinaliza quem é responsável |
| Fato novo | a informação que esta mensagem introduz que não estava antes |
| Pedido/decisão | o que esta mensagem pede ou decide |

### Ruído a ignorar

- Disclaimers de confidencialidade ("The information contained in this communication...") — repetidos em todo email, sem valor.
- Avisos do Mimecast ("This email has been scanned for viruses...").
- Assinaturas longas repetidas (telefone, CNPJ, endereço) — pegue o nome e a organização uma vez, descarte o resto.
- Banners "CAUTION: This email originated from outside..." — ruído.

## O que a thread alimenta no dossiê

A thread é a fonte principal das seções **2 (o que foi negociado)**, **3 (divergências)**, **4 (quem é quem)** e **5 (linha do tempo)** do template. É na prosa dos emails que aparece o que o CRM não tem: o valor exato acordado, a condição que uma das partes alega, o pedido que está pendente.

## Compliance

- Sem screenshot do Outlook.
- Não persista o corpo dos emails em arquivo. O parsing é em memória.
- Não reencaminhe, responda ou mova nenhum email — esta skill **lê**, não age na caixa. Se o Lucas quiser responder a Marcelina, isso é uma ação separada que ele aprova explicitamente (e aí use `message_compose_v1` ou rascunho, nunca envio direto).
