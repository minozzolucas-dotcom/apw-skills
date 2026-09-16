# Edge Cases de Parsing

A view de atividades do Dynamics, quando copiada como texto, é suja. Este guia cobre os casos em que `parse_activities.py` pode falhar e como tratar manualmente.

## Como a view chega

O cabeçalho típico: `N activities found. Click Here to refresh the list of activities.` seguido de uma linha de cabeçalho `Subject  Description  Activity Owner  Status  Created On  Actual End` e depois as linhas de dados, separadas por TAB.

## Casos difíceis

### 1. Descrições multi-linha
A coluna `Description` frequentemente contém quebras de linha — bullets, mensagens de WhatsApp coladas com timestamps `[11:52, 21/01/2026]`, parágrafos. Isso quebra parsers ingênuos que dividem por `\n`.

**Solução:** uma nova atividade só começa quando a linha bate com o padrão de início de registro — começa com `task` (ou outro tipo de atividade) seguido de TAB. Tudo entre dois inícios de registro pertence à descrição do registro anterior. O script usa essa heurística; se falhar, identifique manualmente as âncoras `task\t`.

### 2. Activity Owner vazio ou `undefined`
Tasks automáticas da calculadora têm owner `undefined`. Não é erro — registre como "Sistema (Calculator)". São marcadores de que uma proposta foi precificada.

### 3. Actual End vazio
Atividades com `Status: Open` não têm `Actual End`. Normal. A última coluna fica vazia.

### 4. Datas
Formato ISO `2026-05-20T14:12:55Z` na maioria dos campos. Mas dentro das descrições aparecem datas em formato BR (`19/05`, `28/07/2021`, `[11:52, 21/01/2026]`). Não confundir: as datas de ordenação são as das colunas `Created On`/`Actual End`, não as do texto livre.

### 5. Ordem invertida
A view lista do mais recente para o mais antigo. O parser deve reordenar por `Created On` ascendente. Sempre confira: a primeira atividade analisada deve ser a mais antiga (frequentemente um "Assignment" ou "Begin work").

### 6. Caracteres e acentuação
Texto em português com acentos, e às vezes erros de digitação ("Sínsica" por "Síndica", "ctt" por "contato", "qd" por "quando", "pq" por "porque"). Não corrija no parsing — preserve o original; a interpretação acontece na leitura forense, não no parser.

### 7. Múltiplas opps no mesmo input
Se o Lucas colar atividades de mais de uma opp (vários códigos L), o parser deve agrupar por código L. Cada opp recebe sua própria análise e seu par de artefatos.

## Quando o script falha completamente

Se o input está irrecuperável para o script (ex.: colado sem TABs, formatação destruída), faça o parsing manualmente: leia o bloco, identifique visualmente cada atividade pelas âncoras (`task` no início, datas ISO no fim), e estruture à mão. A leitura forense é o que importa — o parser é só conveniência.
