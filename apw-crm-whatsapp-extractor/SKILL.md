---
name: apw-crm-whatsapp-extractor
description: Extrai telefones celulares e códigos L de uma view do Dynamics 365 CRM da APW Brasil via snippet JS rodado no console do navegador, pra alimentar campanhas de WhatsApp slow-drip. Use SEMPRE que o Lucas pedir "extrair telefones do CRM", "pegar celulares de uma view do Dynamics", "lista de contatos pra WhatsApp", "campanha slow drip", "exportar CSV de contatos do pipeline", "contatos de Stage X pra disparar WhatsApp", ou colar uma URL de view do Dynamics (apwireless.crm.dynamics.com, apw.crm.dynamics.com) pedindo extração dos landlords. Também acione quando ele mencionar Z-API, Twilio, WPPConnect ou outra plataforma de WhatsApp junto com o CRM. NÃO use pra reportes de pipeline (apw-reporte-crm-diario), análise de performance (apw-performance-patterns), nem forensics de uma única opp (apw-opp-activity-forensics).
---

# APW CRM → WhatsApp Extractor

Skill operacional pra extrair **código L + celular do landlord** de uma view do Dynamics 365 da APW Brasil, formatado em CSV pronto pra plataforma de disparo (Z-API, Twilio, WPPConnect, etc.).

Roda via snippet JS no **console do navegador**, usando `Xrm.WebApi` com a sessão autenticada do Lucas. Não precisa de API key, OAuth, nem fluxo externo.

---

## Fundamentos do schema APW

Descoberto em 19/10/2026 analisando a view Stage 5 da APW Brasil:

1. **O landlord não vive na `opportunity`**. Vive na entidade **`lead`**, linkada via dois lookups possíveis:
   - `apwip_leadopportunityid` (prioritário)
   - `originatingleadid` (fallback)

2. **Views da APW são `userQuery`**, não `savedQuery`. Chamar `?savedQuery=<id>` retorna "Record Is Unavailable" (erro 2147746327). Usar `?userQuery=<id>`.

3. **Taxa de preenchimento dos campos de telefone no lead** (amostra de 10):
   - `mobilephone`: 9/10 (prioritário)
   - `telephone1`: 8/10
   - `telephone2`: 7/10
   - `telephone3`: 7/10
   - `new_currentownermobilephonenumber`: 3/10
   - `new_currentownerphonenumber`: 4/10
   - `new_whatsapp`: 0/10 (campo morto)
   - `apwip_ownerphonenumber`: 0/10

4. **Casos edge comuns**:
   - Múltiplos números num campo só: "+5519996455151 / +551933076646" → splitar por /, ;, ,
   - Notas inline: "+55 32 99964 9234 - zap" → stripar parênteses e tudo depois de " - "
   - Telefone de terceiro (nora, zelador, imobiliária) misturado → marcar com flag multi_source_flag=revisar

---

## Como rodar

### 1) Abrir a view no CRM

Qualquer view de opportunity. Exemplo Stage 5:
https://apwireless.crm.dynamics.com/main.aspx?app=d365default&forceUCI=1&pagetype=entitylist&etn=opportunity&viewid=<VIEW_ID>&viewType=4230

Copiar o viewid da URL.

### 2) Abrir DevTools → Console (F12)

### 3) Diagnóstico (opcional, só na primeira vez)

Rodar scripts/01-diagnostic.js. Confirma userQuery vs savedQuery e preenchimento dos campos.

### 4) Extração

- scripts/02-extract.js — versão completa (12 colunas, flags).
- scripts/03-minimal.js — versão enxuta (só code, phone).

Pra teste, setar LIMITE=200 no topo.

### 5) Resultado

CSV cai no clipboard. Cola no Google Sheets (Ctrl+V) ou arquivo .csv.
Dados também em window.__apw (minimal) ou window.__apwExport (completa).

---

## Compliance (APW Brasil)

- Nunca screenshot desta tela (regra apw-chrome-agent-lean-compliance).
- Snippet roda local no navegador do Lucas, com sessão dele. Zero dado sai do Dynamics pra terceiros.
- CSV tem PII (telefones de landlords) → tratar como confidencial. Sheets usado deve ser privado.
- Pra disparo via plataforma externa (Z-API etc.), confirmar que a plataforma tem contrato ativo e opt-out visível.

---

## Normalização de número → E.164 BR

1. Strip de tudo que não é dígito.
2. Se começa com 55 e tem >=12 dígitos → já é E.164, só prefixa +.
3. Se tem 10 ou 11 dígitos → prefixa +55.
4. Pra campanha WhatsApp (celular only): exigir 11 dígitos pós-DDD E 3º dígito = 9.
5. Fixos (10 dígitos ou 3º dígito != 9) ficam marcados is_mobile=fixo ou são descartados na versão minimal.

---

## Troubleshooting

| Sintoma | Causa | Fix |
|---|---|---|
| Record Is Unavailable (2147746327) | View é userQuery, não savedQuery | Trocar ?savedQuery= por ?userQuery= |
| CSV vazio | Campos de telefone diferentes | Rodar 01-diagnostic.js |
| Muitos pulados | Opps sem lead ligado | Normal pra opps antigas |
| Chrome trava no paste | CSV > 2000 linhas | Usar download de arquivo |
| Throttle do Dataverse | View com milhares de opps | Trocar loop em série por $batch |

---

## Roadmap

- [ ] Suporte a $batch pra views com 1000+ opps.
- [ ] Output direto pra API da plataforma de WhatsApp (Z-API).
- [ ] Enriquecer com last_contact_date pra priorizar quem não é contactado há mais tempo.
- [ ] Flag de opt-out: ler donotphone do lead e excluir.
- [ ] Deduplicação por telefone.

---

## Histórico

- **19/10/2026**: Skill criada. Descoberta inicial na view Stage 5 (viewid 572e1df3-7198-eb11-b1ac-000d3a32d0bd), 10 leads de amostra, resultado: mobilephone cobre 90% + telephone1-3 cobrem o resto.
