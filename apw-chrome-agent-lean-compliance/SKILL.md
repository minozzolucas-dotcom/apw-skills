---
name: apw-chrome-agent-lean-compliance
description: Use SEMPRE que o usuário pedir automação ou navegação no Claude in Chrome — abrir páginas, extrair dados, preencher formulários, raspar listas, ler CRM/ERP/email/Sheets, ou qualquer fluxo agêntico no navegador. Estabelece a ordem de ferramentas que minimiza consumo de tokens (read_page → get_page_text → javascript_tool antes de qualquer screenshot) e bloqueia screenshots em domínios corporativos sensíveis (Dynamics 365, Microsoft Teams, Outlook, Power BI, APW Brasil, qualquer subdomínio *.apwbrasil.com.br / *.apwireless.* / *.radiusglobal.* / dynamics.com / office.com / sharepoint.com / teams.microsoft.com / powerbi.com) para evitar problemas de compliance com captura visual de dados confidenciais. Permite screenshots apenas em sites públicos e somente quando estritamente necessário. Acione esta skill mesmo se o usuário não mencionar "compliance" ou "tokens" — o gatilho é o uso do Claude in Chrome em si.
---

# Chrome Agent — Lean & Compliance

Skill operacional para o **Claude in Chrome**. Define duas coisas:

1. **Ordem de ferramentas que gasta menos token** — porque screenshots e DOMs gigantes consomem contexto rápido.
2. **Regra de compliance sobre screenshots** — para não criar artefatos visuais de dados sensíveis em sistemas corporativos do Lucas (APW Brasil, Dynamics 365, Microsoft 365, Power BI).

---

## Princípio central

> **Texto estruturado antes de pixel.** Screenshots são o último recurso, nunca o primeiro.

Toda vez que o agente precisar "ver" uma página, percorrer essa ordem:

1. **`read_page`** — árvore de acessibilidade. Estruturada, leve, contém `ref` IDs para clicar/preencher. Use para entender layout, formulários, listas de resultados.
2. **`get_page_text`** — texto puro do conteúdo principal. Use quando você só quer ler artigo, descrição, corpo de email, transcrição, notas.
3. **`javascript_tool`** — cirúrgico. Use para extrair dados específicos (`document.querySelectorAll(...).map(...)`), ler valores de campos, contar elementos, pegar `dataset`, etc. Quase sempre é a opção mais barata em token.
4. **`read_network_requests`** — quando a página carrega dados via XHR/Fetch (Dynamics, Power BI, qualquer SPA). Pegar a resposta da API direto é muito mais limpo do que raspar o DOM renderizado.
5. **`read_console_messages`** — só quando estiver debugando comportamento da página.
6. **`computer` (screenshot)** — **último recurso**, e somente com as regras da próxima seção.

---

## Regra de compliance — quando screenshot é PROIBIDO

Screenshots criam artefatos visuais que ficam armazenados no histórico da conversa e podem expor dados confidenciais (PII de proprietários de terrenos, valores de deals, números de contratos, dados de pipeline, emails internos, etc.). No contexto APW Brasil, isso é especialmente sensível dado o histórico de revisão de compliance de IA sobre uso de dados do CRM.

### Domínios em que screenshot é PROIBIDO por padrão

Bloquear `computer` (screenshot) em qualquer URL que contenha:

- `apwbrasil.com.br` (e qualquer subdomínio)
- `apwireless.*`
- `radiusglobal.*`
- `dynamics.com` / `crm.dynamics.com` / `*.crm*.dynamics.com` (Microsoft Dynamics 365)
- `office.com` / `office365.com`
- `outlook.com` / `outlook.office.com` / `outlook.office365.com`
- `teams.microsoft.com` / `teams.live.com`
- `sharepoint.com`
- `powerbi.com` / `app.powerbi.com`
- `microsoft365.com` / `login.microsoftonline.com`
- Qualquer URL com tokens `dynamics`, `dataverse`, `crm` no path corporativo do Lucas

### O que fazer nesses domínios

- Usar **somente** `read_page`, `get_page_text`, `javascript_tool`, `read_network_requests`, `form_input`, `find`, `navigate`.
- Para clicar/preencher: usar `find` + `read_page` para pegar `ref` e depois `form_input` ou clique via ref — **sem** screenshot intermediário "para confirmar visualmente".
- Se o agente sentir necessidade real de inspecionar layout visualmente, **parar e perguntar ao usuário** antes de capturar: "Preciso de um screenshot deste painel para confirmar X. Posso prosseguir?" — e só seguir com confirmação explícita no chat.

### Domínios em que screenshot é PERMITIDO

Sites públicos: notícias, documentação técnica pública, Mercado Livre (listagens públicas), GitHub público, blogs, sites de informação. Mesmo assim, screenshot só quando texto/estrutura não resolveriam (ex.: ler um gráfico, validar layout visual de uma página de produto).

### Domínios em zona cinzenta

Google Sheets, Google Drive, Netlify, Apps Script editor, contas pessoais bancárias, brokers (XP, BTG, Inter), ERPs (Bling, Shopify Admin) — tratar como **corporativos/sensíveis**: sem screenshot, pedir confirmação se realmente necessário.

---

## Padrões de uso por tarefa

### Ler uma lista de registros (deals do CRM, emails, tickets)

❌ Errado: `computer screenshot` → tentar OCR / leitura visual.
✅ Certo:
```
1. navigate(URL da view/lista)
2. read_network_requests → pegar payload JSON da API que alimentou a grid
3. (se não tiver API) javascript_tool: 
   document.querySelectorAll('[role="row"]').forEach(r => 
     console.log(r.innerText.replace(/\s+/g,'|'))
   )
4. read_console_messages para coletar a saída
```

### Preencher um campo num formulário (ex.: RF Expert Notes em deal do Dynamics)

❌ Errado: screenshot → identificar visualmente → clicar por coordenadas.
✅ Certo:
```
1. read_page → localizar o campo pelo label / aria
2. form_input com o ref ID do campo
3. find("botão Save") → form_input/click no ref
4. read_page de novo para confirmar (não screenshot)
```

### Extrair texto de um email/documento

✅ `get_page_text` resolve em uma chamada. Não precisa de mais nada.

### Confirmar que uma ação deu certo

❌ Screenshot da tela inteira.
✅ `javascript_tool` lendo o elemento de confirmação específico, ou `read_page` filtrando pela região do toast/banner.

---

## Padrão para o agente comunicar economia ao usuário

No início de cada tarefa de browser, o agente declara em uma linha o plano de ferramentas:

> "Plano: vou usar `read_page` + `javascript_tool` para extrair os dados, sem screenshots (domínio corporativo APW)."

E ao final, declarar o que foi usado, para o Lucas ter visibilidade do consumo:

> "Concluído. 4 chamadas de `javascript_tool`, 2 de `read_page`, 0 screenshots."

---

## Regras rápidas (TL;DR)

1. Screenshot é o **último** recurso, nunca o primeiro.
2. Em domínio APW / Microsoft 365 / Dynamics / Power BI / Teams / Outlook / SharePoint → **screenshot proibido**. Sem exceção sem confirmação explícita no chat.
3. Preferir nesta ordem: `javascript_tool` > `read_page` > `get_page_text` > `read_network_requests` > `computer`.
4. Para clicar/preencher: sempre via `ref` do `read_page` + `form_input`, nunca por coordenadas de pixel.
5. Para confirmar resultado de ação: ler o elemento específico, não capturar a tela.
6. Declarar o plano de ferramentas no início e o consumo no fim.
7. Em zona cinzenta (Sheets, Bling, broker, banco) → tratar como corporativo.

---

## Notas para o Lucas

- Esta skill **não impede** que você peça explicitamente um screenshot ("tire um print desta tela"). Nesse caso o agente pergunta o domínio, confirma que você quer mesmo, e segue.
- Se você quiser endurecer ainda mais (bloqueio absoluto até em sites públicos), me avise e a gente edita a seção "Domínios em que screenshot é PERMITIDO".
- A lista de domínios proibidos é editável. Se aparecer um novo sistema corporativo (ex.: novo ERP, nova ferramenta de BI), adicionar na seção "Domínios em que screenshot é PROIBIDO".
