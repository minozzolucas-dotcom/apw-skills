# Índices de Reajuste em Contratos Telecom BR — Quick Reference

## Índices mais comuns em cadeias APW

| Índice | Divulgação | Fonte | Quando aparece em contratos APW |
|---|---|---|---|
| **IGP-M** | Fim do mês de referência (~28-30) | FGV | Contratos antigos (anos 1990-início 2000s); foi o índice "default" de aluguel até virar tóxico em 2020-2022 (deflator de commodities) |
| **IGP-DI** | Início do mês seguinte | FGV | Variação do IGP-M; raro em contratos novos |
| **IPC-Fipe / IPC-FIPE** | Quadrissemanal (4 vezes por mês) + fechamento ~10 dias após fim do mês | FIPE/USP | Migração natural de contratos VIVO/Telefônica nos anos 2009-2012, fugindo do IGP-M |
| **IPCA** | Em torno do dia 10 do mês seguinte | IBGE | Padrão atual em contratos novos pós-2020; também índice de Tesouro IPCA+ |
| **INPC** | Em torno do dia 10 do mês seguinte | IBGE | Pouco usado em telecom; mais comum em pensões e revisões salariais |

## Sequência típica em cadeias antigas (anos 1990-2025)

Contratos originais dos anos 1990 → IGP-M ou média IGP-M/IGP-DI
↓
Aditivos de 2009-2012 → migração para **IPC-FIPE** (movimento setorial das operadoras fugindo do IGP-M)
↓
Aditivos pós-2015 com cessão para towerco (ATC, SBA, IHS) → costuma **manter o índice** anterior por ratificação, mas pode mover data-base
↓
Contratos novos pós-2020 ou novações → IPCA

## Lag entre data-base e cobrança

| Índice | Data-base contratual | Mês típico em que aparece o reajuste no extrato |
|---|---|---|
| IGP-M | Dezembro 1º | Janeiro (IGP-M de dez fecha em ~30/12) |
| IPC-FIPE | Dezembro 1º | Janeiro (IPC-FIPE de dez fecha ~10/01) |
| IPCA | Dezembro 1º | Fevereiro (IPCA de dez sai em ~10/01, mas se a cobrança usa "12 meses contados até dez", o índice só está disponível mês seguinte) |

**Importante:** o "mês de cobrança" não muda a data-base contratual. Sempre registrar a data-base como ela aparece no contrato e explicar o lag separadamente.

## Tipos de cláusula de reajuste

1. **"Calculado conforme variação dos últimos 12 meses"** — acumulado anual; é o padrão. O índice de referência é o IPC-FIPE/IPCA/IGP-M acumulado dos 12 meses anteriores à data-base.

2. **"Calculado entre o primeiro mês do período considerado e o primeiro mês do período seguinte"** — fraseado da Cláusula 5.2 do Aditivo VIVO de 2009. Significa a mesma coisa que (1) na prática, mas é redação mais ambígua. Sempre interpretar como acumulado 12 meses.

3. **"Pro rata temporis"** — proporcional ao tempo decorrido. Raro em telecom.

4. **"Sem reajuste durante o prazo X"** — congelamento. Verificar se foi removido em aditivo posterior.

## Substituição de índice (cláusula de salvaguarda)

Muitos contratos preveem que **se o índice contratual for extinto** ou substituído por lei, prevalece o substituto legal ou outro índice acordado. Exemplo do contrato VIVO 2009:

> "Na hipótese de extinção do índice supra mencionado, prevalecerá o índice que tenha substituído legalmente, admitindo-se outro critério de reajustamento de valores locatícios que vier a ser fixado por lei ou autoridade administrativa competente."

Isso é importante porque o IGP-M já está num movimento de queda de uso institucional, e em algum momento pode haver pressão para migrar para IPCA.

## Periodicidade legal mínima

A Lei do Inquilinato (Lei 8.245/91) estabelece que aluguel só pode ser reajustado **anualmente**, salvo lei superveniente. Cláusulas como a 5.4 do Aditivo VIVO de 2009 mencionam justamente essa salvaguarda:

> "Se lei subseqüente vier a permitir atualização do valor locatício em periodicidade inferior à prevista na legislação em vigor, concordam as Partes que o valor do aluguel passará a ser atualizado na periodicidade autorizada pela nova lei, desde que não seja inferior a 6 (seis) meses."
