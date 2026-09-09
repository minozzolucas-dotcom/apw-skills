# APW Brasil — Skills CRM

Scripts e instruções para o Reporte Diário e Calor do Dia da Diretoria de Aquisições APW Brasil.

## Estrutura

```
apw-reporte-crm-diario/
  SKILL.md                    — instruções e regras de negócio
  references/
    build_report.py           — build HTML + PNG (14 diretores, formato oficial)
    collection_snippet.js     — snippet F12 pra coleta no Dynamics 365
    
apw-calor-do-dia/
  SKILL.md                    — instruções e regras de negócio
  references/                 — build_calor.py e collect_calor.js (restaurar via Claude)
```

## Como usar

1. Abrir aba autenticada em `https://apwireless.crm.dynamics.com`
2. F12 → Console → colar `collection_snippet.js` → Enter → baixa `reporte_YYYY-MM-DD.json`
3. `python3 build_report.py reporte_YYYY-MM-DD.json ./saida YYYY-MM-DD`
4. Entregar HTML (Outlook) + PNG

## 14 Diretores ativos (atualizado 25/08/2026)

| GUID | Nome |
|---|---|
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
| 8e616ea9-8d8a-f111-ab0f-70a8a5b0fc4c | Marcia Mangiulli |
