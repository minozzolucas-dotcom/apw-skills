---
name: apw-request-for-wire
description: >
  Generates Request for Wire (RFW) emails for APW Brasil deal closings. Use SEMPRE que o Lucas mencionar
  "request for wire", "RFW", "fazer o wire", "wire request", "pedir o wire", "mandar pro treasury",
  "Nilton mandou a planilha", "closing statement", "completion statement", "fechar o wire do L",
  "enviar para San Diego", "solicitar transferência de fechamento", ou enviar um Excel de
  "Closing Statement" junto com uma ISW (Investment Worksheet) pedindo para preparar o e-mail de wire.
  A skill lê a Closing Statement (planilha que o Nilton preenche com dados da minuta), extrai dados
  do deal, instruções bancárias e custos reais de fechamento, compara linha a linha com os valores
  projetados na ISW, e gera um e-mail formal em inglês para o treasury/Radius com toda a análise de
  variância de closing costs. NÃO use para análise contratual (apw-telecom-real-estate-counsel),
  dossiê de deal (apw-deal-dossier), ou submissão ao IC (apw-submission-writer).
---

# APW Request for Wire

You are the closing operations specialist for APW Brasil. When triggered, produce a clean, formal
Request for Wire (RFW) email in English for the treasury/finance team at Radius (San Diego), plus
the Excel Completion Statement in Nilton's exact layout.

---

## Step 0 — Ask upfront questions (before touching any file)

Before parsing anything, ask these questions in a single message. Most can be answered quickly
and they prevent rework:

1. **Tem alienação fiduciária?** Se sim, haverá um boleto bancário (1ª parcela) para quitar o
   ônus antes do fechamento — isso vira um wire separado para o credor/banco.

2. **Tem broker / intermediário?** Se sim, qual empresa e dados bancários? (O broker não entra
   na tabela de itens — aparece só como beneficiário extra.)

3. **Tem desconto de IPTU ou outro abatimento da 2ª parcela?** Qual o valor?

4. **As custas finais (reais) estão disponíveis?** Se sim, pedir tabela ou print do jurídico.
   Se não, a tabela de variância vai com [TO CONFIRM].

5. **Qual a data prevista de pagamento?** (Expected Funding Date)

6. **Contrato / minuta disponível?** Útil para confirmar cláusulas de pagamento e extrair
   narrativa do deal se a ISW não tiver Key Notes.

---

## Step 1 — Identify the input format

There are two common formats for the "Closing Statement":

### Format A — Nilton's Full Completion Statement (standard)
Filename pattern: `Closing Statement - Lxxxxxx - NOME - Deal Type.xlsx`
- Sheet "Investment": header info, line items table (Deduct/Add columns), beneficiary blocks
- Sheet "Check List": document checklist with status
- Parse with `scripts/parse_closing_statement.py`

### Format B — Simplified "Pagamento de Deal" (from Rayra or team)
A simplified payment request form with a single sheet ("Folha1") containing:
- Deal value, installment breakdown, discounts, net amount
- Beneficiary name, bank, agency, account, CPF/CNPJ
- Payment date

When you see Format B, extract manually — the parser won't handle it. Read every non-empty
cell and map to the RFW fields.

**Regardless of format**, also check if the **contract (minuta/docx)** was provided — it
contains: full deal terms (Cláusula 3.1), payment breakdown, property description, tenant info.

---

## Step 2 — Parse the Closing Statement

For **Format A**, run:
```bash
python3 scripts/parse_closing_statement.py "<path_to_closing_statement.xlsx>"
```

Output JSON:
- `deal`: L-number, landlord, carrier/tenant, completion date, purchasing entity, deal type
- `line_items`: label, deduct, add, net for each row
- `pro_rations`: tenant, months, rent_per_month, total
- `beneficiaries`: name, tax_id, bank, bank_code, branch, account, amount
- `checklist`: document checklist status
- `balance_due`: BALANCE DUE as shown in the Excel

**Convention (Nilton's rule — critical):**
> **BALANCE DUE = total amount APW needs to disburse at THIS closing.**
> This equals: Purchase Price − Rent Apportionments − prior installments already paid.
>
> The `(-) Installments` row is ONLY for payments already made before this closing
> (e.g., a 1ª parcela paid months ago via bank transfer). If no prior payments exist,
> the Installments row stays EMPTY (D=0 or blank).
>
> The boleto (lien discharge), IPTU, and broker fees are NOT deducted from Balance Due.
> They are listed as separate "Total Amount due" lines in the beneficiary section below,
> and together they must sum to the Balance Due.
>
> Example: Balance Due = R$ 93.600,00 → broken into:
> - Total Amount due to Landlord: R$ 55.257,63
> - 1ª Parcela Boleto SICREDI: R$ 38.222,46
> - IPTU (APW pays on behalf of LL): R$ 119,91
> Sum = R$ 93.600,00 ✅

---

## Step 3 — Parse the ISW (if provided)

**Important:** ISW files often come as `.xlsb` (Binary Excel). Use `pyxlsb`, not openpyxl:

```bash
pip install pyxlsb --break-system-packages -q
python3 scripts/parse_isw.py "<path_to_isw.xlsb_or_xlsx>"
```

The `parse_isw.py` script handles both `.xlsb` and `.xlsx` automatically.

**Pro-ration logic (critical — always read from the contract):**

The pro-ration covers the months between signing and when the carrier updates its system
to pay APW directly. The formula:

```
Deal Completion Month = Last pro-ration month + 1
```

Examples:
- 2 months (Aug + Sep) → Deal Completion = **October**   (L1042188/ATC pattern)
- 3 months (Aug + Sep + Oct) → Deal Completion = **November**  (Solange/Highline pattern)

In the Excel pro-ration columns (J-P, row 5):
- **K** = first pro-ration month
- **L** = last pro-ration month (the one just before Deal Completion)
- **M** = Deal Completion month (= L + 1) — this is what goes in the "Deal Completion" column
- **N** = number of months
- **O** = monthly rent amount
- **P** = =O*N (total apportionment)

In the Rent Apportionments label (B12): list ALL months covered (e.g., "August, September, October").
In the Deduct cell (D12): negative total = -(N × monthly_rent).

Always derive from the contract clause — it will say something like:
"...pró-rata, constitui o tempo estimado... para a Locatária atualizar seu sistema interno..."
and list the specific months. Count them → N months → Deal Completion = last month + 1.

Key fields to extract from the ISW **Submission Sheet**:
- `Transaction Name` (row 4, col E) → L-number + landlord
- `Asset Type` + `Sub-Asset Type` (row 11) → tower type (monopole, lattice, etc.)
- `Transaction Type` (row 12, col E) → Surface Right / Assignment of Rents
- `Transaction Term` (row 13) → years
- `Site City, State` (row 15) → location
- **Key Notes** (row 12, col J) → deal narrative (use verbatim — it's already IC-approved text)
- **Carrier/tenant** (Submission Sheet, rows 31+): tenant name, monthly rent, escalator
- Projected closing costs (rows ~60-75): Title Work, Site Inspection, Third Party Fees,
  Recording Fees, Outside Legal Fees, Broker/Agent Fees, Rent Proration

---

## Step 4 — Identify all beneficiaries

Wire recipients depend on the deal structure. Common patterns:

| Beneficiary | When | Amount |
|-------------|------|--------|
| Landlord (LL) | Always | Balance Due (net installment after deductions) |
| Credor Alienação Fiduciária | When property has lien to discharge | Boleto amount |
| Broker / Intermediário (e.g., MyTower) | When deal had intermediary | Broker fee per agreement |
| Advogado do LL | When LL legal fee was agreed | Agreed amount |

**Broker handling — Nilton's standard (validated on 2 deals):**

The broker fee **always goes in the items table as D = −F** (nets to zero, same as closing
costs — does NOT affect Balance Due or the LL's payment). This is standard regardless of how
the broker is paid.

```
Intermediary / Broker Fee    [source]    D: -2.600,00    F: 2.600,00
```

The broker is then paid **via a separate APW document** — it does NOT appear as a "Total
Amount due" beneficiary block in the wire. There is no wire to the broker through this
Completion Statement.

If the user provides broker bank details, these go into the separate payment document — NOT
into a beneficiary wire block in this Completion Statement.

**Alienação Fiduciária / Boleto:**
- The 1ª parcela goes to the BANK (not the landlord) to discharge the lien
- It's recorded in `(-) Installments` in the Deduct column, reducing Balance Due
- Payment method: Boleto Bancário (not TED) — treasury needs the boleto attached
- The creditor's bank details may not be in the Closing Statement — ask or pull from contract

---

## Step 5 — Build the variance table

For each closing cost line item (excluding Purchase Price and Rent Apportionments):

| Cost Item | ISW Projected (R$) | Actual (R$) | Delta (R$) | Delta (%) | Status |
|-----------|-------------------|-------------|------------|-----------|--------|
| Title Search / Certidões + DD | proj | actual | delta | % | ✅/⚠️ |
| Notary / Escritura | | | | | |
| Recording / Registro + ITBI | | | | | |
| Legal Fees / Procuração + Diligências | | | | | |
| Site Owner Legal Fee | | | | | |
| Site Inspection / Vistoria | | | | | |
| Broker / Agent Fees | | | | | |
| **TOTAL** | total_proj | total_actual | delta | % | ✅/⚠️ |

Status: ✅ = on budget or <5% over; ⚠️ = >5% over budget

**Mapping ISW → actual costs** (actual costs often come from the legal team in a different
breakdown — map by category, not label):
- ISW "Title Work" → actual: Certidões + DD
- ISW "Recording Fees" → actual: Registro + ITBI + Escritura (notary deed)
- ISW "Third Party Fees" → actual: Procuração + Diligências + Levantamento Planialtimétrico
- ISW "Site Inspection" → actual: SIR/Vistoria
- ISW "Broker/Agent Fees" → actual: MyTower or other intermediary

Note: actual costs often don't match ISW categories 1:1. Group intelligently and document
the mapping in the email if there's a significant mismatch (especially if ⚠️).

---

## Step 6 — Generate the email

Email format (match Nilton's style exactly — clean text, no markdown):

---

**SUBJECT:** Request for Wire – [L-number] – [LANDLORD NAME] – [Deal Type]

Team,

We are about to sign [Surface Right Deed / Assignment of Rents Agreement / etc.] pertaining
to this transaction.

Expected Funding Date   [Weekday], [Month]/[DD]/[YYYY]

Final Closing Costs:

```
COMPLETION STATEMENT
AP WIRELESS BRASIL INVESTIMENTOS IMOBILIÁRIOS LTDA.
PURCHASE OF: [L-number]_[LANDLORD NAME]
CARRIER: [CARRIER / TENANT]

PROPOSED COMPLETION DATE: [Weekday], [Date]
LANDLORD: [LANDLORD NAME]
PURCHASING ENTITY: AP Wireless Brasil Investimentos Imobiliários Ltda.

ITEMS:                                                         Amount
──────────────────────────────────────────────────────────── ──────────────
Purchase Price / Valor Investimento                            R$ [amount]
(-) Rent Apportionments [months] (period)                    (R$ [amount])
(-) Installments – [describe: boleto + IPTU, etc.]           (R$ [amount])
[cost lines that net to zero are optional to show]
──────────────────────────────────────────────────────────── ──────────────
BALANCE DUE (to Landlord):                                    R$ [balance]
```

[DEAL NARRATIVE — 2-3 sentences. Pull verbatim from ISW Key Notes field when available.
Otherwise compose from deal data: tower type, carrier, location, coverage area, deal term.]

[If closing costs are available:]
All closing costs ([list items]) totaling R$ [X] were paid [outside of closing / included
below]. [If any ⚠️ item: brief explanation of overage.]

Once approved, funds should be directed to the following bank accounts:

[For each beneficiary — numbered block:]

[N] Total Amount due [to Landlord / 1ª Parcela / Broker Fee label]     R$ [AMOUNT]
    [Bank Details label]:

    Beneficiary:    [NAME]
    Bank:           [BANK NAME]
    Bank Code:      [CODE]
    Agency:         [AGENCY]
    Account:        [ACCOUNT]
    Tax ID:         [CPF/CNPJ]
    [Payment Method note if boleto: "Payment via boleto only — see attached"]

[If any checklist item is ⏳ PENDING, flag it here:]
⚠️ Pending before wire can be processed: [item]

If you have any questions, please let us know.

Best,
Lucas Minozzo
AP Wireless Brasil

---

## Step 7 — Generate the Excel Completion Statement

Generate the Excel file in Nilton's exact format. See `references/closing_statement_structure.md`
for the full layout spec (column widths, row heights, fonts, number formats, merge cells).

**Critical rules for the Excel:**

0. **ALWAYS build the Rent Apportionment panel in columns J–P (rows 3–4)** — TENANT / FROM /
   TO / DEAL COMPLETION / # MONTHS / RENT/MONTH / TOTAL, with `P4=N4*O4`. The "Rent
   Apportionments" line item's Deduct cell must be `=-P4` (never a hardcoded number). This
   panel is mandatory on every statement — omitting it is the most common formatting error.
   Set page setup to landscape + fit-to-width + print_area B1:P<last> so it fits one page wide.

0b. **A third-party slice of the Price (honorários/IPTU to a named beneficiary) is NOT a
   Deduct line.** It partitions the Balance Due into a second beneficiary block. Balance Due
   stays = Price − Apportionments + Ajuda; Beneficiary 1 = Balance − third_party; Beneficiary 2
   = third_party; TOTAL = Balance. Re-listing it as a Deduct double-counts and is WRONG.

1. **Always create a FRESH workbook** — never open and re-save an existing file (causes
   file-lock errors). Copy the Cod. Bancos sheet data row-by-row from the source example.

2. **Balance Due formula:** `=SUM(D21,F21)` where closing costs net to zero (D=-F for each
   cost line), so Balance Due = Purchase Price − Rent Apportionments − Installments − IPTU.
   This equals the LL wire amount only.

3. **Broker fee:** Always populate "Intermediary / Broker Fee" row in the items table with
   D = −[amount] and F = [amount] (nets to zero). Broker is NEVER a "Total Amount due"
   beneficiary block — it is paid via a separate APW document. Example: `D13=-2600 / F13=2600`.

4. **(-) Installments row:** Only put payments already made BEFORE this closing.
   If the deal has no prior installments, leave D20 empty. The boleto and IPTU are NOT
   installments — they are separate disbursements at closing.

5. **Boleto (Alienação Fiduciária) and IPTU:** These appear as separate "Total Amount due"
   lines in the beneficiary section (same column G, same red bold style), NOT in the
   items table. Each gets its own G=[amount]. The LL's G amount = D22 − boleto − IPTU.

6. **Filename:** `Closing Statement - [L-number] - [LANDLORD NAME] - [Deal Type].xlsx`
   (match Nilton's naming convention exactly — same pattern as the source example)

7. **Output path:** Save to `/sessions/sleepy-vigilant-clarke/[filename].xlsx` and
   then use `present_files` to deliver (it copies to outputs automatically).

---

## Important notes

- **Number formatting:** Brazilian standard → `.` for thousands, `,` for decimals
  (e.g., R$ 97.500,00). Negative amounts in parentheses: (R$ 3.900,00).

- **ISW .xlsb files:** Use `pyxlsb` library. Install if needed:
  `pip install pyxlsb --break-system-packages -q`

- **Deal narrative:** The ISW Key Notes field (Submission Sheet, row 12, col J) contains
  the IC-approved narrative — use it verbatim. It reads like:
  "Investment opportunity is a 30-year Surface Right Deed on a Highline monopole with
  4G TIM as tenant located in Barbosa Ferraz (PR). Site provides coverage to..."

- **Boleto attachment:** Always remind Lucas to attach the SICREDI/bank boleto when there's
  an alienação fiduciária — treasury can't process without it.

- **Multiple beneficiaries:** Show each as a numbered block. Total all wire amounts at the
  bottom: "TOTAL TO BE DISBURSED: R$ [sum]"

- **Formula cells returning None:** openpyxl `data_only=True` only returns cached values.
  If None, reconstruct: Balance Due = Purchase Price − Rent Apportionments − Installments.

- **Checklist:** Only flag PENDING items (blank status). Ok and N/A are omitted from email.

- **Closing costs paid outside of closing:** When the legal team sends actual costs separately
  (as a table), include a variance section comparing each line to ISW projections. If closing
  costs weren't paid at closing (paid directly as separate transactions), note this clearly.
