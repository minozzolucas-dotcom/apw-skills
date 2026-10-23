---
name: apw-request-for-wire
description: Gera o Closing Statement (Excel no padrão exato do Nilton) + o e-mail "Request for Wire" para a tesouraria/UW da Radius em San Diego, a partir da pasta de closing de um deal APW Brasil (custas do jurídico, contrato/minuta/aditivo, planilha de pagamento/provisionamento, ISW). Use quando o Lucas pedir "closing statement", "request for wire", "RFW", "pedido de wire", "monta o closing", "completion statement", ou mandar a pasta/arquivos de fechamento de um L. Cobre Cessão, DRS, Fee Simple, Cessão+DRS, parcelados, pagamento condicionado ao registro, CAPEX TBSA, broker, IPTU, advogado e terceiros como beneficiários.
---

# APW Request for Wire — Closing Statement + e-mail RFW

**Produto:** 1) `Closing Statement - <L> - <Nome> - <Tipo>.xlsx` idêntico ao do Nilton; 2) corpo do e-mail RFW (HTML) + assunto/destinatários.
**Princípio:** o layout é SEMPRE o mesmo. Nunca construir planilha do zero — preencher o template (`references/closing_template.xlsx`, closing real do Nilton com variáveis limpas) via `scripts/fill_closing.py`. A versão antiga desta skill gerava layout próprio, custas da ISW e fórmulas sem valor — tudo isso é proibido.

Base empírica: 85 closings reais jan–out/2026. Arquétipos e regras abaixo foram validados reproduzindo closings do Nilton centavo a centavo.

---

## 1. Fontes — hierarquia (quem manda em caso de conflito)

| Dado | Fonte que manda | Nunca usar |
|---|---|---|
| Preço, pró-rata (meses e valor), auxílio advogado, forma de pagamento, parcelas e datas, terceiros pagos (broker do LL, IPTU, advogado), conta bancária | **Contrato mais recente** (aditivo > minuta "atualizada/limpa/final" > minuta; arquivos em `Old/` são histórico) | ISW, e-mail antigo |
| Custas (linhas 14–17, 19) | **Tabela de custas do jurídico** — a **primeira** tabela do thread (a mais recente); "Custas atualizadas/Corrigidas" > "Custas" | ISW (é projeção) |
| Dados bancários quando o contrato só diz "chave PIX"/"vide cláusula" | Planilha de Pagamento/Provisionamento (fora de `Old/`) ou Vendor Request Form | — |
| Key Notes (narrativa do e-mail) | ISW, Submission Sheet, Key Notes (`scripts/parse_isw.py`) — verbatim | — |
| Código L / nome | Nome da pasta / CRM | Código no nome de anexo (já veio L errado, já aconteceu) |
| CAPEX TBSA | ISW linha "Other – Capex/TBSA Contribution" (se divergir do valor que o Lucas informar, perguntar) | — |

**Regra de ouro das custas:** somar os ITENS da tabela você mesmo. A linha "Saldo" do jurídico errou 5× em 10 meses (L962411, L943649, L1265019, L1108371, L1011589). O auxílio advogado vem do **contrato**, não da custas (L975597: custas listava R$2k de auxílio, contrato não tinha → F18 = 0).

---

## 2. Workflow

1. **Inventário da pasta.** Listar arquivos; ignorar `Old/`; identificar contrato mais recente, custas mais recente, planilha de pagamento, ISW. Contrato em .docx → python-docx; PDF → pdftotext; PDF-imagem (pdftotext vazio) → ler visualmente.
2. **Extrair** (seção 3) e **classificar o arquétipo** (seção 4).
3. **Montar `deal.json`** (schema em `references/deal_schema.md`; exemplos reais em `references/examples/`).
4. **Rodar:** `python3 scripts/fill_closing.py deal.json --out <pasta-saída>`
5. **Ler a VALIDAÇÃO.** 🔴 = não entregar sem resolver. 🟡 = entregar com o alerta explícito no chat.
6. **Conferir visualmente** (LibreOffice → PDF → PNG) antes de entregar.
7. **Entregar:** xlsx + HTML do e-mail + header (assunto/To/Cc). No chat: Balance Due, valor ao LL, demais beneficiários, alertas, e o que ficou `[a confirmar]`.

Perguntar só o que não estiver nos documentos (ex.: Expected Funding Date se o e-mail de custas não trouxer "Data estimada para pagamento"; "Please note" com condições especiais).

---

## 3. Mapa de células (aba Investment) — fixo

| Célula | Conteúdo | Fonte / regra |
|---|---|---|
| C4 | `<L>_<Nome>` | pasta/CRM |
| D6 | Proposed Completion Date (datetime) | "Data estimada para pagamento" do e-mail de custas |
| J5 | Tenant = **quem paga o aluguel**: torreira (ATC, SBA, Torres do Brasil, Highline, IHS, Z-Sites, Winity) ou a operadora direta (TIM, Claro, Telefonica/VIVO); pode ser "Highline / TIM" | contrato |
| K5 / L5 / M5 | 1º mês pró-rata / último mês / Deal Completion (= último + 1), em inglês | cláusula do pró-rata (b) |
| N5 / O5 / P5 | nº meses (1 a 4) / aluguel mensal (item 12 do Quadro Resumo, do contrato MAIS RECENTE) / `=O5*N5` | contrato |
| B12 / D12 | "Rent Apportionments" + meses listados / `=-P5` | sem pró-rata: K–M "-", N5=O5=0, D12=0 |
| F11 | Preço (aceita centavos; deal combinado: `=34000+34000`) | item 5 do Quadro Resumo |
| B13/F13/D13 | "CAPEX Contribution" (TBSA) **ou** "Intermediary / Broker Fee" (broker da APW) | ver seção 5 |
| F14 Title | Manancial, Certidões, Levantamento Planialtimétrico/Georref., TopSat | custas |
| F15 Notary | Rec. Firmas, Procuração, Traslado, Diligências, Agrimensor, e-notariado | custas |
| F16 Recording | ITBI + Escritura + Registro(s) CDT/comarca + Emolumentos/Averbação — como **fórmula com os componentes** (`=2224.03+6118.11`) | custas |
| F17 Legal | o "DD" da custas (3.200 é o comum; já foi 4.800, 5.300, 2.000, 0) | custas |
| F18 | Auxílio advogado — **só F, sem D** (vai para o LL) | contrato (item 6 / cl. 1.3 ou 3.2) |
| F19 | SIR (2.000 comum; já foi 3.000) | custas |
| D14–D17, D19 | `=-F` (custas netam zero; são pagas por fora) | — |

Linha combinada na custas ("Certidões/Diligências" R$3.500) → pode dividir `=3500/2` entre F14 e F15 ou pôr inteira numa linha — só o total importa. **Teste: F14+F15+F16+F17+F19 = soma dos itens da custas sem a linha de auxílio.**

Linha 20 em diante é gerada pelo script: [linhas de sinal já pago] → `(-) Installments` → Sub-total → BALANCE DUE (`=SUM(Dsub,Fsub)`) → blocos de pagamento.

**BALANCE DUE = tudo que a APW desembolsa NESTE closing** = Preço − Pró-rata + Auxílio − Sinal já pago − Parcelas futuras (+ broker APW pago no wire). A soma dos blocos "Total Amount due…" (sem as parcelas futuras) tem que ser igual ao Balance Due — o script valida.

---

## 4. Arquétipos (todos cobertos pelo script)

| # | Arquétipo | Como fica | Exemplo |
|---|---|---|---|
| A | Cessão / DRS / Fee Simple à vista | G(LL) = `F11+D12+F18` | `examples/A_*.json` |
| B | TBSA com CAPEX | linha 13 CAPEX (D=−F); resto igual A | L922851, L932401 |
| C | **Parcelado** (DRS ou Cessão; 2 a 15 parcelas; semestral ou anual) | `first_payment` = 1ª parcela; cronograma "Nº Installment payment due until MM/DD/YYYY" (datas **literais do contrato**); D(Installments) = `−SUM(cronograma)`; G(LL) = `<1ª>+D12+F18` | `B_C_tbsa_capex_parcelado_15x.json`, L1256398, L968107, L975597 |
| D | **2º pagamento condicionado ao registro** | linha "2º payment conditioned to Public Deed Registration, date uncertain but expected between X to Y days" (prazo copiado do contrato). Se há `first_payment` → não desconta do LL (`carve_from_landlord:false`); se não há → desconta | `D_cessao_drs_pagto_condicionado.json`, L929595, L1264288, L884023, L923086 |
| E | **Sinal já pago** antes do closing | linha extra antes de Installments ("Payment in advance (Month YYYY)"), D negativo; entra somado na fórmula do LL | `E_sinal_pago_material_tecnico_2LL.json` |
| F | **Beneficiários múltiplos** (Balance Due não muda, só é repartido) | bloco próprio por terceiro; G(LL) subtrai cada um | `F_iptu_broker_LL_advogado.json`, L1265019 (4 beneficiários) |

Tipo no nome do arquivo/assunto vem do **contrato**: Cessão → `Assignment of Rents`; DRS → `Surface Right`; C&V/Promessa C&V → `Fee Simple Interest`; Cessão + DRS → `Credit Assignment and Surface Right`. (L975486 saiu "Surface Right" sendo Cessão — erro a não repetir.)

---

## 5. Beneficiários e terceiros — tabela de decisão

| Situação (gatilho no contrato) | Tratamento |
|---|---|
| Auxílio "na conta indicada no item 8" | F18, vai junto com o LL, sem bloco |
| Auxílio "será pago na seguinte conta bancária:" (advogado) | F18 + bloco próprio, C = "2K Site Owner Legal Fee" (ou valor), desconta do LL |
| Alínea "c)/d) … será pago para a conta … em nome de [TERCEIRO]" (ex.: **Integra Energia** — broker do LL) | bloco próprio, desconta do LL; se metade é pós-registro, a 2ª metade vira `extra_lines` condicionada |
| IPTU em atraso quitado pela APW (cl. 3.1/3.3: "desconto… débitos de IPTU") | linha anexa ao LL "According 3.x of Surface Right - APW will pay the property tax (IPTU)", desconta do LL (boleto) |
| Material técnico / outro adiantamento a abater (aditivo) | linha anexa ao LL, desconta do LL |
| **Broker da APW** pago por Vendor Form separado (MyTower etc.) | linha 13, D=−F, **sem bloco** |
| **Broker da APW** pago no próprio wire (contrato de intermediação APW, ex. L1068138) | linha 13 **F sem D** + bloco "Total Amount due to Broker at closing" com `carve_from_landlord:false` → Balance Due inclui o broker (padrão corrigido pela UW no L1068138; ver `C_parcelado_broker_apw_no_wire.json`) |
| Fornecedor (TopSat, Prefeitura/ITBI) | é custa: entra em F14/F16 netado; pago por Vendor Form; sem bloco |
| Conta em nome de outra pessoa (cônjuge, filho anuente, administradora, conta de um bloco em condomínio de vários blocos (L367571)) | D(Beneficiary) = titular da conta conforme item 8 / dados bancários, mesmo ≠ LL |
| Dois proprietários 50/50 | dois blocos bancários com nota "50% of each payment" |
| Só PIX | repetir a chave nos campos sem dado |

---

## 6. E-mail RFW (formato que vai para o time todo)

**Assunto:** `Request for Wire - <L> - <Nome> - <Tipo>`
**To:** Paulina Guerrero; Juan Carlos Martinez; Ryan Eppel; Luiz Alfredo; Fabiana Siviero
**Cc:** Scott Langeland; Dan Hasselman; Esteban Castrejon; Eric Pape; Michelle Carvalho; Marcelina Silva; Lucas Minozzo; Daniel Presson; Guglielmo Noya; Marnique Richards-Ouellette; Diogo Bueno; Douglas Alves; Gracia Serrano; Daniel Romagnolo
(endereços completos no `header.txt` gerado)

Corpo (o script gera em HTML, pronto para colar no Outlook):
```
Team,

We are about to sign **<Tipo>** pertaining to this transaction.

Expected Funding Date  <Weekday>, <Month>/<DD>/<YYYY>   ← negrito, vermelho, sublinhado, marca-texto amarelo

Final Closing Costs:
[tabela = faixa B2:G22 do Excel: cabeçalho, itens, Sub-total, BALANCE DUE]

**<Key Notes da ISW, verbatim>**

Please note:                      ← só se houver condição especial
- **<ex.: APW has agreed to pay R$407 (approximately $80 USD, indexed annually) for annual property taxes.>**

Once approved, funds should be directed to the following bank accounts:   ← vermelho, negrito
[tabela = blocos de pagamento do Excel: valores e dados bancários]

If you have any questions, please let us know.
```
No Outlook, o ideal é colar as faixas do próprio Excel (como o Nilton faz); o HTML é o equivalente pronto. Sem bloco "Notes", sem "TOTAL TO BE DISBURSED", sem "Payment Method" — não existem no padrão.

---

## 7. Checklist antes de entregar (o script cobre os itens marcados com *)

- [ ] * Soma dos blocos = Balance Due; valor ao LL > 0
- [ ] * Custas F14:F17+F19 = itens da tabela (sem auxílio); divergência do "Saldo" do jurídico sinalizada
- [ ] Auxílio = contrato (não custas)
- [ ] Pró-rata: meses e aluguel do contrato mais recente; Deal Completion = último mês + 1
- [ ] * Datas das parcelas em ordem, sem ano absurdo (já houve "05/22/2038"); copiadas do contrato
- [ ] * D6 próximo de hoje (já houve D6 com ano 2023 e datas velhas de anexo)
- [ ] Beneficiário/conta = item 8 do contrato (ou planilha de pagamento fora de `Old/`)
- [ ] Tipo do arquivo coerente com o contrato
- [ ] Bank Code conferido na aba "Cod. Bancos" (bancos raros: 070 BRB, 085 Ailos/Unilos, 003 Amazônia, 481 Superlógica, 748 Sicredi, 756 Sicoob)

## 8. Decisões em aberto (defaults até o Lucas dizer o contrário)
- Datas das parcelas: **literais do contrato** (a UW às vezes reescreve para dia 20 do mês seguinte — ela ajusta se quiser).
- D6 em DRS: data estimada informada pelo jurídico.
- CAPEX TBSA divergente entre ISW e informação do time: perguntar.
