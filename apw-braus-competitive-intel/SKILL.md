---
name: apw-braus-competitive-intel
description: Radar semanal de inteligencia competitiva de jiu-jitsu apparel pra Braus / Alliance Fight. Monitora 20 concorrentes globais e nacionais (Shoyoroll, Kingz, Hyperfly, Origin, Sanabul, Tatami, Atama, Keiko, Vulkan, Koral, Fighters Market BR, Naja, Torah e outros) em 5 fontes — social, e-commerce, imprensa BJJ, atletas, eventos (IBJJF/ADCC/UAEJJF/AJP/CBJJ). Orquestra parallel-deep-research, agent-browser e competitive-ads-extractor. Entrega markdown deep + dashboard HTML dark em /mnt/user-data/outputs/. Use SEMPRE que o Lucas pedir "radar Braus", "briefing competitivo", "rodar inteligencia Braus", "monitorar concorrentes jiu-jitsu", "competitive intel", "o que os concorrentes fizeram essa semana", "relatorio semanal Braus", "espionar concorrencia kimono", ou colar noticias/posts de concorrentes pedindo estruturar. NAO use para analise fundacional de mercado (relatorio ja existe), marca Jitsu isolada, nem consulta pontual sobre um unico concorrente (use parallel-web-search).
---

# Braus Competitive Intel — Radar Semanal de Concorrentes

## Overview

Skill que entrega um **briefing executivo semanal de inteligencia competitiva** do mercado global de jiu-jitsu apparel, sob a otica de um Diretor de Inteligencia Competitiva e Produto PhD agindo como CEO + gerente de produto senior da Braus / Alliance Fight.

Entrega dupla, salva em `/mnt/user-data/outputs/`:
1. **Relatorio markdown deep** — `braus-intel-YYYY-MM-DD.md` (5-8 paginas, ~3500-5500 palavras)
2. **Dashboard HTML dark interativo** — `braus-intel-YYYY-MM-DD.html`

**Filosofia:** A Braus opera num mercado fragmentado e veloz. Nenhum concorrente tem >5% de share global, mas movimentos individuais (um drop da Shoyoroll, Kingz abrindo loja em SP, Sanabul cruzando pra Amazon BR) mudam o jogo regional. A skill captura o sinal cru, traduz em leitura estrategica, e devolve 3 recomendacoes acionaveis com prazo. Cadencia ideal: 1x por semana, sexta-feira.

## Contexto da Braus (sempre carregar antes de analisar)

- Marca brasileira global de jiu-jitsu apparel. Fabrica propria no Paquistao.
- Exclusividade ADCC nas Americas (produz itens oficiais + opera eventos).
- Parceria estrategica com a academia Alliance (produz todo o estoque + logistica).
- Operacao em 4 mercados: Brasil, EUA (us.brausfight.com), Europa (eu.brausfight.com), Australia/internacional (brausfight.com).
- Faturamento ~R$ 4,8M/ano. **Concentracao critica: Alliance = 62,5% da receita.**
- Custo gi ~R$ 250 no porto de Santos. B2C BR ~R$ 750, B2B ~R$ 600. Margem liquida ~15%.
- Pricing por regiao (referencia maio 2026): EUA Pro Light USD 120 (mais barato), Europa Pro Light EUR 150 (mais caro), Australia USD 146.
- Marca-filha em lancamento: **Jitsu** (entry-level, kimono preto unico, R$<500, standalone, DTC + marketplaces).

## Quando NAO usar

- Analise fundacional de mercado completa (one-shot) → ja existe o relatorio `relatorio_braus_jitsu_executivo.md`
- Pergunta pontual sobre UM concorrente → usar `parallel-web-search` direto
- Tese aprofundada em uma unica marca → usar `parallel-deep-research` direto
- Monitoramento isolado da marca Jitsu → criar skill dedicada quando Jitsu lancar
- Pricing global Braus → consultar anexo `anexo_pricing_global_braus.md`

## Anti-padroes (NUNCA fazer)

- NUNCA copiar trecho literal de materia/post com 15+ palavras. SEMPRE parafrasear.
- NUNCA inventar lancamento, preco, contratacao de atleta ou patrocinio. Sem fonte = nao entra. Se sinal fraco, marcar `[uma fonte]` ou `[nao confirmado]`.
- NUNCA incluir sinal fora da janela de 7 dias. Data-stamp tudo. Noticia velha = descarta.
- NUNCA repetir sinal que ja saiu no relatorio da semana anterior — so novidade ou evolucao.
- NUNCA tratar rumor como fato. Rumor de r/bjj ≠ anuncio oficial de Instagram.
- NUNCA omitir a fonte (URL) de um sinal.
- NUNCA recomendar algo generico ("investir em digital"). Toda recomendacao amarra a um sinal especifico da semana.
- NUNCA poluir o relatorio com concorrente que ficou quieto — silencio se menciona so no bloco de padroes.
- NUNCA gerar imagem com IA para o relatorio. Dashboard usa CSS/SVG apenas.
- NUNCA recomendar compra/venda. Skill analisa, Lucas decide.

## Universo de cobertura — 20 concorrentes

### Globais Tier 1 (alta prioridade, deep)
| Marca | Site | Instagram | Por que importa |
|---|---|---|---|
| Shoyoroll | shoyoroll.com | @shoyoroll | Lider hype/premium, Batches numerados |
| Kingz | kingzkimonos.com | @kingz | Concorrente direto Braus, loja fisica SP |
| Hyperfly | hyperfly.com | @hyperfly | Premium lightweight, atletas top |
| Origin | originmaine.com | @originmaine | Premium USA-made |
| Sanabul | sanabulsports.com | @sanabul | Domina Amazon entry US, risco BR |

### Globais Tier 2 (media prioridade)
Tatami Fightwear (@tatamifightwear), Progress Jiu-Jitsu (@progressjj), Albino & Preto (@albinoandpreto), Manto (@mantofightwear), Scramble (@scramble_brand).

### Nacionais Tier 1 (concorrentes Braus)
| Marca | Site | Instagram |
|---|---|---|
| Atama | atama.com.br | @atamabrasil |
| Keiko Sports | keikosports.com.br | @keikoraca |
| Vulkan | vulkan.com.br | @vulkanstore |
| Koral | koral.com.br | @koralfightcompany |
| Fighters Market BR | fightersmarket.com.br | @fightersmarket |

### Nacionais Tier entry (concorrentes Jitsu — monitorar quando Jitsu lancar)
Naja (@najafight), Torah (@torahkimonos), Shiroi (@shiroioficial), MKS Combat (@mks_combat), Pretorian (@pretorianoficial).

## As 5 fontes obrigatorias

Cada concorrente ativo precisa de varredura nas 5 fontes:

- **🅐 Redes sociais** — Instagram, TikTok, YouTube: lancamentos, campanhas, viralizacao, mudanca de identidade visual, ativacao com criador.
- **🅑 Sites/e-commerce** — novos SKUs, pricing, promocoes, sumico de SKU, bundle novo, mudanca de copy.
- **🅒 Imprensa/comunidade** — BJJ Heroes, Jits Magazine, Grappling Insider, Tatame, FloGrappling, r/bjj, r/bjj_brasil.
- **🅓 Atletas** — contratacoes, saidas, resultados em eventos, momentos de midia.
- **🅔 Eventos/patrocinios** — IBJJF, ADCC, UAEJJF, AJP, CBJJ: patrocinios anunciados, sponsors oficiais, calendario.

## Ferramentas que a skill orquestra

A skill NAO faz tudo com web_search simples. Ela escala para ferramentas dedicadas:

1. **`parallel-deep-research`** — para teses profundas sobre um concorrente que teve movimento grande na semana (ex.: "Kingz abriu loja SP — investigar estrategia de varejo fisico deles"). Usar quando um sinal merece >5 buscas de profundidade.

2. **`agent-browser`** — para raspar o que web_search nao alcanca bem:
   - Perfis de Instagram/TikTok (posts recentes, engagement aproximado)
   - Paginas de colecao de e-commerce (detectar SKU novo / SKU sumido comparando com semana anterior)
   - Catalogos de marketplace (Mercado Livre, Amazon BR) para precos de concorrentes nacionais
   - SEMPRE respeitar `apw-chrome-agent-lean-compliance`: read_page → get_page_text → javascript_tool antes de screenshot. Sites de concorrentes sao publicos, screenshot permitido se necessario.

3. **`competitive-ads-extractor`** — para capturar os anuncios pagos ativos dos concorrentes (Meta Ad Library, etc.). Revela: que produto estao empurrando, que mensagem/dor exploram, que criativo. Rodar para os Tier 1 globais + Fighters Market BR no minimo.

Ver `references/workflow.md` para a ordem exata de chamada.

## Workflow resumido

1. **Carregar contexto** — ler este SKILL.md + (se existir) o relatorio da semana anterior em `/mnt/user-data/outputs/` para evitar repeticao.
2. **Pegar data atual** — definir janela de 7 dias.
3. **Planejar buscas** — listar 20-25 buscas em bullets (ver distribuicao em `references/workflow.md`).
4. **Coletar** — web_search para sinais amplos; `agent-browser` para sites/social; `competitive-ads-extractor` para ads; `parallel-deep-research` para 1-2 teses profundas da semana.
5. **Triangular** — sinal forte = 2+ fontes; sinal fraco = marcar.
6. **Escrever relatorio markdown** — 8 secoes obrigatorias (ver `references/report-structure.md`).
7. **Gerar dashboard HTML** — usar `assets/dashboard-template.html` como base.
8. **Salvar** ambos em `/mnt/user-data/outputs/` com data no nome.
9. **Verificar checklist** de qualidade (ver `references/workflow.md`).
10. **Entregar** via present_files + resumo curto do TL;DR no chat.

## Arquivos da skill

- `SKILL.md` — este arquivo (overview + regras)
- `references/workflow.md` — passo a passo detalhado, distribuicao de buscas, checklist
- `references/report-structure.md` — estrutura das 8 secoes do relatorio markdown
- `assets/dashboard-template.html` — template HTML dark do dashboard

## Melhoria continua

A cada 4 execucoes, revisar com o Lucas: lista de concorrentes ainda valida? Fontes capturando o que importa? Recomendacoes passadas se confirmaram? Ajustar este SKILL.md conforme aprendizado.
