---
name: apw-dossie-drs
description: Gera o DOSSIÊ INFORMATIVO de Direito Real de Superfície (DRS) da APW Brasil — PDF na marca oficial explicando ao proprietário PF a natureza do DRS (art. 1.369 CC), o enquadramento como ganho de capital (Lei 7.713/88, INs RFB 84/2001 e 599/2005, RIR/2018), a fórmula com redutores por tempo de posse e a simulação personalizada do IR do deal. Antes de gerar, COLETA as infos necessárias via checklist (valor da alienação, data de aquisição, custo). Use SEMPRE que o Lucas pedir "dossiê do DRS", "material informativo pro proprietário", "doc de DRS", "simula o imposto do DRS", "quanto de IR o proprietário paga", "material explicativo de superfície", ou mandar valor de alienação + data de aquisição pedindo material ou simulação. NÃO use para proposta comercial (apw-proposta-comercial), parecer de cláusula (apw-telecom-real-estate-counsel), material de condomínio (apw-dossie-cessao), pré-DD (apw-pre-dd-legal) nem gross-up de aluguel (apw-rent-gross-up).
---

# APW Dossiê Informativo — DRS (Ganho de Capital PF)

Gera o material educativo em PDF (marca APW) que explica ao proprietário pessoa física — e ao contador dele — o que é o DRS e como fica o imposto de renda na alienação. **Não é a proposta comercial** — é o material que destrava a objeção "quanto vou pagar de imposto?".

## Passo 1 — Coleta de informações (checklist obrigatório)

Verifique o que já está na conversa e **pergunte só o que faltar**, numa única mensagem:

**Obrigatórios para simulação personalizada:**
1. **Valor da alienação do DRS** (R$ da antecipação)
2. **Data de aquisição do imóvel** pelo proprietário (mês/ano — define os redutores)
3. **Custo de aquisição** declarado do imóvel (se desconhecido, usar R$ 0,00 e sinalizar — cenário conservador, IR máximo)

**Opcionais (melhoram o material):**
4. Nome do(s) proprietário(s) e código L
5. Prazo do DRS (default 30 anos)
6. Matrícula / cartório
7. Se o proprietário vendeu outro imóvel nos últimos 5 anos ou se é o único imóvel (afeta teses de isenção — NÃO prometer isenção do art. 39 da Lei 11.196/05: ela exige aplicação em imóvel residencial e o DRS não se enquadra de forma pacífica; apenas mencionar como ponto a validar com contador, se relevante)

**Sem os itens 1–2**, gerar a versão genérica (template com os dois exemplos padrão) e avisar que a simulação personalizada fica pendente.

## Passo 2 — Simulação do ganho de capital

Leia `references/calculo_gcap.md` para a matemática dos redutores (Lei 7.713/88 art. 18 + fatores FR1/FR2 da Lei 11.196/05 art. 40). Regras:
- Alíquota: 15% até R$ 5 milhões de ganho (tabela progressiva da Lei 13.259/16 acima disso — raro em deal APW)
- Sempre apresentar também a **carga efetiva sobre o valor recebido** (IR ÷ valor da alienação) — é o número que destrava a conversa
- Sempre rotular como **simulação estimativa**, a confirmar no programa GCAP com o contador, com DARF até o último dia útil do mês seguinte ao recebimento
- Pagamento parcelado: IR proporcional a cada parcela (mencionar apenas se o deal for parcelado)

## Passo 3 — Gerar o PDF

Use `assets/template_drs.html` (marca APW validada: navy #012B5E, azul #1C75BB, sage #91A5A4, Arial). Estrutura fixa:
1. Natureza do DRS (art. 1.369 CC; sem transferência da propriedade do solo)
2. Enquadramento tributário (tabela de base legal)
3. Cálculo do ganho de capital (fórmula em destaque + box "regra prática" do custo zero)
4. Exemplos/simulação — **substituir os exemplos genéricos pela simulação do deal** quando houver dados; manter linha de carga efetiva
5. Conclusão + disclaimer obrigatório

Renderizar com weasyprint e salvar em `/mnt/user-data/outputs/APW_Brasil_DRS_[Lnumber_ou_nome].pdf`.

## Guardrails — NÃO NEGOCIÁVEIS

1. Toda simulação leva o rótulo de estimativa e a recomendação de validação com contador/GCAP. O disclaimer final não sai do documento sem confirmação explícita do Lucas após alerta.
2. NUNCA afirmar isenção total do ganho de capital (imóvel único, art. 39 da 11.196/05 etc.) — no máximo listar como tese a validar com o contador do proprietário.
3. Não confundir com o IRRF mensal do aluguel (isso é apw-rent-gross-up); aqui o tributo é ganho de capital na alienação.
4. Datas de aquisição anteriores a 1989 têm redutor adicional de 5% ao ano (Lei 7.713/88) — pode zerar o ganho para imóveis muito antigos; conferir na referência antes de calcular.

## Passo 4 — Entrega

`present_files` com o PDF + resumo curto: valores simulados, carga efetiva e o que ficou pendente de confirmação.
