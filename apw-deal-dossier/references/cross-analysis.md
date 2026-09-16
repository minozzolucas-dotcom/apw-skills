# Cross-Analysis — cruzar CRM + email num diagnóstico

Leia no Passo 3. Aqui está o catálogo de padrões a caçar quando você tem CRM, atividades e thread de email na mão ao mesmo tempo.

## A pergunta que organiza tudo

Antes de escrever o dossiê, responda mentalmente: **por que esse caso chegou ao Lucas?**

Quase nunca é "só pra saber". É porque alguém (asset manager, advogado, torreira) bateu num ponto que precisa de decisão. O dossiê inteiro existe para isolar esse ponto e dar ao Lucas o que ele precisa pra decidir. A seção 7 (próximo passo) é a entrega — as outras seis a sustentam.

## Tipos de divergência (seção 3 — o achado mais valioso)

Divergência = duas fontes afirmam coisas diferentes sobre o mesmo fato. É frequentemente *a razão* pela qual o caso travou. Os tipos recorrentes na APW:

### Divergência sistema interno × contraparte
Um sistema da APW (ISW, CRM, Rolling Forecast) registra uma condição; a contraparte (SBA, ATC, IHS, operadora) afirma outra.
- **Exemplo real (L1256097):** a SBA afirma que o acordo entre as matrizes previa redução do aluguel pra R$6k **e** isenção de reajuste em 2026. A ISW não prevê a isenção. Isso é uma divergência que **trava a assinatura do aditivo** — a APW não pode redigir o item "a" sem decidir de qual lado fica.
- Implicação típica: alguém tem que validar qual versão é a correta (achar o acordo de matrizes, consultar quem negociou) antes de qualquer documento ser assinado.

### Divergência de dado cadastral
Endereço, dados bancários, nome do proprietário diferem entre contrato, CRM e o que a contraparte tem.
- **Exemplo real (L1256097):** dados bancários — o CRM/contrato indicava Bradesco (1º termo aditivo de 01/01/2023); a SBA pediu pra usar Caixa Econômica. Resolve-se atualizando o cadastro, mas **bloqueia o pagamento do aluguel** até alinhar.
- Implicação típica: baixo risco estratégico, mas trava operação (pagamento, cobrança) — sinalize como 🟡.

### Divergência de valor
Aluguel declarado de memória ≠ calculado ≠ o que está no contrato físico. Preço proposto que mudou ao longo da thread sem o CRM acompanhar.

### Divergência de prazo / vigência
Data de início de competência, mês de reajuste, prazo do DRS divergem entre fontes.
- **Exemplo real (L1256097):** aluguel "efetivo a partir da competência ABRIL/2026, pago em MAIO/2026" — competência e pagamento são meses diferentes; confundir os dois gera erro de cobrança.

### Divergência stage CRM × realidade operacional
O CRM diz "fechado/Stage 99" mas os emails mostram pendência ativa (aditivo não assinado, reajuste não acordado, dado bancário errado). **O stage do CRM pode mentir** — o diagnóstico vem do cruzamento.

> Regra: quando achar uma divergência, **não concilie em silêncio**. Exiba as duas versões com a fonte de cada uma e a implicação. Se a divergência também é risco, cite-a de novo na seção 6.

## Vocabulário de risco telecom (seção 6)

Sinais que, se aparecerem no CRM ou nos emails, viram ponto de atenção:

| Sinal no texto | Risco | Severidade default |
|---|---|---|
| atraso / inadimplência de aluguel | receita | 🔴 |
| "retiraram equipamento" / "retirada de equipamentos" | site pode estar sendo descomissionado | 🔴 |
| "descomissionamento" / "site desativado" | perda do site | 🔴 |
| dados bancários incorretos / desatualizados | pagamento travado | 🟡 |
| aditivo / termo não assinado há meses | deal não se consolida | 🟡 |
| reajuste em disputa | valor do contrato indefinido | 🟡 |
| contraparte "sem resposta" / silêncio longo | deal esfriando | 🟡 |
| prazo de vigência curto / vencendo | renovação necessária | 🟡 |
| anuência de operadora pendente | cessão pode não valer | 🟡 |
| divergência resolvida / condição acordada | — | 🟢 |

## Mapa de papéis típico (seção 4)

Identifique a organização de cada pessoa pelo domínio do email e pelo cargo na assinatura:

**Lado APW Brasil** (`@apwbrasil.com.br`):
- **Asset Manager** (I, II, III) — gestão operacional do site/contrato. Quem toca o dia a dia (Marcelina, Adalton no caso L1256097).
- **Advogado / Legal** — minutas, aditivos.
- **Lucas / Diogo Bueno** — frequentemente acionados como escalão de decisão ("podem ajudar?").

**Lado APW US / PM** (`@apwip.com`):
- **PMBrazil / Project Management** — em cópia, acompanha.

**Lado contraparte — torreira** (`@sbasite.com` = SBA, e equivalentes para ATC, IHS, American Tower):
- **Attorney / Advogado** da torreira — conduz a negociação do aditivo do lado deles (Julio Fagundes, SBA).
- **Atendimento ao Locador** — abre e gerencia os chamados/incidentes.

**Proprietário do terreno** — a PF/PJ dona da área (José Luiz / Jessica de Oliveira no caso). Geralmente não está na thread, mas é citado.

Marque sempre: **quem decide** (tem autoridade pra fechar a condição), **quem trava** (está esperando algo ou discordando), **quem só executa**.

## Jargão APW que aparece nas fontes

- **DRS / Direito Real de Superfície** — instrumento jurídico pelo qual a APW adquire o direito sobre a área da torre.
- **Cessão de direitos creditórios** — a APW compra o fluxo de aluguel sem adquirir o imóvel.
- **ISW** — sistema interno da APW (referência de dados do deal; fonte de uma das divergências clássicas).
- **Rolling Forecast / RF** — pipeline de forecast; `RF Expert Notes` é campo do CRM.
- **Termo aditivo** — documento que formaliza a mudança de titularidade do aluguel para a APW.
- **Competência** — mês de referência do aluguel (≠ mês de pagamento).
- **Incident# / chamado** — número que a torreira usa para rastrear a tratativa.
- **Stage 1 / 3 / 99** — estágios do funil no CRM; 99 = fechado e fundeado.
- **L-code** — identificador da oportunidade.

## Montando a seção 7 (próximo passo)

O próximo passo tem que ser **acionável e específico**. Padrão ruim: "acompanhar o caso". Padrão bom:

> 1. Decidir internamente se a APW aceita a isenção de reajuste 2026 que a SBA alega — checar com quem negociou o acordo de matrizes / validar contra a ISW. **É o que destrava tudo.**
> 2. Se aceitar: ajustar o item "a" do formulário para a redação que o Julio Fagundes propôs e enviar o documento assinado.
> 3. Em paralelo, confirmar com a SBA a conta bancária correta (Caixa vs. Bradesco) pra liberar o pagamento de maio/2026.

Quando o caso chegou via "podem ajudar?", **formule explicitamente a pergunta que o Lucas precisa responder** — não deixe implícita. Se houver uma recomendação defensável, dê-a com o raciocínio; se for genuinamente uma decisão de negócio que só o Lucas/Diogo podem tomar, diga isso e liste o que ele precisa checar pra decidir.
