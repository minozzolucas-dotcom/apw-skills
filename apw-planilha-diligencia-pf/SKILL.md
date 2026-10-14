---
name: apw-planilha-diligencia-pf
description: Gera a Planilha de Diligência de Pessoa Física da APW Brasil (as 4 abas padrão — Condições Contratuais, CUSTAS, Diligência Interna PF, Andamento Processual) preenchida com os dados de um deal APW, pronta pra encaminhar ao jurídico interno (Michelle/Anderson/Márcia Sena).
---

# apw-planilha-diligencia-pf

Automatiza o preenchimento da **Planilha de Diligência - Pessoa Física** que a APW Brasil envia ao jurídico interno no handoff de Stage 7 → Stage 8 de deals com vendedor PF.

## Quando usar

Acione SEMPRE que o Lucas pedir:

- "cria a planilha de diligência do L#####"
- "preenche a planilha de diligência PF"
- "monta a planilha pro jurídico"
- "planilha de condições contratuais do L#####"
- "planilha pra DD do deal"

NÃO use pra:
- Submission/IC em inglês → apw-submission-writer / apw-stage7-sub
- Pré-DD registral de documento bruto → apw-pre-dd-legal
- Deal com vendedor PJ (template diferente)

## Estrutura do template (4 abas + 1 vazia)

### Aba 1 — Condições Contratuais

Header (linha 1):
- B1: Lnumber/ Deal: L##### [nomes dos vendedores]
- C1: Diretor: [nome]
- D1: Cidade/UF: [cidade]/[UF]

Bloco Condições negociadas (linhas 5-13):
- C5 Valor do Investimento (número puro)
- C6 Forma de Pagamento (A vista, Parcelado)
- C7 Participação em renegociações (sim/não)
- C8 Participação em novas receitas (sim/não)
- C9 Prazo (ex: 30, Definitivo - Propriedade Plena)
- C10 Tipo de Transação (DRS, Cessão de Créditos, Compra e Venda do Imóvel)
- C12 Pagamento Advogado (SIM/NÃO)
- C13 Forma de pagamento advogado (Pago ao cliente, N/A)

Bloco Informações Contrato de Locação (linhas 15-17):
- C15 Operadora(s) — se torreira ≠ operadora, explicitar os dois
- C16 Aluguel Atual (POP) — string formato BR
- C17 Aluguel corrigido

Célula de contexto do reajuste (merged B18:D24):
- B18 nota explicando reajuste. Se CONGELADO, ser explícito: cláusula, até quando, próximo reajuste real

Bloco Informações adicionais (linhas 26-30, cada uma merged C#:D#):
- B26-B30 até 5 observações densas. Priorizar nesta ordem:
  1. Particularidades fiscais do vendedor (ex: Lei 11.196/2005 art. 39)
  2. Regime matrimonial se 2 vendedores + split do wire
  3. Origem do domínio se não-trivial (usucapião, inventário, doação)
  4. Status do direito de preferência (torreira notificada?)
  5. Comissões externas (MyTower, broker)

### Aba 2 — CUSTAS

Linha 4: resumo (B4 descritivo, C4 payout, D4 IRR, E4 threshold 0.25%, F4 fórmula)
Linhas 5-16: itens com valores NEGATIVOS
C17 tem SUM pronto — NÃO MEXER

Itens padrão (negativos): SIR, DD, Jurídico, ITBI (2% se C&V), Escritura, Registro RGI, Certidões, Comissão broker, Correios

### Aba 3 — Diligência Interna - PF

Linhas 3-13: checklist 11 docs. Coluna D (merged D#:E#) recebe status:
- OK - [detalhes] se coletado
- aguardando se pendente
- N/A se não aplicável

Linha 15: A15 observações do Diretor (contexto estratégico). A15 NÃO é merged.

Linhas 18-30: coluna E (observações) com jurisdições:
- E19 CND Receita Federal
- E22 Justiça Federal (nomear TRF)
- E27 Pesquisa Cível (nomear comarcas)
- E28 TJ 2ª Instância
- E29 Trabalhistas (TRTs)

### Aba 4 — Andamento Processual

Só se tem processo relevante. Linha 2: A2 nº CNJ, B2 cidade/UF, C2 vara, D2 requerente, E2 requerido, F2 valor causa, G2 último estágio, H2 observações (dizer se é BASE DOMINIAL), I2 tipo de ação

### Aba 5 — CÁLCULO EXATO

MANTIDA VAZIA.

## Mecânica (Python/openpyxl)

Template em assets/template.xlsx DENTRO da skill:

```python
from openpyxl import load_workbook
import shutil
from pathlib import Path

TEMPLATE = Path(__file__).parent / "assets" / "template.xlsx"
OUT = f"/mnt/user-data/outputs/Planilha_Diligencia_PF_{lnumber}_{cidade}_{vendedor}.xlsx"

shutil.copy(TEMPLATE, OUT)
wb = load_workbook(OUT)
# escrever só em células TOP-LEFT de cada merge
wb.save(OUT)
```

## Pegadinhas de merge (DECORADAS — testadas em L1044259)

Aba Diligência Interna - PF:
- D3:E3 a D13:E13 → escrever em D#
- F2:L2 a F13:L13 → pré-DD jurídico (deixar vazio)
- A16:L16 header
- A22:A26, A27:A28, A29:A30 labels agrupados
- C22:C24, D22:D24, E22:L24 Justiça Federal → escrever em E22
- E17:L17 a E30:L30 observações → escrever em E##
- A15 NÃO é merged — escrever direto

Aba Condições Contratuais:
- B2:D2 header
- B14:D14 subheader
- B18:D24 nota reajuste → escrever em B18
- B25:D25 subheader
- C26:D26 a C30:D30 observações → escrever em B26...B30 (B fica fora do merge)

Se escrever em MergedCell que não é top-left: AttributeError: MergedCell object attribute value is read-only.

## Entregável

Path: /mnt/user-data/outputs/Planilha_Diligencia_PF_L[#####]_[Cidade]_[Vendedor].xlsx

Depois de salvar, enviar com SendUserFile + resumo de 4-6 bullets por aba.

## Fontes de dados a cruzar

1. Dossiê memória (/areas/apw-[deal].md)
2. Matrícula (nº, cartório, oficial, selo, confrontantes)
3. IPTU/CND Municipal (inscrição, valor venal, código CND)
4. POPs (datas, bancos, formato)
5. Certidão de casamento (regime)
6. Contratos e aditivos (torreira, cláusulas reajuste/preferência)
7. Calculator .xlsb (valor final, IRR)
8. Notificação torreira (telegrama, prazo decaído?)
9. Anatel via apw-erb-towerco-triage (operadora real, tenancy)

Se faltar dado crítico, PERGUNTAR — não inventar.

## Comportamento esperado

- PRESERVAR template (shutil.copy + load_workbook + wb.save)
- Nunca escrever em MergedCell não-top-left
- Antes de preencher, DECLARAR o que vai colocar
- Valores em reais: vírgula decimal como string ou número puro para fórmula
- Observações DENSAS, não genéricas
- Depois de entregar, oferecer UMA próxima ação lógica
