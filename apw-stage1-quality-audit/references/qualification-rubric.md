# Rubrica de Qualificação Stage 1 — léxico e regras

Esta é a lógica que `build_audit.py score` implementa e que você (modelo) aplica na revisão
forense. A regex é o **primeiro filtro**; a leitura humana do texto é a palavra final. Leia
isto inteiro antes de sobrescrever qualquer tier.

## Heurístico de atividade substantiva (base)

Herdado do `apw-reporte-crm-diario`. Uma atividade conta como **substantiva** se:
`len(desc) ≥ 180` **OU** (`len(desc) ≥ 140` **e** ≥2 sinais abaixo).

Sinais: valor/número (R$, milhares, %), contraparte (síndico, proprietário, administradora,
condomínio, operadora, torre, locador, advogado), próximo passo (retornar, agendar, enviar,
aguardar, follow, reunião, visita, proposta, marcar, ligar), objeção/info (objeção, recusa,
negociação, contraproposta, exigência, condição, "quer", "pediu", "preocupa").

Atividades de workflow com descrição automática (vazias, "opportunity created/updated",
"stage changed", "reminder:", "notificação automática") são **descartadas** — não contam nem
a favor nem contra. Uma opp cuja única "atividade" é automática = **zero atividade real**.

## Pilar 1 — Decisor real contatado

Pergunta: o diretor falou com **quem decide** sobre o terreno/condomínio?

**Sinais positivos** (papel decisório nomeado): `síndic`, `proprietári`, `dono d`, `dona d`,
`decisor`, `respons[áa]vel pelo`, `procurador`, `s[óo]cio`, `administrador(a) <nome>`,
`gestor predial`, `presidente do conselho`, `quem decide`, `é o dono`, `titular da matrícula`,
`herdeir`, `inventariante`, `representante legal`. Reforço quando confirma autoridade:
`é quem decide`, `responsável pela negociação`, `vai levar pra assembleia` (síndico com poder
de pauta).

**Sinais negativos** (tocou em quem NÃO decide, ou ninguém): `porteir`, `zelador`, `recep[çc]`,
`secretári`, `atendente`, `funcionári` (genérico), `falei com o pessoal`, `o pessoal do
pr[éedio`, `deixei recado na portaria`, `ningu[ée]m sabia informar`, `não soube dizer quem`.

**Negativo forte** = nenhuma contraparte nomeada em nenhuma atividade substantiva.

Pilar 1 **cumprido** se há ≥1 sinal positivo de decisor nomeado **e** nenhum indício de que
só se falou com não-decisor. Se só há sinal negativo → não cumprido. Se há positivo E
negativo, o positivo prevalece (tocou no decisor em algum momento) — mas registre a nuance.

## Pilar 2 — Pitch inicial completo

Pergunta: apresentou o modelo APW de forma completa e capturou reação?

**Sinais positivos** (apresentação do modelo): `apresentei`, `expliquei o modelo`, `como
funciona`, `cess[ãa]o de cr[ée]dito`, `cess[ãa]o de direitos credit[óo]rios`, `DRS`,
`direito real de superf[íi]cie`, `antecipa[çc][ãa]o de aluguel`, `compra do fluxo`,
`mostrei a proposta`, `enviei a minuta`, `expliquei a vantagem`, `pitch`, `passei o material`.

**Sinais de reação/engajamento capturado** (vale como pitch que pegou): `achou interessante`,
`vai analisar`, `pediu a minuta`, `pediu pra ver o contrato`, `levou pra assembleia`,
`ficou de retornar com`, `tem dúvida sobre`, `questionou`, `objeção`, `contraproposta`,
`pediu mais informações sobre`, `quer entender`.

**Sinais negativos** (atividade sem pitch — só logging): `liguei, n[ãa]o atendeu`,
`vou retornar`, `deixei recado`, `mandei whats` (sem conteúdo), `sem retorno`, `aguardando`,
`tentando contato`, `n[úu]mero errado`, `caixa postal`.

Pilar 2 **cumprido** se há ≥1 sinal de apresentação do modelo **ou** ≥1 sinal de reação
substantiva capturada (uma objeção registrada prova que houve pitch). Só sinais negativos /
tentativas de contato → não cumprido.

## Pilar 3 — Contato salvo

Pergunta: o contato do decisor foi registrado?

**Sinais positivos:** telefone (`\b\d{2}\s?9?\d{4}[-\s]?\d{4}\b`, `(\d{2})`, `tel:`,
`whats(app)?:?\s*\d`), e-mail (`[\w.+-]+@[\w-]+\.[\w.-]+`), `contato:`, `salvei o contato`,
`cadastrei no CRM`, `dados do síndico:`, `telefone do propriet[áa]rio`.

Pilar 3 **cumprido** se há ≥1 telefone OU e-mail OU marcador explícito de contato salvo em
qualquer atividade. (Enriquecimento opcional: campos estruturados de contato na opp — se a
coleta os trouxer, contam também.)

## Atribuição de tier

Conte os pilares cumpridos (0–3) sobre as atividades **substantivas** da opp:

| Tier | Regra |
|---|---|
| 🟢 **Sólida** | 3 pilares cumpridos. |
| 🟡 **Rasa** | 1 ou 2 pilares. Qualificação real mas incompleta — coachable. |
| 🔴 **Suspeita** | 0 pilares cumpridos **E** nenhuma atividade substantiva (só fina/automática). Stage 1 movido sem lastro visível. |

**Reforços de Suspeita** (elevam confiança da flag, registre no `tier_reason`):
- Segue em Stage 1 e **sem atividade substantiva há ≥30 dias** após a entrada em S1.
- **Surrender rápido** (≤14 dias do S1) com qualificação 0–1 pilar → padrão de "qualifiquei
  pra pontuar e larguei".
- Cohort do diretor com vários 🔴 no mesmo dia (lote de S1 movido em bloco sem atividade).

**Guardrails anti-falso-positivo** (NÃO flagueie 🔴 quando):
- A opp entrou em S1 **há poucos dias** — não houve tempo de logar profundidade. Marque
  `🟡 Rasa (recente)` e não a conte como suspeita.
- Há atividade substantiva clara mas a regex não pegou o léxico (sinônimo, abreviação, ASR).
  Promova na revisão forense, citando a frase.
- Property type / contexto explica registro curto (ex.: deal herdado, reativação). Anote.

Regra de ouro: **registro fino pode ser trabalho real mal documentado.** A flag diz
"verificar", não "condenar".

## Rollup por diretor e regra de outlier

Para cada diretor (owner efetivo do S1), agregue o cohort dele:
`n_cohort`, `n_solida`, `n_rasa`, `n_suspeita`, `pct_suspeita = n_suspeita / n_cohort`,
`mediana_atividades_substantivas_por_opp`.

**Flag de integridade** (atenção, não condenação):
- `pct_suspeita` do diretor **acima da mediana do time + 15 pontos percentuais** OU
  `pct_suspeita ≥ 30%` em valor absoluto, **com `n_cohort ≥ 5`** (volume mínimo pra
  confiança). Abaixo de 5, sinalize `amostra pequena — inconclusivo`.
- Padrão de **lote** (vários S1 movidos no mesmo dia com 0 pilar) é flag mesmo com pct baixo.

Apresente o diretor com maior pct_suspeita no topo do scorecard. **Sempre** com a contagem
absoluta ao lado do percentual (3 de 4 ≠ 30 de 100). Outlier com cohort pequeno = oliva
(atenção/incerto), não vermelho.

## Saída do `score` (audit.json)

```json
{
  "year": 2026,
  "generated": "2026-06-24",
  "_meta": { "columns_discovered": { "...": "..." }, "host": "apwireless.crm.dynamics.com" },
  "cohort": {
    "total": 0, "evolved_s3": 0, "still_s1": 0, "surrendered": 0, "fast_surrender": 0,
    "surrender_reasons": { "<motivo>": 0 },
    "property_type": { "<tipo>": 0 },
    "owner": { "person": 0, "pool": 0, "by_director": { "<nome>": 0 } }
  },
  "directors": [
    { "name": "...", "n_cohort": 0, "n_solida": 0, "n_rasa": 0, "n_suspeita": 0,
      "pct_suspeita": 0.0, "median_subst": 0.0, "flag": "none|atencao|inconclusivo" }
  ],
  "opps": [
    { "L": "L12345", "owner": "...", "is_pool": false, "status": "still_s1|evolved|surrendered",
      "surrender_reason": null, "property_type": "...", "stage1_date": "...", "stage3_date": null,
      "days_in_s1": 0, "n_acts": 0, "n_subst": 0,
      "pillars": { "decisor": true, "pitch": false, "contato": false },
      "tier": "solida|rasa|suspeita", "tier_reason": "...",
      "evidence": [ { "date": "...", "owner": "...", "quote": "trecho mínimo" } ] }
  ]
}
```

O `score` preenche tudo determinístico. Você revisa `tier`/`tier_reason`/`evidence` nos
borderline antes do `render`.
