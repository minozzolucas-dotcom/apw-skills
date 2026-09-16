# Relatórios consolidados

Quando o Lucas pede coisas tipo "gera o reporte diário", "performance dos diretores essa semana", "pipeline consolidado", "closing pipeline".

Esses padrões já estão estabilizados nos workflows anteriores dele. Esta referência sintetiza o que funciona.

## Padrões de relatório que o Lucas costuma pedir

### 1. Closing Pipeline diário
- Sweep das oportunidades com estimatedclosedate próximo ou stage avançado
- Cross-check com emails de DUE DILIGENCE da Elian Sanches / PP F
- Output via Gmail pro corporativo dele (lminozzo@apwbrasil.com.br)

### 2. Movimentações do dia anterior (D-1)
Quatro views são fonte:
- Stg 1 moves this week
- Stg 3 moves this week
- Pricing current week
- Brasil Closed Activities yesterday

Classificação por diretor + link direto pra cada oportunidade.

### 3. Performance semanal de diretores Brasil
- ~15 sales directors
- KPIs: activity counts, pipeline stage movements
- Já existe uma versão com fluxo de reconciliação/errata pra quando alguém contesta os números

### 4. Rolling Forecast 2026
Pipeline contínuo: Hot deals + Closing deals → ACF (aluguel) + Pricing Option (purchase price). Existe versão GAS que sincroniza isso pro Google Sheets.

## Workflow padrão de relatório

### Passo 1: estabelece o recorte
Antes de buscar nada, confirma:
- Período (hoje, semana, mês fiscal, custom)
- Escopo (Brasil só, US só, global)
- Granularidade (por deal, por diretor, por stage)
- Destino (chat, email, planilha, dashboard)

### Passo 2: identifica as views fonte
Cada relatório padrão dele tem views específicas. Se ele citar pelo nome, pede o `viewid` da URL. Se ele descrever ("movimentações de stage 1 essa semana"), procura entre as views dele ou monta FetchXML direto.

### Passo 3: coleta paralela
Multiplas views? Usa `Promise.all` no JS — Web API do Dynamics aguenta requisições paralelas tranquilo, sessão é a mesma.

```js
(async () => {
  const base = window.location.origin;
  const headers = {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.include-annotations=*'};
  const viewIds = {
    stg1: 'GUID_1',
    stg3: 'GUID_2',
    pricing: 'GUID_3',
    closed: 'GUID_4'
  };
  const results = await Promise.all(
    Object.entries(viewIds).map(async ([key, id]) => {
      const r = await fetch(`${base}/api/data/v9.2/opportunities?savedQuery=${id}&$select=opportunityid,apwip_autonumberid,name,_ownerid_value`, {headers});
      const d = await r.json();
      return [key, d.value];
    })
  );
  return Object.fromEntries(results);
})();
```

### Passo 4: agregação em memória
Faz join por diretor (`_ownerid_value`), conta por stage, calcula deltas. Tudo dentro do JS ou no contexto da conversa. **Não cria CSV temporário em disco**.

### Passo 5: apresentação
Pro chat: resumo executivo em prosa curta + tabela compacta com top movements.
Pra email: o Lucas tem template próprio em Gmail, segue o estilo que ele já usa.

### Passo 6: confirmação de envio (se mandar email)
Padrão consolidado dele:
1. Clica Send
2. Aguarda 3-5 segundos
3. Confirma o toast "Mensagem enviada" via `get_page_text`
4. Navega `https://mail.google.com/mail/u/0/#sent`
5. Confirma o email como item mais recente
6. **Só agora** declara concluído

## Regra de honestidade

Nunca retornar "Concluído" sem confirmação visual de envio. Se falhou em qualquer ponto, imprime o relatório completo no chat em markdown e explica o que deu errado. O Lucas prefere isso a um falso positivo.

## Performance de diretores — cuidado especial

O fluxo de errata existe porque uma diretora contestou números. Antes de afirmar "Diretora X teve Y movimentações", confira:
1. Período exato (segunda 00:00 até domingo 23:59? Ou D-7 até hoje?)
2. Critério de "movimentação" (mudança de stage? Update de qualquer campo? Activity logada?)
3. Atribuição (owner atual ou owner no momento da movimentação?)

Documente o critério usado no próprio relatório pra que reconciliação seja fácil depois.
