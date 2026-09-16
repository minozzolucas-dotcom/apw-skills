---
name: apw-sir-request
description: Monta o pedido de SIR (Site Inspection Report / vistoria de campo) da APW Brasil para o Filipe da FCA Telecom (filipe@fcatelecom.com.br) — puxa do Dynamics 365 via snippet F12 (ou Chrome agent) o endereço do site, coordenadas, tipo de imóvel, torreira/operadora e o MELHOR telefone e e-mail de contato (varrendo cadastro E as atividades da opp), e devolve o e-mail pronto com o checklist de documentos a anexar. Use SEMPRE que o Lucas disser "pede o SIR", "solicita vistoria", "manda pro Filipe", "e-mail de SIR do Lxxxxx", "preciso agendar vistoria nesse site", "puxa os dados pro SIR", "quais docs mando pro vistoriador", "monta o pedido de inspeção", ou mandar um código L pedindo vistoria de campo. Acione também com menção a FCA Telecom, fcatelecom.com.br, vistoriador, inspeção de site, ou lote de L-numbers para vistoria. NÃO use para ANALISAR um SIR já recebido (apw-sir-analyst), dossiê do deal (apw-deal-dossier), pré-DD registral (apw-pre-dd-legal), nem upload de docs no M-Files (apw-mfiles-upload).
---

# apw-sir-request

Gera a solicitação de vistoria (SIR) para o **Filipe — FCA Telecom — filipe@fcatelecom.com.br**.

O gargalo do pedido de SIR nunca é o texto do e-mail: é **juntar endereço + coordenada + contato que atende + os documentos certos**. Esta skill resolve as quatro coisas.

## Fluxo (3 passos)

1. **Extração** — rodar o snippet no Dynamics e coletar os campos do deal.
2. **Validação** — mostrar ao Lucas o que veio, com as divergências marcadas, antes de escrever.
3. **E-mail** — montar o rascunho no template fixo + checklist de anexos.

**Nunca enviar e-mail.** Sempre devolver o texto pronto para o Lucas colar/revisar no Outlook.

---

## Passo 1 — Extração no Dynamics

**REGRA APW: sempre perguntar antes de executar** — "roda via snippet F12 no console ou via agente do Chrome?" Não assumir. Default sugerido: **F12** (mais rápido, sem screenshot, compliance-friendly).

Se F12: entregar o snippet de `scripts/snippet_sir.js`, substituindo o L-number. O Lucas roda com a aba do Dynamics aberta e logada (`apwbrasil.crm2.dynamics.com`) e cola o JSON de volta.

Se Chrome agent: seguir `apw-chrome-agent-lean-compliance` — `javascript_tool` executando o mesmo snippet, **sem screenshot** (domínio Dynamics é sensível).

### O que a extração precisa entregar

| Campo | Onde procurar | Regra |
|---|---|---|
| Código L + nome do site | `opportunity.name` | — |
| Endereço completo | campos de address da opp / lead vinculado | logradouro, nº, bairro, município, UF, CEP |
| Coordenadas | lat/long da opp ou do lead | **decimal, 6 casas, sinal negativo** + link Maps |
| Property type | campo de tipo de imóvel | define se matrícula entra na lista de docs |
| Torreira / operadora | campos carrier/tower | se ausente, marcar "a confirmar" |
| Telefone de contato | contact/account **+ atividades** | ver regra abaixo |
| E-mail de contato | contact/account **+ atividades** | idem |

### Regra do contato (a mais importante)

O telefone do cadastro no Dynamics costuma ser velho. **O número que funciona quase sempre está na descrição da última atividade** ("liguei no 11 9xxxx, falei com o zelador"). Então:

- Varrer as últimas ~25 atividades da opp com regex de telefone e e-mail.
- Se cadastro e atividade divergirem, **mostrar os dois ao Lucas** com a data de cada, e recomendar o mais recente.
- Nunca escolher sozinho em silêncio. Nunca inventar contato.
- Registrar observação operacional quando aparecer na atividade ("falar com o zelador", "só de manhã", "portaria não repassa").

---

## Passo 2 — Validação antes de escrever

Devolver no chat um bloco curto:

```
L969223 — Cond. Ed. Aurora — Santo André/SP
Endereço: Rua X, 223 — Vila Y — Santo André/SP — 09070-000
Coord: -23.181920, -47.094030  ✅ bate com o endereço
Tipo: ROOFTOP → matrícula NÃO entra nos anexos
Torreira: SBA | Operadora: TIM

Contato:
  Cadastro:   José Silva — (11) 3333-4444 — jose@x.com   (contact, últ. edição 2023)
  Atividade:  (11) 99999-8888 — "falei com o síndico Marcos"  (12/08/2026) ← RECOMENDADO

Docs a anexar: contrato+aditivos ✅ | croqui ❌ falta | POP ✅ | IPTU ❌ falta
```

Coordenada que não bate com o município do endereço = **parar e avisar**. Vistoria em coordenada errada queima o deal e a viagem.

Docs faltando: apontar onde buscar (M-Files do L-number) e perguntar se segue mesmo assim ou espera.

---

## Passo 3 — E-mail

Template fixo em `assets/template_email.md`. Regras:

- Tratamento **"você"** — nunca "o senhor". (Regra APW para toda comunicação externa.)
- Direto, campos em bloco, sem narrativa. O Filipe precisa do endereço, da coordenada e de quem atende.
- Assunto: `Solicitação de SIR – L[xxxxxx] – [Município]/[UF]`
- Campo sem dado → **omitir a linha inteira**. Não escrever "não informado", não inventar.
- Batch: um e-mail por site. Nunca juntar dois sites no mesmo e-mail — a vistoria é agendada individualmente.

### Checklist de documentos (regra de negócio)

Sempre anexar:

- **Contrato de locação + toda a cadeia de aditivos**
- **Croqui do contrato** (o anexo do próprio contrato, não croqui novo)
- **Comprovante de pagamento do aluguel** (POP)
- **Espelho de IPTU** — serve para o vistoriador conferir a área/inscrição contra a matrícula

Anexar **somente se greenfield / torre / terreno (Trilha B)**:

- **Matrícula do imóvel**

Em rooftop / condomínio (Trilha A) a matrícula **não vai** — o objeto é o direito creditório, não o imóvel, e mandar matrícula de condomínio só gera ruído.

Se property type vier ambíguo no CRM, decidir pelo croqui/contrato (torre em solo = Trilha B) e **avisar o Lucas da inferência**.

---

## Casos de borda

- **Site sem coordenada no CRM** → geocodificar pelo endereço, marcar como **estimada** no e-mail e pedir ao Filipe que confirme em campo. Nunca mandar coordenada estimada sem sinalizar.
- **Endereço sem número (s/n)** → obrigatório mandar ponto de referência da atividade ou coordenada de alta confiança.
- **Contato só via síndico/administradora** → colocar nome da administradora e horário comercial no bloco de obs.
- **Lote de L-numbers** → rodar o snippet uma vez por L (ou versão em loop), consolidar numa tabela de validação, e só então gerar os e-mails em sequência.
- **Deal em condomínio sem contato direto do síndico** → sinalizar; vistoria sem alguém para abrir a porta do terraço é viagem perdida.

## Arquivos

- `scripts/snippet_sir.js` — snippet F12 de extração (opp + contatos + varredura de atividades)
- `assets/template_email.md` — template do e-mail e do assunto
