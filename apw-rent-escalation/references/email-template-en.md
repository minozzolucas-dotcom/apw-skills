# Email Template — Rent Escalation Summary (English, for San Diego / Radius)

Use este template SOMENTE quando o Lucas pedir explicitamente para gerar email/comunicação em inglês para a equipe de underwriting (Paulina e San Diego), investidores Radius, ou comitê de investimento.

## Princípios

1. **Mês sempre escrito por extenso** quando houver risco de confusão (June 1st, December 1st — never 01/06 or 06/01).
2. Tom direto, factual, sem floreios. O leitor é underwriting/IC, não cliente.
3. Subject line traz o código L + tipo de operação.
4. Estrutura: contexto curto → quadro → trechos contratuais → pontos de atenção.
5. Não repetir conclusões do quadro no corpo do texto — o quadro é o entregável.

## Template

```
Subject: [L-code] — Rent Escalation Summary — [Counterparty] / [City, State]

Hi [Paulina / team],

Following up on the chain of amendments for [L-code], here is the consolidated rent escalation in effect today:

**Current rent escalation:**

| Layer | Value | Source |
|---|---|---|
| Current monthly rent | R$ X,XXX.XX (since [Month] 1st, YYYY) | [Amendment N], Clause [X], item [Y.Z] |
| Adjustment index | [IPC-FIPE / IGP-M / IPCA] | [Amendment M], item [Y.Z] |
| Reset date (anniversary) | [Month written out] 1st (annual) | [Amendment N], item [Y.Z] |

**Amendment chain:**

| # | Signed | Tenant | Rent fixed | Index | Reset date |
|---|---|---|---|---|---|
| Original | DD-MMM-YYYY | [Operator] | R$ XXX.XX | [Index] | — |
| 1st Amendment | DD-MMM-YYYY | [Operator] | R$ XXX.XX | [Index] | [Month] 1st |
| ... | | | | | |
| **[Current] Amendment** | **DD-MMM-YYYY** | **[Current tenant]** | **R$ X,XXX.XX** | **[Index]** | **[Month] 1st** |

**Key contractual excerpts:**

> [Amendment N], Clause [X], item [Y.Z]:
> "[English translation, with month written out]"

> [Amendment M], item [Y.Z] (index — carried over by ratification):
> "[English translation, with month written out]"

**Points of attention:**
- [Conflicts between amendments, gaps, renegotiated values vs. pure index escalation, cession events, etc.]

Let me know if you want me to run the gross-up (gross/net with IR withholding) at any specific reference date.

Best,
Lucas
```

## Exemplo preenchido — L1045166

```
Subject: L1045166 — Rent Escalation Summary — Helio Akira Suzuki / Jacareí, SP

Hi Paulina,

Following up on the chain of amendments for L1045166, here is the consolidated rent escalation in effect today:

**Current rent escalation:**

| Layer | Value | Source |
|---|---|---|
| Current monthly rent | R$ 4,100.00 (since June 1st, 2016) | 4th Amendment (ATC, signed March 1st, 2016), Clause II, item 2.1 |
| Adjustment index | IPC-FIPE | VIVO Amendment (May 25th, 2009), item 5.2 — carried over by ratification |
| Reset date (anniversary) | December 1st (annual) | 4th Amendment, Clause II, item 2.1 |

**Amendment chain:**

| # | Signed | Tenant | Rent fixed | Index | Reset date |
|---|---|---|---|---|---|
| Original | Nov-1st-1998 | Telesp Celular | R$ 300.00 | IGP-M / IGP-DI average | — |
| 1st Amendment | Jun-21st-2005 | Telesp Celular | R$ 2,170.00 (Jun-2005) | IGP-M/FGV | June 1st |
| VIVO Amendment | May-25th-2009 | VIVO S/A | R$ 2,518.50 (Jun-2008) | IPC-FIPE (changed) | June 1st |
| 3rd Amendment | Dec-15th-2011 | Telefônica/VIVO | R$ 3,255.31 (Jan-2012) | IPC-FIPE (kept) | June 1st |
| **4th Amendment** | **Mar-1st-2016** | **ATC** (cession VIVO→ATC, Mar-30th-2012) | **R$ 4,100.00 (Jun-2016)** | **Kept by ratification** | **December 1st (changed)** |

**Key contractual excerpts:**

> 4th Amendment (ATC), Clause II, item 2.1:
> "As of June 1st, 2016, the monthly rent shall be increased to R$ 4,100.00 (four thousand one hundred reais). The base date for adjustment is December 1st, 2016 and so on thereafter."

> 3rd Amendment (Telefônica, December 15th, 2011), Clause IV, item 4.2 (index — carried over by ratification):
> "As of June 1st, 2012, the rent shall be adjusted based on the IPC-FIPE index, calculated according to the variation of said index over the last twelve (12) months."

> 4th Amendment, Final Ratification Clause:
> "All other clauses and conditions of the Contract not expressly amended herein are hereby ratified."

**Points of attention:**
- The 4th Amendment (ATC, 2016) **moved the reset date from June to December** but did NOT restate the index. IPC-FIPE remains in force through the ratification clause, anchored on the VIVO Amendment (2009) and the 3rd Amendment (2011).
- Each amendment in the chain set a fully renegotiated rent figure, so the escalation is not reconstructable by applying the index alone from 1998 forward.
- Cession from VIVO to ATC took place on March 30th, 2012, and was formally incorporated into the contract via the 4th Amendment in 2016.

Let me know if you want me to run the gross-up (gross/net with IR withholding) at any specific reference date.

Best,
Lucas
```
