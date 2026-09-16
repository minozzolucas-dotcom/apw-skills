# Extração de dados do contrato

Guia para o passo 2 do workflow. O objetivo é tirar dos documentos exatamente o que o formulário "New Lead" precisa — nada mais.

## O que cada parte do contrato significa

Contratos de site de telecom no Brasil seguem um padrão. Os papéis:

- **LOCADOR / CEDENTE / PROPRIETÁRIO** — dono do terreno. É **esta** parte que vira o *Contact* do Lead (First Name, Last Name, Entity, telefone, e-mail). Pode ser pessoa física (agricultor, com cônjuge co-proprietário) ou pessoa jurídica.
- **LOCATÁRIA** — quem instala/opera a torre. Normalmente uma torreira (SBA, American Tower, IHS, Telecom Torres, Highline...) ou uma operadora (Vivo, Claro, TIM, Oi). **Não** vira o Contact — vira contexto (vai no Description, ajuda a identificar quem paga o aluguel).

Se o contrato tiver dois locadores (casal), o Contact principal é normalmente o primeiro nomeado; cite o cônjuge no Description.

## Campos a extrair

### Identificação do site
- **Código do site** — procure no cabeçalho/rodapé do contrato e no nome do arquivo. Padrões: `TT0081`, `CE_CCN`, `MS00052`, `RS CZA11 3519-25`. Vira parte do Subject.
- **Município e UF** — da cláusula "Descrição do Imóvel".
- **Bairro / distrito / localidade** — pode estar no contrato, no alvará, ou no endereço dos proprietários.
- **Referência de acesso** — rodovia, km, "sentido tal". Geralmente está mais clara no **alvará** que no contrato.
- **Área locada** — em m². Cuidado: contratos rurais antigos usam "braças". 1 braça ≈ 2,2 m², mas normalmente o próprio contrato converte ("200 m²").
- **Matrícula e ofício/cartório de registro** — ex.: "matrícula 4.987 no 2º Ofício".

### Partes
- **Locador**: nome completo, e separe em First Name / Last Name para o form. CPF — anote para contexto, mas não precisa ir pro form. Endereço residencial — pode servir como Mailing Address.
- **Locatária**: razão social e CNPJ. Só para o Description.

### Comercial
- **Aluguel mensal** — valor em R$.
- **Índice de reajuste** — IGP-M, IPCA, etc.
- **Prazo** — anos, data de início, regras de renovação.

### Red flags — sempre destacar no Description e na revisão
- Divergência de município entre documentos.
- Cláusula restritiva: anti-cessão, anti-alienação, exclusividade telecom, direito de preferência. (Se for relevante para a decisão de deal, sugira ao Lucas acionar a `apw-telecom-real-estate-counsel` — mas não faça a análise jurídica aqui.)
- Ônus, gravame ou pendência registral mencionada.
- Contrato antigo sem aditivo — o aluguel pode estar muito defasado.

## Princípio

Extraia o que está escrito. Se um campo não está no documento, ele fica vazio — não preencha por dedução. "Provavelmente é X" não vai pro CRM; vira pergunta pro Lucas.
