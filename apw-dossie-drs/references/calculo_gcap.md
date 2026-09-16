# Cálculo do ganho de capital — alienação de DRS por PF

## Fórmula geral
```
Ganho bruto = Valor da alienação − Custo de aquisição
Ganho tributável = Ganho bruto × (1 − redutor Lei 7.713) × FR1 × FR2
IR = 15% × Ganho tributável   (até R$ 5 mi; acima, tabela progressiva Lei 13.259/16: 17,5% / 20% / 22,5%)
```

## Redutor Lei 7.713/88, art. 18 (imóveis adquiridos até 31/12/1988)
5% por ano de aquisição anterior a 1989, contando de 1988 para trás:
aquisição em 1988 = 5%; 1987 = 10%; ... 1969 ou antes = 100% (ganho zerado).

## Fatores de redução Lei 11.196/05, art. 40 (aplicam após o redutor acima)
- **FR1** = 1 / 1,0060^m1 — m1 = nº de meses entre jan/1996 (ou a aquisição, se posterior) e nov/2005
- **FR2** = 1 / 1,0035^m2 — m2 = nº de meses entre dez/2005 (ou a aquisição, se posterior) e o mês da alienação
- Imóvel adquirido após nov/2005: só FR2 se aplica.
- O GCAP calcula automaticamente; a simulação manual deve reproduzir essa lógica e ser rotulada como estimativa.

## Exemplo de sanidade (validado)
Aquisição mai/2006, alienação 2025 por R$ 1.115.000, custo R$ 0:
m2 ≈ 228 meses → FR2 ≈ 1/1,0035^228 ≈ 0,451 → redução ≈ 35% do ganho... conferir sempre no GCAP; no material usar os números redondos da simulação com a ressalva.

## Pontos de atenção
- **Custo de aquisição do DRS**: quando o direito nasce da propriedade original sem destaque de custo, prática corrente = custo R$ 0,00 (cenário conservador, IR máximo). Se o proprietário tiver custo declarado do imóvel, discutir com contador se cabe proporcionalização — não prometer no material.
- **Casal**: se o imóvel é do casal, cada cônjuge apura 50% (dois DARFs). Relevante quando há dois locadores PF.
- **Prazo de pagamento do DARF**: último dia útil do mês seguinte ao recebimento (código 4600).
- **Parcelado**: ganho proporcional a cada parcela recebida.
- **Isenções (NÃO prometer)**: imóvel único até R$ 440 mil (art. 23 Lei 9.250/95) e reinvestimento em residencial em 180 dias (art. 39 Lei 11.196/05) foram desenhadas para venda de imóvel residencial; enquadramento de DRS é controverso — listar apenas como tese a validar com o contador.
