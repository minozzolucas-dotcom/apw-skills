---
name: apw-pin-creator
description: Cria o PIN (Lead geolocalizado) no Dynamics 365 CRM da APW Brasil a partir de documentos de um site de telecom que ainda NÃO está no CRM. Recebe contrato de locação, alvará, matrícula ou memorial (texto ou PDF/DOCX), extrai e mapeia os dados para o formulário "New Lead" do leadsearch2.aspx, faz o farejamento de coordenadas em 3 níveis de confiança, mostra o mapeamento campo-a-campo para revisão e — só após confirmação do Lucas — cria o Lead via Web API autenticada. Use SEMPRE que o Lucas disser "criar o PIN", "cadastrar o site no CRM", "esse site não está no CRM", "rodar o PIN desse contrato", "criar lead a partir do contrato", "farejar coordenada do site", "novo lead geolocalizado", ou enviar documentos de um site (contrato telecom, alvará, matrícula) pedindo para cadastrar a oportunidade que ainda não existe. NÃO use para deals já cadastrados por código L (apw-deal-dossier), análise de cláusula (apw-telecom-real-estate-counsel), nem para preencher Key Notes de opp existente (apw-crm-key-notes-writer).
---

# APW PIN Creator

Skill para o Lucas (APW Brasil) cadastrar um site de telecom **novo** no Dynamics 365 — criar o "PIN", que no fluxo da APW é um **Lead geolocalizado** criado pelo formulário "New Lead" do `leadsearch2.aspx`.

O caso de uso: o Lucas tem um contrato (e às vezes alvará, matrícula, memorial) de um site que **não está no CRM ainda**. Ele manda os documentos, a skill transforma isso num Lead pronto, ele confirma, a skill cria.

Esta skill **escreve no CRM** (cria o Lead). Por isso ela nunca cria às cegas: monta tudo, mostra o mapeamento campo-a-campo, e só executa após o Lucas dizer "confirma".

---

## Base Anatel local (validação automática de coordenada)

Antes de gravar coordenada no Lead, VALIDE contra a base Anatel nacional
embutida na skill `apw-erb-towerco-triage` (extração jul/2026, 111.296
estações — não precisa pedir planilha nem abrir o Mosaico):

```bash
python3 /mnt/skills/user/apw-erb-towerco-triage/scripts/anatel_lookup.py \
  --near=<LAT>,<LNG> --radius 150 --json
```

- **Achou ERB** → sobe o nível de confiança da coordenada e herde
  operadora / ClassInfraFis (→ trilha) / Tecs para os campos do Lead.
- **Não achou** em 150 m → alargue para 300 m; se ainda nada, sinalize ao
  Lucas que o ponto não tem estação licenciada na base de jul/2026
  (site novo, descomissionado ou coordenada ruim) antes de criar o Lead.

## Herança de outras skills

Esta skill **não reinventa** o acesso ao Dynamics. Ela herda o padrão da `apw-dynamics-copilot`:

- **Acesso via sessão autenticada do navegador** — nunca OAuth próprio, nunca credencial armazenada. Usa a sessão que o Lucas já tem aberta no Chrome.
- **Anti-screenshot agressivo** — ordem: `javascript_tool` → `get_page_text` → `read_page` → `computer` (último recurso). Tenant Brasil: `apwbrasil.crm2.dynamics.com`.
- **Não-retenção** — nada de salvar contrato, PII, valores ou payload do CRM em disco. Tudo em memória ou no contexto da conversa. Ver `references/nao-retencao.md` se precisar do detalhe; as regras são as mesmas da `apw-dynamics-copilot`.

Se a `apw-chrome-agent-lean-compliance` estiver disponível, ela também se aplica — domínio Dynamics é corporativo sensível, screenshot bloqueado.

---

## Workflow — 6 passos

Siga nesta ordem. Não pule a confirmação (passo 5).

### 1. Receber e ler os documentos

O Lucas manda os documentos do site. Podem vir como texto colado OU arquivo (PDF/DOCX) — os dois casos acontecem.

- Se vier **arquivo**: leia primeiro o `SKILL.md` da skill `pdf` (para PDF) ou `docx` (para DOCX) antes de processar. PDFs escaneados precisam de OCR.
- Se vier **texto colado**: use direto.

Documentos típicos de um caso, e o que cada um entrega:

| Documento | O que extrair |
|---|---|
| Contrato de locação / ground lease | Locador (proprietário), locatária (operadora/torreira), município, área locada, matrícula, aluguel, prazo, reajuste |
| Alvará de construção | Confirmação da torre, endereço da obra, bairro, município, área |
| Matrícula do imóvel | Proprietário registral, descrição, ônus |
| Memorial descritivo / Anexo | Confrontações, referências geográficas (rios, rodovias) |

Pode vir só o contrato. Pode vir um pacote. Processe tudo que chegar.

### 2. Extrair e estruturar os dados

Leia `references/extracao-contrato.md` para o guia completo de extração. Em resumo, extraia:

- **Partes**: nome do locador (proprietário — vira o Contact), nome e CNPJ da locatária (operadora/torreira)
- **Site**: município, bairro/distrito, rodovia/referência de acesso, área locada (m²), matrícula e ofício de registro
- **Comercial**: aluguel mensal, índice de reajuste, prazo, data de início, renovações
- **Coordenadas**: qualquer pista de localização (ver passo 3)

### 3. Farejar as coordenadas — 3 níveis de confiança

Este é o coração da skill e o passo onde mais se erra. Leia `references/farejador-coordenadas.md` para o procedimento completo.

**Regra de ouro: a skill NUNCA inventa uma coordenada com cara de precisa.** Ela classifica a pista de localização em um de três níveis e é honesta sobre qual:

- **ALTA** — o documento traz latitude/longitude explícitas (decimais ou GMS). Use direto. Valide só se cai no município certo.
- **MÉDIA** — não há lat/long, mas há um endereço geocodificável (rodovia + km + bairro + município). Geocodifique, devolva o ponto e diga ao Lucas: "isto é uma estimativa de ~X centenas de metros, confirma no satélite antes de criar."
- **BAIXA** — só há memorial descritivo por confrontações (rios, divisas, "200 braças"), sem azimute nem coordenada. **Não tente triangular.** Devolva o centroide do distrito/município como ponto de partida e diga explicitamente: "isto NÃO é a torre — é só pra você abrir o satélite nessa região e achar a estrutura visualmente."

**Divergência de município é red flag.** Se o contrato diz um município e o alvará/endereço dos proprietários diz outro (comum em imóvel rural na divisa), NÃO escolha um calado. Aponte a divergência para o Lucas e pergunte qual usar. Imóvel rural na divisa de municípios é caso clássico.

### 4. Montar o mapeamento campo-a-campo

Monte a tabela de mapeamento para o formulário "New Lead". Os campos do form estão em `references/campos-lead-form.md`. Estrutura da tabela:

```
CAMPO DO FORM          | VALOR PROPOSTO              | FONTE              | CONFIANÇA
-----------------------|-----------------------------|--------------------|-----------
Lead Source            | (pedir ao Lucas)            | —                  | —
Street                 | BR-020, km 13               | Alvará             | média
Neighborhood           | Cacimba Nova                | Alvará             | alta
City                   | Madalena  ⚠ contrato diz Quixeramobim | Alvará/Contrato | DIVERGÊNCIA
State/Province          | CE                          | Contrato           | alta
Latitude / Longitude   | -5.00xx / -39.5xxx (centroide distrito) | Farejador | BAIXA — não é a torre
Property Type          | (pedir ao Lucas)            | —                  | —
First/Last Name        | Francisca Idelvani / Brito Dede | Contrato       | alta
Entity                 | —                           | —                  | —
Subject                | TT0081 — Site Cacimba Nova  | gerado             | —
Description            | resumo do contrato          | gerado             | —
```

Campos que **sempre** ficam para o Lucas decidir (não invente): `Lead Source` e `Property Type` são dropdowns — proponha o que fizer sentido mas peça a seleção. Campos sem fonte ficam vazios; não preencha com suposição.

O **Subject** deve ser curto e identificável (código do site + referência). O **Description** é um resumo objetivo do contrato: partes, aluguel, prazo, matrícula, e qualquer red flag (divergência de município, ônus, cláusula restritiva).

### 5. Mostrar para revisão e ESPERAR confirmação

Mostre ao Lucas a tabela de mapeamento completa, mais:

- O nível de confiança da coordenada e o que ele precisa fazer (validar no satélite, se média/baixa).
- Qualquer divergência ou gap (campo sem fonte, município conflitante).
- Os dois dropdowns que ele precisa preencher.

Então pergunte, literalmente: **"Confirma a criação do Lead com esses dados?"**

**Não crie nada antes do "sim/confirma/segue".** Se ele pedir ajuste, ajuste e mostre de novo.

### 6. Criar o Lead via Web API

Só depois do "confirma". Leia `references/criar-lead-webapi.md` para o procedimento.

Resumo: o `leadsearch2.aspx` é uma página **customizada** da APW — o endpoint que o botão `Create Lead` chama não é conhecido de antemão. Por isso o passo 6 começa com **descoberta**:

1. Confirme que há aba aberta no `apwbrasil.crm2.dynamics.com` (`tabs_context_mcp`). Se não, peça pro Lucas abrir — não faça login.
2. Inspecione a página do form `leadsearch2.aspx` via `javascript_tool` para descobrir como o `Create Lead` submete (entidade `lead` nativa via `/api/data/v9.2/leads`, ou um endpoint custom). Detalhes em `references/criar-lead-webapi.md`.
3. Monte o payload com os campos confirmados no passo 5.
4. Execute a criação.
5. Confirme o sucesso e devolva ao Lucas o ID do Lead criado. **Não tire screenshot pra "provar"** — confie no retorno da API.

Se a descoberta falhar ou o endpoint não for reproduzível, **não force**. Caia para o modo alternativo: entregue ao Lucas o mapeamento 100% pronto e os valores na ordem do form, para ele colar e clicar `Create Lead` na mão. Melhor um fallback honesto que um POST cego num endpoint errado.

---

## Estilo de comunicação

- Português brasileiro casual, direto, sem floreio (padrão APW do Lucas).
- Estrutura escaneável — o Lucas tem ADHD, tabelas e blocos ajudam.
- Quando algo falhar, diga o que falhou e o que vai tentar. Não simule sucesso.
- Nunca ecoe PII (CPF, CNPJ, nome de proprietário) sem necessidade. Os documentos têm muito disso.

## Quando NÃO usar

- Deal já existe no CRM (tem código L) → `apw-deal-dossier` ou `apw-dynamics-copilot`.
- Análise jurídica de cláusula → `apw-telecom-real-estate-counsel`.
- Preencher Key Notes / Pricing Option de opp existente → `apw-crm-key-notes-writer`.
- Montar a proposta comercial → `apw-proposta-comercial`.

Esta skill é só a porta de entrada: transformar documentos de um site **novo** num PIN no CRM.
