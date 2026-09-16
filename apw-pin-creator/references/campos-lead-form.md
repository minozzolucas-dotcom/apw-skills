# Campos do formulário "New Lead" (leadsearch2.aspx)

Mapa dos campos do form, agrupados como aparecem na tela. Use para montar a tabela do passo 4.

## Lead Source
- **Lead Source** — dropdown. De onde veio o lead. **Não invente** — proponha o que fizer sentido e peça ao Lucas selecionar.

## Site Information
- **Street** — logradouro do site. Em site rural, costuma ser a referência de rodovia + km.
- **Street 2 / Street 3** — complemento. Normalmente vazios.
- **Neighborhood** — bairro / distrito / localidade.
- **City** — município.
- **State/Province** — UF (dropdown).
- **Zip/Postal Code** — CEP.
- **Country** — país (dropdown). Default Brazil — o form já abre assim.
- **Latitude / Longitude** — coordenadas. Vêm do farejador (passo 3) com o nível de confiança.
- **Property Type** — dropdown. Tipo do imóvel (terreno/land, rooftop, greenfield, etc.). **Não invente** — proponha e peça ao Lucas selecionar. As opções do dropdown só são conhecidas inspecionando a página; se precisar, leia as opções no passo 6 e mostre ao Lucas.

## Contact Information
A pessoa aqui é o **locador/proprietário** do terreno (não a operadora).
- **First Name** / **Last Name** — nome do proprietário, separado.
- **Entity** — pessoa jurídica, se o proprietário for PJ. Para proprietário PF, vazio.
- **E-Mail** — e-mail do proprietário (às vezes está na cláusula de Correspondências do contrato).
- **Business Phone / Home Phone / Mobile Phone** — telefones, se houver.

## Mailing Information
Endereço de correspondência do proprietário — costuma estar no preâmbulo do contrato (endereço residencial do locador).
- **Mailing Street / City / State / Zip Code / Country**.

## Notes
- **Subject** — título curto e identificável. Padrão sugerido: `<código do site> — <referência>`. Ex.: `TT0081 — Site Cacimba Nova`.
- **Description** — resumo objetivo do contrato: partes (locador e locatária), aluguel mensal, índice de reajuste, prazo, matrícula, e **red flags** (divergência de município, ônus, cláusula restritiva). É o campo que dá contexto pra quem pegar o Lead depois.

## Ação final
- **Create Lead** — botão que cria o registro. A skill só "clica" nele (via Web API) depois da confirmação do Lucas no passo 5.

## Regras de preenchimento
- Campo sem fonte no documento → fica **vazio**. Nunca preencha por suposição.
- Os dois dropdowns de conteúdo (`Lead Source`, `Property Type`) → sempre decisão do Lucas.
- `Country` → Brazil por default.
- `Latitude`/`Longitude` → sempre acompanhados do nível de confiança do farejador.
