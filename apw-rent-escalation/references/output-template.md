# Output Template — Rent Escalation Quadro

## Formato mínimo (sempre sai)

```markdown
## [Código L ou identificador do site] — [Nome do locador], [Cidade/UF]

**Rent escalation vigente:**

| Camada | Valor / Conteúdo | Fonte |
|---|---|---|
| Valor mensal atual | R$ X.XXX,XX (desde [mês/ano]) | [Aditivo N], Cláusula [X], item [Y.Z] |
| Índice de reajuste | [IPC-FIPE / IGP-M / IPCA / INPC] | [Aditivo M], Cláusula [X], item [Y.Z] |
| Data-base do reajuste | [mês escrito por extenso] 1º (anual) | [Aditivo N], Cláusula [X], item [Y.Z] |
| Frequência | Anual | (idem) |

**Cadeia de aditivos:**

| # | Data assinatura | Locatária | Valor fixado | Índice introduzido | Data-base | Observação |
|---|---|---|---|---|---|---|
| Contrato original | DD/MM/AAAA | [Operadora] | R$ XXX,XX | [Índice] | [Mês] | [obs] |
| 1º Aditivo | DD/MM/AAAA | [Operadora] | R$ XXX,XX | [Índice ou "mantido"] | [Mês] | [obs] |
| ... | | | | | | |
| Aditivo vigente | DD/MM/AAAA | [Locatária atual] | R$ X.XXX,XX | [Índice ou "mantido por ratificação"] | [Mês] | **EM VIGOR** |

**Trechos citados (PT + EN):**

> **[Aditivo N], Cláusula [X], item [Y.Z] — original:**
> "[trecho exato em português]"
>
> **English:**
> "[tradução com mês escrito por extenso quando houver ambiguidade]"

[Repetir bloco para cada cláusula relevante]

**Pontos de atenção:**
- [Listar conflitos, lacunas, premissas adotadas, valores que não batem com índice puro, etc.]
```

## Exemplo preenchido — L1045166 (caso real Helio Akira Suzuki)

```markdown
## L1045166 — Helio Akira Suzuki, Jacareí/SP

**Rent escalation vigente:**

| Camada | Valor / Conteúdo | Fonte |
|---|---|---|
| Valor mensal atual | R$ 4.100,00 (desde junho/2016) | 4º Aditivo (ATC, 01/03/2016), Cláusula II, item 2.1 |
| Índice de reajuste | IPC-FIPE | Aditivo VIVO (25/05/2009), item 5.2, mantido por ratificação |
| Data-base do reajuste | Dezembro 1º (anual) | 4º Aditivo (ATC), Cláusula II, item 2.1 |
| Frequência | Anual (variação 12 meses) | 3º Aditivo (Telefônica, 15/12/2011), Cláusula IV, item 4.2 |

**Cadeia de aditivos:**

| # | Data assinatura | Locatária | Valor fixado | Índice introduzido | Data-base | Observação |
|---|---|---|---|---|---|---|
| Contrato original | 01/11/1998 | Telesp Celular | R$ 300,00 | Média IGP-M / IGP-DI | — | — |
| 1º Aditivo | 21/06/2005 | Telesp Celular | R$ 2.170,00 (jun/2005) | IGP-M/FGV | Junho 1º | Eficácia em 01/06/2005 |
| Aditivo VIVO | 25/05/2009 | VIVO S/A | R$ 2.518,50 (jun/2008) | **IPC-Fipe** (mudou) | Junho 1º | Renegociação cheia |
| 3º Aditivo | 15/12/2011 | Telefônica/VIVO | R$ 3.255,31 (jan/2012) | IPC-FIPE (mantido) | Junho 1º | Reajuste 12 meses |
| **4º Aditivo** | **01/03/2016** | **ATC** (cessão VIVO→ATC em 30/03/2012) | **R$ 4.100,00 (jun/2016)** | **Mantido por ratificação** | **Dezembro 1º (MUDOU)** | **EM VIGOR** |

**Trechos citados (PT + EN):**

> **4º Aditivo (ATC), Cláusula II, item 2.1 — original:**
> "A partir de 01.06.2016, o aluguel mensal sofrerá uma majoração passando a viger pela importância de R$ 4.100,00 (Quatro mil e cem reais). A data base para reajuste é 01/12/2016 e assim sucessivamente."
>
> **English:**
> "As of June 1st, 2016, the monthly rent shall be increased to R$ 4,100.00 (four thousand one hundred reais). The base date for adjustment is December 1st, 2016 and so on thereafter."

> **4º Aditivo (ATC), Cláusula de Ratificação Final — original:**
> "Ficam ratificadas todas as demais cláusulas e condições do Contrato que não foram aqui expressamente alteradas."
>
> **English:**
> "All other clauses and conditions of the Contract not expressly amended herein are hereby ratified."

> **3º Aditivo (Telefônica, 15/12/2011), Cláusula IV, item 4.2 — original:**
> "A partir de (01/06/2012) o valor do aluguel será reajustado com base no IPC-FIPE, calculado de acordo com a variação do referido índice nos últimos 12 (doze) meses."
>
> **English:**
> "As of June 1st, 2012, the rent shall be adjusted based on the IPC-FIPE index, calculated according to the variation of said index over the last twelve (12) months."

> **Aditivo VIVO (25/05/2009), Cláusula 5, item 5.2 — original:**
> "A partir de 01/06/2009, o valor do aluguel será reajustado com base na variação do IPC-Fipe, calculada entre o primeiro mês do período de reajuste considerado e o primeiro mês do período de reajuste seguinte."
>
> **English:**
> "As of June 1st, 2009, the rent shall be adjusted based on the variation of the IPC-Fipe index, calculated between the first month of the relevant adjustment period and the first month of the following adjustment period."

**Pontos de atenção:**
- O 4º Aditivo (ATC, 2016) **alterou a data-base** de junho para **dezembro**, mas **não restabeleceu o índice**. IPC-FIPE permanece vigente por força da cláusula de ratificação, com lastro nos itens 5.2 (Aditivo VIVO/2009) e 4.2 (3º Aditivo/2011).
- A diferença entre "data-base de reajuste (dezembro)" e "mês em que o valor reajustado aparece na competência (geralmente janeiro)" se deve ao lag de divulgação do IPC-FIPE — não é um regime de reajuste diferente.
- Cada aditivo da cadeia fixou valor cheio renegociado; não é possível reconstruir o histórico aplicando índice puro de 1998 em diante.
- Cessão VIVO→ATC ocorrida em 30/03/2012, formalmente incorporada ao contrato no 4º Aditivo de 2016.
```
