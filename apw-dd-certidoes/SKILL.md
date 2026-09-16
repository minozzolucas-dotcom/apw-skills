---
name: apw-dd-certidoes
description: Use quando precisar COLETAR o kit de certidões e documentos de due diligence (DD) de um deal APW Trilha B (terreno/PF ou PJ) — matrícula atualizada e certidão de ônus, certidões cíveis/criminais/fiscais/trabalhistas, IPTU/tributos municipais, protesto, CNIB, registro civil, POP de aluguel — acionando agentes de navegador em PARALELO, um por fonte. Aciona com "puxa as certidões do Lxxxx", "coleta a DD", "busca os documentos do deal", "roda os agentes de certidão", "monta o kit de DD", normalmente depois que a pré-DD apontou o que falta. NÃO use para a análise registral/veredito em si (apw-pre-dd-legal), para gravar no CRM (apw-crm-key-notes-writer), nem para deal de condomínio/Trilha A.
---

# APW DD Certidões — Coletor Paralelo

## Overview
Orquestra **agentes de navegador em paralelo** para coletar o kit documental de due diligence de um deal APW **Trilha B** (terreno/PF ou PJ), **um agente por fonte**. A `apw-pre-dd-legal` diz **o que** falta (Bloco B1–B3); esta skill **busca**. Princípio inegociável: o agente **lê, baixa e reporta** — **nunca** cria conta, loga, paga, resolve captcha ou assina. Tudo que exige conta/pagamento/captcha **para e volta para o humano (Lucas)** com o link no ponto exato.

## When to use
- Depois da pré-DD apontar pendências documentais: "puxa as certidões do Lxxxx", "coleta a DD", "monta o kit de DD", "roda os agentes de certidão".
- Deal **Trilha B** (terreno/PF ou PJ).

**Não usar para:** análise registral / veredito de vedação (`apw-pre-dd-legal`); gravar no CRM (`apw-crm-key-notes-writer`); deal de condomínio/**Trilha A** (lá o foco é ata/edital/procuração, não certidão de matrícula).

## Regras inegociáveis — o agente NÃO faz
**Violar a letra destas regras é violar o espírito.** Em cada fonte, o agente:
1. **NÃO cria conta / NÃO faz login.** Tela de cadastro/login → PARA, marca `PENDENTE-LOGIN`, devolve o link.
2. **NÃO paga nada** — boleto, cartão, PIX, checkout. → PARA, marca `PENDENTE-PAGAMENTO`, devolve o link no ponto exato. Pagamento é ação humana.
3. **NÃO resolve captcha** (nem "só dessa vez"). → PARA, marca `PENDENTE-LOGIN`.
4. **NÃO assina, NÃO outorga procuração, NÃO submete formulário que crie obrigação.**
5. **Só insere o estritamente necessário** (CPF, matrícula, inscrição) nos campos exigidos — nada de dado pessoal extra.
6. **Salva** cada documento como `DD_L<número>_<fonte>.pdf` na pasta do deal; **não sobe** em lugar nenhum (o Lucas arquiva no M-Files).
7. Portais públicos `.gov`/`.org` → screenshot ok se necessário. Domínio **corporativo** (Dynamics, M-Files) segue `apw-chrome-agent-lean-compliance` (sem screenshot).

## Inputs (coletar antes de disparar — não inventar)
- **Deal:** L-number.
- **Vendedor/concedente:** PF → nome, CPF, RG, estado civil, naturalidade, **domicílio atual + comarcas anteriores na cadeia** (varrer todas). PJ → razão social, CNPJ, sócios/representante (abre bloco societário).
- **Imóvel:** matrícula nº + **RGI/comarca**, inscrição municipal, **UF/município**.
- **Receita:** torreira/operadora + dados bancários do aluguel (para o POP).

Faltou algum campo? **Perguntar ao Lucas antes** de disparar.

## Os 6 agentes (em paralelo)
| # | Agente | Fonte / objeto | Input | Flag típica |
|---|---|---|---|---|
| 1 | Registral | Central RI (ONR/UF): inteiro teor **atualizado**, ônus e ações reais/reipersecutórias, pesquisa de bens | matrícula + comarca + CPF | PAGO + LOGIN |
| 2 | Tributário municipal | Prefeitura: espelho IPTU + CN débitos imobiliários | inscrição municipal | varia (cidade pequena = MANUAL) |
| 3 | Judicial PF | TJ da UF (1º grau, por comarca) + Justiça Federal da região: cível + criminal | CPF (+ filiação p/ criminal) | TJ varia / criminal grátis |
| 4 | Fiscal PF | PGFN/RFB + Receita Estadual da UF + TST(CNDT) | CPF | federais GRÁTIS/IMEDIATO |
| 5 | Civil/Protesto/CNIB | CENPROT (protesto) + CNIB (indisponibilidade) + CRC (nascimento/interdição) | CPF/nome | CNIB grátis; protesto/CRC pode pagar |
| 6 | Receita/Contrato (com Lucas) | contrato de locação (já em mãos) + POP dos 3 últimos aluguéis | extrato/banco | MANUAL |

PJ na cadeia → abrir bloco extra (CND FGTS, falência/recuperação, distribuidores da PJ, prova de poderes).

## Portais — nacionais fixos + estaduais por UF
**Nacionais (qualquer UF):**
- Matrícula / ônus / pesquisa de bens → `registradores.onr.org.br` (ou central da UF: `registradores.org.br/<uf>`)
- CND federal PF (RFB/PGFN) → `regularize.pgfn.gov.br` / `servicos.receita.fazenda.gov.br` — GRÁTIS
- CNDT trabalhista → `cndt-certidao.tst.jus.br` — GRÁTIS/IMEDIATO
- CNIB indisponibilidade → `indisponibilidade.org.br` — GRÁTIS
- Protesto → `cenprotnacional.org.br`
- Registro civil (nascimento/interdição) → `registrocivil.org.br` (CRC)

**Estaduais — RESOLVER pela UF do imóvel/domicílio antes de disparar:** TJ da UF, TRF da região (1ª DF/GO…, 3ª SP/MS, 4ª PR/SC/RS, etc.), Secretaria da Fazenda da UF. *Disparar sem resolver a UF = usar portal errado.*

## Consolidação (output final, obrigatório)
Tabela **fonte → status → arquivo**, com `status ∈ {OBTIDA, PENDENTE-PAGAMENTO, PENDENTE-LOGIN, MANUAL, FALHOU}`. Depois, 3 listas: **(i)** obtidas; **(ii)** precisa do humano (com o link no ponto de parada); **(iii)** manual (prefeitura, POP). Devolver os achados para **atualizar o dossiê da `apw-pre-dd-legal`** (Blocos B1–B3).

## Exemplo preenchido — L1354712 (Solange Maquea Garcia · Barbosa Ferraz/PR)
- PF: Solange Maquea Garcia · CPF 866.823.349-15 · RG 6.021.786-6 SESP/PR · solteira · natural de Araruna/PR · domicílio Rua Pernambuco 300, Barbosa Ferraz/PR · comarcas a varrer: Barbosa Ferraz **e** São João do Ivaí.
- Imóvel: matrícula 5.543, RGI Barbosa Ferraz/PR · inscrição 05-080-0002-000000001-001 · UF PR.
- UF resolvida → TJ `tjpr.jus.br/certidoes`, Justiça Federal `trf4.jus.br` (4ª região), Receita Estadual `fazenda.pr.gov.br`.
- Prioridade 1 = **inteiro teor atualizado da matrícula 5.543** (confirma o R-07 da Solange) — é a peça-rainha e a 1ª condicionante da carta de intenção.

## Rationalization table
| Desculpa | Realidade |
|---|---|
| "É só um captcha rápido" | Captcha = PARA. Sempre handoff. |
| "O cadastro é grátis, posso criar a conta" | Não criar conta. `PENDENTE-LOGIN`. |
| "O boleto é baixo, pago e a APW reembolsa" | Nunca pagar. Pagamento é humano. |
| "Assino só para prosseguir o pedido" | Não assinar nada. |
| "Preencho o endereço todo para garantir o match" | Só o campo exigido (CPF/matrícula/inscrição). |
| "A cidade não tem portal, então deixo em branco" | Marca `MANUAL` e sugere e-mail à prefeitura — não some. |

## Red flags — PARE e marque status
Tela de login/cadastro · captcha · checkout/boleto/cartão/PIX · "assine para continuar" · pedido de dado pessoal além de CPF/matrícula/inscrição. → PARA, marca o status, devolve o link no ponto exato.

## Common mistakes
- Disparar sem **resolver a UF** → portal errado.
- Esquecer as **comarcas anteriores** do domicílio na varredura judicial.
- Tratar matrícula desatualizada como "ok" — a DD exige **inteiro teor atualizado**.
- Confundir **Trilha A** (condomínio) com **Trilha B** — esta skill é Trilha B.
