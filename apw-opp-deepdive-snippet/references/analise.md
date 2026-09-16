# Análise — as sete lentes

Leia antes de escrever o dossiê. O valor da skill não está na extração — está aqui.

---

## 1. Deriva de preço e IRR

Monte a tabela cronológica: **data · estrutura · valor apresentado · IRR · aluguel base** (o aluguel sai do `apwip_calculatorvariables` de cada pricing option). Marque com destaque a **Chosen Pricing Option** e qualquer valor aceito verbalmente nas atividades.

O que caçar:

- **IRR caindo enquanto o preço sobe.** Se o aluguel subiu 24% e a IRR caiu 3 pontos ao longo de 4 anos, a APW pagou progressivamente mais caro por um ativo cujo risco de execução não caiu. Isso é custo afundado disfarçado de "atualização de proposta". Diga isso com essas palavras.
- **Valor aceito que não virou pricing option.** Atividade registra R$X acordado, mas não existe pricing option com esse valor. O número real do deal só existe na prosa de um follow-up.
- **Reprecificação repetida sem mudança de premissa.** Três ou quatro rodadas com o mesmo bloqueio intacto = o preço nunca foi o problema. É a evidência mais forte para recomendar reestruturação ou surrender em vez de nova proposta.
- **Proposta expirada há muito tempo.** Os e-mails "Proposal will expire" datam a última tentativa viva.

## 2. Cadeia de bloqueio

Tabela cronológica só com os fatos que travaram. Regras:

- **Separe bloqueios independentes.** Um deal pode ter dois (ex.: anuência de terceiro + irregularidade fiscal do vendedor). Resolver um não destrava o outro. Diga quantos são.
- **Marque o que está fora do controle da APW.** Política de órgão público, dívida do proprietário, aprovação de prefeitura — a APW não executa, só espera.
- **Ache o momento em que alguém disse "provavelmente não vai sair".** Costuma estar enterrado numa atividade anos antes do deal ser oficialmente parado. É a data em que o deal realmente morreu; o resto é inércia.
- **Ache a alternativa proposta que nunca foi respondida.** Padrão frequente: alguém do campo sugere reestruturar, um interno fica de verificar, e não há registro de retorno. Isso é uma decisão nunca tomada — recupere-a.

## 3. Divergências de CRM 🔴

Bloco de maior valor. Tabela: **item · fonte A · fonte B · implicação**. Catálogo do que checar sempre:

| Divergência | Como detectar | Por que importa |
|---|---|---|
| Chosen Pricing Option obsoleta | `_apwip_chosenpricingoption_value` aponta para uma option `Inactive` e antiga, enquanto existem options `Active` recentes | Quem gerar submission hoje sai com valor e IRR errados |
| Valor aceito sem pricing option | atividade registra acordo verbal; nenhuma option com esse valor | O número real do deal não existe no sistema |
| Transaction Type inconsistente | option aprovada é `Fee Simple Interest`, options recentes são `Easement Interest` | Muda o instrumento que o jurídico redige |
| On Hold date desatualizada | campo `new_onholddate` × datas de on hold nas atividades | O deal parece mais morto (ou mais vivo) do que é nos relatórios |
| Estimated close vencida | `estimatedclosedate` no passado | Polui forecast |
| Surrender reason mentiroso | campo estruturado diz uma coisa, `apwip_surrenderreasonlegal`/atividades dizem outra | Quem filtrar por motivo não acha o caso |
| Aluguel declarado × calculado | `calculatorvariables` × extrato citado nas atividades | Base de precificação errada |
| Operadora do contrato × pagador real | contrato diz Claro/Vivo, POP mostra torreira | Muda contraparte, regras de anuência e bloco de CAPEX Fee |
| Checkbox × documento | checklist do CRM marcado, doc ausente no M-Files | Falso conforto no handoff |
| Owner do campo × quem trabalhou | `_apwip_stageNowner_value` × autor real das atividades | Atividades podem aparecer sob o owner atual mesmo tendo sido escritas por outro diretor — **nunca atribua uma atividade antiga ao owner atual** |

## 4. Mapa de atores

- **Decisor** — quem assina. Frequentemente ausente e não atende.
- **Gatekeeper** — quem de fato responde (secretária, advogada, despachante). Costuma ser a única fonte confiável de status.
- **Terceiro que trava** — órgão público, torreira, condomínio, sócio.
- **Back-office APW** — legal, paralegal, processor, RF, closer, review manager. Útil para saber a quem perguntar internamente sobre uma pendência antiga.

Separe quem decide de quem executa de quem trava.

## 5. Esforço real × teatro de CRM

Filtre as atividades automáticas (notificação de stage, expiração de proposta, mail merge, "Pricing Desk … created automatically by the Calculator", reatribuição). O que sobra é o esforço humano.

- Conte as interações humanas por ano.
- Identifique a **última interação humana real** — não confunda com a reatribuição automática que trouxe a opp para o Lucas.
- Diga quantos meses de silêncio.
- Note o padrão de follow-up: se são 12 registros seguidos de "cobrei retorno / sem resposta", o diretor manteve disciplina de CRM enquanto o deal já estava morto. É honestidade de registro, não trabalho — diga isso sem crucificar ninguém.

## 6. Risco de instrumento (regra APW)

| Estrutura | Quando cabe | O que exige | O que dispensa |
|---|---|---|---|
| **Fee Simple** (compra do terreno) | proprietário pleno, lote autônomo ou desmembrável | desmembramento, aprovação municipal, certidões, eventual anuência de órgão | — |
| **DRS** (art. 1.369 CC) | terreno PF/PJ onde o desmembramento trava | memorial descritivo + averbação na matrícula-mãe | **desmembramento e prefeitura**; não dispara ROFR — basta ciência, não anuência |
| **Cessão de Direitos Creditórios** (art. 290 CC) | rooftop / condomínio | notificação ao devedor; verificar vedação contratual à cessão | aquisição de imóvel |

Regras que decidem:

- Se o bloqueio é **desmembramento ou aprovação municipal**, o DRS é a primeira hipótese a testar — e é barata de testar, porque o memorial descritivo normalmente já existe no M-Files.
- **Verifique a matrícula antes de afirmar que o DRS resolve.** Cláusula de destinação, reversão ou vedação a oneração faz o DRS bater na mesma parede — DRS é oneração real. Isso é binário e decide o caso.
- **Irregularidade fiscal do vendedor independe do instrumento.** Execução fiscal ativa torna qualquer alienação ou oneração atacável por fraude à execução. Se existe, é gate anterior a tudo.
- **Se as pricing options recentes já estão como Easement Interest**, o deal já foi modelado economicamente como direito, não como propriedade — a migração para DRS é ajuste de processo jurídico, não reprecificação do zero.
- Torreira (TBSA, SBA, IHS, ATC, Highline) **não sai da Anatel nem do contrato** — sai do POP. Se não há POP recente, escreva "a confirmar", não chute.
- Regra permanente: deal **TBSA** exige bloco de CAPEX Fee com piso de IRR 16% no submission. Isso afeta o submission, não a viabilidade jurídica.

## 7. Veredito de retomada

Nunca termine com "atualizar a proposta". Estruture assim:

1. **Qual é o bloqueio real** — em uma frase.
2. **Qual hipótese o destrava** — mudança de instrumento, mudança de contraparte, mudança de escopo. Com o mecanismo explícito.
3. **O que precisa ser checado antes** — em ordem, e diga qual item é binário (o que, se vier vermelho, mata a tese).
4. **O argumento comercial novo** — se a reestruturação melhora o resultado *do proprietário* sem subir o payout da APW, esse é o gancho de retomada, não o preço. Procure isso ativamente.
5. **A condição de surrender** — explicite. "Se X vier vermelho, surrender formal, sem quinta rodada." Deal em Stage 7 On Hold segurando forecast por mais um ano é custo real.
6. **Higiene de CRM imediata** — independentemente da decisão: chosen pricing option, transaction type, on hold date, estimated close date, surrender reason.

---

## Tom

Português brasileiro informal, denso, direto. Bottom-line na primeira linha. Sem floreio, sem "é importante notar". Números exatos sempre — "R$ 353.000 (16,53%) em 31/03/25", não "cerca de 350 mil". Quando o deal está morto, diga que está morto. Quando a APW errou, diga onde, sem dramatizar e sem culpar pessoa nominalmente por falha de processo.
