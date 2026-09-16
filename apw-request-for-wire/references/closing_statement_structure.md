# Closing Statement Excel Structure

Reference for understanding the "Closing Statement - Lxxxxxxx - LANDLORD - Deal Type.xlsx" file
that Nilton prepares from the signed minuta.

## Sheets

| Sheet | Purpose |
|-------|---------|
| Investment | Main completion statement — header, line items, bank details |
| Check List | RFW document checklist with status |
| Cod. Bancos | Bank code reference table (read-only reference) |
| Sheet1 | Usually empty |

---

## Investment Sheet Layout (1-indexed rows)

| Row | Col B | Col C | Col D | Col F | Col J–P |
|-----|-------|-------|-------|-------|---------|
| 1 | "COMPLETION STATEMENT" | | | | |
| 2 | Company name | | | | |
| 3 | "PURCHASE OF:" | L-number_LANDLORD | | | (tenant headers) |
| 4 | | | | | ATC, Aug, Sep, Oct, 2 months, R$1690/mo |
| 5 | "PROPOSED COMPLETION DATE:" | | Date | | |
| 6 | "LANDLORD:" | | | | |
| 7 | "PURCHASING ENTITY" | | Entity name | | |
| 8 | "ITEMS:" | "Source/Fonte" | "Deduct" | "Add" | |
| 9 | (currency labels) | | R$ | R$ | |
| 10 | Purchase Price | Lease M-files | (blank) | 145000 | |
| 11 | Rent Apportionments | Lease M-files | -3380 | (blank) | |
| 12 | Intermediary / Broker Fee | | | | |
| 13 | Title Search Charges / Certidões | link | -F14 | 3744.24 | |
| 14 | Local Notary Fees / Despesas Cartório | Link | -F15 | 300 | |
| 15 | Recording Fees / Custo de Registro | Link | -F16 | 13542.28 | |
| 16 | Legal Fees | Fixed Amount | -F17 | 3200 | |
| 17 | Site Owner Legal Fee / Auxílio Advogado | Director | | 0 | |
| 18 | Site Inspection | Link | -F19 | 2000 | |
| 19 | (-) Installments | | | | |
| 20 | Sub-total | | =SUM(D11:D20) | =SUM(F11:F20) | |
| 21 | BALANCE DUE: | | =SUM(D21,F21) | | |
| 22 | Total Amount due to Landlord at closing | | | | G22 = formula |
| 23 | Landlord Bank Details: | | | | |
| 24 | Beneficiary: | | [Name] | | |
| 25 | Bank: | | [Bank] | | |
| 26 | Bank Code: | | [Code] | | |
| 27 | Account: | | [Account] | | |
| 28 | Branch: | | [Branch] | | |
| 29 | Tax ID: | | [CPF/CNPJ] | | |
| 30 | Total Amount due to [2nd entity] | | | | G30 = amount |
| 31 | Landlord Bank Details: | | | | |
| ... | (same pattern repeats) | | | | |

### Column mapping

- **Col B (index 1)**: Row label / line item name
- **Col C (index 2)**: Source note (M-Files path, "link", "Fixed Amount", "Director", etc.)
- **Col D (index 3)**: DEDUCT amount (negative — money coming back from escrow / credit)
- **Col E (index 4)**: DEDUCT (VAT) — usually empty in Brazil
- **Col F (index 5)**: ADD amount (positive — money APW pays out)
- **Col G (index 6)**: ADD (VAT) / also used for "Total Amount due to [beneficiary]"
- **Cols J–P (indices 9–15)**: Pro-ration / apportionment data for tenant

### Formula behavior with openpyxl

When reading with `data_only=True`:
- Simple numeric cells → return float value ✅
- Formula cells that were last saved with Excel → return cached value ✅
- Formula cells from files never opened in Excel → return None ⚠️

For formula cells returning None, the script attempts reconstruction:
- First beneficiary amount ≈ balance_due − sum(other beneficiary amounts)
- Individual line items can often be read directly if they're hardcoded (not formulas)

---

## Check List Sheet Layout

| Col A | Col B | Col C |
|-------|-------|-------|
| Document description | Where to file in M-Files/Dropbox | Status (Ok / N/A / blank) |

Status values:
- **Ok** → document confirmed and filed
- **N/A** → not applicable to this deal type
- **blank** → still pending / to be confirmed before wire

---

## ISW (Investment Worksheet) Structure

The ISW is a separate Excel prepared at submission time. Its structure varies slightly
by deal vintage, but consistently contains:

- Purchase Price (Valor Investimento)
- Projected closing costs per line item
- Total investment

The `parse_isw.py` script scans all sheets and rows using keyword matching to find each
cost item regardless of layout variation. If the ISW format changes significantly, update
the `ITEM_KEYWORDS` dict in that script.

---

## Deal Types and Naming Convention

| Deal Type | Portuguese | Excel filename contains |
|-----------|-----------|------------------------|
| Surface Right Deed | Direito Real de Superfície (DRS) | "Surface Right" |
| Assignment of Rents | Cessão de Direitos Creditórios (CDC) | "Assignment" or "CDC" |
| Fee Simple (Compra e Venda) | Compra e Venda | "Fee Simple" or "Compra e Venda" |

---

## Wire recipients (beneficiaries)

A deal may have 1, 2, or 3 wire recipients:

1. **Landlord** — the main wire for the purchase price (less apportionments)
2. **Intermediary / Broker** — if a local broker was involved
3. **Lawyer / Advogado** — if the landlord's legal fee was separately agreed

Each has its own "Total Amount due to Landlord at closing" block + bank details.
Always verify total of all wires = BALANCE DUE on the statement.
