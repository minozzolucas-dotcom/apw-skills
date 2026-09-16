---
name: apw-arbitragem-lead
description: Julga disputas entre diretores de aquisição da APW Brasil sobre titularidade de lead/oportunidade e conduta no atendimento 0800 (código de marketing, endereço da torre, checagem no CRM). Reconstrói a linha do tempo com evidência do Dynamics 365, aplica o teste de estágio (Stage 1 parado transfere; Stage 3/5 com proposta viva fica), emite VEREDITO com titularidade, ações, falhas de processo e e-mail pronto pro time, e alimenta um placar de reincidência por diretor. Use SEMPRE que o Lucas trouxer um caso entre dois diretores — "recebi um caso da X com a Y", "conflito de lead", "disputa de oportunidade", "de quem é esse deal", "quem está certo", "dois diretores no mesmo site", "abriu lead que já existia", "não pediu código de marketing", "julga esse caso" — ou colar reclamação de diretor sobre lead pego por outro. Também quando surgir nome/telefone novo sem match no CRM mas o site já estiver com alguém. NÃO use para dossiê de deal (apw-deal-dossier) nem reporte diário (apw-reporte-crm-diario).
---

# Arbitragem de Lead — APW Brasil

Julgar caso de dois diretores no mesmo site. A saída é uma decisão, não um relatório.

## Ordem de prioridade do julgamento

Nesta ordem, sempre. Quando conflitarem, a de cima ganha.

1. **Não perder o site e não subir o preço.** Duas propostas no mesmo imóvel viram leilão contra a APW. Matar a duplicidade é mais urgente que fazer justiça entre diretores.
2. **Titularidade correta.** Quem trabalhou de fato fica com o deal.
3. **Correção de processo.** Quem furou o protocolo é registrado — mesmo que ganhe a disputa.

Diga isso no veredito quando as três divergirem. O diretor precisa entender que perdeu o deal por causa do site, não por castigo.

## Princípio-mestre: o SITE é o deal, a pessoa não é

A chave de identidade de uma oportunidade, em ordem decrescente de força:

| Nível | Chave | Força |
|---|---|---|
| 1 | Matrícula / inscrição imobiliária | Definitiva |
| 2 | Endereço + coordenada (raio 150 m) | Forte |
| 3 | ERB/torre identificada (operadora + torreira) | Forte |
| 4 | CNPJ do condomínio / PJ proprietária | Média |
| 5 | Nome da pessoa | Fraca |
| 6 | Telefone | Fraca |

Nome e telefone diferentes **não** criam deal novo. Cônjuge, filho, espólio, coproprietário, procurador, síndico, subsíndico, conselheiro, administradora e zelador são todos interlocutores do **mesmo** deal. Essa é a origem de quase toda disputa: o CRM indexa pessoa, o negócio é o imóvel.

Quando o entrante não trouxer endereço, use `apw-erb-towerco-triage` para localizar a ERB pelo que houver (bairro, operadora, referência) antes de declarar "não existe no CRM".

## Protocolo de atendimento (a regra que se julga)

Quem atende o 0800 é obrigado a, na mesma ligação:

1. **Pedir o código de marketing** — é a prova de origem do contato. Sem código, o contato não sustenta reivindicação de origem nova.
2. **Pedir o endereço da torre/prédio** — é a chave do deal. Sem endereço, a busca no CRM é inútil e a duplicidade é inevitável.
3. **Checar no CRM na hora** — por endereço e por raio de coordenada, não só por nome/telefone — e verificar se já está com alguém.

Falha em qualquer um dos três é falha de processo registrável, independentemente de quem fique com o deal.

## Fase 0 — Enquadrar o caso

Antes de puxar qualquer dado, escreva em 5 linhas:

- **Partes:** quem reclama, quem detém.
- **Alegação de cada lado**, na versão de cada um.
- **Fato incontroverso:** o que os dois lados concordam.
- **Ponto de virada:** o fato único que, se confirmado, decide o caso.
- **O que ainda é boato:** tudo que veio de fala de terceiro sem registro.

Se o ponto de virada não estiver claro, o caso ainda não está pronto pra julgar. Pergunte antes de puxar CRM.

## Fase 1 — Coleta de evidência no CRM

Delegue a extração para `apw-dynamics-copilot` (Web API via sessão autenticada; sem screenshot em domínio Dynamics, conforme `apw-chrome-agent-lean-compliance`). Peça exatamente:

**Do L em disputa:**
- Owner atual, owner anterior e datas de troca (audit trail)
- Stage, statuscode, createdon
- Endereço completo, coordenada, operadora, torreira
- Contatos vinculados: nome, telefone, papel
- Origem: campanha / código de marketing / source
- Pricing options: quantas, criadas quando, por quem, valor
- Atividades completas: subject, **description integral**, activity owner, createdon, actualend

**Do lado do entrante:**
- Busca por telefone do entrante (todos os formatos)
- Busca por nome do entrante
- Busca por endereço e por **raio de 150 m** da coordenada do site
- Existe outro L no mesmo imóvel? (duplicidade histórica é comum)

Para ler as descrições de atividade palavra a palavra — quem falou com quem, se houve contato com o decisor — delegue a `apw-opp-activity-forensics`.

## Fase 2 — Linha do tempo única

Monte uma tabela cronológica com tudo, das duas fontes:

| Data | Fato | Fonte | Quem registrou | Peso |
|---|---|---|---|---|

Peso: **Registro** (campo/atividade no CRM, datado) > **Documento** (proposta, e-mail) > **Relato** (fala de diretor) > **Alegação de terceiro** (o que o proprietário disse por telefone).

Relato de proprietário nunca derruba registro sozinho. Ele levanta a hipótese; a atividade confirma ou desmente.

## Fase 3 — Árvore de decisão

Aplique em ordem. Pare na primeira que resolver.

**R1 — Mesmo site?**
Se as chaves de nível 1–3 baterem, é o mesmo deal. Não existe "lead novo" para o mesmo imóvel. Se forem sites distintos, não há disputa: abra o L novo e encerre.

**R2 — Teste de estágio (porta decisória).**
O estágio no pipeline decide a maioria dos casos sozinho. Consulte a matriz:

| Estágio do L | Atividade substantiva ≤30d **ou** proposta ≤90d | Veredito |
|---|---|---|
| Lead / Stage 1 | Não | **Transfere** pro diretor que pegou a ligação |
| Lead / Stage 1 | Sim | Fica com o dono — o trabalho começou |
| Stage 3 | Sim | **Fica. Não se discute.** |
| Stage 3 | Não (proposta velha, sem follow-up) | Fica, com prazo de reativação — ver R3 |
| Stage 5 | Sim | **Fica. Não se discute.** |
| Stage 5 | Não | Fica, com prazo de reativação — ver R3 |
| Stage 7+ | Qualquer | Fica sempre — documentação e jurídico já rodando |

A lógica: Stage 1 parado é estoque, não é posse. Stage 3 ou 5 com proposta na mesa é relação viva com o proprietário — tirar isso de alguém destrói a negociação e entrega ao landlord a informação de que há dois compradores internos.

Efeito colateral desejado: isso pressiona o estoque de Stage 1 frio. Quem não trabalha o que qualificou corre risco real de perder pra quem atendeu o telefone.

**R3 — Estágio alto porém parado.**
Stage 3/5 sem atividade há mais de 90 dias não transfere automaticamente, mas também não fica intocável. Dono tem **5 dias úteis** para registrar contato substantivo com o decisor. Não registrou, o caso volta e aí sim entra a avaliação de transferência. Comunique o prazo ao dono no mesmo e-mail do veredito.

**R4 — Estágio inflado (anti-gaming).**
O estágio só protege se for real. Dois testes:

- **Stage 3 sem pricing option linkada é Stage 1 disfarçado.** Confira se existe pricing option criada e vinculada, com valor e data. Sem isso, o deal cai na linha de Stage 1 da matriz.
- **Atividade substantiva** pelo critério APW: ≥180 caracteres, ou ≥140 + 2 sinais concretos (nome do interlocutor, valor citado, endereço, data marcada, próximo passo definido). Atividade genérica ("liguei, sem sucesso", "enviei proposta") não sustenta posse contra contato entrante com decisor.

Se a atividade da proposta não nomear com quem foi negociado, isso é o achado principal do caso. E se um diretor empurrou o deal de estágio logo depois de saber da disputa, isso é evidência, não coincidência — confira a data da mudança de estágio no audit trail contra a data da ligação entrante.

**R5 — Interlocutor errado.**
Se o titular do L negociou com quem não decide e o entrante é o decisor real: a titularidade **permanece** com o dono do L, e o entrante entra como canal, nomeado no CRM. Não se tira deal de quem trabalhou por causa de porta de entrada.

**R6 — Origem do entrante.**
Sem código de marketing, o contato entrante não prova origem nova e não sustenta reivindicação. Com código de campanha diferente da que originou o L, registre — mas origem não transfere titularidade sozinha.

**R7 — Desempate final.**
Proposta viva > relação documentada com o decisor > antiguidade do L. **Nunca dividir o deal.** Se dois precisarem atuar, um é owner e o outro é apoio nomeado, com o crédito acordado por escrito antes do próximo contato.

## Fase 4 — Veredito

Formato fixo:

```
## VEREDITO — [caso] · [L-number]

**Titularidade:** [nome] — regra [Rx]
**Confiança:** Alta / Média / Baixa
**Risco imediato:** [ex.: proprietário com duas propostas em aberto → preço em leilão]

### Linha do tempo
[tabela]

### Fundamento
[3 a 6 linhas, direto]

### O que inverte este veredito
[o fato específico que, se confirmado no CRM, muda a decisão]

### Ações
- [Diretor A]: ...
- [Diretor B]: ...
- Lucas: ...
- Prazo: ...

### Falhas de processo
| Regra | Quem | Evidência | Reincidência |

### E-mail pronto pro time
[texto curto, sem adjetivo, sem culpa pessoal — regra + decisão + próximo passo]
```

O e-mail responde ao grupo no mesmo tom em que o caso chegou. Nomeia a regra, não o defeito da pessoa.

## Fase 5 — Placar acumulativo

Mantenha `apw-arbitragem-placar.md` e re-entregue atualizado a cada caso (o Lucas guarda o arquivo e reenvia no caso seguinte; se não vier, peça).

```
| Data | Caso | L | Partes | Veredito a favor de | Regra | Falha de processo | Reincidência |
```

E o consolidado por diretor:

```
| Diretor | Disputas | A favor | Contra | Falha mais comum | Última |
```

**Honestidade estatística:** com N < 10 isso é descritivo, não preditivo. Nunca escreva "fulano costuma estar errado" com 2 casos. O que o placar detecta bem é **padrão de falha repetida** (ex.: "3 de 3 vezes atendeu 0800 sem pedir endereço"), e isso é acionável com N pequeno. Taxa de acerto só vira argumento com N ≥ 10.

## Armadilhas conhecidas

**"O proprietário disse que não falou com ninguém."**
Quatro explicações concorrentes, todas comuns:
1. O entrante é pessoa diferente do titular do L, do mesmo imóvel — e literalmente não falou.
2. A proposta foi para outro interlocutor do mesmo site.
3. Negação estratégica: negar contato é o jeito mais rápido de conseguir uma segunda proposta, provavelmente melhor.
4. Atividade fantasma: a proposta foi registrada no CRM e não aconteceu.

Nunca escolha uma sem ler a descrição da atividade e o telefone registrado nela. As hipóteses 3 e 4 têm consequências opostas e o custo de errar é alto: na 3, o diretor honesto é punido; na 4, gaming de CRM passa batido.

**Landlord fabricando concorrência interna.** Se o proprietário souber que há dois diretores, o preço sobe. Assim que a duplicidade for confirmada, uma única voz fala com ele — antes do veredito, se preciso.

**Condomínio.** Síndico troca, subsíndico responde, administradora intermedeia. Nenhum deles cria deal novo.

**Espólio e coproprietários.** Vários nomes, um imóvel. Sempre o mesmo L.

## Quando não decidir sozinho

Escale para o Luiz Alfredo (e não emita veredito público) quando houver:
- indício de atividade registrada que não ocorreu (gaming deliberado);
- reincidência do mesmo diretor no mesmo tipo de falha pela 3ª vez;
- acusação de má-fé entre diretores;
- envolvimento de valor já proposto ao proprietário por dois canais.

Nesses casos entregue o dossiê de evidência ao Lucas e pare.

## Exemplo trabalhado

**Caso:** Gisele × Aline Felix. Contato entrante João Pinto (0800), nome e telefone sem match no CRM. Proprietário afirma não ter falado com ninguém e pede proposta. Site corresponde ao **L370877**, em nome de Lourdes, outro telefone, dona Aline Felix, com atividade de proposta no mês anterior.

**Primeiro teste (R2):** qual o estágio do L370877? Proposta no mês passado sugere Stage 3 ou 5 com proposta viva — nesse caso fica com a Aline e o mérito acaba aqui. Se estiver em Stage 1 ou Lead, a proposta citada nas atividades não bate com o estágio: ou o estágio não foi movido, ou a proposta não existiu. Investigue antes de qualquer coisa.

**Segundo teste (R4):** a atividade da proposta nomeia o interlocutor e o telefone usado?

- Nomeia Lourdes, telefone bate, conteúdo substantivo → R2+R3+R4 satisfeitos. Deal da Aline. João Pinto é interlocutor adicional do mesmo imóvel (R1); Gisele repassa o contato e registra a ligação na opp da Aline. Falha de processo: verificar se Gisele pediu código de marketing e endereço — se não pediu, registra no placar mesmo com o mérito resolvido.
- Atividade genérica, sem nome nem telefone → R4 falha. A posse vira frágil: pedir à Aline a evidência do contato (e-mail, WhatsApp, proposta enviada) em 24 h. Sem evidência, o caso sobe.
- Coordenada do João Pinto fica fora do raio de 150 m e é outra torre → não há disputa. Abre L novo para a Gisele.

Em todos os cenários, ação imediata antes do veredito: **uma só voz fala com o proprietário**, para não colocar duas propostas na mesa.
