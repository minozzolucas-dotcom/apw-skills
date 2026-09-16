---
name: apw-telecom-intel-daily
description: Use SEMPRE que o Lucas pedir "radar APW", "briefing telecom", "rodar radar telecom", "panorama telecom", "inteligencia de contrapartes", "dashboard telecom", "agenda de releases", "release trimestral telecom", ou variacao pedindo panorama setor telecom BR com foco em torreiras (ATC, SBA, IHS, Highline), MNOs (Vivo, Claro, TIM, Oi), ISPs (V.tal, Alloha, Alares, Desktop, Unifique, Brisanet, Sumicity), lease aggregators (TIP, Unison, Radius, MD7, Landmark, Diamond, APW Brasil) e regulacao Anatel. Entrega email HTML dark editorial em /mnt/user-data/outputs/ com: noticias do dia + agenda releases proximos 30 dias + painel contrapartes (receita, EBITDA, alavancagem, rating) + cruzamento noticia x financeiro pra exposicao APW. Use tambem quando colar bloco bruto de noticias pedindo estruturar no formato APW. NAO use para perguntas pontuais sobre uma unica empresa nem analise contratual (use apw-telecom-real-estate-counsel).
---

# APW Telecom Intel — Radar Diario de Contrapartes

## Overview

Skill que entrega um **email HTML executivo dark editorial** salvo em `/mnt/user-data/outputs/radar-apw-YYYY-MM-DD.html`, integrando tres camadas de inteligencia:

1. **Noticias do dia** — torreiras, MNOs, ISPs, lease aggregators, regulacao
2. **Calendario financeiro** — releases dos proximos 30 dias + destaque do que saiu hoje
3. **Painel de contrapartes** — KPIs financeiros (receita, EBITDA, alavancagem, rating) de todas as operadoras e ISPs relevantes pro pipeline APW

**Filosofia:** APW compra ground leases (terreno sob torres) e direitos de superficie em rooftops. A saude financeira de quem paga aluguel nos sites importa tanto quanto a noticia do dia. Skill cruza as duas dimensoes pra sinalizar risco de churn ou janela de aquisicao.

## Quando NAO usar

- Pergunta pontual sobre uma empresa especifica → usar `parallel-web-search` direto
- Tese aprofundada em uma unica contraparte → usar `parallel-deep-research`
- Analise de clausula contratual / minuta → usar `apw-telecom-real-estate-counsel`
- Consulta CRM Dynamics → usar `apw-dynamics-copilot`

## Anti-padroes (NUNCA fazer)

- NUNCA copiar trecho literal de materia com 15+ palavras. SEMPRE parafrasear.
- NUNCA inventar numero financeiro. Se nao acessou release, marcar com "—" e nota.
- NUNCA tratar empresa em RJ como saudavel (Oi sempre tem tag 🔴 RJ).
- NUNCA omitir fonte de dado financeiro. Sempre citar (RI/CVM/B3/imprensa).
- NUNCA usar emoji no corpo de texto, so nas tags coloridas 🔴🟡🟢🟠.
- NUNCA recomendar compra/venda de imovel ou contraparte. Analise, Lucas decide.

## Universo de cobertura

### Listadas B3 (release publico + ITR CVM)
| Empresa | Ticker | RI |
|---|---|---|
| Vivo / Telefonica Brasil | VIVT3 | https://ri.telefonica.com.br/ |
| TIM Brasil | TIMS3 | https://ri.tim.com.br/ |
| Brisanet | BRIT3 | https://ri.brisanet.com.br/ |
| Desktop | DESK3 | https://ri.desktop.com.br/ |
| Unifique | FIQE3 | https://ri.unifique.com.br/ |
| Oi (RJ) | OIBR3 | https://www.oi.com.br/ri/ |

### Listadas exterior com peso Brasil
| Empresa | Ticker | RI |
|---|---|---|
| American Tower | AMT (NYSE) | https://www.americantower.com/investor-relations |
| SBA Communications | SBAC (NASDAQ) | https://www.sbasite.com/investor-relations |
| IHS Holding | IHS (NYSE) | https://www.ihstowers.com/investors |
| America Movil (Claro BR) | AMX (NYSE) | https://www.americamovil.com/ |

### Capital fechado com debentures (CVM + Debentures.com.br + Anbima)
- V.tal — emissor grande, varias series
- Alloha Fibra / Giga+
- Alares
- Sumicity
- Highline do Brasil (torreira)
- IHS Brasil (separado do holding US)

### Lease aggregators (concorrentes APW — sem release publico)
APW Brasil (Radius), TIP, Unison, MD7, Landmark Dividend, Diamond Communications

## Protocolo de execucao

### FASE 1 — Salvar baseline (so na primeira rodada ou se nao existe)

Verificar se existe `/home/claude/apw-baseline.json` com snapshot financeiro mais recente das contrapartes. Se nao existe ou tem >90 dias, tentar rodar `apw_baseline_builder.py`.

```bash
ls /home/claude/apw-baseline.json 2>/dev/null || ls /home/claude/apw_baseline_builder.py 2>/dev/null
```

> **Se o builder NAO existir** (skill ainda nao tem o script): NAO travar. Montar o baseline na hora, buscando os KPIs de cada contraparte via parallel-web-search/RI durante a Fase 3.3 e gravando o `apw-baseline.json` direto. A skill nunca deve abortar por falta de arquivo auxiliar.

### FASE 2 — Coleta de noticias (paralelo)

Usar `parallel-web-search` com queries direcionadas. Janela: ultimas 24h (ou 72h se segunda-feira).

> **REGRA DE OURO DA RECENCIA (nao negociavel).** O ano sozinho ("2026") NAO filtra data de publicacao — eh so mais um termo, e o motor devolve o resultado mais linkado do ano (quase sempre velho). Por isso:
> 1. **Ancorar pelo MES.** Toda query leva `{MES_ATUAL} {MES_ANTERIOR} {ANO}` calculados a partir da data real de hoje (ex.: hoje jun/2026 → "maio junho 2026"). NUNCA deixar so o ano.
> 2. **Uma query por player/tema.** Proibido OR gigante (`A OR B OR C OR D`) — degrada recencia e devolve generico. Players separados.
> 3. **Verificar a data de CADA resultado depois de buscar.** Descartar (ou marcar com nota) qualquer materia com data de publicacao > 30 dias. Se o pedido for "do dia", manter so <= 7 dias. Validar a recencia pelo proprio slug da URL quando possivel — teletime e convergencia carimbam `/DD/MM/AAAA/` no link.
> 4. Se a melhor materia encontrada for antiga, **dizer isso explicitamente** no output ("nada novo nesse player; ultimo fato relevante eh de [data]") em vez de apresentar velho como novo.

**Queries obrigatorias** (substituir `{mes}` pela janela mes atual + anterior; uma busca por linha, separadas):
```
teletime torre site operadora {mes} {ano}
convergencia digital Anatel telecom {mes} {ano}
mobiletime telecom rede {mes} {ano}
Oi recuperacao judicial intervencao credor {mes} {ano}
American Tower Brasil {mes} {ano}
SBA Communications Brasil torre {mes} {ano}
IHS Brasil torre site {mes} {ano}
Highline Brasil torre {mes} {ano}
V.tal debenture data center fibra {mes} {ano}
Vivo Telefonica rede site torre {mes} {ano}
TIM rede torre lease {mes} {ano}
Claro America Movil Brasil {mes} {ano}
ground lease rooftop torre celular Brasil {mes} {ano}
APWireless Radius TIP Unison lease aggregator Brasil {mes} {ano}
Anatel espectro leilao 5G consulta publica {mes} {ano}
```

**Fontes prioritarias (verificar via parallel-web-search):**
- Tier 1: teletime.com.br, convergenciadigital.com.br, mobiletime.com.br, teleco.com.br
- Tier 2: gov.br/anatel/pt-br/assuntos/noticias
- Tier 3: canaltech.com.br/telecom, tecnoblog.net/telecom, valor.globo.com/empresas
- Tier 4: pipeline, brazil journal, neofeed
- Tier 5 (so segunda): insidetowers.com, rcrwireless.com/tag/towers

### FASE 3 — Releases e agenda

**3.1 — Checar se algum release saiu nas ultimas 24h:**

Para cada empresa do universo listado, query especifica (ancorar pelo mes, nunca so o ano):
```
"[empresa]" release ITR resultado trimestre {mes} {ano}
"[empresa]" investor relations earnings {mes} {ano}
```

Se encontrou release publicado hoje → extrair:
- Periodo de referencia (1T26, 2T26, etc)
- Receita liquida, EBITDA, margem EBITDA, lucro liquido
- Divida liquida, alavancagem (Div Liq/EBITDA)
- Capex
- KPIs operacionais telecom: ARPU movel, ARPU FTTH, base de clientes, churn, HPs
- Cobertura de juros
- Variacao YoY de cada metrica
- Frase do guidance/outlook

Release fresco = **card destaque 🟠 RELEASE no Top 3**.

**3.2 — Agenda dos proximos 30 dias:**

Para cada empresa, estimar proxima data de release usando padrao historico:
- Vivo/TIM: ~30-45 dias apos fim do trimestre (final fev, mai, ago, nov)
- Brisanet/Desktop/Unifique: ~45 dias (mid mar, mai, ago, nov)
- AMT/SBAC/IHS: calendario US (final jan/abr/jul/out)
- V.tal/Alloha/Alares/Highline: ITRs CVM ~45 dias

Buscar confirmacoes via "[empresa] earnings call date 2026" ou agenda de eventos no RI.

**3.3 — Atualizar painel de contrapartes:**

Para cada empresa, garantir snapshot atualizado em `/home/claude/apw-baseline.json`:
```json
{
  "empresa": "TIM Brasil",
  "ticker": "TIMS3",
  "ultimo_periodo": "3T25",
  "data_release": "2025-11-05",
  "receita_liq_mi": 6420,
  "ebitda_mi": 3010,
  "margem_ebitda_pct": 46.9,
  "divida_liq_mi": 8920,
  "alavancagem": 2.8,
  "capex_mi": 1180,
  "arpu_mobile": 32.4,
  "churn_mobile_pct": 2.1,
  "base_mobile_mi": 60.2,
  "rating": "AAA(bra)/Fitch",
  "status": "🟢",
  "fonte": "https://ri.tim.com.br/...",
  "ultima_atualizacao": "2025-11-05"
}
```

Status semaforo:
- 🟢 SAUDAVEL — alavancagem <3x, margem estavel/crescendo, IG
- 🟡 ATENCAO — alavancagem 3-5x, margem em queda, BB
- 🔴 RISCO — alavancagem >5x, EBITDA caindo, B-/distress/RJ

### FASE 4 — Cruzamentos criticos

Antes de gerar HTML, cruzar noticias x painel:

- 🔴🔴 **DUPLO RISCO**: noticia negativa + contraparte ja em risco → revisar exposicao
- 🟢🟢 **DUPLA OPORTUNIDADE**: noticia de expansao + contraparte saudavel → janela buyout
- ⚠️ **DIVERGENCIA**: release diz X, regulador/mercado diz Y → monitorar

Maximo 3 cruzamentos. Se nao houver, omitir secao.

### FASE 5 — Gerar HTML

Se existir `template.html` na pasta da skill, usar como base e substituir placeholders. **Se NAO existir**, gerar o HTML inline do zero seguindo a estrutura e a paleta dark editorial definidas abaixo (secoes "Estrutura do email HTML" / "Paleta"). A skill nunca deve abortar por falta do template — ele eh conveniencia, nao dependencia.

Salvar em `/mnt/user-data/outputs/radar-apw-YYYY-MM-DD.html`.

Usar `present_files` no final.

## Estrutura do email HTML

### Restricoes tecnicas (CRITICAS — eh email, nao webpage)

- HTML self-contained, sem CDN, sem JS, sem fontes externas
- TODO CSS INLINE em cada elemento (`style="..."`)
- Layout em `<table>` com `cellpadding`, `cellspacing="0"`, `border="0"`
- Largura maxima 720px, centralizado
- Fontes: `-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif`
- Sem emojis no corpo, so em tags coloridas 🔴🟡🟢🟠⚠️
- Sem imagens (cai em spam)
- Links com `target="_blank"` e style inline

### Paleta (dark editorial)

| Token | Cor |
|---|---|
| Background body | `#0d0d0f` |
| Card | `#161618` |
| Card destaque release | `#1f1612` (tom laranja sutil) |
| Borda | `#2a2a2e` |
| Texto principal | `#e8e8ea` |
| Texto secundario | `#9a9a9f` |
| Accent laranja | `#ff6b35` |
| Verde (oportunidade/saudavel) | `#4ade80` |
| Amarelo (monitorar/atencao) | `#fbbf24` |
| Vermelho (risco) | `#ef4444` |
| Laranja release | `#fb923c` |

### Ordem das secoes

1. **Header** — "RADAR APW · TELECOM BR · INTELIGENCIA DE CONTRAPARTES" + data por extenso + subtitulo
2. **Resumo executivo** — 1 paragrafo, 3-4 linhas, tom de dono
3. **Agenda dos proximos 30 dias** — tabela compacta ordenada por data, highlight em laranja se nos proximos 7 dias
4. **KPIs do dia** — 3 cards: Renegociacoes & Contratos | Churn/Desligamento sites | M&A & Densificacao
5. **Cruzamentos criticos** (se houver) — maximo 3 cards horizontais
6. **TOP 3 do dia** — cards verticais. Release fresco vira card 🟠 RELEASE com mini-tabela de KPIs
7. **Painel de contrapartes** — tabela completa ordenada por status (🔴 primeiro)
8. **Todas as materias do dia** — tabela: Data | Players | Headline | Leitura APW | Link
9. **Sinais estruturais** — 2 paragrafos costurando movimentos
10. **Rodape** — disclaimer + data ultima atualizacao do painel

### Regras editoriais (nao negociaveis)

- NUNCA copiar trechos literais com 15+ palavras. Parafrasear sempre.
- Portugues brasileiro casual-profissional. "O jogo", "trava churn", "mexe no valuation", "de dono".
- "Leitura APW" SEMPRE conecta a ground lease/rooftop/buyout/churn/exposicao de contraparte. Nunca resumo generico.
- Dados financeiros: sempre citar fonte e periodo de referencia.
- Fonte bloqueada (paywall, anti-bot) → marcar com "—" e nota de rodape.
- Empresa em RJ (Oi) → sempre tag 🔴 RJ + ultima atualizacao do processo.

## Entrega final

1. Salvar HTML em `/mnt/user-data/outputs/radar-apw-YYYY-MM-DD.html`
2. Atualizar `/home/claude/apw-baseline.json` se houve release novo
3. Chamar `present_files` com o HTML
4. No chat, resumir:
   - Fontes visitadas: X
   - Releases capturados hoje: Y (lista empresas)
   - Empresas no painel: Z
   - Cruzamentos criticos: N
   - Bloqueios: lista (se houver)

## Arquivos da skill

- `SKILL.md` — este arquivo (obrigatorio)
- `query_pack.md` — queries pre-formatadas com ancora de mes movel (incluido)

**Auxiliares OPCIONAIS** (a skill funciona sem eles — degrada graciosamente):
- `template.html` — template HTML base. Se faltar, gerar HTML inline pela paleta acima.
- `apw_baseline_builder.py` — script que monta `apw-baseline.json`. Se faltar, montar baseline on-the-fly na Fase 3.3.
- `universe.json` — lista canonica de empresas/tickers/RI. Se faltar, usar as tabelas da secao "Universo de cobertura" acima.
