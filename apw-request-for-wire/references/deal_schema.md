# deal.json — schema do `fill_closing.py`

Exemplos em `examples/` — valores de closings reais que reproduzem o Nilton centavo a centavo; nomes e dados bancários anonimizados:
`A_cessao_a_vista` · `A_drs_a_vista_please_note` · `B_C_tbsa_capex_parcelado_15x` · `C_parcelado_broker_apw_no_wire` · `D_cessao_drs_pagto_condicionado` · `E_sinal_pago_material_tecnico_2LL` · `F_iptu_broker_LL_advogado`.

```jsonc
{
  "l_code": "L0000000",                // da pasta/CRM (código O também vale)
  "name": "Nome do Deal",
  "deal_type": "Surface Right",        // Assignment of Rents | Surface Right | Fee Simple Interest | Credit Assignment and Surface Right
  "completion_date": "2026-04-30",     // D6
  "funding_date": "2026-04-30",        // opcional (e-mail); default = completion_date
  "tenant": "Torres do Brasil",        // J5

  "prorata": {"from": "May", "to": "August", "completion": "September", "months": 4, "rent": 2520.47},
                                       // null se o contrato não tem pró-rata. "label" opcional sobrescreve os meses do B12
  "price": 200000,                     // ou lista [34000, 34000] → =34000+34000
  "row13": {"kind": "capex", "amount": 35000},              // ou {"kind":"broker","amount":..,"paid_in_wire":true}
  "costs": {                           // número ou lista de componentes (vira fórmula =a+b+c)
    "title": 900, "notary": 400, "recording": [4000, 3400.86, 1100],
    "legal": 3200, "site_inspection": 2000
  },
  "custas_items": [2000, 3200, 4000, 3400.86, 1100, 900, 400],  // itens da tabela do jurídico SEM o auxílio → validação
  "custas_saldo_juridico": 15000.86,   // opcional: o "Saldo" que veio no e-mail (só p/ alertar divergência)
  "legal_aid": {"amount": 1000},       // F18, do CONTRATO

  "first_payment": 16666.62,           // só se parcelado/condicionado: valor da 1ª parcela (sem pró-rata/auxílio)
  "advance_payments": [{"label": "Payment in advance (August 2025)", "amount": 6000}],
  "installments": [{"label": "2º Installment payment due until 05/20/2026", "amount": 16666.67}],

  "ll_attached_lines": [               // linhas logo abaixo do LL, sem banco
    {"label": "According 3.3 of Surface Right - APW will pay the property tax (IPTU)", "amount": 7367.05},
    {"label": "2º payment conditioned to Public Deed Registration, date uncertain but expected between 60 to 180 days",
     "amount": 34000, "carve_from_landlord": false}   // false quando existe first_payment
  ],
  "landlord_bank": {"beneficiary": "...", "bank": "...", "bank_code": 41, "account": "...", "branch": "...", "tax_id": "..."},
                                       // ou lista de blocos; "note": "50% of each payment"
  "other_payees": [                    // advogado, broker do LL, broker APW no wire
    {"label": "Total Amount due at closing", "c_label": "Site Owner Legal Fee/ Auxílio Advogado", "amount": 1000,
     "bank": {...}, "carve_from_landlord": true,       // false p/ broker APW pago no wire
     "extra_lines": [{"label": "2º payment to Broker conditioned to ...", "amount": 17100}]}
  ],

  "key_notes": "Investment opportunity is a ...",     // ISW verbatim
  "please_note": ["APW has agreed to pay R$407 ..."], // opcional
  "checklist": {"Procuração": "Ok", "Recibo ADV": "N/A"}  // opcional: casa por substring na aba Check List
}
```

Fórmula gerada para o LL (padrão Nilton):
`G(LL) = <first_payment ou F11> + D12 + F18 + D(sinal…) − G(linhas anexas com carve) − G(outros com carve)`
