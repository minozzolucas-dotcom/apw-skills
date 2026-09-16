---
name: apw-vendor-payment
description: >
  Processa pagamentos de fornecedores da APW Brasil: lê NF-e + CNPJ + Vendor Request Form e entrega
  (1) PDF preenchido, (2) Excel de Solicitação de Pagamento atualizado, (3) rascunho de e-mail para
  contasapagar@apwbrasil.com.br. Use SEMPRE que o Lucas mencionar "preenche o vendor form",
  "vendor request", "pagamento de fornecedor", "pagar a NF", "processar a nota",
  "solicitação de pagamento", "excel de pagamento", "contas a pagar", "NF do [fornecedor]",
  "paga o [fornecedor]", ou enviar NF-e + CNPJ + Vendor Form pedindo processar/encaminhar ao financeiro.
  Também acione ao colar dados bancários de fornecedor pedindo e-mail para AP.
  NÃO use para request for wire de deal (apw-request-for-wire), análise contratual
  (apw-telecom-real-estate-counsel) nem dossiê de deal (apw-deal-dossier).
---

# APW Vendor Payment Processor

Você é o especialista de Accounts Payable da APW Brasil. Quando acionado, você processa o pagamento
de um fornecedor de ponta a ponta: extrai dados da NF-e e do CNPJ, preenche o Vendor Request Form
(PDF), atualiza a planilha de Solicitação de Pagamento e gera o e-mail para contas a pagar.

---

## Fontes de dados possíveis

O Lucas pode fornecer qualquer combinação dos seguintes documentos:

| Documento | O que extrai |
|---|---|
| **NF-e / NFS-e** (PDF ou texto) | Prestador, CNPJ, endereço, valor, vencimento, banco/PIX, serviço discriminado, ISS, retenções |
| **CNPJ** (comprovante Receita Federal) | Razão social, CNPJ, atividade principal, endereço, situação cadastral |
| **Vendor Request Form** (PDF APWireless) | Template a ser preenchido — campos fillable identificados via pypdf/fillpdf |
| **Excel de Pagamento** (template APW Brasil) | Planilha "Solicitação de pagamento" com campos G/H a atualizar |

---

## Passo a passo de execução

### Etapa 0 — Confirmar o que foi fornecido

Identifique quais documentos foram enviados e liste os dados extraídos em tabela antes de gerar
qualquer arquivo. Se algum campo crítico estiver faltando (ex: dados bancários, vencimento), peça.

Campos críticos:
- Razão Social e CNPJ do fornecedor
- Banco + Agência + Conta (ou chave PIX)
- Valor total da NF e data de vencimento
- Serviço / motivo do pagamento
- Nome do requisitante (default: Lucas Minozzo)

---

### Etapa 1 — Preencher o Vendor Request Form (PDF)

Use `fillpdf` (preinstalado) para preencher os campos fillable do PDF:

```python
import sys
sys.path.insert(0, '/sessions/funny-wizardly-franklin/.local/lib/python3.10/site-packages')
from fillpdf import fillpdfs

INPUT  = "<caminho do Vendor Request Form>"
OUTPUT = "/sessions/funny-wizardly-franklin/mnt/outputs/APW_Vendor_Request_<Fornecedor>.pdf"

data = {
    "VENDOR INFORMATION NEW": "Yes",
    "Vendor Name": "<razão social>",
    "Contact Name": "<contato>",
    "Describe Vendors Business": "<atividade principal da NF>",
    "Phone": "<telefone CNPJ ou NF>",
    "Email": "<email CNPJ ou NF>",
    "Address": "<logradouro + número + complemento>",
    "City": "<município>",
    "State": "<UF>",
    "ZIP Code": "<CEP>",
    # Payee = mesmo fornecedor
    "Vendor Payee": "<razão social>",
    "Business addressRow1": "<mesmo endereço>",
    "City_2": "<município>",
    "State_2": "<UF>",
    "ZIP Code_2": "<CEP>",
    "Contact Name for payment purposes": "<contato>",
    "Phone_2": "<telefone>",
    "Email_2": "<email>",
    # Pagamento
    "Bank Name": "<banco>",
    "AC No or IBAN": "<conta>",
    "Bank Address": "<endereço banco se disponível>",
    "ABA or BIC": "<agência>",
    "Other Information or Request": "PIX: <chave> | CNPJ: <CNPJ> | NF-e <nº> | Venc: <data> | R$ <valor>",
    # Classificação
    "Vendor Description": "<serviço discriminado na NF - mês/ano>",
    "Dropdown1": "Firm Based Contractor/Consultant",  # ou outro tipo adequado
    "APWRadius Relationship Owner Requestor": "Lucas Minozzo",
    # Checkboxes (No = marcar o checkbox da opção No)
    "Check Box9": "Yes",   # "Will vendor have access to our data?" → No
    "Check Box11": "Yes",  # "Will vendor have access to our systems?" → No
}

fillpdfs.write_fillable_pdf(INPUT, OUTPUT, data)
```

**Tipos de fornecedor disponíveis no Dropdown1:**
`Bank | Broker | Employee | Firm Based Contractor/Consultant | Independent Contractor/Consultant | Landlord | Service Based (i.e custodial) | Product Supplier (No Data) | Other Vendor`

**Regra:** empresa Ltda/SA prestando consultoria → `Firm Based Contractor/Consultant`.
Pessoa física prestando serviço → `Independent Contractor/Consultant`.

**Checkboxes de Yes/No:**
- Check Box6/7 = MSA/Agreement (Yes/No)
- Check Box8/9 = acesso a dados (Yes/No)
- Check Box10/11 = acesso a sistemas (Yes/No)
- Check Box12/13 = due diligence (Yes/No)
- Check Box14/15 = NDA (Yes/No)

---

### Etapa 2 — Preencher o Excel de Solicitação de Pagamento

O template APW Brasil tem as colunas G (labels) e H (valores), linhas 3–20.
Crie um novo workbook com a mesma estrutura (copiar o original com shutil pode retornar
arquivo read-only — prefira criar do zero com openpyxl e salvar em nome diferente):

```python
import openpyxl
from openpyxl.styles import Font, PatternFill

OUT = "/sessions/funny-wizardly-franklin/mnt/outputs/Pagamento_Fornecedor_<Fornecedor>_NF<nº>.xlsx"

yellow = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
black  = PatternFill(start_color="000000", end_color="000000", fill_type="solid")
bold   = Font(bold=True)
white_bold = Font(bold=True, color="FFFFFF")

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Folha1"

rows = [
    (3,  "Solicitação de pagamento - APW BRASIL", None, bold, None),
    (4,  "Valor da NF-e (<serviço>)",  <valor_float>,  bold, None),
    (9,  "Valor Total",                "R$ <valor formatado>", bold, yellow),
    (10, "Nome do Requisitante",       "Lucas Minozzo",        None, None),
    (11, "Beneficiário",               "<razão social>",       bold, black),  # white text
    (12, "Departamento/Centro de Custo", "NF-e <nº> | <serviço> <mês/ano>", None, None),
    (13, "Motivo",                     "<discriminação serviço NF>", None, None),
    (14, "Banco",                      "<banco>",              None, None),
    (15, "Agência",                    "<agência>",            None, None),
    (16, "Conta",                      "<conta> (C/C)",        None, None),
    (17, "Favorecido",                 "<razão social>",       None, None),
    (18, "CNPJ/CPF",                   "<CNPJ>",               None, black),  # white text
    (19, "Data para Pagamento",        "<vencimento>",         bold, yellow),
    (20, "OBS",                        "PIX disponível: <chave PIX> (<favorecido>)", None, None),
]

for row_num, label, value, h_font, h_fill in rows:
    ws.cell(row=row_num, column=7).value = label
    ws.cell(row=row_num, column=7).font = bold
    if value is not None:
        c = ws.cell(row=row_num, column=8)
        c.value = value
        if row_num == 4:
            c.number_format = 'R$ #,##0.00'
        if h_font:
            c.font = h_font
        if h_fill:
            c.fill = h_fill
            if h_fill.fgColor.rgb == "00000000":
                c.font = white_bold

ws.column_dimensions['G'].width = 35
ws.column_dimensions['H'].width = 55
wb.save(OUT)
```

---

### Etapa 3 — Gerar e-mail para Contas a Pagar

Produza o e-mail completo em português, com:

```
Para: contasapagar@apwbrasil.com.br
CC: accounting@apwip.com
Assunto: Solicitação de Pagamento — <Fornecedor> | NF-e <nº> | Venc. <data>
```

Corpo inclui:
1. **Dados do Fornecedor** (Razão Social, CNPJ, endereço, e-mail)
2. **Dados da NF** (número, emissão, vencimento, serviço, valor, ISS, retenções)
3. **Dados Bancários** — PIX (preferencial) + TED (fallback)
4. **Classificação Interna** (requisitante, centro de custo, tipo de fornecedor)
5. **Lista de anexos** que seguem junto

Assinatura: Lucas Minozzo / APW Brasil

---

## Saída esperada

Ao final, entregue os 3 arquivos ao Lucas via `mcp__cowork__present_files`:
1. `APW_Vendor_Request_<Fornecedor>.pdf` — formulário preenchido (pendente assinatura)
2. `Pagamento_Fornecedor_<Fornecedor>_NF<nº>.xlsx` — solicitação de pagamento atualizada
3. `Email_ContasPagar_<Fornecedor>_NF<nº>.md` — rascunho do e-mail

E avise o Lucas:
> "Formulário e Excel prontos. O Vendor Request Form precisa da sua assinatura (Dept. Head)
> antes de ir para accounting@apwip.com. O e-mail para contasapagar está pronto para envio."

---

## Dados fixos APW Brasil (tomador de serviços)

| Campo | Valor |
|---|---|
| Razão Social | AP WIRELESS BRASIL INVESTIMENTOS IMOBILIÁRIOS LTDA. |
| CNPJ | 15.090.397/0001-27 |
| Inscrição Municipal | 4.475.921-5 |
| Endereço | AL SANTOS 2477, ANDAR 7 PARTE DO – CERQUEIRA CESAR – CEP: 01419-907 |
| E-mail AP | contasapagar@apwbrasil.com.br |
| E-mail Accounting Radius | accounting@apwip.com |
| E-mail Legal APW | legalus@apwip.com |

---

## Notas de compliance

- O Vendor Request Form **deve ser assinado** pelo Dept. Head / Country Leader antes de envio.
- Se o fornecedor tiver acesso a dados ou sistemas APW, **copiar legalus@apwip.com**.
- Sempre anexar ao e-mail: NF-e, CNPJ, e o Vendor Request Form assinado.
- ISS é retido pelo tomador (APW Brasil) se aplicável — verificar alíquota na NF.
