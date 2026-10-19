---
name: apw-crm-whatsapp-extractor
description: Pipeline completo de campanha WhatsApp slow-drip pros landlords da APW Brasil — extrai telefones da view do Dynamics 365 via snippet JS, monta planilha de controle no Google Sheets com qualificação de lead (exige comprovante de aluguel + contrato), e dispara via Waseller (extensão Chrome identificada e mapeada) com config conservadora anti-ban. Use SEMPRE que o Lucas pedir "extrair telefones do CRM", "campanha slow drip", "disparar WhatsApp pros landlords", "lista de contatos pra WhatsApp", "contatos de Stage X pra campanha", "controle de disparo", "planilha de disparo", "configurar Waseller", "campanha nova no Waseller", ou colar uma URL de view do Dynamics (apwireless.crm.dynamics.com, apw.crm.dynamics.com) pedindo extração dos landlords. Também acione quando mencionar Z-API, Twilio, WPPConnect, Waseller ou outra plataforma de disparo WhatsApp junto com o CRM. NÃO use pra reportes de pipeline (apw-reporte-crm-diario), análise de performance (apw-performance-patterns), nem forensics de uma única opp (apw-opp-activity-forensics).
---

# APW CRM → WhatsApp Slow-Drip Pipeline

Skill operacional em TRÊS PARTES. Fluxo completo:

**CRM** (extração) → **Google Sheets** (controle + qualificação) → **Waseller** (disparo).

---

## PARTE 1 — Extração do CRM

### Fundamentos do schema APW

Descoberto em 19/10/2026 analisando a view Stage 5 da APW Brasil:

1. **O landlord não vive na opportunity**. Vive na entidade **lead**, linkada via dois lookups possíveis:
   - apwip_leadopportunityid (prioritário)
   - originatingleadid (fallback)

2. **Views da APW são userQuery**, não savedQuery. Chamar ?savedQuery=<id> retorna "Record Is Unavailable" (erro 2147746327). Usar ?userQuery=<id>.

3. **Taxa de preenchimento dos campos de telefone no lead** (amostra de 10):
   - mobilephone: 9/10 (prioritário)
   - telephone1: 8/10
   - telephone2: 7/10
   - telephone3: 7/10
   - new_currentownermobilephonenumber: 3/10
   - new_currentownerphonenumber: 4/10
   - new_whatsapp: 0/10 (campo morto)
   - apwip_ownerphonenumber: 0/10

4. **Taxa real de celular válido** (teste 19/10/2026 com 200 opps da view Stage 5): 129/200 = ~65%.

5. **Casos edge comuns**:
   - Múltiplos números num campo só: "+5519996455151 / +551933076646" → splitar por / ; ,
   - Notas inline: "+55 32 99964 9234 - zap" → stripar parênteses e tudo depois de " - "
   - Telefone de terceiro misturado → marcar com flag multi_source_flag=revisar

### Como rodar a extração

1. Abrir a view no CRM. Copiar o viewid da URL.
2. F12 → Console.
3. Diagnóstico (opcional, só primeira vez): scripts/01-diagnostic.js
4. Extração: scripts/02-extract.js (completa, 12 colunas) ou scripts/03-minimal.js (só code,phone).
5. Setar LIMITE no topo pra teste (200 é bom pra piloto). null = tudo.
6. CSV cai no clipboard. Download automático também (anti-foco do Chrome).

### Troubleshooting conhecido

| Sintoma | Causa | Fix |
|---|---|---|
| Record Is Unavailable (2147746327) | View é userQuery, não savedQuery | Trocar ?savedQuery= por ?userQuery= |
| CSV vazio | Campos de telefone diferentes | Rodar 01-diagnostic.js |
| Muitos pulados | Opps sem lead ligado | Normal pra opps antigas |
| sw.js Failed to fetch | Service worker do Dynamics | Ignorar, não interfere |
| Clipboard "Document is not focused" | Aba DevTools focada em vez da página | Usar o fallback de download de arquivo (já embutido na v2) |
| window.__apw undefined depois | Página recarregou | Rodar extração de novo |
| Chrome trava no paste | CSV > 2000 linhas | Usar download de arquivo |
| Throttle do Dataverse | View com milhares de opps | Trocar loop em série por $batch |

---

## PARTE 2 — Controle no Google Sheets com qualificação

Depois da extração, a campanha vive numa planilha Google Sheets. Padrão de nome: **"APW Stage <N> - Campanha WhatsApp <Mes Ano>"**.

### Estrutura da planilha

Colunas (nessa ordem):
1. code — código L da opp
2. phone — celular E.164 (+55DDDXXXXXXXXX)
3. status — dropdown (ver abaixo)
4. data_1o_envio
5. data_resposta
6. resultado — texto livre curto
7. doc_recebido — SIM / NAO (recebeu comprovante + contrato?)
8. notas — texto livre longo

### Dropdown de status (coluna C)

- Nao contactado (default inicial)
- 1o envio feito
- 2o envio feito
- Respondeu
- Mandou documentos (qualificado — virar proposta)
- Agendou call
- Em negociação
- Fechou
- Opt-out
- Numero errado
- Nao atende

### Cores por status

- Fechou → verde
- Mandou documentos / Agendou call / Em negociação → amarelo
- Respondeu → azul claro
- Opt-out / Numero errado → vermelho/cinza
- Nao contactado → branco (default)

### Painel de contadores (3 linhas no topo)

Inserir 3 linhas vazias acima do cabeçalho. Fórmulas:

| Métrica | Fórmula |
|---|---|
| Total | =COUNTA(A5:A1000) |
| Já abordados | =COUNTIF(C5:C1000,"<>Nao contactado")-COUNTBLANK(C5:C1000) |
| Qualificados (doc recebido) | =COUNTIF(C5:C1000,"Mandou documentos")+COUNTIF(C5:C1000,"Em negociação")+COUNTIF(C5:C1000,"Fechou") |
| Fechou | =COUNTIF(C5:C1000,"Fechou") |
| Taxa de resposta | =COUNTIF(C5:C1000,"Respondeu")/COUNTIF(C5:C1000,"<>Nao contactado") |
| Taxa de qualificação | =(Qualificados)/COUNTIF(C5:C1000,"Respondeu") |

### Criação automática via MCP Google Drive

Pode ser criada direto no Drive do Lucas via mcp__Google_Drive__create_file com contentMimeType=text/csv — o Drive converte pra Sheets automaticamente.

### Filosofia de qualificação (CRÍTICO)

A campanha NÃO entrega proposta pra todo mundo que responder. **Exige fricção na resposta pra separar landlord sério de curioso**:

Dois documentos obrigatórios pra virar lead qualificado:
1. **Comprovante do aluguel atual** (extrato ou recibo da torreira, últimos 1-3 meses) — sem isso qualquer proposta é chute (a própria skill apw-proposta-comercial diz: "errar aluguel = errar tudo").
2. **Cópia do contrato + aditivos** — pra DD jurídica preliminar e identificação da torreira real.

Por que o filtro funciona:
- Elimina curioso que não é dono.
- Cria compromisso psicológico (quem envia doc já se vê em negociação).
- Dá informação pra proposta formal sair calibrada (via skill apw-proposta-comercial).
- Economiza tempo do Lucas e dos diretores de aquisição.

Expectativa realista: dos ~2-5% que respondem, só ~30-50% mandam docs. Mas quem manda é lead quase pronto — taxa de fechamento muito alta.

### Copy padrão da campanha v4 (educativo + qualificação + fontes reais)

Mensagem única, pros 4 argumentos de risco de mercado:

```
Olá! Aqui é da APW Brasil (apwireless.com.br).

Sou Lucas Minozzo, Diretor de Investimentos. Estou mapeando proprietários que recebem aluguel de antena de operadora (Vivo, Claro, TIM, Oi) porque o setor passa por mudanças profundas neste 2026:

1️⃣ CONSOLIDAÇÃO: a IHS vendeu toda a operação de torres da América Latina para o grupo Macquarie. A Oi vendeu 8.000 torres para a Highline por R$ 1,6 bi. O dono do SEU contrato pode mudar sem aviso.
→ https://www.datacenterdynamics.com/br/not%C3%ADcias/ihs-acerta-a-venda-de-suas-opera%C3%A7%C3%B5es-de-torres-na-am%C3%A9rica-latina-para-grupo-macquarie/

2️⃣ RACIONALIZAÇÃO: a TIM anunciou que vai se desfazer de 60% das antenas que comprou da Oi. Sites redundantes são desinstalados.
→ https://www.agenzianova.com/en/news/?p=97449

3️⃣ DESINSTALAÇÃO: em Brasília, operadoras ameaçaram desligar antenas inteiras por disputa com lei municipal. Proprietários perderam o aluguel.
→ https://tecnoblog.net/arquivo/caladao-antena-brasilia-governo-df/

4️⃣ STARLINK: a SpaceX de Elon Musk comprou US$ 17 bi em frequências de celular da EchoStar em setembro/2025 para oferecer sinal direto do satélite. Testes começam em final de 2026 — boa parte dos sites atuais vira ativo redundante.
→ https://www.aljazeera.com/economy/2025/9/8/spacex-expands-starlink-satellite-network-with-17bn-echostar-deal

O aluguel de antena é uma receita contratual, não uma renda perpétua garantida. A APW é um veículo de investimento (lastreado por EQT e PSP Investments) que paga à vista o valor presente dos próximos 20-30 anos desse aluguel, assumindo integralmente o risco do contrato.

Pra eu rodar uma simulação precisa pro seu caso, preciso de 2 informações:

📎 1. Último comprovante de pagamento do aluguel (extrato ou recibo da torreira — últimos 1-3 meses)
📎 2. Cópia do contrato de locação + aditivos (se houver)

Me envia os dois arquivos por aqui e em 48h te mando uma proposta exata. Sem os documentos, qualquer número é estimativa — e meu compromisso é apresentar número real.

Lucas Minozzo
Diretor de Investimentos | APW Brasil
```

Vocabulário obrigatório (herdado da skill apw-proposta-comercial):
- ✅ "veículo de investimento lastreado por EQT e PSP"
- ✅ "receita contratual, não renda perpétua"
- ✅ "assume integralmente o risco do contrato"
- ✅ "você" (nunca "Sr./Sra.")
- ❌ NUNCA "antecipação", "antecipar", "venda", "monetização"
- ❌ NUNCA mencionar TIR, juros, taxa, custo
- ❌ NUNCA atacar a torreira (SBA, ATC, IHS, Highline são parceiros APW)

### Fluxo operacional da campanha

1. **Dia 0**: extrai do CRM, cria Sheets, dispara os primeiros 10 contatos (piloto manual).
2. **Marca status** → "1o envio feito" + data em data_1o_envio.
3. **Dia 1-3**: observa taxa de resposta e qualidade. Ajusta copy se preciso.
4. **Semanal**: filtra status = "Nao contactado" e dispara mais 45/leva.
5. **Quando responder**: muda status + preenche data_resposta.
6. **Quando mandar docs**: muda pra "Mandou documentos" + doc_recebido=SIM → gerar proposta formal via `apw-proposta-comercial`.
7. **Mensal**: contador "Taxa de qualificação" indica se o filtro está bem calibrado.

---

## PARTE 3 — Disparo via Waseller (ferramenta mapeada 19/10/2026)

### Identificação da ferramenta

- **Nome oficial**: WaSeller — "Perder vendas no WhatsApp não é normal"
- **Tipo**: extensão Chrome Manifest V3
- **Versão testada**: 7.4.3.89
- **Chrome ID**: `illemhbijpiebjfilfmgebahaakajkpe`
- **Publicador**: "wsll" (independente, não corporativo)
- **Base**: ~90 mil usuários, em queda ~10% nos últimos 30 dias
- **Conta do Lucas**: Premium, sem trava de volume

### Como acessar

Waseller NÃO abre popup próprio e NÃO tem app separado. **Injeta uma barra lateral de ícones à esquerda dentro do WhatsApp Web** (web.whatsapp.com). O 2º ícone da barra = "Envio em Massa" (mostra contador de campanhas, ex.: "22").

Ao clicar, aparecem 2 opções: **Versão Clássica** e **Nova Versão**. **Usar sempre a Nova Versão** — é a que está mapeada e mantida.

### Wizard "Nova Versão" — 5 passos

**Tela inicial — Campanhas Existentes**:
- Botões: Nova Campanha, Tutorial, Enviar uma campanha rápida, Gerenciar campanhas, Visualizar Relatórios.
- Cada card de campanha tem Abrir e Deletar.
- "Nova Campanha" pede um campo "Nome da campanha" e cria um rascunho.

**Passo 1 — Contatos (Selecione os destinatários)**

Origens de lista disponíveis:
- Contatos Salvos
- Inbox
- Etiquetas
- Grupos
- Contatos de grupos
- CRMs/Abas
- Perfil do contato
- **Importar planilha** ← esse é o caminho pros nossos extracts do CRM

Controles: Filtros, Agrupamentos, busca, Selecionar tudo, Adicionar contato, Exportar selecionados (.XLSX).

Importação aceita `.xlsx` e `.csv`. **Não aceita colar lista nem mapear colunas** — precisa seguir o template exato.

Dois toggles críticos:
- "A planilha contém números internacionais?" → **MARCAR** (nossos números são +55...)
- "Ignorar validação do 9º dígito brasileiro?" → **DEIXAR DESMARCADO** (nosso extractor já filtra só celular com 9 na frente)

Regra escrita: "os contatos precisam ter DDD". Nosso CSV já vem com DDI+DDD (+55DDDXXXXXXXXX).

Template literal do CSV: baixar via "Importar planilha → Visualizar Modelo → Baixar Modelo" na primeira vez (vai pro Downloads). Confirmar header antes de subir lista real.

**Passo 2 — Ações (Componha suas ações)**

Campanha é uma sequência de ações encadeadas. Categorias:
- **Enviar Mensagem**: Texto, Imagem, Vídeo, Áudio, Documentos, Pix, Convite para Grupo, Contato, Link com Banner, Figurinha, Lista.
- **Temporizadores**: Esperar X segundos, "digitando…", "gravando áudio…".
- **Aba do CRM e Etiquetas**: adicionar/remover.
- **Utilitários**: arquivar, fixar, marcar não lido, bloquear.
- **Respostas Rápidas, Transferir Atendimento, Tags**.

Ação **Texto** abre:
- Área de texto ("Digite o texto") — cola a mensagem v4 inteira.
- "Exibir digitando por N segundos" (padrão 5).
- "Aguarde para chamar a próxima ação por N segundos" (padrão 5).
- Pré-visualização do fluxo.
- "Desativar a assinatura" + "Personalizar o nome da assinatura".

**Variáveis e spintax**: não há botão nem documentação na UI. Teste empírico mostra que `{nome}` e `{a|b}` renderizam **literal** na prévia — portanto **assumir que NÃO funcionam** até teste real. Pros ~130 contatos, usar mensagem única sem variável (todo mundo vira "Olá!" ou nada).

**Passo 3 — Revisão (Revise e confirme)**

Mostra: sequência de ações, total, tempo estimado, destinatários, botão Editar por bloco.

Dois botões críticos:
- **"Executar teste para mim"** → dispara pro próprio número do Lucas. **SEMPRE RODAR antes de cada leva** pra validar: render dos links, assinatura, previews, formatação, variáveis.
- **"Executar Ações"** → disparo de verdade (irreversível).

**Passo 4 e 5 — Envio e Resultados**: execução + relatório.

### Delays e limites disponíveis na UI

| Parâmetro | Padrão | Faixa |
|---|---|---|
| Intervalo entre envios | 10 s | 1–60 s |
| Pausa a cada X envios | 10 contatos | 1–50 |
| Tempo da pausa | 60 s | 5–300 s |
| "Digitando…" antes de enviar | 5 s | 0+ livre |
| Espera até a próxima ação | 5 s | 0+ livre |

### O que a Waseller NÃO oferece (compensar manualmente)

- ❌ **Limite diário** — controlar via tamanho da lista por campanha.
- ❌ **Janela de horário permitido** — rodar manualmente só em horário comercial dias úteis.
- ❌ **Aquecimento de número** — fazer antes, por fora.
- ❌ **Rotação de números** — se escalar além de 100-150/dia, precisa chip novo.
- ❌ **Jitter aleatório confirmado** — intervalo parece fixo; mitigar com intervalo maior (45-60s) pra reduzir detecção.

### Config CONSERVADORA recomendada pros ~130 contatos APW

Padrões default do Waseller (10s, pausa 60s) são **perfil de ban certo** pra lista fria. Config correta:

| Parâmetro | Valor |
|---|---|
| Intervalo entre envios | **45–60 s** |
| Pausa a cada | **10 contatos** |
| Tempo da pausa | **300 s** (5 min) |
| "Digitando…" antes | **5-8 s** |
| Espera próxima ação | **5 s** |

**Divisão em levas**: 3 levas de ~45 contatos cada, **em dias diferentes** (ou pelo menos turnos diferentes do mesmo dia). Tempo estimado por leva: ~1h30 com os delays acima.

### Pré-disparo — checklist obrigatório

1. **Chip de disparo aquecido 1-2 semanas** (não o número pessoal, não o número principal da APW).
2. **Perfil WhatsApp Business configurado**: foto, descrição ("APW Brasil — Antecipação de aluguel de antena"), site, horário.
3. **Fechar campanha fantasma antiga** — o agente achou uma campanha de 27/03/2026 ainda com status "Enviando" (86 e 2 nos contadores). Deletar antes de criar nova pra não voltar a disparar junto.
4. **Rodar "Executar teste para mim"** → confirmar visualmente a mensagem renderizada no seu WhatsApp, incluindo preview dos links e assinatura.
5. **Validar formato da lista**: celulares em +55DDDXXXXXXXXX, header exato do modelo Waseller.

### Fluxo de disparo recomendado (passo a passo)

1. Abrir WhatsApp Web no chip de disparo aquecido.
2. Clicar no 2º ícone da barra lateral do Waseller → Envio em Massa → Nova Versão.
3. Fechar/deletar campanha fantasma antiga (se houver).
4. "Nova Campanha" → nomear "APW Stage 5 - Leva 1 - [data]".
5. Passo 1 Contatos → Importar planilha → subir CSV de ~45 linhas → marcar "números internacionais".
6. Passo 2 Ações → Texto → colar v4 completa → configurar delays conservadores.
7. Passo 3 Revisão → "Executar teste para mim" → validar no WhatsApp pessoal.
8. Se OK → "Executar Ações" (disparo real).
9. Enquanto roda: anotar na planilha de controle, marcar "1o envio feito" + data_1o_envio.
10. Ao final, baixar relatório da campanha Waseller → cruzar com planilha pra marcar "Numero errado" nos que falharam.
11. **Esperar 48-72h** antes da Leva 2 pra absorver respostas e evitar padrão de ban.

### Riscos observados (ferramenta e processo)

- **Padrões default são agressivos** — sempre reconfigurar manualmente antes de disparar.
- **Publicador independente ("wsll")** com base de usuários em queda — tem acesso total ao WhatsApp. Em out/2025 foram descobertas 131 extensões Chrome fazendo spam pelo WhatsApp Web no Brasil (Canaltech). Waseller não está confirmado nessa lista, mas vale pesar o risco pra dados APW. Alternativa pra dado sensível: Z-API (API oficial, mais caro mas mais seguro).
- **Conta Premium sem trava de volume** — nada impede erro operacional (subir lista errada e disparar). Sempre revisar lista no Passo 3 antes do Executar Ações.
- **Sem rotação de número nem aquecimento** — se escalar além de 100-150/dia, precisa planejar chips extras.

---

## Alternativa de escala — Z-API

Quando a campanha-piloto validar o copy (taxa de resposta aceitável, taxa de qualificação OK), vale migrar para **Z-API** se o próximo lote for 1000+ contatos:

- API oficial WhatsApp Business — risco de ban muito menor.
- Integra com Sheets via Zapier/Make → status atualiza sozinho.
- Custa R$ 150-300/mês.
- Vale pela escala e pela segurança dos dados APW.

Se a decisão for escalar, construir a integração como projeto separado.

---

## Compliance (APW Brasil)

- Nunca screenshot do CRM nem do WhatsApp Web (regra apw-chrome-agent-lean-compliance).
- Snippet de extração roda local no navegador do Lucas, sessão dele. Zero dado sai do Dynamics pra terceiros.
- CSV + Sheets têm PII (telefones de landlords) → tratar como confidencial. Drive pessoal, nunca compartilhar público.
- Waseller como extensão Chrome tem acesso total ao WhatsApp — risco inerente de qualquer extensão de disparo. Avaliar vs Z-API conforme sensibilidade.
- Opt-out na coluna status é terminal: NUNCA re-contactar quem marcou essa opção.
- LGPD: se landlord pedir pra parar, marca Opt-out imediatamente e apaga da lista das próximas levas.

---

## Normalização de número → E.164 BR

1. Strip de tudo que não é dígito.
2. Se começa com 55 e tem >=12 dígitos → já é E.164, só prefixa +.
3. Se tem 10 ou 11 dígitos → prefixa +55.
4. Pra campanha WhatsApp (celular only): exigir 11 dígitos pós-DDD E 3º dígito = 9.
5. Fixos (10 dígitos ou 3º dígito != 9) ficam marcados is_mobile=fixo ou são descartados na versão minimal.

---

## Roadmap

- [ ] Suporte a $batch pra views com 1000+ opps.
- [ ] Integração Sheets ↔ Z-API — status atualiza sozinho quando mensagem é entregue/lida/respondida.
- [ ] Migração opcional pra dashboard Cloudflare Pages + D1 (igual family-prev-dash).
- [ ] Enriquecer com last_contact_date do lead pra priorizar quem é antigo.
- [ ] Flag de opt-out: ler donotphone do lead no CRM e excluir ANTES do CSV.
- [ ] Deduplicação por telefone (mesmo landlord com 3 opps = 1 disparo).
- [ ] Script de pré-flight que valida CSV contra template do Waseller antes de subir.
- [ ] Explorar/validar funcionamento de variáveis `{nome}` no Waseller com teste controlado.

---

## Histórico

- **19/10/2026 manhã**: Skill criada. Descoberta inicial na view Stage 5 (viewid 572e1df3-7198-eb11-b1ac-000d3a32d0bd), 10 leads de amostra. Resultado: mobilephone cobre 90% + telephone1-3 cobrem o resto.
- **19/10/2026 tarde**: Primeiro extract real com LIMITE=200 → 129 celulares válidos (65%). Planilha de controle criada no Drive (file ID 10ELABxfsws2JjRNLrFkvWr34cvdrsp3VWvuloqMxn28). Adicionada Parte 2 (Controle Google Sheets).
- **19/10/2026 noite**: Copy evoluiu até v4 (4 blocos de risco + qualificação via docs). Agent-browser mapeou Waseller v7.4.3.89 ponta a ponta — wizard 5 passos, config conservadora, armadilhas identificadas (padrões agressivos, campanha fantasma antiga, publicador independente). Adicionada Parte 3 (Disparo via Waseller).
