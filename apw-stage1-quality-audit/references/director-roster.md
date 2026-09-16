# Diretores Brasil — roster (GUID → nome)

Os 14 diretores de aquisição Brasil. GUIDs validados em produção (mesma lista do
`apw-reporte-crm-diario`). Qualquer owner fora desta lista é pool/sistema/outro e entra na
contagem de "pool", não de pessoa.

| GUID | Nome |
|---|---|
| 98e379bf-6d55-ed11-bba3-000d3a5a8269 | Bruna Matos |
| 70a07063-6fdf-e311-8265-00155d00fe04 | Jose Daniel Ramos |
| c336d752-e6fb-ed11-8849-000d3a5a8269 | Regina Silveira |
| b5ece3de-6c3c-ee11-bdf4-000d3a5a8e5c | Kamilla Rosa |
| 0f5c2d0c-d6d4-e911-a9a8-000d3a360ed5 | Felipe Porto |
| 342e4168-9660-e911-a997-000d3a360ed5 | Fabio Boturao |
| 2d3010fa-61f4-ed11-8848-000d3a5a82bf | Aline Sanzi |
| f41da072-58a6-ed11-aad1-000d3a5a8baa | Victoria Navarro |
| bd19844f-8b38-ee11-bdf4-6045bd095340 | Daiane dos Santos |
| cb48e1a0-4959-ee11-be6f-000d3a317ead | Gisele Tognolo |
| edbec271-d59d-ef11-8a6a-0022480985f3 | Andressa Bueno |
| bea2794a-97c3-ef11-b8e9-000d3a3355b9 | Roana Reboredo |
| d49fdec3-f849-ef11-a317-000d3a5be4ff | Carolina Brentzel |
| 06a1eeda-93d7-f011-8543-6045bd0a09fc | Aline Felix |

**Regex de pool/sistema** (owner cujo nome formatado casa = não-pessoa):
`/pool|apwreports|surrender|disqualified|system/i`

**Owner efetivo de um Stage 1:** o `ownerid` direto da opp; se for pool/sistema, cair para o
campo de owner do estágio (`_apwip_stage1owner_value`) quando existir — é quem de fato moveu
o S1. A coleta resolve isso e devolve o nome já normalizado.

> A lista muda quando entra/sai diretor. Se a coleta encontrar um owner-pessoa fora desta
> lista com cohort relevante, sinalize ao Lucas para atualizar o roster — não o jogue
> silenciosamente em "pool".
