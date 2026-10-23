# Closing Statement — estrutura real do template do Nilton

Validado em 85 closings jan–out/2026. Abas: `Investment`, `Sheet1` (vazia), `Check List`, `Cod. Bancos` (274 bancos).

## Investment — linhas fixas

| Linha | B | C | D | F | Painel J–P |
|---|---|---|---|---|---|
| 2 | COMPLETION STATEMENT (merge B2:G2) | | | | J2 "Apportionments/Pro-rations" |
| 3 | AP WIRELESS BRASIL INVESTIMENTOS IMOBILIÁRIOS LTDA. (B3:G3) | | | | |
| 4 | PURCHASE OF: | `L_Nome` (C4:G4) | | | J4:P4 cabeçalhos: Tenant · Rent Due (Month of Reference) · Due Month · Deal Completion · Months · Rent Per Month · Apportionment Due |
| 5 | CARRIER (vazio) | | | | **J5:P5 valores**, P5 `=O5*N5` |
| 6 | PROPOSED COMPLETION DATE: | | data (D6:G6, formato dia-da-semana) | | |
| 7 | LANDLORD: (vazio) | | | | |
| 8 | PURCHASING ENTITY | | AP Wireless Brasil Investimentos Imobiliario | | |
| 9–10 | ITEMS / Source/Fonte / Deduct / Deduct (VAT) / Add / ADD (VAT) / R$ | | | | |
| 11 | Purchase Price / Valor Investimento | Lease M-files | | preço | |
| 12 | Rent Apportionments + meses | Lease M-files | −pró-rata | | |
| 13 | Intermediary / Broker Fee **ou** CAPEX Contribution | | `=-F13` | valor | |
| 14 | Title Search Charges/Certidões/Documentos/Correio | link | `=-F14` | | |
| 15 | Local Notary Fees/ Despesas com Cartório (s) | Link | `=-F15` | | |
| 16 | Recording Fees/ Custo de Registro | Link | `=-F16` | `=a+b+c` | |
| 17 | Legal Fees | Fixed Amount | `=-F17` | DD | |
| 18 | Site Owner Legal Fee/ Auxílio Advogado | Director | (vazio) | auxílio | |
| 19 | Site Inspection | Link | `=-F19` | SIR | O19 "TOTAL", P19 `=SUM(P5:P18)` |
| 20 | (-) Installments | | `=-SUM(G..)` | | |
| 21 | Sub-total | | `=SUM(D11:D20)` | `=SUM(F11:F20)` | |
| 22 | BALANCE DUE: | | `=SUM(D21,F21)` (D22:G22) | | |
| 24 | Total Amount due to Landlord at closing (C24:F24) | | | | G24 fórmula do LL |
| 25 | Landlord Bank Details: | | | | |
| 26–31 | Beneficiary / Bank / Bank Code / Account / Branch / Tax ID (D:G merge) | | | | |

Com sinal já pago (L1277302), entra uma linha antes de Installments e tudo de 20 para baixo desce 1.
Linhas anexas ao LL (IPTU, condicionado, parcelas) ficam entre G24 e "Landlord Bank Details"; outros beneficiários vêm depois do bloco bancário do LL, cada um com linha de valor + bloco bancário.

Estilo: rótulos dos blocos de pagamento em vermelho (FFFF0000), valor G em vermelho negrito `R$`; células variáveis do painel em vermelho.
