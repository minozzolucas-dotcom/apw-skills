# H1-2026 — ciclo semestral oficial UKG

Primeiro ciclo real da skill repivotada pra semestral (commit 3a105e0 de
22/10/2026).

## Diretores rodados

| Diretor | Regime | Pipeline H1 | Business H1 (S8+S99+Rent) | Nota final |
|---|---|---|---|:---:|
| Fabio Boturao | Sr Experiente | 70/110 (64%) | S8 3/6 · S99 1/5 · Rent R$58k/R$320k (29% consolidado) | 1 Needs Improvement (1,47) |
| Felipe Porto | Sr Experiente | 58/110 (53%) | S8 3/6 · S99 3/5 · Rent R$177k/R$320k (55% consolidado) | 1 Needs Improvement (1,42) |

## Harvest

Pacote único rodado em 22/10/2026 via snippet único no console do Dynamics
(seção "Como rodar — H1-2026" do README da skill). Pacote baixado:
`apw_qpr_harvest_FABFEL_2026-10-22.json` com 4 seções:
- `pace` ✅ (todos os stages, time inteiro agregado por owner × mês)
- `rent` ❌ (null — nenhum dos 7 campos candidatos existe no tenant;
  fallback: dados do PBI oficial copiados manualmente do dashboard)
- `activities` ✅ (filtrado Fabio+Felipe no server)
- `keynotes` ❌ (field name `new_keynotes` provavelmente errado no tenant;
  rodar discovery antes de confiar nessa seção)

## TODO antes do H2-2026

1. **Descobrir campo real de Rent Acquired** — rodar discovery snippet
   (listado no histórico do chat), gravar o nome correto no CSV
   `data/rent_pbi_oficial_YYYY-MM-DD.csv` e atualizar a lista `CANDIDATOS`
   em `references/1_harvest_rent_acquired.js`
2. **Descobrir campo real de Key Notes** — mesmo discovery, atualizar o
   `$select` do snippet 3 em `references/3_harvest_keynotes_sample.js`
3. **Capturar snapshot do pace-score em 31/dez/2026** — pra ter base limpa
   de H2 sem contaminação de atividade pós-ciclo (quando rodar o H2 em
   jan/2027)

## Framework de tom (aprendizado deste ciclo)

- Honesto mas construtivo, com números concretos
- Separar "atitude" (frequentemente forte) de "excellence" (resultado
  consistente, ainda em construção)
- Pontos de melhoria enquadrados como refinamento técnico, não mudança de
  atitude
- Overall sempre encerra com um ativo real do diretor + direção pro
  próximo ciclo
