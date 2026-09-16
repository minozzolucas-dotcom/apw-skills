# Correções de ASR — Vocabulário APW / Telecom

Transcrição automática de áudio em português comete erros previsíveis, especialmente com jargão técnico, siglas e nomes de empresas. Este catálogo lista os erros recorrentes e como reconhecê-los pelo contexto. Não é exaustivo — é calibrado pelos padrões reais de reuniões da APW Brasil. Atualize conforme novos erros aparecerem.

## Como usar

Ao ler a transcrição, toda vez que uma palavra **não faz sentido no contexto técnico**, é provável erro de ASR. Cruze com este catálogo. Registre cada correção no glossário do briefing (eixo G). Se não conseguir determinar o termo correto com confiança, marque `[?]` — não chute.

## 1. Siglas e termos técnicos

| ASR escreveu | Quase certamente é | Pista de contexto |
|---|---|---|
| "herbes", "erbes", "9 mil herbes" | **ERBs** (Estações Rádio-Base) | Aparece com números grandes (90 mil, 25 mil); é o ativo contado no pipeline |
| "bad", "uma bad", "fazer uma bad" | **base** (de dados) | Contexto de CRM, planilha, "mandar a bad do CRM" |
| "frete", "lista de frete" | **leads** | Contexto de pipeline; "lista de leads" |
| "lei dema", "uma lei dema", "fazer uma dema" | **demo** (demonstração) | "fazer uma demo da ferramenta" |
| "LGTB", "questão de LGTB" | **LGPD** (Lei Geral de Proteção de Dados) | Contexto de compartilhar base, empresa global, burocracia |
| "pure guys", "pure pool", "fresh pool" | **leads crus / fresh leads** ("pool" de leads frescos) | Contexto de base nunca trabalhada |
| "take rate" | take rate (correto — taxa de conversão/aceitação) | Termo de negócio legítimo, não erro |
| "use of proceeds" | use of proceeds (correto — destinação do recurso) | Termo de negociação legítimo |
| "raw", "é raw" | raw (correto — dado cru) | Legítimo |
| "CTI", "dados CTI" | provavelmente **dados cadastrais / do contrato** [?] | Ambíguo — marcar [?] |
| "ARI" | Análise de Risco do Imóvel | Jargão APW |
| "DRS" / "direito de superfície" | Direito Real de Superfície | Termo contratual |

## 2. Nomes de empresas e ferramentas (telecom BR)

| ASR escreveu | Quase certamente é | Observação |
|---|---|---|
| "InfoQual" | **InfoSimples** ou similar [?] | Ferramenta de enriquecimento de dados por CPF/placa/e-mail — confirmar nome exato |
| "Teleco" | **Teleco** (correto) | Consultoria/base de dados de telecom BR |
| "Anatel" | Anatel (correto) | Agência reguladora |
| "Telemont" | **Telemont** (correto) | Empresa de infraestrutura telecom |
| "Lato a Lato", "a PC da Lato" | nome de empresa/operadora [?] | Ambíguo — possivelmente uma lease aggregator concorrente; marcar [?] |
| "Cal", "contratos da Cal" | torreira/empresa [?] | Contexto: "contratos da IHS, da Cal" — provável nome de tower company |
| "QMC" | **QMC Telecom** | Tower company |
| "Highline" | Highline (correto) | Tower company |
| "American Tower" / "ATC" | American Tower / ATC (correto) | Tower company |
| "IHS" | IHS (correto) | Tower company |
| "SBA" | SBA (correto) | Tower company |

## 3. Operadoras (MNOs)

Vivo, Claro, TIM, Oi — geralmente transcritas corretas. "Nextel" pode aparecer; foi absorvida pela Claro.

## 4. Erros estruturais (não de vocabulário)

- **Sem pontuação:** o ASR entrega um fluxo contínuo. Frases longas precisam ser segmentadas mentalmente para extrair a decisão de dentro.
- **Sem speaker labels:** quando não há rótulo de quem fala, inferir pelo conteúdo (ver Passo 1 do workflow).
- **Falas sobrepostas:** "[Falando ao fundo]", "[Silêncio]", "[Música]" — marcadores de que o ASR perdeu trecho. Não invente o conteúdo perdido.
- **Repetição e divagação:** fala falada repete muito ("é, é, então, então"). Não confunda ênfase repetida com fato novo.
- **Números falados:** "70 mulheres" quase certamente é **"70 aluguéis"** ou "70 múltiplos" no contexto de proposta financeira; "mil dividido por 25" é uma conta de taxa de conversão sendo feita em voz alta. Reconstrua o número pretendido pelo contexto.

## 5. Regra de ouro

Corrigir ASR é reconstrução com base em contexto, não adivinhação livre. Se o contexto sustenta a correção com segurança, corrija e registre no glossário. Se não, mantenha o termo original com `[?]` ao lado. É melhor um briefing que admite uma dúvida do que um que afirma um erro com confiança.
