# Lentes Forenses — Catálogo de Padrões

Este é o catálogo de coisas a caçar ao ler as descrições das atividades. Não é exaustivo — é um ponto de partida calibrado para o pipeline da APW Brasil (lease aggregation telecom). Trate como gatilhos de atenção: quando um padrão aparece, pare e investigue.

## Índice
1. Sinais de risco de receita e de site
2. Vocabulário de gatekeeper e poder
3. Marcadores de deriva de preço
4. Divergências de dados típicas
5. Perfil comportamental da contraparte
6. Jargão interno APW
7. Marcadores de mudança de estado do deal

---

## 1. Sinais de risco de receita e de site

O risco mais grave num deal de lease aggregation é o site morrer antes do fechamento. Caçar:

- **Atraso de aluguel.** "condomínio está sem receber os aluguéis há X meses", "ATC não está pagando", "erro interno nos pagamentos". → 🔴 Crítico. Se a operadora parou de pagar, o ativo que a APW compraria pode estar em disputa ou em vias de extinção.
- **Retirada de equipamento.** "retiraram equipamentos", "retiraram bateria", "desinstalação". → 🔴 Crítico. Retirar bateria/equipamento é frequentemente o primeiro passo de um descomissionamento de site. Mesmo "uns equipamentos aleatórios" importa.
- **Chamado aberto sem resposta.** "abriu chamado", "ATC não responde", "2 chamados mas sem retorno". → 🟡 Atenção. A contraparte está cega sobre o próprio contrato — atrasa qualquer precificação.
- **Possível entrada/saída de operadora.** "entrada de nova operadora", "site pode não ser desinstalado". → 🟡 Atenção. Muda a tese de valor.
- **Ausência de carta formal.** "não houve carta de retirada, redução ou negociação". → registra que o risco ainda é informal/ambíguo — não confirmado, mas não descartado.

## 2. Vocabulário de gatekeeper e poder

Quem aparece no campo "contato" raramente é quem decide. Caçar quem **intermedeia** e quem **bloqueia**:

- **Administradora / síndico profissional.** "a ADM é a Lello", "Evelyn da administradora", "vão levar para a assembleia". A administradora frequentemente é o gatekeeper real — pode matar o deal por política interna, não por mérito.
- **Sinais de resistência velada.** "não senti firmeza nela", "não estava comprando a ideia", "apresentou ponderações", "resistência ao formato". → o deal pode travar aqui mesmo com preço bom.
- **Delegação como escudo.** "a síndica delegou à administradora", "pediu que eu tratasse com ela". → o decisor está se distanciando; cadência fica refém do intermediário.
- **Assembleia / conselho.** "levar para a assembleia", "consultar o conselho", "AGE". → decisão coletiva, prazo dilatado, mais pontos de falha.
- **Consulta a terceiros.** "decidiram consultar a ATC", "buscar opinião da Lello". → o deal saiu do controle do dono APW; sinal de freio.

Para cada pessoa, classifique o poder: **decisor** (assina) / **influenciador** (opina e é ouvido) / **gatekeeper** (controla acesso/informação e pode vetar) / **executor** (só operacionaliza).

## 3. Marcadores de deriva de preço

Rastrear TODOS os valores citados, em ordem cronológica, com data. A âncora se move e isso conta uma história:

- Propostas formais: "Proposta: 1050m à vista ou 1.3m em 3 anos".
- Contrapropostas / pedidos: "condomínio solicitou R$ 1,5 milhão", "evoluiu para R$ 1,160 milhão".
- Cálculos internos: "cheguei em 1.160m".
- Sinalize: a âncora subiu ou desceu? O gap entre pedido e viável está aumentando? Houve mudança de modalidade (à vista ↔ parcelado)?

Marcar quando a contraparte ancora alto cedo ("show me the money", "1,5 milhão") — define o tom da negociação.

## 4. Divergências de dados (eixo próprio)

O achado mais valioso da leitura palavra a palavra, e por isso recebe **seção própria** no briefing e no dashboard. Procurar ativamente o mesmo fato dito de formas diferentes entre fontes:

- **Operadora.** Anatel diz uma coisa, planilha interna diz outra, contrato físico (frequentemente antigo) diz uma terceira. Ex.: "na Anatel consta Claro e na planilha consta Vivo" — e o contrato em mãos ser da Nextel.
- **Valor do aluguel.** Contraparte fala um número redondo de memória ("14k", "em torno de 14k"); o cálculo exato dá outro ("R$ 15.286,34"). Sempre capture os dois.
- **Qual contrato a APW tem.** "só temos o contrato antigo, da Nextel" vs. operadora atual ser ATC. Documento desatualizado = risco de precificação.
- **Prazo.** Percepções divergentes sobre duração contratual ("prazo considerado longo").

Formato de saída: tabela. Fato | Fonte A (valor) | Fonte B (valor) | Fonte C | Implicação para o deal.

**Ligação com as Red Flags:** uma divergência que ameaça o deal (ex.: operadora errada → precificar o ativo errado) deve aparecer *também* na seção de Red Flags, classificada por severidade, remetendo de volta a esta seção. O registro completo da divergência fica aqui; a Red Flag é o eco do risco. Não concilie silenciosamente as contradições — exiba-as.

## 5. Perfil comportamental da contraparte

O tom com que o dono descreve a contraparte é dado operacional — afeta cadência e estratégia:

- **Desconfiança.** "extremamente desconfiada", "super confusa", "ser bem cirúrgica com ela". → exige proposta ultra-clara, simples, sem ambiguidade.
- **Indisponibilidade crônica.** "sempre viajando", "voltou de férias", "estava de saída". → ciclos de follow-up longos; não é desinteresse necessariamente, mas trava o ritmo.
- **Receptividade.** "foi receptiva", "boa conversa", "entendeu tudo". → janela de avanço, agir rápido.
- **Mercenarismo.** "show me the money", "não fizeram negócio por questões exclusivamente financeiras". → deal é puramente preço; sem espaço para venda de modelo.

## 6. Jargão interno APW

Abreviações e termos que aparecem nas tasks e o que significam:

- **FUP** — Follow-up. Task de acompanhamento, sem fato novo necessariamente.
- **ARI** — Análise de Risco do Imóvel (due diligence do site/terreno).
- **CI** — Contato Inicial (ou Carta de Intenção, conforme contexto — verificar pelo conteúdo).
- **SURRENDER** — Desistência formal da opp. "SURRENDER - não está engajada e sumiu". Marca o deal como morto naquele momento — mas opps ressuscitam.
- **Pricing Desk / Calculator** — Tasks automáticas geradas pela calculadora de precificação. "This task was created and completed automatically by the Calculator". Não têm dono humano (`undefined`) — marcam que uma proposta foi precificada.
- **Assignment of Lxxxxx** — Troca de dono da opp. Cada uma marca uma transição; vale rastrear, pois muda o estilo de condução e reseta relacionamento.
- **L-code (Lxxxxxxx)** — Identificador único da oportunidade no Dynamics.
- **ATC / American Tower, SBA, IHS, Highline** — Tower companies (proprietárias/operadoras de torres).
- **Vivo, Claro, TIM, Oi, Nextel** — Operadoras (MNOs). Nextel foi absorvida pela Claro — contrato "da Nextel" hoje é tecnicamente Claro, fato relevante para divergências.

## 7. Marcadores de mudança de estado do deal

Frases que sinalizam que o deal mudou de patamar:

- **Ressurreição.** "paramos de investir na região e agora retornamos", "retomar futuramente". Uma opp morta voltou — o histórico antigo ainda é válido como contexto.
- **Travamento.** "talvez a negociação não avance neste momento", "decidiram consultar X antes de qualquer definição", "não dá para fazer proposta pois...".
- **Avanço real.** "vão levar para a assembleia", "modelo de edital enviado", "gestor entendeu tudo e disse que é viável".
- **Falsa atividade.** Muitas tasks "Completed" seguidas sem fato novo ("Contato — não atendeu", "FUP — sem retorno") = deal estagnado apesar de parecer ativo no CRM.

Regra de ouro: **o stage do CRM e o número de atividades não dizem se o deal está vivo.** O texto diz. Uma opp com 40 atividades e stage avançado pode estar morta; uma com 5 pode estar quente.
